from loader import dp
from aiogram import types
import string, json


@dp.message_handler()
async def other_message(message: types.Message):
	send_message = await message.answer('''Команда не распознана.
Введите /help что-бы узнать все комманды''')
	await message.delete()
