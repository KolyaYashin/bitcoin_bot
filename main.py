from main_menu import set_main_menu
from create_bot import dp, bot
import handlers
from settings import id2settings
from config import ALLOW_USERS


if __name__=='__main__':
    for id in ALLOW_USERS:
        if not (id in id2settings):
            id2settings[id]={}
            id2settings[id]['pair'] = 'BTCUSDT'
            id2settings[id]['state'] = 'in_menu'
            id2settings[id]['threshold'] = 0.2
    dp.startup.register(set_main_menu)
    dp.include_router(router=handlers.general_handl.general_router)
    dp.include_router(router=handlers.model_handl.model_router)
    dp.include_router(router=handlers.old_model_handl.oldmodel_router)
    dp.run_polling(bot)
