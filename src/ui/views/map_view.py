import flet as ft
import json
import os
from typing import Callable, Optional, List, Dict
from ...database.db import db_manager
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

REGION_EMOJIS = {
    "brest": "🌲",
    "vitebsk": "💧",
    "gomel": "🪵",
    "grodno": "🏰",
    "minsk": "🏛️",
    "mogilev": "🌊"
}

class MapView(ft.Container):
    def __init__(self, on_select_species: Callable[[str], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.on_select_species = on_select_species
        self.get_language = get_language
        self.geo_data = self._load_geo()
        self.selected_park_id = "belovezhskaya-pushcha"
        self.selected_region_id: str = "brest"

        self._build_ui()

    def _load_geo(self):
        if os.path.exists(GEO_PATH):
            with open(GEO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"regions": [], "national_parks": []}

    def _build_ui(self):
        lang = self.get_language()
        parks = self.geo_data.get("national_parks", [])
        regions = self.geo_data.get("regions", [])

        # Выбранный нацпарк
        selected_park = next((p for p in parks if p["id"] == self.selected_park_id), parks[0] if parks else None)

        # Карточки заповедников
        park_cards = []
        for p in parks:
            is_active = (p["id"] == self.selected_park_id)
            title = p["name_be"] if lang == "be" else p["name_ru"]
            park_cards.append(
                ft.Container(
                    width=280,
                    padding=14,
                    border_radius=14,
                    bgcolor=AppColors.PRIMARY_CONTAINER if is_active else ft.Colors.SURFACE,
                    border=ft.Border.all(2 if is_active else 1, AppColors.PRIMARY if is_active else ft.Colors.OUTLINE_VARIANT),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.BLACK_12) if is_active else None,
                    ink=True,
                    on_click=lambda e, pid=p["id"]: self._select_park(pid),
                    content=ft.Column(
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(title, weight=ft.FontWeight.BOLD, size=13, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Icon(ft.Icons.CHECK_CIRCLE if is_active else ft.Icons.PARK, size=16, color=AppColors.PRIMARY if is_active else ft.Colors.GREY_500)
                                ]
                            ),
                            ft.Text(f"🌲 {p['area_sq_km']:,} км² • Засн. {p['established_year']} г.".replace(",", " "), size=11, color=AppColors.TEXT_MUTED_LIGHT),
                        ]
                    )
                )
            )

        # Детальная карточка выбранного заповедника
        detail_card = ft.Container()
        if selected_park:
            p_title = selected_park["name_be"] if lang == "be" else selected_park["name_ru"]
            key_species_chips = [
                ft.Chip(
                    label=ft.Text(sp_name, size=11, weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.WHITE,
                    on_click=lambda e, name=sp_name: self._find_and_open_species(name)
                )
                for sp_name in selected_park.get("key_species", [])
            ]

            detail_card = ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=18,
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        tight=True,
                                        spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.FOREST, color=AppColors.PRIMARY, size=24),
                                            ft.Text(p_title, size=18, weight=ft.FontWeight.BOLD)
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=12,
                                        bgcolor=AppColors.PRIMARY_CONTAINER,
                                        content=ft.Text(f"📍 GPS: {selected_park['center'][0]:.2f}, {selected_park['center'][1]:.2f}", size=11, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD)
                                    )
                                ]
                            ),
                            ft.Text(selected_park["description_ru"], size=13),
                            ft.Divider(height=1),
                            ft.Text("Особо охраняемые виды территории (нажмите для перехода):" if lang == "ru" else "Асабліва ахоўныя віды тэрыторыі (націсніце для пераходу):", weight=ft.FontWeight.BOLD, size=12),
                            ft.Row(wrap=True, spacing=6, controls=key_species_chips)
                        ]
                    )
                )
            )

        # Карточки 6 областей с индикатором активности и кликабельностью
        region_rows = []
        for r in regions:
            r_title = r["name_be"] if lang == "be" else r["name_ru"]
            is_active_region = (r["id"] == self.selected_region_id)
            r_prefix = REGION_PREFIX_MAP.get(r["id"], "")
            sp_count = len(db_manager.get_species(region=r_prefix)) if r_prefix else 0
            emoji = REGION_EMOJIS.get(r["id"], "📍")

            region_rows.append(
                ft.Container(
                    col={"sm": 12, "md": 6, "lg": 4},
                    padding=16,
                    border_radius=16,
                    bgcolor=ft.Colors.GREEN_50 if is_active_region else ft.Colors.SURFACE,
                    border=ft.Border.all(2 if is_active_region else 1, AppColors.PRIMARY if is_active_region else ft.Colors.OUTLINE_VARIANT),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.BLACK_12) if is_active_region else None,
                    ink=True,
                    on_click=lambda e, rid=r["id"]: self._select_region(rid),
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        tight=True,
                                        spacing=8,
                                        controls=[
                                            ft.Text(emoji, size=20),
                                            ft.Text(r_title, weight=ft.FontWeight.BOLD, size=15)
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=10,
                                        bgcolor=AppColors.PRIMARY if is_active_region else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                        content=ft.Text(
                                            f"{sp_count} видов" if lang == "ru" else f"{sp_count} відаў",
                                            size=10,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE if is_active_region else ft.Colors.GREY_700
                                        )
                                    )
                                ]
                            ),
                            ft.Text(f"Площадь: {r['area_sq_km']:,} км²".replace(",", " "), size=11, color=AppColors.TEXT_MUTED_LIGHT),
                            ft.Text(r["description_ru"], size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.ON_SURFACE_VARIANT)
                        ]
                    )
                )
            )

        # Блок видов выбранной области
        selected_region_data = next((r for r in regions if r["id"] == self.selected_region_id), None)
        region_species_cards = []
        if selected_region_data:
            prefix = REGION_PREFIX_MAP.get(self.selected_region_id, "")
            species_in_reg = db_manager.get_species(region=prefix) if prefix else []

            for sp in species_in_reg:
                sp_name = sp["name_be"] if lang == "be" else sp["name_ru"]
                cat_color = get_category_color(sp["category"])
                region_species_cards.append(
                    ft.Container(
                        col={"sm": 12, "md": 6, "lg": 4},
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.Colors.SURFACE,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        ink=True,
                        on_click=lambda e, sid=sp["id"]: self.on_select_species(sid),
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(
                                    width=54,
                                    height=54,
                                    border_radius=10,
                                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                    content=ft.Image(src=sp["image_url"], fit="cover")
                                ),
                                ft.Column(
                                    spacing=2,
                                    expand=True,
                                    controls=[
                                        ft.Text(sp_name, weight=ft.FontWeight.BOLD, size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(sp["name_lat"], italic=True, size=11, color=AppColors.TEXT_MUTED_LIGHT),
                                        ft.Row(
                                            tight=True,
                                            spacing=4,
                                            controls=[
                                                ft.Container(
                                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                                    border_radius=6,
                                                    bgcolor=cat_color,
                                                    content=ft.Text(f"Кат. {sp['category']}", size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                                ),
                                                ft.Text(sp["taxon_group"].capitalize(), size=10, color=ft.Colors.GREY_600)
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )

        selected_reg_title = (selected_region_data["name_be"] if lang == "be" else selected_region_data["name_ru"]) if selected_region_data else ""

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            spacing=18,
            controls=[
                # Заголовок
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "География охраны природы Республики Беларусь" if lang == "ru" else "Геаграфія аховы прыроды Рэспублікі Беларусь",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Интерактивный атлас ареалов видов, 6 областей и национальных парков." if lang == "ru" else "Інтэрактыўны атлас арэалаў відаў, 6 абласцей і нацыянальных паркаў.",
                            size=13,
                            color=AppColors.TEXT_MUTED_LIGHT
                        )
                    ]
                ),
                # Плашка министерского протокола безопасности
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_50,
                    border=ft.Border.all(1, ft.Colors.BLUE_200),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.SECURITY, color=ft.Colors.BLUE_800, size=22),
                            ft.Text(
                                "Этический протокол: в открытом атласе точные GPS-координаты редких гнездовий и нор генерализованы до границ ООПТ для предотвращения браконьерства." if lang == "ru" else "Этычны пратакол: у адкрытым атласе каардынаты рэдкіх гнёздаў і нор абагульнены да межаў АПТ для аховы ад браканьерства.",
                                size=11,
                                color=ft.Colors.BLUE_900,
                                expand=True
                            )
                        ]
                    )
                ),
                # Блок 6 областей Беларуси (Интерактивные плитки)
                ft.Text("Природные зоны 6 областей Беларуси (нажмите на область для просмотра видов):" if lang == "ru" else "Прыродныя зоны 6 абласцей Беларусі (націсніце на вобласць для прагляду відаў):", weight=ft.FontWeight.BOLD, size=15),
                ft.ResponsiveRow(
                    spacing=12,
                    run_spacing=12,
                    controls=region_rows
                ),
                # Выпадающий список видов выбранной области
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
                                        ft.Text(f"Редкие виды: {selected_reg_title}" if lang == "ru" else f"Рэдкія віды: {selected_reg_title}", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Найдено: {len(region_species_cards)}", size=12, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD)
                                    ]
                                ),
                                ft.Divider(height=1),
                                ft.ResponsiveRow(
                                    spacing=10,
                                    run_spacing=10,
                                    controls=region_species_cards
                                )
                            ]
                        )
                    )
                ),
                ft.Divider(height=1),
                # Национальные парки и биосферные заповедники
                ft.Text("Национальные парки и биосферные заповедники Беларуси:" if lang == "ru" else "Нацыянальныя паркі і біясферныя запаведнікі Беларусі:", weight=ft.FontWeight.BOLD, size=15),
                ft.Row(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=12,
                    controls=park_cards
                ),
                detail_card,
                ft.Container(height=24) # Bottom padding
            ]
        )

    def _select_park(self, pid: str):
        self.selected_park_id = pid
        self._build_ui()
        self.update()

    def _select_region(self, rid: str):
        self.selected_region_id = rid
        self._build_ui()
        self.update()

    def _find_and_open_species(self, species_name: str):
        all_sp = db_manager.get_species()
        for s in all_sp:
            if s["name_ru"].lower() in species_name.lower() or s["name_be"].lower() in species_name.lower():
                self.on_select_species(s["id"])
                return
