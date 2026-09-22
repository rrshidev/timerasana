import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, API_URL
from src.handlers.command_handlers import CommandHandlers
from src.handlers.timer_handlers import TimerHandlers
from src.handlers.routing import register_all
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
    register_all(dp, timer_handlers)

    # Фоновая задача обновления таймеров
    asyncio.create_task(timer_handlers.start_timer_update_loop())

    logger.info("Timer bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")