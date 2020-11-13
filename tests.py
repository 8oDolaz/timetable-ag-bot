import psycopg2 as ps2


def connect_to_db():
    connection = ps2.connect(
        database='d9rkqtvh45pj8c',
        host='ec2-176-34-123-50.eu-west-1.compute.amazonaws.com',
        port=5432,
        user='zwlligehjlxrxw',
        password='e233e3aed49ebfb74cd270b8d1dda3bcc6838036c32eeb52de2038d856475b09'
    )
    cursor = connection.cursor()
    return connection, cursor


def disconnect(connection, cursor):
    connection.commit()
    cursor.close()
    connection.close()


def get_day_time_title(cursor, day, stream):
    cursor.execute('''
    select time, day from lessons_time where(position(%s in lessons_time.day) > 0 and lessons_time.stream=%s);
    ''', (day, stream,))
    info = cursor.fetchall()
    time, date = [item[0] for item in info], [item[1] for item in info]

    cursor.execute('''
    select title from lessons_title where(position(%s in lessons_title.day) > 0 and lessons_title.stream=%s);
    ''', (day, stream,))
    title = [item[0] for item in cursor.fetchall()]

    return date, time, title


connection, cursor = connect_to_db()

print(
    get_day_time_title(cursor, '16', 275100)
)
