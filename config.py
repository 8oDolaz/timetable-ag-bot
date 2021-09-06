from telebot.types import KeyboardButton, ReplyKeyboardMarkup

# token = '1483091692:AAF8LHuy-vk7DnELz8GI3U-CJVEtjNh6qa0'  # тестовый бот
token = '1382842329:AAGm6ydcY0mybVfkLxwH7q0rAkqF9S7hh8M'  # основной бот

main_keyboard = ReplyKeyboardMarkup()  # создаем клавиатуру
main_keyboard.row(
        KeyboardButton('Сегодня'),
        KeyboardButton('Завтра'),
        KeyboardButton('На неделю'))  # добавляем
main_keyboard.row(
        KeyboardButton('Сменить класс'),
)

instruction = '''Пожалуйста, введите свой класс, чтобы воспользоваться ботом и посмотреть ваше расписание!
Вот примеры: 10и1, 8к2, 9м1, где:
    1) 10, 9, 8 — ваш классс;
    2) и, к, м (и т.п.) — ваше направление (не важно, заглавными или нет);
    3) 1, 2 — ваша группа (если вы не знаете, то просто пишите 1).'''

text_after_change = '''Ты выбрал класс, поздравляю! Теперь ты можешь посмотреть расписание, нажав на кнопки: "Сегодня", "Завтра" и "На неделю".
Чтобы сменить свой класс, нажми "Сменить класс"'''

notification = '''Привет! Я очень рад, что ты уже пользовался ботм! Летом я доработал бота и исправил ошибки.
Только вот СПбГУ решиили все сломать)))
Но для тебя это не станет проблемой, нужно просто заново указать класс'''

info = '''Расписание в боте обновляется каждые 10 минут. Как мы это делаем?
Код регулярно собирает его с сайта timetable.spbu.ru, поэтому любые переносы, отмены или добавления будут обнаружены.
Любые предложения, ошибки или технические вопросы можно обсудить вот с ним: @I_name_I'''


days = ['понедельник',
        'вторник',
        'среда',
        'четверг',
        'пятница',
        'суббота',
        'воскресенье',
]  # отсюда мы берем название дня

months = [
        'января',
        'февраля',
        'марта',
        'апреля',
        'мая',
        'июня',
        'июля',
        'августа',
        'сентября',
        'октября',
        'ноября',
        'декабря',
]
