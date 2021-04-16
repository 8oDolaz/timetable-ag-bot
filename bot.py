import telebot
import json
import config
import datetime
import psycopg2 as ps2


def main():

    def get_date(date):
        # берем номер нашего дня в неделе
        day_in_week = date.isoweekday() - 1
        # берем дату это для
        date = date.strftime('%d')
        # если вначале есть 0, то убираем его
        date = date[1:] if date[0] == '0' else date
        # получаем финальное название дня
        return config.days[day_in_week] + ', ' + date

    def delete_spaces(string):
        # я не буду писать комментарий к каждой строке, но здесь мы сначала ищем первую букву с начала, а потом с конца
        # чтобы удалить все лишнее пробелы
        for i in range(len(string)):
            if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                string = string[i:]
                break

        for i in reversed(range(len(string))):
            if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                string = string[:i + 1]
                break

        return string

    def connect_to_db():  # это функция подключает нас к базе данных
        connection = ps2.connect(  # сюда мы передаем всё необходимое
            host='ec2-54-217-224-85.eu-west-1.compute.amazonaws.com',
            database='deocs7tolmvlhl',
            user='kvrovbpxebvygf',
            port=5432,
            password='2a9a8d39986ac9095ec905091708ba357a0df483caa195141ca5ae53bafc3628',
        )
        return connection, connection.cursor()

    def disconnect(connection, cursor):  # эта функция просто нас отключает
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_info_day(cursor, day, stream):  # это функция возвращает все что нужно для формирования сообщения
        cursor.execute('''
        select * from day_info where
        (position(%s in day_info.day) > 0 and day_info.stream=%s)
        ''', (day, stream,))

        time, title, _day, type = [], [], [], []
        info = cursor.fetchall()

        for i in range(len(info)):  # вот именно здесь мы записываем все необходимое
            time.append(info[i][0])
            title.append(info[i][1])
            type.append(info[i][2])
            _day.append(info[i][3])

        return time, title, _day, type

    def prepare_answer(day, time, title, place, s=''):  # здесь мы формируем само сообщение
        # day[0].upper() —— теперь первая буква заглавная!
        s += day[0].upper() + day[1:] + '\n'
        for item in range(len(time)):
            # Я не знаю где эта проблема, но пробелы я должен удалять здесь
            s += time[item].replace(' ', '') + ' ' + delete_spaces(
                title[item]) + '\n'  # ' '+ '('+delete_spaces(place[item])+')' + '\n'
            # Возможно, когда-то, я добавлю Очно или Дистанционо
        return s

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

                try:
                    answer_tomorrow = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                    disconnect(connection, cursor)

                    bot.send_message(message.chat.id,
                                     answer_tomorrow,
                                     reply_markup=keyboard)
                except IndexError:
                    bot.send_message(message.chat.id,
                                     'Сегодня нет уроков',
                                     reply_markup=keyboard)

            elif message.text.lower() == 'завтра':

                connection, cursor = connect_to_db()
                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]  # так мы получаем поток на котором учиться пользователь

                if datetime.datetime.today().isoweekday() != 7:
                    # берем завтрашнюю дату
                    date = (datetime.datetime.today() + datetime.timedelta(days=1))
                    # смотрим, воскресенье это или нет
                    date = (date + datetime.timedelta(days=1)) if date.isoweekday() == 7 else date
                    date = get_date(date)
                else:
                    date = (datetime.datetime.today() + datetime.timedelta(days=2))
                    date = get_date(date)

                day_info = get_all_info_day(cursor, date, user_stream)

                try:
                    answer_tomorrow = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                    disconnect(connection, cursor)

                    bot.send_message(message.chat.id,
                                     answer_tomorrow,
                                     reply_markup=keyboard)
                except IndexError:
                    bot.send_message(message.chat.id,
                                     'Сегодня нет уроков',
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

                        try:
                            day_info = get_all_info_day(cursor, date, user_stream)

                            answer = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                            bot.send_message(message.chat.id,
                                             answer,
                                             reply_markup=keyboard)
                        except IndexError:
                            bot.send_message(message.chat.id,
                                             'Сегодня нет уроков',
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
