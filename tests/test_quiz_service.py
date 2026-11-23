import pytest
from src.services.quiz_service import quiz_service

def test_quiz_service_initialization():
    quizzes = quiz_service.get_all_quizzes()
    assert len(quizzes) >= 6, "Должно быть загружено минимум 6 образовательных викторин"

def test_quiz_check_answer_correct():
    quiz_service.reset_score()
    all_q = quiz_service.get_all_quizzes()
    target = all_q[0]
    res = quiz_service.check_answer(quiz_id=target["id"], selected_index=target["correct_index"], language="ru")
    assert res["is_correct"] is True
    assert quiz_service.current_score == 1

def test_quiz_check_answer_incorrect():
    quiz_service.reset_score()
    all_q = quiz_service.get_all_quizzes()
    target = all_q[0]
    wrong_index = (target["correct_index"] + 1) % len(target["options_ru"])
    res = quiz_service.check_answer(quiz_id=target["id"], selected_index=wrong_index, language="ru")
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

def test_quiz_categories():
    cats_ru = quiz_service.get_categories("ru")
    assert len(cats_ru) == 6
    assert any(c["id"] == "tournament" for c in cats_ru)
    assert any(c["id"] == "tracks" for c in cats_ru)

    cats_be = quiz_service.get_categories("be")
    assert len(cats_be) == 6

def test_quiz_view_states():
    from src.ui.views.quiz_view import QuizView
    
    selected_species = []
    view = QuizView(
        get_language=lambda: "ru",
        on_select_species=lambda sid: selected_species.append(sid)
    )
    assert view.view_state == "categories"
    assert view.content is not None

    # Запуск категории
    view._start_category("animals")
    assert view.view_state == "question"
    assert len(view.session_quizzes) > 0
    assert view.content is not None
    assert view.answer_checked is False

    # Выбор варианта и проверка ответа
    view._select_option(0)
    assert view.selected_option == 0
    view._handle_action_btn(None)
    assert view.answer_checked is True
    assert view.last_result is not None

    # Переход к сертификату
    view.view_state = "certificate"
    view._build_ui()
    assert view.content is not None

    # Проверка вызова паспорта вида
    view._open_species("bison-bonasus")
    assert "bison-bonasus" in selected_species

    # Возврат к категориям
    view._return_to_categories(None)
    assert view.view_state == "categories"

def test_full_quiz_session():
    from src.ui.views.quiz_view import QuizView
    view = QuizView(get_language=lambda: "ru")
    view._start_category("tournament")
    assert len(view.session_quizzes) == 10
    for _ in range(10):
        assert view.view_state == "question"
        view._select_option(0)
        view._handle_action_btn(None) # check answer
        view._handle_action_btn(None) # next question or finish
    assert view.view_state == "certificate"
    assert view.content is not None

def test_quiz_session_options_shuffled():
    session_q = quiz_service.start_session("tournament", limit=10)
    indices = [q["correct_index"] for q in session_q]
    assert len(set(indices)) > 1, f"Indices should be distributed, got {indices}"

