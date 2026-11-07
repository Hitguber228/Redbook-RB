import os
import sys
import io
import re
import json
import sqlite3
import urllib.request
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'redbook.db'))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'species'))
os.makedirs(IMAGES_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'RedBookBelarusEducation/2.0 (belarus_ecology_education@tut.by; educational non-profit bot)'
}

def clean_binomial(latin_text):
    latin_text = latin_text.replace('ё', 'e').replace('Ё', 'E')
    text = re.sub(r'\(.*?\)', '', latin_text).strip()
    words = text.split()
    if len(words) >= 2:
        w1 = words[0]
        if words[1].lower() in ['var.', 'subsp.', 'f.', 'ssp.', 'x'] and len(words) >= 3:
            w2 = words[2].lower().rstrip('.,;')
        else:
            w2 = words[1].lower().rstrip('.,;')
        return f"{w1} {w2}", w1
    return latin_text, (words[0] if words else latin_text)

def clean_ru_title(ru_text):
    text = re.sub(r'\(.*?\)', '', ru_text).strip()
    return text.split('/')[0].strip()

def fetch_json(url, timeout=5, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429: # Rate limit
                time.sleep(1.2 + attempt * 1.5)
            elif e.code in (404, 400):
                return None
        except Exception:
            pass
        time.sleep(0.08)
    return None

def optimize_and_save_image(raw_bytes, save_path):
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        # Сжимаем до компактного разрешения 520x400 px
        img.thumbnail((520, 400), Image.Resampling.LANCZOS)
        img.save(save_path, 'JPEG', quality=75, optimize=True)
        return True
    except Exception:
        return False

def compress_existing_if_large(save_path):
    try:
        if os.path.exists(save_path) and os.path.getsize(save_path) > 100_000:
            with open(save_path, 'rb') as f:
                data = f.read()
            optimize_and_save_image(data, save_path)
    except Exception:
        pass

def get_species_wiki_info(sp):
    sp_id = sp["id"]
    lat_full = sp["name_lat"]
    binomial, genus = clean_binomial(lat_full)
    ru_name = clean_ru_title(sp["name_ru"])
    be_name = clean_ru_title(sp["name_be"])
    cat = sp["category"]

    img_path = os.path.join(IMAGES_DIR, f"{sp_id}.jpg")
    has_local_img = os.path.exists(img_path) and os.path.getsize(img_path) > 3000

    if has_local_img:
        compress_existing_if_large(img_path)
        img_url_to_save = f"/images/species/{sp_id}.jpg"
    else:
        img_url_to_save = None

    desc_ru = None
    desc_be = None
    morphology = None

    # Поиск информации в Википедии (приоритет: чистый биноминал -> русское название -> род -> английская wiki)
    ru_data = None
    search_candidates_ru = [binomial, ru_name, genus]
    for term in search_candidates_ru:
        if not term or len(term) < 3:
            continue
        page = term.replace(' ', '_')
        url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page)}"
        ru_data = fetch_json(url)
        if ru_data and ru_data.get('type') != 'disambiguation' and ru_data.get('extract'):
            break
        time.sleep(0.06)

    # Если фото не найдено в русской, ищем в английской по биноминалу или роду
    if not ru_data or not ru_data.get('thumbnail'):
        for term_en in [binomial, genus]:
            if not term_en or len(term_en) < 3:
                continue
            page_en = term_en.replace(' ', '_')
            url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_en)}"
            en_data = fetch_json(url_en)
            if en_data and en_data.get('type') != 'disambiguation':
                if not ru_data:
                    ru_data = en_data
                elif en_data.get('thumbnail'):
                    ru_data['thumbnail'] = en_data['thumbnail']
                if ru_data.get('thumbnail'):
                    break
            time.sleep(0.06)

    # Скачивание и оптимизация изображения через Pillow
    if not has_local_img and ru_data and ru_data.get('thumbnail'):
        thumb_src = ru_data['thumbnail'].get('source')
        if thumb_src:
            try:
                req = urllib.request.Request(thumb_src, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=7) as resp:
                    raw_data = resp.read()
                    if len(raw_data) > 1500:
                        if optimize_and_save_image(raw_data, img_path):
                            img_url_to_save = f"/images/species/{sp_id}.jpg"
            except Exception:
                pass

    # Формирование описания и морфологии
    if ru_data and ru_data.get('extract'):
        ext = ru_data['extract'].strip()
        if len(ext) > 30:
            desc_ru = f"{ext} Включен в Красную книгу Республики Беларусь (Постановление Минприроды РБ № 10 от 14 марта 2025 г., категория {cat})."
            morphology = ext[:350]

    # Белорусское описание
    be_data = None
    for term_be in [binomial, be_name, genus]:
        if not term_be or len(term_be) < 3:
            continue
        page_be = term_be.replace(' ', '_')
        url_be = f"https://be.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_be)}"
        be_data = fetch_json(url_be)
        if be_data and be_data.get('type') != 'disambiguation' and be_data.get('extract'):
            break
        time.sleep(0.05)

    if be_data and be_data.get('extract'):
        be_ext = be_data['extract'].strip()
        if len(be_ext) > 25:
            desc_be = f"{be_ext} Уключаны ў Чырвоную кнігу Рэспублікі Беларусь (Пастанова Мінпрыроды РБ № 10 ад 14 сакавіка 2025 г., катэгорыя {cat})."

    time.sleep(0.08)

    return {
        "id": sp_id,
        "name_ru": sp["name_ru"],
        "name_lat": lat_full,
        "image_url": img_url_to_save,
        "description_ru": desc_ru,
        "description_be": desc_be,
        "morphology": morphology
    }

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Выбираем виды, которые еще не обогащены индивидуальными фото
    cursor.execute("""
        SELECT id, name_ru, name_be, name_lat, category, image_url, description_ru, description_be 
        FROM species 
        WHERE image_url IN (
            '/images/species/bison.jpg',
            '/images/species/stork.jpg',
            '/images/species/toad.jpg',
            '/images/species/turtle.jpg',
            '/images/species/sterlet.jpg',
            '/images/species/stag_beetle.jpg',
            '/images/species/sparassis.jpg',
            '/images/species/sarcosoma.jpg',
            '/images/species/slipper.jpg'
        )
    """)
    species_to_enrich = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total_queue = len(species_to_enrich)
    print(f"Видов на обогащение: {total_queue}", flush=True)

    if total_queue == 0:
        print("Все виды уже обогащены индивидуальными изображениями!", flush=True)
        return

    print("Запуск сбора реальных научных фото и описаний (3 потока, вежливый интервал)...", flush=True)
    results = []
    start_time = time.time()
    images_found = 0
    desc_found = 0

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(get_species_wiki_info, sp): sp for sp in species_to_enrich}
        for i, future in enumerate(as_completed(futures), 1):
            res = future.result()
            results.append(res)
            if res.get("image_url"):
                images_found += 1
            if res.get("description_ru"):
                desc_found += 1

            if i % 20 == 0 or i == total_queue:
                elapsed = round(time.time() - start_time, 1)
                speed = round(i / elapsed, 1) if elapsed > 0 else 1
                rem_sec = round((total_queue - i) / speed) if speed > 0 else 0
                print(f"[{i}/{total_queue}] {elapsed}s (осталось ~{rem_sec}с) | Новых фото: {images_found} | Новых описаний: {desc_found}", flush=True)

    print("\nСохранение обогащенных данных в redbook.db...", flush=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated = 0
    for r in results:
        updates = []
        params = []
        if r.get("image_url"):
            updates.append("image_url = ?")
            params.append(r["image_url"])
        if r.get("description_ru"):
            updates.append("description_ru = ?")
            params.append(r["description_ru"])
        if r.get("description_be"):
            updates.append("description_be = ?")
            params.append(r["description_be"])
        if r.get("morphology"):
            updates.append("morphology = ?")
            params.append(r["morphology"])

        if updates:
            params.append(r["id"])
            cursor.execute(f"UPDATE species SET {', '.join(updates)} WHERE id = ?", params)
            updated += 1

    conn.commit()
    conn.close()
    print(f"Обновлено записей в базе данных: {updated}", flush=True)

    # Оптимизация размера всех файлов в папке картинок
    print("Проверка и сжатие всех локальных файлов...", flush=True)
    for fname in os.listdir(IMAGES_DIR):
        if fname.endswith('.jpg'):
            compress_existing_if_large(os.path.join(IMAGES_DIR, fname))

    # Синхронизация геоданных карты
    print("Экспорт геоданных в map_data.js...", flush=True)
    import subprocess
    subprocess.run([sys.executable, "scripts/export_map_data.py"], check=True)
    print("Готово! Все данные и карта синхронизированы.", flush=True)

if __name__ == "__main__":
    main()
