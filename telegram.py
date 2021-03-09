import os
import yaml

import telebot
import sonarr

from telebot import types

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf8"))
search_results = {}
selected_results = {}

bot = telebot.TeleBot(config["telegram"]["token"], parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Welcome please use the /search command with the title of the media you're looking for to start searching for a movie or TV Show")

@bot.message_handler(commands=['search'])
def search_media(message):
    selected_results.clear()
    search_results.clear()
    if len(message.text) <= 8:
        bot.reply_to(message, 'Don''t do a Pete, include something to search for: /search a tv show')
    else:
        search_term = message.text[8:]
        bot.reply_to(message, "Searching for: " + search_term)
        search_results.update(sonarr.SonarrRetriever().searchForMedia(search_term))
        result_text = 'Found: {results} available TV Shows. Showing first 10.'.format(results = len(search_results))
        markup = generate_markup(search_results, 0)
        bot.reply_to(message, result_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def  show_selection_handler(call):
    if call.data == 'END':
        bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id, reply_markup=None)
        if len(selected_results) > 0:
            added_items = ', '.join(str(x.title) for x in selected_results.values())
            bot.reply_to(message=call.message, text="Added: " + added_items)
        else:
            bot.reply_to(message=call.message, text="No additional media added")
    else:
        added_media = search_results.get(call.data)
        response = 'Adding show: {details}'.format(details = added_media.title)
        bot.answer_callback_query(call.id, response)
        sonarr.SonarrRetriever().addMedia(call.data[1:])
        selected_results[call.data] = added_media
        markup = generate_markup(search_results,0, selected_results)
        bot.edit_message_reply_markup(message_id=call.message.id, chat_id=call.message.chat.id, reply_markup=markup)

def generate_markup(results, start_item_num: int, dont_include_shows: list[int] = []):
    markup = types.InlineKeyboardMarkup()
    last_item = min(len(results) - start_item_num,9)
    for i in range(last_item):
        item = list(results)[i]
        item_details = results.get(item)
        if item not in dont_include_shows:
            itemtext = '{title} ({year}) - {overview}...'.format(title=item_details.title, year = item_details.year if item_details.year > 0 else 'Unk', overview = item_details.overview[:100])
            itembtn = types.InlineKeyboardButton(itemtext, callback_data=item)
            markup.add(itembtn)
    itemtext = 'END SEARCH'
    itembtn = types.InlineKeyboardButton(itemtext, callback_data='END')
    markup.add(itembtn)
    return markup

bot.polling()