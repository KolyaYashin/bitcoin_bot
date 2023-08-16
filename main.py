from main_menu import set_main_menu
from create_bot import dp, bot
from handlers.handlers import router
from settings import id2settings
from config import ALLOW_USERS

if __name__=='__main__':
    for id in ALLOW_USERS:
        if not (id in id2settings):
            id2settings[id]={}
            id2settings[id]['pair'] = 'BTCUSDT'
            id2settings[id]['state'] = 'in_menu'
    dp.startup.register(set_main_menu)
    dp.include_router(router=router)
    dp.run_polling(bot)
