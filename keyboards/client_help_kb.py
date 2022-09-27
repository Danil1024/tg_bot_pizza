from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb1 = KeyboardButton('/расписание')
kb2 = KeyboardButton('/меню')
kb3 = KeyboardButton('/адрес')

kb_help_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_help_client.add(kb1).add(kb2).add(kb3)