from aiogram import Bot
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot):
    main_menu_commands=[
        BotCommand(command='get', description=LEXICON_RU['get_d']),
        BotCommand(command='show', description=LEXICON_RU['show']),
        BotCommand(command='predict', description=LEXICON_RU['predict_d']),
        BotCommand(command='visualize', description=LEXICON_RU['vis_d']),
        BotCommand(command='get_old', description=LEXICON_RU['get_d']),
        BotCommand(command='predict_old', description=LEXICON_RU['predict_d']),
        BotCommand(command='visualize_old', description=LEXICON_RU['vis_d']),
        BotCommand(command='settings', description=LEXICON_RU['settings_d']),
        BotCommand(command='current', description='Получить текущую цену биткоина')
    ]

    await bot.set_my_commands(main_menu_commands)