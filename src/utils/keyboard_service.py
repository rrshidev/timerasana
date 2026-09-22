from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.i18n import t


class KeyboardService:
    """Inline-клавиатуры таймерасаны."""

    @staticmethod
    def start_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "kb_timer"), callback_data="timer_main")],
                [
                    InlineKeyboardButton(text=t(lang, "kb_language"), callback_data="lang_menu"),
                    InlineKeyboardButton(text=t(lang, "kb_about"), callback_data="about_us"),
                ],
            ]
        )

    @staticmethod
    def language_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=t(lang, "kb_lang_ru"), callback_data="lang_set_ru"),
                    InlineKeyboardButton(text=t(lang, "kb_lang_en"), callback_data="lang_set_en"),
                ],
                [InlineKeyboardButton(text=t(lang, "kb_back"), callback_data="timer_exit")],
            ]
        )