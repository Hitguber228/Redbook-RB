import flet as ft

class AppColors:
    # Природная палитра Беларуси (пущи, мхи, торф, лен)
    PRIMARY = "#2D6A4F"         # Хвойный темно-зеленый
    PRIMARY_LIGHT = "#40916C"   # Светлый мох
    PRIMARY_CONTAINER = "#D8F3DC"
    SECONDARY = "#B7E4C7"
    
    # Фоны
    BG_LIGHT = "#F8F9FA"        # Натуральный светлый лен
    BG_DARK = "#121A16"         # Ночной лес (для ночных наблюдений)
    SURFACE_LIGHT = "#FFFFFF"
    SURFACE_DARK = "#1B2620"
    
    # Текст
    TEXT_MAIN_LIGHT = "#1B2620"
    TEXT_MUTED_LIGHT = "#52796F"
    TEXT_MAIN_DARK = "#F8F9FA"
    TEXT_MUTED_DARK = "#95D5B2"
    
    # Официальные охранные категории Красной книги РБ
    CAT_I = "#DC2626"   # I Категория - На грани исчезновения (CR)
    CAT_II = "#EA580C"  # II Категория - Исчезающие (EN)
    CAT_III = "#D97706" # III Категория - Уязвимые (VU)
    CAT_IV = "#65A30D"  # IV Категория - Требующие контроля (NT)
    
    # Нейтральный маркер
    BORDER_COLOR = "#D1D5DB"

def get_category_color(cat: str) -> str:
    mapping = {
        "I": AppColors.CAT_I,
        "II": AppColors.CAT_II,
        "III": AppColors.CAT_III,
        "IV": AppColors.CAT_IV,
    }
    return mapping.get(cat, AppColors.PRIMARY)

def get_category_label(cat: str, lang: str = "ru") -> str:
    if lang == "be":
        labels = {
            "I": "I Катэгорыя (На мяжы знікнення)",
            "II": "II Катэгорыя (Знікаючыя)",
            "III": "III Катэгорыя (Уразлівыя)",
            "IV": "IV Катэгорыя (Пад кантролем)",
        }
    else:
        labels = {
            "I": "I Категория (На грани исчезновения)",
            "II": "II Категория (Исчезающие)",
            "III": "III Категория (Уязвимые)",
            "IV": "IV Категория (Требующие контроля)",
        }
    return labels.get(cat, f"Категория {cat}")

