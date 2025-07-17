import re

import telebot
from telebot.types import Message

from dotenv import load_dotenv
import os
from datetime import date
import schedule
import time
from threading import Thread

from info import *
from keyboard import create_keyboard
from db import *
from user_time import *


logging.basicConfig(
    filename=LOG_NAME,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

create_db()
create_table()
run_periodically()


@bot.message_handler(commands=['start'])
def say_start(message: Message) -> None:
    bot.send_message(message.chat.id, GREETING, reply_markup=create_keyboard(['/help', '/schedule']))


@bot.message_handler(commands=['help'])
def say_help(message: Message) -> None:
    bot.send_message(message.chat.id, TEXT_HELP, reply_markup=create_keyboard(['/today', '/tomorrow']))


@bot.message_handler(commands=['schedule'])
def send_schedule(message: Message) -> None:
    bot.send_message(message.chat.id, TEXT_SCHEDULE)


# Создает напоминание, записывает его в базу данных и сразу же устанавливает время, когда его отправить
@bot.message_handler(commands=['add'])
def add_new_reminder(message: Message) -> None:
    # Парсим сообщение
    match = re.match(r'/add\s+(\S.*)\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', message.text.strip())

    # Если команда была введена корректно
    if match:
        event_name, event_date, event_time = match.groups()
        # Если время было введено правильно.
        if check_time(f"{event_date} {event_time}") == True:
            insert_row(message.chat.id, event_name, event_date, event_time)

            # Создаем напоминание.
            result_time = reduce_by_hour(event_time)
            date_time_str = datetime.strptime(f"{event_date} {result_time}", "%Y-%m-%d %H:%M")
            task = schedule.every().day.at(date_time_str.strftime("%H:%M")).do(send_reminder,
                                                                               message.chat.id, event_name)
            task.job_func.max_runs = 1
            task.next_run = date_time_str

            bot.send_message(message.chat.id, "Напоминание успешно записано!",
                             reply_markup=create_keyboard(['/help', '/today']))

        # Если назначенное событие состоится меньше, чем через час.
        elif check_time(f"{event_date} {event_time}") == INCORRECT_DATE_3:
            insert_row(message.chat.id, event_name, event_date, event_time)
            bot.send_message(message.chat.id, INCORRECT_DATE_3)

        else:
            logging.info(f'Некорректно введена дата {message.chat.id}')
            bot.send_message(message.chat.id, check_time(f"{event_date} {event_time}"))

    else:
        # Отправляем сообщение пользователю, если формат неверный
        bot.send_message(message.chat.id, INCORRECT_DATE_4)


@bot.message_handler(commands=['today'])
def send_today(message: Message) -> None:
    list = check_schedule(message.chat.id, date.today().strftime("%Y-%m-%d"))
    if not list:
        bot.send_message(message.chat.id, "На сегодня нет запланированных дел.")
    else:
        msg = "Список напоминаний на сегодня:"
        for i in list:
            msg += f"\n {i[0]} — {i[1]} {i[2]}"
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['tomorrow'])
def send_tomorrow(message: Message) -> None:
    tomorrow = (datetime.now() + timedelta(days=1)).date().strftime("%Y-%m-%d")
    list = check_schedule(message.chat.id, tomorrow)
    if not list:
        bot.send_message(message.chat.id, "На завтра нет запланированных дел.")
    else:
        msg = "Список напоминаний на завтра:"
        for i in list:
            msg += f"\n {i[0]} — {i[1]} {i[2]}"
        bot.send_message(message.chat.id, msg)


# Отправляет напоминание.
def send_reminder(user_id: int, event_name: str) -> None:
    bot.send_message(user_id, f"Через час состоится событие: {event_name}")


# Запускает бесконечный цикл для отправки напоминаний.
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    thread = Thread(target=run_scheduler)
    thread.start()
    bot.polling()

