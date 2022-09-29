from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMmakingOrder(StatesGroup):
	adress_and_phone = State()
	check_adress_and_phone = State()
	