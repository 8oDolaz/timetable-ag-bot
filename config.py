import telebot

# token = '1483091692:AAF8LHuy-vk7DnELz8GI3U-CJVEtjNh6qa0'  # тестовый бот
token = '1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M'

keyboard1 = telebot.types.ReplyKeyboardMarkup()  # создаем клавиатуру
button1 = telebot.types.KeyboardButton('Сегодня')
button2 = telebot.types.KeyboardButton('Завтра')
button3 = telebot.types.KeyboardButton('На неделю')
button4 = telebot.types.KeyboardButton('Сменить класс')
keyboard1.row(button1, button2, button3)  # добавляем
keyboard1.row(button4)

instruction = '''Пожалуйста, введите свой класс, чтобы воспользоваться ботом и посмотреть ваше расписание!
Вот примеры: 10и1, 8к2, 9м1, где:
    1) 10, 9, 8 - ваш классс;
    2) и, к, м (и т.п.) - ваше направление (не важно, заглавными или нет);
    3) 1, 2 — ваша группа (если вы не знаете, то просто пишите 1).'''

text_after_change = '''Вы выбрали класс, теперь вы можете посмотреть ваше расписание, для этого нажмите на кнопку "сегодня", чтобы посмотреть сегодняшнее расписание вашего класса, кнопку "на завтра", чтобы посмотреть расписание вашего класса на завтра или кнопку "на неделю", чтобы увидеть всё расписание, указанного вами (вашего), класса на неделю.
Если вы ввели неправильно или хотите посмотреть расписание другого класса, то нажмите на нижнюю кнопку "сменить класс".'''

# Здесь лижит все, чем я не хотел засорять основной файл

days = ["понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",]
