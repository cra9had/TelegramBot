from settings import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from api import Api

import asyncio


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
server1_id = 104
server2_id = 136
current_server_id = 0
api = Api()
white_list = [11871421639, 558669472, 494870154, 1140197457]


@dp.message_handler(Text(equals="Назад"))
@dp.message_handler(commands="start")
async def start(message: types.Message):
    if message.from_user.id not in white_list:
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1️⃣Сервер1", "2️⃣Сервер2", "❓Статус", "⚠Аварийное выключение"]
    keyboard.add(*buttons)
    await message.answer("Выберете действие", reply_markup=keyboard)


@dp.message_handler(Text(equals="❓Статус"))
async def status(message: types.Message):
    status1 = api.get_server_status(server1_id)
    await asyncio.sleep(0.2)
    status2 = api.get_server_status(server2_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")

    await message.reply(f"Сервер 1: {status1}\nСервер 2: {status2}", reply_markup=keyboard)


@dp.message_handler(Text(equals="⚠Аварийное выключение"))
async def gather_reboot(message: types.Message):
    api.change_power_status(server1_id, "power_reset")
    await asyncio.sleep(0.2)
    api.change_power_status(server2_id, "power_reset")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")

    await message.reply(f"Серверы перезагружены", reply_markup=keyboard)


@dp.message_handler(Text(equals="1️⃣Сервер1"))
async def server1(message: types.Message):
    global current_server_id
    server_status = api.get_server_status(server1_id)
    current_server_id = server1_id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if server_status == "on":
        buttons = ["Выключить", "Перезагрузить", "Назад"]
    else:
        buttons = ["Включить", "Перезагрузить", "Назад"]
    keyboard.add(*buttons)
    await message.answer("Что будем делать ?", reply_markup=keyboard)


@dp.message_handler(Text(equals="2️⃣Сервер2"))
async def server2(message: types.Message):
    global current_server_id
    current_server_id = server2_id
    server_status = api.get_server_status(server2_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if server_status == "on":
        buttons = ["Выключить", "Перезагрузить", "Назад"]
    else:
        buttons = ["Включить", "Перезагрузить", "Назад"]
    keyboard.add(*buttons)
    await message.answer("Что будем делать ?", reply_markup=keyboard)


@dp.message_handler(Text(equals="Выключить"))
async def turn_off(message: types.Message):
    api.change_power_status(current_server_id, "power_off")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно выключен", reply_markup=keyboard)


@dp.message_handler(Text(equals="Включить"))
async def turn_on(message: types.Message):
    api.change_power_status(current_server_id, "power_on")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно включен", reply_markup=keyboard)


@dp.message_handler(Text(equals="Перезагрузить"))
async def reset(message: types.Message):
    api.change_power_status(current_server_id, "power_reset")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно перезагружен", reply_markup=keyboard)


if __name__ == "__main__":
    api.auth()
    executor.start_polling(dp, skip_updates=True)
