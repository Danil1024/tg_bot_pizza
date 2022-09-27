from .int_filter import IntFilter
from .admin_filter import AdminFilter
from aiogram import Dispatcher

def setup(dp: Dispatcher):
	dp.filters_factory.bind(IntFilter)
	dp.filters_factory.bind(AdminFilter)
