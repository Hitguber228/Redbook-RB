import flet as ft
from typing import Callable, Optional
from ...database.db import db_manager
from ..theme import AppColors, get_category_color

class CatalogView(ft.Container):
    def __init__(self, on_select_species: Callable[[str], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.on_select_species = on_select_species
        self.get_language = get_language
        self.search_query = ""
        self.selected_category: Optional[str] = None
        self.selected_kingdom: Optional[str] = None
        self.selected_region: Optional[str] = None

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()

        # Поисковая строка
        self.search_field = ft.TextField(
            hint_text="Поиск по названию или латыни... (напр. Зубр, Ciconia)" if lang == "ru" else "Пошук па назве ці латыні... (напр. Зубр, Ciconia)",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            on_change=self._on_search_change,
            expand=True
        )

        # Чипсы категорий I - IV
        self.category_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=[
                ft.Chip(
                    label=ft.Text("Все категории" if lang == "ru" else "Усе катэгорыі"),
                    selected=(self.selected_category is None),
                    on_select=lambda e: self._select_category(None)
                ),
                ft.Chip(
                    label=ft.Text("I (CR)", color=AppColors.CAT_I, weight=ft.FontWeight.BOLD),
                    selected=(self.selected_category == "I"),
                    on_select=lambda e: self._select_category("I")
                ),
                ft.Chip(
                    label=ft.Text("II (EN)", color=AppColors.CAT_II, weight=ft.FontWeight.BOLD),
                    selected=(self.selected_category == "II"),
                    on_select=lambda e: self._select_category("II")
                ),
                ft.Chip(
                    label=ft.Text("III (VU)", color=AppColors.CAT_III, weight=ft.FontWeight.BOLD),
                    selected=(self.selected_category == "III"),
                    on_select=lambda e: self._select_category("III")
                ),
                ft.Chip(
                    label=ft.Text("IV (NT)", color=AppColors.CAT_IV, weight=ft.FontWeight.BOLD),
                    selected=(self.selected_category == "IV"),
                    on_select=lambda e: self._select_category("IV")
                )
            ]
        )

        # Чипсы царств (Животные, Растения, Грибы)
        self.kingdom_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=[
                ft.Chip(
                    label=ft.Text("Все царства" if lang == "ru" else "Усе царствы"),
                    selected=(self.selected_kingdom is None),
                    on_select=lambda e: self._select_kingdom(None)
                ),
                ft.Chip(
                    label=ft.Text("🐾 Животные" if lang == "ru" else "🐾 Жывёлы"),
                    selected=(self.selected_kingdom == "animals"),
                    on_select=lambda e: self._select_kingdom("animals")
                ),
                ft.Chip(
                    label=ft.Text("🌿 Растения" if lang == "ru" else "🌿 Расліны"),
                    selected=(self.selected_kingdom == "plants"),
                    on_select=lambda e: self._select_kingdom("plants")
                ),
                ft.Chip(
                    label=ft.Text("🍄 Грибы" if lang == "ru" else "🍄 Грыбы"),
                    selected=(self.selected_kingdom == "fungi"),
                    on_select=lambda e: self._select_kingdom("fungi")
                )
            ]
        )

        # Сетка карточек видов
        self.grid_container = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16
        )

        self._refresh_species_list()

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.all(16),
            spacing=14,
            controls=[
                self.search_field,
                ft.Text("Охранный статус в Республике Беларусь:" if lang == "ru" else "Ахоўны статус у Рэспубліцы Беларусь:", size=13, weight=ft.FontWeight.W_500, color=AppColors.TEXT_MUTED_LIGHT),
                self.category_row,
                self.kingdom_row,
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                self.grid_container
            ]
        )

    def _select_category(self, cat: Optional[str]):
        self.selected_category = cat
        self._build_ui()
        self.update()

    def _select_kingdom(self, k: Optional[str]):
        self.selected_kingdom = k
        self._build_ui()
        self.update()

    def _on_search_change(self, e):
        self.search_query = e.control.value
        self._refresh_species_list()
        self.grid_container.update()

    def _refresh_species_list(self):
        species_list = db_manager.get_species(
            query=self.search_query,
            category=self.selected_category,
            kingdom=self.selected_kingdom,
            region=self.selected_region
        )

        self.grid_container.controls.clear()
        lang = self.get_language()

        if not species_list:
            self.grid_container.controls.append(
                ft.Container(
                    col={"sm": 12},
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=56, color=ft.Colors.GREY_400),
                            ft.Text("Виды не найдены" if lang == "ru" else "Віды не знойдзены", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Попробуйте изменить параметры поиска или фильтров" if lang == "ru" else "Паспрабуйце змяніць параметры пошуку ці фільтраў", color=ft.Colors.GREY_600)
                        ]
                    )
                )
            )
            return

        for sp in species_list:
            card = self._create_species_card(sp, lang)
            self.grid_container.controls.append(card)

    def _create_species_card(self, sp: dict, lang: str) -> ft.Control:
        cat_color = get_category_color(sp["category"])
        title = sp["name_be"] if lang == "be" else sp["name_ru"]

        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.BLACK_12),
            ink=True,
            on_click=lambda e, sid=sp["id"]: self.on_select_species(sid),
            content=ft.Column(
                spacing=0,
                controls=[
                    # Фото вида с бейджем категории
                    ft.Stack(
                        controls=[
                            ft.Image(
                                src=sp["image_url"],
                                height=180,
                                width=float("inf"),
                                fit="cover",
                            ),
                            # Бейдж категории
                            ft.Container(
                                top=12,
                                left=12,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=20,
                                bgcolor=cat_color,
                                content=ft.Row(
                                    tight=True,
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.SHIELD, size=14, color=ft.Colors.WHITE),
                                        ft.Text(f"Категория {sp['category']}" if lang == "ru" else f"Катэгорыя {sp['category']}", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                    ]
                                )
                            ),
                            # Индикатор наличия звука
                            ft.Container(
                                top=12,
                                right=12,
                                visible=bool(sp.get("sound_url")),
                                padding=ft.Padding.all(6),
                                border_radius=20,
                                bgcolor=ft.Colors.BLACK_54,
                                content=ft.Icon(ft.Icons.VOLUME_UP, size=16, color=ft.Colors.WHITE)
                            )
                        ]
                    ),
                    # Описание карточки
                    ft.Container(
                        padding=14,
                        content=ft.Column(
                            spacing=6,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text(
                                    title,
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                ft.Text(
                                    sp["name_lat"],
                                    size=13,
                                    italic=True,
                                    color=AppColors.TEXT_MUTED_LIGHT
                                ),
                                ft.Text(
                                    sp["habitat"],
                                    size=12,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    color=ft.Colors.GREY_700
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"📍 {len(sp['distribution_rb'])} обл." if lang == "ru" else f"📍 {len(sp['distribution_rb'])} вобл.",
                                            size=11,
                                            color=AppColors.PRIMARY
                                        ),
                                        ft.TextButton(
                                            "Подробнее" if lang == "ru" else "Падрабязней",
                                            icon=ft.Icons.ARROW_FORWARD,
                                            on_click=lambda e, sid=sp["id"]: self.on_select_species(sid)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )

