import os

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import logging
import redis
from flask import Flask, request, abort

app = Flask(__name__)

global redis1
config = configparser.ConfigParser()
config.read('config.ini')
redis1 = redis.Redis(host=config['REDIS']['HOST'],
                     password=config['REDIS']['PASSWORD'],
                     port=config['REDIS']['REDISPORT'])

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

@app.route("/")
def index():
    return "Hello World!"

@app.route(f"/{config['TELEGRAM']['ACCESS_TOKEN']}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return 'OK'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
    dp = telegram.ext.Dispatcher(bot, None)
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("help", help_command))
    app.run(port=int(os.environ.get('PORT', 5000)), debug=True, use_reloader=False)
