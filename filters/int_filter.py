from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IntFilter(BoundFilter):
	async def check(self, message: types.Message):
		return message.text.isdigit()
