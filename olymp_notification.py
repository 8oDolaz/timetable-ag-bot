import config

import requests
import bs4
import telebot

bot = telebot.TeleBot(config.token_test)


def schedule():
    req = requests.get(
        'https://olimpiada.ru/activities?type=ind&subject%5B7%5D=on&class=11&period_date=&period=year'
    )
    soup = bs4.BeautifulSoup(req.text, features='lxml')

    for olymp in soup.find_all('div', {'class': 'fav_olimp'}):
        olymp_name = olymp.find('span', {'class': 'headline'}).text

        if olymp_name.count('Газпром'):
            olymp_timeline = olymp.find('div', {'class': 'timeline'})
            olymp_timeline = olymp_timeline.find_all('span', {'class': 'tl_cont_s'})

            if len(olymp_timeline) == 4:
                olymp_date = olymp_timeline[3].text.strip()
                bot.send_message(862932540, olymp_date)


schedule()
