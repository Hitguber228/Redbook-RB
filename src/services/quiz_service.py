import os
import random
from typing import List, Dict, Any, Optional
from ..database.db import db_manager

RECOGNIZABLE_PHOTO_GROUPS = {
    "mammals", "birds", "reptiles", "amphibians",
    "fish", "vascular_plants", "mushrooms", "insects"
}


class QuizService:
    def __init__(self):
        self.current_score = 0
        self.total_answered = 0
        self.current_streak = 0
        self.max_streak = 0
        self.active_category = "tournament"
        self.session_quizzes: List[Dict[str, Any]] = []
        self._valid_photo_species_cache: Optional[List[Dict[str, Any]]] = None

    def get_categories(self, language: str = "ru") -> List[Dict[str, Any]]:
        is_ru = (language == "ru")
        return [
            {
                "id": "tournament",
                "title": "Большой эко-турнир" if is_ru else "Вялікі эка-турнір",
                "subtitle": "Смешанный олимпиадный режим" if is_ru else "Змешаны алімпіядны рэжым",
                "description": (
                    "Случайный микс из всех разделов Красной книги: фото-загадки, редкие звери и растения, следы, голоса и законы."
                    if is_ru else
                    "Выпадковы мікс з усіх раздзелаў Чырвонай кнігі: фота-загадкі, рэдкія звяры і расліны, сляды, галасы і законы."
                ),
                "icon": "MILITARY_TECH",
                "badge": "10 вопросов • Все форматы" if is_ru else "10 пытанняў • Усе фарматы"
            },
            {
                "id": "photo",
                "title": "Фото-определитель" if is_ru else "Фота-азначнік",
                "subtitle": "Узнай вид по фото" if is_ru else "Пазнай від па фота",
                "description": (
                    "Определяйте редких зверей, птиц, насекомых, грибы и растения Беларуси по реальным фотографиям."
                    if is_ru else
                    "Вызначайце рэдкіх звяроў, птушак, насякомых, грыбы і расліны Беларусі па рэальных фатаграфіях."
                ),
                "icon": "PHOTO_CAMERA",
                "badge": "Визуальный тест" if is_ru else "Візуальны тэст"
            },
            {
                "id": "animals",
                "title": "Звери и птицы" if is_ru else "Звяры і птушкі",
                "subtitle": "Фауна Беларуси" if is_ru else "Фаўна Беларусі",
                "description": "Млекопитающие и пернатые: рацион, повадки, сезонные миграции и зимовки." if is_ru else "Млекакормячыя і птушкі: рацыён, паводзіны і зімоўка.",
                "icon": "PETS",
                "badge": "Млекопитающие и птицы" if is_ru else "Звяры і птушкі"
            },
            {
                "id": "plants",
                "title": "Растения и грибы" if is_ru else "Расліны і грыбы",
                "subtitle": "Флора и микобиота" if is_ru else "Флора і мікабіёта",
                "description": "Дикорастущие лесные орхидеи, первоцветы, реликтовые деревья и грибы." if is_ru else "Дзікарослыя архідэі, першацветы, рэліктавыя дрэвы і грыбы.",
                "icon": "LOCAL_FLORIST",
                "badge": "Флора и грибы" if is_ru else "Флора і грыбы"
            },
            {
                "id": "tracks",
                "title": "Следопыт и биотопы" if is_ru else "Следапыт і біятопы",
                "subtitle": "Полевые признаки" if is_ru else "Палявыя прыкметы",
                "description": "Отпечатки лап и копыт, формы нор, погрызы, жилища и лесные биотопы." if is_ru else "Адбіткі лап і капытоў, формы нор, жыллё і лясныя біятопы.",
                "icon": "EXPLORE",
                "badge": "Следы и биотопы" if is_ru else "Сляды і біятопы"
            },
            {
                "id": "voice",
                "title": "Голоса природы" if is_ru else "Галасы прыроды",
                "subtitle": "Аудио-определитель" if is_ru else "Аўдыё-азначнік",
                "description": "Узнавание редких птиц и зверей по брачным песням, крикам и эхолокации." if is_ru else "Пазнаванне птушак і звяроў па спевах, крыках і рэхалакацыі.",
                "icon": "VOLUME_UP",
                "badge": "Аудио-вопросы" if is_ru else "Аўдыё-пытанні"
            },
            {
                "id": "law",
                "title": "Охрана и законы" if is_ru else "Ахова і законы",
                "subtitle": "Заповедное дело" if is_ru else "Запаведная справа",
                "description": "Охранные категории I–IV, заповедники Беларуси и ответственность по ст. 16.8 КоАП." if is_ru else "Ахоўныя катэгорыі I–IV, запаведнікі Беларусі і арт. 16.8 КаАП.",
                "icon": "SHIELD",
                "badge": "Законы и категории" if is_ru else "Законы і катэгорыі"
            }
        ]

    @staticmethod
    def _first_sentence(text: str, max_len: int = 180) -> str:
        if not text:
            return ""
        clean = " ".join(text.strip().split())
        if len(clean) <= max_len:
            return clean
        dot_idx = clean.find(".", 40, max_len)
        if dot_idx != -1:
            return clean[:dot_idx + 1]
        return clean[:max_len].rstrip(" ,;:") + "..."

    @staticmethod
    def _photo_prompt_for_species(sp: Dict[str, Any]) -> tuple[str, str]:
        group = sp.get("taxon_group", "")
        kingdom = sp.get("kingdom", "animals")
        if group == "birds":
            return (
                "Какая редкая птица из Красной книги Беларуси изображена на фотографии?",
                "Якая рэдкая птушка з Чырвонай кнігі Беларусі выяўлена на фатаграфіі?"
            )
        if group == "insects":
            return (
                "Какое редкое насекомое из Красной книги Беларуси изображено на фотографии?",
                "Якое рэдкае насякомае з Чырвонай кнігі Беларусі выяўлена на фатаграфіі?"
            )
        if group == "fish":
            return (
                "Какая редкая рыба из Красной книги Беларуси изображена на фотографии?",
                "Якая рэдкая рыба з Чырвонай кнігі Беларусі выяўлена на фатаграфіі?"
            )
        if group == "mushrooms":
            return (
                "Какой редкий гриб из Красной книги Беларуси изображен на фотографии?",
                "Які рэдкі грыб з Чырвонай кнігі Беларусі выяўлены на фатаграфіі?"
            )
        if kingdom == "plants":
            return (
                "Какое редкое растение из Красной книги Беларуси изображено на фотографии?",
                "Якая рэдкая расліна з Чырвонай кнігі Беларусі выяўлена на фатаграфіі?"
            )
        return (
            "Какое редкое животное из Красной книги Беларуси изображено на фотографии?",
            "Якая рэдкая жывёла з Чырвонай кнігі Беларусі выяўлена на фатаграфіі?"
        )

    def _get_valid_photo_species(self) -> List[Dict[str, Any]]:
        if self._valid_photo_species_cache is None:
            all_species = db_manager.get_species()
            assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
            self._valid_photo_species_cache = [
                s for s in all_species
                if s.get("image_url")
                and os.path.exists(os.path.join(assets_root, s["image_url"].lstrip("/")))
            ]
        return self._valid_photo_species_cache

    def _generate_photo_quizzes(self, count: int = 10) -> List[Dict[str, Any]]:
        valid_species = self._get_valid_photo_species()
        if len(valid_species) < 4:
            return []

        pool = [s for s in valid_species if s.get("taxon_group") in RECOGNIZABLE_PHOTO_GROUPS]
        if len(pool) < count:
            pool = valid_species

        by_group: Dict[str, List[Dict[str, Any]]] = {}
        by_kingdom: Dict[str, List[Dict[str, Any]]] = {}
        for s in valid_species:
            by_group.setdefault(s.get("taxon_group", "other"), []).append(s)
            by_kingdom.setdefault(s.get("kingdom", "animals"), []).append(s)

        featured = [s for s in pool if s.get("is_featured")]
        regular = [s for s in pool if not s.get("is_featured")]
        random.shuffle(featured)
        random.shuffle(regular)

        # Баланс: до половины вопросов — знаковые виды, остальные — случайные из базы
        featured_quota = min(len(featured), max(1, count // 2))
        targets = featured[:featured_quota] + regular[:max(0, count - featured_quota)]
        if len(targets) < count:
            used_ids = {s["id"] for s in targets}
            rest = [s for s in pool if s["id"] not in used_ids]
            random.shuffle(rest)
            targets.extend(rest[:count - len(targets)])
        random.shuffle(targets)

        generated: List[Dict[str, Any]] = []
        for idx, sp in enumerate(targets[:count], start=1):
            group_candidates = [
                c for c in by_group.get(sp.get("taxon_group", "other"), [])
                if c["id"] != sp["id"] and c["name_ru"] != sp["name_ru"]
            ]
            if len(group_candidates) < 3:
                kingdom_candidates = [
                    c for c in by_kingdom.get(sp.get("kingdom", "animals"), [])
                    if c["id"] != sp["id"] and c["name_ru"] != sp["name_ru"]
                    and c["id"] not in {g["id"] for g in group_candidates}
                ]
                random.shuffle(kingdom_candidates)
                group_candidates.extend(kingdom_candidates)

            if len(group_candidates) < 3:
                fallback = [
                    c for c in valid_species
                    if c["id"] != sp["id"] and c["name_ru"] != sp["name_ru"]
                    and c["id"] not in {g["id"] for g in group_candidates}
                ]
                random.shuffle(fallback)
                group_candidates.extend(fallback)

            if len(group_candidates) < 3:
                continue

            distractors = random.sample(group_candidates, 3)
            q_ru, q_be = self._photo_prompt_for_species(sp)

            short_ru = self._first_sentence(sp.get("description_ru", ""))
            short_be = self._first_sentence(sp.get("description_be", "")) or short_ru

            exp_ru = f"На фотографии: {sp['name_ru']} ({sp['name_lat']}), {sp['category']} категория охраны."
            if short_ru:
                exp_ru += f" {short_ru}"

            exp_be = f"На фатаграфіі: {sp['name_be']} ({sp['name_lat']}), {sp['category']} катэгорыя аховы."
            if short_be:
                exp_be += f" {short_be}"

            generated.append({
                "id": -idx,
                "quiz_type": "photo",
                "question_ru": q_ru,
                "question_be": q_be,
                "options_ru": [sp["name_ru"]] + [d["name_ru"] for d in distractors],
                "options_be": [sp["name_be"]] + [d["name_be"] for d in distractors],
                "correct_index": 0,
                "explanation_ru": exp_ru,
                "explanation_be": exp_be,
                "media_url": sp["image_url"],
                "related_species_id": sp["id"],
            })

        return generated

    def start_session(self, category_id: str = "tournament", limit: int = 10) -> List[Dict[str, Any]]:
        self.current_score = 0
        self.total_answered = 0
        self.current_streak = 0
        self.max_streak = 0
        self.active_category = category_id

        if category_id == "photo":
            selected = self._generate_photo_quizzes(limit)
        elif category_id == "tournament":
            photo_count = min(3, max(1, limit // 3))
            photo_q = self._generate_photo_quizzes(photo_count)
            text_q = list(db_manager.get_quizzes())
            random.shuffle(text_q)
            selected = photo_q + text_q[:max(0, limit - len(photo_q))]
            random.shuffle(selected)
        else:
            all_q = db_manager.get_quizzes(category_id)
            shuffled = list(all_q)
            random.shuffle(shuffled)
            selected = shuffled[:limit]

        # Динамическое перемешивание вариантов ответов (A, B, C, D) для каждого запуска
        session_list = []
        for q in selected:
            q_copy = dict(q)
            opts_ru = list(q["options_ru"])
            opts_be = list(q["options_be"])
            corr_idx = q["correct_index"]

            paired = []
            for i in range(len(opts_ru)):
                ru_val = opts_ru[i]
                be_val = opts_be[i] if i < len(opts_be) else ru_val
                paired.append((ru_val, be_val, (i == corr_idx)))

            random.shuffle(paired)
            q_copy["options_ru"] = [p[0] for p in paired]
            q_copy["options_be"] = [p[1] for p in paired]
            q_copy["correct_index"] = next((i for i, p in enumerate(paired) if p[2]), 0)
            session_list.append(q_copy)

        self.session_quizzes = session_list
        return self.session_quizzes

    def get_all_quizzes(self, quiz_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return db_manager.get_quizzes(quiz_type)

    def check_answer(self, quiz_id: int, selected_index: int, language: str = "ru") -> Dict[str, Any]:
        target = next((q for q in self.session_quizzes if q["id"] == quiz_id), None)
        if not target:
            quizzes = db_manager.get_quizzes()
            target = next((q for q in quizzes if q["id"] == quiz_id), None)

        if not target:
            return {"is_correct": False, "explanation": "Вопрос не найден"}

        is_correct = (selected_index == target["correct_index"])
        self.total_answered += 1
        if is_correct:
            self.current_score += 1
            self.current_streak += 1
            if self.current_streak > self.max_streak:
                self.max_streak = self.current_streak
        else:
            self.current_streak = 0

        explanation = target["explanation_be"] if language == "be" else target["explanation_ru"]

        return {
            "is_correct": is_correct,
            "correct_index": target["correct_index"],
            "explanation": explanation,
            "current_score": self.current_score,
            "total_answered": self.total_answered,
            "streak": self.current_streak,
            "related_species_id": target.get("related_species_id")
        }

    def reset_score(self):
        self.current_score = 0
        self.total_answered = 0
        self.current_streak = 0
        self.max_streak = 0

    def get_certificate_data(self, user_name: str, total_count: Optional[int] = None, language: str = "ru") -> Dict[str, Any]:
        score = self.current_score
        total = total_count if total_count is not None else max(self.total_answered, 1)
        total = max(total, 1)
        percentage = int((score / total) * 100)

        if percentage >= 90:
            rank_ru = "Эксперт заповедного дела Беларуси (I степень)"
            rank_be = "Эксперт запаведнай справы Беларусі (I ступень)"
            badge_title = "Высшая академическая степень" if language == "ru" else "Найвышэйшая акадэмічная ступень"
        elif percentage >= 70:
            rank_ru = "Хранитель природы Беларуси (II степень)"
            rank_be = "Захавальнік прыроды Беларусі (II ступень)"
            badge_title = "Отличные знания экологии" if language == "ru" else "Выдатныя веды экалогіі"
        elif percentage >= 50:
            rank_ru = "Полевой натуралист Беларуси (III степень)"
            rank_be = "Палявы натураліст Беларусі (III ступень)"
            badge_title = "Базовый квалификационный уровень" if language == "ru" else "Базавы кваліфікацыйны ўзровень"
        else:
            rank_ru = "Юный исследователь природы Беларуси"
            rank_be = "Юны даследчык прыроды Беларусі"
            badge_title = "Сертификат участника" if language == "ru" else "Сертыфікат удзельніка"

        name_display = user_name.strip() if user_name and user_name.strip() else ("Учащийся" if language == "ru" else "Вучань")

        return {
            "user_name": name_display,
            "score": f"{score} из {total}" if language == "ru" else f"{score} з {total}",
            "percentage": f"{percentage}%",
            "rank": rank_be if language == "be" else rank_ru,
            "badge_title": badge_title,
            "streak": self.max_streak,
            "correct_count": score,
            "total_count": total
        }

quiz_service = QuizService()
