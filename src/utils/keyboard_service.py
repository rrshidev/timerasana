from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class KeyboardService:
    """Reply-клавиатуры таймерасаны."""

    @staticmethod
    def start_menu() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⏱️ Таймер")],
                [KeyboardButton(text="🙏 О нас")],
            ],
            resize_keyboard=True,
        )