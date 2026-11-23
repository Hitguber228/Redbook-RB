import flet as ft
from typing import Optional
from .ui.theme import AppColors
from .ui.views.catalog_view import CatalogView
from .ui.views.species_detail_view import SpeciesDetailView
from .ui.views.map_view import MapView
from .ui.views.quiz_view import QuizView
from .ui.views.ai_scanner_view import AIScannerView
from .ui.views.diary_view import DiaryView

class RedBookApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.language = "ru" # "ru" | "be"
        self.current_nav_index = 0
        self.active_species_id: Optional[str] = None

        # Инициализация сервиса выбора файлов для ИИ-сканера
        self.file_picker = ft.FilePicker()
        if hasattr(self.page, "services") and hasattr(self.page.services, "register_service"):
            try:
                self.page.services.register_service(self.file_picker)
            except Exception:
                pass

        self._configure_page()
        self._build_layout()

    def _configure_page(self):
        self.page.title = "Интерактивная красная книга Республики Беларусь"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.spacing = 0
        self.page.on_keyboard_event = self._on_keyboard_event
        
        # Настройка цветовой темы
        self.page.theme = ft.Theme(
            color_scheme_seed=AppColors.PRIMARY,
            font_family="Roboto"
        )
        self.page.dark_theme = ft.Theme(
            color_scheme_seed=AppColors.PRIMARY,
            font_family="Roboto"
        )

    def _on_keyboard_event(self, e: ft.KeyboardEvent):
        # Поддержка вставки фото из буфера обмена (Ctrl+V)
        if (e.ctrl or e.meta) and e.key and e.key.upper() == "V":
            if hasattr(self, "current_view_instance") and hasattr(self.current_view_instance, "_paste_from_clipboard"):
                self.current_view_instance._paste_from_clipboard()
            elif self.current_nav_index != 2:
                # Если нажали Ctrl+V на другой вкладке, переключаемся на ИИ-сканер и вставляем снимок
                self.current_nav_index = 2
                self.active_species_id = None
                self._build_layout()
                if hasattr(self, "current_view_instance") and hasattr(self.current_view_instance, "_paste_from_clipboard"):
                    self.current_view_instance._paste_from_clipboard()

    def get_language(self) -> str:
        return self.language

    def _build_layout(self):
        self.page.controls.clear()
        lang = self.language

        # Заголовок верхней панели
        app_title = "Красная книга Беларуси" if lang == "ru" else "Чырвоная кніга Беларусі"

        # Верхний AppBar
        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.ECO, color=ft.Colors.WHITE, size=28),
            leading_width=44,
            title=ft.Text(app_title, weight=ft.FontWeight.BOLD, size=19, color=ft.Colors.WHITE),
            center_title=False,
            bgcolor=AppColors.PRIMARY,
            actions=[
                # Сегментированный переключатель языка РУС | БЕЛ с визуальным выделением активного
                ft.Container(
                    margin=ft.Padding.only(right=6),
                    border_radius=20,
                    bgcolor=ft.Colors.WHITE_24,
                    padding=ft.Padding.all(3),
                    content=ft.Row(
                        tight=True,
                        spacing=2,
                        controls=[
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                border_radius=16,
                                bgcolor=ft.Colors.WHITE if lang == "ru" else ft.Colors.TRANSPARENT,
                                ink=True,
                                tooltip="Русский язык интерфейса",
                                on_click=lambda e: self._set_language("ru"),
                                content=ft.Row(
                                    tight=True,
                                    spacing=5,
                                    controls=[
                                        ft.Container(
                                            width=16,
                                            height=11,
                                            border_radius=2,
                                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                            content=ft.Image(src="/flags/flag_ru.png", fit="cover")
                                        ),
                                        ft.Text(
                                            "РУС",
                                            size=11,
                                            weight=ft.FontWeight.BOLD if lang == "ru" else ft.FontWeight.NORMAL,
                                            color=AppColors.PRIMARY if lang == "ru" else ft.Colors.WHITE
                                        )
                                    ]
                                )
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                border_radius=16,
                                bgcolor=ft.Colors.WHITE if lang == "be" else ft.Colors.TRANSPARENT,
                                ink=True,
                                tooltip="Беларуская мова інтэрфейсу",
                                on_click=lambda e: self._set_language("be"),
                                content=ft.Row(
                                    tight=True,
                                    spacing=5,
                                    controls=[
                                        ft.Container(
                                            width=16,
                                            height=11,
                                            border_radius=2,
                                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                            content=ft.Image(src="/flags/flag_by.png", fit="cover")
                                        ),
                                        ft.Text(
                                            "БЕЛ",
                                            size=11,
                                            weight=ft.FontWeight.BOLD if lang == "be" else ft.FontWeight.NORMAL,
                                            color=AppColors.PRIMARY if lang == "be" else ft.Colors.WHITE
                                        )
                                    ]
                                )
                            ),
                        ]
                    )
                ),
                # Переключатель темы (Светлая / Темная)
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Переключить ночной режим для полевых выходов" if lang == "ru" else "Пераключыць начны рэжым для палявых выхадаў",
                    on_click=self._toggle_theme
                )
            ]
        )

        # Контент активного экрана
        content_view = self._get_active_view()
        self.current_view_instance = content_view

        # Нижняя мобильная панель навигации (NavigationBar)
        bottom_nav = ft.NavigationBar(
            selected_index=self.current_nav_index,
            on_change=self._on_nav_change,
            bgcolor=ft.Colors.SURFACE,
            indicator_color=AppColors.PRIMARY_CONTAINER,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.AUTO_STORIES_OUTLINED,
                    selected_icon=ft.Icons.AUTO_STORIES,
                    label="Каталог" if lang == "ru" else "Каталог"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.MAP_OUTLINED,
                    selected_icon=ft.Icons.MAP,
                    label="Карта РБ" if lang == "ru" else "Карта РБ"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                    selected_icon=ft.Icons.AUTO_AWESOME,
                    label="ИИ-Сканер" if lang == "ru" else "ІІ-Сканер"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SCHOOL_OUTLINED,
                    selected_icon=ft.Icons.SCHOOL,
                    label="Викторины" if lang == "ru" else "Віктарыны"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOKMARK_BORDER,
                    selected_icon=ft.Icons.BOOKMARK,
                    label="Дневник" if lang == "ru" else "Дзённік"
                )
            ]
        )

        centered_shell = ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Container(
                expand=True,
                max_width=1140,
                content=content_view
            )
        )

        self.page.appbar = app_bar
        self.page.navigation_bar = bottom_nav
        self.page.add(centered_shell)
        self.page.update()

    def _get_active_view(self) -> ft.Control:
        if self.active_species_id is not None:
            return SpeciesDetailView(
                species_id=self.active_species_id,
                on_back=self._back_to_catalog,
                get_language=self.get_language
            )

        if self.current_nav_index == 0:
            return CatalogView(
                on_select_species=self._select_species,
                get_language=self.get_language
            )
        elif self.current_nav_index == 1:
            return MapView(
                on_select_species=self._select_species,
                get_language=self.get_language
            )
        elif self.current_nav_index == 2:
            return AIScannerView(
                on_select_species=self._select_species,
                get_language=self.get_language,
                file_picker=self.file_picker
            )
        elif self.current_nav_index == 3:
            return QuizView(
                get_language=self.get_language
            )
        elif self.current_nav_index == 4:
            return DiaryView(
                get_language=self.get_language
            )

        return ft.Text("Раздел в разработке")

    def _select_species(self, species_id: str):
        self.active_species_id = species_id
        self._build_layout()

    def _back_to_catalog(self):
        self.active_species_id = None
        self._build_layout()

    def _on_nav_change(self, e):
        self.current_nav_index = e.control.selected_index
        self.active_species_id = None
        self._build_layout()

    def _set_language(self, lang: str):
        if self.language != lang:
            self.language = lang
            self._build_layout()

    def _toggle_language(self, e):
        self.language = "be" if self.language == "ru" else "ru"
        self._build_layout()

    def _toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self._build_layout()

def main(page: ft.Page):
    RedBookApp(page)

if __name__ == "__main__":
    runner = getattr(ft, "run", getattr(ft, "app", None))
    runner(main)

