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
    cursor.execute('''
    -- Сбрасываем все таблицы (уверен, можно элегантнее, но чтобы не возникало конфликтов, делаем так)
    DROP TABLE IF EXISTS DAY CASCADE;
    DROP TABLE IF EXISTS LESSONS_TIME CASCADE;
    DROP TABLE IF EXISTS LESSONS_TITLE CASCADE;

    -- Создаем таблицу День (у нас всегда будет 6 объектов)
    CREATE TABLE DAY
    (
        DAY_NAME CHAR(50) UNIQUE
    );

    -- Здесь время, во сколько начинается (будет ~6 объектов на каждый день, всего 36)
    CREATE TABLE LESSONS_TIME
    (
        TIME CHAR(50),
        DAY_NAME CHAR(50),
        CONSTRAINT FK_DAYS
            FOREIGN KEY(DAY_NAME)
                REFERENCES DAY(DAY_NAME)
                ON DELETE CASCADE
    );

    -- Здесь название предмета (будет примерно ~6 объектов на каждый день, всегро 36)
    CREATE TABLE LESSONS_TITLE
    (
        TITLE CHAR(100),
        DAY_NAME CHAR(50),
        CONSTRAINT FK_DAY
            FOREIGN KEY(DAY_NAME)
                REFERENCES DAY(DAY_NAME)
                ON DELETE CASCADE
    );
    ''')  # reset all tables and create it again

    for iteration in range(len(data)):  # all info in array so we need to go throw it
        for day in data[iteration].keys():  # goes throw all objects
            cursor.execute('INSERT INTO DAY(DAY_NAME) VALUES (%s);', (day,))

            for time in data[iteration].get(day)[0]:  # [0] after get means that we take all subjects time
                cursor.execute('INSERT INTO LESSONS_TIME(TIME, DAY_NAME) VALUES (%s, %s);', (time, day,))

            for title in data[iteration].get(day)[1]:  # [1] after get means that we take all subjects title
                cursor.execute('INSERT INTO LESSONS_TITLE(TITLE, DAY_NAME) VALUES (%s, %s);', (title, day,))

    connection.commit()
    cursor.close()
    connection.close()  # determinate connection


database_update(parse_timetable())  # run parsing and write all date to db
