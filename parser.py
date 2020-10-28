import datetime
import requests
from bs4 import BeautifulSoup
import psycopg2 as ps2


def parse_timetable():
    now = datetime.datetime.now()  # today's date
    now = now.strftime('%Y-%m-%d')  # example: 2020-09-09

    # website link for actual day
    url_lessons = f'https://timetable.spbu.ru/AGSM/StudentGroupEvents/Primary/275100/%s' % now
    # send a get request
    request = requests.get(url_lessons, headers={'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'})

    soup = BeautifulSoup(request.text, features='lxml')  # init Beautiful soup
    # all info except first and second (some useless info in it)
    all_info = soup.find_all('div', {'class': 'panel panel-default'})[2:]

    all_data = []  # empty array for all information

    for item in all_info:  # go in all info
        title_m, time_m = [], []  # empty arrays for time and subject
        # prepare data (a lot of useless symbols)
        date = item.find('h4', {'class': 'panel-title'}).text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        # replacing spaces after text
        date = date[::-1].replace(' ', '', 16)[::-1]  # today's date

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Время'}):
            time = i.text.replace(' ', '').replace('\n', '').replace('\r', '')
            time_m.append(time)  # find and add all lessons timing

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Предмет'}):
            title = i.text.replace(' ', '', 15).replace('\n', '').replace('\r', '')
            title = title[:(title.find(','))]
            title_m.append(title)  # find and add all lessons title

        all_data.append({date: [time_m, title_m]})  # add everything to the array

    return all_data


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
