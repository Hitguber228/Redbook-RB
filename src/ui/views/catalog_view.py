import flet as ft
from typing import Callable, Optional
from ...database.db import db_manager
from ...database.species_be_data import SPECIES_BE_TRANSLATIONS
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
        self.has_sound_only: bool = False

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()
        is_filtered = bool(
            self.search_query or
            self.selected_category or
            self.selected_kingdom or
            self.selected_region or
            self.has_sound_only
        )

        # 1. Поисковая строка с подсказкой и кнопкой быстрой очистки
        self.search_field = ft.TextField(
            hint_text="Поиск по названию или латыни... (напр. Зубр, Ciconia, Рысь)" if lang == "ru" else "Пошук па назве ці латыні... (напр. Зубр, Ciconia, Рысь)",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_color=ft.Colors.TRANSPARENT,
            value=self.search_query,
            on_change=self._on_search_change,
            suffix=ft.IconButton(
                icon=ft.Icons.CLEAR,
                icon_size=18,
                tooltip="Очистить поиск" if lang == "ru" else "Ачысціць пошук",
                on_click=self._clear_search,
                visible=bool(self.search_query)
            ),
            expand=True
        )

        # 2. Фильтр царств (строго без эмодзи, только чистые векторные иконки)
        kingdom_items = [
            (None, "Все царства" if lang == "ru" else "Усе царствы", ft.Icons.ALL_INCLUSIVE),
            ("animals", "Животные" if lang == "ru" else "Жывёлы", ft.Icons.PETS),
            ("plants", "Растения" if lang == "ru" else "Расліны", ft.Icons.ECO),
            ("fungi", "Грибы" if lang == "ru" else "Грыбы", ft.Icons.FOREST),
        ]
        kingdom_chips = []
        for k_id, k_label, k_icon in kingdom_items:
            is_sel = (self.selected_kingdom == k_id)
            kingdom_chips.append(
                ft.Chip(
                    leading=ft.Icon(k_icon, size=15, color=AppColors.PRIMARY if is_sel else ft.Colors.ON_SURFACE_VARIANT),
                    label=ft.Text(k_label, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500),
                    selected=is_sel,
                    on_select=lambda e, k=k_id: self._select_kingdom(k)
                )
            )

        self.kingdom_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=kingdom_chips
        )

        # 3. Фильтр категорий охраны (официальные цвета Красной книги: I CR, II EN, III VU, IV NT)
        cat_items = [
            (None, "Все категории" if lang == "ru" else "Усе катэгорыі", None, None),
            ("I", "I (CR)", AppColors.CAT_I, "На грани исчезновения" if lang == "ru" else "На мяжы знікнення"),
            ("II", "II (EN)", AppColors.CAT_II, "Исчезающие виды" if lang == "ru" else "Знікаючыя віды"),
            ("III", "III (VU)", AppColors.CAT_III, "Уязвимые виды" if lang == "ru" else "Уразлівыя віды"),
            ("IV", "IV (NT)", AppColors.CAT_IV, "Требующие контроля" if lang == "ru" else "Патрабуюць кантролю"),
        ]
        cat_chips = []
        for c_id, c_label, c_color, c_tooltip in cat_items:
            is_sel = (self.selected_category == c_id)
            if c_color:
                label_ctrl = ft.Row(
                    tight=True,
                    spacing=5,
                    controls=[
                        ft.Icon(ft.Icons.SHIELD, size=13, color=c_color),
                        ft.Text(c_label, color=c_color if not is_sel else None, weight=ft.FontWeight.BOLD)
                    ]
                )
            else:
                label_ctrl = ft.Text(c_label, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500)

            cat_chips.append(
                ft.Chip(
                    label=label_ctrl,
                    tooltip=c_tooltip,
                    selected=is_sel,
                    on_select=lambda e, c=c_id: self._select_category(c)
                )
            )

        self.category_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=cat_chips
        )

        # 4. Умная строка дополнительных фильтров (Область Беларуси + Аудиозапись + Сброс)
        region_options_ru = [
            ("all", "Все области Беларуси"),
            ("Брестская", "Брестская область"),
            ("Витебская", "Витебская область"),
            ("Гомельская", "Гомельская область"),
            ("Гродненская", "Гродненская область"),
            ("Минская", "Минская область"),
            ("Могилевская", "Могилевская область"),
        ]
        region_options_be = [
            ("all", "Усе вобласці Беларусі"),
            ("Брэсцкая", "Брэсцкая вобласць"),
            ("Віцебская", "Віцебская вобласць"),
            ("Гомельская", "Гомельская вобласць"),
            ("Гродзенская", "Гродзенская вобласць"),
            ("Мінская", "Мінская вобласць"),
            ("Магілёўская", "Магілёўская вобласць"),
        ]
        region_options = region_options_ru if lang == "ru" else region_options_be

        current_reg_val = self.selected_region if self.selected_region else "all"

        self.region_dropdown = ft.Dropdown(
            value=current_reg_val,
            options=[ft.dropdown.Option(val, text) for val, text in region_options],
            prefix_icon=ft.Icons.MAP_OUTLINED,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_change=self._on_region_change,
            width=230
        )

        self.sound_chip = ft.Chip(
            leading=ft.Icon(ft.Icons.VOLUME_UP, size=15, color=AppColors.PRIMARY if self.has_sound_only else ft.Colors.ON_SURFACE_VARIANT),
            label=ft.Text("С аудиозаписью" if lang == "ru" else "З аўдыязапісам", weight=ft.FontWeight.BOLD if self.has_sound_only else ft.FontWeight.W_500),
            selected=self.has_sound_only,
            on_select=self._toggle_sound_filter
        )

        reset_btn = ft.TextButton(
            icon=ft.Icons.RESTART_ALT,
            text="Сбросить все" if lang == "ru" else "Скінуць усё",
            style=ft.ButtonStyle(color=ft.Colors.RED_600),
            visible=is_filtered,
            on_click=self._reset_all_filters
        )

        self.smart_filter_row = ft.Row(
            wrap=True,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.region_dropdown,
                self.sound_chip,
                reset_btn
            ]
        )

        # 5. Сетка карточек видов
        self.grid_container = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16
        )

        self.count_text = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY)

        self._refresh_species_list()

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            spacing=12,
            controls=[
                self.search_field,
                self.kingdom_row,
                self.category_row,
                self.smart_filter_row,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Реестр редких видов Беларуси:" if lang == "ru" else "Рэестр рэдкіх відаў Беларусі:",
                            size=13,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.count_text
                    ]
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                self.grid_container,
                ft.Container(height=24) # Bottom padding
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

    def _on_region_change(self, e):
        val = e.control.value
        self.selected_region = None if val == "all" else val
        self._build_ui()
        self.update()

    def _toggle_sound_filter(self, e):
        self.has_sound_only = not self.has_sound_only
        self._build_ui()
        self.update()

    def _clear_search(self, e):
        self.search_query = ""
        self.search_field.value = ""
        self._build_ui()
        self.update()

    def _reset_all_filters(self, e):
        self.search_query = ""
        self.selected_category = None
        self.selected_kingdom = None
        self.selected_region = None
        self.has_sound_only = False
        self._build_ui()
        self.update()

    def _on_search_change(self, e):
        self.search_query = e.control.value
        if self.search_field.suffix:
            self.search_field.suffix.visible = bool(self.search_query)
            self.search_field.update()
        self._refresh_species_list()
        self.grid_container.update()
        self.count_text.update()

    def _refresh_species_list(self):
        species_list = db_manager.get_species(
            query=self.search_query,
            category=self.selected_category,
            kingdom=self.selected_kingdom,
            region=self.selected_region,
            has_sound_only=self.has_sound_only
        )

        self.grid_container.controls.clear()
        lang = self.get_language()

        self.count_text.value = f"Найдено: {len(species_list)}" if lang == "ru" else f"Знойдзена: {len(species_list)}"

        if not species_list:
            self.grid_container.controls.append(
                ft.Container(
                    col={"sm": 12},
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=56, color=ft.Colors.GREY_400),
                            ft.Text("Виды не найдены" if lang == "ru" else "Віды не знойдзены", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Попробуйте сбросить фильтры или ввести другое название" if lang == "ru" else "Паспрабуйце скінуць фільтры ці ўвесці іншую назву", color=ft.Colors.GREY_600),
                            ft.ElevatedButton(
                                icon=ft.Icons.RESTART_ALT,
                                text="Сбросить все фильтры" if lang == "ru" else "Скінуць усе фільтры",
                                on_click=self._reset_all_filters
                            )
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

        # Значок царства — чистый векторный значок Material Icons (без эмодзи!)
        if sp["kingdom"] == "animals":
            k_icon_ctrl = ft.Icon(ft.Icons.PETS, size=14, color=ft.Colors.WHITE)
        elif sp["kingdom"] == "plants":
            k_icon_ctrl = ft.Icon(ft.Icons.ECO, size=14, color=ft.Colors.WHITE)
        else:
            k_icon_ctrl = ft.Icon(ft.Icons.FOREST, size=14, color=ft.Colors.WHITE)

        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.BLACK_12),
            ink=True,
            on_click=lambda e, sid=sp["id"]: self.on_select_species(sid),
            content=ft.Column(
                spacing=0,
                controls=[
                    # Фото вида с бейджем категории и звука
                    ft.Stack(
                        controls=[
                            ft.Image(
                                src=sp["image_url"],
                                height=200,
                                width=float("inf"),
                                fit="cover",
                            ),
                            # Бейдж категории
                            ft.Container(
                                top=10,
                                left=10,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=16,
                                bgcolor=cat_color,
                                content=ft.Row(
                                    tight=True,
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.SHIELD, size=14, color=ft.Colors.WHITE),
                                        ft.Text(f"Кат. {sp['category']}", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                    ]
                                )
                            ),
                            # Бейдж царства (Векторная иконка)
                            ft.Container(
                                top=10,
                                right=10,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                border_radius=16,
                                bgcolor=ft.Colors.BLACK_54,
                                content=k_icon_ctrl
                            ),
                            # Индикатор наличия звука (снизу фото)
                            ft.Container(
                                bottom=10,
                                right=10,
                                visible=bool(sp.get("sound_url")),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                border_radius=12,
                                bgcolor=ft.Colors.BLACK_54,
                                content=ft.Row(
                                    tight=True,
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.VOLUME_UP, size=14, color=ft.Colors.WHITE),
                                        ft.Text("Аудио" if lang == "ru" else "Аўдыя", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                    ]
                                )
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
                                    SPECIES_BE_TRANSLATIONS.get(sp["id"], {}).get("habitat", sp["habitat"]) if lang == "be" else sp["habitat"],
                                    size=12,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                                ft.Divider(height=1),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            tight=True,
                                            spacing=3,
                                            controls=[
                                                ft.Icon(ft.Icons.LOCATION_ON, size=14, color=AppColors.PRIMARY),
                                                ft.Text(
                                                    f"{len(sp['distribution_rb'])} обл." if lang == "ru" else f"{len(sp['distribution_rb'])} вобл.",
                                                    size=11,
                                                    weight=ft.FontWeight.W_500,
                                                    color=AppColors.PRIMARY
                                                )
                                            ]
                                        ),
                                        ft.Text(
                                            "Паспорт вида →" if lang == "ru" else "Пашпарт віду →",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=AppColors.PRIMARY
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )
