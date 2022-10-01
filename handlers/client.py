from loader import dp
from aiogram import types
from keyboards import kb_help_client
from utils.db_api import api_pizza_db
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states import FSMmakingOrder
from aiogram.dispatcher import FSMContext
from utils.db_api import api_pizza_db


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

# добавление еды в корзину
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('заказ'))
async def comand_add_item(callback_query: types.CallbackQuery):
	name_price = callback_query.data.replace('заказ ', '').split(':')
	global list_product
	list_product.append(name_price)
	print(list_product)
	await callback_query.answer(f'{name_price[0]} добавленна', show_alert=True)

# просмотр корзины
@dp.message_handler(commands=['корзина'])
async def comand_view_basket(message: types.Message):
	if list_product:
		summ = float()
		for k in list_product:
			summ += float(k[1])
		for i in list_product:
			name = i[0]
			await message.answer(text= f'{name}, {i[-1]}', reply_markup= InlineKeyboardMarkup(row_width=1)\
				.add(InlineKeyboardButton(f'убрать из корзины {name}', callback_data=f'убрать из корзины {name}')))
		await message.answer(text= f'ценна за все : {summ}', reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
			.add(KeyboardButton('/заказать')).add(KeyboardButton('/очистить_корзину'))\
				.add(KeyboardButton('/меню')).add(KeyboardButton('/корзина')))
	else:
		await message.answer(text= 'корзина пуста')

# удаление из корзины
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('убрать из корзины'))
async def comand_dell_item(callback_query: types.CallbackQuery):
	name_ = callback_query.data.replace('убрать из корзины ', '')
	global list_product
	print(name_)
	for i in list_product:
		if name_ in i:
			i.clear()
			list_product = [ele for ele in list_product if ele != []]
			break
	print(list_product)
	await callback_query.answer(f'{name_} убрано', show_alert=True)

# полное очишение корзины
@dp.message_handler(commands=['очистить_корзину'])
async def comand_clear_basket(message: types.Message):
	global list_product
	list_product = []
	await message.answer(text= 'корзина очищенна')


@dp.message_handler(commands=['заказать'])
async def comand_start_making_order(message: types.Message):
	if list_product:
		await message.answer(text= '''Внимание мы работаем только по городу Бишкек.
Введите пожалуйста ваш адрес (улица.дом.квартира)
Введите пожалуйста мобильный телефон по которому с вами сможет связаться курьер''')
		await FSMmakingOrder.adress_and_phone.set()
	else:
		await message.answer(text= 'Вы нечего не добавили в корзину!')


@dp.message_handler(state=FSMmakingOrder.adress_and_phone)
async def check_adress_and_phone(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['adress_and_phone'] = message.text
	await message.answer(text= 'Все правильно?\n' + message.text,\
		reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton(text= '/Да_все_верно')).add(KeyboardButton(text= '/Изменить_адрес_или_телефон')))
	await FSMmakingOrder.next()

@dp.message_handler(commands= 'Да_все_верно', state=FSMmakingOrder.check_adress_and_phone)
async def write_order_bd(message: types.Message, state: FSMContext):
	name = f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.username}' 
	global list_product
	str_product = str()
	summ = float()
	for i in list_product:
		str_product += ' ' + str(i)
		summ += float(i[1])
	async with state.proxy() as date:
		adres_and_phone = date['adress_and_phone']
	await api_pizza_db.db_add_order_command(name, str_product, summ, adres_and_phone, message.from_user.id)
	await state.finish()
	list_product = []
	summ = 0.0
	await message.answer(text= 'Ваш заказ в режиме ожидание когда его примут вам вышлют сообщение',\
		reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton(text= '/мои_заказы')))

@dp.message_handler(commands= 'Изменить_адрес_или_телефон', state=FSMmakingOrder.check_adress_and_phone)
async def comand_change_adres_and_phone_order(message: types.Message, state: FSMContext):
	await state.finish()
	if list_product:
		await message.answer(text= '''Внимание мы работаем только по городу Бишкек.
Введите пожалуйста ваш адрес (улица.дом.квартира)
Введите пожалуйста мобильный телефон по которому с вами сможет связаться курьер''')
		await FSMmakingOrder.adress_and_phone.set()
@dp.message_handler(commands= ['мои_заказы'])
async def user_menu_order_command(message: types.Message):
	await api_pizza_db.user_menu_order(message.from_user.id)

@dp.callback_query_handler(lambda x: 'отменить заказ:' in x.data)
async def user_cause_order(callback_query: types.CallbackQuery):
	if await api_pizza_db.check_order(callback_query.data.split(':')[1]) != []:
		id_order = callback_query.data.split(':')[1]
		id_user = callback_query.data.split(':')[2]
		await api_pizza_db.delete_one_order(id_order)
		await callback_query.answer('Заказ удален', show_alert=True)
	else:
		await callback_query.answer('Заказ уже был удален!', show_alert=True)
