import logging
import sys

import telebot

import config
import db_access
import flaskapp
import process_commands
import updater_thread

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='html')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f'Got message: {message}')

    process_commands.process_welcome(message)

    bot.send_message(message.chat.id, 'Hey space lover! 🧑‍🚀\n\n'
                                      'This bot can tell you about people currently in low Earth orbit.\n'
                                      'Use the command /peopleinorbit to get the recent updates 👌')


@bot.message_handler(commands=['peopleinorbit'])
def send_people_in_orbit(message):
    logging.debug(f'Got message: {message}')

    text = process_commands.process_people_in_orbit(message)

    bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(threadName)s[%(thread)s] %(message)s')
    db_access.check_sqlite_exists()

    if config.UPDATER_ENABLED:
        updater_thread = updater_thread.UpdaterThread()
        updater_thread.start()

    if config.FLASK_APP_ENABLED:
        app_thread = flaskapp.FlaskAppThread()
        app_thread.start()

    if config.BOT_ENABLED:
        logging.info('Starting polling')
        bot.infinity_polling()
