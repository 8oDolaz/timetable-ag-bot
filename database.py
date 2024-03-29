from parser import parse_timetable

import json
import psycopg2 as ps2


def connect_to_db():
    connection = ps2.connect(
        """Your database"""
    )
    return connection, connection.cursor()


def disconnect(connection, cursor):
    connection.commit()
    cursor.close()
    connection.close()


def database_update(data, stream, cursor):
    for day in data.keys():
        info = data.get(day)
        for i in range(len(info[0])):
            time, title, _type = info[0][i], info[1][i], info[2][i]

            cursor.execute('''
            INSERT INTO day_info(lesson_time, lesson_title, lesson_type, day, stream)
                    VALUES(%s, %s, %s, %s, %s);
            ''', (
                time, title, _type, day, stream,
            ))


def main():
    connection, cursor = connect_to_db()
    cursor.execute('TRUNCATE TABLE day_info;')

    with open('streams_info.json', 'r') as db:
        streams = json.load(db)

    all_classes = streams.keys()
    for key_i, key in enumerate(all_classes):
        stream = streams.get(key)
        database_update(parse_timetable(stream), stream, cursor)

    disconnect(connection, cursor)


if __name__ == '__main__':
    main()
