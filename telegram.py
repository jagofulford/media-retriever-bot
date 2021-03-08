import os
import yaml

import telebot
import sonarr


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf8"))


bot = telebot.TeleBot(config["telegram"]["token"], parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Welcome please use the /search command to start searching for a movie or TV Show")

@bot.message_handler(commands=['search'])
def search_media(message):
    search_term = message.text[8:]
    bot.reply_to(message, "Searching for: " + search_term)
    search_results = sonarr.SonarrRetriever().searchForMedia(search_term)
    bot.reply_to(message, "Found: %d available TV Shows: " % len(search_results))

bot.polling()