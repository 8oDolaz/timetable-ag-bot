import telebot

token = '1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M'
<<<<<<< HEAD
test_token = '1483091692:AAF8LHuy-vk7DnELz8GI3U-CJVEtjNh6qa0'

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('На завтра')
=======

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # add a keyboard
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
>>>>>>> 3817aab925dc454e8eb47ada8525407e39ba2ffc
button3 = telebot.types.KeyboardButton('На неделю')
button4 = telebot.types.KeyboardButton('Сменить класс')
keyboard1.row(button1, button2, button3)  # add it all to one row
keyboard1.row(button4)

<<<<<<< HEAD
instruction = '''Пожалуйста, введите свой класс, чтобы воспользоваться ботом и посмотреть ваше расписание!
Вот примеры: 10и1, 8к2, 9м1, где:
    1) 10, 9, 8 - ваш классс;
    2) и, к, м (и т.п.) - ваше направление (не важно, заглавными или нет);
    3) 1, 2 — ваша группа (если вы не знаете, то просто пишите 1).'''

text_after_change = '''Вы выбрали класс, теперь вы можете посмотреть ваше расписание, для этого нажмите на кнопку "сегодня", чтобы посмотреть сегодняшнее расписание вашего класса, кнопку "на завтра", чтобы посмотреть расписание вашего класса на завтра или кнопку "на неделю", чтобы увидеть всё расписание, указанного вами (вашего), класса на неделю.
Если вы ввели неправильно или хотите посмотреть расписание другого класса, то нажмите на нижнюю кнопку "сменить класс".'''
=======
salute = "Привет! Для начала выбери свой класс:\nПожалуйста, введи в таком формате: '10И1' ('10' - класс, " \
             "'И' - твое направление, '1' - твоя группа)"

instruction = '''Пожалуйста, введите свой класс. Вот примеры: 10и1, 8к2, 9м1, где:
    1) 10, 8, 9 - ваш классс;
    2) и, к, м - ваше направление (не важно, заглавными или нет);
    3) 1, 2, 1 - ваша группа (если не знаете, то просто пишите 1).'''
>>>>>>> 3817aab925dc454e8eb47ada8525407e39ba2ffc
