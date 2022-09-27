from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMmakingPizza(StatesGroup):
	photo = State()
	name = State()
	description = State()
	price = State()
	