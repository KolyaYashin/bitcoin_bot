from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU as ru
import filters.filters as f
from config import ALLOW_USERS
import warnings
from settings import id2settings
from keyboard.buttons import settings_keyboard
from settings import every_pair_set, usdt_pairs_set

warnings.filterwarnings('ignore')

general_router=Router()

@general_router.message(~f.IsAdmin(ALLOW_USERS))
async def permission_denied(msg: Message):
    print(msg.from_user.id)
    await msg.reply(ru['denied'])

@general_router.message(Command(commands=['start']))
async def start(msg: Message):
    await msg.answer(ru['start_welcome'])


@general_router.message(Command(commands=['settings']))
async def settings(msg: Message):
    await msg.answer(ru['settings'], reply_markup = settings_keyboard)


@general_router.callback_query(Text(text=['to_pair_change']))
async def pair_change(callback: CallbackQuery):
    id2settings[callback.from_user.id]['state'] = 'in_pair_change'
    await callback.message.answer('Напишите валютную пару, на которую хотите изменить. Сейчас выбрана - '
                                f'{id2settings[callback.from_user.id]["pair"]}.')
    await callback.answer()

@general_router.callback_query(Text(text=['to_threshold_change']))
async def pair_change(callback: CallbackQuery):
    id2settings[callback.from_user.id]['state'] = 'in_threshold_change'
    await callback.message.answer('Введите, насколько должен произойти скачок в процентах, чтобы вам пришло уведомление. \nCейчас выбрано - '
                                f'{id2settings[callback.from_user.id]["threshold"]}.')
    await callback.answer()


@general_router.message(f.InPairChange(id2settings))
async def in_pair_change(message: Message):
    new_pair = message.text.upper()
    id2settings[message.from_user.id]['state'] = 'in_menu'
    if new_pair in every_pair_set:
        id2settings[message.from_user.id]['pair'] = new_pair
        await message.answer('Новая валютная пара успешно добавлена!')
    else:
        await message.answer('Такой пары нет(\n Нажмите на /all_pairs или /usdt_pairs чтобы посмотреть список доступных пар')


@general_router.message(f.InThresholdChange(id2settings))
async def in_threshold_change(message: Message):
    try:
        new_threshold = float(message.text)
        id2settings[message.from_user.id]['state'] = 'in_menu'
        id2settings[message.from_user.id]['threshold'] = new_threshold
        await message.answer('Вы успешно поменяли!')
    except ValueError:
        await message.answer('Вы ввели не число. Попробуйте ещё раз')




@general_router.message(Command(commands=['all_pairs','usdt_pairs']))
async def show_list(msg: Message):
    if msg.text.split('/')[0]=='all_pairs':
        await msg.answer('Первые 20 пар:\n'+'\n'.join(every_pair_set[:20]))
    else:
        await msg.answer('Первые 20 пар:\n'+'\n'.join(usdt_pairs_set[:20]))
