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
