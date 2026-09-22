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


class TestProgressFormat:
    """Формат прогресса «Xм Yс / Zм Wс» должен совпадать в RU и EN (единицы локализованы)."""

    def _med_session(self, elapsed, duration, paused=False):
        from src.models.timer_models import TimerStatus
        s = type("S", (), {
            "timer_type": "meditation",
            "status": TimerStatus.PAUSED if paused else TimerStatus.RUNNING,
            "elapsed": elapsed,
            "duration": duration,
            "total_elapsed": elapsed,
            "current_phase": None,
            "current_cycle": 1,
            "cycles": 1,
            "rest_duration": 0,
            "get_remaining_time": lambda self: max(duration - elapsed, 0),
            "get_progress_bar": lambda self: "░" * 10,
        })()
        return s

    def test_meditation_progress_en_matches_ru(self):
        from src.utils.timer_ui import TimerUI
        session = self._med_session(151, 660)  # 2м31с / 11м
        ru = TimerUI._format_meditation_message(session, "ru")
        en = TimerUI._format_meditation_message(session, "en")
        assert "2м 31с / 11м 0с" in ru, f"RU progress сломан: {ru!r}"
        assert "2m 31s / 11m 0s" in en, f"EN progress сломан: {en!r}"

    def test_meditation_progress_zero_seconds(self):
        from src.utils.timer_ui import TimerUI
        session = self._med_session(60, 300)  # 1м0с / 5м0с
        ru = TimerUI._format_meditation_message(session, "ru")
        en = TimerUI._format_meditation_message(session, "en")
        assert "1м 0с / 5м 0с" in ru, ru
        assert "1m 0s / 5m 0s" in en, en

    def test_state_line_total_en_matches_ru(self):
        from src.utils.timer_ui import TimerUI
        from src.models.timer_models import TimerPhase, TimerStatus
        s = type("S", (), {
            "timer_type": "asana",
            "status": TimerStatus.RUNNING,
            "current_phase": TimerPhase.WORK,
            "elapsed": 120,
            "total_elapsed": 3725,  # 62м5с
            "current_cycle": 2,
            "cycles": 5,
            "rest_duration": 15,
            "work_duration": 60,
            "get_remaining_time": lambda self: 30,
            "get_progress_bar": lambda self: "█" * 10,
        })()
        ru = TimerUI._format_asana_message(s, "ru")
        en = TimerUI._format_asana_message(s, "en")
        assert "62м 5с" in ru, f"RU total сломан: {ru!r}"
        assert "62m 5s" in en, f"EN total сломан: {en!r}"


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