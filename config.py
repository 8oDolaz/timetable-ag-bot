import telebot

token = 'bot token'

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
button3 = telebot.types.KeyboardButton('На неделю')
button4 = telebot.types.KeyboardButton('/reset')
keyboard1.row(button1, button2, button3)  # add it all to one row
keyboard1.row(button4)
