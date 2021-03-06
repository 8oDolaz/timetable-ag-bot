from parser import parse_timetable
import json
import psycopg2 as ps2


def connect_to_db():  # это функция подключает нас к базе данных
    connection = ps2.connect()  # сюда передаем данные для поключения к db
    return connection, connection.cursor()


def disconnect(connection, cursor):  # эта функция просто нас отключает
    connection.commit()
    cursor.close()
    connection.close()


def database_update(data, stream):
    connection, cursor = connect_to_db()

    for iteration in range(len(data)):
        for day in data[iteration].keys():
            '''наш iteration выглядит вот так ({ инфо. })
            получается, что нам нужно брать первый объект словаря'''

            info = data[iteration].get(day)  # берем все, что будем записывать в базу данных
            for i in range(len(info[0])):
                try:
                    time, title, type = info[0][i], info[1][i], info[2][i]
                except IndexError:
                    time, title, type = info[0][i], info[1][i], 'Очно'

                cursor.execute('''
                insert into day_info(lesson_time, lesson_title, lesson_type, day, stream) values(%s, %s, %s, %s, %s);
                ''', (time, title, type, day, stream))

    disconnect(connection, cursor)


connection, cursor = connect_to_db()
cursor.execute('truncate table day_info;')
disconnect(connection, cursor)

with open('streams_info.json', 'r') as db:
    streams = json.load(db)

for key in streams.keys():
    stream = streams.get(key)
    database_update(parse_timetable(stream), stream)
