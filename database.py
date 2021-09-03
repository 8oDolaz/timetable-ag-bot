from parser import parse_timetable
from functions import connect_to_db, disconnect

import json


def database_update(data, stream):
    connection, cursor = connect_to_db()

    for day in data.keys():
        info = data.get(day)  # берем все, что будем записывать в базу данных
        for i in range(len(info[0])):
            time, title, type = info[0][i], info[1][i], info[2][i]

            cursor.execute('''
                INSERT INTO day_info(lesson_time, lesson_title, lesson_type, day, stream) VALUES(%s, %s, %s, %s, %s);
                ''', (time, title, type, day, stream))

    disconnect(connection, cursor)


def main():
    connection, cursor = connect_to_db()
    cursor.execute('TRUNCATE TABLE day_info;')
    disconnect(connection, cursor)

    with open('streams_info.json', 'r') as db:
        streams = json.load(db)

    all_classes = streams.keys()
    for key_i, key in enumerate(all_classes):
        stream = streams.get(key)
        database_update(parse_timetable(stream), stream)


if __name__ == '__main__':
    main()
