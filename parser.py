import datetime
import requests
from bs4 import BeautifulSoup


def parse_element(info, start):
    output = []
    for elements in range(start, len(info), 5):
        element = info[elements].text.replace('\n', '').replace('\r', '')
        element = element[:(element.find(','))]

        if element.count(':') != 0: element = element.replace(' ', '')

        output.append(element)

    return output


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

    all_data = []  # empty array for all information

    for item in all_info:  # go in all info
        title_m, time_m= [], []  # empty arrays for time and subject

        # prepare data (a lot of useless symbols)
        date = item.find('h4', {'class': 'panel-title'}).text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        # replacing spaces after text
        date = date[::-1].replace(' ', '', 16)[::-1]  # today's date

        all_lesson_info = item.find_all('span')
       
        time_m = parse_element(all_lesson_info, 0)
        title_m = parse_element(all_lesson_info, 1)

        all_data.append({date: [time_m, title_m]})  # add everything to the array

    return all_data
