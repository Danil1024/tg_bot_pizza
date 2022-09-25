import sqlite3 as sq
from aiogram import types
from loader import bot


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

async def db_view_menu_command(message: types.Message):
	for pizza in cur.execute('SELECT * FROM menu').fetchall():
		await bot.send_photo(chat_id= message.from_user.id,
							 photo= pizza[0],
							 caption= f'Название: {pizza[1]}\nОписание: {pizza[2]}\nЦена: {pizza[-1]}')
