from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from data import config


class AdminFilter(BoundFilter):
	async def check(self, message: types.Message):
		return message.from_user.id in [int(i) for i in config.ADMINS.split(' ')]