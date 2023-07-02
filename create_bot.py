from config import TOKEN
from aiogram import Bot
from aiogram import Dispatcher

bot: Bot = Bot(token = TOKEN, parse_mode='HTML')
dp: Dispatcher = Dispatcher()