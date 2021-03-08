import os
import yaml

import telebot
import sonarr

from telebot import types

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf8"))
search_results = []

bot = telebot.TeleBot(config["telegram"]["token"], parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Welcome please use the /search command with the title of the show to start searching for a movie or TV Show")

@bot.message_handler(commands=['search'])
def search_media(message):
    search_term = message.text[8:]
    bot.reply_to(message, "Searching for: " + search_term)
    search_results = sonarr.SonarrRetriever().searchForMedia(search_term)
    result_text = 'Found: {results} available TV Shows. Chose one: '.format(results = len(search_results))
    markup = generate_markup(search_results, 0)
    bot.reply_to(message, result_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def  test_callback(call):
    if call.data == 'END':
        bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id, reply_markup=None)
    else:
        response = 'Adding show: {details}'.format(details = call.data)
        bot.answer_callback_query(call.id, response)
        markup = generate_markup(search_results,0, call.data)
        bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id, reply_markup=markup)

def generate_markup(results, start_item_num: int, dont_include_shows: int = 0):
    markup = types.InlineKeyboardMarkup()
    last_item = min(len(results) - start_item_num,9)
    for i in range(last_item):
        item = results[i + start_item_num]
        if item.id != dont_include_shows:
            itemtext = '{title} ({year}) - {overview}...'.format(title=item.title, year = item.year, overview = item.overview[:100])
            itembtn = types.InlineKeyboardButton(itemtext, callback_data=item.id)
            markup.add(itembtn)
    itemtext = 'SHOW MORE RESULTS'
    itembtn = types.InlineKeyboardButton(itemtext, callback_data='MORE')
    markup.add(itembtn)
    itemtext = 'END SEARCH'
    itembtn = types.InlineKeyboardButton(itemtext, callback_data='END')
    markup.add(itembtn)
    return markup

bot.polling()