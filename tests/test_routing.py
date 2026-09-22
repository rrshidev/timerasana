# -*- coding: utf-8 -*-
"""Проверка согласованности роутинга: каждый callback_data, который генерирует
TimerUI, должен покрываться ровно одним предикатом из src.handlers.routing.
Это защищает от рассинхрона клавиатур и регистрации (как было с meditation_* и
pranayama_* до фикса).
"""
import pytest

from src.utils import timer_ui
from src.handlers import routing


class _CB:
    def __init__(self, data):
        self.data = data


def _iter_keyboards():
    """Инстанс-методы без сессии генерируем, остальные перебираем с параметрами."""
    kws = [
        ("get_main_menu", {}),
        ("get_meditation_menu", {}),
        ("get_asana_config_menu", {}),
        ("get_work_duration_menu", {}),
        ("get_rest_duration_menu", {}),
        ("get_cycles_menu", {}),
        ("get_pranayama_menu", {}),
        ("get_pranayama_exercises_menu", {}),
        ("get_pranayama_exercise_time_menu", {}),
        ("get_pranayama_rest_time_menu", {}),
    ]
    for name, kw in kws:
        fn = getattr(timer_ui.TimerUI, name)
        try:
            m = fn(**kw)
        except TypeError:
            m = fn("ru", **kw)
        if m is not None and hasattr(m, "inline_keyboard"):
            yield m

    # get_control_keyboard нуждается в сессии; проверяем все три статуса.
    from src.models.timer_models import TimerStatus

    for status in (TimerStatus.RUNNING, TimerStatus.PAUSED, TimerStatus.STOPPED,
                   TimerStatus.COMPLETED):
        _Session = type("_Session", (), {"status": status})
        kb = timer_ui.TimerUI.get_control_keyboard(_Session(), "ru")
        if kb is not None and hasattr(kb, "inline_keyboard"):
            yield kb


def _all_callback_data():
    data = set()
    for kb in _iter_keyboards():
        for row in kb.inline_keyboard:
            for btn in row:
                data.add(btn.callback_data)
    return data


def _all_predicates():
    """Все предикаты, зарегистрированные в routing."""
    preds = []
    for fn_name in ("register_meditation", "register_asana", "register_pranayama", "register_controls"):
        fn = getattr(routing, fn_name)
        # подменяем Dispatcher сборщиком предикатов
        captured = []

        class FakeDP:
            @property
            def callback_query(self):
                return self

            def register(self, handler, predicate):
                captured.append((handler, predicate))

        # у routing-функций первый аргумент dp, второй handlers
        class _Handlers:
            def __getattr__(self, name):
                return lambda *a, **kw: None

        fn(FakeDP(), _Handlers())
        preds.extend(p[1] for p in captured)
    return preds


def _pred_matches(pred, data):
    return bool(pred(_CB(data)))


class TestRoutingCoverage:
    def test_every_callback_data_is_routed(self):
        data = _all_callback_data()
        preds = _all_predicates()
        assert data, "не собрано ни одного callback_data"

        unmatched = sorted(d for d in data if not any(_pred_matches(p, d) for p in preds))
        assert not unmatched, f"callback_data без обработчика: {unmatched}"

    def test_no_overlap_between_routes(self):
        """Каждый callback_data матчится ровно одним предикатом (нет неоднозначности)."""
        data = _all_callback_data()
        preds = _all_predicates()

        ambiguous = []
        for d in sorted(data):
            matches = [i for i, p in enumerate(preds) if _pred_matches(p, d)]
            if len(matches) != 1:
                ambiguous.append((d, matches))
        assert not ambiguous, f"неоднозначные callback_data (num matches): {ambiguous}"

    def test_added_example_routes_cover_key_groups(self):
        """Контрольные группы: медитация/асана/пранаяма/управление."""
        data = _all_callback_data()
        preds = _all_predicates()

        groups = {
            "meditation": ["meditation_1", "meditation_60", "meditation_custom"],
            "asana": ["asana_config_work", "asana_work_60", "asana_start", "asana_cycles_5"],
            "pranayama": ["pranayama_exercises", "pranayama_exercises_3",
                          "pranayama_exercise_time", "pranayama_exercise_time_45",
                          "pranayama_rest_time", "pranayama_start"],
            "controls": ["timer_pause", "timer_stop", "timer_start", "timer_reset",
                         "timer_delete", "timer_exit", "timer_main"],
        }
        for name, samples in groups.items():
            for probe in samples:
                matches = [i for i, p in enumerate(preds) if _pred_matches(p, probe)]
                assert len(matches) == 1, f"{name}: {probe} -> {len(matches)} матчей {matches}"
                assert probe in data, f"{name}: {probe} отсутствует в клавиатурах TimerUI"