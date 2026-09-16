import pytest


class TestTimerModels:
    def test_timer_config_defaults(self):
        from src.models.timer_models import TimerConfig
        config = TimerConfig()
        assert config.work_duration == 60
        assert config.rest_duration == 20
        assert config.cycles == 5

    def test_pranayama_config_defaults(self):
        from src.models.timer_models import PranayamaConfig
        config = PranayamaConfig()
        assert config.exercises == 3
        assert config.exercise_duration == 30
        assert config.rest_duration == 20


class TestTimerService:
    def test_create_meditation_timer(self):
        from src.services.timer_service import timer_service
        from src.models.timer_models import TimerType, TimerStatus

        user_id = 999001
        timer_service.clear_all_sessions()
        session = timer_service.create_meditation_timer(user_id, 10)
        assert session.timer_type == TimerType.MEDITATION
        assert session.duration == 600
        assert timer_service.get_session(user_id) is session

    def test_timer_flow_update_completes(self):
        from src.services.timer_service import timer_service
        from src.models.timer_models import TimerStatus

        user_id = 999002
        timer_service.clear_all_sessions()
        session = timer_service.create_meditation_timer(user_id, 1)
        timer_service.start_timer(user_id)

        updated = timer_service.update_timer(user_id)
        assert updated is not None

        # Силой доводим до конца: сдвигаем start_time в прошлое
        from datetime import datetime, timedelta
        session.start_time = datetime.now() - timedelta(seconds=session.duration + 1)
        updated = timer_service.update_timer(user_id)
        assert updated.status == TimerStatus.COMPLETED

        # Удаляем сессию вручную (в проде это делает update-цикл)
        assert timer_service.delete_session(user_id) is True
        assert timer_service.get_session(user_id) is None

    def test_clear_all_sessions(self):
        from src.services.timer_service import timer_service

        user_id = 999003
        timer_service.create_meditation_timer(user_id, 5)
        timer_service.clear_all_sessions()
        assert len(timer_service.active_sessions) == 0