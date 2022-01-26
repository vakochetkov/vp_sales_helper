import asyncio
import logging

from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from aiogram.utils.callback_data import CallbackData
import aiogram.utils.markdown as fmt

from constants import WC_DATE_FORMAT, APP_DATE_FORMAT
from config import config
from utils import strfdelta
from sender import send_to_chat


logger = logging.getLogger(__name__)

cbFabOrder = CallbackData("order", "state")
states = [
    "Взять",
    "Завершить"
]


class Order(): 
    def __init__(self, data: dict) -> None:
        self.id = int(data.get("id", 0))
        self.total = int(data.get("total", 0))
        self.date = datetime.strptime(data.get("date_created", ""), WC_DATE_FORMAT).strftime(APP_DATE_FORMAT)

        self.customer = str(data.get("billing", {}).get("first_name", "")) + " " + str(data.get("billing", {}).get("last_name", ""))
        self.email = str(data.get("billing", {}).get("email", ""))
        self.phone = str(data.get("billing", {}).get("phone", ""))
        self.note = str(data.get("customer_note", ""))

        self.payment = str(data.get("payment_method_title", ""))
        self.shipping_type = str(data.get("shipping_lines", [])[0].get("method_title", ""))
        self.shipping_info = str(data.get("shipping", {}).get("city", ""))
        self.shipping_info += " " + str(data.get("shipping", {}).get("address_1", "")) 
        self.shipping_info += " " + str(data.get("shipping", {}).get("address_2", ""))
        
        self.products = []
        products = data.get("line_items", [])
        for p in products:
            text = "{} - {} - {}{}".format(
                p.get("name", ""), p.get("quantity", ""), p.get("total", ""), data.get("currency", "")
            )
            self.products.append(text)


def determine_salers(order: Order) -> str:
    for k, v in config.user_map.items():
        if str(k) in order.shipping_type:
            return str(v)
    return "@everyone"


def build_keyboard(state: str) -> types.InlineKeyboardMarkup:
    button = types.InlineKeyboardButton(text=state, 
        callback_data=cbFabOrder.new(state=state))

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(button) 
    return keyboard


async def send_order_message(data: dict):
    order = Order(data)
    salers = determine_salers(order)
    prods = ""
    state = ""

    for prod in order.products:
        prods += f"📦{prod}\n"

    message = f"{salers}\n"
    message += str(
        f"🆕НОВЫЙ\n"
        f"🏷️Заказ {order.id}\n"
        f"\n"
        f"🧑Покупатель: {order.customer} {order.email}\n"
        f"\n"
        f"☎️ {order.phone} ☎️\n"
        f"\n"
        f"✉️Доставка: {order.shipping_type} {order.shipping_info}\n"
        f"\n"
        f"{prods}"
        f"\n"
        f"💵Сумма заказа: {order.total}\n"
        f"\n"        
        f"📌Примечания к заказу: {order.note}\n"
        f"⌚Дата заказа: {order.date}\n"
    )

    kb = build_keyboard(states[0])
    await send_to_chat(message, kb)


async def callback_order_notified(call: types.CallbackQuery, callback_data: dict):
    # filter user
    uid = str(call.from_user.username)
    users = str(call.message.text.splitlines()[0])
    if uid in users or "@everyone" in users:
        # dispatch state
        state = str(callback_data["state"])
        if state == states[0]:
            msg = call.message.text.splitlines()
            msg[1] = "🔃В ОБРАБОТКЕ"
            text = '\n'.join(map(str, msg)) 
            await call.message.edit_text(
                str(f"\n{text}"), reply_markup=build_keyboard(states[1])
            )
        elif state == states[1]:
            msg = call.message.text.splitlines()
            started = datetime.strptime(msg[-1].split(":", maxsplit=1)[-1].strip(), APP_DATE_FORMAT)
            ended = datetime.now()
            delta = strfdelta(ended - started, "{H}ч {M}мин {S}сек")
            msg[1] = f"✅ЗАВЕРШЕН за {delta}"

            text = '\n'.join(map(str, msg)) 
            await call.message.edit_text(
                str(f"\n{text}"), reply_markup=types.InlineKeyboardMarkup()
            )
        else:
            logger.error(f"Invalid order callback with state {state}")
        await call.answer()
    else:
        await call.answer(text='Управлять заказом могут только назначенные продавцы', show_alert=True)


async def new_order_callback(data: dict) -> None:
    if not config.chat_id or not config.user_map:
        logger.error("Config is invalid, unable to handle new order")
    else:
        await send_order_message(data)


def reg_handlers_manager(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(callback_order_notified, cbFabOrder.filter())