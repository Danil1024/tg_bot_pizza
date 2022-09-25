from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb1 = KeyboardButton('/timetable')
kb2 = KeyboardButton('/menu')
kb3 = KeyboardButton('/address')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.add(kb1).add(kb2).add(kb3)