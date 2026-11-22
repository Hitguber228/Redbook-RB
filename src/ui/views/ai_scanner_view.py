import os
import time
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
        self.analyzed_image: Optional[str] = None
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)

        self._build_ui()

    def did_mount(self):
        if self.page:
            # В Flet 1.1+ FilePicker регистрируется в page.services (не в overlay, чтобы избежать ошибки Unknown control)
            if hasattr(self.page, "services") and self.file_picker not in self.page.services:
                self.page.services.append(self.file_picker)
            if hasattr(self.page, "overlay") and self.file_picker in self.page.overlay:
                self.page.overlay.remove(self.file_picker)
            self.page.update()

    def _open_camera_capture(self, e=None):
        # На смартфонах через Web/PWA активирует камеру
        if self.page:
            try:
                self.page.run_task(
                    self.file_picker.pick_files,
                    dialog_title="Сфотографируйте вид камерой смартфона" if self.get_language() == "ru" else "Сфатаграфуйце від камерай смартфона",
                    file_type=ft.FilePickerFileType.IMAGE,
                    allow_multiple=False,
                    with_data=True
                )
            except Exception:
                self._open_file_dialog()

    def _open_file_dialog(self, e=None):
        # 1. Если запущено на десктопе Windows — открываем нативный проводник Windows через tkinter
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askopenfilename(
                title="Выберите фото животного или растения",
                filetypes=[
                    ("Изображения", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.gif"),
                    ("Все файлы", "*.*")
                ]
            )
            root.destroy()
            if selected and os.path.exists(selected):
                self._run_image_analysis(selected)
                return
        except Exception:
            pass

        # 2. Если режим Web / PWA (или мобильный) — вызываем через асинхронный task Flet
        if self.page:
            self.page.run_task(
                self.file_picker.pick_files,
                dialog_title="Выберите фото из медиатеки или папки" if self.get_language() == "ru" else "Выберыце фота з медыятэкі ці тэчкі",
                file_type=ft.FilePickerFileType.IMAGE,
                allow_multiple=False,
                with_data=True
            )

    def _paste_from_clipboard(self, e=None):
        try:
            from PIL import ImageGrab, Image
            content = ImageGrab.grabclipboard()

            # 1. Если в буфере обмена находится изображение (скриншот, скопированное фото)
            if isinstance(content, Image.Image):
                upload_dir = os.path.abspath(os.path.join("assets", "uploads"))
                os.makedirs(upload_dir, exist_ok=True)
                temp_filename = f"clipboard_{int(time.time() * 1000)}.jpg"
                save_path = os.path.join(upload_dir, temp_filename)

                img_rgb = content.convert("RGB") if content.mode in ("RGBA", "P", "LA") else content
                img_rgb.save(save_path, "JPEG", quality=85)

                if self.page:
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=18),
                                ft.Text("Изображение успешно вставлено из буфера обмена!")
                            ]),
                            bgcolor=ft.Colors.GREEN_700
                        )
                    )
                self._run_image_analysis(save_path)
                return

            # 2. Если в буфере обмена скопирован файл (например, через Ctrl+C в проводнике Windows)
            elif isinstance(content, list) and len(content) > 0:
                candidate = content[0]
                if isinstance(candidate, str) and os.path.exists(candidate):
                    ext = os.path.splitext(candidate)[1].lower()
                    if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
                        if self.page:
                            self.page.open(
                                ft.SnackBar(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=18),
                                        ft.Text(f"Файл вставлен из буфера: {os.path.basename(candidate)}")
                                    ]),
                                    bgcolor=ft.Colors.GREEN_700
                                )
                            )
                        self._run_image_analysis(candidate)
                        return

            # 3. Буфер пуст или не содержит картинки
            if self.page:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.WHITE, size=18),
                            ft.Text("В буфере обмена нет картинки. Скопируйте фото (или Win+Shift+S) и нажмите кнопку снова.")
                        ]),
                        bgcolor=ft.Colors.AMBER_800
                    )
                )
        except Exception as ex:
            if self.page:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Ошибка чтения буфера обмена: {ex}"),
                        bgcolor=ft.Colors.RED_700
                    )
                )

    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_item = e.files[0]
            # 1. Если передан прямой путь файловой системы (Windows Desktop)
            if file_item.path and os.path.exists(file_item.path):
                self._run_image_analysis(file_item.path)
                return

            # 2. Если фото снято на камеру смартфона или выбрано в браузере (iPhone / Android)
            raw_bytes = getattr(file_item, "bytes", None)
            if raw_bytes:
                upload_dir = os.path.abspath(os.path.join("assets", "uploads"))
                os.makedirs(upload_dir, exist_ok=True)
                temp_filename = f"capture_{int(time.time() * 1000)}.jpg"
                save_path = os.path.join(upload_dir, temp_filename)
                with open(save_path, "wb") as f:
                    f.write(raw_bytes)
                self._run_image_analysis(save_path)

    def _build_ui(self):
        lang = self.get_language()

        # Вкладки: Сканер видов / Диалог с гидом
        tabs_header = ft.Row(
            spacing=10,
            controls=[
                ft.FilledButton(
                    content=ft.Text("ИИ-Определитель" if lang == "ru" else "ІІ-Азначнік"),
                    icon=ft.Icons.CAMERA_ALT,
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY if self.active_tab == 0 else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        color=ft.Colors.WHITE if self.active_tab == 0 else ft.Colors.ON_SURFACE
                    ),
                    on_click=lambda e: self._switch_tab(0)
                ),
                ft.FilledButton(
                    content=ft.Text("Гид-натуралист" if lang == "ru" else "Гід-натураліст"),
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
            hint_text="Опишите вид или ключевые признаки (напр. 'черная птица с красным клювом', 'след копыт')..." if lang == "ru" else "Апішыце від ці прыкметы (напр. 'чорная птушка з чырвонай дзюбай', 'след капыт')...",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            border_radius=12,
            expand=True
        )

        # Образцы фотографий для моментального тестирования ИИ-модели
        sample_photos = [
            ("Зубр", "assets/images/species/bison-bonasus.jpg"),
            ("Рысь", "assets/images/species/lynx-lynx.jpg"),
            ("Неясыть", "assets/images/species/strix-nebulosa.jpg"),
            ("Баранец", "assets/images/species/huperzia-selago.jpg"),
            ("Черепаха", "assets/images/species/emys-orbicularis.jpg"),
            ("Жук-олень", "assets/images/species/lucanus-cervus.jpg")
        ]

        sample_chips = []
        for name, path in sample_photos:
            abs_p = os.path.abspath(path)
            if os.path.exists(abs_p):
                sample_chips.append(
                    ft.Chip(
                        leading=ft.Icon(ft.Icons.IMAGE, size=14, color=AppColors.PRIMARY),
                        label=ft.Text(f"{name}", size=11, weight=ft.FontWeight.W_500),
                        on_click=lambda e, p=abs_p: self._run_image_analysis(p)
                    )
                )

        quick_tests = [
            ("След зубра", "крупное рогатое животное с бородой и следы копыт", True),
            ("Черный аист", "черная лесная птица с красным клювом и ногами", False),
            ("След рыси", "круглый след кошачьих на снегу без когтей", True),
            ("Венерин башмачок", "желтый цветок в форме башмачка с бурыми лепестками", False),
            ("Грибная капуста", "шаровидный кудрявый гриб у корней сосны", False)
        ]

        text_chips = [
            ft.Chip(
                leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=14),
                label=ft.Text(label, size=11),
                on_click=lambda e, txt=hint, tr=track: self._run_text_analysis(txt, tr)
            )
            for label, hint, track in quick_tests
        ]

        result_container = ft.Container()
        if self.scanner_result:
            res = self.scanner_result
            cat_color = get_category_color(res.get("category", "IV"))
            conf = res.get("confidence", 0.0)
            conf_percent = int(conf * 100) if conf <= 1.0 else int(conf)
            is_uncertain = res.get("is_uncertain", False)
            top_candidates = res.get("top_candidates", [])

            # Блок миниатюры фото, если было проанализировано изображение
            img_preview = None
            if self.analyzed_image and os.path.exists(self.analyzed_image):
                img_preview = ft.Container(
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src=self.analyzed_image,
                        height=160,
                        width=240,
                        fit="cover"
                    )
                )

            # Функция создания красивой карточки кандидата
            def _create_candidate_card(cand: dict, is_primary_choice: bool = False):
                c_conf = cand.get("confidence", 0.0)
                c_pct = int(c_conf * 100) if c_conf <= 1.0 else int(c_conf)
                c_cat_col = get_category_color(cand.get("category", "IV"))
                name_disp = cand.get("name_be" if lang == "be" else "name_ru", cand.get("id"))
                img_src = cand.get("image_url", "")

                return ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if not is_primary_choice else ft.Colors.SURFACE,
                    border=ft.Border.all(1.5, AppColors.PRIMARY if is_primary_choice else ft.Colors.OUTLINE_VARIANT),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=4, color=ft.Colors.BLACK_12) if is_primary_choice else None,
                    content=ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=68,
                                height=68,
                                border_radius=10,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(
                                    src=img_src,
                                    fit="cover",
                                    error_content=ft.Container(
                                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(ft.Icons.ECO, color=AppColors.PRIMARY, size=26)
                                    )
                                )
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(name_disp, size=14, weight=ft.FontWeight.BOLD),
                                            ft.Container(
                                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=6,
                                                bgcolor=c_cat_col,
                                                content=ft.Text(f"Кат. {cand.get('category', 'IV')}", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                            )
                                        ]
                                    ),
                                    ft.Text(cand.get("name_lat", ""), italic=True, size=11, color=AppColors.TEXT_MUTED_LIGHT),
                                    ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.ProgressBar(
                                                value=c_conf if c_conf <= 1.0 else c_conf/100,
                                                color=AppColors.PRIMARY if not is_uncertain else ft.Colors.AMBER_700,
                                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                                width=110,
                                                height=6
                                            ),
                                            ft.Text(
                                                f"Сходство {c_pct}%" if lang == "ru" else f"Супадзенне {c_pct}%",
                                                size=11,
                                                weight=ft.FontWeight.BOLD,
                                                color=AppColors.PRIMARY if not is_uncertain else ft.Colors.AMBER_800
                                            )
                                        ]
                                    ),
                                    ft.Text(
                                        f"Биотоп: {cand.get('habitat', '')}" if lang == "ru" else f"Біятоп: {cand.get('habitat', '')}",
                                        size=11,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    ) if cand.get("habitat") else ft.Container()
                                ]
                            ),
                            ft.FilledButton(
                                content=ft.Text("Паспорт →" if lang == "ru" else "Пашпарт →"),
                                icon=ft.Icons.ARROW_FORWARD,
                                style=ft.ButtonStyle(
                                    bgcolor=AppColors.PRIMARY if is_primary_choice else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                    color=ft.Colors.WHITE if is_primary_choice else ft.Colors.ON_SURFACE
                                ),
                                on_click=lambda e, sid=cand["id"]: self.on_select_species(sid)
                            )
                        ]
                    )
                )

            if is_uncertain:
                # ВАРИАНТ А: НЕЙРОСЕТЬ НЕ УВЕРЕНА — ПОКАЗЫВАЕМ НЕСКОЛЬКО ВАРИАНТОВ
                cand_cards = [
                    _create_candidate_card(c, is_primary_choice=(idx == 0))
                    for idx, c in enumerate(top_candidates[:4])
                ]

                result_container = ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=14,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.AMBER_800, size=24),
                                                ft.Text(
                                                    "Нейросеть не уверена: найдено несколько вариантов" if lang == "ru" else "Нейрасетка не ўпэўненая: знойдзена некалькі варыянтаў",
                                                    weight=ft.FontWeight.BOLD,
                                                    size=15,
                                                    color=ft.Colors.AMBER_900
                                                )
                                            ]
                                        ),
                                        ft.Container(
                                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                            border_radius=12,
                                            bgcolor=ft.Colors.AMBER_100,
                                            border=ft.Border.all(1, ft.Colors.AMBER_400),
                                            content=ft.Text(
                                                "Требуется уточнение" if lang == "ru" else "Патрабуецца ўдакладненне",
                                                color=ft.Colors.AMBER_900,
                                                size=11,
                                                weight=ft.FontWeight.BOLD
                                            )
                                        )
                                    ]
                                ),
                                ft.Text(
                                    "Признаки снимка или описания частично совпадают сразу с несколькими видами Красной книги Беларуси. Ознакомьтесь с кандидатами и выберите подходящий вид для просмотра паспорта:" if lang == "ru" else "Прыкметы здымка ці апісання падыходзяць да некалькіх відаў Чырвонай кнігі. Азнаёмцеся з кандыдатамі і абярыце адпаведны пашпарт:",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                                *([img_preview] if img_preview else []),
                                ft.Column(spacing=8, controls=cand_cards)
                            ]
                        )
                    )
                )
            else:
                # ВАРИАНТ Б: ВЫСОКАЯ УВЕРЕННОСТЬ — ОТОБРАЖАЕМ ГЛАВНЫЙ ВИД + ДРУГИЕ ВАРИАНТЫ ДЛЯ СРАВНЕНИЯ
                other_candidates = [
                    _create_candidate_card(c, is_primary_choice=False)
                    for c in top_candidates[1:4]
                ]

                result_container = ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=24),
                                                ft.Text("Вид определен с высокой уверенностью" if lang == "ru" else "Від вызначаны з высокай дакладнасцю", weight=ft.FontWeight.BOLD, size=16)
                                            ]
                                        ),
                                        ft.Container(
                                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                            border_radius=20,
                                            bgcolor=cat_color,
                                            content=ft.Text(f"Категория {res.get('category', 'IV')}", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
                                        )
                                    ]
                                ),
                                ft.Row(
                                    spacing=16,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ctrl for ctrl in [
                                            img_preview,
                                            ft.Column(
                                                expand=True,
                                                spacing=6,
                                                controls=[
                                                    ft.Text(f"{res.get('name_ru', '')} ({res.get('name_lat', '')})", size=17, weight=ft.FontWeight.BOLD),
                                                    ft.ProgressBar(value=conf if conf <= 1.0 else conf/100, color=ft.Colors.GREEN_600),
                                                    ft.Row(
                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                        controls=[
                                                            ft.Text(f"Уверенность сходства: {conf_percent}%", size=12, color=AppColors.TEXT_MUTED_LIGHT),
                                                            ft.Text("ONNX CPU • 100% Офлайн", size=11, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD)
                                                        ]
                                                    ),
                                                    ft.Container(
                                                        padding=10,
                                                        border_radius=8,
                                                        bgcolor=ft.Colors.RED_50,
                                                        border=ft.Border.all(1, ft.Colors.RED_200),
                                                        content=ft.Text(res.get("warning", ""), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900)
                                                    )
                                                ]
                                            )
                                        ] if ctrl is not None
                                    ]
                                ),
                                ft.Text(f"• {res.get('distinguishing_features', '')}", size=12),
                                ft.Text(f"• Характерный биотоп: {res.get('habitat', '')}", size=12),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    controls=[
                                        ft.FilledButton(
                                            content=ft.Text("Открыть паспорт вида в каталоге →" if lang == "ru" else "Адкрыць пашпарт віду ў каталогу →"),
                                            icon=ft.Icons.ARROW_FORWARD,
                                            on_click=lambda e: self.on_select_species(res.get("species_id", ""))
                                        )
                                    ]
                                ),
                                *([
                                    ft.Divider(height=1),
                                    ft.Text("Другие возможные варианты для сравнения:" if lang == "ru" else "Іншыя магчымыя варыянты для параўнання:", size=13, weight=ft.FontWeight.BOLD),
                                    ft.Column(spacing=6, controls=other_candidates)
                                ] if other_candidates else [])
                            ]
                        )
                    )
                )

        return ft.ListView(
            expand=True,
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Локальный ИИ-сканер редких видов Беларуси" if lang == "ru" else "Лакальны ІІ-сканер рэдкіх відаў Беларусі", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                            border_radius=12,
                            bgcolor=ft.Colors.GREEN_100,
                            content=ft.Row(
                                tight=True,
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.OFFLINE_BOLT, size=14, color=ft.Colors.GREEN_800),
                                    ft.Text("Офлайн ONNX (4.7 МБ)", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800)
                                ]
                            )
                        )
                    ]
                ),
                # Блок загрузки и моментальной фотосъемки с мобильного / ПК
                ft.Container(
                    padding=16,
                    border_radius=14,
                    border=ft.Border.all(1.5, AppColors.PRIMARY),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=12,
                                        controls=[
                                            ft.Icon(ft.Icons.ADD_A_PHOTO, size=28, color=AppColors.PRIMARY),
                                            ft.Column(
                                                spacing=2,
                                                controls=[
                                                    ft.Text("Сфотографировать или загрузить снимок" if lang == "ru" else "Сфатаграфаваць ці загрузіць здымак", size=14, weight=ft.FontWeight.BOLD),
                                                    ft.Text("На iPhone и Android сразу активируется камера" if lang == "ru" else "На iPhone і Android адразу актывуецца камера", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=10,
                                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                        content=ft.Row(
                                            tight=True,
                                            spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.PHONE_IPHONE, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                                                ft.Text("iOS • Android • ПК", size=11, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    )
                                ]
                            ),
                            ft.Row(
                                wrap=True,
                                spacing=10,
                                controls=[
                                    ft.FilledButton(
                                        content=ft.Text("Сделать фото (Камера)" if lang == "ru" else "Зрабіць фота (Камера)"),
                                        icon=ft.Icons.PHOTO_CAMERA,
                                        style=ft.ButtonStyle(
                                            bgcolor=AppColors.PRIMARY,
                                            color=ft.Colors.WHITE
                                        ),
                                        on_click=self._open_camera_capture
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Text("Медиатека / Файл" if lang == "ru" else "Медыятэка / Файл"),
                                        icon=ft.Icons.PHOTO_LIBRARY,
                                        on_click=self._open_file_dialog
                                    ),
                                    ft.FilledTonalButton(
                                        content=ft.Text("Вставить из буфера (Ctrl+V)" if lang == "ru" else "Уставіць з буфера (Ctrl+V)"),
                                        icon=ft.Icons.CONTENT_PASTE,
                                        on_click=self._paste_from_clipboard
                                    )
                                ]
                            )
                        ]
                    )
                ),
                ft.Text("Или протестируйте локальную нейросеть на образцах:" if lang == "ru" else "Ці пратэстуйце лакальную нейрасетку на ўзорах:", size=12, weight=ft.FontWeight.BOLD),
                ft.Row(wrap=True, spacing=6, controls=sample_chips),
                ft.Divider(height=1),
                ft.Text("Морфологический поиск по описанию и следам:" if lang == "ru" else "Пошук па апісанні і слядах:", size=12, weight=ft.FontWeight.BOLD),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.input_field,
                        ft.FilledButton(
                            content=ft.Text("Определить" if lang == "ru" else "Вызначыць"),
                            icon=ft.Icons.AUTO_AWESOME,
                            on_click=lambda e: self._run_text_analysis(self.input_field.value, False)
                        )
                    ]
                ),
                ft.Row(wrap=True, spacing=6, controls=text_chips),
                result_container,
                ft.Container(height=20)
            ]
        )

    def _run_image_analysis(self, image_path: str):
        if not image_path or not os.path.exists(image_path):
            return
        self.analyzed_image = image_path
        res = ai_service.identify_species(image_path=image_path)
        self.scanner_result = res
        self._build_ui()
        self.update()

    def _run_text_analysis(self, hint: str, is_track: bool = False):
        if not hint:
            return
        self.analyzed_image = None
        res = ai_service.identify_species(hint=hint, is_track=is_track)
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
