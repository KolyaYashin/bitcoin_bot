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

router=Router()

@router.message(~f.IsAdmin(ALLOW_USERS))
async def permission_denied(msg: Message):
    print(msg.from_user.id)
    await msg.reply(ru['denied'])

@router.message(Command(commands=['start']))
async def start(msg: Message):
    await msg.answer(ru['start_welcome'])

@router.message(Command(commands=['go']))
async def go(msg:Message):
    ban = 0
    while True:
        ban-=1
        minutes = 5
        global y
        y=await extract_data(id2settings[msg.from_user.id]['pair'])
        draw_figure('fig.jpg',12*5,6)
        old_price = y.iloc[-7]
        new_price = y.iloc[-1]
        change_percent = (1-new_price/old_price)*100
        change_percent_abs = abs(change_percent)
        for id in ALLOW_USERS:
            if change_percent_abs>id2settings[id]['threshold'] and ban<=0:
                if change_percent<0:
                    ban=3
                    await bot.send_message(id,f'В ближайшие полчаса ожидается повышение на {change_percent:.{3}} процентов')
                else:
                    ban=3
                    await bot.send_message(id,f'В ближайшие полчаса ожидается понижение на {change_percent:.{3}} процентов')
        await asyncio.sleep(minutes*60-15)


async def show_prices_text_old(current,msg:Message, count,hour=0.5):
    sns.set()
    if hour==0.5:
        message = f'Курс BTC-USD за прошлые {count*hour} часов:\n'
        now = dt.datetime.now()
        #now = now + dt.timedelta(hours=3)
        if now.minute>=30:
            now = now.replace(minute=30,second=0,microsecond=0)
        else:
            now = now.replace(minute=0,second=0,microsecond=0)
        delta = dt.timedelta(minutes=30)
        _lags={}
        for i in range(count,0,-1):
            message+=f'Цена за {str((now-(i-1)*delta).time())}: {current[f"lag_{i}h"].iloc[0]}\n'
            _lags[str((now-(i-1)*delta).time())] = current[f"lag_{i}h"].iloc[0]
        await msg.answer(message)
        _lags[str((now+delta).time())] = predicted_value
        lags=pd.Series(_lags)
        lags.index = pd.to_datetime(lags.index)
        sns.lineplot(x = pd.to_datetime(lags.iloc[:-1].index), y = lags.iloc[:-1],color="blue")
        try:
            sns.lineplot(y.iloc[-6-count*6:-6])
            plot_2 = sns.lineplot(y.iloc[-7:])
        except NameError:
            pass
        plot_2 = sns.lineplot(x = pd.to_datetime(lags.iloc[-2:].index), y = lags.iloc[-2:], color='red')
        plot_2.figure.savefig('fig_old.jpg')
        clf()


def draw_figure(name,count,predict_count):
    sns.lineplot(y.iloc[-predict_count-count:-predict_count])
    plot_2 = sns.lineplot(y.iloc[-predict_count-1:])
    plot_2.figure.savefig(name)
    clf()


async def show_prices(y,msg: Message, count):
    sns.set()
    message = f'Курс BTC-USD за прошлые {count/12} часов:\n'
    for j,i in enumerate(reversed(y.iloc[-count-6:-6].index)):
        if j==0:
            message+=f'Курс за {str(i)}: {y[i]}\n'
    await msg.answer(message)

    now = dt.datetime.now().time()
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
    await msg.answer(f'Цена за {now}: {response.json()["price"]}')
    draw_figure('fig.jpg',count,6)



@router.message(Command(commands=['get_old']))
async def rate(msg: Message):
    global current_price
    global predicted_value
    await msg.answer('Собираю и обрабатываю данные...')
    start = dt.datetime.now()
    current_price, predicted_value = await extract_and_fit('30m',16,id2settings[msg.from_user.id]['pair'])
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices_text_old(current_price, msg, 10)
    await msg.answer('Теперь вы можете нажать либо /predict_old, либо /visualize_old')

@router.message(Command(commands='get'))
async def rate_new(msg: Message):
    await msg.answer('Собираю и обрабатываю данные...')
    start = dt.datetime.now()
    global y
    y=await extract_data(id2settings[msg.from_user.id]['pair'])
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices(y,msg,12*5)
    await msg.answer('Теперь вы можете нажать либо /predict, либо /visualize')

@router.message(Command(commands=['show']))
async def show(msg: Message):
    try:
        await show_prices(y,msg,12*2)
        await msg.answer('Теперь вы можете нажать либо /predict, либо /visualize')
    except NameError:
        await msg.answer('Вы ещё не получили данные. Нажмите /get')




@router.message(Command(commands=['predict_old']))
async def predict(msg: Message):
    try:
        new_price = predicted_value
        old_price = current_price['lag_1h'].iloc[0]
        if new_price>old_price:
            await msg.answer(f'Ожидаемая цена через 30 минут: {new_price}, повышение на {(new_price/old_price-1)*100} процентов.')
        else:
            await msg.answer(f'Ожидаемая цена через 30 минут: {new_price}, понижение на {-(new_price/old_price-1)*100} процентов.')
    except NameError:
        await msg.answer('Вы ещё не получили данные. Нажмите /get')


@router.message(Command(commands=['predict']))
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



@router.message(Command(commands=['visualize_old']))
async def visualize(msg: Message):
    photo=FSInputFile('fig_old.jpg')
    await msg.answer_photo(photo)


@router.message(Command(commands=['visualize']))
async def visualize(msg: Message):
    photo=FSInputFile('fig.jpg')
    await msg.answer_photo(photo)


@router.message(Command(commands=['settings']))
async def settings(msg: Message):
    await msg.answer(ru['settings'], reply_markup = settings_keyboard)


@router.callback_query(Text(text=['to_pair_change']))
async def pair_change(callback: CallbackQuery):
    id2settings[callback.from_user.id]['state'] = 'in_pair_change'
    await callback.message.answer('Напишите валютную пару, на которую хотите изменить. Сейчас выбрана - '
                                f'{id2settings[callback.from_user.id]["pair"]}.')
    await callback.answer()

@router.callback_query(Text(text=['to_threshold_change']))
async def pair_change(callback: CallbackQuery):
    id2settings[callback.from_user.id]['state'] = 'in_threshold_change'
    await callback.message.answer('Введите, насколько должен произойти скачок в процентах, чтобы вам пришло уведомление. \nCейчас выбрано - '
                                f'{id2settings[callback.from_user.id]["threshold"]}.')
    await callback.answer()


@router.message(f.InPairChange(id2settings))
async def in_pair_change(message: Message):
    new_pair = message.text.upper()
    id2settings[message.from_user.id]['state'] = 'in_menu'
    if new_pair in every_pair_set:
        id2settings[message.from_user.id]['pair'] = new_pair
        await message.answer('Новая валютная пара успешно добавлена!')
    else:
        await message.answer('Такой пары нет(\n Нажмите на /all_pairs или /usdt_pairs чтобы посмотреть список доступных пар')


@router.message(f.InThresholdChange(id2settings))
async def in_threshold_change(message: Message):
    try:
        new_threshold = float(message.text)
        id2settings[message.from_user.id]['state'] = 'in_menu'
        id2settings[message.from_user.id]['threshold'] = new_threshold
        await message.answer('Вы успешно поменяли!')
    except ValueError:
        await message.answer('Вы ввели не число. Попробуйте ещё раз')




@router.message(Command(commands=['all_pairs','usdt_pairs']))
async def show_list(msg: Message):
    if msg.text.split('/')[0]=='all_pairs':
        await msg.answer('Первые 20 пар:\n'+'\n'.join(every_pair_set[:20]))
    else:
        await msg.answer('Первые 20 пар:\n'+'\n'.join(usdt_pairs_set[:20]))
