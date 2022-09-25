from .int_filter import IntFilter 
from aiogram import Dispatcher

def setup(dp: Dispatcher):
	dp.filters_factory.bind(IntFilter)
