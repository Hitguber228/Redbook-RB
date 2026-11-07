import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Поля страницы (стандартные 2 см)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Цветовая гамма проекта
    PRIMARY_COLOR = RGBColor(45, 106, 79)    # Лесной темно-зеленый #2D6A4F
    DARK_TEXT = RGBColor(30, 41, 59)         # Темно-серый #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139)     # Приглушенный серый

    # Заголовок документа
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("ВЫБОР И ОБОСНОВАНИЕ ТЕХНОЛОГИЧЕСКОГО СТЕКА")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(17)
    r_title.font.color.rgb = PRIMARY_COLOR

    # Подзаголовок
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(18)
    r_sub = sub_p.add_run("Программный комплекс «Интерактивная Красная книга Республики Беларусь»")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = DARK_TEXT
    r_sub.italic = True

    # Блок с автором
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_table.rows[0].cells[0].paragraphs[0].add_run("Разработчик: Иван\nУчебный проект для внедрения в образование").font.size = Pt(10)
    meta_table.rows[0].cells[1].paragraphs[0].add_run("Направление: Кроссплатформенная разработка, ГИС и БД\nГод: 2026").font.size = Pt(10)
    meta_table.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    for row in meta_table.rows:
        for cell in row.cells:
            set_cell_background(cell, "F1F5F9")
            set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Функция добавления раздела
    def add_heading_section(num_str, title_str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(f"{num_str}. {title_str}")
        r.font.name = "Arial"
        r.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = PRIMARY_COLOR
        return h

    def add_body_p(text, bold_prefix="", space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(space_after)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.name = "Arial"
            r_b.font.size = Pt(11)
            r_b.font.color.rgb = DARK_TEXT
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_TEXT
        return p

    def add_bullet_p(title, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"{title}: ")
        r1.bold = True
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = PRIMARY_COLOR
        r2 = p.add_run(text)
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT
        return p

    # --- РАЗДЕЛ 1 ---
    add_heading_section("1", "Введение и задача проекта")
    add_body_p(
        "Цель проекта — создать современное, простое и красивое приложение об исчезающих и редких видах животных, растений и грибов Беларуси. "
        "Продукт рассчитан на реальное использование: его можно показывать на уроках биологии в школах, использовать на парах в колледжах и университетах, "
        "а также брать с собой в поездки и полевые экспедиции по лесам и заказникам."
    )
    add_body_p(
        "Перед выбором технологий мы сформулировали три главных практических требования:",
        bold_prefix="Главные требования заказчика: "
    )
    add_bullet_p("Работа без интернета (Офлайн)", "В лесу, на болоте или в классе без Wi-Fi приложение должно работать на 100%: открывать фото видов, запускать викторины, показывать карту и сохранять наблюдения.")
    add_bullet_p("Работа на компьютере и на телефонах", "Учитель за компьютером запускает приложение в виде быстрой программы Windows, а ученики со смартфонов могут подключиться к нему по Wi-Fi прямо в браузере без установки лишних программ.")
    add_bullet_p("Интерактивная карта", "Пользователь может кликнуть в любую точку страны или выбрать город, задать радиус поиска (3–30 км) и сразу увидеть, какие редкие птицы, звери или растения там обитают.")

    # --- РАЗДЕЛ 2 ---
    add_heading_section("2", "Язык программирования: Python 3")
    add_body_p(
        "Для написания всего проекта был выбран язык Python (версия 3.14).",
        bold_prefix="Почему именно Python: "
    )
    add_bullet_p("Простота и надежность кода", "Python позволяет сосредоточиться на логике приложения, биологических правилах и защите природы, не тратя месяцы на сложный рутинный код.")
    add_bullet_p("Единый язык для всего", "На Python написан и графический интерфейс, и локальная база данных, и алгоритмы поиска по карте, и даже ИИ-распознаватель видов. Не нужно учить 3 разных языка и связывать их между собой.")
    add_bullet_p("Отличная математика и базы данных", "В Python «из коробки» встроена поддержка СУБД SQLite, работа с форматами JSON и математические функции для расчета расстояний между координатами на поверхности Земли.")

    # --- РАЗДЕЛ 3 ---
    add_heading_section("3", "Графический интерфейс: Фреймворк Flet (движок Flutter)")
    add_body_p(
        "Главный выбор интерфейса стоял между старыми библиотеками (Tkinter, PyQt), веб-обертками (Electron) и современным фреймворком Flet.",
        bold_prefix="Обоснование интерфейса: "
    )
    add_bullet_p("Почему не Tkinter", "Tkinter сильно устарел визуально. Приложение выглядело бы как программа из 90-х годов и не вызвало бы интереса у современных школьников и студентов.")
    add_bullet_p("Почему не Electron", "Electron требует запуска целого скрытого браузера Chromium и потребляет более 500 МБ оперативной памяти, из-за чего старые школьные компьютеры начинают сильно тормозить.")
    add_bullet_p("Почему именно Flet", "Flet работает на сверхбыстром графическом движке Flutter (разработка Google). Он дает 60 кадров в секунду, плавную анимацию, современный аккуратный дизайн (Material Design 3) и умеет компилироваться под Windows, Web, iOS и Android из одного общего Python-файла.")

    # --- РАЗДЕЛ 4 ---
    add_heading_section("4", "База данных: Встроенная СУБД SQLite 3")
    add_body_p(
        "Для хранения научной информации о животных, истории полевых наблюдений и вопросов викторин используется локальная база данных SQLite 3.",
        bold_prefix="Почему именно SQLite: "
    )
    add_bullet_p("Не нужен сервер баз данных", "Для классических баз (PostgreSQL или MySQL) нужно ставить тяжелые серверные программы, настраивать порты и пароли. На обычных ПК в школах это делать неудобно и часто запрещено политиками безопасности.")
    add_bullet_p("Вся база в одном файле", "Все 19 подробных паспортов редких видов, фенологические календари, 12 интерактивных викторин и полевой дневник хранятся в одном легком файле redbook.db рядом с программой. Проект можно просто скопировать на флешку — и он сразу работает.")
    add_bullet_p("Мгновенная скорость и надежность", "Поскольку база данных встроена прямо в память программы, поиск видов по фильтрам и категориям охраны (I, II, III, IV) происходит менее чем за 1 миллисекунду.")

    # --- РАЗДЕЛ 5 ---
    add_heading_section("5", "Интерактивная карта и ГИС: Leaflet.js и картографические слои")
    add_body_p(
        "Карта — одна из важнейших частей проекта. Она должна быть наглядной, плавной и полностью понятной учащимся.",
        bold_prefix="Как устроена картография: "
    )
    add_bullet_p("Движок Leaflet.js", "Самая популярная и легковесная библиотека для веб-карт (весит всего 40 КБ). Она сохранена прямо в проекте и не зависит от интернета.")
    add_bullet_p("Радиусный сканер (3, 5, 15, 30 км)", "Пользователь кликает на любой лес, деревню или нажимает кнопку города (Минск, Брест, Гродно, Беловежская пуща). Программа рассчитывает сферическое расстояние по формуле гаверсинусов и сразу выводит боковую карточку с животными в этом радиусе.")
    add_bullet_p("Надежные картографические слои (Esri и OSM)", "Мы используем топографический атлас Esri Topo и детальную подложку OpenStreetMap. Они не требуют платных API-ключей, дают красивое отображение рельефа, рек, озер и лесов Беларуси, а также позволяют переключаться на спутниковые снимки местности.")

    # --- РАЗДЕЛ 6 ---
    add_heading_section("6", "ИИ-модуль, викторины и полевой дневник")
    add_bullet_p("ИИ-определитель и гид-натуралист", "Программа умеет определять животных по текстовым описаниям и следам (например, 'крупный рогатый зверь с бородой' -> Зубр, 'след кошачьих без когтей на снегу' -> Рысь). Это работает быстро и локально без платных API.")
    add_bullet_p("Образовательные викторины", "12 иллюстрированных тестов по категориям редкости, биологии и законодательству (статья 16.8 КоАП Республики Беларусь) с автоматическим подсчетом баллов и выдачей ранга юного исследователя.")
    add_bullet_p("Полевой дневник натуралиста (Citizen Science)", "Возможность прямо в экспедиции записать дату, место, вид и заметки, а затем нажать одну кнопку и выгрузить официальный отчет в формате Excel (CSV).")

    # --- ТАБЛИЦА СРАВНЕНИЯ ---
    add_heading_section("7", "Сводная таблица выбранных технологий")
    
    table = doc.add_table(rows=6, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Компонент системы", "Выбранная технология", "Главное практическое преимущество"]
    for i, h_text in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_background(cell, "2D6A4F")
        set_cell_margins(cell, top=140, bottom=140, left=150, right=150)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ("Язык логики", "Python 3.14", "Высокая скорость создания, чистый код, мощная математика"),
        ("Графический UI", "Flet (движок Flutter)", "Работает и на Windows (быстро, 60 FPS), и на смартфонах по Wi-Fi"),
        ("База данных", "SQLite 3 (встроенная)", "Не требует отдельного сервера, переносится файлом на флешке"),
        ("Интерактивная карта", "Leaflet.js + Esri / OSM", "Офлайн-ядро, радиусный поиск 3–30 км, спутниковые слои"),
        ("Полевой экспорт", "CSV (UTF-8 c BOM)", "Отчет открывается в Excel на русском и белорусском языках")
    ]

    for row_idx, row_data in enumerate(data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F8FAFC"
        for col_idx, text in enumerate(row_data):
            cell = table.rows[row_idx].cells[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            r.font.color.rgb = DARK_TEXT

    # Заключение
    add_heading_section("8", "Заключение")
    add_body_p(
        "Предложенный технологический стек ориентирован на реальную жизнь: программа работает автономно, не требует покупки "
        "дорогого оборудования и сторонних серверов, защищена от сбоев интернета и готова к показу преподавателям, учащимся и коммерческим заказчикам."
    )

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Выбор_и_обоснование_технологического_стека.docx"))
    doc.save(output_path)
    print(f"✅ Документ Word успешно создан: {output_path}")

if __name__ == "__main__":
    create_document()
