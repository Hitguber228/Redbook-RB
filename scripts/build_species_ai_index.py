import os
import sys
import sqlite3
import numpy as np
from PIL import Image
import onnxruntime as ort

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'redbook.db'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'ai', 'vision_model.onnx'))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'species'))
INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'ai', 'species_index.npz'))

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

def preprocess_image(img_path):
    try:
        with Image.open(img_path) as img:
            img = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
            arr = np.array(img, dtype=np.float32) / 255.0
            # [H, W, C] -> [1, C, H, W]
            arr = np.transpose(arr, (2, 0, 1))[np.newaxis, ...]
            # Нормализация
            arr = (arr - MEAN) / STD
            return arr.astype(np.float32)
    except Exception:
        return None

def main():
    print(f"Загрузка легковесной ONNX модели из {MODEL_PATH}...")
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name_ru, name_be, name_lat, category, kingdom, taxon_group, image_url FROM species")
    species_list = [dict(r) for r in c.fetchall()]
    conn.close()

    print(f"Построение векторного индекса для {len(species_list)} видов Красной книги...")

    species_ids = []
    names_ru = []
    names_lat = []
    categories = []
    embeddings_list = []

    for sp in species_list:
        sp_id = sp["id"]
        # Путь к локальному фото
        img_rel = sp.get("image_url", "")
        img_name = os.path.basename(img_rel) if img_rel else f"{sp_id}.jpg"
        img_path = os.path.join(IMAGES_DIR, img_name)

        if not os.path.exists(img_path):
            img_path = os.path.join(IMAGES_DIR, f"{sp_id}.jpg")

        if not os.path.exists(img_path):
            # Fallback к первому попавшемуся
            img_path = os.path.join(IMAGES_DIR, "bison-bonasus.jpg")

        tensor = preprocess_image(img_path)
        if tensor is None:
            continue

        raw_out = session.run(None, {input_name: tensor})[0] # [1, 1000]
        vec = raw_out[0]
        # L2-нормализация для косинусного сходства
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm

        species_ids.append(sp_id)
        names_ru.append(sp["name_ru"])
        names_lat.append(sp["name_lat"])
        categories.append(sp["category"])
        embeddings_list.append(vec)

    embeddings_matrix = np.array(embeddings_list, dtype=np.float32) # [N, 1000]

    np.savez_compressed(
        INDEX_PATH,
        ids=np.array(species_ids),
        names_ru=np.array(names_ru),
        names_lat=np.array(names_lat),
        categories=np.array(categories),
        embeddings=embeddings_matrix
    )

    file_size_kb = round(os.path.getsize(INDEX_PATH) / 1024, 1)
    print(f"Готово! Векторный индекс сохранен в {INDEX_PATH} ({file_size_kb} КБ, векторов: {len(species_ids)}).")

if __name__ == "__main__":
    main()
