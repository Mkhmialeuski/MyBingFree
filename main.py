from EdgeGPT import Chatbot
from key import api_key
from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup
import pandas as pd
import sqlite3


def send_excel_file(file_path, chat_id):
    with open(file_path, 'rb') as file:
        bot.sendDocument(chat_id, file)


def output():
    conn = sqlite3.connect('mydatabase.db')
    query = "SELECT * FROM posr;"
    df = pd.read_sql_query(query, conn)
    df.to_excel('output.xlsx', index=False)


def base_user():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id_user int,
    ueser_name varchar)""")

    l = []
    cur.execute("SELECT * FROM users")
    for person in cur.fetchall():
        l.append(person[0])
    cur.close()
    return l


def base_post():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS posr(
    id_user int,
    user_name varchar,
    message varchar)""")


def inse_post(id, name, messag):
    con = sqlite3.connect("mydatabase.db")
    cursor = con.cursor()
    cursor.execute(f"""INSERT INTO posr (id_user, user_name, message) VALUES ('{id}', '{name}', '{messag}')""")
    con.commit()


def inser(id, name):
    con = sqlite3.connect("mydatabase.db")
    cursor = con.cursor()
    cursor.execute(f"""INSERT INTO users (id_user, ueser_name) VALUES ('{id}', '{name}')""")
    con.commit()


telegram_token = api_key


async def bing_chat(prompt):
    # Функция получения ответа от BingAI с использованием cookies.
    gbot = Chatbot(cookiePath='cookies.json')
    response_dict = await gbot.ask(prompt=prompt)
    return response_dict['item']['messages'][1]['text'].replace("[^\\d^]", "")


bot = Bot(telegram_token)
dp = Dispatcher(bot)
l = base_user()
file_path = 'output.xlsx'
chat_id1 = 812031098


@dp.message_handler(lambda message: message.from_user.id != bot.id)
async def send(message: types.Message):
    global l, chat_id
    chat_id = message.from_user.id
    try:
        prompt = message.text
        if message.from_user.id not in l:
            await message.answer('Вас нет в базе данных')
            menu_default = ReplyKeyboardMarkup(resize_keyboard=True)
            menu_default.row("Зарегистрироваться", "Не хочу")
            await message.answer('Вам нужно дать свои данные, для регистрации', reply_markup=menu_default)

            if message.text == 'Зарегистрироваться':
                inser(message.from_user.id, message.from_user.first_name)
                await message.answer('Вы зарегистрированы. Пишите запрос, для бота')
                l = base_user()
            elif message.text == 'Не хочу':
                await message.answer('Вам нужно пройти регистрацию')

        else:
            if not prompt:
                await message.answer('Вы задали пустой запрос.')
            else:
                inse_post(message.from_user.id, message.from_user.first_name, message.text)
                # await message.answer('Ожидание ответа на ваш запрос...')
                bot_response = await bing_chat(prompt=prompt)

                menu_default = ReplyKeyboardMarkup(resize_keyboard=True)
                menu_default.row("Экспорт в Excel всех запросов")
                await message.answer('Подготовка ответа', reply_markup=menu_default)
                await message.answer(bot_response, parse_mode="markdown")

                if message.text == 'Экспорт в Excel всех запросов':
                    output()
                    doc = open(('output') + '.xlsx', 'rb')
                    await message.reply_document(doc)

    except Exception as ex:
        await message.answer(f'BingAI не хочет общаться с Вами, ошибка: {ex}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
