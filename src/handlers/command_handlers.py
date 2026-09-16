import logging

from aiogram import types
from aiogram.enums import ParseMode

from src.services.user_service import UserService
from src.utils.keyboard_service import KeyboardService

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Командные обработчики таймерасаны."""

    def __init__(self, bot, user_service: UserService):
        self.bot = bot
        self.user_service = user_service
        self.keyboard_service = KeyboardService()

    async def _register_user(self, message: types.Message) -> None:
        """При первом обращении добавляет пользователя в единую БД Dharana (app_users)."""
        await self.user_service.register_or_sync(
            telegram_id=message.from_user.id,
            name=message.from_user.first_name or "",
            username=message.from_user.username or "",
        )

    def _welcome_text(self, first_name: str, username: str) -> str:
        name = first_name or username or ""
        greeting = f"Намаскар, {name}! 🙏" if name else "Намаскар! 🙏"
        return (
            f"{greeting}\n\n"
            "Добро пожаловать в **TimerAsana** — таймер для йогических практик "
            "проекта **Dharana** 🧘\n\n"
            "Что я умею:\n"
            "• 🧘 **Медитация** — от 1 до 60 минут\n"
            "• 🧘‍♂️ **Асана** — практика с циклами работы и отдыха\n"
            "• 🌬️ **Пранаяма** — дыхательные упражнения с настройкой\n\n"
            "Полезные ссылки:\n"
            "• Основной бот Dharana — [@yogaasana_bot](https://t.me/yogaasana_bot)\n"
            "• Веб-приложение — [dharana.ru](https://dharana.ru)\n\n"
            "Выбери действие ниже 👇"
        )

    async def start_command(self, message: types.Message):
        """Команда /start."""
        await self._register_user(message)

        await message.reply(
            self._welcome_text(message.from_user.first_name, message.from_user.username),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(),
        )

    async def help_command(self, message: types.Message):
        """Команда /help."""
        help_text = (
            "**TimerAsana** — таймер для йогических практик проекта Dharana.\n\n"
            "🕐 **ТАЙМЕР** 🕐\n\n"
            "🧘 **Медитация** — выбери время от 1 до 60 минут (пресеты или ручной ввод)\n"
            "🧘‍♂️ **Асана** — настраиваемые циклы работы и отдыха (30с-3м работа, 10с-1м отдых, 3-20 циклов)\n"
            "🌬️ **Пранаяма** — дыхательные упражнения (1-8 упражнений, 10с-2м каждое, 5с-1м отдых)\n\n"
            "Управление во время практики: пауза, продолжить, стоп, сброс.\n\n"
            "Команды:\n"
            "----> /start 🚀 - Главное меню\n"
            "----> /help ❓ - Справка\n"
            "----> /about_us 🙏 - О проекте и авторах"
        )
        await message.reply(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(),
        )

    async def about_us_command(self, message: types.Message):
        """Команда /about_us."""
        await self._register_user(message)

        await message.reply(
            self._about_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(),
        )

    async def about_us_callback(self, callback_query: types.CallbackQuery):
        """Кнопка «О нас»."""
        await self.bot.answer_callback_query(callback_query.id)
        await self.user_service.register_or_sync(
            telegram_id=callback_query.from_user.id,
            name=callback_query.from_user.first_name or "",
            username=callback_query.from_user.username or "",
        )
        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=self._about_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(),
        )

    def _about_text(self) -> str:
        return (
            "🙏 **TimerAsana — часть проекта Dharana**\n\n"
            "TimerAsana — это таймер для йогических практик: медитации, асан и пранаямы. "
            "Он создан как часть экосистемы **Dharana** — проекта, который помогает "
            "делать йогу регулярной и доступной каждому.\n\n"
            "**Dharana** включает:\n"
            "• Основной бот [@yogaasana_bot](https://t.me/yogaasana_bot) — каталог из 100+ асан, "
            "готовые комплексы, генератор практики, асана дня\n"
            "• Веб-приложение [dharana.ru](https://dharana.ru)\n"
            "• TimerAsana — этот таймер для практик\n\n"
            "Два человека. Йога. Немного кода. И желание, чтобы ваша практика "
            "была регулярной и приносила радость.\n\n"
            "Связаться с нами:\n"
            "@RrshiDev · @yogaolleg\n"
            "instagram.com/yogaolleg/\n\n"
            "Хорошей практики! 🙏"
        )