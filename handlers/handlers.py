from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU as ru
import filters.filters as f
from config import ALLOW_USERS

router=Router()


@router.message(f.IsAdmin(ALLOW_USERS))
async def permission_denied(msg: Message):
    print(msg.from_user.id)
    await msg.reply(ru['denied'])

@router.message(Command(commands=['start']))
async def start(msg: Message):
    await msg.answer(ru['start_welcome'])




@router.message(Command(commands=['rate']))
async def rate(msg: Message):
    await msg.answer(ru['rate'])



@router.message(Command(commands=['predict']))
async def predict(msg: Message):
    await msg.answer(ru['predict'])



@router.message(Command(commands=['visualize']))
async def visualize(msg: Message):
    await msg.answer(ru['visualize'])



@router.message(Command(commands=['settings']))
async def settings(msg: Message):
    await msg.answer(ru['settings'])
