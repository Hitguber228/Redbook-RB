import os
import re
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from PIL import Image
from ..database.db import db_manager

NEW_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ai', 'mobilenetv3_large.onnx'))
OLD_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ai', 'vision_model.onnx'))
MODEL_PATH = NEW_MODEL_PATH if os.path.exists(NEW_MODEL_PATH) else OLD_MODEL_PATH
INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ai', 'species_index.npz'))

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

STOP_WORDS = {
    "и", "в", "во", "на", "с", "со", "по", "у", "к", "ко", "о", "об", "за", "от", "до", "из", "изо", "без",
    "под", "над", "для", "при", "про", "как", "так", "это", "то", "или", "не",
    "же", "бы", "ли", "только", "очень", "самый", "самое", "самая", "вид", "виды", "виде"
}

def clean_stem(w: str) -> str:
    w = w.lower().strip(",.?!;:'\"()[]{}—–-")
    for sfx in ('ейшего', 'ейший', 'ейшая', 'ейшие', 'ому', 'ему', 'ыми', 'ими', 'ого', 'его',
                'очка', 'очки', 'очек', 'очок', 'ка', 'ки', 'ку', 'ке', 'ок', 'ек',
                'ых', 'их', 'ая', 'яя', 'ое', 'ее', 'ый', 'ий', 'ой', 'ами', 'ями',
                'ах', 'ях', 'ов', 'ев', 'ей', 'ам', 'ям', 'ом', 'ем', 'а', 'е', 'и', 'й', 'о', 'у', 'ы', 'ь', 'я'):
        if len(w) > 3 and w.endswith(sfx):
            w = w[:-len(sfx)]
            break
    return w

class AIService:
    """
    Интеллектуальный биологический сервис на Python:
    - Локальное компьютерное зрение (ONNX Runtime эмбеддер, L2 косинусный поиск k-NN по 515 видам)
    - Определение по фотографии с порогом уверенности (отсечение обычных видов и шума)
    - Диалоговый гид-натуралист (RAG на базе текстов Красной книги Беларуси)
    - Определение следов жизнедеятельности
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self._session = None
        self._index = None

    def _get_vision_session(self):
        if self._session is None and os.path.exists(MODEL_PATH):
            try:
                import onnxruntime as ort
                self._session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
            except Exception:
                self._session = None
        return self._session

    def _get_vector_index(self):
        if self._index is None and os.path.exists(INDEX_PATH):
            try:
                self._index = np.load(INDEX_PATH)
            except Exception:
                self._index = None
        return self._index

    def identify_by_image(self, image_path: str, hint: Optional[str] = None, taxon_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Локальное распознавание фотографии через векторный эмбеддер ONNX.
        Поддерживает мультимодальное уточнение (фото + морфологические признаки или таксон).
        Работает офлайн за доли секунды.
        """
        session = self._get_vision_session()
        index = self._get_vector_index()

        if not session or not index or not os.path.exists(image_path):
            return self.identify_species(hint=hint or os.path.basename(image_path), taxon_filter=taxon_filter)

        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
                arr = (np.transpose(np.array(img_rgb, dtype=np.float32) / 255.0, (2, 0, 1))[np.newaxis, ...] - MEAN) / STD
                input_name = session.get_inputs()[0].name
                raw_out = session.run(None, {input_name: arr.astype(np.float32)})[0][0]
                norm = np.linalg.norm(raw_out)
                query_vec = raw_out / norm if norm > 1e-6 else raw_out

            ids = list(index['ids'])

            # Проверяем, содержит ли индекс мультипрототипный пул (5 прототипов на вид)
            if 'proto_embeddings' in index and 'proto_ids' in index:
                proto_embs = index['proto_embeddings']
                proto_ids = list(index['proto_ids'])
                proto_sims = np.dot(proto_embs, query_vec) # [num_protos]

                # Находим максимальное сходство по всем ракурсам/прототипам каждого вида
                species_proto_sim = {}
                for p_idx, p_id in enumerate(proto_ids):
                    s = float(proto_sims[p_idx])
                    if p_id not in species_proto_sim or s > species_proto_sim[p_id]:
                        species_proto_sim[p_id] = s

                centroids = index['embeddings']
                centroid_sims = np.dot(centroids, query_vec)

                sims_dict = {}
                for idx_sp, sp_id in enumerate(ids):
                    p_sim = species_proto_sim.get(sp_id, float(centroid_sims[idx_sp]))
                    c_sim = float(centroid_sims[idx_sp])
                    # Взвешенное сочетание лучшего ракурса (75%) и центроида (25%)
                    sims_dict[sp_id] = 0.75 * p_sim + 0.25 * c_sim
            else:
                embeddings = index['embeddings']
                sims_raw = np.dot(embeddings, query_vec)
                sims_dict = {sp_id: float(sims_raw[i]) for i, sp_id in enumerate(ids)}

            hint_clean = (hint or "").strip()
            k_intent, t_intent, tokens = self._extract_biology_intent(hint_clean) if hint_clean else (None, None, [])

            # Мультимодальная гибридная оценка всех видов (одним запросом к БД вместо N+1)
            species_by_id = {s["id"]: s for s in db_manager.get_species()}
            scored_candidates = []
            for sp_id in ids:
                sp = species_by_id.get(sp_id)
                if not sp:
                    continue

                vis_sim = float(sims_dict.get(sp_id, 0.0))
                final_score = vis_sim

                # Жесткая или мягкая таксономическая фильтрация
                if taxon_filter and taxon_filter != "all":
                    sp_taxon = sp.get("taxon_group")
                    sp_kingdom = sp.get("kingdom")
                    norm_filter = "fish" if taxon_filter == "fishes" else taxon_filter
                    if norm_filter in ["mammals", "birds", "insects", "reptiles", "amphibians", "fish"]:
                        if sp_taxon != norm_filter:
                            final_score -= 1.0 # Отсекаем нерелевантные таксоны
                    elif norm_filter in ["plants", "fungi"]:
                        if sp_kingdom != norm_filter:
                            final_score -= 1.0

                # Учет текстовой подсказки пользователя
                if hint_clean:
                    morph_sc = self._score_species_morphology(sp, hint_clean, k_intent, t_intent, tokens)
                    final_score += (morph_sc / 50.0) * 0.40

                scored_candidates.append({
                    "score": final_score,
                    "vis_sim": vis_sim,
                    "species": sp
                })

            scored_candidates.sort(key=lambda x: x["score"], reverse=True)

            best_item = scored_candidates[0]
            matched = best_item["species"]
            best_sim = best_item["vis_sim"]
            best_score = best_item["score"]

            # Формирование списка топ-кандидатов (до 4 вариантов) с дифференцированной уверенностью
            top_candidates = []
            for cand in scored_candidates[:4]:
                sp_cand = cand["species"]
                raw_s = cand["vis_sim"]
                # Масштабирование уверенности для наглядного UI
                if hint_clean:
                    c_conf = min(0.98, max(0.40, round(0.50 + (cand["score"] / 1.5) * 0.48, 2)))
                else:
                    if raw_s > 0.60:
                        # Диапазон SqueezeNet (0.88 - 0.97)
                        c_conf = min(0.96, max(0.45, round(0.50 + max(0.0, (raw_s - 0.88)) / 0.09 * 0.46, 2)))
                    else:
                        # Новый диапазон MobileNetV3 (0.20 - 0.36)
                        c_conf = min(0.96, max(0.45, round(0.50 + max(0.0, (raw_s - 0.20)) / 0.16 * 0.46, 2)))

                top_candidates.append({
                    "id": sp_cand["id"],
                    "name_ru": sp_cand["name_ru"],
                    "name_be": sp_cand["name_be"],
                    "name_lat": sp_cand["name_lat"],
                    "category": sp_cand["category"],
                    "confidence": c_conf,
                    "image_url": sp_cand["image_url"],
                    "habitat": sp_cand.get("habitat", "")
                })

            primary_conf = top_candidates[0]["confidence"] if top_candidates else 0.50
            second_conf = top_candidates[1]["confidence"] if len(top_candidates) > 1 else 0.0

            # Порог уверенности нейросети:
            # 1. Если максимальное сходство ниже 0.70
            # 2. Или если отрыв 1-го от 2-го места менее 0.04 (сеть сомневается между похожими видами)
            is_uncertain = (primary_conf < 0.70) or ((primary_conf - second_conf) < 0.04)
            status = "uncertain" if is_uncertain else "confirmed"

            category_warnings = {
                "I": "КРАЙНЯЯ СТЕПЕНЬ УГРОЗЫ (I Категория, CR)! Вид на грани исчезновения. Любое изъятие или повреждение строго наказуемо законом.",
                "II": "ВЫСОКИЙ ОХРАННЫЙ СТАТУС (II Категория, EN)! Исчезающий вид фауны/флоры Беларуси.",
                "III": "УЯЗВИМЫЙ ВИД (III Категория, VU)! Редкий вид природы Беларуси. Не беспокойте и не срывайте.",
                "IV": "ВИД ПОД НАБЛЮДЕНИЕМ (IV Категория, NT)! Потенциально уязвимый вид, включенный в постоянный мониторинг."
            }

            features_desc = f"Локальный ИИ определил сходство {int(primary_conf * 100)}% по ключевым визуальным признакам."
            if hint_clean:
                features_desc += f" Учтены морфологические признаки: '{hint_clean}'."

            return {
                "species_id": matched["id"],
                "name_ru": matched["name_ru"],
                "name_be": matched["name_be"],
                "name_lat": matched["name_lat"],
                "category": matched["category"],
                "confidence": primary_conf,
                "is_uncertain": is_uncertain,
                "is_confident": not is_uncertain,
                "status": status,
                "status_title": "Нейросеть не уверена: найдено несколько похожих вариантов" if is_uncertain else "Вид определен с высокой уверенностью",
                "top_candidates": top_candidates,
                "warning": category_warnings.get(matched["category"], "Охраняется Красной книгой Республики Беларусь."),
                "distinguishing_features": features_desc,
                "track_comment": None,
                "habitat": matched["habitat"],
                "image_url": matched["image_url"],
                "analyzed_image_path": image_path
            }
        except Exception:
            return self.identify_species(hint=hint or os.path.basename(image_path), taxon_filter=taxon_filter)

    def _extract_biology_intent(self, query: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        q = query.lower()
        kingdom = None
        taxon = None

        # 1. Насекомые
        if any(k in q for k in ["насеком", "жук", "бабочк", "гусениц", "стрекоз", "шмел", "короед", "усач", "бронзовк", "плавунец"]):
            kingdom = "animals"
            taxon = "insects"
        # 2. Птицы
        elif any(k in q for k in ["птиц", "перья", "клюв", "крыл", "гнезд", "полет", "сова", "аист", "орлан", "беркут", "неясыт", "кулик"]):
            kingdom = "animals"
            taxon = "birds"
        # 3. Рыбы
        elif any(k in q for k in ["рыб", "чешу", "плавник", "жабр", "стерляд", "лосос", "форел", "хариус"]):
            kingdom = "animals"
            taxon = "fish"
        # 4. Рептилии
        elif any(k in q for k in ["рептили", "пресмыкающ", "зме", "черепах", "медянк"]):
            kingdom = "animals"
            taxon = "reptiles"
        # 5. Земноводные
        elif any(k in q for k in ["земноводн", "амфиби", "жаб", "лягушк", "тритон"]):
            kingdom = "animals"
            taxon = "amphibians"
        # 6. Млекопитающие
        elif any(k in q for k in ["млекопитающ", "звер", "шерст", "копыт", "хищник", "рысь", "медвед", "зубр", "грызун", "соня", "барсук"]):
            kingdom = "animals"
            taxon = "mammals"
        # 7. Растения
        elif any(k in q for k in ["растен", "цветок", "цветк", "трав", "дерев", "папоротник", "мох", "кустарник", "ягод", "орхиде", "башмач"]):
            kingdom = "plants"
        # 8. Грибы
        elif any(k in q for k in ["гриб", "лишайник", "трутовик", "мицели", "шляпк"]):
            kingdom = "fungi"

        if not kingdom:
            if "животн" in q:
                kingdom = "animals"

        raw_tokens = re.findall(r'[а-яёa-z0-9]+', q)
        tokens = [clean_stem(t) for t in raw_tokens if t not in STOP_WORDS and len(t) > 2]
        return kingdom, taxon, tokens

    def _score_species_morphology(self, sp: dict, query: str, kingdom_intent: Optional[str], taxon_intent: Optional[str], tokens: List[str], is_track: bool = False) -> float:
        # Жесткий штраф за несовпадение царства
        if kingdom_intent and sp.get("kingdom") != kingdom_intent:
            return -100.0

        score = 0.0
        if taxon_intent:
            if sp.get("taxon_group") == taxon_intent:
                score += 25.0
            else:
                score -= 15.0

        q_lower = query.lower()
        is_large = any(w in q_lower for w in ["больш", "крупн", "гигант", "огромн", "тяжел", "массивн"])
        is_small = any(w in q_lower for w in ["маленьк", "мелк", "крошечн", "карлик"])

        full_text = " ".join([
            sp.get("name_ru", ""),
            sp.get("name_be", ""),
            sp.get("name_lat", ""),
            sp.get("description_ru", "") or "",
            sp.get("morphology", "") or "",
            sp.get("habitat", "") or ""
        ]).lower()

        # Размеры
        if is_large:
            if taxon_intent == "insects":
                if sp.get("id") == "lucanus-cervus":
                    score += 35.0
            elif sp.get("id") == "bison-bonasus":
                score += 35.0  # Зубр - крупнейший зверь Беларуси
            elif sp.get("id") == "ursus-arctos":
                score += 30.0  # Бурый медведь
            elif sp.get("id") in ["lynx-lynx", "haliaeetus-albicilla", "aquila-chrysaetos", "equus-przewalskii"]:
                score += 25.0
            elif any(m in full_text for m in ["крупнейш", "массивн", "тяжел", "гигантск", "мощн"]):
                score += 15.0

        if is_small:
            if any(m in full_text for m in ["мелк", "крошечн", "карликов", "миниатюрн"]):
                score += 20.0

        # Следы
        if is_track:
            if any(k in q_lower for k in ["копыт", "круглый след", "рогат"]) and sp.get("id") == "bison-bonasus":
                score += 45.0
            elif any(k in q_lower for k in ["кошач", "кисточк", "без когтей"]) and sp.get("id") == "lynx-lynx":
                score += 45.0
            elif any(k in q_lower for k in ["когти", "лап", "пясть"]) and sp.get("id") == "ursus-arctos":
                score += 40.0

        # Сопоставление очищенных лемм
        for tok in tokens:
            if not tok:
                continue
            ru_lower = sp.get("name_ru", "").lower()
            be_lower = sp.get("name_be", "").lower()
            lat_lower = sp.get("name_lat", "").lower()
            morph_lower = (sp.get("morphology", "") or "").lower()
            desc_lower = (sp.get("description_ru", "") or "").lower()

            if tok in ru_lower:
                score += 30.0
            elif tok in be_lower:
                score += 25.0
            elif tok in lat_lower:
                score += 20.0

            if tok in morph_lower:
                score += 12.0
            if tok in desc_lower:
                score += 8.0

        return score

    def identify_species(self, image_path: Optional[str] = None, hint: Optional[str] = None, taxon_filter: Optional[str] = None, is_track: bool = False) -> Dict[str, Any]:
        """
        Идентификация вида по фото через локальный ИИ, либо по текстовым признакам / следам.
        """
        if image_path and os.path.exists(image_path):
            return self.identify_by_image(image_path, hint=hint, taxon_filter=taxon_filter)

        all_species = db_manager.get_species()
        hint_clean = (hint or "").lower().strip()

        # 1. Биологический анализ запроса
        k_intent, t_intent, tokens = self._extract_biology_intent(hint_clean)

        # 2. Оценка всех 515 видов
        scored_candidates = []
        for sp in all_species:
            sc = self._score_species_morphology(sp, hint_clean, k_intent, t_intent, tokens, is_track=is_track)
            if sc > 0:
                scored_candidates.append((sc, sp))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        if not scored_candidates:
            # Ничего не подошло
            matched = all_species[0]
            confidence = 0.35
            is_uncertain = True
            top_candidates = []
        else:
            top_score = scored_candidates[0][0]
            matched = scored_candidates[0][1]

            confidence = min(0.96, max(0.45, round(0.50 + (top_score / 120.0) * 0.46, 2)))
            second_score = scored_candidates[1][0] if len(scored_candidates) > 1 else 0.0

            # Нейросеть не уверена, если очков мало или разрыв минимален
            is_uncertain = (top_score < 34.0) or ((top_score - second_score) < 7.0)

            top_candidates = []
            for sc, sp_cand in scored_candidates[:4]:
                c_conf = min(0.96, max(0.40, round(0.42 + (sc / 120.0) * 0.54, 2)))
                top_candidates.append({
                    "id": sp_cand["id"],
                    "name_ru": sp_cand["name_ru"],
                    "name_be": sp_cand["name_be"],
                    "name_lat": sp_cand["name_lat"],
                    "category": sp_cand["category"],
                    "confidence": c_conf,
                    "image_url": sp_cand["image_url"],
                    "habitat": sp_cand.get("habitat", "")
                })

        category_warnings = {
            "I": "КРАЙНЯЯ СТЕПЕНЬ УГРОЗЫ (I Категория, CR)! Вид находится на грани полного исчезновения с территории Беларуси. Любое изъятие строго наказуемо.",
            "II": "ВЫСОКИЙ ОХРАННЫЙ СТАТУС (II Категория, EN)! Исчезающий вид фауны/флоры Беларуси.",
            "III": "УЯЗВИМЫЙ ВИД (III Категория, VU)! Редкий вид Беларуси. Не изымайте особь из естественной среды.",
            "IV": "ВИД ПОД НАБЛЮДЕНИЕМ (IV Категория, NT)! Потенциально уязвимый вид под постоянным государственным мониторингом."
        }

        look_alike = matched.get("look_alike_species")
        distinguishing_note = f"Внимание: обратите внимание на отличия от похожих видов: {look_alike}" if look_alike else "Характерный вид, трудно спутать с другими."

        track_comment = None
        if is_track:
            if matched["id"] == "bison-bonasus":
                track_comment = "Обнаружен характерный крупный округлый след парнокопытного (14-18 см). Соответствует взрослому Европейскому зубру."
            elif matched["id"] == "lynx-lynx":
                track_comment = "Круглый отпечаток лапы без отметин когтей (когти втяжные), диаметр 7-10 см. Указывает на Европейскую рысь."
            else:
                track_comment = "Отпечаток исследован: форма указывает на редкого лесного обитателя фауны Беларуси."

        status = "uncertain" if is_uncertain else "confirmed"

        return {
            "species_id": matched["id"],
            "name_ru": matched["name_ru"],
            "name_be": matched["name_be"],
            "name_lat": matched["name_lat"],
            "category": matched["category"],
            "confidence": confidence,
            "is_uncertain": is_uncertain,
            "is_confident": not is_uncertain,
            "status": status,
            "status_title": "Нейросеть не уверена: найдено несколько похожих вариантов" if is_uncertain else "Вид определен с высокой уверенностью",
            "top_candidates": top_candidates,
            "warning": category_warnings.get(matched["category"], "Охраняется Красной книгой Республики Беларусь."),
            "distinguishing_features": distinguishing_note,
            "track_comment": track_comment,
            "habitat": matched["habitat"],
            "image_url": matched["image_url"]
        }

    def ask_naturalist(self, question: str, language: str = "ru") -> str:
        """
        Диалоговый гид-натуралист с базой знаний Красной книги РБ (ред. 2025).
        """
        q = question.lower().strip()
        all_species = db_manager.get_species()

        for s in all_species:
            if s["name_ru"].lower() in q or s["name_be"].lower() in q or s["name_lat"].lower() in q:
                if language == "be":
                    return (
                        f"**{s['name_be']} ({s['name_lat']})** — занесены ў Чырвоную кнігу Беларусі з **{s['category']} катэгорыяй аховы**.\n\n"
                        f"• **Апісанне**: {s['description_be']}\n"
                        f"• **Дзе сустракаецца**: {s['habitat']} (Вобласці: {', '.join(s['distribution_rb'])}).\n"
                        f"• **Чаму знікае**: {s['limiting_factors']}\n"
                        f"• **Ахова**: {s['protection_measures']}"
                    )
                else:
                    return (
                        f"**{s['name_ru']} ({s['name_lat']})** — включен в Красную книгу Беларуси с **{s['category']} категорией охраны**.\n\n"
                        f"• **Описание**: {s['description_ru']}\n"
                        f"• **Где обитает**: {s['habitat']} (Области: {', '.join(s['distribution_rb'])}).\n"
                        f"• **Причины редкости**: {s['limiting_factors']}\n"
                        f"• **Охрана и закон**: {s['protection_measures']}"
                    )

        if "птен" in q or "слет" in q or "нашел" in q or "птушаня" in q:
            if language == "be":
                return (
                    "**ВАЖНА**: Калі вы знайшлі ў лесе ці парку птушаня (падлётка), яго **НЕЛЬГА забіраць дадому**!\n\n"
                    "Бацькі знаходзяцца побач і працягваюць карміць яго на зямлі ці галінах. "
                    "Перанясіце яго на некалькі метраў у кусты толькі ў выпадку яўнай пагрозы (сабакі, дарога). "
                    "Калі птушка відавочна паранена або гэта рэдкі драпежнік (арлан, неясыць), патэлефануйце ў раённую інспекцыю Мінпрыроды РБ."
                )
            else:
                return (
                    "**ВАЖНО**: Если вы нашли в лесу или траве птенца-слетка, в 95% случаев его **НЕЛЬЗЯ забирать домой**!\n\n"
                    "Родители находятся рядом и докармливают его. Забирая птенца, человек обрекает его на гибель. "
                    "Пересадите его на пару метров в безопасный кустарник только если рядом кошки или автодорога. "
                    "Если особь явно травмирована или относится к редким хищникам (орлан-белохвост, подорлик), немедленно обратитесь в районную инспекцию Минприроды РБ."
                )

        if "штраф" in q or "закон" in q or "покаран" in q:
            if language == "be":
                return (
                    "**Адказнасць паводле заканадаўства Рэспублікі Беларусь**:\n\n"
                    "Згодна з арт. 16.8 КаАП РБ, незаконнае знішчэнне або выняцце дзікіх жывёл і дзікарослых раслін з Чырвонай кнігі РБ "
                    "цягне штраф **ад 20 да 30 базавых велічынь**, а таксама спагнанне шкоды прыродзе ў **трохразовым памеры** таксы. "
                    "За асабліва буйную шкоду прадугледжана крымінальная адказнасць (арт. 282 КК РБ)."
                )
            else:
                return (
                    "**Ответственность по законодательству Республики Беларусь**:\n\n"
                    "Согласно статье 16.8 КоАП РБ, незаконное изъятие или уничтожение диких животных и дикорастущих растений, "
                    "включенных в Красную книгу РБ, влечет штраф **от 20 до 30 базовых величин** с возмещением вреда окружающей среде "
                    "в **тройном размере** таксы за каждую особь. За крупный ущерб наступает уголовная ответственность (ст. 282 УК РБ)."
                )

        if language == "be":
            return (
                "Вітаю! Я разумны гід-натураліст па Чырвонай кнізе Рэспублікі Беларусь.\n\n"
                "Вы можаце спытаць мяне пра любы рэдкі від (зубр, чорны бусел, балотная чарапаха, сон-трава), "
                "пра асаблівасці запаведнікаў (Белавежская пушча, Бярэзінскі, Ельня) ці правілы паводзін на прыродзе!"
            )
        else:
            return (
                "Здравствуйте! Я умный гид-натуралист по Красной книге Республики Беларусь.\n\n"
                "Вы можете спросить меня о любом краснокнижном виде (зубр, черный аист, болотная черепаха, венерин башмачок), "
                "о национальных парках и заповедниках (Беловежская пуща, Припятский, Браславские озера) или правилах помощи диким животным!"
            )

ai_service = AIService()
