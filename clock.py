import json
import datetime
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def parse_timetable():
    now = datetime.datetime.now()  # today's date
    now = now.strftime('%Y-%m-%d')

    url_lessons = f'https://timetable.spbu.ru/AGSM/StudentGroupEvents/Primary/275100/%s' % now  # timetable site
    r = requests.get(url_lessons, headers={'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'})
    # send a get request

    soup = BeautifulSoup(r.text, features='lxml')  # init Beautiful soup
    all_info = soup.find_all('div', {'class': 'panel panel-default'})[2:]
    # all info except first to (we don't need that)

    all_data = []  # empty array for all information

    with open('data_base.json', 'w') as file:  # clear our database
        file.write('')
        file.close()

    for item in all_info:  # go in all info
        title_m, time_m = [], []  # empty arrays for time and subject
        date = item.find('h4', {'class': 'panel-title'}).text.replace(' ', '', 20).replace('\n', '').replace('\r', '')
        date = date[::-1].replace(' ', '', 16)[::-1]  # today's date

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Время'}):
            time = i.text.replace(' ', '').replace('\n', '').replace('\r', '')
            time_m.append(time)  # find and add all lessons timing

        for i in item.find_all('span', {'class': 'moreinfo', 'title': 'Предмет'}):
            title = i.text.replace(' ', '', 16).replace('\n', '').replace('\r', '')
            title = title[:(title.find(','))]
            title_m.append(title)  # find and add all lessons title

        all_data.append([{date: [time_m, title_m]}])  # add everything to the array

    with open('data_base.json', 'a') as file:  # add the array to a database
        file.write(json.dumps(all_data))
        file.close()

    print(1)


sched.start()
