import telebot
import psycopg2 as ps2
import json
import config
import datetime


def main():

    def delete_spaces(string):
        for i in range(len(string)):
            if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                string = string[i:]
                break

        for i in reversed(range(len(string))):
            if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                string = string[:i + 1]
                break

        return string

    def connect_to_db():
        connection = ps2.connect(
            host='ec2-54-217-224-85.eu-west-1.compute.amazonaws.com',
            database='deocs7tolmvlhl',
            user='kvrovbpxebvygf',
            port=5432,
            password='2a9a8d39986ac9095ec905091708ba357a0df483caa195141ca5ae53bafc3628',
        )
        return connection, connection.cursor()

    def disconnect(connection, cursor):
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_info_day(cursor, day, stream):
        cursor.execute('''
        select * from day_info where
        (position(%s in day_info.day) > 0 and day_info.stream=%s)
        ''', (day, stream,))

        time, title, _day, type = [], [], [], []
        info = cursor.fetchall()

        for i in range(len(info)):
            time.append(info[i][0])
            title.append(info[i][1])
            type.append(info[i][2])
            _day.append(info[i][3])

        return time, title, _day, type

    def prepare_answer(day, time, title, place, s=''):
        # day[0].upper() - first letter is now upper!
        s += day[0].upper() + day[1:] + '\n'
        for item in range(len(time)):
            # I don't know where is the problem but I need to delete spaces here
            s += time[item].replace(' ', '') +' '+ delete_spaces(title[item]) + '\n'  # ' '+ '('+delete_spaces(place[item])+')' + '\n'
        return s

    bot = telebot.TeleBot(config.token)  # bot with our token

    keyboard = config.keyboard1

    @bot.message_handler(func=lambda message: True, commands=['start'])
    def start(message):
        connection, cursor = connect_to_db()

        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s', (message.chat.id,))
        if len(cursor.fetchall()) == 0:
            bot.send_message(message.chat.id, config.instruction)
        else: # if user already exist
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его нажмите на кнопку)',
                             reply_markup=keyboard)

    @bot.message_handler(func=lambda message: True, content_types=['text'])  # to see a timetable
    def main_bot(message):
        connection, cursor = connect_to_db()
        cursor.execute('SELECT USER_INFO FROM USER_INFO WHERE c1=%s', (message.chat.id,))

        if len(cursor.fetchall()) != 0:  # if we have such user in table

            if message.text.lower() == 'сегодня':

                connection, cursor = connect_to_db()
                date = datetime.datetime.today()
                # looking for tomorrow date
                date = (date + datetime.timedelta(days=1)).strftime('%d') if date.isoweekday() == 7 else date.strftime('%d')
                # we try to find out is it wednesday or not
                date = date[1:] if date[0] == '0' else date
                # take of first 0

                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                day_info = get_all_info_day(cursor, date, user_stream)

                answer_today = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_today,
                                 reply_markup=keyboard)  # send a message with timetable
            elif message.text.lower() == 'завтра':

                connection, cursor = connect_to_db()
                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                date = (datetime.datetime.today() + datetime.timedelta(days=1))
                # looking for tomorrow date
                date = (date + datetime.timedelta(days=1)).strftime('%d') if date.isoweekday() == 1 else date.strftime('%d')
                # we try to find out is it wednesday or not
                date = date[1:] if date[0] == '0' else date
                # take of first 0

                day_info = get_all_info_day(cursor, date, user_stream)

                answer_tomorrow = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_tomorrow,
                                 reply_markup=keyboard)  # send a message with timetable
            elif message.text.lower() == 'на неделю':

                connection, cursor = connect_to_db()

                cursor.execute('''
                select c2 from user_info where c1=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                for delta in range(0, 7):
                    date = (datetime.datetime.today() + datetime.timedelta(days=delta))
                    if date.isoweekday() != 7:
                        date = date.strftime('%d')
                        date = date[1:] if date[0] == '0' else date

                        day_info = get_all_info_day(cursor, date, user_stream)

                        answer = prepare_answer(day_info[2][0], day_info[0], day_info[1], day_info[3])

                        bot.send_message(message.chat.id,
                                         answer,
                                         reply_markup=keyboard)

                disconnect(connection, cursor)
            elif message.text.lower() == 'сменить класс':
                connection, cursor = connect_to_db()
                cursor.execute('''DELETE FROM USER_INFO WHERE c1=%s;''',
                               (message.chat.id,))  # delete this user from db
                disconnect(connection, cursor)
                bot.send_message(message.chat.id,
                                 config.instruction)
            else:  # if we don't know what user typed
                bot.send_message(message.chat.id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard)
        else:
            # if we haven't such user in table
            with open('streams_info.json', 'r') as file:
                stream = (json.load(file)).get(message.text.lower())  # json.load(file) returns a dictionary
                file.close()

            if stream is not None:  # if we have such stream
                cursor.execute('INSERT INTO USER_INFO(c1, c2) VALUES(%s, %s);',
                               (message.chat.id, stream,))

                disconnect(connection, cursor)
                bot.send_message(message.chat.id,
                                 config.text_after_change,
                                 reply_markup=keyboard)
            else:  # if we haven't such user in stream
                bot.send_message(message.chat.id,
                                 config.instruction)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
