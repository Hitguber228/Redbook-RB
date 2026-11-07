import pytest
from src.services.ai_service import ai_service

def test_identify_bison_by_morphology():
    res = ai_service.identify_species(hint="крупное рогатое животное с бородой и горбом")
    assert res["species_id"] == "bison-bonasus"
    assert res["confidence"] >= 0.7
    assert res["category"] in ["II", "IV"]

def test_identify_lynx_track():
    res = ai_service.identify_species(hint="круглый след кошачьих на снегу без когтей", is_track=True)
    assert res["species_id"] == "lynx-lynx"
    assert "рысь" in res["name_ru"].lower()

def test_ai_naturalist_chat():
    resp = ai_service.ask_naturalist("Расскажи про зубра")
    assert "зубр" in resp.lower() or "bison" in resp.lower()

def test_identify_by_real_image():
    import os
    img_path = os.path.abspath("assets/images/species/bison-bonasus.jpg")
    res = ai_service.identify_species(image_path=img_path)
    assert res is not None
    assert "confidence" in res
    assert res["confidence"] > 0.5
    assert len(res["top_candidates"]) > 0

def test_clipboard_image_format_support():
    import os
    from PIL import Image
    # Test creating a test RGB image and identifying it
    test_img_path = os.path.abspath("assets/uploads/test_paste.jpg")
    os.makedirs(os.path.dirname(test_img_path), exist_ok=True)
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    img.save(test_img_path)
    try:
        res = ai_service.identify_species(image_path=test_img_path)
        assert res is not None
        assert "species_id" in res
    finally:
        if os.path.exists(test_img_path):
            os.remove(test_img_path)
