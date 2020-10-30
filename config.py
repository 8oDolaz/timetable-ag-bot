import telebot

token = '1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M'

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
button3 = telebot.types.KeyboardButton('На неделю')
keyboard1.row(button1, button2, button3)  # add it all to one row
