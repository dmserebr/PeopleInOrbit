import config
import logging
import telebot

import db_access
import message_formatter


bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='html')


def send_updates_to_all_users(updates):
    added = updates['added']
    removed = updates['removed']

    users = db_access.get_users_to_send_updates()
    for user in users:
        user_id = user[0]
        uid = user[1]
        chat_id = user[2]
        if chat_id is None:
            logging.warning(f'Unfortunately, chat_id of user {uid} is unknown, cannot send message!')
            continue

        try:
            if added:
                logging.info(f'Sending {len(added)} added to user {uid}, chat_id {chat_id}')
                bot.send_message(chat_id, message_formatter.format_added(added))
            if removed:
                logging.info(f'Sending {len(removed)} removed to user {uid}, chat_id {chat_id}')
                bot.send_message(chat_id, message_formatter.format_removed(removed))
            db_access.update_sent_updates(user_id)
        except Exception:
            logging.exception(f'Error while sending updates to user {uid}')
