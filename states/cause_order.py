from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMcauseOrder(StatesGroup):
	cause_start = State()
	cause_finish = State()
	