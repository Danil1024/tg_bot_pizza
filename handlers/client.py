from loader import dp
from aiogram import types, Dispatcher
from keyboards import kb_help_client
from utils.db_api import api_pizza_db
from aiogram.types import ReplyKeyboardRemove

list_product = list()


@dp.message_handler(commands=['start'])
async def comand_start(message: types.Message):
	await message.answer('''вас приветствует бот пиццери!
Введите "/help" что-бы узнать все комманды''')

@dp.message_handler(commands=['help'])
async def comand_help(message: types.Message):
	await message.answer(text = "Меню комманд у вас на клавиaтуре!", reply_markup=kb_help_client)

@dp.message_handler(commands=['расписание'])
async def comand_timetable(message: types.Message):
	await message.answer('''Работаем с 8:00 до 20:00.
Без обедов!''', reply_markup= ReplyKeyboardRemove())

@dp.message_handler(commands=['меню'])
async def comand_menu_client(message: types.Message):
	await message.answer('МЕНЮ:', reply_markup= ReplyKeyboardRemove())
	await api_pizza_db.db_view_client_menu_command(message)

@dp.message_handler(commands=['адрес'])
async def comand_address(message: types.Message):
	await message.answer('ул.Колбаскина, дом 15', reply_markup= ReplyKeyboardRemove())

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('заказ'))
async def dell_item(callback_query: types.CallbackQuery):
	name_price = tuple(callback_query.data.replace('заказ ', '').split(' '))
	global list_product
	list_product.append(name_price)
	print(list_product)
	await callback_query.answer(f'{name_price[0]} добавленна', show_alert=True)
