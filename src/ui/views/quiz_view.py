import flet as ft
from typing import Callable, Optional
from ...services.quiz_service import quiz_service
from ..theme import AppColors

class QuizView(ft.Container):
    def __init__(self, get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.get_language = get_language
        self.current_index = 0
        self.selected_option: Optional[int] = None
        self.answer_checked = False
        self.last_result: Optional[dict] = None
        self.quizzes = quiz_service.get_all_quizzes()

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()

        if not self.quizzes or self.current_index >= len(self.quizzes):
            # Финал викторины / Сертификат
            cert = quiz_service.get_certificate_data("Учащийся", lang)
            self.content = ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=24,
                content=ft.Card(
                    elevation=4,
                    content=ft.Container(
                        padding=24,
                        width=500,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                            controls=[
                                ft.Icon(ft.Icons.EMOJI_EVENTS, size=64, bgcolor=ft.Colors.AMBER_600),
                                ft.Text("ВИКТОРИНА ЗАВЕРШЕНА!" if lang == "ru" else "ВІКТАРЫНА ЗАВЯРШЫЛАСЯ!", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Ваш результат: {cert['score']} ({cert['percentage']})", size=16),
                                ft.Container(
                                    padding=12,
                                    border_radius=8,
                                    bgcolor=AppColors.PRIMARY_CONTAINER,
                                    content=ft.Text(f"Присвоенный ранг: {cert['rank']}", weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY)
                                ),
                                ft.FilledButton(
                                    content="Пройти заново" if lang == "ru" else "Прайсці нанова",
                                    icon=ft.Icons.REFRESH,
                                    on_click=self._restart_quizzes
                                )
                            ]
                        )
                    )
                )
            )
            return

        current_quiz = self.quizzes[self.current_index]
        q_text = current_quiz["question_be"] if lang == "be" else current_quiz["question_ru"]
        options = current_quiz["options_be"] if lang == "be" else current_quiz["options_ru"]

        # Кнопки вариантов ответа
        option_buttons = []
        for i, opt in enumerate(options):
            is_selected = (self.selected_option == i)
            
            btn_color = ft.Colors.SURFACE
            border_color = ft.Colors.OUTLINE_VARIANT
            text_color = ft.Colors.ON_SURFACE

            if self.answer_checked:
                if i == current_quiz["correct_index"]:
                    btn_color = ft.Colors.GREEN_100
                    border_color = ft.Colors.GREEN_600
                    text_color = ft.Colors.GREEN_900
                elif is_selected:
                    btn_color = ft.Colors.RED_100
                    border_color = ft.Colors.RED_600
                    text_color = ft.Colors.RED_900

            option_buttons.append(
                ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor=btn_color,
                    border=ft.Border.all(2 if (is_selected or (self.answer_checked and i == current_quiz["correct_index"])) else 1, border_color),
                    ink=not self.answer_checked,
                    on_click=(lambda e, idx=i: self._select_option(idx)) if not self.answer_checked else None,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=28,
                                height=28,
                                border_radius=14,
                                bgcolor=AppColors.PRIMARY if is_selected else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    chr(65 + i), # A, B, C, D
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE if is_selected else ft.Colors.GREY_700
                                )
                            ),
                            ft.Text(opt, size=14, weight=ft.FontWeight.W_500, color=text_color, expand=True)
                        ]
                    )
                )
            )

        # Блок пояснения после ответа
        explanation_box = ft.Container()
        if self.answer_checked and self.last_result:
            is_ok = self.last_result["is_correct"]
            explanation_box = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.GREEN_50 if is_ok else ft.Colors.RED_50,
                border=ft.Border.all(1, ft.Colors.GREEN_300 if is_ok else ft.Colors.RED_300),
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE if is_ok else ft.Icons.CANCEL, color=ft.Colors.GREEN_700 if is_ok else ft.Colors.RED_700),
                                ft.Text("Правильно!" if is_ok else "Не совсем так...", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900 if is_ok else ft.Colors.RED_900)
                            ]
                        ),
                        ft.Text(self.last_result["explanation"], size=13, color=ft.Colors.GREEN_900 if is_ok else ft.Colors.RED_900)
                    ]
                )
            )

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.all(16),
            spacing=16,
            controls=[
                # Прогресс
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"Вопрос {self.current_index + 1} из {len(self.quizzes)}", weight=ft.FontWeight.BOLD, size=14, color=AppColors.PRIMARY),
                        ft.Text(f"Баллы: {quiz_service.current_score}", weight=ft.FontWeight.BOLD, size=14)
                    ]
                ),
                ft.ProgressBar(value=(self.current_index + 1) / len(self.quizzes), color=AppColors.PRIMARY),
                # Текст вопроса
                ft.Card(
                    content=ft.Container(
                        padding=18,
                        content=ft.Text(q_text, size=17, weight=ft.FontWeight.BOLD)
                    )
                ),
                # Варианты ответов
                ft.Column(spacing=10, controls=option_buttons),
                explanation_box,
                # Кнопка действия (Проверить или Далее)
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.FilledButton(
                            content="Проверить ответ" if not self.answer_checked else ("Следующий вопрос" if lang == "ru" else "Наступнае пытанне"),
                            icon=ft.Icons.CHECK if not self.answer_checked else ft.Icons.ARROW_FORWARD,
                            disabled=(self.selected_option is None and not self.answer_checked),
                            on_click=self._handle_action_btn
                        )
                    ]
                )
            ]
        )

    def _select_option(self, idx: int):
        self.selected_option = idx
        self._build_ui()
        self.update()

    def _handle_action_btn(self, e):
        lang = self.get_language()
        if not self.answer_checked:
            current_quiz = self.quizzes[self.current_index]
            res = quiz_service.check_answer(current_quiz["id"], self.selected_option, lang)
            self.last_result = res
            self.answer_checked = True
        else:
            self.current_index += 1
            self.selected_option = None
            self.answer_checked = False
            self.last_result = None

        self._build_ui()
        self.update()

    def _restart_quizzes(self, e):
        quiz_service.reset_score()
        self.current_index = 0
        self.selected_option = None
        self.answer_checked = False
        self.last_result = None
        self._build_ui()
        self.update()

