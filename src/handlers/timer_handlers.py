import logging
import asyncio
import re

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.timer_service import timer_service
from src.services.user_service import UserService
from src.utils.timer_ui import TimerUI
from src.utils.keyboard_service import KeyboardService
from src.i18n import t
from src.models.timer_models import (
    TimerType, TimerStatus, TimerPhase, TimerConfig, PranayamaConfig, timer_messages
)

logger = logging.getLogger(__name__)


class TimerHandlers:
    """Обработчики таймера медитации, асан и пранаямы."""

    def __init__(self, bot, user_service: UserService):
        self.bot = bot
        self.user_service = user_service
        self.awaiting_meditation_time = set()  # пользователи, ожидающие ввода времени медитации

    async def _lang(self, user_id: int) -> str:
        return await self.user_service.get_language(user_id)

    # Главное меню таймера
    async def timer_main_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        timer_messages[callback_query.from_user.id] = callback_query.message.message_id
        lang = await self._lang(callback_query.from_user.id)

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "timer_main_text"),
            reply_markup=TimerUI.get_main_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    # Медитация
    async def meditation_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "med_menu_text"),
            reply_markup=TimerUI.get_meditation_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def meditation_start_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 2:
            return

        try:
            minutes = int(parts[1])
        except ValueError:
            return

        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.create_meditation_timer(callback_query.from_user.id, minutes)
        timer_service.start_timer(callback_query.from_user.id)

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "med_started", minutes=minutes),
            reply_markup=TimerUI.get_control_keyboard(session, lang)
        )

        timer_messages[callback_query.from_user.id] = callback_query.message.message_id

    async def meditation_custom_callback(self, callback_query: types.CallbackQuery):
        """Запрос ручного ввода времени медитации."""
        await self.bot.answer_callback_query(callback_query.id)
        self.awaiting_meditation_time.add(callback_query.from_user.id)
        lang = await self._lang(callback_query.from_user.id)

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "med_custom_prompt"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="timer_meditation")]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_meditation_time_input(self, message: types.Message):
        """Обработка ручного ввода времени медитации."""
        user_id = message.from_user.id
        text = message.text.strip()
        lang = await self._lang(user_id)

        if not text.isdigit():
            if user_id not in self.awaiting_meditation_time:
                await message.reply(t(lang, "med_not_digit"))
            return

        minutes = int(text)
        if minutes < 1 or minutes > 120:
            await message.reply(t(lang, "med_range_error"))
            return

        self.awaiting_meditation_time.discard(user_id)

        session = timer_service.create_meditation_timer(user_id, minutes)
        timer_service.start_timer(user_id)

        timer_message = await message.answer(
            t(lang, "med_started", minutes=minutes),
            reply_markup=TimerUI.get_control_keyboard(session, lang)
        )
        timer_messages[user_id] = timer_message.message_id

        notification_message = await message.answer(
            t(lang, "med_notification", minutes=minutes),
            parse_mode=ParseMode.MARKDOWN
        )
        asyncio.create_task(self.delete_notification_after_delay(user_id, notification_message.message_id, 2))

    # Асана
    async def asana_callback(self, callback_query: types.CallbackQuery):
        """Меню конфигурации асан."""
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.ASANA:
            config = TimerConfig(
                work_duration=session.work_duration,
                rest_duration=session.rest_duration,
                cycles=session.cycles
            )
        else:
            config = TimerConfig()

        work_text = f"{config.work_duration}с" if config.work_duration < 60 else f"{config.work_duration//60}м"
        rest_text = f"{config.rest_duration}с" if config.rest_duration < 60 else f"{config.rest_duration//60}м"

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "asana_menu_text", work=work_text, rest=rest_text, cycles=config.cycles),
            reply_markup=TimerUI.get_asana_config_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def asana_config_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        await self.asana_callback(callback_query)

    async def asana_config_work_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_duration = session.work_duration if session and session.timer_type == TimerType.ASANA else 60

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "asana_choose_work"),
            reply_markup=TimerUI.get_work_duration_menu(current_duration, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def asana_config_rest_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_duration = session.rest_duration if session and session.timer_type == TimerType.ASANA else 20

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "asana_choose_rest"),
            reply_markup=TimerUI.get_rest_duration_menu(current_duration, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def asana_config_cycles_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_cycles = session.cycles if session and session.timer_type == TimerType.ASANA else 5

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "asana_choose_cycles"),
            reply_markup=TimerUI.get_cycles_menu(current_cycles, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def asana_work_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 3:
            return
        try:
            duration = int(parts[2])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.ASANA:
            session.work_duration = duration
        else:
            config = TimerConfig(work_duration=duration)
            timer_service.create_asana_timer(callback_query.from_user.id, config)

        await self.asana_callback(callback_query)

    async def asana_rest_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 3:
            return
        try:
            duration = int(parts[2])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.ASANA:
            session.rest_duration = duration
        else:
            config = TimerConfig(rest_duration=duration)
            timer_service.create_asana_timer(callback_query.from_user.id, config)

        await self.asana_callback(callback_query)

    async def asana_cycles_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 3:
            return
        try:
            cycles = int(parts[2])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.ASANA:
            session.cycles = cycles
        else:
            config = TimerConfig(cycles=cycles)
            timer_service.create_asana_timer(callback_query.from_user.id, config)

        await self.asana_callback(callback_query)

    async def asana_start_callback(self, callback_query: types.CallbackQuery):
        """Запуск таймера асан."""
        await self.bot.answer_callback_query(callback_query.id)

        user_id = callback_query.from_user.id
        lang = await self._lang(user_id)
        session = timer_service.get_session(user_id)
        if not session or session.timer_type != TimerType.ASANA:
            session = timer_service.create_asana_timer(user_id, TimerConfig())
        else:
            session = timer_service.start_timer(user_id)

        work_text = f"{session.work_duration}с" if session.work_duration < 60 else f"{session.work_duration//60}м"
        rest_text = f"{session.rest_duration}с" if session.rest_duration < 60 else f"{session.rest_duration//60}м"

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "asana_started", work=work_text, rest=rest_text, cycles=session.cycles),
            reply_markup=TimerUI.get_control_keyboard(session, lang),
            parse_mode=ParseMode.MARKDOWN
        )

        timer_messages[user_id] = callback_query.message.message_id

    # Пранаяма
    async def pranayama_callback(self, callback_query: types.CallbackQuery):
        """Меню пранаямы."""
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.PRANAYAMA:
            exercises = session.exercises
            exercise_time = session.exercise_duration
            rest_time = session.rest_duration
        else:
            exercises = 3
            exercise_time = 30
            rest_time = 20

        exercise_text = f"{exercise_time}с" if exercise_time < 60 else f"{exercise_time//60}м"
        rest_text = f"{rest_time}с" if rest_time < 60 else f"{rest_time//60}м"

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(
                lang, "pranayama_menu_text",
                exercises=exercises, exercise_time=exercise_text, rest_time=rest_text
            ),
            reply_markup=TimerUI.get_pranayama_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def pranayama_config_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        await self.pranayama_callback(callback_query)

    async def pranayama_exercises_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_exercises = session.exercises if session and session.timer_type == TimerType.PRANAYAMA else 3

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "pranayama_choose_exercises"),
            reply_markup=TimerUI.get_pranayama_exercises_menu(current_exercises, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def pranayama_exercise_time_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_time = session.exercise_duration if session and session.timer_type == TimerType.PRANAYAMA else 30

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "pranayama_choose_ex_time"),
            reply_markup=TimerUI.get_pranayama_exercise_time_menu(current_time, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def pranayama_rest_time_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        session = timer_service.get_session(callback_query.from_user.id)
        current_time = session.rest_duration if session and session.timer_type == TimerType.PRANAYAMA else 20

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "pranayama_choose_rest"),
            reply_markup=TimerUI.get_pranayama_rest_time_menu(current_time, lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def pranayama_exercises_select_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 3:
            return
        try:
            exercises = int(parts[2])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.PRANAYAMA:
            session.exercises = exercises
            session.cycles = exercises  # Для пранаямы cycles = exercises
        else:
            config = PranayamaConfig(exercises=exercises)
            timer_service.create_pranayama_timer(callback_query.from_user.id, config)

        await self.pranayama_callback(callback_query)

    async def pranayama_exercise_time_select_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 4:
            return
        try:
            duration = int(parts[3])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.PRANAYAMA:
            session.exercise_duration = duration
            session.work_duration = duration  # Для пранаямы work_duration = exercise_duration
        else:
            config = PranayamaConfig(exercise_duration=duration)
            timer_service.create_pranayama_timer(callback_query.from_user.id, config)

        await self.pranayama_callback(callback_query)

    async def pranayama_rest_time_select_callback(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)

        parts = callback_query.data.split('_')
        if len(parts) < 4:
            return
        try:
            duration = int(parts[3])
        except ValueError:
            return

        session = timer_service.get_session(callback_query.from_user.id)
        if session and session.timer_type == TimerType.PRANAYAMA:
            session.rest_duration = duration
        else:
            config = PranayamaConfig(rest_duration=duration)
            timer_service.create_pranayama_timer(callback_query.from_user.id, config)

        await self.pranayama_callback(callback_query)

    async def pranayama_start_callback(self, callback_query: types.CallbackQuery):
        """Запуск таймера пранаямы."""
        await self.bot.answer_callback_query(callback_query.id)

        user_id = callback_query.from_user.id
        lang = await self._lang(user_id)
        session = timer_service.get_session(user_id)
        if not session or session.timer_type != TimerType.PRANAYAMA:
            session = timer_service.create_pranayama_timer(user_id, PranayamaConfig())
        else:
            timer_service.start_timer(user_id)

        exercise_text = f"{session.exercise_duration}с" if session.exercise_duration < 60 else f"{session.exercise_duration//60}м"
        rest_text = f"{session.rest_duration}с" if session.rest_duration < 60 else f"{session.rest_duration//60}м"

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(
                lang, "pranayama_started",
                exercises=session.exercises, exercise_time=exercise_text, rest_time=rest_text
            ),
            reply_markup=TimerUI.get_control_keyboard(session, lang),
            parse_mode=ParseMode.MARKDOWN
        )

        timer_messages[callback_query.from_user.id] = callback_query.message.message_id

    # Управление таймером
    async def timer_control_callback(self, callback_query: types.CallbackQuery):
        """Общий обработчик управления таймером."""
        await self.bot.answer_callback_query(callback_query.id)

        action = callback_query.data.split('_')[1]  # pause, stop, start, reset, delete
        user_id = callback_query.from_user.id
        lang = await self._lang(user_id)

        if action == "start":
            session = timer_service.start_timer(user_id)
            if session:
                await self.update_timer_message(user_id, session)

        elif action == "pause":
            session = timer_service.pause_timer(user_id)
            if session:
                await self.update_timer_message(user_id, session)

        elif action == "stop":
            session = timer_service.stop_timer(user_id)
            if session:
                if user_id in timer_messages:
                    try:
                        await self.bot.delete_message(
                            chat_id=user_id,
                            message_id=timer_messages[user_id]
                        )
                    except:
                        pass
                    del timer_messages[user_id]

                await self.bot.send_message(
                    user_id,
                    t(lang, "timer_stopped"),
                    reply_markup=TimerUI.get_main_menu(lang),
                    parse_mode=ParseMode.MARKDOWN
                )

        elif action == "reset":
            session = timer_service.reset_timer(user_id)
            if session:
                await self.update_timer_message(user_id, session)

        elif action == "delete":
            session = timer_service.get_session(user_id)
            if session:
                await self.bot.edit_message_text(
                    chat_id=callback_query.from_user.id,
                    message_id=callback_query.message.message_id,
                    text=t(lang, "timer_deleted"),
                    reply_markup=TimerUI.get_main_menu(lang)
                )
            timer_service.delete_session(user_id)

    async def timer_back_callback(self, callback_query: types.CallbackQuery):
        """Возврат в главное меню таймера."""
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "timer_back"),
            reply_markup=TimerUI.get_main_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def timer_exit_callback(self, callback_query: types.CallbackQuery):
        """Выход из таймера в главное меню бота."""
        await self.bot.answer_callback_query(callback_query.id)
        lang = await self._lang(callback_query.from_user.id)

        if callback_query.from_user.id in timer_messages:
            del timer_messages[callback_query.from_user.id]

        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "timer_exit"),
            reply_markup=KeyboardService.start_menu(lang),
            parse_mode=ParseMode.MARKDOWN
        )

    async def update_timer_message(self, user_id: int, session):
        """Обновляет сообщение таймера."""
        if user_id not in timer_messages:
            return

        try:
            lang = self.user_service.get_cached_language(user_id, "ru")
            await self.bot.edit_message_text(
                chat_id=user_id,
                message_id=timer_messages[user_id],
                text=TimerUI.format_timer_message(session, lang),
                reply_markup=TimerUI.get_control_keyboard(session, lang),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error updating timer message: {e}")

    async def delete_notification_after_delay(self, user_id: int, message_id: int, delay_seconds: int):
        """Удаляет уведомление через указанное время."""
        await asyncio.sleep(delay_seconds)
        try:
            await self.bot.delete_message(
                chat_id=user_id,
                message_id=message_id
            )
            logger.info(f"Deleted notification message {message_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete notification message {message_id}: {e}")

    # Фоновая задача обновления таймеров
    async def start_timer_update_loop(self):
        """Запустить фоновый цикл обновления таймеров."""
        while True:
            try:
                for user_id, session in list(timer_service.active_sessions.items()):
                    if session.status == TimerStatus.RUNNING:
                        old_phase = session.current_phase

                        updated_session = timer_service.update_timer(user_id)

                        if updated_session:
                            # Обновляем основное сообщение каждые 5 секунд
                            if updated_session.elapsed % 5 == 0:
                                await self.update_timer_message(user_id, updated_session)

                            # Проверяем завершение
                            if updated_session.status == TimerStatus.COMPLETED:
                                timer_message_id = timer_messages.get(user_id)
                                timer_service.delete_session(user_id)

                                try:
                                    lang = self.user_service.get_cached_language(user_id, "ru")
                                    complete_notification = await self.bot.send_message(
                                        user_id,
                                        t(lang, "practice_completed"),
                                        parse_mode=ParseMode.MARKDOWN
                                    )
                                    asyncio.create_task(
                                        self.delete_notification_after_delay(user_id, complete_notification.message_id, 2)
                                    )
                                except Exception as e:
                                    logger.error(f"Error sending completion notification: {e}")

                                if user_id in timer_messages:
                                    try:
                                        lang = self.user_service.get_cached_language(user_id, "ru")
                                        await self.bot.edit_message_text(
                                            chat_id=user_id,
                                            message_id=timer_messages[user_id],
                                            text=TimerUI.format_timer_message(updated_session, lang),
                                            reply_markup=TimerUI.get_main_menu(lang),
                                            parse_mode=ParseMode.MARKDOWN
                                        )
                                    except:
                                        pass
                                    del timer_messages[user_id]

                            # Проверяем смену фазы — отправляем временное уведомление
                            elif (updated_session.timer_type in [TimerType.ASANA, TimerType.PRANAYAMA] and
                                  old_phase != updated_session.current_phase and
                                  updated_session.rest_duration > 0):
                                lang = self.user_service.get_cached_language(user_id, "ru")
                                notification_message = await self.bot.send_message(
                                    user_id,
                                    TimerUI.get_phase_notification(updated_session, lang),
                                    reply_markup=TimerUI.get_control_keyboard(updated_session, lang),
                                    parse_mode=ParseMode.MARKDOWN
                                )
                                asyncio.create_task(self.delete_notification_after_delay(user_id, notification_message.message_id, 2))

                await asyncio.sleep(1)  # Обновляем каждую секунду

            except Exception as e:
                logger.error(f"Error in timer update loop: {e}")
                await asyncio.sleep(5)