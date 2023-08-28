from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU as ru
import filters.filters as f
from config import ALLOW_USERS
from model import extract_and_fit
from model import dt
from model import pd
from model_upgrade import extract_data
import warnings
import seaborn as sns
from aiogram.types import FSInputFile
from matplotlib.pyplot import clf
from settings import id2settings
from keyboard.buttons import settings_keyboard
from settings import every_pair_set, usdt_pairs_set
import asyncio
from create_bot import bot
import requests

warnings.filterwarnings('ignore')

model_router=Router()

#start endless loop which starts model every 5 minutes
@model_router.message(Command(commands=['go']))
async def go(msg:Message):
    while True:
        minutes = 5
        global y
        y=await extract_data(id2settings[msg.from_user.id]['pair'])
        draw_figure('fig.jpg',12*5,6)
        old_price = y.iloc[-7]
        new_price = y.iloc[-1]
        change_percent = (1-new_price/old_price)*100
        change_percent_abs = abs(change_percent)
        for id in ALLOW_USERS:
            if change_percent_abs>id2settings[id]['threshold']:
                if change_percent<0:
                    await bot.send_message(id,f'В ближайшие полчаса ожидается повышение на {change_percent_abs:.{3}} процентов')
                else:
                    await bot.send_message(id,f'В ближайшие полчаса ожидается понижение на {change_percent:.{3}} процентов')
        await asyncio.sleep(minutes*60-15)



def draw_figure(name,count,predict_count):
    sns.lineplot(y.iloc[-predict_count-count:-predict_count])
    plot_2 = sns.lineplot(y.iloc[-predict_count-1:])
    plot_2.figure.savefig(name)
    clf()

async def show_current_price(msg: Message):
    now = dt.datetime.now().time().replace(microsecond=0)
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
    await msg.answer(f'Цена за {now}: <b>{response.json()["price"]:.8}</b>')

async def show_prices(y,msg: Message, count):
    sns.set()
    message = ''
    for _,i in enumerate(reversed(y.iloc[-count-6:-6].index)):
        message+=f'Курс за {str(i.time().replace(microsecond=0))}: <b>{y[i]}</b>\n'
    await msg.answer(message)
    show_current_price(msg)
    draw_figure('fig.jpg',12*count,6)


@model_router.message(Command(commands='get'))
async def rate_new(msg: Message):
    await msg.answer('<em>Собираю и обрабатываю данные...</em>')
    start = dt.datetime.now()
    global y
    y=await extract_data(id2settings[msg.from_user.id]['pair'])
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices(y,msg,12)
    await msg.answer('Теперь вы можете нажать либо /predict, либо /visualize')

@model_router.message(Command(commands=['show']))
async def show(msg: Message):
    try:
        await show_prices(y,msg,6)
        await msg.answer('Теперь вы можете нажать либо /predict, либо /visualize')
    except NameError:
        await msg.answer('Вы ещё не получили данные. Нажмите /get')


@model_router.message(Command(commands=['current']))
async def show_current(msg: Message):
    await show_current_price(msg)



@model_router.message(Command(commands=['predict']))
async def predict_price(msg: Message):
    try:
        old_price = y.iloc[-7]
        new_price = y.iloc[-1]
        message = 'Ожидаемый курс на следующие полчаса:\n'
        for i in range(1,7):
            message+=f'Предсказанная цена за {y.index[-i]} - {y.iloc[-i]}.\n'
        if new_price>old_price:
            message+=f'За полчаса произойдёт повышение на {(new_price/old_price-1)*100} процентов.'
        else:
            message+=f'За полчаса произойдёт понижение на {-(new_price/old_price-1)*100} процентов.'
        await msg.answer(message)
    except NameError:
        await msg.answer('Вы ещё не получили данные. Нажмите /get')



@model_router.message(Command(commands=['visualize_old']))
async def visualize(msg: Message):
    photo=FSInputFile('fig_old.jpg')
    await msg.answer_photo(photo)


@model_router.message(Command(commands=['visualize']))
async def visualize(msg: Message):
    photo=FSInputFile('fig.jpg')
    await msg.answer_photo(photo)
