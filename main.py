from settings import TOKEN, TG_PASSWORD
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from peewee import *
from api import Api

import asyncio


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = SqliteDatabase('sqlite.db')
server1_id = 104
server2_id = 136
current_server_id = 0
api = Api()


class User(Model):
    id = CharField()
    is_auth = BooleanField(default=False)

    class Meta:
        database = db


def is_auth(func):
    async def wrapper(message: types.Message):
        user_id = message.from_user.id
        user, _ = User.get_or_create(id=str(user_id))
        if user.is_auth:
            await func(message)
    return wrapper


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("Введите пароль")


@dp.message_handler(lambda message: len(message.text) == len(TG_PASSWORD))
async def auth(message: types.Message):
    user, _ = User.get_or_create(id=str(message.from_user.id))
    if message.text == TG_PASSWORD:
        user.is_auth = True
        user.save()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Главная")
        await message.answer("Вы успешно авторизировались!", reply_markup=keyboard)


@dp.message_handler(Text(equals="Главная"))
@dp.message_handler(Text(equals="Назад"))
@is_auth
async def main(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1️⃣Сервер1", "2️⃣Сервер2", "❓Статус", "⚠Аварийное выключение"]
    keyboard.add(*buttons)
    await message.answer("Выберете действие", reply_markup=keyboard)


@dp.message_handler(Text(equals="❓Статус"))
@is_auth
async def status(message: types.Message):
    status1 = api.get_server_status(server1_id)
    await asyncio.sleep(0.2)
    status2 = api.get_server_status(server2_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")

    await message.reply(f"Сервер 1: {status1}\nСервер 2: {status2}", reply_markup=keyboard)


@dp.message_handler(Text(equals="⚠Аварийное выключение"))
@is_auth
async def gather_power_off(message: types.Message):
    api.change_power_status(server1_id, "power_off")
    await asyncio.sleep(0.2)
    api.change_power_status(server2_id, "power_off")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")

    await message.reply(f"Серверы перезагружены", reply_markup=keyboard)


@dp.message_handler(Text(equals="1️⃣Сервер1"))
@is_auth
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
@is_auth
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
@is_auth
async def turn_off(message: types.Message):
    api.change_power_status(current_server_id, "power_off")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно выключен", reply_markup=keyboard)


@dp.message_handler(Text(equals="Включить"))
@is_auth
async def turn_on(message: types.Message):
    api.change_power_status(current_server_id, "power_on")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно включен", reply_markup=keyboard)


@dp.message_handler(Text(equals="Перезагрузить"))
@is_auth
async def reset(message: types.Message):
    api.change_power_status(current_server_id, "power_reset")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    await message.answer("Сервер успешно перезагружен", reply_markup=keyboard)


if __name__ == "__main__":
    db.connect()
    api.auth()
    executor.start_polling(dp, skip_updates=True)
