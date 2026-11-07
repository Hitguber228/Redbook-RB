from typing import List, Dict, Any, Optional
from ..database.db import db_manager

class QuizService:
    def __init__(self):
        self.current_score = 0
        self.total_answered = 0

    def get_all_quizzes(self, quiz_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return db_manager.get_quizzes(quiz_type)

    def check_answer(self, quiz_id: int, selected_index: int, language: str = "ru") -> Dict[str, Any]:
        quizzes = db_manager.get_quizzes()
        target = next((q for q in quizzes if q["id"] == quiz_id), None)
        if not target:
            return {"is_correct": False, "explanation": "Вопрос не найден"}

        is_correct = (selected_index == target["correct_index"])
        self.total_answered += 1
        if is_correct:
            self.current_score += 1

        explanation = target["explanation_be"] if language == "be" else target["explanation_ru"]

        return {
            "is_correct": is_correct,
            "correct_index": target["correct_index"],
            "explanation": explanation,
            "current_score": self.current_score,
            "total_answered": self.total_answered
        }

    def reset_score(self):
        self.current_score = 0
        self.total_answered = 0

    def get_certificate_data(self, user_name: str, language: str = "ru") -> Dict[str, str]:
        score = self.current_score
        total = max(self.total_answered, 1)
        percentage = int((score / total) * 100)

        if percentage >= 80:
            rank_ru = "Хранитель природы Беларуси (Высшая степень)"
            rank_be = "Захавальнік прыроды Беларусі (Найвышэйшая ступень)"
        elif percentage >= 50:
            rank_ru = "Полевой натуралист Беларуси"
            rank_be = "Палявы натураліст Беларусі"
        else:
            rank_ru = "Юный исследователь Красной книги"
            rank_be = "Юны даследчык Чырвонай кнігі"

        return {
            "user_name": user_name or ("Юный натуралист" if language == "ru" else "Юны натураліст"),
            "score": f"{score} / {total}",
            "percentage": f"{percentage}%",
            "rank": rank_be if language == "be" else rank_ru
        }

quiz_service = QuizService()
