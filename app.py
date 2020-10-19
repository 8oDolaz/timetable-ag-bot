import telebot
import json

bot = telebot.TeleBot('1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M')  # bot with our token


keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
button3 = telebot.types.KeyboardButton('На неделю')
keyboard1.row(button1, button2, button3)  # add it all to one row


def prepare_answer(data, s=''):
    for item in data[0].keys():  # get all information that we need
        s += item + '\n' + '\n'  # do nice view
        for i in range(len(data[0].get(item)[0])):  # print all day info
            s += data[0].get(item)[0][i] + ' ' + data[0].get(item)[1][i] + '\n'  # first is time, second is subject
    return s


@bot.message_handler(func=lambda message: True, commands=['start'])  # just to start use the bot
def start(message):
    bot.send_message(message.chat.id, 'Добрый день!', reply_markup=keyboard1)


@bot.message_handler(func=lambda message: True, content_types=['text'])  # to see a timetable
def main_bot(message):
    if message.text.lower() == 'сегодня':  # to see today's timetable

        with open('data_base.json', 'r') as file:  # get everything we need from db
            data = json.loads(file.read())
            file.close()
            data = data[0]

        answer = prepare_answer(data)

        bot.send_message(message.chat.id, answer, reply_markup=keyboard1)  # send a message with timetable

    elif message.text.lower() == 'завтра':  # to see tomorrow's timetable

        with open('data_base.json', 'r') as file:  # get everything we need from db
            data = json.loads(file.read())
            file.close()
            data = data[1]

        answer = prepare_answer(data)

        bot.send_message(message.chat.id, answer, reply_markup=keyboard1)  # send a message with timetable

    elif message.text.lower() == 'на неделю':  # to see week's timetable

        with open('data_base.json', 'r') as file:  # get all information from db expect today's info
            data = json.loads(file.read())
            data = data[1:]
            file.close()

        s = ''
        for item in data:  # add all timetable to a string
            s += '\n' + '\n'
            for v in item[0].keys():
                s += v + '\n'
                for i in range(len(item[0].get(v)[0])):
                    s += item[0].get(v)[0][i] + ' ' + item[0].get(v)[1][i] + '\n'

        bot.send_message(message.chat.id, s, reply_markup=keyboard1)  # send a message

    else:

        bot.send_message(message.chat.id, 'choose one of the options', reply_markup=keyboard1)


bot.polling()  # start infinity circle
