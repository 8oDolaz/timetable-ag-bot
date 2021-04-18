from functions import delete_spaces

import datetime
import requests

from bs4 import BeautifulSoup


def parse_timetable(stream):
    now = datetime.datetime.now()  # today's date
    now = now.strftime('%Y-%m-%d')  # example: 2020-09-09

    # website link for actual day
    url_lessons = f'https://timetable.spbu.ru/AGSM/StudentGroupEvents/Primary/%s/%s' % (stream, now)
    # send a get request
    request = requests.get(url_lessons, headers={'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'})

    soup = BeautifulSoup(request.text, features='lxml')  # init Beautiful soup
    # all info except first and second (some useless info in it)
    all_info = soup.find_all('div', {'class': 'panel panel-default'})[2:]

    output = {}

    for day in all_info:
        time_array, title_array = [], []
        date = day.find('h4', {'class': 'panel-title'})
        date = date.text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        date = delete_spaces(date)

        for row in day.find_all('li', {'class': 'common-list-item row'}):
            for item in row.find_all('span'):
                if str(item).count('cancelled') == 0 and str(item).count('moreinfo') != 0:

                    if str(item).lower().count('время') != 0:
                        time = item.text.replace('\n', '').replace('\r', '')
                        time_array.append(
                            delete_spaces(time)
                        )

                    if str(item).lower().count('предмет') != 0:
                        title = item.text.replace('\n', '').replace('\r', '')
                        title = title[:title.find(',')]
                        title_array.append(
                            delete_spaces(title)
                        )

        output[date] = [
            time_array,
            title_array,
            ['Очно' for _ in range(len(time_array))]
        ]

    return output
