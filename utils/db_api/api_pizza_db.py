import sqlite3 as sq
from aiogram import types
from loader import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import time


def db_start():
	global base, cur
	base = sq.connect('pizza_db')
	cur = base.cursor()
	if base:
		print('Подключенно к базе данных')
	base.execute('CREATE TABLE IF NOT EXISTS menu(photo TEXT,\
				name TEXT PRIMARY KEY, description TEXT, price TEXT)')
	base.execute('CREATE TABLE IF NOT EXISTS orders(name TEXT ,\
				 list_product TEXT, summ TEXT, time_order TEXT, adres_and_phone TEXT,\
				 status TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT)')
	base.commit()


# добовление еду в базу данных админом
async def db_add_menu_command(state):
	async with state.proxy() as date:
		cur.execute('INSERT INTO menu VALUES(?, ?, ?, ?)', tuple(date.values()))
		base.commit()

# просмотр админ_меню админов (с возможностью удалять)
async def db_view_admin_menu_command(message: types.Message):
	for pizza in cur.execute('SELECT * FROM menu').fetchall():
		await bot.send_photo(chat_id= message.from_user.id,
							 photo= pizza[0],
							 caption= f'Название: {pizza[1]}\nОписание: {pizza[2]}\nЦена: {pizza[-1]}')
		await message.answer(text= '^^^', reply_markup= InlineKeyboardMarkup(row_width=1)\
			.add(InlineKeyboardButton(f'удалить {pizza[1]}', callback_data=f'удалить {pizza[1]}')))

# просмотр меню пользователем
async def db_view_client_menu_command(message: types.Message):
	for pizza in cur.execute('SELECT * FROM menu').fetchall():
		await bot.send_photo(chat_id= message.from_user.id,
							 photo= pizza[0],
							 caption= f'Название: {pizza[1]}\nОписание: {pizza[2]}\nЦена: {pizza[-1]}')
		await message.answer(text= '^^^', reply_markup= InlineKeyboardMarkup(row_width=1)\
			.add(InlineKeyboardButton(f'заказать {pizza[1]}', callback_data=f'заказ {pizza[1]}:{pizza[-1]}')))
	await message.answer(text= '^^^', reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton('/корзина')))

# удаление еды из меню
async def db_dellete_menu_command(name):
	cur.execute('DELETE FROM menu WHERE name = ?', (name,))
	base.commit()

# создание нового заказа пользователем
async def db_add_order_command(name, list_product, summ, adres_and_phone, user_id):
	time_order = time.strftime('%B %d %A %H:%M.\n', time.localtime())
	cur.execute('INSERT INTO orders (name, list_product, summ, time_order, adres_and_phone, status, user_id)\
	VALUES(?, ?, ?, ?, ?, ?, ?)',\
		(name, list_product, summ, time_order,  adres_and_phone, 'pending', user_id))
	base.commit()

# просмотр заказов в разных состояниях
async def view_pending_orders(message: types.Message):
	for order in cur.execute('SELECT * FROM orders WHERE status="pending"').fetchall():
		await message.answer(text=f'''Имя заказчика: {order[0]}
Заказ: {order[1]}
Цена заказа: {order[2]}
Время заказа: {order[3]}
Адрес и телефон: {order[4]}''', reply_markup=InlineKeyboardMarkup(row_width=1)\
.add(InlineKeyboardButton(text='Принять заказ', callback_data=f'заказ_принят:{order[6]}:{order[7]}'))\
		.add(InlineKeyboardButton(text='Отказать!', callback_data=f'отказан:{order[6]}:{order[7]}')))
	base.commit()

async def view_accepted_orders(message: types.Message):
	for order in cur.execute('SELECT * FROM orders WHERE status="accepted"').fetchall():
		await message.answer(text=f'''Имя заказчика: {order[0]}
Заказ: {order[1]}
Цена заказа: {order[2]}
Время заказа: {order[3]}
Адрес и телефон: {order[4]}''', reply_markup=InlineKeyboardMarkup(row_width=1)\
.add(InlineKeyboardButton(text='заказ выполнен', callback_data=f'заказ_выполнен:{order[6]}')))
	base.commit()

async def view_completed_orders(message: types.Message):
	for order in cur.execute('SELECT * FROM orders WHERE status="completed"').fetchall():
		await message.answer(text=f'''Имя заказчика: {order[0]}
Заказ: {order[1]}
Цена заказа: {order[2]}
Время заказа: {order[3]}
Адрес и телефон: {order[4]}''')


# изменение состояния заказа
async def update_order(id_order):
	cur.execute('UPDATE orders set status= ? WHERE id = ?', ("accepted", id_order))
	base.commit()

async def close_order(id_order):
	cur.execute('UPDATE orders set status= ? WHERE id = ?', ("completed", id_order))
	base.commit()

# меню заказов пользователя
async def user_menu_order(user_id):
	for order in cur.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,)).fetchall():
		 await bot.send_message(chat_id= user_id, text=f'''Заказ: {order[1]}
Цена заказа: {order[2]}
Время заказа: {order[3]}
Адрес и телефон: {order[4]}''', reply_markup=InlineKeyboardMarkup(row_width=1)\
	.add(InlineKeyboardButton(text='отменить заказ',\
		callback_data=f'отменить заказ:{order[6]}:{user_id}')))
	base.commit() 

# удаление заказа из базы данных
async def delete_one_order(id_order):
	cur.execute('DELETE FROM orders WHERE id = ?', (id_order,))
	base.commit()
	
# проверка существует ли заказ
async def check_order(id_order):
	return cur.execute('SELECT * FROM orders WHERE id = ?', (id_order,)).fetchall()

async def delete_all_orders():
	cur.execute('DELETE FROM orders WHERE status = ?', ('completed',))
	base.commit()
