import flet as ft
import json
import math
import os
from typing import Callable, Optional, List, Dict
from ...database.db import db_manager
from ...utils import open_target
from ..theme import AppColors, get_category_color

GEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "geo", "belarus_geo.json"))

REGION_PREFIX_MAP = {
    "brest": "Брестская",
    "vitebsk": "Витебская",
    "gomel": "Гомельская",
    "grodno": "Гродненская",
    "minsk": "Минская",
    "mogilev": "Могилевская"
}

LOCATIONS_PRESETS = [
    {"id": "minsk", "name_ru": "Минск", "name_be": "Мінск", "coords": (53.9006, 27.5590), "type": "city"},
    {"id": "pushcha", "name_ru": "Беловежская пуща", "name_be": "Белавежская пушча", "coords": (52.5724, 23.8016), "type": "park"},
    {"id": "pripyat", "name_ru": "НП Припятский (Полесье)", "name_be": "НП Прыпяцкі (Палессе)", "coords": (52.0210, 27.8100), "type": "park"},
    {"id": "berezina", "name_ru": "Березинский биосферный", "name_be": "Бярэзінскі запаведнік", "coords": (54.7300, 28.3500), "type": "park"},
    {"id": "braslav", "name_ru": "Браславские озёра", "name_be": "Браслаўскія азёры", "coords": (55.6300, 27.0500), "type": "park"},
    {"id": "naroch", "name_ru": "НП Нарочанский", "name_be": "НП Нарачанскі", "coords": (54.8500, 26.8500), "type": "park"},
    {"id": "sporovo", "name_ru": "Заказник Споровский", "name_be": "Заказнік Спораўскі", "coords": (52.4167, 25.1667), "type": "reserve"},
    {"id": "nesvizh", "name_ru": "Несвиж (Крапчатый суслик)", "name_be": "Нясвіж (Крапчаты хоўлік)", "coords": (53.2200, 26.6800), "type": "city"},
    {"id": "brest", "name_ru": "Брест", "name_be": "Брэст", "coords": (52.0976, 23.7341), "type": "city"},
    {"id": "grodno", "name_ru": "Гродно", "name_be": "Гродна", "coords": (53.6884, 23.8258), "type": "city"},
    {"id": "vitebsk", "name_ru": "Витебск", "name_be": "Віцебск", "coords": (55.1904, 30.2049), "type": "city"},
    {"id": "gomel", "name_ru": "Гомель", "name_be": "Гомель", "coords": (52.4345, 30.9754), "type": "city"},
    {"id": "mogilev", "name_ru": "Могилёв", "name_be": "Магілёў", "coords": (53.8938, 30.3353), "type": "city"},
]

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class MapView(ft.Container):
    def __init__(self, on_select_species: Callable[[str], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.on_select_species = on_select_species
        self.get_language = get_language
        self.geo_data = self._load_geo()
        self.selected_radius_km = 15
        self.selected_location = LOCATIONS_PRESETS[1] # Беловежская пуща по умолчанию
        self.legend_expanded = True

        self._build_ui()

    def _load_geo(self):
        if os.path.exists(GEO_PATH):
            with open(GEO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"regions": [], "national_parks": []}

    def _build_ui(self):
        lang = self.get_language()
        all_species = db_manager.get_species()

        # 1. Заголовок и запуск интерактивной полноэкранной карты Leaflet
        gis_header = ft.Card(
            elevation=2,
            content=ft.Container(
                padding=16,
                border_radius=16,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=[AppColors.PRIMARY, "#1B4332"]
                ),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True,
                    spacing=12,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Row(
                                    tight=True,
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.PUBLIC, color=ft.Colors.WHITE, size=24),
                                        ft.Text(
                                            "Интерактивная ГИС-карта Беларуси" if lang == "ru" else "Інтэрактыўная ГІС-карта Беларусі",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE
                                        )
                                    ]
                                ),
                                ft.Text(
                                    "Кликните в любую точку страны для сканирования радиуса на редкие виды (3–30 км)." if lang == "ru" else "Клікніце ў любы пункт краіны для сканавання радыуса на рэдкія віды.",
                                    size=12,
                                    color=ft.Colors.WHITE_70
                                )
                            ]
                        ),
                        ft.FilledButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            content=ft.Text("Открыть веб-карту Leaflet" if lang == "ru" else "Адкрыць вэб-карту Leaflet", weight=ft.FontWeight.BOLD),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=AppColors.PRIMARY),
                            on_click=lambda e: open_target("/map/index.html", self.page)
                        )
                    ]
                )
            )
        )

        # 2. Выбор радиуса поиска (3, 5, 15, 30 км)
        radius_buttons = []
        for r_val in [3, 5, 15, 30]:
            is_active = (self.selected_radius_km == r_val)
            radius_buttons.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                    border_radius=12,
                    bgcolor=AppColors.PRIMARY if is_active else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border=ft.Border.all(1.5, AppColors.PRIMARY if is_active else ft.Colors.TRANSPARENT),
                    ink=True,
                    on_click=lambda e, val=r_val: self._change_radius(val),
                    content=ft.Text(
                        f"{r_val} км",
                        size=12,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if is_active else ft.Colors.ON_SURFACE
                    )
                )
            )

        # 3. Быстрый выбор локации (Города и Заповедники)
        location_chips = []
        for loc in LOCATIONS_PRESETS:
            is_loc_active = (loc["id"] == self.selected_location["id"])
            loc_title = loc["name_be"] if lang == "be" else loc["name_ru"]
            loc_icon = ft.Icons.PARK if loc["type"] == "park" else (ft.Icons.GRASS if loc["type"] == "reserve" else ft.Icons.LOCATION_CITY)

            location_chips.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=16,
                    bgcolor=AppColors.PRIMARY_CONTAINER if is_loc_active else ft.Colors.SURFACE,
                    border=ft.Border.all(1.5, AppColors.PRIMARY if is_loc_active else ft.Colors.OUTLINE_VARIANT),
                    ink=True,
                    on_click=lambda e, l=loc: self._select_location(l),
                    content=ft.Row(
                        tight=True,
                        spacing=5,
                        controls=[
                            ft.Icon(loc_icon, size=13, color=AppColors.PRIMARY if is_loc_active else ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(
                                loc_title,
                                size=11,
                                weight=ft.FontWeight.BOLD if is_loc_active else ft.FontWeight.NORMAL,
                                color=AppColors.PRIMARY if is_loc_active else ft.Colors.ON_SURFACE
                            )
                        ]
                    )
                )
            )

        # 4. Расчет видов в радиусе вокруг выбранной локации (Haversine Spatial Query)
        center_lat, center_lon = self.selected_location["coords"]
        species_in_radius = []

        for sp in all_species:
            coords_list = json.loads(sp["coordinates_json"]) if isinstance(sp["coordinates_json"], str) else sp.get("coordinates_json", [])
            min_dist = float("inf")

            for c in coords_list:
                dist = haversine_km(center_lat, center_lon, c[0], c[1])
                if dist < min_dist:
                    min_dist = dist

            # Если расстояние укладывается в расширенный радиус биотопа
            if min_dist <= self.selected_radius_km * 2.5:
                species_in_radius.append({
                    "species": sp,
                    "distance_km": min_dist
                })

        species_in_radius.sort(key=lambda x: x["distance_km"])

        # Карточки найденных видов в радиусе
        species_result_cards = []
        for item in species_in_radius:
            sp = item["species"]
            dist_val = item["distance_km"]
            cat_color = get_category_color(sp["category"])
            sp_name = sp["name_be"] if lang == "be" else sp["name_ru"]

            species_result_cards.append(
                ft.Container(
                    col={"sm": 12, "md": 6, "lg": 4},
                    padding=12,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=4, color=ft.Colors.BLACK_12),
                    ink=True,
                    on_click=lambda e, sid=sp["id"]: self.on_select_species(sid),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=60,
                                height=60,
                                border_radius=10,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(src=sp["image_url"], fit="cover")
                            ),
                            ft.Column(
                                spacing=3,
                                expand=True,
                                controls=[
                                    ft.Text(sp_name, weight=ft.FontWeight.BOLD, size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(sp["name_lat"], italic=True, size=11, color=AppColors.TEXT_MUTED_LIGHT),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Container(
                                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                                border_radius=6,
                                                bgcolor=cat_color,
                                                content=ft.Text(f"Кат. {sp['category']}", size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                            ),
                                            ft.Container(
                                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                                border_radius=6,
                                                bgcolor=AppColors.PRIMARY_CONTAINER,
                                                content=ft.Text(f"~{dist_val:.1f} км", size=10, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD)
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                )
            )

        # 5. Раздел легенды карты (полная легенда со всеми символами)
        legend_content = ft.Card(
            elevation=1,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    tight=True,
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.LAYERS, color=AppColors.PRIMARY, size=20),
                                        ft.Text("Официальная легенда карты и символика:" if lang == "ru" else "Афіцыйная легенда карты і сімволіка:", weight=ft.FontWeight.BOLD, size=14)
                                    ]
                                ),
                                ft.Text("4 категории охраны РБ", size=11, color=AppColors.TEXT_MUTED_LIGHT)
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.ResponsiveRow(
                            spacing=12,
                            run_spacing=8,
                            controls=[
                                ft.Container(
                                    col={"sm": 6, "md": 3},
                                    content=ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=14, height=14, border_radius=7, bgcolor=AppColors.CAT_I),
                                            ft.Text("I (CR) — На грани исчезновения", size=11, weight=ft.FontWeight.W_500)
                                        ]
                                    )
                                ),
                                ft.Container(
                                    col={"sm": 6, "md": 3},
                                    content=ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=14, height=14, border_radius=7, bgcolor=AppColors.CAT_II),
                                            ft.Text("II (EN) — Исчезающие виды", size=11, weight=ft.FontWeight.W_500)
                                        ]
                                    )
                                ),
                                ft.Container(
                                    col={"sm": 6, "md": 3},
                                    content=ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=14, height=14, border_radius=7, bgcolor=AppColors.CAT_III),
                                            ft.Text("III (VU) — Уязвимые виды", size=11, weight=ft.FontWeight.W_500)
                                        ]
                                    )
                                ),
                                ft.Container(
                                    col={"sm": 6, "md": 3},
                                    content=ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=14, height=14, border_radius=7, bgcolor=AppColors.CAT_IV),
                                            ft.Text("IV (NT) — Под контролем", size=11, weight=ft.FontWeight.W_500)
                                        ]
                                    )
                                ),
                            ]
                        ),
                        ft.Row(
                            wrap=True,
                            spacing=12,
                            controls=[
                                ft.Text("Обозначения на карте:", size=11, weight=ft.FontWeight.BOLD),
                                ft.Row([ft.Icon(ft.Icons.PETS, size=13, color=AppColors.PRIMARY), ft.Text("Млекопитающие", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.FLIGHT, size=13, color=AppColors.PRIMARY), ft.Text("Птицы", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.WATER, size=13, color=AppColors.PRIMARY), ft.Text("Рыбы / Земноводные", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.BUG_REPORT, size=13, color=AppColors.PRIMARY), ft.Text("Насекомые", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.LOCAL_FLORIST, size=13, color=AppColors.PRIMARY), ft.Text("Растения", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.SPA, size=13, color=AppColors.PRIMARY), ft.Text("Грибы", size=11)], spacing=4, tight=True),
                                ft.Row([ft.Icon(ft.Icons.PARK, size=13, color=AppColors.PRIMARY), ft.Text("ООПТ / Нацпарки", size=11, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY)], spacing=4, tight=True),
                            ]
                        )
                    ]
                )
            )
        )

        selected_loc_name = self.selected_location["name_be"] if lang == "be" else self.selected_location["name_ru"]

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            spacing=16,
            controls=[
                gis_header,
                legend_content,
                # Панель выбора радиуса и локации
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Интерактивный радиусный сканер:" if lang == "ru" else "Інтэрактыўны радыусны сканер:", weight=ft.FontWeight.BOLD, size=15),
                                        ft.Row(spacing=6, controls=radius_buttons)
                                    ]
                                ),
                                ft.Text("Выберите точку на карте или населенный пункт:" if lang == "ru" else "Абярыце пункт на карце ці населены пункт:", size=12, color=AppColors.TEXT_MUTED_LIGHT),
                                ft.Row(
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    spacing=8,
                                    controls=location_chips
                                ),
                                ft.Divider(height=1),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            tight=True,
                                            spacing=6,
                                            controls=[
                                                ft.Icon(ft.Icons.RADAR, color=AppColors.PRIMARY, size=20),
                                                ft.Text(f"Радиус {self.selected_radius_km} км вокруг «{selected_loc_name}»:", size=14, weight=ft.FontWeight.BOLD)
                                            ]
                                        ),
                                        ft.Container(
                                            padding=ft.Padding.symmetric(horizontal=10, vertical=3),
                                            border_radius=12,
                                            bgcolor=AppColors.PRIMARY_CONTAINER,
                                            content=ft.Text(f"Найдено видов: {len(species_result_cards)}", size=11, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD)
                                        )
                                    ]
                                ),
                                ft.ResponsiveRow(
                                    spacing=10,
                                    run_spacing=10,
                                    controls=species_result_cards if species_result_cards else [
                                        ft.Container(
                                            col={"sm": 12},
                                            padding=30,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Text("В этом узком радиусе редких видов не зафиксировано. Попробуйте увеличить радиус до 15 или 30 км.", color=ft.Colors.GREY_600)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ),
                # Информационный блок по географической подложке
                ft.Card(
                    elevation=1,
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Картографическая подложка OpenStreetMap (Беларусь):" if lang == "ru" else "Картаграфічная падложка OpenStreetMap (Беларусь):", weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text("Координаты WGS-84", size=11, color=AppColors.TEXT_MUTED_LIGHT)
                                    ]
                                ),
                                ft.Container(
                                    height=280,
                                    border_radius=12,
                                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                                    content=ft.Image(
                                        src="/geo/belarus_map_preview.png",
                                        fit="contain",
                                        height=280
                                    )
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.FilledButton(
                                            icon=ft.Icons.MAP,
                                            content=ft.Text("Открыть динамический Leaflet-слой с зумом и перемещением" if lang == "ru" else "Адкрыць дынамічны Leaflet-слой з зумам", weight=ft.FontWeight.BOLD),
                                            on_click=lambda e: open_target("/map/index.html", self.page)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ),
                ft.Container(height=24) # Bottom padding
            ]
        )

    def _change_radius(self, val: int):
        self.selected_radius_km = val
        self._build_ui()
        self.update()

    def _select_location(self, loc: dict):
        self.selected_location = loc
        self._build_ui()
        self.update()
