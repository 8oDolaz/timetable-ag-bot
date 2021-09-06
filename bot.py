from database import connect_to_db, disconnect

import telebot
import json
import config
import datetime


# Таблицы в базе данных

# таблица day_info
# lesson_time, lesson_title, lesson_type, day,                stream
# 10:00–14:00, Алгебра,      Очно,        четверг, 2 сентября 303263

# таблица user_info
# c1, c2
# c1 -- id пользователя в телеграм, c2 -- класс пользователя


def get_date(date):
    # date -- datetime.datetime.now()

    # возвращает дату в формате "вторник, 1", "среда, 2" и т.д.
    # получаем индекс дня в неделе, потом этот индекс используем в массиве с названием дней недели
    # получаем дату (день) и берем

    # номер дня в неделе
    day_in_week = date.isoweekday() - 1
    # дата (день)
    date = date.strftime('%d')
    # убираем первый ноль, если он есть
    date = date[1:] if date[0] == '0' else date
    # получаем название дня, которое находится под индексом day_in_week
    return config.days[day_in_week] + ', ' + date


def get_all_info_day(cursor, day, stream):
    # cursor -- подключение к базе данных
    # day -- "вторник, 1" строка
    # stream -- значение по ключу (streams_info.json) число

    # возвращает 4 массива: время урока, название предмета, дата, тип занятия (соответственно)
    # тип урока в боте не отображается, т.к. в расписании это не соответствует реальности,
    # но возможность не была убрана

    cursor.execute('''
    SELECT * FROM day_info WHERE
    (position(%s IN day_info.day) > 0 AND day_info.stream=%s)
    ''', (day, stream,))

    time, title, _day, type = [], [], [], []
    info = cursor.fetchall()

    for i in range(len(info)):
        time.append(info[i][0])
        title.append(info[i][1])
        type.append(info[i][2])
        _day.append(info[i][3])
    # в каждый массив записываются соответствующее столбцы

    return time, title, _day, type


def prepare_answer(info, date):
    #

    # возвращает сообщение для одного дня строкой
    # Вторник, 1 сентября
    # 10:00-14:00 Алгебра
    # ...

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
    bot = telebot.TeleBot(config.token)

    keyboard = config.main_keyboard

    # заранее созданная клавиатура

    @bot.message_handler(func=lambda message: True, commands=['start'])
    # стартовая команда бота
    def start(message):
        # здесь, как и в дальнейшем,
        # message -- объект, который содержит всю информацию о сообщении и чате

        connection, cursor = connect_to_db()
        # подключение к базе данных

        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (message.chat.id,))
        if len(cursor.fetchall()) == 0:
            # пользователь не указывал класс
            bot.send_message(message.chat.id, config.instruction)
        else:
            # такой пользователь уже указывал класс
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его нажмите на кнопку)',
                             reply_markup=keyboard)

        disconnect(connection, cursor)
        # отключение от базы данных. все время быть подлюченным нельзя, т.к. соединение рвется

    @bot.message_handler(func=lambda message: True, commands=['info'])
    # информация о боте
    def info(message):
        bot.send_message(message.chat.id,
                         config.info)

    # основная функция бота, показывающая расписание
    @bot.message_handler(func=lambda message: True, content_types=['text'])  # все наши команды выводят текст
    def main_bot(message):
        connection, cursor = connect_to_db()
        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s;', (message.chat.id,))

        if len(cursor.fetchall()) != 0:
            # такой пользователь уже существует
            cursor.execute('''
            SELECT c2 FROM user_info WHERE c1=%s;
            ''', (message.chat.id,))
            user_stream = cursor.fetchall()[0][0]

            if message.text.lower() in ['сегодня', 'завтра']:
                date = datetime.datetime.today()

                if message.text.lower() == 'сегодня':
                    date_for_db = get_date(date)
                    # эта функция возвращает все нужное

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)
                    # здесь мы получаем всю необходимую инфу

                    # подгатавливаем наш ответ
                    answer_today = prepare_answer(day_info, date)

                    bot.send_message(message.chat.id,
                                     answer_today,
                                     reply_markup=keyboard)  # отправляем сообщение

                elif message.text.lower() == 'завтра':

                    date = date + datetime.timedelta(days=1)
                    date_for_db = get_date(date)

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)

                    answer_tomorrow = prepare_answer(day_info, date)

                    bot.send_message(message.chat.id,
                                     answer_tomorrow,
                                     reply_markup=keyboard)

            elif message.text.lower() == 'на неделю':
                for delta in range(7):  # здесь мы пускаем цикл как-бы по дням недели
                    date = (datetime.datetime.today() + datetime.timedelta(days=delta))
                    date_for_db = get_date(date)

                    day_info = get_all_info_day(cursor, date_for_db, user_stream)

                    answer = prepare_answer(day_info, date)

                    bot.send_message(message.chat.id,
                                     answer,
                                     reply_markup=keyboard)

            elif message.text.lower() == 'сменить класс':
                cursor.execute('''DELETE FROM USER_INFO WHERE c1=%s;''',
                               (message.chat.id,))  # delete this user from db

                bot.send_message(message.chat.id,
                                 config.instruction)
            else:  # если пользователь не выбрал предложенные функции
                bot.send_message(message.chat.id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard)
        else:
            # если у нас нет такого пользователя
            with open('streams_info.json', 'r') as file:
                stream = message.text.lower()
                if not stream[-1].isdigit():
                    stream += '1'

                stream = (json.load(file)).get(stream)
                file.close()

            if stream is not None:  # если такой поток существует
                cursor.execute('INSERT INTO USER_INFO(c1, c2) VALUES(%s, %s);',
                               (message.chat.id, stream,))

                bot.send_message(message.chat.id,
                                 config.text_after_change,
                                 reply_markup=keyboard)
            else:  # если пользователь ввел поток неправильно
                bot.send_message(message.chat.id,
                                 config.instruction)

        disconnect(connection, cursor)

    bot.polling(none_stop=True)
    # запускаем бота


if __name__ == '__main__':
    main()
