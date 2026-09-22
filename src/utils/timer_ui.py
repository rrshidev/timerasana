from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.i18n import t, normalize_lang
from src.models.timer_models import TimerSession, TimerType, TimerStatus, TimerPhase


def _fmt_duration(seconds: int, lang: str) -> str:
    """Отформатировать длительность: 45с / 1м."""
    if seconds < 60:
        return t(lang, "dur_s", n=seconds)
    return t(lang, "dur_m", n=seconds // 60)


class TimerUI:
    """UI компоненты для таймера"""

    @staticmethod
    def get_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        """Главное меню таймера"""
        lang = normalize_lang(lang)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=t(lang, "kb_meditation"), callback_data="timer_meditation"),
                    InlineKeyboardButton(text=t(lang, "kb_asana"), callback_data="timer_asana")
                ],
                [
                    InlineKeyboardButton(text=t(lang, "kb_pranayama"), callback_data="timer_pranayama"),
                    InlineKeyboardButton(text=t(lang, "kb_exit_timer"), callback_data="timer_exit")
                ]
            ]
        )
        return keyboard

    @staticmethod
    def get_meditation_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора времени медитации"""
        lang = normalize_lang(lang)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "med_min_1"), callback_data="meditation_1")],
                [InlineKeyboardButton(text=t(lang, "med_min_5"), callback_data="meditation_5")],
                [InlineKeyboardButton(text=t(lang, "med_min_10"), callback_data="meditation_10")],
                [InlineKeyboardButton(text=t(lang, "med_min_15"), callback_data="meditation_15")],
                [InlineKeyboardButton(text=t(lang, "med_min_20"), callback_data="meditation_20")],
                [InlineKeyboardButton(text=t(lang, "med_min_30"), callback_data="meditation_30")],
                [InlineKeyboardButton(text=t(lang, "med_min_45"), callback_data="meditation_45")],
                [InlineKeyboardButton(text=t(lang, "med_min_60"), callback_data="meditation_60")],
                [InlineKeyboardButton(text=t(lang, "med_custom"), callback_data="meditation_custom")],
                [InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="timer_main")]
            ]
        )
        return keyboard

    @staticmethod
    def get_asana_config_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню конфигурации таймера асан"""
        lang = normalize_lang(lang)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=t(lang, "kb_work_time"), callback_data="asana_config_work"),
                    InlineKeyboardButton(text=t(lang, "kb_rest_time"), callback_data="asana_config_rest")
                ],
                [
                    InlineKeyboardButton(text=t(lang, "kb_cycles"), callback_data="asana_config_cycles"),
                    InlineKeyboardButton(text=t(lang, "kb_start"), callback_data="asana_start")
                ],
                [InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="timer_main")]
            ]
        )
        return keyboard

    @staticmethod
    def get_work_duration_menu(current_duration: int = 60, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора времени работы"""
        lang = normalize_lang(lang)
        durations = [30, 45, 60, 90, 120, 180]  # 30с, 45с, 1м, 1.5м, 2м, 3м

        keyboard = []
        for duration in durations:
            text = _fmt_duration(duration, lang)
            if duration == current_duration:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"asana_work_{duration}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="asana_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_rest_duration_menu(current_duration: int = 20, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора времени отдыха"""
        lang = normalize_lang(lang)
        durations = [10, 15, 20, 30, 45, 60]  # 10с, 15с, 20с, 30с, 45с, 1м

        keyboard = []
        for duration in durations:
            text = _fmt_duration(duration, lang)
            if duration == current_duration:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"asana_rest_{duration}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="asana_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_cycles_menu(current_cycles: int = 5, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора количества циклов"""
        lang = normalize_lang(lang)
        cycles = [3, 5, 7, 10, 15, 20]

        keyboard = []
        for cycle in cycles:
            text = t(lang, "cycles_n", n=cycle)
            if cycle == current_cycles:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"asana_cycles_{cycle}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="asana_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_pranayama_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню конфигурации пранаямы"""
        lang = normalize_lang(lang)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=t(lang, "kb_exercises"), callback_data="pranayama_exercises"),
                    InlineKeyboardButton(text=t(lang, "kb_ex_time"), callback_data="pranayama_exercise_time")
                ],
                [
                    InlineKeyboardButton(text=t(lang, "kb_rest_time"), callback_data="pranayama_rest_time"),
                    InlineKeyboardButton(text=t(lang, "kb_start"), callback_data="pranayama_start")
                ],
                [InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="timer_main")]
            ]
        )
        return keyboard

    @staticmethod
    def get_pranayama_exercises_menu(current_exercises: int = 3, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора количества упражнений"""
        lang = normalize_lang(lang)
        exercises = [1, 2, 3, 4, 5, 6, 7, 8]

        keyboard = []
        for exercise in exercises:
            text = t(lang, f"ex_{exercise}")
            if exercise == current_exercises:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"pranayama_exercises_{exercise}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="pranayama_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_pranayama_exercise_time_menu(current_time: int = 30, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора времени упражнения"""
        lang = normalize_lang(lang)
        times = [10, 15, 20, 30, 45, 60, 90, 120]

        keyboard = []
        for time in times:
            text = _fmt_duration(time, lang)
            if time == current_time:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"pranayama_exercise_time_{time}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="pranayama_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_pranayama_rest_time_menu(current_time: int = 20, lang: str = "ru") -> InlineKeyboardMarkup:
        """Меню выбора времени отдыха"""
        lang = normalize_lang(lang)
        times = [5, 10, 15, 20, 30, 45, 60]

        keyboard = []
        for time in times:
            text = _fmt_duration(time, lang)
            if time == current_time:
                text = f"✅ {text}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"pranayama_rest_time_{time}")])

        keyboard.append([InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="pranayama_config")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_control_keyboard(session: TimerSession, lang: str = "ru") -> InlineKeyboardMarkup:
        """Клавиатура управления таймером"""
        lang = normalize_lang(lang)
        if session.status == TimerStatus.RUNNING:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=t(lang, "kb_pause"), callback_data="timer_pause"),
                        InlineKeyboardButton(text=t(lang, "kb_stop"), callback_data="timer_stop")
                    ],
                    [InlineKeyboardButton(text=t(lang, "kb_reset"), callback_data="timer_reset")]
                ]
            )
        elif session.status == TimerStatus.PAUSED:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=t(lang, "kb_resume"), callback_data="timer_start"),
                        InlineKeyboardButton(text=t(lang, "kb_stop"), callback_data="timer_stop")
                    ],
                    [InlineKeyboardButton(text=t(lang, "kb_reset"), callback_data="timer_reset")]
                ]
            )
        else:  # STOPPED or COMPLETED
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=t(lang, "kb_start"), callback_data="timer_start"),
                        InlineKeyboardButton(text=t(lang, "kb_delete"), callback_data="timer_delete")
                    ],
                    [InlineKeyboardButton(text=t(lang, "kb_reset"), callback_data="timer_reset")]
                ]
            )
        return keyboard

    @staticmethod
    def format_timer_message(session: TimerSession, lang: str = "ru") -> str:
        """Отформатировать сообщение о состоянии таймера"""
        lang = normalize_lang(lang)
        if session.timer_type == TimerType.MEDITATION:
            return TimerUI._format_meditation_message(session, lang)
        else:
            return TimerUI._format_asana_message(session, lang)

    @staticmethod
    def _format_meditation_message(session: TimerSession, lang: str) -> str:
        """Отформатировать сообщение для медитации"""
        remaining = session.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60

        if session.status == TimerStatus.COMPLETED:
            return t(lang, "med_done")

        status_emoji = "⏸️" if session.status == TimerStatus.PAUSED else "🧘"

        m_word = "m" if lang == "en" else "м"
        s_word = "s" if lang == "en" else "с"
        progress = (
            f"{session.elapsed // 60}{m_word} {session.elapsed % 60}{s_word} / "
            f"{session.duration // 60}{m_word} {session.duration % 60}{s_word}"
        )

        return t(
            lang, "med_running",
            emoji=status_emoji,
            time=f"{minutes:02d}:{seconds:02d}",
            bar=session.get_progress_bar(),
            progress=progress
        )

    @staticmethod
    def _format_asana_message(session: TimerSession, lang: str) -> str:
        """Отформатировать сообщение для асан/пранаямы"""
        if session.timer_type == TimerType.ASANA:
            timer_name = t(lang, "asana_name")
        else:
            timer_name = t(lang, "pranayama_name")

        if session.status == TimerStatus.COMPLETED:
            return t(lang, "practice_done", name=timer_name)

        phase_emoji = "🛏️"
        phase_name = t(lang, "phase_rest")
        status_emoji = "⏸️" if session.status == TimerStatus.PAUSED else phase_emoji
        if session.current_phase == TimerPhase.WORK:
            phase_emoji = "💪"
            phase_name = t(lang, "phase_work")
            status_emoji = "⏸️" if session.status == TimerStatus.PAUSED else phase_emoji

        remaining = session.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60

        return t(
            lang, "state_line",
            emoji=status_emoji,
            name=timer_name,
            phase=phase_name,
            time=f"{minutes:02d}:{seconds:02d}",
            bar=session.get_progress_bar(),
            cycle=session.current_cycle,
            cycles=session.cycles,
            total=TimerUI._fmt_total(session, lang)
        )

    @staticmethod
    def _fmt_total(session: TimerSession, lang: str) -> str:
        m_word = "m" if lang == "en" else "м"
        s_word = "s" if lang == "en" else "с"
        return f"{session.total_elapsed // 60}{m_word} {session.total_elapsed % 60}{s_word}"

    @staticmethod
    def get_phase_notification(session: TimerSession, lang: str = "ru") -> str:
        """Получить уведомление о смене фазы"""
        lang = normalize_lang(lang)
        if session.current_phase == TimerPhase.REST:
            return t(lang, "phase_notif_rest", rest=session.rest_duration)
        else:
            return t(lang, "phase_notif_work", work=session.work_duration)