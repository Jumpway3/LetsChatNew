import os

import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackContext
import configparser
import logging
import redis
global redis1
def main():
# Load your token and create an Updater for your Bot
# Set OpenAI API Secret Key
    openai.api_key = os.environ['OPENAI_TOKEN']
    MODEL_ID = "text-davinci-003"

    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# register a dispatcher to handle message: here we register an echo dispatcher
#     echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
#     dispatcher.add_handler(echo_handler)
# on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))

# To start the bot:
    updater.start_polling()
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    updater.idle()
def handle_message(update, context):
    # Get input text
    user_input = update.message.text

    # Use
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=user_input,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # 获取 OpenAI API 返回的生成文本
    generated_text = response.choices[0].text.strip()
    # 存储生成的文本到 Redis 数据库中
    redis1.incr(generated_text)
    # 向用户发送生成的文本
    update.message.reply_text(generated_text)

# def echo(update, context):
#     reply_message = update.message.text.upper()
#     logging.info("Update: " + str(update))
#     logging.info("context: " + str(context))
#     context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
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
        update.message.reply_text('You have said ' + msg + ' for ' +
                          redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
if __name__ == '__main__':
    main()
