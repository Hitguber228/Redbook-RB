import os

with open('src/database/seed_data.py', encoding='utf-8') as f:
    content = f.read()

split_token = 'INITIAL_QUIZZES_DATA = ['
idx = content.find(split_token)
if idx != -1:
    part2 = content[idx:]
else:
    raise ValueError("Could not find INITIAL_QUIZZES_DATA")

header = '''"""
Научный реестр видов Красной книги Республики Беларусь
(Постановление Минприроды РБ № 10 от 14 марта 2025 года)
"""
import os
import json

_species_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "full_redbook_species.json"))
if os.path.exists(_species_json_path):
    with open(_species_json_path, encoding="utf-8") as _f:
        INITIAL_SPECIES_DATA = json.load(_f)
else:
    INITIAL_SPECIES_DATA = []

'''

with open('src/database/seed_data.py', 'w', encoding='utf-8') as f:
    f.write(header + part2)

print("Updated seed_data.py successfully!")

