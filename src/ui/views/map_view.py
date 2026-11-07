import flet as ft
import json
import os
from typing import Callable
from ...database.db import db_manager
from ..theme import AppColors

GEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "geo", "belarus_geo.json"))

class MapView(ft.Container):
    def __init__(self, on_select_species: Callable[[str], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.on_select_species = on_select_species
        self.get_language = get_language
        self.geo_data = self._load_geo()
        self.selected_park_id = "belovezhskaya-pushcha"

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

        park_cards = []
        for p in parks:
            is_active = (p["id"] == self.selected_park_id)
            title = p["name_be"] if lang == "be" else p["name_ru"]
            park_cards.append(
                ft.Container(
                    width=260,
                    padding=14,
                    border_radius=12,
                    bgcolor=AppColors.PRIMARY_CONTAINER if is_active else ft.Colors.SURFACE,
                    border=ft.border.all(2 if is_active else 1, AppColors.PRIMARY if is_active else ft.Colors.OUTLINE_VARIANT),
                    ink=True,
                    on_click=lambda e, pid=p["id"]: self._select_park(pid),
                    content=ft.Column(
                        spacing=4,
                        cross_axis_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=13, max_lines=2),
                            ft.Text(f"🌲 {p['area_sq_km']} км² • Осн. {p['established_year']} г.", size=11, color=AppColors.TEXT_MUTED_LIGHT),
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
                    label=ft.Text(sp_name, size=11),
                    bgcolor=ft.Colors.WHITE,
                    on_click=lambda e, name=sp_name: self._find_and_open_species(name)
                )
                for sp_name in selected_park.get("key_species", [])
            ]

            detail_card = ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        spacing=10,
                        cross_axis_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(p_title, size=17, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"📍 GPS: {selected_park['center'][0]:.2f}, {selected_park['center'][1]:.2f}", size=11, color=AppColors.PRIMARY)
                                ]
                            ),
                            ft.Text(selected_park["description_ru"], size=13, line_height=1.4),
                            ft.Divider(height=1),
                            ft.Text("Особо охраняемые виды территории:" if lang == "ru" else "Асабліва ахоўныя віды тэрыторыі:", weight=ft.FontWeight.BOLD, size=12),
                            ft.Row(wrap=True, spacing=6, controls=key_species_chips)
                        ]
                    )
                )
            )

        # Карточки областей
        region_rows = []
        for r in regions:
            r_title = r["name_be"] if lang == "be" else r["name_ru"]
            region_rows.append(
                ft.Container(
                    col={"sm": 12, "md": 6, "lg": 4},
                    padding=12,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(width=12, height=12, border_radius=6, bgcolor=r["color"]),
                                    ft.Text(r_title, weight=ft.FontWeight.BOLD, size=14)
                                ]
                            ),
                            ft.Text(f"Площадь: {r['area_sq_km']:,} км²".replace(",", " "), size=11, color=AppColors.TEXT_MUTED_LIGHT),
                            ft.Text(r["description_ru"], size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                        ]
                    )
                )
            )

        self.content = ft.ListView(
            expand=True,
            padding=ft.padding.all(16),
            spacing=16,
            controls=[
                # Заголовок и пояснение
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "География охраны природы Республики Беларусь" if lang == "ru" else "Геаграфія аховы прыроды Рэспублікі Беларусь",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Интерактивная карта ареалов, национальных парков и биосферных заповедников." if lang == "ru" else "Інтэрактыўная карта арэалаў, нацыянальных паркаў і біясферных запаведнікаў.",
                            size=13,
                            color=AppColors.TEXT_MUTED_LIGHT
                        )
                    ]
                ),
                # Плашка безопасности
                ft.Container(
                    padding=12,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.SECURITY, color=ft.Colors.BLUE_800, size=20),
                            ft.Text(
                                "Этический протокол: в открытом приложении координаты редких видов генерализованы до границ ООПТ для защиты от браконьеров." if lang == "ru" else "Этычны пратакол: у дадатку каардынаты рэдкіх відаў абагульнены да межаў АПТ для аховы ад браканьераў.",
                                size=11,
                                color=ft.Colors.BLUE_900,
                                expand=True
                            )
                        ]
                    )
                ),
                ft.Text("Национальные парки и ключевые заказники:" if lang == "ru" else "Нацыянальныя паркі і ключавыя заказнікі:", weight=ft.FontWeight.BOLD, size=15),
                ft.Row(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=10,
                    controls=park_cards
                ),
                detail_card,
                ft.Divider(height=1),
                ft.Text("6 областей Беларуси (природные зоны):" if lang == "ru" else "6 абласцей Беларусі (прыродныя зоны):", weight=ft.FontWeight.BOLD, size=15),
                ft.ResponsiveRow(
                    spacing=12,
                    run_spacing=12,
                    controls=region_rows
                )
            ]
        )

    def _select_park(self, pid: str):
        self.selected_park_id = pid
        self._build_ui()
        self.update()

    def _find_and_open_species(self, species_name: str):
        all_sp = db_manager.get_species()
        for s in all_sp:
            if s["name_ru"].lower() in species_name.lower() or s["name_be"].lower() in species_name.lower():
                self.on_select_species(s["id"])
                return
