from states import FSMmakingPizza
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from filters import IntFilter, AdminFilter
from utils.db_api import api_pizza_db


@dp.message_handler(AdminFilter(), commands=['создать'])
async def start_making_pizza(message: types.Message):
	await FSMmakingPizza.photo.set()
	await message.reply(text='Загрузите фото')

@dp.message_handler(AdminFilter(), content_types=['photo'], state=FSMmakingPizza.photo)
async def load_photo(message: types.Message, state=FSMmakingPizza.photo):
	async with state.proxy() as data:
		data['photo'] = message.photo[0].file_id
	await FSMmakingPizza.next()
	await message.reply(text='Введите название')

@dp.message_handler(AdminFilter(), commands= 'отмена', state='*')
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

@dp.message_handler(AdminFilter(), commands=['admin_menu'])
async def comand_menu(message: types.Message):
	await message.answer('МЕНЮ:')
	await api_pizza_db.db_view_admin_menu_command(message)

@dp.callback_query_handler(AdminFilter(), lambda x: x.data and x.data.startswith('удалить'))
async def dell_item(callback_query: types.CallbackQuery):
	name = callback_query.data.replace('удалить ', '')
	await api_pizza_db.db_dellete_menu_command(name)
	await callback_query.answer(f'{name} удалена', show_alert=True)

