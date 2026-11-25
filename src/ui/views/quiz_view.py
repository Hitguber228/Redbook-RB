import flet as ft
from typing import Callable, Optional, Dict, Any, List
from ...services.quiz_service import quiz_service
from ..theme import AppColors

CATEGORY_ICONS = {
    "MILITARY_TECH": ft.Icons.MILITARY_TECH,
    "PHOTO_CAMERA": ft.Icons.PHOTO_CAMERA,
    "PETS": ft.Icons.PETS,
    "LOCAL_FLORIST": ft.Icons.LOCAL_FLORIST,
    "EXPLORE": ft.Icons.EXPLORE,
    "VOLUME_UP": ft.Icons.VOLUME_UP,
    "SHIELD": ft.Icons.SHIELD,
}

class QuizView(ft.Container):
    def __init__(
        self,
        get_language: Callable[[], str],
        on_select_species: Optional[Callable[[str], None]] = None
    ):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_LIGHT
        self.get_language = get_language
        self.on_select_species = on_select_species

        # Состояния экрана: "categories" | "question" | "certificate"
        self.view_state: str = "categories"
        self.active_category_id: str = "tournament"
        self.current_index: int = 0
        self.selected_option: Optional[int] = None
        self.answer_checked: bool = False
        self.last_result: Optional[Dict[str, Any]] = None
        self.session_quizzes: List[Dict[str, Any]] = []
        self.student_name: str = "Учащийся"

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()
        if self.view_state == "categories":
            self.content = self._build_categories_hub(lang)
        elif self.view_state == "question":
            self.content = self._build_question_flow(lang)
        elif self.view_state == "certificate":
            self.content = self._build_certificate_view(lang)

    # =========================================================================
    # ЭКРАН 1: ХАБ КАТЕГОРИЙ И ТЕМ ВИКТОРИН
    # =========================================================================
    def _build_categories_hub(self, lang: str) -> ft.Control:
        is_ru = (lang == "ru")
        categories = quiz_service.get_categories(lang)

        # Верхний баннер-заголовок
        header_card = ft.Container(
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                        controls=[
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=12,
                                bgcolor=AppColors.PRIMARY_CONTAINER,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.SCHOOL, color=AppColors.PRIMARY, size=26)
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Экологические викторины" if is_ru else "Экалагічныя віктарыны",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppColors.TEXT_MAIN_LIGHT
                                    ),
                                    ft.Text(
                                        "Тематические и олимпиадные тесты по Красной книге Республики Беларусь" if is_ru else "Тэматычныя і алімпіядныя тэсты па Чырвонай кнізе Рэспублікі Беларусь",
                                        size=13,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ]
                            )
                        ]
                    ),
                    # Информационная плашка со сводкой
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            spacing=20,
                            wrap=True,
                            controls=[
                                self._build_mini_info_chip(
                                    ft.Icons.HELP_OUTLINE,
                                    "515 видов + 40 вопросов" if is_ru else "515 відаў + 40 пытанняў"
                                ),
                                self._build_mini_info_chip(
                                    ft.Icons.CATEGORY,
                                    "7 направлений" if is_ru else "7 напрамкаў"
                                ),
                                self._build_mini_info_chip(
                                    ft.Icons.WORKSPACE_PREMIUM,
                                    "Академический диплом" if is_ru else "Акадэмічны дыплом"
                                )
                            ]
                        )
                    )
                ]
            )
        )

        # Выделенная карточка главного смешанного турнира (во всю ширину)
        tournament_cat = next((c for c in categories if c["id"] == "tournament"), None)
        thematic_cats = [c for c in categories if c["id"] != "tournament"]

        featured_card = ft.Container()
        if tournament_cat:
            featured_card = ft.Card(
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=16),
                content=ft.Container(
                    padding=ft.Padding.symmetric(horizontal=22, vertical=18),
                    bgcolor=AppColors.PRIMARY_CONTAINER,
                    border=ft.Border.all(1, AppColors.PRIMARY_LIGHT),
                    border_radius=16,
                    ink=True,
                    on_click=lambda e, cid=tournament_cat["id"]: self._start_category(cid),
                    content=ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                        controls=[
                            ft.Container(
                                col={"xs": 12, "md": 8},
                                content=ft.Row(
                                    spacing=14,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            width=50,
                                            height=50,
                                            border_radius=12,
                                            bgcolor=AppColors.PRIMARY,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(ft.Icons.MILITARY_TECH, color=ft.Colors.WHITE, size=28)
                                        ),
                                        ft.Column(
                                            spacing=3,
                                            expand=True,
                                            controls=[
                                                ft.Row(
                                                    spacing=8,
                                                    wrap=True,
                                                    controls=[
                                                        ft.Text(
                                                            tournament_cat["title"],
                                                            size=17,
                                                            weight=ft.FontWeight.BOLD,
                                                            color=AppColors.TEXT_MAIN_LIGHT
                                                        ),
                                                        ft.Container(
                                                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                                            border_radius=8,
                                                            bgcolor=ft.Colors.SURFACE,
                                                            content=ft.Text(
                                                                tournament_cat["badge"],
                                                                size=11,
                                                                weight=ft.FontWeight.W_600,
                                                                color=AppColors.PRIMARY
                                                            )
                                                        )
                                                    ]
                                                ),
                                                ft.Text(
                                                    tournament_cat["description"],
                                                    size=13,
                                                    color=AppColors.TEXT_MAIN_LIGHT
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ),
                            ft.Container(
                                col={"xs": 12, "md": 4},
                                alignment=ft.Alignment.CENTER_RIGHT,
                                content=ft.FilledButton(
                                    content=ft.Text("Начать турнир" if is_ru else "Пачаць турнір"),
                                    icon=ft.Icons.PLAY_ARROW,
                                    style=ft.ButtonStyle(
                                        bgcolor=AppColors.PRIMARY,
                                        color=ft.Colors.WHITE,
                                        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    on_click=lambda e, cid=tournament_cat["id"]: self._start_category(cid)
                                )
                            )
                        ]
                    )
                )
            )

        # Сетка 6 тематических карточек (ровная сетка 3x2 на ПК, 2x3 на планшете)
        cards = []
        for cat in thematic_cats:
            icon_key = cat.get("icon", "HELP_OUTLINE")
            material_icon = CATEGORY_ICONS.get(icon_key, ft.Icons.HELP_OUTLINE)

            cards.append(
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 6, "lg": 4},
                    content=ft.Card(
                        elevation=0,
                        shape=ft.RoundedRectangleBorder(radius=16),
                        content=ft.Container(
                            padding=18,
                            bgcolor=ft.Colors.SURFACE,
                            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                            border_radius=16,
                            ink=True,
                            on_click=lambda e, cid=cat["id"]: self._start_category(cid),
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Container(
                                                width=42,
                                                height=42,
                                                border_radius=10,
                                                bgcolor=AppColors.PRIMARY_CONTAINER,
                                                alignment=ft.Alignment.CENTER,
                                                content=ft.Icon(material_icon, color=AppColors.PRIMARY, size=22)
                                            ),
                                            ft.Container(
                                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                                border_radius=10,
                                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                                content=ft.Text(
                                                    cat["badge"],
                                                    size=11,
                                                    weight=ft.FontWeight.W_600,
                                                    color=AppColors.TEXT_MUTED_LIGHT
                                                )
                                            )
                                        ]
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                cat["title"],
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=AppColors.TEXT_MAIN_LIGHT
                                            ),
                                            ft.Text(
                                                cat["subtitle"],
                                                size=12,
                                                weight=ft.FontWeight.W_500,
                                                color=AppColors.PRIMARY
                                            )
                                        ]
                                    ),
                                    ft.Container(
                                        height=48,
                                        content=ft.Text(
                                            cat["description"],
                                            size=12,
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                            max_lines=3,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        )
                                    ),
                                    ft.FilledButton(
                                        content=ft.Text("Начать тест" if is_ru else "Пачаць тэст"),
                                        icon=ft.Icons.PLAY_ARROW,
                                        style=ft.ButtonStyle(
                                            bgcolor=AppColors.PRIMARY,
                                            color=ft.Colors.WHITE,
                                            shape=ft.RoundedRectangleBorder(radius=10)
                                        ),
                                        on_click=lambda e, cid=cat["id"]: self._start_category(cid)
                                    )
                                ]
                            )
                        )
                    )
                )
            )

        grid_row = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16,
            controls=cards
        )

        return ft.ListView(
            expand=True,
            padding=ft.Padding.all(20),
            spacing=18,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        max_width=960,
                        content=ft.Column(
                            spacing=18,
                            controls=[
                                header_card,
                                featured_card,
                                grid_row
                            ]
                        )
                    )
                )
            ]
        )

    def _build_mini_info_chip(self, icon: str, text: str) -> ft.Control:
        return ft.Row(
            spacing=6,
            controls=[
                ft.Icon(icon, size=15, color=AppColors.PRIMARY),
                ft.Text(text, size=12, weight=ft.FontWeight.W_500, color=AppColors.TEXT_MAIN_LIGHT)
            ]
        )

    @staticmethod
    def _normalize_image_src(media_url: Optional[str]) -> Optional[str]:
        if not media_url or not isinstance(media_url, str):
            return None
        lower = media_url.lower()
        if lower.endswith((".mp3", ".wav", ".ogg")):
            return None
        if media_url.startswith("assets/"):
            return "/" + media_url[len("assets/"):]
        return media_url

    # =========================================================================
    # ЭКРАН 2: ПРОХОЖДЕНИЕ ТЕСТА (АКТИВНЫЙ ВОПРОС)
    # =========================================================================
    def _build_question_flow(self, lang: str) -> ft.Control:
        is_ru = (lang == "ru")

        if not self.session_quizzes or self.current_index >= len(self.session_quizzes):
            self.view_state = "certificate"
            return self._build_certificate_view(lang)

        current_quiz = self.session_quizzes[self.current_index]
        q_text = current_quiz["question_be"] if lang == "be" else current_quiz["question_ru"]
        options = current_quiz["options_be"] if lang == "be" else current_quiz["options_ru"]
        total_q = len(self.session_quizzes)
        quiz_type = current_quiz.get("quiz_type", "general")

        # Верхняя панель навигации и индикаторов
        top_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.TextButton(
                    content=ft.Text("К разделам" if is_ru else "Да раздзелаў"),
                    icon=ft.Icons.ARROW_BACK,
                    style=ft.ButtonStyle(color=AppColors.PRIMARY),
                    on_click=self._return_to_categories
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        # Индикатор серии правильных ответов
                        ft.Container(
                            visible=(quiz_service.current_streak > 1),
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12,
                            bgcolor=ft.Colors.AMBER_100,
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.BOLT, size=15, color=ft.Colors.AMBER_900),
                                    ft.Text(
                                        f"Серия: {quiz_service.current_streak}" if is_ru else f"Серыя: {quiz_service.current_streak}",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.AMBER_900
                                    )
                                ]
                            )
                        ),
                        # Индикатор текущих баллов
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12,
                            bgcolor=AppColors.PRIMARY_CONTAINER,
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.CHECK, size=15, color=AppColors.PRIMARY),
                                    ft.Text(
                                        f"Баллы: {quiz_service.current_score}" if is_ru else f"Балы: {quiz_service.current_score}",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppColors.PRIMARY
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )

        # Прогресс прохождения
        progress_val = (self.current_index + 1) / max(total_q, 1)
        progress_block = ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            f"Вопрос {self.current_index + 1} из {total_q}" if is_ru else f"Пытанне {self.current_index + 1} з {total_q}",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=AppColors.PRIMARY
                        ),
                        ft.Text(
                            f"{int(progress_val * 100)}%",
                            size=12,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ]
                ),
                ft.ProgressBar(
                    value=progress_val,
                    color=AppColors.PRIMARY,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    height=6,
                    border_radius=3
                )
            ]
        )

        # Дополнительная плашка для биоакустических вопросов или фото-блок
        media_src = self._normalize_image_src(current_quiz.get("media_url"))
        question_media_controls: List[ft.Control] = []

        if quiz_type == "voice":
            question_media_controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=10,
                    bgcolor=AppColors.PRIMARY_CONTAINER,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.VOLUME_UP, size=18, color=AppColors.PRIMARY),
                            ft.Text(
                                "Биоакустический вопрос: проанализируйте голосовые сигналы и биотоп" if is_ru else "Біяакустычнае пытанне: прааналізуйце галасавыя сігналы і біятоп",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=AppColors.PRIMARY,
                                expand=True
                            )
                        ]
                    )
                )
            )
        elif quiz_type == "photo" and media_src:
            question_media_controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=8,
                    bgcolor=AppColors.PRIMARY_CONTAINER,
                    content=ft.Row(
                        spacing=6,
                        alignment=ft.MainAxisAlignment.START,
                        tight=True,
                        controls=[
                            ft.Icon(ft.Icons.PHOTO_CAMERA, size=16, color=AppColors.PRIMARY),
                            ft.Text(
                                "Фото-определитель: узнайте вид по изображению" if is_ru else "Фота-азначнік: пазнайце від па выяве",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=AppColors.PRIMARY
                            )
                        ]
                    )
                )
            )
            question_media_controls.append(
                ft.Container(
                    height=240,
                    width=float("inf"),
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src=media_src,
                        height=240,
                        width=float("inf"),
                        fit="contain",
                        error_content=ft.Container(
                            height=240,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=36, color=ft.Colors.ON_SURFACE_VARIANT),
                                    ft.Text(
                                        "Изображение временно недоступно" if is_ru else "Выява часова недаступная",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ]
                            )
                        )
                    )
                )
            )

        # Карточка вопроса
        question_card = ft.Card(
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=16),
            content=ft.Container(
                padding=22,
                bgcolor=ft.Colors.SURFACE,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=16,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        *question_media_controls,
                        ft.Text(
                            q_text,
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=AppColors.TEXT_MAIN_LIGHT
                        )
                    ]
                )
            )
        )

        # Варианты ответов (A, B, C, D)
        option_letters = ["A", "B", "C", "D"]
        option_buttons = []
        for i, opt_text in enumerate(options):
            is_selected = (self.selected_option == i)
            letter = option_letters[i] if i < len(option_letters) else str(i + 1)

            btn_bg = ft.Colors.SURFACE
            border_color = ft.Colors.OUTLINE_VARIANT
            border_width = 1
            text_color = AppColors.TEXT_MAIN_LIGHT
            letter_bg = ft.Colors.SURFACE_CONTAINER_HIGHEST
            letter_fg = ft.Colors.ON_SURFACE_VARIANT
            trailing_icon = None

            if not self.answer_checked:
                if is_selected:
                    btn_bg = AppColors.PRIMARY_CONTAINER
                    border_color = AppColors.PRIMARY
                    border_width = 2
                    letter_bg = AppColors.PRIMARY
                    letter_fg = ft.Colors.WHITE
            else:
                correct_idx = current_quiz["correct_index"]
                if i == correct_idx:
                    btn_bg = ft.Colors.GREEN_50
                    border_color = ft.Colors.GREEN_600
                    border_width = 2
                    text_color = ft.Colors.GREEN_900
                    letter_bg = ft.Colors.GREEN_600
                    letter_fg = ft.Colors.WHITE
                    trailing_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=22)
                elif is_selected:
                    btn_bg = ft.Colors.RED_50
                    border_color = ft.Colors.RED_600
                    border_width = 2
                    text_color = ft.Colors.RED_900
                    letter_bg = ft.Colors.RED_600
                    letter_fg = ft.Colors.WHITE
                    trailing_icon = ft.Icon(ft.Icons.CANCEL, color=ft.Colors.RED_700, size=22)
                else:
                    text_color = ft.Colors.ON_SURFACE_VARIANT

            option_buttons.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                    border_radius=12,
                    bgcolor=btn_bg,
                    border=ft.Border.all(border_width, border_color),
                    ink=not self.answer_checked,
                    on_click=(lambda e, idx=i: self._select_option(idx)) if not self.answer_checked else None,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            ft.Row(
                                spacing=12,
                                expand=True,
                                controls=[
                                    ft.Container(
                                        width=30,
                                        height=30,
                                        border_radius=15,
                                        bgcolor=letter_bg,
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Text(
                                            letter,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=letter_fg
                                        )
                                    ),
                                    ft.Text(
                                        opt_text,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color=text_color,
                                        expand=True
                                    )
                                ]
                            ),
                            trailing_icon if trailing_icon else ft.Container()
                        ]
                    )
                )
            )

        # Блок пояснения и ссылки на паспорт вида (после ответа)
        explanation_card = ft.Container()
        if self.answer_checked and self.last_result:
            is_ok = self.last_result.get("is_correct", False)
            exp_text = self.last_result.get("explanation", "")
            species_id = self.last_result.get("related_species_id")

            exp_text_block = ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if is_ok else ft.Icons.INFO_OUTLINE,
                                color=ft.Colors.GREEN_700 if is_ok else ft.Colors.RED_700,
                                size=20
                            ),
                            ft.Text(
                                "Правильно!" if is_ok else ("Не совсем так..." if is_ru else "Не зусім так..."),
                                weight=ft.FontWeight.BOLD,
                                size=15,
                                color=ft.Colors.GREEN_900 if is_ok else ft.Colors.RED_900
                            )
                        ]
                    ),
                    ft.Text(
                        exp_text,
                        size=13,
                        color=ft.Colors.GREEN_900 if is_ok else ft.Colors.RED_900
                    )
                ]
            )

            if quiz_type != "photo" and media_src:
                exp_header_row = ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            width=72,
                            height=72,
                            border_radius=10,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            bgcolor=ft.Colors.SURFACE,
                            border=ft.Border.all(1, ft.Colors.GREEN_300 if is_ok else ft.Colors.RED_300),
                            content=ft.Image(src=media_src, width=72, height=72, fit="cover")
                        ),
                        exp_text_block
                    ]
                )
                exp_controls = [exp_header_row]
            else:
                exp_controls = [exp_text_block]

            # Кнопка перехода к паспорту вида в Красной книге
            if species_id and self.on_select_species:
                exp_controls.append(
                    ft.Container(
                        padding=ft.Padding.only(top=6),
                        content=ft.OutlinedButton(
                            content=ft.Text(
                                "Паспорт вида в Красной книге Беларуси" if is_ru else "Пашпарт віду ў Чырвонай кнізе Беларусі"
                            ),
                            icon=ft.Icons.AUTO_STORIES,
                            style=ft.ButtonStyle(
                                color=AppColors.PRIMARY,
                                side=ft.BorderSide(1, AppColors.PRIMARY),
                                shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            on_click=lambda e, sid=species_id: self._open_species(sid)
                        )
                    )
                )

            explanation_card = ft.Container(
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.GREEN_50 if is_ok else ft.Colors.RED_50,
                border=ft.Border.all(1, ft.Colors.GREEN_300 if is_ok else ft.Colors.RED_300),
                content=ft.Column(
                    spacing=8,
                    controls=exp_controls
                )
            )

        # Нижняя кнопка действия
        is_last = (self.current_index + 1 >= total_q)
        if not self.answer_checked:
            action_btn = ft.FilledButton(
                content=ft.Text("Проверить ответ" if is_ru else "Праверыць адказ"),
                icon=ft.Icons.CHECK,
                disabled=(self.selected_option is None),
                style=ft.ButtonStyle(
                    bgcolor=AppColors.PRIMARY,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=self._handle_action_btn
            )
        else:
            if is_last:
                action_btn = ft.FilledButton(
                    content=ft.Text("Завершить и получить сертификат" if is_ru else "Завяршыць і атрымаць сертыфікат"),
                    icon=ft.Icons.WORKSPACE_PREMIUM,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._handle_action_btn
                )
            else:
                action_btn = ft.FilledButton(
                    content=ft.Text("Следующий вопрос" if is_ru else "Наступнае пытанне"),
                    icon=ft.Icons.ARROW_FORWARD,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._handle_action_btn
                )

        return ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=20),
            spacing=16,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        max_width=760,
                        content=ft.Column(
                            spacing=16,
                            controls=[
                                top_bar,
                                progress_block,
                                question_card,
                                ft.Column(spacing=10, controls=option_buttons),
                                explanation_card,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    controls=[action_btn]
                                )
                            ]
                        )
                    )
                )
            ]
        )

    # =========================================================================
    # ЭКРАН 3: АКАДЕМИЧЕСКИЙ СЕРТИФИКАТ И ИТОГИ
    # =========================================================================
    def _build_certificate_view(self, lang: str) -> ft.Control:
        is_ru = (lang == "ru")
        total_count = len(self.session_quizzes) if self.session_quizzes else quiz_service.total_answered
        cert = quiz_service.get_certificate_data(
            user_name=self.student_name,
            total_count=total_count,
            language=lang
        )

        diploma_card = ft.Card(
            elevation=1,
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
                padding=28,
                bgcolor=ft.Colors.SURFACE,
                border=ft.Border.all(2, AppColors.PRIMARY),
                border_radius=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                    controls=[
                        # Эмблема и гербовый заголовок
                        ft.Icon(ft.Icons.WORKSPACE_PREMIUM, size=52, color=AppColors.PRIMARY),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "РЕСПУБЛИКА БЕЛАРУСЬ • НАЦИОНАЛЬНАЯ СИСТЕМА ОХРАНЫ ПРИРОДЫ" if is_ru else "РЭСПУБЛІКА БЕЛАРУСЬ • НАЦЫЯНАЛЬНАЯ СІСТЭМА АХОВЫ ПРЫРОДЫ",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=AppColors.TEXT_MUTED_LIGHT
                                ),
                                ft.Text(
                                    "СЕРТИФИКАТ ЗНАНИЙ" if is_ru else "СЕРТЫФІКАТ ВЕДАЎ",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=AppColors.PRIMARY
                                ),
                                ft.Text(
                                    "по результатам экологического тестирования Красной книги Беларуси" if is_ru else "па выніках экалагічнага тэсціравання Чырвонай кнігі Беларусі",
                                    size=13,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER
                                )
                            ]
                        ),
                        # Поле ввода имени учащегося
                        ft.Container(
                            width=380,
                            content=ft.TextField(
                                label="ФИО исследователя / учащегося" if is_ru else "Прозвішча і імя даследчыка",
                                value=self.student_name,
                                prefix_icon=ft.Icons.PERSON,
                                border_radius=10,
                                text_size=14,
                                on_change=self._update_student_name
                            )
                        ),
                        # Блок академического ранга
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                            border_radius=12,
                            bgcolor=AppColors.PRIMARY_CONTAINER,
                            border=ft.Border.all(1, AppColors.PRIMARY_LIGHT),
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        cert["rank"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppColors.PRIMARY,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Text(
                                        cert["badge_title"],
                                        size=12,
                                        color=AppColors.TEXT_MUTED_LIGHT,
                                        text_align=ft.TextAlign.CENTER
                                    )
                                ]
                            )
                        ),
                        # Метрики результатов в 3 плашках
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=14,
                            wrap=True,
                            controls=[
                                self._build_stat_tile(
                                    ft.Icons.CHECK_CIRCLE_OUTLINE,
                                    "Результат" if is_ru else "Вынік",
                                    cert["score"]
                                ),
                                self._build_stat_tile(
                                    ft.Icons.PERCENT,
                                    "Точность" if is_ru else "Дакладнасць",
                                    cert["percentage"]
                                ),
                                self._build_stat_tile(
                                    ft.Icons.BOLT,
                                    "Макс. серия" if is_ru else "Макс. серыя",
                                    f"{cert['streak']} подряд" if is_ru else f"{cert['streak']} запар"
                                )
                            ]
                        ),
                        # Кнопки управления
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                            wrap=True,
                            controls=[
                                ft.OutlinedButton(
                                    content=ft.Text("Все разделы" if is_ru else "Усе раздзелы"),
                                    icon=ft.Icons.GRID_VIEW,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    on_click=self._return_to_categories
                                ),
                                ft.FilledButton(
                                    content=ft.Text("Пройти тему снова" if is_ru else "Прайсці тэму нанова"),
                                    icon=ft.Icons.REFRESH,
                                    style=ft.ButtonStyle(
                                        bgcolor=AppColors.PRIMARY,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    on_click=self._restart_current_category
                                )
                            ]
                        )
                    ]
                )
            )
        )

        return ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=24),
            spacing=16,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        max_width=720,
                        content=diploma_card
                    )
                )
            ]
        )

    def _build_stat_tile(self, icon: str, label: str, value: str) -> ft.Control:
        return ft.Container(
            width=150,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Icon(icon, size=20, color=AppColors.PRIMARY),
                    ft.Text(label, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(value, size=15, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN_LIGHT)
                ]
            )
        )

    # =========================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ И НАВИГАЦИИ
    # =========================================================================
    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass

    def _start_category(self, category_id: str):
        self.active_category_id = category_id
        self.session_quizzes = quiz_service.start_session(category_id, limit=10)
        self.current_index = 0
        self.selected_option = None
        self.answer_checked = False
        self.last_result = None
        self.view_state = "question"
        self._build_ui()
        self._safe_update()

    def _return_to_categories(self, e):
        self.view_state = "categories"
        self._build_ui()
        self._safe_update()

    def _restart_current_category(self, e):
        self._start_category(self.active_category_id)

    def _select_option(self, idx: int):
        self.selected_option = idx
        self._build_ui()
        self._safe_update()

    def _handle_action_btn(self, e):
        lang = self.get_language()
        if not self.answer_checked:
            if self.selected_option is None:
                return
            current_quiz = self.session_quizzes[self.current_index]
            res = quiz_service.check_answer(current_quiz["id"], self.selected_option, lang)
            self.last_result = res
            self.answer_checked = True
        else:
            if self.current_index + 1 >= len(self.session_quizzes):
                self.view_state = "certificate"
            else:
                self.current_index += 1
                self.selected_option = None
                self.answer_checked = False
                self.last_result = None

        self._build_ui()
        self._safe_update()

    def _update_student_name(self, e):
        self.student_name = e.control.value

    def _open_species(self, species_id: str):
        if self.on_select_species and species_id:
            self.on_select_species(species_id)
