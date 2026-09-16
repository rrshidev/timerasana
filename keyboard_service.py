from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardService:
    """Inline-клавиатуры таймерасаны."""

    @staticmethod
    def start_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⏱️ Таймер", callback_data="timer_main")],
                [InlineKeyboardButton(text="🙏 О нас", callback_data="about_us")],
            ]
        )