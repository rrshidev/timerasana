import logging

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from src.i18n import t, lang_from_telegram
from src.services.user_service import UserService
from src.utils.keyboard_service import KeyboardService

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Командные обработчики таймерасаны."""

    def __init__(self, bot, user_service: UserService):
        self.bot = bot
        self.user_service = user_service
        self.keyboard_service = KeyboardService()

    async def _register_user(self, message: types.Message, language: str = None) -> None:
        """При первом обращении добавляет пользователя в единую БД Dharana (app_users)."""
        await self.user_service.register_or_sync(
            telegram_id=message.from_user.id,
            name=message.from_user.first_name or "",
            username=message.from_user.username or "",
            language=language,
        )

    async def _lang(self, user_id: int) -> str:
        """Язык таймер-бота пользователя."""
        return await self.user_service.get_language(user_id)

    def _welcome_text(self, first_name: str, username: str, lang: str) -> str:
        name = first_name or username or ""
        greeting = t(lang, "welcome_greeting_name", name=name) if name else t(lang, "welcome_greeting")
        return (
            f"{greeting}\n\n"
            f"{t(lang, 'welcome_body')}"
        )

    async def start_command(self, message: types.Message):
        """Команда /start."""
        tg_lang = lang_from_telegram(message.from_user.language_code)
        await self._register_user(message, language=tg_lang)
        lang = await self._lang(message.from_user.id)

        await message.reply(
            self._welcome_text(message.from_user.first_name, message.from_user.username, lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(lang),
        )

    async def help_command(self, message: types.Message):
        """Команда /help."""
        lang = await self._lang(message.from_user.id)

        await message.reply(
            t(lang, "help_text"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(lang),
        )

    async def about_us_command(self, message: types.Message):
        """Команда /about_us."""
        await self._register_user(message)
        lang = await self._lang(message.from_user.id)

        await message.reply(
            t(lang, "about_text"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(lang),
        )

    async def about_us_callback(self, callback_query: types.CallbackQuery):
        """Кнопка «О нас»."""
        await self.bot.answer_callback_query(callback_query.id)
        await self.user_service.register_or_sync(
            telegram_id=callback_query.from_user.id,
            name=callback_query.from_user.first_name or "",
            username=callback_query.from_user.username or "",
        )
        lang = await self._lang(callback_query.from_user.id)
        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "about_text"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(lang),
        )

    async def language_command(self, message: types.Message):
        """Команда /language — выбор языка."""
        await self._register_user(message)
        lang = await self._lang(message.from_user.id)

        await message.reply(
            t(lang, "lang_choose"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.language_menu(lang),
        )

    async def language_menu_callback(self, callback_query: types.CallbackQuery):
        """Кнопка «Язык» в главном меню."""
        await self.bot.answer_callback_query(callback_query.id)
        await self.user_service.register_or_sync(
            telegram_id=callback_query.from_user.id,
            name=callback_query.from_user.first_name or "",
            username=callback_query.from_user.username or "",
        )
        lang = await self._lang(callback_query.from_user.id)
        await self.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=t(lang, "lang_choose"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.language_menu(lang),
        )

    async def language_set_callback(self, callback_query: types.CallbackQuery):
        """Выбор языка: установить и вернуться в главное меню."""
        await self.bot.answer_callback_query(callback_query.id)
        user_id = callback_query.from_user.id

        new_lang = "en" if callback_query.data == "lang_set_en" else "ru"
        await self.user_service.set_language(user_id, new_lang)
        lang = await self.user_service.get_language(user_id)

        await self.bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=t(lang, "lang_set_en" if new_lang == "en" else "lang_set_ru"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_service.start_menu(lang),
        )