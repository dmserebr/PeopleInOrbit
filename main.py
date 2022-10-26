import telebot

import config
import db_access
import process_commands

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='html')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f'Got message: {message}')

    process_commands.process_welcome(message)

    bot.send_message(message.chat.id, 'Hey space lover! 🧑‍🚀\n\n'
                                      'This bot can tell you about people currently in low Earth orbit.\n'
                                      'Use the command /peopleinorbit to get the recent updates 👌')


@bot.message_handler(commands=['peopleinorbit'])
def send_people_in_orbit(message):
    print(f'Got message: {message}')

    text = process_commands.process_people_in_orbit(message)

    bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    db_access.check_sqlite_exists()

    print('Starting polling')
    bot.infinity_polling()
