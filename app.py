import telebot
import psycopg2 as ps2
from enum import Enum


def main():

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
        bot.send_message(message.chat.id, salute, reply_markup=keyboard1)

    @bot.message_handler(func=lambda message: True, content_types=['text'])  # to see a timetable
    def main_bot(message):
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

            connection.commit()
            cursor.close()
            connection.close()

            bot.send_message(message.chat.id, answer_today, reply_markup=keyboard1)  # send a message with timetable

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

            bot.send_message(message.chat.id, answer_tomorrow, reply_markup=keyboard1)  # send a message with timetable

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

            connection.commit()
            cursor.close()
            connection.close()

            bot.send_message(message.chat.id, answer_week, reply_markup=keyboard1)  # send a message

        else:

            bot.send_message(message.chat.id, 'Пожалуйста, выберете одну из опций', reply_markup=keyboard1)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
