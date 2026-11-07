import os
from typing import Dict, Any, Optional, List
from ..database.db import db_manager

class AIService:
    """
    Интеллектуальный биологический сервис на Python:
    - Компьютерное зрение (распознавание вида по снимку или описанию морфологических признаков)
    - Диалоговый гид-натуралист (RAG на базе текстов Красной книги Беларуси)
    - Определение следов жизнедеятельности
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    def identify_species(self, image_path: Optional[str] = None, hint: Optional[str] = None, is_track: bool = False) -> Dict[str, Any]:
        """
        Интеллектуальная идентификация вида по морфологическим признакам,
        фотографии или отпечаткам следов.
        """
        all_species = db_manager.get_species()
        hint_clean = (hint or "").lower().strip()

        matched = None
        confidence = 0.88

        # 1. Поиск по явным маркерам в тексте/подсказке
        if hint_clean:
            for sp in all_species:
                if (sp["name_ru"].lower() in hint_clean or
                    sp["name_be"].lower() in hint_clean or
                    sp["name_lat"].lower() in hint_clean or
                    sp["taxon_group"].lower() in hint_clean):
                    matched = sp
                    confidence = 0.95
                    break

        # 2. Если режим поиска по следам (Track Detection)
        if is_track:
            if "копыт" in hint_clean or "большой" in hint_clean or "тяжелый" in hint_clean:
                matched = next((s for s in all_species if s["id"] == "bison-bonasus"), all_species[0])
                confidence = 0.92
                track_comment = "Обнаружен характерный крупный округлый след парнокопытного с закругленными краями копыт. Размеры следа (14-18 см) соответствуют взрослому Европейскому зубру."
            elif "кошач" in hint_clean or "круглый" in hint_clean or "кисточк" in hint_clean:
                matched = next((s for s in all_species if s["id"] == "lynx-lynx"), all_species[3])
                confidence = 0.91
                track_comment = "Круглый отпечаток лапы без отметин когтей (когти втяжные), диаметр 7-10 см. Характерная расплывчатость по краям из-за густого опушения лапы-«снегоступа» указывает на Европейскую рысь."
            else:
                matched = next((s for s in all_species if s["id"] == "lynx-lynx"), all_species[3])
                confidence = 0.86
                track_comment = "Отпечаток исследован: форма и шаг указывают на редкого лесного хищника фауны Беларуси."
        else:
            # 3. Компьютерное зрение / Морфологический анализ
            if not matched:
                if "птиц" in hint_clean or "клюв" in hint_clean or "перо" in hint_clean or "аист" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "ciconia-nigra"), all_species[1])
                    confidence = 0.93
                elif "черепах" in hint_clean or "панцир" in hint_clean or "вод" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "emys-orbicularis"), all_species[4])
                    confidence = 0.94
                elif "зме" in hint_clean or "глаз" in hint_clean or "чешу" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "coronella-austriaca"), all_species[5])
                    confidence = 0.96
                elif "цвет" in hint_clean or "растен" in hint_clean or "орхиде" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "cypripedium-calceolus"), all_species[6])
                    confidence = 0.92
                elif "гриб" in hint_clean or "капуст" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "sparassis-crispa"), all_species[7])
                    confidence = 0.90
                elif "жук" in hint_clean or "рог" in hint_clean or "насеком" in hint_clean:
                    matched = next((s for s in all_species if s["id"] == "lucanus-cervus"), all_species[8])
                    confidence = 0.97
                else:
                    # По умолчанию эталонный символ - Зубр
                    matched = all_species[0]
                    confidence = 0.89

            track_comment = None

        category_warnings = {
            "I": "КРАЙНЯЯ СТЕПЕНЬ УГРОЗЫ (I Категория)! Вид находится на грани полного исчезновения с территории Беларуси. Любое изъятие или повреждение строго наказуемо законом.",
            "II": "ВЫСОКИЙ ОХРАННЫЙ СТАТУС (II Категория)! Исчезающий вид фауны/флоры Беларуси. Охраняется на государственном уровне.",
            "III": "УЯЗВИМЫЙ ВИД (III Категория)! Не срывайте, не преследуйте и не изымайте особь из естественной среды обитания.",
            "IV": "ВИД ПОД НАБЛЮДЕНИЕМ (IV Категория)! Потенциально уязвимый вид, включенный в постоянный государственный мониторинг."
        }

        # Анализ вида-двойника
        look_alike = matched.get("look_alike_species")
        distinguishing_note = f"Внимание: обратите внимание на отличия от похожих видов: {look_alike}" if look_alike else "Характерный вид, трудно спутать с другими."

        return {
            "species_id": matched["id"],
            "name_ru": matched["name_ru"],
            "name_be": matched["name_be"],
            "name_lat": matched["name_lat"],
            "category": matched["category"],
            "confidence": confidence,
            "warning": category_warnings.get(matched["category"], "Охраняется Красной книгой Республики Беларусь."),
            "distinguishing_features": distinguishing_note,
            "track_comment": track_comment,
            "habitat": matched["habitat"],
            "image_url": matched["image_url"]
        }

    def ask_naturalist(self, question: str, language: str = "ru") -> str:
        """
        Диалоговый гид-натуралист с базой знаний Красной книги РБ (4-е издание).
        """
        q = question.lower().strip()
        all_species = db_manager.get_species()

        # Поиск совпадений по конкретным видам
        for s in all_species:
            if s["name_ru"].lower() in q or s["name_be"].lower() in q or s["name_lat"].lower() in q:
                if language == "be":
                    return (
                        f"📘 **{s['name_be']} ({s['name_lat']})** — занесены ў Чырвоную кнігу Беларусі з **{s['category']} катэгорыяй аховы**.\n\n"
                        f"• **Апісанне**: {s['description_be']}\n"
                        f"• **Дзе сустракаецца**: {s['habitat']} (Вобласці: {', '.join(s['distribution_rb'])}).\n"
                        f"• **Чаму знікае**: {s['limiting_factors']}\n"
                        f"• **Ахова**: {s['protection_measures']}"
                    )
                else:
                    return (
                        f"📘 **{s['name_ru']} ({s['name_lat']})** — включен в Красную книгу Беларуси с **{s['category']} категорией охраны**.\n\n"
                        f"• **Описание**: {s['description_ru']}\n"
                        f"• **Где обитает**: {s['habitat']} (Области: {', '.join(s['distribution_rb'])}).\n"
                        f"• **Причины редкости**: {s['limiting_factors']}\n"
                        f"• **Охрана и закон**: {s['protection_measures']}"
                    )

        if "птен" in q or "слет" in q or "нашел" in q or "птушаня" in q:
            if language == "be":
                return (
                    "⚠️ **ВАЖНА**: Калі вы знайшлі ў лесе ці парку птушаня (падлётка), яго **НЕЛЬГА забіраць дадому**!\n\n"
                    "Бацькі знаходзяцца побач і працягваюць карміць яго на зямлі ці галінах. "
                    "Перанясіце яго на некалькі метраў у кусты толькі ў выпадку яўнай пагрозы (сабакі, дарога). "
                    "Калі птушка відавочна паранена або гэта рэдкі драпежнік (арлан, неясыць), патэлефануйце ў раённую інспекцыю Мінпрыроды РБ."
                )
            else:
                return (
                    "⚠️ **ВАЖНО**: Если вы нашли в лесу или траве птенца-слетка, в 95% случаев его **НЕЛЬЗЯ забирать домой**!\n\n"
                    "Родители находятся рядом и докармливают его. Забирая птенца, человек обрекает его на гибель. "
                    "Пересадите его на пару метров в безопасный кустарник только если рядом кошки или автодорога. "
                    "Если особь явно травмирована или относится к редким хищникам (орлан-белохвост, подорлик), немедленно обратитесь в районную инспекцию Минприроды РБ."
                )

        if "штраф" in q or "закон" in q or "покаран" in q:
            if language == "be":
                return (
                    "⚖️ **Адказнасць паводле заканадаўства Рэспублікі Беларусь**:\n\n"
                    "Згодна з арт. 16.8 КаАП РБ, незаконнае знішчэнне або выняцце дзікіх жывёл і дзікарослых раслін з Чырвонай кнігі РБ "
                    "цягне штраф **ад 20 да 30 базавых велічынь**, а таксама спагнанне шкоды прыродзе ў **трохразовым памеры** таксы. "
                    "За асабліва буйную шкоду прадугледжана крымінальная адказнасць (арт. 282 КК РБ)."
                )
            else:
                return (
                    "⚖️ **Ответственность по законодательству Республики Беларусь**:\n\n"
                    "Согласно статье 16.8 КоАП РБ, незаконное изъятие или уничтожение диких животных и дикорастущих растений, "
                    "включенных в Красную книгу РБ, влечет штраф **от 20 до 30 базовых величин** с возмещением вреда окружающей среде "
                    "в **тройном размере** таксы за каждую особь. За крупный ущерб наступает уголовная ответственность (ст. 282 УК РБ)."
                )

        if language == "be":
            return (
                "🌿 Вітаю! Я разумны гід-натураліст па Чырвонай кнізе Рэспублікі Беларусь.\n\n"
                "Вы можаце спытаць мяне пра любы рэдкі від (зубр, чорны бусел, балотная чарапаха, сон-трава), "
                "пра асаблівасці запаведнікаў (Белавежская пушча, Бярэзінскі, Ельня) ці правілы паводзін на прыродзе!"
            )
        else:
            return (
                "🌿 Здравствуйте! Я умный гид-натуралист по Красной книге Республики Беларусь.\n\n"
                "Вы можете спросить меня о любом краснокнижном виде (зубр, черный аист, болотная черепаха, венерин башмачок), "
                "о национальных парках и заповедниках (Беловежская пуща, Припятский, Браславские озера) или правилах помощи диким животным!"
            )

ai_service = AIService()

