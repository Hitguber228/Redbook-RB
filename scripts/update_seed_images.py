import re

with open('src/database/seed_data.py', 'r', encoding='utf-8') as f:
    text = f.read()

species_ids = [
    'bison-bonasus', 'ciconia-nigra', 'acrocephalus-paludicola', 'lynx-lynx', 'ursus-arctos',
    'meles-meles', 'spermophilus-suslicus', 'strix-nebulosa', 'haliaeetus-albicilla',
    'acipenser-ruthenus', 'epidalea-calamita', 'emys-orbicularis', 'coronella-austriaca',
    'lucanus-cervus', 'cypripedium-calceolus', 'allium-ursinum', 'sparassis-crispa',
    'sarcosoma-globosum', 'pulsatilla-patens'
]

for sp_id in species_ids:
    pattern = rf'("id":\s*"{sp_id}".*?"image_url":\s*")[^"]+(")'
    text = re.sub(pattern, rf'\g<1>/images/species/{sp_id}.jpg\g<2>', text, flags=re.DOTALL)

with open('src/database/seed_data.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated all 19 image_urls to local paths in seed_data.py!')
