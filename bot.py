from database import connect_to_db, disconnect

import telebot
import json
import config
import datetime


# Tables in database

# day_info table:
# lesson_time,          lesson_title,        lesson_type,    day,                            stream
# 10:00–14:00::string,  Алгебра::string,     Очно::string,   четверг, 2 сентября::string     303263::int

# user_info table:
# c1 (id в telegram),   c2 (поток пользователя)
# 1218805540::int,      303263::int

# latest_message table:
# telegram_id,      message_date
# 1218805540::int   2021-09-14 15:20:18.000000::timestamp


def get_date(date):
    # Args:
    #   date -- datetime.datetime.now()

    # Returns:
    #   string = 'вторник, 1'; 'среда, 2' etc.

    # получаем индекс дня недели
    # создаем строку с датой (день)
    # возвращаем день недели по индексу с датой

    day_in_week = date.isoweekday() - 1
    date = date.strftime('%d')
    date = date[1:] if date[0] == '0' else date
    return config.days[day_in_week] + ', ' + date


def get_all_info_day(cursor, day, stream):
    # Args:
    #   cursor -- объект psycopg2, подключение к базе данных
    #   day -- "вторник, 1", string
    #   stream -- streams_info.json[stream], int

    # Returns:
    #   4 list: время урока, название предмета, дата, тип занятия

    cursor.execute('''
    SELECT * FROM day_info WHERE
    (position(%s IN day_info.day) > 0 AND day_info.stream=%s)
    ''', (day, stream,))

    time, title, _day, _type = [], [], [], []
    info = cursor.fetchall()

    for i in range(len(info)):
        time.append(info[i][0])
        title.append(info[i][1])
        _type.append(info[i][2])
        _day.append(info[i][3])

    return time, title, _day, _type


def prepare_answer(info, date):
    # Args:
    #   info -- 4 list, get_all_info_day()

    # Returns:
    #   string --
    #   Вторник, 1 сентября
    #   10:00-14:00 Алгебра
    #   ...

    date_str = get_date(date).strip().capitalize()
    if len(info[2]) != 0:
        day = info[2][0].strip().capitalize()
        time = info[0]
        title = info[1]

        ans = day + '\n'
        for item in range(len(time)):

            ans += time[item].strip() + ' ' + title[item].strip() + '\n'

    else:
        ans = date_str + ' ' + config.months[date.month - 1] + '\n'
        ans += 'Уроков нет!'

    return ans


def main():
    # Постоянно встречающийся параметр:
    #   message -- telegram response
    #   https://github.com/eternnoir/pyTelegramBotAPI#callback-query-handler

    bot = telebot.TeleBot(config.token)

    keyboard = config.main_keyboard

    @bot.message_handler(func=lambda message: True, commands=['start'])
    def start(message):
        connection, cursor = connect_to_db()

        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (message.chat.id,))
        if len(cursor.fetchall()) == 0:
            # пользователь еще не записан в базе данных
            bot.send_message(message.chat.id, config.instruction)
        else:
            # пользователь уже есть в базе данных
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его нажмите на кнопку)',
                             reply_markup=keyboard)

        disconnect(connection, cursor)

    @bot.message_handler(func=lambda message: True, commands=['info'])
    def info(message):
        bot.send_message(message.chat.id,
                         config.info)

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def main_bot(message):
        user_id = message.chat.id

        connection, cursor = connect_to_db()
        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (user_id,))

        if len(cursor.fetchall()) != 0:
            # пользователь есть в базе данных
            date = datetime.datetime.now()
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO latest_message (telegram_id, message_date)
                VALUES (%s::int, %s::timestamp)
            ON CONFLICT (telegram_id) DO
                UPDATE SET message_date = %s::timestamp;

            SELECT c2 FROM user_info WHERE c1=%s;
            ''', (
                user_id, date, date, user_id,
            ))
            user_stream = cursor.fetchall()[0][0]

            if message.text.lower() in ['сегодня', 'завтра']:
                date = datetime.datetime.today()

                if message.text.lower() == 'сегодня':
                    date_for_db = get_date(date)

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)

                    answer_today = prepare_answer(day_info, date)

                    bot.send_message(user_id,
                                     answer_today,
                                     reply_markup=keyboard)

                elif message.text.lower() == 'завтра':
                    date = date + datetime.timedelta(days=1)
                    date_for_db = get_date(date)

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)

                    answer_tomorrow = prepare_answer(day_info, date)

                    bot.send_message(user_id,
                                     answer_tomorrow,
                                     reply_markup=keyboard)

            elif message.text.lower() == 'на неделю':
                for delta in range(7):
                    date = (datetime.datetime.today() + datetime.timedelta(days=delta))
                    date_for_db = get_date(date)

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)

                    answer = prepare_answer(day_info, date)

                    bot.send_message(user_id,
                                     answer,
                                     reply_markup=keyboard)

            elif message.text.lower() == 'сменить класс':
                cursor.execute('''DELETE FROM USER_INFO WHERE c1=%s;''',
                               (user_id,))

                bot.send_message(user_id,
                                 config.instruction)
            else:
                bot.send_message(user_id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard)
        else:
            # пользователя нет в базе данных
            with open('streams_info.json', 'r') as file:
                stream = message.text.lower()
                if not stream[-1].isdigit():
                    stream += '1'

                stream = (json.load(file)).get(stream)
                file.close()

            if stream is not None:
                # указанный поток существует
                cursor.execute('INSERT INTO USER_INFO(c1, c2) VALUES(%s, %s);',
                               (user_id, stream,))

                bot.send_message(user_id,
                                 config.text_after_change,
                                 reply_markup=keyboard)
            else:
                # указанного потока не существует
                bot.send_message(user_id,
                                 config.instruction)

        disconnect(connection, cursor)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
