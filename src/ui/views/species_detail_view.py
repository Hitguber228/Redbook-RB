import flet as ft
from typing import Callable, Optional
from ...database.db import db_manager
from ..theme import AppColors, get_category_color, get_category_label

class SpeciesDetailView(ft.Container):
    def __init__(self, species_id: str, on_back: Callable[[], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.species_id = species_id
        self.on_back = on_back
        self.get_language = get_language
        self.audio_playing = False

        self._build_ui()

    def _build_ui(self):
        sp = db_manager.get_species_by_id(self.species_id)
        if not sp:
            self.content = ft.Text("Вид не найден в базе данных")
            return

        lang = self.get_language()
        cat_color = get_category_color(sp["category"])
        title = sp["name_be"] if lang == "be" else sp["name_ru"]
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
                    height=36,
                    border_radius=8,
                    bgcolor=AppColors.PRIMARY if is_active else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        m_names[i - 1],
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if is_active else ft.Colors.GREY_600
                    )
                )
            )

        # Аудио блок (если есть голос)
        audio_section = ft.Container()
        if sp.get("sound_url"):
            audio_section = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border=ft.border.all(1, AppColors.PRIMARY_CONTAINER),
                content=ft.Row(
                    spacing=12,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.PLAY_CIRCLE_FILL,
                            icon_color=AppColors.PRIMARY,
                            icon_size=36,
                            on_click=lambda e: self._toggle_audio(sp.get("sound_url"))
                        ),
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(
                                    "Голос вида / Аудиозапись" if lang == "ru" else "Голас віду / Аўдыязапіс",
                                    weight=ft.FontWeight.BOLD,
                                    size=13
                                ),
                                ft.Text(
                                    sp.get("sound_title") or "Аутентичная запись из природы Беларуси",
                                    size=11,
                                    color=AppColors.TEXT_MUTED_LIGHT
                                )
                            ]
                        )
                    ]
                )
            )

        # Блок сравнения с видом-двойником
        doubles_section = ft.Container()
        if sp.get("look_alike_species"):
            doubles_section = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.AMBER_50,
                border=ft.border.all(1, ft.Colors.AMBER_300),
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.COMPARE_ARROWS, color=ft.Colors.AMBER_800, size=18),
                                ft.Text(
                                    "Внимание: как отличить от видов-двойников!" if lang == "ru" else "Увага: як адрозніць ад відаў-двайнікоў!",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.AMBER_900,
                                    size=13
                                )
                            ]
                        ),
                        ft.Text(sp["look_alike_species"], size=12, color=ft.Colors.AMBER_900)
                    ]
                )
            )

        self.content = ft.ListView(
            expand=True,
            padding=ft.padding.all(16),
            spacing=16,
            controls=[
                # Верхняя панель: кнопка назад и категория
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.FilledButton(
                            icon=ft.Icons.ARROW_BACK,
                            text="Назад в каталог" if lang == "ru" else "Назад у каталог",
                            on_click=lambda e: self.on_back()
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=20,
                            bgcolor=cat_color,
                            content=ft.Text(
                                get_category_label(sp["category"], lang),
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                size=12
                            )
                        )
                    ]
                ),
                # Главное фото
                ft.Container(
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src=sp["image_url"],
                        height=280,
                        width=float("inf"),
                        fit=ft.ImageFit.COVER
                    )
                ),
                # Заголовки
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"{sp['name_lat']} • {sp['name_ru'] if lang == 'be' else sp['name_be']}",
                            size=15,
                            italic=True,
                            color=AppColors.TEXT_MUTED_LIGHT
                        )
                    ]
                ),
                # Аудио (если есть)
                audio_section,
                # Описание
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=8,
                            cross_axis_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Общая характеристика" if lang == "ru" else "Агульная характарыстыка", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(desc, size=13, line_height=1.4)
                            ]
                        )
                    )
                ),
                # Морфология (внешний вид)
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=8,
                            cross_axis_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Морфологические признаки" if lang == "ru" else "Марфалагічныя прыкметы", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(sp["morphology"], size=13, line_height=1.4)
                            ]
                        )
                    )
                ),
                # Блок сравнения с двойниками
                doubles_section,
                # Биотоп и распространение
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=10,
                            cross_axis_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Места обитания и ареал в Беларуси" if lang == "ru" else "Месцы пражывання і арэал у Беларусі", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(f"🌲 {sp['habitat']}", size=13),
                                ft.Text("Распространение по областям:" if lang == "ru" else "Распаўсюджанне па абласцях:", weight=ft.FontWeight.W_600, size=12),
                                ft.Row(
                                    wrap=True,
                                    spacing=6,
                                    controls=[
                                        ft.Chip(label=ft.Text(reg, size=11))
                                        for reg in sp["distribution_rb"]
                                    ]
                                ),
                                ft.Text("Ключевые заказники и нацпарки:" if lang == "ru" else "Ключавыя заказнікі і нацпаркі:", weight=ft.FontWeight.W_600, size=12),
                                ft.Row(
                                    wrap=True,
                                    spacing=6,
                                    controls=[
                                        ft.Chip(
                                            label=ft.Text(park, size=11),
                                            bgcolor=AppColors.PRIMARY_CONTAINER
                                        )
                                        for park in sp["national_parks"]
                                    ]
                                )
                            ]
                        )
                    )
                ),
                # Фенологический календарь
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=10,
                            cross_axis_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Фенологический календарь активности" if lang == "ru" else "Фенадагічны каляндар актыўнасці", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text("Месяцы, когда вид активен, цветет или гнездится в Беларуси:" if lang == "ru" else "Месяцы, калі від актыўны, цвіце ці гняздуецца ў Беларусі:", size=12, color=AppColors.TEXT_MUTED_LIGHT),
                                ft.Row(
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    spacing=6,
                                    controls=phenology_chips
                                )
                            ]
                        )
                    )
                ),
                # Охрана и ответственность
                ft.Card(
                    color=ft.Colors.RED_50,
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=8,
                            cross_axis_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.GAVEL, color=ft.Colors.RED_800, size=20),
                                        ft.Text("Охрана и правовой режим" if lang == "ru" else "Ахова і прававы рэжым", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900, size=15)
                                    ]
                                ),
                                ft.Text(f"• Причины редкости: {sp['limiting_factors']}", size=12, color=ft.Colors.RED_900),
                                ft.Text(f"• Охранные меры: {sp['protection_measures']}", size=12, color=ft.Colors.RED_900),
                                ft.Text("⚠️ Уничтожение или изъятие влечет ответственность по ст. 16.8 КоАП Республики Беларусь с возмещением вреда в тройном размере.", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900)
                            ]
                        )
                    )
                )
            ]
        )

    def _toggle_audio(self, url: Optional[str]):
        if not url:
            return
        # Для простоты можно открыть ссылку или проиграть через медиаплеер
        self.page.launch_url(url)
