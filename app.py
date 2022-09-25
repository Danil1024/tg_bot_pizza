from aiogram.utils import executor
from loader import dp, bot


async def on_startup(_):
	from utils.db_api import api_pizza_db
	import filters
	api_pizza_db.db_start()
	filters.setup(dp)
	print('Бот успешно запустился')

from handlers import admin, client, other

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)
other.register_handlers_other(dp)


if __name__ == '__main__':
	executor.start_polling(dp, on_startup=on_startup)