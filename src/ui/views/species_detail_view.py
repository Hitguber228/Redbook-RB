import flet as ft
from typing import Callable, Optional
from ...database.db import db_manager
from ...utils import open_target
from ..theme import AppColors, get_category_color, get_category_label

REGION_COLORS = {
    "Брестская": ft.Colors.GREEN_700,
    "Витебская": ft.Colors.BLUE_700,
    "Гомельская": ft.Colors.AMBER_800,
    "Гродненская": ft.Colors.TEAL_700,
    "Минская": ft.Colors.PURPLE_700,
    "Могилевская": ft.Colors.ORANGE_800,
}

class SpeciesDetailView(ft.Container):
    def __init__(self, species_id: str, on_back: Callable[[], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.species_id = species_id
        self.on_back = on_back
        self.get_language = get_language

        self._build_ui()

    def _build_ui(self):
        sp = db_manager.get_species_by_id(self.species_id)
        if not sp:
            self.content = ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=40,
                content=ft.Text("Вид не найден в базе данных", size=18, weight=ft.FontWeight.BOLD)
            )
            return

        lang = self.get_language()
        cat_color = get_category_color(sp["category"])
        title = sp["name_be"] if lang == "be" else sp["name_ru"]
        subtitle_other_lang = sp["name_ru"] if lang == "be" else sp["name_be"]
        desc = sp["description_be"] if lang == "be" else sp["description_ru"]

        # Месяцы активности (фенологический календарь)
        months_names_ru = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        months_names_be = ["Сту", "Лют", "Сак", "Кра", "Май", "Чэр", "Ліп", "Жні", "Вер", "Кас", "Ліс", "Сне"]
        m_names = months_names_be if lang == "be" else months_names_ru

        phenology_chips = []
        for i in range(1, 13):
            is_active = i in sp["phenology_months"]
            phenology_chips.append(
                ft.Container(
                    width=42,
                    height=38,
                    border_radius=8,
                    bgcolor=AppColors.PRIMARY if is_active else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border=ft.Border.all(1.5, AppColors.PRIMARY if is_active else ft.Colors.OUTLINE_VARIANT),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        m_names[i - 1],
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if is_active else ft.Colors.GREY_600
                    )
                )
            )

        # Аудио плеер (если есть аудиозапись голоса)
        audio_section = ft.Container()
        if sp.get("sound_url"):
            audio_section = ft.Container(
                padding=12,
                border_radius=12,
                bgcolor=ft.Colors.GREEN_50,
                border=ft.Border.all(1, ft.Colors.GREEN_300),
                content=ft.Row(
                    spacing=12,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.PLAY_CIRCLE_FILLED,
                            icon_color=AppColors.PRIMARY,
                            icon_size=38,
                            tooltip="Слушать запись голоса",
                            on_click=lambda e: self._play_audio(sp.get("sound_url"))
                        ),
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(
                                    "Голос вида в дикой природе" if lang == "ru" else "Голас віду ў дзікай прыродзе",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=AppColors.PRIMARY
                                ),
                                ft.Text(
                                    sp.get("sound_title") or "Аутентичная аудиозапись из лесов Беларуси",
                                    size=11,
                                    color=ft.Colors.GREY_700
                                )
                            ]
                        )
                    ]
                )
            )

        # Блок сравнения с видом-двойником (с ярким акцентом для распознавания в природе)
        doubles_section = ft.Container()
        if sp.get("look_alike_species"):
            doubles_section = ft.Card(
                elevation=2,
                bgcolor=ft.Colors.AMBER_50,
                content=ft.Container(
                    padding=16,
                    border_radius=12,
                    border=ft.Border.all(1.5, ft.Colors.AMBER_400),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.COMPARE_ARROWS, color=ft.Colors.AMBER_900, size=22),
                                    ft.Text(
                                        "Внимание: как отличить от видов-двойников!" if lang == "ru" else "Увага: як адрозніць ад відаў-двайнікоў!",
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.AMBER_900,
                                        size=14
                                    )
                                ]
                            ),
                            ft.Text(
                                sp["look_alike_species"],
                                size=13,
                                color=ft.Colors.AMBER_900,
                                weight=ft.FontWeight.W_500
                            )
                        ]
                    )
                )
            )

        # Чипсы областей с цветовыми маркерами
        region_chips = []
        for reg in sp["distribution_rb"]:
            reg_color = REGION_COLORS.get(reg, AppColors.PRIMARY)
            region_chips.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                    border_radius=16,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1, reg_color),
                    content=ft.Row(
                        tight=True,
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, size=13, color=reg_color),
                            ft.Text(reg, size=11, weight=ft.FontWeight.BOLD, color=reg_color)
                        ]
                    )
                )
            )

        # Чипсы нацпарков
        park_chips = []
        for park in sp["national_parks"]:
            park_chips.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                    border_radius=16,
                    bgcolor=AppColors.PRIMARY_CONTAINER,
                    border=ft.Border.all(1, AppColors.PRIMARY),
                    content=ft.Row(
                        tight=True,
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.PARK, size=13, color=AppColors.PRIMARY),
                            ft.Text(park, size=11, weight=ft.FontWeight.W_600, color=AppColors.PRIMARY)
                        ]
                    )
                )
            )

        # Верхняя панель навигации (Назад и Категория)
        header_nav = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.FilledButton(
                    icon=ft.Icons.ARROW_BACK,
                    content="Назад в каталог" if lang == "ru" else "Назад у каталог",
                    on_click=lambda e: self.on_back()
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                    border_radius=20,
                    bgcolor=cat_color,
                    content=ft.Row(
                        tight=True,
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.SHIELD, size=16, color=ft.Colors.WHITE),
                            ft.Text(
                                get_category_label(sp["category"], lang),
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                size=12
                            )
                        ]
                    )
                )
            ]
        )

        # Геройский блок: Фото + Идентичность (2 колонки на ПК, 1 на телефоне)
        hero_section = ft.ResponsiveRow(
            spacing=16,
            controls=[
                # Колонка фото
                ft.Container(
                    col={"sm": 12, "md": 6},
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.BLACK_12),
                    content=ft.Image(
                        src=sp["image_url"],
                        height=300,
                        width=float("inf"),
                        fit="cover"
                    )
                ),
                # Колонка названий и статуса
                ft.Container(
                    col={"sm": 12, "md": 6},
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(title, size=26, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{sp['name_lat']} • {subtitle_other_lang}",
                                size=15,
                                italic=True,
                                color=AppColors.TEXT_MUTED_LIGHT
                            ),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=8,
                                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                        content=ft.Text(f"Царство: {sp['kingdom'].capitalize()}", size=11, weight=ft.FontWeight.W_500)
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=8,
                                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                        content=ft.Text(f"Группа: {sp['taxon_group'].capitalize()}", size=11, weight=ft.FontWeight.W_500)
                                    )
                                ]
                            ),
                            ft.Text(desc, size=13, color=ft.Colors.ON_SURFACE),
                            audio_section
                        ]
                    )
                )
            ]
        )

        # Двухколоночный блок деталей на десктопе
        details_grid = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16,
            controls=[
                # Левая колонка: Морфология и Двойники
                ft.Container(
                    col={"sm": 12, "md": 6},
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Card(
                                elevation=1,
                                content=ft.Container(
                                    padding=16,
                                    content=ft.Column(
                                        spacing=8,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    ft.Icon(ft.Icons.SCIENCE, color=AppColors.PRIMARY, size=20),
                                                    ft.Text(
                                                        "Морфологические признаки" if lang == "ru" else "Марфалагічныя прыкметы",
                                                        weight=ft.FontWeight.BOLD,
                                                        size=15
                                                    )
                                                ]
                                            ),
                                            ft.Divider(height=1),
                                            ft.Text(sp["morphology"], size=13, color=ft.Colors.ON_SURFACE)
                                        ]
                                    )
                                )
                            ),
                            doubles_section
                        ]
                    )
                ),
                # Правая колонка: Ареал, Фенология, Охрана
                ft.Container(
                    col={"sm": 12, "md": 6},
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            # Ареал и биотопы
                            ft.Card(
                                elevation=1,
                                content=ft.Container(
                                    padding=16,
                                    content=ft.Column(
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    ft.Icon(ft.Icons.FOREST, color=AppColors.PRIMARY, size=20),
                                                    ft.Text(
                                                        "Места обитания и ареал" if lang == "ru" else "Месцы пражывання і арэал",
                                                        weight=ft.FontWeight.BOLD,
                                                        size=15
                                                    )
                                                ]
                                            ),
                                            ft.Text(sp["habitat"], size=13),
                                            ft.Text("Области обитания:" if lang == "ru" else "Вобласці пражывання:", weight=ft.FontWeight.BOLD, size=12),
                                            ft.Row(wrap=True, spacing=6, controls=region_chips),
                                            ft.Text("Заказники и нацпарки:" if lang == "ru" else "Заказнікі і нацпаркі:", weight=ft.FontWeight.BOLD, size=12),
                                            ft.Row(wrap=True, spacing=6, controls=park_chips)
                                        ]
                                    )
                                )
                            ),
                            # Фенологический календарь
                            ft.Card(
                                elevation=1,
                                content=ft.Container(
                                    padding=16,
                                    content=ft.Column(
                                        spacing=8,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=AppColors.PRIMARY, size=20),
                                                    ft.Text(
                                                        "Фенологический календарь" if lang == "ru" else "Феналагічны каляндар",
                                                        weight=ft.FontWeight.BOLD,
                                                        size=15
                                                    )
                                                ]
                                            ),
                                            ft.Text(
                                                "Месяцы активности в Беларуси (зеленый = активен):" if lang == "ru" else "Месяцы актыўнасці ў Беларусі (зялёны = актыўны):",
                                                size=11,
                                                color=AppColors.TEXT_MUTED_LIGHT
                                            ),
                                            ft.Row(
                                                scroll=ft.ScrollMode.ADAPTIVE,
                                                spacing=4,
                                                controls=phenology_chips
                                            )
                                        ]
                                    )
                                )
                            ),
                            # Охрана и ответственность по закону
                            ft.Card(
                                elevation=2,
                                bgcolor=ft.Colors.RED_50,
                                content=ft.Container(
                                    padding=16,
                                    border_radius=12,
                                    border=ft.Border.all(1.5, ft.Colors.RED_300),
                                    content=ft.Column(
                                        spacing=8,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    ft.Icon(ft.Icons.GAVEL, color=ft.Colors.RED_800, size=20),
                                                    ft.Text(
                                                        "Охрана и закон (ст. 16.8 КоАП РБ)" if lang == "ru" else "Ахова і закон (арт. 16.8 КаАП РБ)",
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.RED_900,
                                                        size=14
                                                    )
                                                ]
                                            ),
                                            ft.Text(
                                                f"• Причины редкости: {sp['limiting_factors']}" if lang == "ru" else f"• Прычыны рэдкасці: {sp['limiting_factors']}",
                                                size=12,
                                                color=ft.Colors.RED_900
                                            ),
                                            ft.Text(
                                                f"• Охранные меры: {sp['protection_measures']}" if lang == "ru" else f"• Ахоўныя захады: {sp['protection_measures']}",
                                                size=12,
                                                color=ft.Colors.RED_900
                                            ),
                                            ft.Container(
                                                padding=8,
                                                border_radius=8,
                                                bgcolor=ft.Colors.RED_100,
                                                content=ft.Text(
                                                    "⚖️ Незаконное изъятие или уничтожение влечет административную ответственность по ст. 16.8 КоАП Республики Беларусь с возмещением вреда в тройном размере." if lang == "ru" else "⚖️ Незаконнае знішчэнне ці канфіскацыя цягне адказнасць паводле арт. 16.8 КаАП Рэспублікі Беларусь з пакрыццём шкоды ў трохразовым памеры.",
                                                    size=11,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.RED_900
                                                )
                                            )
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            spacing=18,
            controls=[
                header_nav,
                hero_section,
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                details_grid,
                ft.Container(height=24) # Bottom padding
            ]
        )

    def _play_audio(self, url: Optional[str]):
        if not url:
            return
        open_target(url, self.page)
