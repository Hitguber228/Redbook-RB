import pytest
import os
import tempfile
import gc
from src.database.db import DatabaseManager

@pytest.fixture
def test_db():
    # Создаем временную тестовую базу данных
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=temp_db_path)
    yield db
    del db
    gc.collect()
    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except Exception:
        pass

def test_database_initialization(test_db):
    species = test_db.get_species()
    assert len(species) >= 19, "В базе должно быть не менее 19 верифицированных видов"

def test_species_nomenclature(test_db):
    bison = test_db.get_species_by_id("bison-bonasus")
    assert bison is not None
    assert bison["name_ru"] == "Европейский зубр"
    assert bison["name_be"] == "Еўрапейскі зубр"
    assert bison["name_lat"] == "Bison bonasus"
    assert bison["category"] == "II"
    assert bison["kingdom"] == "animals"
    assert os.path.exists(os.path.join("assets", bison["image_url"].lstrip("/")))

def test_filter_by_category(test_db):
    cat_1_species = test_db.get_species(category="I")
    assert len(cat_1_species) > 0
    for s in cat_1_species:
        assert s["category"] == "I"

def test_filter_by_kingdom(test_db):
    plants = test_db.get_species(kingdom="plants")
    assert len(plants) > 0
    for p in plants:
        assert p["kingdom"] == "plants"

    fungi = test_db.get_species(kingdom="fungi")
    assert len(fungi) >= 2
    for f in fungi:
        assert f["kingdom"] == "fungi"

def test_filter_by_region(test_db):
    brest_species = test_db.get_species(region="Брестская")
    assert len(brest_species) >= 10
    vitebsk_species = test_db.get_species(region="Витебская")
    assert len(vitebsk_species) >= 8

def test_search_species(test_db):
    # Поиск по-русски
    results_ru = test_db.get_species(query="рысь")
    assert any(s["id"] == "lynx-lynx" for s in results_ru)

    # Поиск по латыни
    results_lat = test_db.get_species(query="Ciconia")
    assert any(s["id"] == "ciconia-nigra" for s in results_lat)

    # Поиск на белорусском языке
    results_be = test_db.get_species(query="бусел")
    assert any(s["id"] == "ciconia-nigra" for s in results_be)

def test_observations_diary(test_db):
    initial_count = len(test_db.get_observations())
    obs_id = test_db.add_observation(
        species_guess="Рысь европейская",
        user_name="Студент-биолог",
        notes="Замечены характерные круглые следы на снегу в Налибокской пуще",
        lat=53.9500,
        lng=26.4200,
        date_str="2026-11-07 14:00"
    )
    assert obs_id > 0
    updated_obs = test_db.get_observations()
    assert len(updated_obs) == initial_count + 1
    assert updated_obs[0]["user_name"] == "Студент-биолог"

