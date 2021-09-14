from parser import parse_timetable

import json
import psycopg2 as ps2


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


def database_update(data, stream, connection, cursor):
    for day in data.keys():
        info = data.get(day)
        for i in range(len(info[0])):
            time, title, type = info[0][i], info[1][i], info[2][i]

            cursor.execute('''
            INSERT INTO day_info(lesson_time, lesson_title, lesson_type, day, stream)
                    VALUES(%s, %s, %s, %s, %s);
            ''', (
                time, title, type, day, stream,
            ))


def main():
    connection, cursor = connect_to_db()
    cursor.execute('TRUNCATE TABLE day_info;')

    with open('streams_info.json', 'r') as db:
        streams = json.load(db)

    all_classes = streams.keys()
    for key_i, key in enumerate(all_classes):
        stream = streams.get(key)
        database_update(parse_timetable(stream), stream, connection, cursor)

    disconnect(connection, cursor)


if __name__ == '__main__':
    main()
