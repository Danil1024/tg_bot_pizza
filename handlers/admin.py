from states import FSMmakingPizza
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from filters import IntFilter
from utils.db_api import api_pizza_db


async def start_making_pizza(message: types.Message):
	await FSMmakingPizza.photo.set()
	await message.reply(text='Загрузите фото')

async def load_photo(message: types.Message, state=FSMmakingPizza.photo):
	async with state.proxy() as data:
		data['photo'] = message.photo[0].file_id
	await FSMmakingPizza.next()
	await message.reply(text='Введите название')

async def load_name(message: types.Message, state=FSMmakingPizza.name):
	async with state.proxy() as data:
		data['name'] = message.text
	await FSMmakingPizza.next()
	await message.reply(text='Введите описание')

async def load_description(message: types.Message, state=FSMmakingPizza.description):
	async with state.proxy() as data:
		data['description'] = message.text
	await FSMmakingPizza.next()
	await message.reply(text='Введите цену')

async def load_price(message: types.Message, state=FSMmakingPizza.price):
	async with state.proxy() as data:
		data['price'] = float(message.text)
	await api_pizza_db.db_add_menu_command(state)
	await state.finish()

async def close_making_pizza(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.reply(text='Создание было прервано!')

def register_handlers_admin(dp: Dispatcher):
	dp.register_message_handler(start_making_pizza, commands=['создать'])
	dp.register_message_handler(load_photo, content_types=['photo'], state=FSMmakingPizza.photo)
	dp.register_message_handler(load_name, state=FSMmakingPizza.name)
	dp.register_message_handler(load_description, state=FSMmakingPizza.description)
	dp.register_message_handler(load_price, IntFilter(), state=FSMmakingPizza.price)
	dp.register_message_handler(close_making_pizza, commands= 'отмена', state='*')
