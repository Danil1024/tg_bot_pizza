import sqlite3 as sq
from aiogram import types
from loader import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def db_start():
	global base, cur
	base = sq.connect('pizza_db')
	cur = base.cursor()
	if base:
		print('Подключенно к базе данных')
	base.execute('CREATE TABLE IF NOT EXISTS menu(photo TEXT,\
				name TEXT PRIMARY KEY, description TEXT, price TEXT)')
	base.commit()

async def db_add_menu_command(state):
	async with state.proxy() as date:
		cur.execute('INSERT INTO menu VALUES(?, ?, ?, ?)', tuple(date.values()))
		base.commit()

async def db_view_admin_menu_command(message: types.Message):
	for pizza in cur.execute('SELECT * FROM menu').fetchall():
		await bot.send_photo(chat_id= message.from_user.id,
							 photo= pizza[0],
							 caption= f'Название: {pizza[1]}\nОписание: {pizza[2]}\nЦена: {pizza[-1]}')
		await message.answer(text= '^^^', reply_markup= InlineKeyboardMarkup(row_width=1)\
			.add(InlineKeyboardButton(f'удалить {pizza[1]}', callback_data=f'удалить {pizza[1]}')))
			
async def db_view_client_menu_command(message: types.Message):
	for pizza in cur.execute('SELECT * FROM menu').fetchall():
		await bot.send_photo(chat_id= message.from_user.id,
							 photo= pizza[0],
							 caption= f'Название: {pizza[1]}\nОписание: {pizza[2]}\nЦена: {pizza[-1]}')
		await message.answer(text= '^^^', reply_markup= InlineKeyboardMarkup(row_width=1)\
			.add(InlineKeyboardButton(f'заказать {pizza[1]}', callback_data=f'заказ {pizza[1]} {pizza[-1]}')))
	# дописать клаву

async def db_dellete_menu_command(name):
	cur.execute('DELETE FROM menu WHERE name = ?', (name,))
	base.commit()

	
