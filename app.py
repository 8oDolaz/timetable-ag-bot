import telebot
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import requests
from flask import Flask
from os import environ
from bs4 import BeautifulSoup  # import everything we need

app = Flask(__name__)
bot = telebot.TeleBot('1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M')  # bot with our token

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
button3 = telebot.types.KeyboardButton('На неделю')
keyboard1.row(button1, button2, button3)  # add it all to one row

shred = BlockingScheduler()  # for timer


@shred.scheduled_job('interval', minutes=1)  # interval in parsing
def parse_timetable():
    now = datetime.datetime.now()  # today's date
    now = now.strftime('%Y-%m-%d')

    url_lessons = f'https://timetable.spbu.ru/AGSM/StudentGroupEvents/Primary/275100/%s' % now  # timetable site
    r = requests.get(url_lessons, headers={'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'})
    # send a get request

    soup = BeautifulSoup(r.text, features='lxml')  # init Beautiful soup
    all_info = soup.find_all('div', {'class': 'panel panel-default'})[2:]
    # all info except first to (we don't need that)

    all_data = []  # empty array for all information

    with open('data_base.json', 'w') as file:  # clear our database
        file.write('')
        file.close()

    for item in all_info:  # go in all info
        title_m, time_m = [], []  # empty arrays for time and subject
        date = item.find('h4', {'class': 'panel-title'}).text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        date = date[::-1].replace(' ', '', 16)[::-1]  # today's date

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Время'}):
            time = i.text.replace(' ', '').replace('\n', '').replace('\r', '')
            time_m.append(time)  # find and add all lessons timing

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Предмет'}):
            title = i.text.replace(' ', '', 16).replace('\n', '').replace('\r', '')
            title = title[:(title.find(','))]
            title_m.append(title)  # find and add all lessons title

        all_data.append([{date: [time_m, title_m]}])  # add everything to the array

    with open('data_base.json', 'a') as file:  # add the array to a database
        file.write(json.dumps(all_data))
        file.close()


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
shred.start()  # start timer
app.run(debug=False, host='127.0.0.1', port=environ.get('PORT', 33500))  # Flask host bind (fix heroku problem)
