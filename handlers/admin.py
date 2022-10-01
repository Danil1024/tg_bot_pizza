from states import FSMmakingPizza, FSMcauseOrder
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from filters import IntFilter, AdminFilter
from utils.db_api import api_pizza_db
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

id_order = str()
id_user = str()

# запись новой еды в базу данных
@dp.message_handler(AdminFilter(), commands=['создать'])
async def start_making_pizza(message: types.Message):
	await FSMmakingPizza.photo.set()
	await message.reply(text='Загрузите фото',\
		reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton(text= '/отменить_создание')))

@dp.message_handler(AdminFilter(), content_types=['photo'], state=FSMmakingPizza.photo)
async def load_photo(message: types.Message, state=FSMmakingPizza.photo):
	async with state.proxy() as data:
		data['photo'] = message.photo[0].file_id
	await FSMmakingPizza.next()
	await message.reply(text='Введите название')

@dp.message_handler(AdminFilter(), commands= 'отменить_создание', state='*')
async def close_making_pizza(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.reply(text='Создание было прервано!')

@dp.message_handler(AdminFilter(), state=FSMmakingPizza.name)
async def load_name(message: types.Message, state=FSMmakingPizza.name):
	async with state.proxy() as data:
		data['name'] = message.text
	await FSMmakingPizza.next()
	await message.reply(text='Введите описание')

@dp.message_handler(AdminFilter(), state=FSMmakingPizza.description)
async def load_description(message: types.Message, state=FSMmakingPizza.description):
	async with state.proxy() as data:
		data['description'] = message.text
	await FSMmakingPizza.next()
	await message.reply(text='Введите цену')

@dp.message_handler(AdminFilter(), IntFilter(), state=FSMmakingPizza.price)
async def load_price(message: types.Message, state=FSMmakingPizza.price):
	async with state.proxy() as data:
		data['price'] = float(message.text)
	await api_pizza_db.db_add_menu_command(state)
	await message.reply(text='Успешно создано')
	await state.finish()

@dp.callback_query_handler(AdminFilter(), lambda x: 'удалить' in x.data)
async def dell_item(callback_query: types.CallbackQuery):
	name = callback_query.data.replace('удалить ', '')
	await api_pizza_db.db_dellete_menu_command(name)
	await callback_query.answer(f'{name} удалена', show_alert=True)

@dp.message_handler(AdminFilter(), commands=['admin_menu'])
async def comand_admin_menu(message: types.Message):
	await message.answer('МЕНЮ:')
	await api_pizza_db.db_view_admin_menu_command(message)

@dp.message_handler(commands=['управление_заказами'])
async def comand_view_basket(message: types.Message):
	await message.answer(text= 'Меню управления заказами',\
		reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)\
			.add(KeyboardButton('/Ожидающие')).add(KeyboardButton('/Выполняются'))\
				.add(KeyboardButton('/Завершенные')))

# просмотр заказов в разных состояниях
@dp.message_handler(AdminFilter(), commands=['Ожидающие'])
async def view_pending_orders_command(message: types.Message):
	await message.answer('Ожидающие заказы: ')
	await api_pizza_db.view_pending_orders(message)
	
@dp.message_handler(AdminFilter(), commands=['Выполняются'])
async def view_accepted_orders_command(message: types.Message):
	await message.answer('Выполняются сейчас: ')
	await api_pizza_db.view_accepted_orders(message)

@dp.message_handler(AdminFilter(), commands=['Завершенные'])
async def view_completed_orders_command(message: types.Message):
	await message.answer('Выполнены: ')
	await api_pizza_db.view_completed_orders(message)
	
# изменение состояния заказа
@dp.callback_query_handler(AdminFilter(), lambda x: 'заказ_принят:' in x.data)
async def order_accepted(callback_query: types.CallbackQuery):
	id_order = callback_query.data.split(':')[1]
	id_user = callback_query.data.split(':')[2]
	await bot.send_message(chat_id=id_user, text='Ваш заказ был принят\nОжидайте')
	await api_pizza_db.update_order(id_order)
	await callback_query.answer('Успешно', show_alert=True)
	
@dp.callback_query_handler(AdminFilter(), lambda x: 'заказ_выполнен:' in x.data)
async def completed_orders(callback_query: types.CallbackQuery):
	id_order = callback_query.data.split(':')[1]
	await api_pizza_db.close_order(id_order)
	await callback_query.answer('Успешно', show_alert=True)

# отказ в заказе
@dp.callback_query_handler(AdminFilter(), lambda x: 'отказан:' in x.data)
async def cause_order_start(callback_query: types.CallbackQuery):
	if await api_pizza_db.check_order(callback_query.data.split(':')[1]) != []:
		global id_user
		global id_order
		id_order = callback_query.data.split(':')[1]
		id_user = callback_query.data.split(':')[2]
		await FSMcauseOrder.cause_start.set()
		await callback_query.answer(text= 'Напишите причину отказа: ', show_alert=True)
	else:
		await callback_query.answer(text= 'Уже удален', show_alert=True)

@dp.message_handler(state=FSMcauseOrder.cause_start)
async def cause_order_change(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['id_user'] = id_user
		data['id_order'] = id_order
		data['cause'] = message.text
	await message.answer(text= 'Продолжить?\n' + message.text,\
		reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton(text= '/продолжить_отмену')).add(KeyboardButton(text= '/прекратить_отмену')))
	await FSMcauseOrder.next()

@dp.message_handler(commands= 'продолжить_отмену', state=FSMcauseOrder.cause_finish)
async def cause_order_finish(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		cause = data['cause'] 
		await bot.send_message(chat_id= data['id_user'],\
		text=f'Заказ не принят по причине: {cause}')
		await message.answer('Заказ был отменен',reply_markup= ReplyKeyboardRemove())
		await api_pizza_db.delete_one_order(data['id_order'])	
	await state.finish()

@dp.message_handler(commands= 'прекратить_отмену', state=FSMcauseOrder.cause_finish)
async def cause_order_break(message: types.Message, state: FSMContext):
	await message.answer('Заказ не был отменен',reply_markup= ReplyKeyboardRemove())
	await state.finish()

@dp.message_handler(commands= 'очистить_выполненые_заказы')
async def clear_completed_orders(message: types.Message):
	await api_pizza_db.delete_all_orders()
	await message.answer('Выполненые заказы были удаленны',reply_markup= ReplyKeyboardRemove())

@dp.message_handler(commands= 'help_admin')
async def clear_completed_orders(message: types.Message):
	await message.answer('комады администратора: ',\
		reply_markup= ReplyKeyboardMarkup(resize_keyboard=True)\
		.add(KeyboardButton(text= '/очистить_выполненые_заказы'))\
		.add(KeyboardButton(text= '/управление_заказами'))\
		.add(KeyboardButton(text= '/admin_menu')).add(KeyboardButton(text= '/создать')))
