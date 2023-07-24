from aiogram import Bot
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot):
    main_menu_commands=[
        BotCommand(command='start', description=LEXICON_RU['start_d']),
        BotCommand(command='get', description=LEXICON_RU['get_d']),
        BotCommand(command='predict', description=LEXICON_RU['predict_d']),
        BotCommand(command='visualize', description=LEXICON_RU['vis_d']),
        BotCommand(command='settings', description=LEXICON_RU['settings_d'])
    ]

    await bot.set_my_commands(main_menu_commands)