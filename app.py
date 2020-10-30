import telebot
import psycopg2 as ps2


def main():

    def disconnect(connect, cursor):
        connect.commit()
        cursor.close()
        connect.close()

    def get_time_title(day, cursor):
        cursor.execute('SELECT TIME FROM LESSONS_TIME WHERE DAY_NAME=%s;', (day,))
        time = [item for item in cursor.fetchall()]  # item[0] because second field is day and we don't need it

        cursor.execute('SELECT TITLE FROM LESSONS_TITLE WHERE DAY_NAME=%s;', (day,))
        title = [item for item in cursor.fetchall()]  # item[0] because second field is day and we don't need it

        return time, title

    def prepare_answer(day, time, title, s=''):
        # day[0].upper() - first letter is now upper!
        s += day[0].upper() + day[1:] + '\n'
        for item in range(len(time)):
            # I don't know where is the problem but I need to delete spaces here
            s += time[item].replace(' ', '') + ' ' + title[item] + '\n'
        return s

    salute = "Привет! Для начала выбери свой класс:\nПожалуйста, введи в таком формате: '10И1' ('10' - класс, " \
             "'И' - твое направление, '1' - твоя группа) "

    bot = telebot.TeleBot('1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M')  # bot with our token

    keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
    button1 = telebot.types.KeyboardButton('Сегодня')
    button2 = telebot.types.KeyboardButton('Завтра')
    button3 = telebot.types.KeyboardButton('На неделю')
    keyboard1.row(button1, button2, button3)  # add it all to one row

    @bot.message_handler(func=lambda message: True, commands=['start'])
    def start(message):
        connection = ps2.connect(
            database='d9rkqtvh45pj8c',
            host='ec2-176-34-123-50.eu-west-1.compute.amazonaws.com',
            port=5432,
            user='zwlligehjlxrxw',
            password='e233e3aed49ebfb74cd270b8d1dda3bcc6838036c32eeb52de2038d856475b09'
        )
        cursor = connection.cursor()

        cursor.execute('SELECT USER_ID FROM USER_INFO WHERE USER_ID=%s', (message.chat.id,))
        if len(cursor.fetchall()) == 0:
            bot.send_message(message.chat.id,
                             salute,
                             reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id,
                             'Мы уже занем ваш класс (чтобы сменить его введите /reset)',
                             reply_markup=keyboard1)

    @bot.message_handler(func=lambda message: True, commands=['reset'])
    def reset(message):
        connection = ps2.connect(
            database='d9rkqtvh45pj8c',
            host='ec2-176-34-123-50.eu-west-1.compute.amazonaws.com',
            port=5432,
            user='zwlligehjlxrxw',
            password='e233e3aed49ebfb74cd270b8d1dda3bcc6838036c32eeb52de2038d856475b09'
        )
        cursor = connection.cursor()

        cursor.execute('''DELETE FROM USER_INFO WHERE USER_ID=%s;''', (message.chat.id,))

        disconnect(connection, cursor)

        bot.send_message(message.chat.id, 'Ваш класс сброшен! Теперь введите его снова.')

    @bot.message_handler(func=lambda message: True, content_types=['text'])  # to see a timetable
    def main_bot(message):
        connection = ps2.connect(
            database='d9rkqtvh45pj8c',
            host='ec2-176-34-123-50.eu-west-1.compute.amazonaws.com',
            port=5432,
            user='zwlligehjlxrxw',
            password='e233e3aed49ebfb74cd270b8d1dda3bcc6838036c32eeb52de2038d856475b09'
        )
        cursor = connection.cursor()

        cursor.execute('SELECT USER_ID FROM USER_INFO WHERE USER_ID=%s', (message.chat.id,))

        if len(cursor.fetchall()) != 0:
            if message.text.lower() == 'сегодня':

                connection = ps2.connect(
                    database='dfsp85rbt6tna2',
                    host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com',
                    user='rmpqgvxcfahbdg',
                    password='935a6af6648144a4044c436a75d94d989084cb84d19c8229a6b6c9690240aafb',
                    port=5432,)

                cursor = connection.cursor()

                cursor.execute('SELECT * FROM DAY;')
                day = cursor.fetchall()[0][0]
                time, title = get_time_title(day, cursor)

                answer_today = prepare_answer(day, time, title)

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_today,
                                 reply_markup=keyboard1)  # send a message with timetable
            elif message.text.lower() == 'завтра':

                connection = ps2.connect(
                    database='dfsp85rbt6tna2',
                    host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com',
                    user='rmpqgvxcfahbdg',
                    password='935a6af6648144a4044c436a75d94d989084cb84d19c8229a6b6c9690240aafb',
                    port='5432',)

                cursor = connection.cursor()

                cursor.execute('SELECT * FROM DAY;')
                day = cursor.fetchall()[1][0]
                time, title = get_time_title(day, cursor)

                answer_tomorrow = prepare_answer(day, time, title)

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_tomorrow,
                                 reply_markup=keyboard1)  # send a message with timetable
            elif message.text.lower() == 'на неделю':

                connection = ps2.connect(
                    database='dfsp85rbt6tna2',
                    host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com',
                    user='rmpqgvxcfahbdg',
                    password='935a6af6648144a4044c436a75d94d989084cb84d19c8229a6b6c9690240aafb',
                    port='5432',)

                cursor = connection.cursor()

                answer_week = ''

                cursor.execute('SELECT * FROM DAY;')
                days = cursor.fetchall()
                for day in days:
                    # we need to take first one to prevent error (there are only one object)
                    time, title = get_time_title(day[0], cursor)
                    answer_week += prepare_answer(day[0], time, title) + '\n'

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 answer_week,
                                 reply_markup=keyboard1)  # send a message
            else:
                bot.send_message(message.chat.id,
                                 'Пожалуйста, выберете одну из опций',
                                 reply_markup=keyboard1)
        else:
            if message.text[0] in '189' and message.text[len(message.text) - 1] in '12':

                cursor.execute('''
                    INSERT INTO USER_INFO(USER_ID, USER_CLASS) VALUES(%s, %s);
                    ''', (message.chat.id, message.text,))

                disconnect(connection, cursor)

                bot.send_message(message.chat.id,
                                 'Вы выбрали класс (чтобы сменить, введите /reset)',
                                 reply_markup=keyboard1)
            else:
                bot.send_message(message.chat.id,
                                 'Введите свой класс в указаном формате (10и1)')

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
