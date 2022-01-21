import asyncio
import logging 

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from constants import TOKEN
from sender import binder as sender_binder
import handlers.commands as cmd
import handlers.manager as manager
import server as webhook_server


# logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger.warning("Starting bot")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать")
    ]
    await bot.set_my_commands(commands)


async def main():
    logger.warning("Starting main")

    loop = asyncio.get_event_loop()
    bot = Bot(TOKEN, loop)
    logger.warning((await bot.get_me()).username)

    # MemoryStorage, лучше взять что-то другое (Redis, Memcached)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    # reg all handlers
    cmd.reg_handlers_commands(dp)
    manager.reg_handlers_manager(dp)
    sender_binder.bind_bot(bot)

    # set bot's visible commands
    await set_commands(bot)

    # run webhook server
    loop.create_task(webhook_server.run(manager.new_order_callback))

    # skip accumulated updates and poll
    await dp.skip_updates()  
    await dp.start_polling()
    logging.warning("Bot stoped!")


# entry point 
if __name__ == '__main__':
    asyncio.run(main())

    

