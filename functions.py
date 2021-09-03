import psycopg2 as ps2

delete_spaces = lambda string: string.strip()


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
