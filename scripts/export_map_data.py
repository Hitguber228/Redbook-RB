import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database.seed_data import INITIAL_SPECIES_DATA

GEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "geo", "belarus_geo.json"))

with open(GEO_PATH, "r", encoding="utf-8") as f:
    geo_data = json.load(f)

# Format species for GIS
species_gis = []
for sp in INITIAL_SPECIES_DATA:
    species_gis.append({
        "id": sp["id"],
        "name_ru": sp["name_ru"],
        "name_be": sp["name_be"],
        "name_lat": sp["name_lat"],
        "category": sp["category"],
        "kingdom": sp["kingdom"],
        "taxon_group": sp["taxon_group"],
        "image_url": sp["image_url"],
        "habitat": sp["habitat"],
        "description_ru": sp.get("description_ru", ""),
        "description_be": sp.get("description_be", ""),
        "morphology": sp.get("morphology", ""),
        "look_alike_species": sp.get("look_alike_species", ""),
        "sound_url": sp.get("sound_url", ""),
        "sound_title": sp.get("sound_title", ""),
        "coordinates": sp.get("coordinates", [])
    })

js_content = f"""// Данные Красной книги Беларуси для интерактивной карты
const REDBOOK_SPECIES = {json.dumps(species_gis, ensure_ascii=False, indent=2)};

const NATIONAL_PARKS = {json.dumps(geo_data.get("national_parks", []), ensure_ascii=False, indent=2)};

const BELARUS_REGIONS = {json.dumps(geo_data.get("regions", []), ensure_ascii=False, indent=2)};
"""

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "map", "map_data.js"))
with open(output_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"✅ Экспортированы геоданные для карты в {output_path} ({len(species_gis)} видов, {len(geo_data.get('national_parks', []))} парков)")
