from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU as ru
import filters.filters as f
from config import ALLOW_USERS
from model import extract_and_fit
from model import dt
from model import pd
from model_upgrade import extract_data
import warnings
import seaborn as sns
from create_bot import bot
from aiogram.types import FSInputFile

warnings.filterwarnings('ignore')

router=Router()

@router.message(~f.IsAdmin(ALLOW_USERS))
async def permission_denied(msg: Message):
    print(msg.from_user.id)
    await msg.reply(ru['denied'])

@router.message(Command(commands=['start']))
async def start(msg: Message):
    await msg.answer(ru['start_welcome'])


async def show_prices_text_old(current,msg:Message, count,hour=0.5):
    sns.set()
    if hour==0.5:
        message = f'Курс BTC-USD за прошлые {count*hour} часов:\n'
        now = dt.datetime.now()
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
        sns.lineplot(x = pd.to_datetime(lags.iloc[:-1].index), y = lags.iloc[:-1],color="blue")
        plot_2 = sns.lineplot(x = pd.to_datetime(lags.iloc[-2:].index), y = lags.iloc[-2:], color='red')
        plot_2.figure.savefig('fig_old.jpg')

async def show_prices(y,msg: Message, count):
    sns.set()
    message = f'Курс BTC-USD за прошлые {count/12} часов:\n'
    for j,i in enumerate(reversed(y.iloc[-count-6:-6].index)):
        if j%6==0:
            message+=f'Курс за {str(i)}: {y[i]}\n'
    await msg.answer(message)
    sns.lineplot(y.iloc[-6-count:-6])
    plot_2 = sns.lineplot(y.iloc[-7:])
    plot_2.figure.savefig('fig.jpg')



@router.message(Command(commands=['get_old']))
async def rate(msg: Message):
    global current_price
    global predicted_value
    await msg.answer('Собираю и обрабатываю данные...')
    start = dt.datetime.now()
    current_price, predicted_value = extract_and_fit('30m',16)
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices_text_old(current_price, msg, 10)
    await msg.answer('Теперь вы можете нажать либо /predict_old, либо /visualize_old')

@router.message(Command(commands='get'))
async def rate_new(msg: Message):
    await msg.answer('Собираю и обрабатываю данные...')
    start = dt.datetime.now()
    global y
    y=extract_data()
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices(y,msg,12*5)
    await msg.answer('Теперь вы можете нажать либо /predict, либо /visualize')





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
            message+=f'За полчаса произошло повышение на {(new_price/old_price-1)*100} процентов.'
        else:
            message+=f'За полчаса произошло понижение на {-(new_price/old_price-1)*100} процентов.'
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
    await msg.answer(ru['settings'])
