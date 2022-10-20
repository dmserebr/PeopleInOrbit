from bs4 import BeautifulSoup
import requests
import telebot

import db_access
import wiki_parser
import message_formatter

BOT_TOKEN = ''

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='html')

WIKI_URL = 'https://en.wikipedia.org'
PEOPLE_IN_ORBIT_URL = WIKI_URL + '/wiki/Low_Earth_orbit'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f'Got message: {message}')

    db_access.store_query(message)

    bot.send_message(message.chat.id, 'Hey space lover! 🧑‍🚀\n\n'
                                      'This bot can tell you about people currently in low Earth orbit.\n'
                                      'Use the command /peopleinorbit to get the recent updates 👌')


@bot.message_handler(commands=['peopleinorbit'])
def send_welcome(message):
    print(f'Got message: {message}')

    text = 'Cannot get information about people in orbit 😕\nPlease contact the bot administrator.'
    astronauts = []
    try:
        people_in_orbit_page = requests.get(PEOPLE_IN_ORBIT_URL)
        soup = BeautifulSoup(people_in_orbit_page.content, 'html.parser')
        astronauts = wiki_parser.get_astronauts(soup)
        text = message_formatter.generate_msg(astronauts)
    except Exception as e:
        print('Got exception: ', e.__repr__(), e.args)

    db_access.store_query(message, {'astronauts_count': len(astronauts)})

    bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    db_access.check_sqlite_exists()

    print('Starting polling')
    bot.infinity_polling()
