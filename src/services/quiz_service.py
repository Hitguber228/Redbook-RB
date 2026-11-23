import random
from typing import List, Dict, Any, Optional
from ..database.db import db_manager

class QuizService:
    def __init__(self):
        self.current_score = 0
        self.total_answered = 0
        self.current_streak = 0
        self.max_streak = 0
        self.active_category = "tournament"
        self.session_quizzes: List[Dict[str, Any]] = []

    def get_categories(self, language: str = "ru") -> List[Dict[str, Any]]:
        is_ru = (language == "ru")
        return [
            {
                "id": "tournament",
                "title": "Большой эко-турнир" if is_ru else "Вялікі эка-турнір",
                "subtitle": "Все разделы" if is_ru else "Усе раздзелы",
                "description": "Случайный олимпиадный тест по всем разделам Красной книги Беларуси." if is_ru else "Выпадковы тэст па ўсіх раздзелах Чырвонай кнігі Беларусі.",
                "icon": "MILITARY_TECH",
                "badge": "10 вопросов" if is_ru else "10 пытанняў"
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

    def start_session(self, category_id: str = "tournament", limit: int = 10) -> List[Dict[str, Any]]:
        self.current_score = 0
        self.total_answered = 0
        self.current_streak = 0
        self.max_streak = 0
        self.active_category = category_id

        if category_id == "tournament":
            all_q = db_manager.get_quizzes()
        else:
            all_q = db_manager.get_quizzes(category_id)

        # Перемешивание вопросов для разнообразия каждого прохождения
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
            q_copy["correct_index"] = next(i for i, p in enumerate(paired) if p[2])
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
            "score": f"{score} из {total}",
            "percentage": f"{percentage}%",
            "rank": rank_be if language == "be" else rank_ru,
            "badge_title": badge_title,
            "streak": self.max_streak,
            "correct_count": score,
            "total_count": total
        }

quiz_service = QuizService()
