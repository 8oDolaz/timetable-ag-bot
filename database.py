from parser import parse_timetable
import json
from functions import *


def database_update(data, stream):
    connection, cursor = connect_to_db()

    for iteration in range(len(data)):
        for day in data[iteration].keys():
            '''our iteration looks like this: ({ info here })
            we need to take first object which is dictionary
            we will take key from it (we can't take only one so we take all of them)'''

            info = data[iteration].get(day)
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
