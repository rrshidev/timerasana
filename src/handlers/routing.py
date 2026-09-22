"""Регистрация обработчиков таймер-бота.

Единый источник правды для роутинга callbacks: main.py использует register(),
а тесты проверяют, что каждый callback_data, генерируемый TimerUI, покрыт
хотя бы одним предикатом.
"""

from aiogram import Dispatcher


def register_meditation(dp, handlers):
    r = [
        ("meditation_start", lambda c: c.data.startswith("meditation_") and c.data != "meditation_custom",
         handlers.meditation_start_callback),
        ("meditation_custom", lambda c: c.data == "meditation_custom", handlers.meditation_custom_callback),
        ("timer_meditation", lambda c: c.data == "timer_meditation", handlers.meditation_callback),
    ]
    for _, p, h in r:
        dp.callback_query.register(h, p)


def register_asana(dp, handlers):
    r = [
        ("asana_work_", lambda c: c.data.startswith("asana_work_") and "_m_" not in c.data and c.data != "asana_work_back",
         handlers.asana_work_callback),
        ("asana_rest_", lambda c: c.data.startswith("asana_rest_") and "_m_" not in c.data and c.data != "asana_rest_back",
         handlers.asana_rest_callback),
        ("asana_cycles_", lambda c: c.data.startswith("asana_cycles_") and "_m_" not in c.data and c.data != "asana_cycles_back",
         handlers.asana_cycles_callback),
        ("asana_start", lambda c: c.data == "asana_start", handlers.asana_start_callback),
        ("asana_config_work", lambda c: c.data == "asana_config_work", handlers.asana_config_work_callback),
        ("asana_config_rest", lambda c: c.data == "asana_config_rest", handlers.asana_config_rest_callback),
        ("asana_config_cycles", lambda c: c.data == "asana_config_cycles", handlers.asana_config_cycles_callback),
        ("asana_config", lambda c: c.data == "asana_config", handlers.asana_config_callback),
        ("timer_asana", lambda c: c.data == "timer_asana", handlers.asana_callback),
    ]
    for _, p, h in r:
        dp.callback_query.register(h, p)


def register_pranayama(dp, handlers):
    r = [
        ("pranayama_exercises_", lambda c: c.data.startswith("pranayama_exercises_") and "_m_" not in c.data and c.data != "pranayama_exercises_back",
         handlers.pranayama_exercises_select_callback),
        ("pranayama_exercise_time_", lambda c: c.data.startswith("pranayama_exercise_time_") and c.data != "pranayama_exercise_time_back",
         handlers.pranayama_exercise_time_select_callback),
        ("pranayama_rest_time_", lambda c: c.data.startswith("pranayama_rest_time_") and c.data != "pranayama_rest_time_back",
         handlers.pranayama_rest_time_select_callback),
        ("pranayama_start", lambda c: c.data == "pranayama_start", handlers.pranayama_start_callback),
        ("pranayama_exercises", lambda c: c.data == "pranayama_exercises", handlers.pranayama_exercises_callback),
        ("pranayama_exercise_time", lambda c: c.data == "pranayama_exercise_time", handlers.pranayama_exercise_time_callback),
        ("pranayama_rest_time", lambda c: c.data == "pranayama_rest_time", handlers.pranayama_rest_time_callback),
        ("pranayama_config", lambda c: c.data == "pranayama_config", handlers.pranayama_config_callback),
        ("timer_pranayama", lambda c: c.data == "timer_pranayama", handlers.pranayama_callback),
    ]
    for _, p, h in r:
        dp.callback_query.register(h, p)


def register_controls(dp, handlers):
    r = [
        ("timer_pause", lambda c: c.data.startswith("timer_pause"), handlers.timer_control_callback),
        ("timer_stop", lambda c: c.data.startswith("timer_stop"), handlers.timer_control_callback),
        ("timer_start", lambda c: c.data.startswith("timer_start"), handlers.timer_control_callback),
        ("timer_reset", lambda c: c.data.startswith("timer_reset"), handlers.timer_control_callback),
        ("timer_delete", lambda c: c.data.startswith("timer_delete"), handlers.timer_control_callback),
        ("timer_back", lambda c: c.data == "timer_back", handlers.timer_back_callback),
        ("timer_exit", lambda c: c.data == "timer_exit", handlers.timer_exit_callback),
        ("timer_main", lambda c: c.data == "timer_main", handlers.timer_main_callback),
    ]
    for _, p, h in r:
        dp.callback_query.register(h, p)


def register_all(dp, handlers):
    """Зарегистрировать все callback-обработчики таймера."""
    register_meditation(dp, handlers)
    register_asana(dp, handlers)
    register_pranayama(dp, handlers)
    register_controls(dp, handlers)