import telebot
import json
import config
import datetime
from functions import *


def main():

    bot = telebot.TeleBot(config.token)  # бот с нашим токеном

    keyboard = config.keyboard1  # импортируем клавиатуру

    @bot.message_handler(func=lambda message: True, commands=['start'])  # стартовая комманда бота
    def start(message):
        connection, cursor = connect_to_db()  # в дальнейшем так мы будем подкючаться к дб

        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (message.chat.id,))
        if len(cursor.fetchall()) == 0:  # если у нас нет такого пользователя
            bot.send_message(message.chat.id, config.instruction)
        else:  # если у нас он уже есть
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его нажмите на кнопку)',
                             reply_markup=keyboard)

        disconnect(connection, cursor)  # а так мы будем отключаться от нее

    # основная функция бота, показывающая расписание
    @bot.message_handler(func=lambda message: True, content_types=['text'])  # все наши команды выводят текст
    def main_bot(message):
        connection, cursor = connect_to_db()
        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (message.chat.id,))

        if len(cursor.fetchall()) != 0:  # если у нас есть таккой пользователь

            if message.text.lower() == 'сегодня':  # дальше так мы будем обрабатывать команды

                connection, cursor = connect_to_db()

                # берем сегодняшнюю дату
                date = datetime.datetime.today()
                # смотрим, воскресенье это или нет
                date = (date + datetime.timedelta(days=1)) if date.isoweekday() == 7 else date
                date = get_date(date)  # эта функция возвращает все нужное

                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                day_info = get_all_info_day(cursor, date, user_stream)  # здесь мы получаем всю необходимую инфу

                # здесь мы подготавливаем наш ответ
                answer_today = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_today,
                                 reply_markup=keyboard)  # отправляем сообщение

            elif message.text.lower() == 'завтра':

                connection, cursor = connect_to_db()
                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]  # так мы получаем поток на котором учиться польщователь

                # берем сегодняшнюю дату
                date = (datetime.datetime.today() + datetime.timedelta(days=1))
                # смотрим, воскресенье это или нет
                date = (date + datetime.timedelta(days=1)) if date.isoweekday() == 1 else date
                date = get_date(date)

                day_info = get_all_info_day(cursor, date, user_stream)

                answer_tomorrow = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_tomorrow,
                                 reply_markup=keyboard)

            elif message.text.lower() == 'на неделю':

                connection, cursor = connect_to_db()

                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                for delta in range(0, 7):  # здесь мы пускаем цикл как-бы по дням недели
                    date = (datetime.datetime.today() + datetime.timedelta(days=delta))
                    if date.isoweekday() != 7:  # если день —— не воскресенье
                        date = get_date(date)

                        day_info = get_all_info_day(cursor, date, user_stream)

                        answer = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                        bot.send_message(message.chat.id,
                                         answer,
                                         reply_markup=keyboard)

                disconnect(connection, cursor)
            elif message.text.lower() == 'сменить класс':  # до этого были команды, которые выводили расписание, но эта немного другая
                connection, cursor = connect_to_db()
                cursor.execute('''DELETE FROM USER_INFO WHERE c1=%s;''',
                               (message.chat.id,))  # delete this user from db
                disconnect(connection, cursor)
                bot.send_message(message.chat.id,
                                 config.instruction)
            else:  # если пользователь не выбрал предложенные функции
                bot.send_message(message.chat.id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard)
        else:
            # если у нас нет такого пользователя
            with open('streams_info.json', 'r') as file:
                stream = (json.load(file)).get(message.text.lower())  # json.load(file) возвращает нам словарь
                file.close()

            if stream is not None:  # если такой поток существует
                cursor.execute('INSERT INTO USER_INFO(c1, c2) VALUES(%s, %s);',
                               (message.chat.id, stream,))

                disconnect(connection, cursor)
                bot.send_message(message.chat.id,
                                 config.text_after_change,
                                 reply_markup=keyboard)
            else:  # если пользователь ввел поток неправильно
                bot.send_message(message.chat.id,
                                 config.instruction)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
