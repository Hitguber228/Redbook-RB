import pytest
from src.services.quiz_service import quiz_service

def test_quiz_service_initialization():
    quizzes = quiz_service.get_all_quizzes()
    assert len(quizzes) >= 6, "Должно быть загружено минимум 6 образовательных викторин"

def test_quiz_check_answer_correct():
    # Проверка правильного ответа на 1-й вопрос
    quiz_service.reset_score()
    res = quiz_service.check_answer(quiz_id=1, selected_index=0, language="ru")
    assert res["is_correct"] is True
    assert quiz_service.current_score == 1

def test_quiz_check_answer_incorrect():
    quiz_service.reset_score()
    res = quiz_service.check_answer(quiz_id=1, selected_index=3, language="ru")
    assert res["is_correct"] is False
    assert quiz_service.current_score == 0

def test_quiz_certificate_generation():
    quiz_service.reset_score()
    quiz_service.current_score = 5
    quiz_service.total_answered = 6
    cert = quiz_service.get_certificate_data(user_name="Иван", language="ru")
    assert cert["user_name"] == "Иван"
    assert "score" in cert
    assert "rank" in cert
