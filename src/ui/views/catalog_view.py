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

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()
        is_filtered = bool(
            self.search_query or
            self.selected_category or
            self.selected_kingdom or
            self.selected_taxon or
            self.selected_biotope or
            self.selected_region or
            self.selected_national_park or
            self.has_sound_only or
            self.sort_by != "name_asc"
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

        # 2. Фильтр царств (строго без эмодзи, векторные значки + точные счётчики)
        kingdom_items = [
            (None, "Все (515)" if lang == "ru" else "Усе (515)", ft.Icons.ALL_INCLUSIVE),
            ("animals", "Животные (213)" if lang == "ru" else "Жывёлы (213)", ft.Icons.PETS),
            ("plants", "Растения (245)" if lang == "ru" else "Расліны (245)", ft.Icons.ECO),
            ("fungi", "Грибы и лишайники (57)" if lang == "ru" else "Грыбы і лішайнікі (57)", ft.Icons.FOREST),
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
            ("I", "I CR (119)", AppColors.CAT_I, "На грани исчезновения" if lang == "ru" else "На мяжы знікнення"),
            ("II", "II EN (151)", AppColors.CAT_II, "Исчезающие виды" if lang == "ru" else "Знікаючыя віды"),
            ("III", "III VU (152)", AppColors.CAT_III, "Уязвимые виды" if lang == "ru" else "Уразлівыя віды"),
            ("IV", "IV NT (93)", AppColors.CAT_IV, "Требующие контроля" if lang == "ru" else "Патрабуюць кантролю"),
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

        # 4. Выпадающие списки расширенной фильтрации (Таксон, Биотоп, ООПТ, Область, Сортировка)
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
            value=current_taxon_val,
            options=[ft.dropdown.Option(val, text) for val, text in t_opts],
            leading_icon=ft.Icons.CATEGORY_OUTLINED,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_select=self._on_taxon_change,
            width=210,
            tooltip="Фильтр по таксономической группе" if lang == "ru" else "Фільтр па таксанамічнай групе"
        )

        # 4.2 Биотопы
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
            value=current_biotope_val,
            options=[ft.dropdown.Option(val, text) for val, text in b_opts],
            leading_icon=ft.Icons.FOREST_OUTLINED,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_select=self._on_biotope_change,
            width=210,
            tooltip="Фильтр по экосистеме обитания" if lang == "ru" else "Фільтр па экасістэме пражывання"
        )

        # 4.3 ООПТ / Национальные парки и заповедники
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
            value=current_park_val,
            options=[ft.dropdown.Option(val, text) for val, text in p_opts],
            leading_icon=ft.Icons.PARK_OUTLINED,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_select=self._on_park_change,
            width=230,
            tooltip="Фильтр по заповедникам и национальным паркам" if lang == "ru" else "Фільтр па запаведніках і нацпарках"
        )

        # 4.4 Область Беларуси
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
            value=current_reg_val,
            options=[ft.dropdown.Option(val, text) for val, text in reg_opts],
            leading_icon=ft.Icons.MAP_OUTLINED,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_select=self._on_region_change,
            width=210,
            tooltip="Фильтр по административным областям" if lang == "ru" else "Фільтр па адміністрацыйных абласцях"
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
            value=self.sort_by,
            options=[ft.dropdown.Option(val, text) for val, text in s_opts],
            leading_icon=ft.Icons.SORT_BY_ALPHA,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            dense=True,
            on_select=self._on_sort_change,
            width=220,
            tooltip="Порядок сортировки реестра" if lang == "ru" else "Парадак сартавання рэестра"
        )

        # 4.6 Чекбокс аудио и кнопка сброса
        self.sound_chip = ft.Chip(
            leading=ft.Icon(ft.Icons.VOLUME_UP, size=15, color=AppColors.PRIMARY if self.has_sound_only else ft.Colors.ON_SURFACE_VARIANT),
            label=ft.Text("С аудиозаписью" if lang == "ru" else "З аўдыязапісам", weight=ft.FontWeight.BOLD if self.has_sound_only else ft.FontWeight.W_500),
            selected=self.has_sound_only,
            on_select=self._toggle_sound_filter
        )

        reset_btn = ft.OutlinedButton(
            icon=ft.Icons.RESTART_ALT,
            content=ft.Text("Сбросить все" if lang == "ru" else "Скінуць усё"),
            style=ft.ButtonStyle(
                color=ft.Colors.RED_600,
                side=ft.BorderSide(1, ft.Colors.RED_200)
            ),
            visible=is_filtered,
            on_click=self._reset_all_filters
        )

        self.dropdown_row = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.taxon_dropdown,
                self.biotope_dropdown,
                self.park_dropdown,
                self.region_dropdown,
                self.sort_dropdown,
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
                self.dropdown_row,
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
                ft.Container(height=32) # Bottom padding
            ]
        )

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

    def _on_biotope_change(self, e):
        val = e.control.value
        self.selected_biotope = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_park_change(self, e):
        val = e.control.value
        self.selected_national_park = None if val == "all" else val
        self.visible_count = 36
        self._build_ui()
        self.update()

    def _on_region_change(self, e):
        val = e.control.value
        self.selected_region = None if val == "all" else val
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

        # Плавная пагинация для мгновенной отрисовки без задержек интерфейса
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
