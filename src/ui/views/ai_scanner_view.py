import flet as ft
from typing import Callable, Optional
from ...services.ai_service import ai_service
from ..theme import AppColors, get_category_color

class AIScannerView(ft.Container):
    def __init__(self, on_select_species: Callable[[str], None], get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.on_select_species = on_select_species
        self.get_language = get_language
        self.active_tab = 0 # 0: Сканер, 1: Чат-гид
        self.scanner_result: Optional[dict] = None
        self.chat_messages = []
        self.is_track_mode = False

        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()

        # Вкладки: Сканер видов / Диалог с гидом
        tabs_header = ft.Row(
            spacing=10,
            controls=[
                ft.FilledButton(
                    content="🔍 ИИ-Определитель" if lang == "ru" else "🔍 ІІ-Азначнік",
                    icon=ft.Icons.CAMERA_ALT,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY if self.active_tab == 0 else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        color=ft.Colors.WHITE if self.active_tab == 0 else ft.Colors.ON_SURFACE
                    ),
                    on_click=lambda e: self._switch_tab(0)
                ),
                ft.FilledButton(
                    content="💬 Гид-натуралист" if lang == "ru" else "💬 Гід-натураліст",
                    icon=ft.Icons.CHAT,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY if self.active_tab == 1 else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        color=ft.Colors.WHITE if self.active_tab == 1 else ft.Colors.ON_SURFACE
                    ),
                    on_click=lambda e: self._switch_tab(1)
                )
            ]
        )

        if self.active_tab == 0:
            tab_content = self._build_scanner_tab(lang)
        else:
            tab_content = self._build_chat_tab(lang)

        self.content = ft.Column(
            expand=True,
            spacing=14,
            controls=[
                ft.Container(padding=ft.Padding.only(left=16, right=16, top=16), content=tabs_header),
                ft.Container(expand=True, padding=ft.Padding.only(left=16, right=16, bottom=16), content=tab_content)
            ]
        )

    def _switch_tab(self, tab_idx: int):
        self.active_tab = tab_idx
        self._build_ui()
        self.update()

    def _build_scanner_tab(self, lang: str) -> ft.Control:
        self.input_field = ft.TextField(
            hint_text="Опишите вид или ключевые признаки (напр. 'черная птица с красным клювом', 'след копыт')...",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            border_radius=12,
            expand=True
        )

        quick_tests = [
            ("Европейский зубр", "крупное рогатое животное с бородой"),
            ("Черный аист", "черная лесная птица с красным клювом и ногами"),
            ("След рыси", "круглый след кошачьих на снегу без когтей"),
            ("Обыкновенная медянка", "небольшая змея с круглым зрачком и темной полосой через глаз"),
            ("Венерин башмачок", "желтый цветок в форме башмачка с бурыми лепестками"),
            ("Грибная капуста", "шаровидный кудрявый гриб у корней сосны")
        ]

        chips = [
            ft.Chip(
                label=ft.Text(label, size=11),
                on_click=lambda e, txt=hint: self._run_analysis(txt)
            )
            for label, hint in quick_tests
        ]

        result_container = ft.Container()
        if self.scanner_result:
            res = self.scanner_result
            cat_color = get_category_color(res["category"])

            result_container = ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.CHECK_CIRCLE, bgcolor=ft.Colors.GREEN, size=24),
                                            ft.Text("Результат ИИ-анализа" if lang == "ru" else "Вынік ІІ-аналізу", weight=ft.FontWeight.BOLD, size=16)
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=20,
                                        bgcolor=cat_color,
                                        content=ft.Text(f"Категория {res['category']}", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
                                    )
                                ]
                            ),
                            ft.Text(f"{res['name_ru']} ({res['name_lat']})", size=18, weight=ft.FontWeight.BOLD),
                            ft.ProgressBar(value=res["confidence"], color=ft.Colors.GREEN),
                            ft.Text(f"Уверенность распознавания: {int(res['confidence']*100)}%", size=12, color=AppColors.TEXT_MUTED_LIGHT),
                            ft.Container(
                                padding=12,
                                border_radius=8,
                                bgcolor=ft.Colors.RED_50,
                                border=ft.Border.all(1, ft.Colors.RED_200),
                                content=ft.Text(res["warning"], size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900)
                            ),
                            ft.Text(f"• {res['distinguishing_features']}", size=12),
                            ft.Text(f"• Характерный биотоп: {res['habitat']}", size=12),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    ft.FilledButton(
                                        content="Открыть карточку вида" if lang == "ru" else "Адкрыць картку віду",
                                        icon=ft.Icons.ARROW_FORWARD,
                                        on_click=lambda e: self.on_select_species(res["species_id"])
                                    )
                                ]
                            )
                        ]
                    )
                )
            )

        return ft.ListView(
            expand=True,
            spacing=14,
            controls=[
                ft.Text("Компьютерное зрение и идентификация редких видов" if lang == "ru" else "Камп'ютарны зрок і ідэнтыфікацыя рэдкіх відаў", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Введите описание замеченного животного, растения, гриба или отпечатка следов:", size=13, color=AppColors.TEXT_MUTED_LIGHT),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.input_field,
                        ft.FilledButton(
                            content="Определить",
                            icon=ft.Icons.AUTO_AWESOME,
                            on_click=lambda e: self._run_analysis(self.input_field.value)
                        )
                    ]
                ),
                ft.Text("Быстрые примеры для проверки ИИ:" if lang == "ru" else "Хуткія прыклады для праверкі ІІ:", size=12, weight=ft.FontWeight.BOLD),
                ft.Row(wrap=True, spacing=6, controls=chips),
                result_container
            ]
        )

    def _run_analysis(self, hint: str):
        if not hint:
            return
        res = ai_service.identify_species(hint=hint)
        self.scanner_result = res
        self._build_ui()
        self.update()

    def _build_chat_tab(self, lang: str) -> ft.Control:
        chat_list = ft.ListView(
            expand=True,
            spacing=10,
            controls=[]
        )

        if not self.chat_messages:
            self.chat_messages.append({
                "role": "assistant",
                "text": ai_service.ask_naturalist("", lang)
            })

        for msg in self.chat_messages:
            is_user = (msg["role"] == "user")
            chat_list.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=12,
                            bgcolor=AppColors.PRIMARY if is_user else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            max_width=480,
                            content=ft.Text(
                                msg["text"],
                                size=13,
                                color=ft.Colors.WHITE if is_user else ft.Colors.ON_SURFACE
                            )
                        )
                    ]
                )
            )

        self.chat_input = ft.TextField(
            hint_text="Задайте вопрос гиду-натуралисту...",
            expand=True,
            border_radius=12,
            filled=True,
            on_submit=lambda e: self._send_chat_message()
        )

        quick_questions = [
            "Что делать, если нашел птенца совы?",
            "Какой штраф за сбор сон-травы?",
            "Расскажи про европейского зубра"
        ]

        q_chips = [
            ft.Chip(
                label=ft.Text(q, size=11),
                on_click=lambda e, question=q: self._send_quick_question(question)
            )
            for q in quick_questions
        ]

        return ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(wrap=True, spacing=6, controls=q_chips),
                ft.Container(expand=True, content=chat_list),
                ft.Row(
                    spacing=8,
                    controls=[
                        self.chat_input,
                        ft.IconButton(
                            icon=ft.Icons.SEND,
                            icon_color=AppColors.PRIMARY,
                            on_click=lambda e: self._send_chat_message()
                        )
                    ]
                )
            ]
        )

    def _send_chat_message(self):
        text = self.chat_input.value
        if not text:
            return
        lang = self.get_language()
        self.chat_messages.append({"role": "user", "text": text})
        ans = ai_service.ask_naturalist(text, lang)
        self.chat_messages.append({"role": "assistant", "text": ans})
        self.chat_input.value = ""
        self._build_ui()
        self.update()

    def _send_quick_question(self, question: str):
        lang = self.get_language()
        self.chat_messages.append({"role": "user", "text": question})
        ans = ai_service.ask_naturalist(question, lang)
        self.chat_messages.append({"role": "assistant", "text": ans})
        self._build_ui()
        self.update()

