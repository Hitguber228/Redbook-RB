import os
import sys
import httpx
from urllib.parse import quote

# Mapping of species id to Wikipedia search term (Russian or Latin)
SPECIES_WIKI_MAP = {
    "bison-bonasus": "Bison bonasus",
    "ciconia-nigra": "Ciconia nigra",
    "acrocephalus-paludicola": "Acrocephalus paludicola",
    "lynx-lynx": "Lynx lynx",
    "ursus-arctos": "Ursus arctos",
    "meles-meles": "Meles meles",
    "spermophilus-suslicus": "Spermophilus suslicus",
    "strix-nebulosa": "Strix nebulosa",
    "haliaeetus-albicilla": "Haliaeetus albicilla",
    "acipenser-ruthenus": "Acipenser ruthenus",
    "epidalea-calamita": "Epidalea calamita",
    "emys-orbicularis": "Emys orbicularis",
    "coronella-austriaca": "Coronella austriaca",
    "lucanus-cervus": "Lucanus cervus",
    "cypripedium-calceolus": "Cypripedium calceolus",
    "allium-ursinum": "Allium ursinum",
    "sparassis-crispa": "Sparassis crispa",
    "sarcosoma-globosum": "Sarcosoma globosum",
    "pulsatilla-patens": "Pulsatilla patens",
}

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "images", "species"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "RedBookBelarusAcademicProject/1.0 (contact: student@edu.by; educational research)"
}

print(f"[DOWNLOAD] Загрузка научных изображений для 19 видов в {OUTPUT_DIR}...")

client = httpx.Client(headers=headers, timeout=20.0, follow_redirects=True)

success_count = 0

for sp_id, query in SPECIES_WIKI_MAP.items():
    file_path = os.path.join(OUTPUT_DIR, f"{sp_id}.jpg")
    print(f"-> Поиск для: {sp_id} ({query})...", end=" ")
    
    # Сначала пробуем русскую Википедию, затем английскую
    img_url = None
    for lang in ["ru", "en"]:
        encoded = quote(query)
        api_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        try:
            resp = client.get(api_url)
            if resp.status_code == 200:
                data = resp.json()
                if "originalimage" in data and "source" in data["originalimage"]:
                    img_url = data["originalimage"]["source"]
                    break
                elif "thumbnail" in data and "source" in data["thumbnail"]:
                    # Берем качественную версию превью
                    thumb = data["thumbnail"]["source"]
                    img_url = thumb
                    break
        except Exception as e:
            continue
            
    if not img_url:
        print("❌ Не найдено изображение в API")
        continue

    # Скачиваем изображение
    try:
        img_resp = client.get(img_url)
        if img_resp.status_code == 200 and len(img_resp.content) > 1000:
            with open(file_path, "wb") as f:
                f.write(img_resp.content)
            print(f"✅ Скачано ({len(img_resp.content) // 1024} КБ)")
            success_count += 1
        else:
            print(f"⚠️ Ошибка скачивания (HTTP {img_resp.status_code})")
    except Exception as ex:
        print(f"⚠️ Исключение: {ex}")

client.close()
print(f"\n[ГОТОВО] Успешно сохранено: {success_count}/{len(SPECIES_WIKI_MAP)} видов!")

