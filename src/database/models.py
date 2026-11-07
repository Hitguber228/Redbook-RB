from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ConservationCategory(str, Enum):
    CR = "I"    # На грани исчезновения (Critically Endangered)
    EN = "II"   # Исчезающие (Endangered)
    VU = "III"  # Уязвимые (Vulnerable)
    NT = "IV"   # Требующие внимания / Потенциально уязвимые (Near Threatened)

class Kingdom(str, Enum):
    ANIMALS = "animals" # Животные / Фауна
    PLANTS = "plants"   # Растения / Флора
    FUNGI = "fungi"     # Грибы и Лишайники / Микобиота

class TaxonGroup(str, Enum):
    MAMMALS = "mammals"                 # Млекопитающие / Млекакормячыя
    BIRDS = "birds"                     # Птицы / Птушкі
    REPTILES = "reptiles"               # Пресмыкающиеся / Паўзуны
    AMPHIBIANS = "amphibians"           # Земноводные / Земнаводныя
    FISH = "fish"                       # Рыбы / Рыбы
    INSECTS = "insects"                 # Насекомые / Насякомыя
    VASCULAR_PLANTS = "vascular_plants" # Сосудистые растения / Сасудзістыя расліны
    MOSSES = "mosses"                   # Мхи / Мхі
    LICHENS = "lichens"                 # Лишайники / Лішайнікі
    FUNGI = "fungi"                     # Грибы / Грыбы

class SpeciesModel(BaseModel):
    id: str
    name_ru: str
    name_be: str
    name_lat: str
    kingdom: Kingdom
    taxon_group: TaxonGroup
    category: ConservationCategory
    description_ru: str
    description_be: str
    morphology: str
    look_alike_species: Optional[str] = None # Сравнение с видом-двойником
    habitat: str
    distribution_rb: List[str]               # Области РБ
    national_parks: List[str]                # Заповедники и заказники
    limiting_factors: str                    # Почему вид исчезает
    protection_measures: str                 # Законы и меры охраны в РБ
    phenology_months: List[int]              # Месяцы активности (1..12)
    image_url: str
    sound_url: Optional[str] = None
    sound_title: Optional[str] = None
    coordinates_json: str = "[]"             # [[lat, lng], ...]
    is_featured: bool = False

class QuizQuestion(BaseModel):
    id: int
    quiz_type: str # 'voice', 'tracks', 'general'
    question_ru: str
    question_be: str
    options_ru: List[str]
    options_be: List[str]
    correct_index: int
    explanation_ru: str
    explanation_be: str
    media_url: Optional[str] = None
    related_species_id: Optional[str] = None

class ObservationModel(BaseModel):
    id: Optional[int] = None
    species_id: Optional[str] = None
    species_guess: str
    user_name: str
    notes: str
    latitude: float
    longitude: float
    date_created: str
    photo_path: Optional[str] = None

