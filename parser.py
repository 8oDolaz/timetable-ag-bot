import datetime
import requests
from bs4 import BeautifulSoup


<<<<<<< HEAD
def lesson_type(string):
    if string.lower().count('дист') != 0:
        return 'Дист.'
    return 'Очно'


=======
>>>>>>> 3817aab925dc454e8eb47ada8525407e39ba2ffc
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
<<<<<<< HEAD
        title_m, time_m, type_m = [], [], []  # empty arrays for time and subject
=======
        title_m, time_m = [], []  # empty arrays for time and subject
>>>>>>> 3817aab925dc454e8eb47ada8525407e39ba2ffc
        # prepare data (a lot of useless symbols)
        date = item.find('h4', {'class': 'panel-title'}).text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        # replacing spaces after text
        date = date[::-1].replace(' ', '', 16)[::-1]  # today's date

        for title_iter in item.find_all('span', {'class': 'moreinfo', 'title': 'Время'}):
            time = title_iter.text.replace(' ', '').replace('\n', '').replace('\r', '')
            time_m.append(time)  # find and add all lessons timing

        for title_iter in item.find_all('span', {'class': 'moreinfo', 'title': 'Предмет'}):
            title = title_iter.text.replace(' ', '', 15).replace('\n', '').replace('\r', '')
            title = title[:(title.find(','))]
            title_m.append(title)  # find and add all lessons title

<<<<<<< HEAD
        types = item.find_all('div', {'class': 'col-sm-3 studyevent-locations'})
        for place in types:
            type = place.find_all('span')
            for iter in type:
                type_m.append(lesson_type(iter.text))

        all_data.append({date: [time_m, title_m, type_m]})  # add everything to the array
=======
        all_data.append({date: [time_m, title_m]})  # add everything to the array
>>>>>>> 3817aab925dc454e8eb47ada8525407e39ba2ffc

    return all_data
