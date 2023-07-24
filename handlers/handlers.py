from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU as ru
import filters.filters as f
from config import ALLOW_USERS
from model import extract_and_fit
from model import dt
import warnings

warnings.filterwarnings('ignore')

router=Router()
global model
global current_price

@router.message(~f.IsAdmin(ALLOW_USERS))
async def permission_denied(msg: Message):
    print(msg.from_user.id)
    await msg.reply(ru['denied'])

@router.message(Command(commands=['start']))
async def start(msg: Message):
    current_price = []
    await msg.answer(ru['start_welcome'])


async def show_prices_text(current,msg:Message, count,hour=0.5):
    message = f'Курс BTC-USD за прошлые {count*hour} часа:\n'
    now = dt.datetime.now()
    delta = dt.timedelta(minutes=30)
    for i in range(1,count+1):
        message+=f'Цена за {str((now-i*delta).time())}: {current[f"lag_{i}h"].iloc[0]}\n'
    await msg.answer(message)



@router.message(Command(commands=['get']))
async def rate(msg: Message):
    await msg.answer('Собираю и обрабатываю данные...')
    start = dt.datetime.now()
    model, current = extract_and_fit('30m',16)
    current_price = current
    end = dt.datetime.now()
    await msg.answer(str(end-start))
    await show_prices_text(current_price, msg, 8)




@router.message(Command(commands=['predict']))
async def predict(msg: Message):
    print(len(current_price),current_price)
    if len(current_price)==0:
        await msg.answer('Вы ещё не получили данные. Нажмите /get')
    else:
        new_price = model.predict(current_price)[0]
        await msg.answer(f'Цена через 30 минут: {new_price}')



@router.message(Command(commands=['visualize']))
async def visualize(msg: Message):
    await msg.answer(ru['visualize'])



@router.message(Command(commands=['settings']))
async def settings(msg: Message):
    await msg.answer(ru['settings'])
