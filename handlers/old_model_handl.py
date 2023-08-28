from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from model import extract_and_fit
from model import dt
from model import pd
import warnings
import seaborn as sns
from matplotlib.pyplot import clf
from settings import id2settings

warnings.filterwarnings('ignore')

oldmodel_router=Router()


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
        plot_2 = sns.lineplot(x = pd.to_datetime(lags.iloc[-2:].index), y = lags.iloc[-2:], color='red')
        plot_2.figure.savefig('fig_old.jpg')
        clf()



@oldmodel_router.message(Command(commands=['get_old']))
async def rate(msg: Message):
    global current_price
    global predicted_value
    await msg.answer('<em>Собираю и обрабатываю данные...</em>')
    start = dt.datetime.now()
    current_price, predicted_value = await extract_and_fit('30m',16,id2settings[msg.from_user.id]['pair'])
    end = dt.datetime.now()
    await msg.answer('Затратилось времени на сбор данных: '+str(end-start))
    await show_prices_text_old(current_price, msg, 10)
    await msg.answer('Теперь вы можете нажать либо /predict_old, либо /visualize_old')



@oldmodel_router.message(Command(commands=['predict_old']))
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
