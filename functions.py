import locale
import calendar
import psycopg2 as ps2


def get_date(date):
    # берем номер нашего дня в неделе
    # day_in_week = date.isoweekday() - 1
    # берем дату это для
    date = date.strftime('%d')
    # если вначале есть 0, то убираем его
    date = date[1:] if date[0] == '0' else date
    # устонавливаем русский язык
    # locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    # получаем финальное название дня
    return date # list(calendar.day_name)[day_in_week] + ', ' +


def delete_spaces(string):
    for i in range(len(string)):
        if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            string = string[i:]
            break

    for i in reversed(range(len(string))):
        if string[i].lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            string = string[:i + 1]
            break

    return string


def connect_to_db():
    connection = ps2.connect(
        host='ec2-54-217-224-85.eu-west-1.compute.amazonaws.com',
        database='deocs7tolmvlhl',
        user='kvrovbpxebvygf',
        port=5432,
        password='2a9a8d39986ac9095ec905091708ba357a0df483caa195141ca5ae53bafc3628',
    )
    return connection, connection.cursor()


def disconnect(connection, cursor):
    connection.commit()
    cursor.close()
    connection.close()


def get_all_info_day(cursor, day, stream):
    cursor.execute('''
    select * from day_info where
    (position(%s in day_info.day) > 0 and day_info.stream=%s)
    ''', (day, stream,))

    time, title, _day, type = [], [], [], []
    info = cursor.fetchall()

    for i in range(len(info)):
        time.append(info[i][0])
        title.append(info[i][1])
        type.append(info[i][2])
        _day.append(info[i][3])

    return time, title, _day, type


def prepare_answer(day, time, title, place, s=''):
    # day[0].upper() - first letter is now upper!
    s += day[0].upper() + day[1:] + '\n'
    for item in range(len(time)):
        # I don't know where is the problem but I need to delete spaces here
        s += time[item].replace(' ', '') + ' ' + delete_spaces(
            title[item]) + '\n'  # ' '+ '('+delete_spaces(place[item])+')' + '\n'
    return s
