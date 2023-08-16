from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU

to_pair_change_button = InlineKeyboardButton(text=LEXICON_RU['to_pair_change'],callback_data='to_pair_change')
settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[[to_pair_change_button]])