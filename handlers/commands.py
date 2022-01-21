import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as fmt

from constants import ADMIN_PIN
from config import config
from sender import send_to_chat


logger = logging.getLogger(__name__)


class SetSalersForm(StatesGroup):
    waitText = State() # wait text input

class SetChatIdForm(StatesGroup):
    waitText = State() # wait text input

    
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()  
    await message.reply("Приветствую! К сожалению, я могу общаться только со своим хозяином!")

async def cmd_get_config(message: types.Message, state: FSMContext):
    await state.finish()  
    if not config.chat_id or not config.user_map:
        await message.reply(f"Бот пока не настроен! Используйте команды /set_salers_{ADMIN_PIN} и /set_chat_{ADMIN_PIN}")
    else:
        mappings = ""
        for k, v in config.user_map.items():
            mappings += f"{k} -> {v}\n"

        await message.reply(
            f"Рабочий чат: {config.chat_id}\n"
            f"Соответствия:\n{mappings}"
        )

async def cmd_set_salers(message: types.Message, state: FSMContext):
    await state.finish()  
    await message.reply("Введите соответствие типов доставки и контактов сотрудников")
    await SetSalersForm.waitText.set()

async def cmd_set_chat(message: types.Message, state: FSMContext):
    await state.finish()  
    await message.reply("1. Получите id рабочего чата с помощью @getidsbot\n2. Пришлите мне id\n3. Добавьте меня в чат")
    await SetChatIdForm.waitText.set()


async def callback_set_chat(message: types.Message, state: FSMContext):
    try:
        cid = int(message.text)
        config.chat_id = cid
        await send_to_chat("Получил доступ к чату!")
        await message.reply(f"Чат {cid} установлен, проверьте сообщение от бота")
    except:
        await message.reply("Ошибка! Попробуйте еще раз!")
    await state.finish()

async def callback_set_salers(message: types.Message, state: FSMContext):
    def pairwise(iterable):
        "s -> (s0, s1), (s2, s3), (s4, s5), ..."
        a = iter(iterable)
        return zip(a, a)

    try:
        lines = message.text.splitlines()
        salers = {}
        for k, v in pairwise(lines):
            logging.info(f"Add {k} -> {v}")
            salers[str(k)] = str(v)
        config.user_map = salers

        msg = f"Соответствие установлено:\n"
        for k, v in config.user_map.items():
            msg += f"{k} -> {v}"
        await message.reply(msg)
    except:
        await message.reply("Ошибка! Попробуйте еще раз!")
    await state.finish()


def reg_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")

    dp.register_message_handler(cmd_get_config, commands=f"get_config_{ADMIN_PIN}", state="*")
    dp.register_message_handler(cmd_set_salers, commands=f"set_salers_{ADMIN_PIN}", state="*")
    dp.register_message_handler(cmd_set_chat, commands=f"set_chat_{ADMIN_PIN}", state="*")

    dp.register_message_handler(callback_set_chat, state=SetChatIdForm.waitText)
    dp.register_message_handler(callback_set_salers, state=SetSalersForm.waitText)
