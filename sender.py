import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as fmt

from config import config


logger = logging.getLogger(__name__)


class BotBinder():
    def __init__(self):
        pass

    def bind_bot(self, bot: Bot):
        self.bot = bot

    def get_bot(self):
        return self.bot


binder = BotBinder()


async def send_to_chat(message: str, kb: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()):
    bot = binder.get_bot()
    chat_id = config.chat_id
    if chat_id:
        try:
            await bot.send_message(chat_id, message, reply_markup=kb)
        except:
            logging.error(f"Could not send message to chat")
    else:
        logging.warning(f"Could not send message to chat cause chat_id not set")