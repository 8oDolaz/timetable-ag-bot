import datetime
import requests

from bs4 import BeautifulSoup


def check_if_time(element):
    element = element.strip()
    for letter in element:
        if letter.isdigit(): return True
    return False


def parse_timetable(stream):
    now = datetime.datetime.now()  # today's date
    now = now.strftime('%Y-%m-%d')  # example: 2020-09-09

    # website link for actual day
    url_lessons = f'https://timetable.spbu.ru/AGSM/StudentGroupEvents/Primary/%s/%s' % (stream, now)
    # send a get request
    request = requests.get(url_lessons, headers={'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'})

    soup = BeautifulSoup(request.text, features='lxml')  # init Beautiful soup
    # all info except first and second (some useless info in it)
    all_info = soup.find_all('div', {'class': 'panel panel-default'})[3:]

    output = {}

    for day in all_info:
        time_array, title_array = [], []
        date = day.find('h4', {'class': 'panel-title'})
        date = date.text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        date = date.strip()

        for row in day.find_all('li', {'class': 'common-list-item row'}):
            for item in row.find_all('span'):
                if str(item).count('cancelled') == 0 and str(item).count('moreinfo') != 0 \
                        and str(item).count('hoverable') == 0:

                    if check_if_time(item.text):  # время урока
                        time = ''.join(item.text.split())
                        time_array.append(
                            time
                        )

                    if not check_if_time(item.text):  # название предмета
                        title = item.text.replace('\n', '').replace('\r', '')
                        title = title[:title.find(',')]
                        title_array.append(
                            title.strip()
                        )

        output[date] = [
            time_array,
            title_array,
            ['Очно'] * len(time_array),
        ]

    return output

