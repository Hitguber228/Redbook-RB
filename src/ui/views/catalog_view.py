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
        self.selected_taxon: Optional[str] = None
        self.selected_biotope: Optional[str] = None
        self.selected_region: Optional[str] = None
        self.selected_national_park: Optional[str] = None
        self.sort_by: str = "name_asc"
        self.has_sound_only: bool = False
        self.visible_count: int = 36
        self.filters_expanded: bool = False

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()

        # Подсчет активных детальных фильтров
        adv_active_count = sum([
            1 if self.selected_taxon else 0,
            1 if self.selected_region else 0,
            1 if self.selected_biotope else 0,
            1 if self.selected_national_park else 0,
            1 if self.has_sound_only else 0
        ])
        total_active_count = adv_active_count + (1 if self.selected_kingdom else 0) + (1 if self.selected_category else 0) + (1 if self.search_query else 0)

        # 1. Поисковая строка в современном дизайне с кнопкой фильтров
        self.search_field = ft.TextField(
            hint_text="Поиск по названию или латыни... (Зубр, Рысь, Ciconia)" if lang == "ru" else "Пошук па назве ці латыні... (Зубр, Рысь, Ciconia)",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=14,
            filled=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_color=ft.Colors.OUTLINE_VARIANT,
            focused_border_color=AppColors.PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            value=self.search_query,
            on_change=self._on_search_change,
            suffix=ft.IconButton(
                icon=ft.Icons.CLEAR,
                icon_size=16,
                tooltip="Очистить поиск" if lang == "ru" else "Ачысціць пошук",
                on_click=self._clear_search,
                visible=bool(self.search_query)
            ),
            expand=True
        )

        # Кнопка открытия/закрытия панели расширенных фильтров
        filter_btn_active = self.filters_expanded or (adv_active_count > 0)
        filter_toggle_btn = ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border_radius=14,
            bgcolor=AppColors.PRIMARY_CONTAINER if filter_btn_active else ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(
                1.5 if filter_btn_active else 1,
                AppColors.PRIMARY if filter_btn_active else ft.Colors.OUTLINE_VARIANT
            ),
            ink=True,
            on_click=self._toggle_filters_panel,
            tooltip="Параметры фильтрации" if lang == "ru" else "Параметры фільтрацыі",
            content=ft.Row(
                tight=True,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.TUNE,
                        size=18,
                        color=AppColors.PRIMARY if filter_btn_active else ft.Colors.ON_SURFACE
                    ),
                    ft.Text(
                        "Фильтры" if lang == "ru" else "Фільтры",
                        size=13,
                        weight=ft.FontWeight.BOLD if filter_btn_active else ft.FontWeight.W_500,
                        color=AppColors.PRIMARY if filter_btn_active else ft.Colors.ON_SURFACE
                    ),
                    *([
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            border_radius=10,
                            bgcolor=AppColors.PRIMARY,
                            content=ft.Text(
                                str(adv_active_count),
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            )
                        )
                    ] if adv_active_count > 0 else [
                        ft.Icon(
                            ft.Icons.KEYBOARD_ARROW_UP if self.filters_expanded else ft.Icons.KEYBOARD_ARROW_DOWN,
                            size=16,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ])
                ]
            )
        )

        top_search_row = ft.Row(
            spacing=10,
            controls=[
                self.search_field,
                filter_toggle_btn
            ]
        )

        # 2. Сегментированный фильтр царств (современные скругленные капсулы)
        kingdom_items = [
            (None, "Все виды (515)" if lang == "ru" else "Усе віды (515)", ft.Icons.ALL_INCLUSIVE),
            ("animals", "Животные (213)" if lang == "ru" else "Жывёлы (213)", ft.Icons.PETS),
            ("plants", "Растения (245)" if lang == "ru" else "Расліны (245)", ft.Icons.ECO),
            ("fungi", "Грибы (57)" if lang == "ru" else "Грыбы (57)", ft.Icons.FOREST),
        ]
        kingdom_pills = []
        for k_id, k_label, k_icon in kingdom_items:
            is_sel = (self.selected_kingdom == k_id)
            kingdom_pills.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    border_radius=16,
                    bgcolor=AppColors.PRIMARY if is_sel else ft.Colors.SURFACE_CONTAINER_LOW,
                    border=ft.Border.all(
                        1.5 if is_sel else 1,
                        AppColors.PRIMARY if is_sel else ft.Colors.OUTLINE_VARIANT
                    ),
                    ink=True,
                    on_click=lambda e, k=k_id: self._select_kingdom(k),
                    content=ft.Row(
                        tight=True,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                k_icon,
                                size=15,
                                color=ft.Colors.WHITE if is_sel else AppColors.PRIMARY
                            ),
                            ft.Text(
                                k_label,
                                size=12,
                                weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500,
                                color=ft.Colors.WHITE if is_sel else ft.Colors.ON_SURFACE
                            )
                        ]
                    )
                )
            )

        kingdom_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=kingdom_pills
        )

        # 3. Фильтр категорий охраны (официальные цвета Красной книги Беларуси)
        cat_items = [
            (None, "Все категории" if lang == "ru" else "Усе катэгорыі", None, None),
            ("I", "I • CR (119)", AppColors.CAT_I, "I (CR) — На грани исчезновения" if lang == "ru" else "I (CR) — На мяжы знікнення"),
            ("II", "II • EN (151)", AppColors.CAT_II, "II (EN) — Исчезающие виды" if lang == "ru" else "II (EN) — Знікаючыя віды"),
            ("III", "III • VU (152)", AppColors.CAT_III, "III (VU) — Уязвимые виды" if lang == "ru" else "III (VU) — Уразлівыя віды"),
            ("IV", "IV • NT (93)", AppColors.CAT_IV, "IV (NT) — Требующие контроля" if lang == "ru" else "IV (NT) — Патрабуюць кантролю"),
        ]
        cat_pills = []
        for c_id, c_label, c_color, c_tooltip in cat_items:
            is_sel = (self.selected_category == c_id)
            cat_pills.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=14,
                    tooltip=c_tooltip,
                    bgcolor=c_color if (is_sel and c_color) else (AppColors.PRIMARY if (is_sel and not c_color) else ft.Colors.SURFACE_CONTAINER_LOW),
                    border=ft.Border.all(
                        1.5 if is_sel else 1,
                        (c_color or AppColors.PRIMARY) if is_sel else ft.Colors.OUTLINE_VARIANT
                    ),
                    ink=True,
                    on_click=lambda e, c=c_id: self._select_category(c),
                    content=ft.Row(
                        tight=True,
                        spacing=6,
                        controls=[
                            *( [ft.Container(width=7, height=7, border_radius=4, bgcolor=ft.Colors.WHITE if is_sel else c_color)] if c_color else [] ),
                            ft.Text(
                                c_label,
                                size=11,
                                weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500,
                                color=ft.Colors.WHITE if is_sel else (c_color if c_color else ft.Colors.ON_SURFACE)
                            )
                        ]
                    )
                )
            )

        category_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=8,
            controls=cat_pills
        )

        # 4. Выпадающие списки расширенной фильтрации
        # 4.1 Таксоны
        taxon_options_ru = [
            ("all", "Все таксоны"),
            ("mammals", "Млекопитающие (22)"),
            ("birds", "Птицы (71)"),
            ("amphibians", "Земноводные (2)"),
            ("reptiles", "Пресмыкающиеся (2)"),
            ("fish", "Рыбы и миноги (10)"),
            ("insects", "Насекомые (96)"),
            ("invertebrates", "Беспозвоночные (10)"),
            ("vascular_plants", "Сосудистые растения (185)"),
            ("mosses", "Мхи (37)"),
            ("algae", "Водоросли (23)"),
            ("mushrooms", "Грибы (29)"),
            ("lichens", "Лишайники (28)"),
        ]
        taxon_options_be = [
            ("all", "Усе таксоны"),
            ("mammals", "Ссусальныя (22)"),
            ("birds", "Птушкі (71)"),
            ("amphibians", "Земнаводныя (2)"),
            ("reptiles", "Паўзуны (2)"),
            ("fish", "Рыбы і міногі (10)"),
            ("insects", "Насякомыя (96)"),
            ("invertebrates", "Беспазваночныя (10)"),
            ("vascular_plants", "Сасудзістыя расліны (185)"),
            ("mosses", "Мхі (37)"),
            ("algae", "Водарасці (23)"),
            ("mushrooms", "Грыбы (29)"),
            ("lichens", "Лішайнікі (28)"),
        ]
        t_opts = taxon_options_ru if lang == "ru" else taxon_options_be
        current_taxon_val = self.selected_taxon if self.selected_taxon else "all"

        self.taxon_dropdown = ft.Dropdown(
            label="Таксономическая группа" if lang == "ru" else "Таксанамічная група",
            value=current_taxon_val,
            options=[ft.dropdown.Option(val, text) for val, text in t_opts],
            leading_icon=ft.Icons.CATEGORY_OUTLINED,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            dense=True,
            on_select=self._on_taxon_change,
            expand=True
        )

        # 4.2 Область Беларуси
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
        reg_opts = region_options_ru if lang == "ru" else region_options_be
        current_reg_val = self.selected_region if self.selected_region else "all"

        self.region_dropdown = ft.Dropdown(
            label="Область Беларуси" if lang == "ru" else "Вобласць Беларусі",
            value=current_reg_val,
            options=[ft.dropdown.Option(val, text) for val, text in reg_opts],
            leading_icon=ft.Icons.MAP_OUTLINED,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            dense=True,
            on_select=self._on_region_change,
            expand=True
        )

        # 4.3 Биотопы
        biotope_options_ru = [
            ("all", "Все биотопы"),
            ("forest", "Леса и дубравы (393)"),
            ("aquatic", "Водотоки и озёра (60)"),
            ("wetland", "Болота и торфяники (46)"),
            ("meadow", "Пойменные луга (16)"),
        ]
        biotope_options_be = [
            ("all", "Усе біятопы"),
            ("forest", "Лясы і дубровы (393)"),
            ("aquatic", "Вадатокі і азёры (60)"),
            ("wetland", "Балоты і тарфянікі (46)"),
            ("meadow", "Поймавыя лугі (16)"),
        ]
        b_opts = biotope_options_ru if lang == "ru" else biotope_options_be
        current_biotope_val = self.selected_biotope if self.selected_biotope else "all"

        self.biotope_dropdown = ft.Dropdown(
            label="Биотоп обитания" if lang == "ru" else "Біятоп пражывання",
            value=current_biotope_val,
            options=[ft.dropdown.Option(val, text) for val, text in b_opts],
            leading_icon=ft.Icons.FOREST_OUTLINED,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            dense=True,
            on_select=self._on_biotope_change,
            expand=True
        )

        # 4.4 ООПТ / Национальные парки
        park_options_ru = [
            ("all", "Все ООПТ и нацпарки"),
            ("Беловежская пуща", "НП «Беловежская пуща»"),
            ("Березинский", "Березинский биосферный заповедник"),
            ("Припятский", "НП «Припятский»"),
            ("Браславские", "НП «Браславские озера»"),
            ("Нарочанский", "НП «Нарочанский»"),
            ("Споровский", "Заказник «Споровский»"),
            ("Налибокская", "Заказник «Налибокская пуща»"),
            ("Красный Бор", "Заказник «Красный Бор»"),
            ("Званец", "Заказник «Званец»"),
            ("Освейский", "Заказник «Освейский»"),
            ("Полесский радиационно", "Полесский радиац.-экол. зап."),
        ]
        park_options_be = [
            ("all", "Усе АПТ і нацпаркі"),
            ("Беловежская пуща", "НП «Белавежская пушча»"),
            ("Березинский", "Бярэзінскі запаведнік"),
            ("Припятский", "НП «Прыпяцкі»"),
            ("Браславские", "НП «Браслаўскія азёры»"),
            ("Нарочанский", "НП «Нарачанскі»"),
            ("Споровский", "Заказнік «Спораўскі»"),
            ("Налибокская", "Заказнік «Налібоцкая пушча»"),
            ("Красный Бор", "Заказнік «Чырвоны Бор»"),
            ("Званец", "Заказнік «Званец»"),
            ("Освейский", "Заказнік «Асвейскі»"),
            ("Полесский радиационно", "Палескі радыяц.-экал. зап."),
        ]
        p_opts = park_options_ru if lang == "ru" else park_options_be
        current_park_val = self.selected_national_park if self.selected_national_park else "all"

        self.park_dropdown = ft.Dropdown(
            label="Заповедник / Нацпарк" if lang == "ru" else "Запаведнік / Нацпарк",
            value=current_park_val,
            options=[ft.dropdown.Option(val, text) for val, text in p_opts],
            leading_icon=ft.Icons.PARK_OUTLINED,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            dense=True,
            on_select=self._on_park_change,
            expand=True
        )

        # 4.5 Сортировка
        sort_options_ru = [
            ("name_asc", "По алфавиту (А–Я)"),
            ("name_desc", "В обратном порядке (Я–А)"),
            ("category_asc", "По степени угрозы (I → IV)"),
            ("category_desc", "По степени угрозы (IV → I)"),
            ("regions_desc", "По широте ареала (числу обл.)"),
        ]
        sort_options_be = [
            ("name_asc", "Па алфавіце (А–Я)"),
            ("name_desc", "У адваротным парадку (Я–А)"),
            ("category_asc", "Па ўзроўні пагрозы (I → IV)"),
            ("category_desc", "Па ўзроўні пагрозы (IV → I)"),
            ("regions_desc", "Па шырыні арэала (колькасці вобл.)"),
        ]
        s_opts = sort_options_ru if lang == "ru" else sort_options_be

        self.sort_dropdown = ft.Dropdown(
            label="Сортировка" if lang == "ru" else "Сартаванне",
            value=self.sort_by,
            options=[ft.dropdown.Option(val, text) for val, text in s_opts],
            leading_icon=ft.Icons.SORT,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            dense=True,
            on_select=self._on_sort_change,
            expand=True
        )

        # Аудио переключатель
        audio_chip = ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=12,
            bgcolor=AppColors.PRIMARY if self.has_sound_only else ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(
                1.5 if self.has_sound_only else 1,
                AppColors.PRIMARY if self.has_sound_only else ft.Colors.OUTLINE_VARIANT
            ),
            ink=True,
            on_click=self._toggle_sound_filter,
            content=ft.Row(
                tight=True,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.VOLUME_UP,
                        size=18,
                        color=ft.Colors.WHITE if self.has_sound_only else AppColors.PRIMARY
                    ),
                    ft.Text(
                        "Только с аудиозаписью" if lang == "ru" else "Толькі з аўдыязапісам",
                        size=12,
                        weight=ft.FontWeight.BOLD if self.has_sound_only else ft.FontWeight.W_500,
                        color=ft.Colors.WHITE if self.has_sound_only else ft.Colors.ON_SURFACE
                    )
                ]
            )
        )

        # Раскрывающаяся панель детальных фильтров
        filter_panel = ft.Container(
            visible=self.filters_expanded,
            padding=16,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                tight=True,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.TUNE, size=16, color=AppColors.PRIMARY),
                                    ft.Text(
                                        "Детальные параметры отбора:" if lang == "ru" else "Дэталёвыя параметры адбору:",
                                        weight=ft.FontWeight.BOLD,
                                        size=13
                                    )
                                ]
                            ),
                            *([
                                ft.TextButton(
                                    icon=ft.Icons.CLEAR_ALL,
                                    text="Сбросить все" if lang == "ru" else "Скінуць усё",
                                    style=ft.ButtonStyle(color=ft.Colors.RED_600),
                                    on_click=self._reset_all_filters
                                )
                            ] if total_active_count > 0 else [])
                        ]
                    ),
                    # Сетка выпадающих списков (4 в ряд на ПК, 2 на планшете, 1 на Android)
                    ft.ResponsiveRow(
                        spacing=10,
                        run_spacing=10,
                        controls=[
                            ft.Container(col={"sm": 12, "md": 6, "lg": 3}, content=self.taxon_dropdown),
                            ft.Container(col={"sm": 12, "md": 6, "lg": 3}, content=self.region_dropdown),
                            ft.Container(col={"sm": 12, "md": 6, "lg": 3}, content=self.biotope_dropdown),
                            ft.Container(col={"sm": 12, "md": 6, "lg": 3}, content=self.park_dropdown),
                        ]
                    ),
                    # Сортировка и аудио
                    ft.ResponsiveRow(
                        spacing=10,
                        run_spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(col={"sm": 12, "md": 6, "lg": 6}, content=self.sort_dropdown),
                            ft.Container(col={"sm": 12, "md": 6, "lg": 6}, content=audio_chip),
                        ]
                    )
                ]
            )
        )

        # 5. Интерактивные чипсы активных фильтров с кнопкой удаления (✕)
        active_tags = []
        if self.selected_kingdom:
            k_dict = {"animals": "Животные", "plants": "Растения", "fungi": "Грибы"} if lang == "ru" else {"animals": "Жывёлы", "plants": "Расліны", "fungi": "Грыбы"}
            active_tags.append(self._create_active_tag(k_dict.get(self.selected_kingdom, self.selected_kingdom), lambda e: self._select_kingdom(None)))
        if self.selected_category:
            active_tags.append(self._create_active_tag(f"Кат. {self.selected_category}", lambda e: self._select_category(None)))
        if self.selected_taxon:
            active_tags.append(self._create_active_tag(self.selected_taxon, lambda e: self._clear_taxon()))
        if self.selected_region:
            active_tags.append(self._create_active_tag(f"{self.selected_region} обл.", lambda e: self._clear_region()))
        if self.selected_biotope:
            b_dict = {"forest": "Леса", "aquatic": "Водные", "wetland": "Болота", "meadow": "Луга"} if lang == "ru" else {"forest": "Лясы", "aquatic": "Водныя", "wetland": "Балоты", "meadow": "Лугі"}
            active_tags.append(self._create_active_tag(b_dict.get(self.selected_biotope, self.selected_biotope), lambda e: self._clear_biotope()))
        if self.selected_national_park:
            active_tags.append(self._create_active_tag(self.selected_national_park, lambda e: self._clear_park()))
        if self.has_sound_only:
            active_tags.append(self._create_active_tag("С аудиозаписью" if lang == "ru" else "З аўдыя", self._toggle_sound_filter))

        active_tags_row = ft.Row(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=6,
            visible=bool(active_tags),
            controls=[
                ft.Text("Активные:" if lang == "ru" else "Актыўныя:", size=11, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY),
                *active_tags,
                ft.TextButton(
                    text="Сбросить все" if lang == "ru" else "Скінуць усё",
                    style=ft.ButtonStyle(color=ft.Colors.RED_600),
                    on_click=self._reset_all_filters
                )
            ]
        )

        # 6. Сетка карточек видов
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
                top_search_row,
                kingdom_row,
                category_row,
                filter_panel,
                active_tags_row,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Реестр Красной книги Республики Беларусь (ред. 2025):" if lang == "ru" else "Рэестр Чырвонай кнігі Рэспублікі Беларусь (рэд. 2025):",
                            size=13,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.count_text
                    ]
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                self.grid_container,
                ft.Container(height=32)
            ]
        )

    def _create_active_tag(self, label: str, on_remove: Callable):
        return ft.Container(
            padding=ft.Padding.only(left=10, right=6, top=3, bottom=3),
            border_radius=12,
            bgcolor=AppColors.PRIMARY_CONTAINER,
            content=ft.Row(
                tight=True,
                spacing=4,
                controls=[
                    ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=12,
                        icon_color=AppColors.PRIMARY,
                        tooltip="Удалить фильтр",
                        on_click=on_remove
                    )
                ]
            )
        )

    def _toggle_filters_panel(self, e):
        self.filters_expanded = not self.filters_expanded
        self._build_ui()
        self.update()

    def _select_category(self, cat: Optional[str]):
        self.selected_category = cat
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _select_kingdom(self, k: Optional[str]):
        self.selected_kingdom = k
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_taxon_change(self, e):
        val = e.control.value
        self.selected_taxon = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _clear_taxon(self):
        self.selected_taxon = None
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_biotope_change(self, e):
        val = e.control.value
        self.selected_biotope = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _clear_biotope(self):
        self.selected_biotope = None
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_park_change(self, e):
        val = e.control.value
        self.selected_national_park = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _clear_park(self):
        self.selected_national_park = None
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_region_change(self, e):
        val = e.control.value
        self.selected_region = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _clear_region(self):
        self.selected_region = None
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_sort_change(self, e):
        self.sort_by = e.control.value
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _toggle_sound_filter(self, e):
        self.has_sound_only = not self.has_sound_only
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _clear_search(self, e):
        self.search_query = ""
        self.search_field.value = ""
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _reset_all_filters(self, e):
        self.search_query = ""
        self.selected_category = None
        self.selected_kingdom = None
        self.selected_taxon = None
        self.selected_biotope = None
        self.selected_region = None
        self.selected_national_park = None
        self.has_sound_only = False
        self.sort_by = "name_asc"
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_search_change(self, e):
        self.search_query = e.control.value
        if self.search_field.suffix:
            self.search_field.suffix.visible = bool(self.search_query)
            self.search_field.update()
        self.visible_count = 36
        self._refresh_species_list()
        self.grid_container.update()
        self.count_text.update()

    def _load_more(self, e):
        self.visible_count += 36
        self._refresh_species_list()
        self.grid_container.update()
        self.count_text.update()

    def _refresh_species_list(self):
        lang = self.get_language()
        species_list = db_manager.get_species(
            query=self.search_query,
            category=self.selected_category,
            kingdom=self.selected_kingdom,
            taxon_group=self.selected_taxon,
            biotope=self.selected_biotope,
            region=self.selected_region,
            national_park=self.selected_national_park,
            sort_by=self.sort_by,
            language=lang,
            has_sound_only=self.has_sound_only
        )

        self.grid_container.controls.clear()
        total_found = len(species_list)

        self.count_text.value = f"Найдено: {total_found}" if lang == "ru" else f"Знойдзена: {total_found}"

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
                            ft.OutlinedButton(
                                icon=ft.Icons.RESTART_ALT,
                                content=ft.Text("Сбросить все фильтры" if lang == "ru" else "Скінуць усе фільтры"),
                                on_click=self._reset_all_filters
                            )
                        ]
                    )
                )
            )
            return

        displayed = species_list[:self.visible_count]
        for sp in displayed:
            card = self._create_species_card(sp, lang)
            self.grid_container.controls.append(card)

        if total_found > self.visible_count:
            remaining = total_found - self.visible_count
            load_more_btn = ft.Container(
                col={"sm": 12},
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.symmetric(vertical=16),
                content=ft.FilledButton(
                    icon=ft.Icons.EXPAND_MORE,
                    content=ft.Text(f"Показать ещё 36 видов (осталось {remaining})" if lang == "ru" else f"Паказаць яшчэ 36 відаў (засталося {remaining})"),
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(horizontal=24, vertical=14)
                    ),
                    on_click=self._load_more
                )
            )
            self.grid_container.controls.append(load_more_btn)

    def _create_species_card(self, sp: dict, lang: str) -> ft.Control:
        cat_color = get_category_color(sp["category"])
        title = sp["name_be"] if lang == "be" else sp["name_ru"]

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
                                error_content=ft.Container(
                                    height=200,
                                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.ECO, size=38, color=AppColors.PRIMARY),
                                            ft.Text(sp["name_ru"], size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                                        ]
                                    )
                                )
                            ),
                            # Бейдж категории охраны
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
