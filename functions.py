import calendar
import psycopg2 as ps2

days = {
    'Monday': 'понедельник',
    'Tuesday': 'вторник',
    'Wednesday': 'среда',
    'Thursday': 'четверг',
    'Friday' : 'пятница',
    'Saturday': 'суббота',
    'Sunday': 'воскресенье',
}  # этот словарь нужен для "первода" дней недели


def get_date(date):
    # берем номер нашего дня в неделе
    day_in_week = date.isoweekday() - 1
    # берем дату это для
    date = date.strftime('%d')
    # если вначале есть 0, то убираем его
    date = date[1:] if date[0] == '0' else date
    # получаем финальное название дня
    return days.get(list(calendar.day_name)[day_in_week]) + ', ' +  date


def delete_spaces(string):
    # я не буду писать комментарий к каждой строке, но здесь мы сначала ищем первую букву с начала, а потмо с конца
    # чтобы удалить все лишнее пробелы
    for i in range(len(string)):
        if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            string = string[i:]
            break

    for i in reversed(range(len(string))):
        if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            string = string[:i + 1]
            break

    return string


def connect_to_db():  # это функция подключает нас к базе данных
    connection = ps2.connect(  # сюда мы передаем всё необходимое
        host='ec2-54-217-224-85.eu-west-1.compute.amazonaws.com',
        database='deocs7tolmvlhl',
        user='kvrovbpxebvygf',
        port=5432,
        password='2a9a8d39986ac9095ec905091708ba357a0df483caa195141ca5ae53bafc3628',
    )
    return connection, connection.cursor()


def disconnect(connection, cursor):  # эта функция просто нас отключает
    connection.commit()
    cursor.close()
    connection.close()


def get_all_info_day(cursor, day, stream):  # это функция возвращает все что нужно для формирования сообщения
    cursor.execute('''
    select * from day_info where
    (position(%s in day_info.day) > 0 and day_info.stream=%s)
    ''', (day, stream,))

    time, title, _day, type = [], [], [], []
    info = cursor.fetchall()

    for i in range(len(info)):  # вот именно здесь мы записываем все необходимое
        time.append(info[i][0])
        title.append(info[i][1])
        type.append(info[i][2])
        _day.append(info[i][3])

    return time, title, _day, type


def prepare_answer(day, time, title, place, s=''):  # здесь мы формируем само сообщение
    # day[0].upper() —— теперь первая буква заглавная!
    s += day[0].upper() + day[1:] + '\n'
    for item in range(len(time)):
        # Я не знаю где эта проблема, но пробелы я должен удалять здесь
        s += time[item].replace(' ', '') + ' ' + delete_spaces(title[item]) + '\n'  # ' '+ '('+delete_spaces(place[item])+')' + '\n'
        # Возможно, когда-то, я добавлю Очно или Дистанционо
    return s
