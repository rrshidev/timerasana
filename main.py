import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, API_URL
from src.handlers.command_handlers import CommandHandlers
from src.handlers.timer_handlers import TimerHandlers
from src.services.user_service import UserService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN не задан. Проверь .env (BOT_TOKEN=...).")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    user_service = UserService(API_URL)
    command_handlers = CommandHandlers(bot, user_service)
    timer_handlers = TimerHandlers(bot, user_service)

    dp.message.register(command_handlers.start_command, CommandStart())
    dp.message.register(command_handlers.help_command, Command("help"))
    dp.message.register(command_handlers.about_us_command, Command("about_us"))
    dp.message.register(command_handlers.language_command, Command("language"))

    # Главное меню (inline-кнопки)
    dp.callback_query.register(command_handlers.about_us_callback, lambda c: c.data == "about_us")
    dp.callback_query.register(command_handlers.language_menu_callback, lambda c: c.data == "lang_menu")
    dp.callback_query.register(command_handlers.language_set_callback, lambda c: c.data in ("lang_set_ru", "lang_set_en"))

    # Ввод времени медитации (цифровое сообщение)
    dp.message.register(
        timer_handlers.handle_meditation_time_input,
        lambda message: message.text and message.text.strip().isdigit()
    )

    # Callback-обработчики таймера
    dp.callback_query.register(timer_handlers.meditation_start_callback, lambda c: c.data.startswith("meditation_start_"))
    dp.callback_query.register(timer_handlers.meditation_custom_callback, lambda c: c.data == "meditation_custom")
    dp.callback_query.register(timer_handlers.meditation_callback, lambda c: c.data == "timer_meditation")
    dp.callback_query.register(timer_handlers.asana_work_callback, lambda c: c.data.startswith("asana_work_") and "_m_" not in c.data and c.data != "asana_work_back")
    dp.callback_query.register(timer_handlers.asana_rest_callback, lambda c: c.data.startswith("asana_rest_") and "_m_" not in c.data and c.data != "asana_rest_back")
    dp.callback_query.register(timer_handlers.asana_cycles_callback, lambda c: c.data.startswith("asana_cycles_") and "_m_" not in c.data and c.data != "asana_cycles_back")
    dp.callback_query.register(timer_handlers.asana_start_callback, lambda c: c.data == "asana_start")
    dp.callback_query.register(timer_handlers.asana_config_work_callback, lambda c: c.data == "asana_config_work")
    dp.callback_query.register(timer_handlers.asana_config_rest_callback, lambda c: c.data == "asana_config_rest")
    dp.callback_query.register(timer_handlers.asana_config_cycles_callback, lambda c: c.data == "asana_config_cycles")
    dp.callback_query.register(timer_handlers.asana_config_callback, lambda c: c.data == "asana_config")
    dp.callback_query.register(timer_handlers.asana_callback, lambda c: c.data == "timer_asana")
    dp.callback_query.register(timer_handlers.pranayama_exercises_select_callback, lambda c: c.data.startswith("pranayama_exercises_") and "_m_" not in c.data and c.data != "pranayama_exercises_back")
    dp.callback_query.register(timer_handlers.pranayama_exercise_time_select_callback, lambda c: c.data.startswith("pranayama_exercise_time_") and c.data != "pranayama_exercise_time_back")
    dp.callback_query.register(timer_handlers.pranayama_rest_time_select_callback, lambda c: c.data.startswith("pranayama_rest_time_") and c.data != "pranayama_rest_time_back")
    dp.callback_query.register(timer_handlers.pranayama_start_callback, lambda c: c.data == "pranayama_start")
    dp.callback_query.register(timer_handlers.pranayama_exercises_callback, lambda c: c.data == "pranayama_config_exercises")
    dp.callback_query.register(timer_handlers.pranayama_exercise_time_callback, lambda c: c.data == "pranayama_config_exercise_time")
    dp.callback_query.register(timer_handlers.pranayama_rest_time_callback, lambda c: c.data == "pranayama_config_rest_time")
    dp.callback_query.register(timer_handlers.pranayama_config_callback, lambda c: c.data == "pranayama_config")
    dp.callback_query.register(timer_handlers.pranayama_callback, lambda c: c.data == "timer_pranayama")
    dp.callback_query.register(timer_handlers.timer_control_callback, lambda c: c.data.startswith("timer_pause"))
    dp.callback_query.register(timer_handlers.timer_control_callback, lambda c: c.data.startswith("timer_stop"))
    dp.callback_query.register(timer_handlers.timer_control_callback, lambda c: c.data.startswith("timer_start"))
    dp.callback_query.register(timer_handlers.timer_control_callback, lambda c: c.data.startswith("timer_reset"))
    dp.callback_query.register(timer_handlers.timer_control_callback, lambda c: c.data.startswith("timer_delete"))
    dp.callback_query.register(timer_handlers.timer_back_callback, lambda c: c.data == "timer_back")
    dp.callback_query.register(timer_handlers.timer_exit_callback, lambda c: c.data == "timer_exit")
    dp.callback_query.register(timer_handlers.timer_main_callback, lambda c: c.data == "timer_main")

    # Фоновая задача обновления таймеров
    asyncio.create_task(timer_handlers.start_timer_update_loop())

    logger.info("Timer bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")