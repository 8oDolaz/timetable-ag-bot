import telebot
import psycopg2 as ps2
import json
import config
import datetime


def main():

    def connect_to_db():
        connection = ps2.connect(
            database='d9rkqtvh45pj8c',
            host='ec2-176-34-123-50.eu-west-1.compute.amazonaws.com',
            port=5432,
            user='zwlligehjlxrxw',
            password='e233e3aed49ebfb74cd270b8d1dda3bcc6838036c32eeb52de2038d856475b09'
        )
        cursor = connection.cursor()
        return connection, cursor

    def disconnect(connection, cursor):
        connection.commit()
        cursor.close()
        connection.close()

    def get_day_time_title(cursor, day, stream):
        cursor.execute('''
        select time, day from lessons_time where(position(%s in lessons_time.day) > 0 and lessons_time.stream=%s);
        ''', (day, stream,))
        info = cursor.fetchall()
        time, date = [item[0] for item in info], [item[1] for item in info]

        cursor.execute('''
        select title from lessons_title where(position(%s in lessons_title.day) > 0 and lessons_title.stream=%s);
        ''', (day, stream,))
        title = [item[0] for item in cursor.fetchall()]

        return date, time, title

    def prepare_answer(day, time, title, s=''):
        # day[0].upper() - first letter is now upper!
        s += day[0].upper() + day[1:] + '\n'
        for item in range(len(time)):
            # I don't know where is the problem but I need to delete spaces here
            s += time[item].replace(' ', '') + ' ' + title[item] + '\n'
        return s

    bot = telebot.TeleBot(config.token)  # bot with our token

    keyboard = config.keyboard1

    @bot.message_handler(func=lambda message: True, commands=['start'])
    def start(message):
        connection, cursor = connect_to_db()

        cursor.execute('SELECT USER_ID FROM USER_INFO WHERE USER_ID=%s', (message.chat.id,))
        if len(cursor.fetchall()) == 0:  # if user already exist
            bot.send_message(message.chat.id,
                             config.salute,
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его введите /reset)',
                             reply_markup=keyboard)

    @bot.message_handler(func=lambda message: True, content_types=['text'])  # to see a timetable
    def main_bot(message):
        connection, cursor = connect_to_db()

        cursor.execute('SELECT USER_ID FROM USER_INFO WHERE USER_ID=%s', (message.chat.id,))

        if len(cursor.fetchall()) != 0:

            # if we have such user in table
            if message.text.lower() == 'сегодня':

                connection, cursor = connect_to_db()
                date = datetime.datetime.today().strftime('%d')
                date = date[1:] if date[0] == '0' else date

                cursor.execute('''
                select user_stream from user_info where user_id=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                day_info = get_day_time_title(cursor, date, user_stream)

                answer_today = prepare_answer(day_info[0][0], day_info[1], day_info[2])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_today,
                                 reply_markup=keyboard)  # send a message with timetable
            elif message.text.lower() == 'завтра':

                connection, cursor = connect_to_db()
                date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%d')
                date = date[1:] if date[0] == '0' else date

                cursor.execute('''
                select user_stream from user_info where user_id=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                day_info = get_day_time_title(cursor, date, user_stream)

                answer_tomorrow = prepare_answer(day_info[0][0], day_info[1], day_info[2])

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_tomorrow,
                                 reply_markup=keyboard)  # send a message with timetable
            elif message.text.lower() == 'на неделю':

                connection, cursor = connect_to_db()

                cursor.execute('''
                select user_stream from user_info where user_id=%s;
                ''', (message.chat.id,))
                user_stream = cursor.fetchall()[0][0]

                for delta in range(0, 6):
                    date = (datetime.datetime.today() + datetime.timedelta(days=delta)).strftime('%d')
                    date = date[1:] if date[0] == '0' else date

                    day_info = get_day_time_title(cursor, date, user_stream)

                    answer = prepare_answer(day_info[0][0], day_info[1], day_info[2])

                    bot.send_message(message.chat.id,
                                     answer,
                                     reply_markup=keyboard)

                disconnect(connection, cursor)
            elif message.text.lower() == 'сменить класс':
                connection, cursor = connect_to_db()
                cursor.execute('''DELETE FROM USER_INFO WHERE USER_ID=%s;''',
                               (message.chat.id,))  # delete this user from db
                disconnect(connection, cursor)
                bot.send_message(message.chat.id, 'Ваш класс сброшен! Теперь, введите его снова.')
            else:
                bot.send_message(message.chat.id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard)
        else:
            # if we haven't such user in table
            with open('streams_info.json', 'r') as file:
                stream = (json.load(file)).get(message.text.lower())  # json.load(file) returns a dictionary
                file.close()

            if stream is not None:
                cursor.execute('INSERT INTO USER_INFO(USER_ID, USER_STREAM) VALUES(%s, %s);',
                               (message.chat.id, stream,))

                disconnect(connection, cursor)
                bot.send_message(message.chat.id,
                                 'Вы выбрали класс (чтобы сменить, введите /reset).', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id,
                                 'Похоже, что вы неправильно указали название класса, попробуйте еще раз (вот '
                                 'образец: 10и1 или 10И1).')

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
