from loader import dp
from aiogram import types, Dispatcher
from keyboards import kb_client
from utils.db_api import api_pizza_db

async def comand_start(message: types.Message):
	await message.answer('''вас приветствует бот пиццери!
Введите "/help" что-бы узнать все комманды''')

async def comand_help(message: types.Message):
	await message.answer(text = "Меню комманд у вас на клавиaтуре!", reply_markup=kb_client)

async def comand_timetable(message: types.Message):
	await message.answer('''Работаем с 8:00 до 20:00.
Без обедов!''')

async def comand_menu(message: types.Message):
	await api_pizza_db.db_view_menu_command(message)

async def comand_address(message: types.Message):
	await message.answer('ул.Колбаскина, дом 15')

def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(comand_start, commands=['start'])
	dp.register_message_handler(comand_help, commands=['help'])
	dp.register_message_handler(comand_timetable, commands=['timetable'])
	dp.register_message_handler(comand_menu, commands=['menu'])
	dp.register_message_handler(comand_address, commands=['address'])
	dp.register_message_handler(comand_address, commands=['address'])