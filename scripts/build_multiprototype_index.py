import os
import sys
import sqlite3
import numpy as np
from PIL import Image, ImageEnhance
import onnxruntime as ort

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'redbook.db'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'ai', 'mobilenetv3_large.onnx'))
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'ai', 'vision_model.onnx'))

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'species'))
INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'ai', 'species_index.npz'))

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

def extract_features(img: Image.Image, session: ort.InferenceSession, input_name: str) -> np.ndarray:
    """Нормализует изображение и извлекает L2-нормализованный вектор признаков."""
    img_rgb = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
    arr = (np.transpose(np.array(img_rgb, dtype=np.float32) / 255.0, (2, 0, 1))[np.newaxis, ...] - MEAN) / STD
    raw = session.run(None, {input_name: arr.astype(np.float32)})[0][0]
    norm = np.linalg.norm(raw)
    return raw / norm if norm > 1e-6 else raw

def generate_augmentations(img: Image.Image):
    """Генерирует мультиракурсные варианты (Test-Time Prototypes) для расширения базы."""
    variants = [img]
    # 1. Горизонтальное отражение
    variants.append(img.transpose(Image.FLIP_LEFT_RIGHT))
    # 2. Фокусированный центральный кроп (зум 1.15x)
    w, h = img.size
    crop_box = (int(w * 0.08), int(h * 0.08), int(w * 0.92), int(h * 0.92))
    variants.append(img.crop(crop_box))
    # 3. Адаптация контраста (для разного лесного/полевого освещения)
    variants.append(ImageEnhance.Contrast(img).enhance(1.2))
    # 4. Адаптация яркости
    variants.append(ImageEnhance.Brightness(img).enhance(1.15))
    return variants

def main():
    print(f"[INDEX] Загрузка ONNX модели: {MODEL_PATH}")
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    print(f"[INDEX] Входной тензор: {input_name}, shape: {session.get_inputs()[0].shape}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name_ru, name_be, name_lat, category, kingdom, taxon_group, image_url FROM species")
    species_list = [dict(r) for r in c.fetchall()]
    conn.close()

    print(f"[INDEX] Построение мультипрототипного индекса для {len(species_list)} видов...")

    species_ids = []
    names_ru = []
    names_lat = []
    categories = []
    centroid_embeddings = []

    # Мультипрототипный пул (все прототипы для точного k-NN)
    all_proto_embs = []
    all_proto_ids = []

    for idx, sp in enumerate(species_list):
        sp_id = sp["id"]
        img_rel = sp.get("image_url", "")
        img_name = os.path.basename(img_rel) if img_rel else f"{sp_id}.jpg"
        img_path = os.path.join(IMAGES_DIR, img_name)

        if not os.path.exists(img_path):
            img_path = os.path.join(IMAGES_DIR, f"{sp_id}.jpg")
        if not os.path.exists(img_path):
            img_path = os.path.join(IMAGES_DIR, "bison-bonasus.jpg")

        try:
            with Image.open(img_path) as base_img:
                aug_imgs = generate_augmentations(base_img)
                aug_vecs = []
                for a_img in aug_imgs:
                    v = extract_features(a_img, session, input_name)
                    aug_vecs.append(v)
                    all_proto_embs.append(v)
                    all_proto_ids.append(sp_id)

                # Вычисляем центроидный вектор вида
                c_vec = np.mean(aug_vecs, axis=0)
                c_norm = np.linalg.norm(c_vec)
                c_vec = c_vec / c_norm if c_norm > 1e-6 else c_vec

                species_ids.append(sp_id)
                names_ru.append(sp["name_ru"])
                names_lat.append(sp["name_lat"])
                categories.append(sp["category"])
                centroid_embeddings.append(c_vec)
        except Exception as e:
            print(f"Ошибка при обработке {sp_id}: {e}")
            continue

        if (idx + 1) % 100 == 0 or (idx + 1) == len(species_list):
            print(f"  Обработано: {idx + 1}/{len(species_list)} видов...")

    centroid_matrix = np.array(centroid_embeddings, dtype=np.float32)
    proto_matrix = np.array(all_proto_embs, dtype=np.float32)

    print(f"[INDEX] Сохранение в {INDEX_PATH}:")
    print(f"  Центроидов видов: {centroid_matrix.shape}")
    print(f"  Всего прототипов в пуле: {proto_matrix.shape}")

    np.savez_compressed(
        INDEX_PATH,
        ids=np.array(species_ids),
        names_ru=np.array(names_ru),
        names_lat=np.array(names_lat),
        categories=np.array(categories),
        embeddings=centroid_matrix,
        proto_embeddings=proto_matrix,
        proto_ids=np.array(all_proto_ids)
    )

    size_kb = round(os.path.getsize(INDEX_PATH) / 1024, 1)
    print(f"[ГОТОВО] Мультипрототипный индекс успешно сохранен: {size_kb} КБ ({round(size_kb/1024, 2)} МБ).")

if __name__ == "__main__":
    main()
