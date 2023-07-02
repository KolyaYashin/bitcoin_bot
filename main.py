from main_menu import set_main_menu
from create_bot import dp, bot
from handlers.handlers import router

if __name__=='__main__':
    dp.startup.register(set_main_menu)
    dp.include_router(router=router)
    dp.run_polling(bot)
