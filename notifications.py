import config
from functions import connect_to_db, disconnect

import telebot

array = [962866053, 689109039, 1347303619, 411632509, 898094599, 1237904830, 1225740071, 757693252, 456124159,
         718019535, 459232402, 897863084, 893837849, 212344237, 472270126, -398950291, 1279137196, 729467687, 846133768,
         1086185873, 547583202, 588597017, 593303990, 495468072, 1015852636, 761412362, 1376562492, 654411066,
         1202936659, 451078721
]


def send_notification(users):
    bot = telebot.TeleBot(config.token)

    for usr in users:
        try:
            bot.send_message(usr, config.notification)
        except: pass


send_notification(array)
