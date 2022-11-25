from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .utils import callback
from const.classes import *


def start_markup(is_user_exist: bool):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if is_user_exist:
        markup.row(types.KeyboardButton("Просмотреть свой список подарков"),
                   types.KeyboardButton("Узнать подарки друга"))
    else:
        markup.row(types.KeyboardButton("Создать список подарков"),
                   types.KeyboardButton("Узнать подарки друга"))
    return markup


def back_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Назад", callback_data='start'))
    return markup


def back_set_name_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Назад к вводу имени"))
    return markup


def back_set_birthdate_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Не хочу давать свой номер!"),
               types.KeyboardButton("Назад к вводу даты рождения"))
    return markup


def back_set_phone():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Да, все верно"),
               types.KeyboardButton("Назад к вводу номера телефона"))
    return markup


def wishes_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Создать подарок"))
    markup.row(types.KeyboardButton("Назад"))
    return markup


def back_to_wishes_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("К списку подарков..."))
    return markup


def del_gift(wish_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Удалить', callback_data=WishToDelete.new(wish_id=wish_id)))
    return markup


def yes_no():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Да, это он!"))
    markup.row(types.KeyboardButton("Нет"))
    return markup


def book_gift(wish_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Забронировать подарок.', callback_data=WishToBook.new(wish_id=wish_id)))
    return markup
