import psycopg2 as ps2
from parser import parse_timetable


def database_update(data):
    connection = ps2.connect(
        database='dfsp85rbt6tna2',
        host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com',
        user='rmpqgvxcfahbdg',
        password='935a6af6648144a4044c436a75d94d989084cb84d19c8229a6b6c9690240aafb',
        port='5432',
    )

    cursor = connection.cursor()
    cursor.execute('TRUNCATE DAY CASCADE;')

    for iteration in range(len(data)):  # goes throe all days
        for day in data[iteration].keys():
            '''our iteration looks like this: ({ info here })
            we need to take first object which is dictionary
            we will take key from it (we can't take only one so we take all of them)'''
            cursor.execute('INSERT INTO DAY(DAY_NAME) VALUES (%s);', (day,))

            for time in data[iteration].get(day)[0]:  # [0] after get means that we take all subjects time
                cursor.execute('INSERT INTO LESSONS_TIME(TIME, DAY_NAME) VALUES (%s, %s);', (time, day,))

            for title in data[iteration].get(day)[1]:  # [1] after get means that we take all subjects title
                cursor.execute('INSERT INTO LESSONS_TITLE(TITLE, DAY_NAME) VALUES (%s, %s);', (title, day,))

    connection.commit()
    cursor.close()
    connection.close()  # determinate connection


database_update(parse_timetable())
