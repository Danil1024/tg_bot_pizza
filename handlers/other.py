from loader import dp
from aiogram import types, Dispatcher
import string, json


async def other_message(message: types.Message):
	send_message = await message.answer('''Команда не распознана.
Введите /help что-бы узнать все комманды''')
	await message.delete()
	print(send_message)


def register_handlers_other(dp: Dispatcher):
	dp.register_message_handler(other_message)