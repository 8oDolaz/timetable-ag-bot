from parser import parse_timetable
import json
import psycopg2 as ps2


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


def database_update(data, stream):
    connection, cursor = connect_to_db()

    for day in data.keys():
        info = data.get(day)  # берем все, что будем записывать в базу данных
        for i in range(len(info[0])):
            time, title, type = info[0][i], info[1][i], info[2][i]

            cursor.execute('''
                insert into day_info(lesson_time, lesson_title, lesson_type, day, stream) values(%s, %s, %s, %s, %s);
                ''', (time, title, type, day, stream))

    disconnect(connection, cursor)


connection, cursor = connect_to_db()
cursor.execute('truncate table day_info;')
disconnect(connection, cursor)

with open('streams_info.json', 'r') as db:
    streams = json.load(db)

for key_i, key in enumerate(streams.keys()):
    stream = streams.get(key)
    database_update(parse_timetable(stream), stream)
