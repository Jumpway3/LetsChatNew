import os
import mysql.connector
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackContext
import configparser
import logging
from dotenv import load_dotenv
load_dotenv()




def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    openai_token = config.get('OPENAI', 'OPENAI_API_KEY')
    openai.api_key = openai_token
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

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


    generated_text = response.choices[0].text.strip()

    update.message.reply_text(generated_text)

    config = configparser.ConfigParser()
    config.read('config.ini')
    connection = mysql.connector.connect(
        host = config.get('DATABASE','host'),
        user = config.get('DATABASE','user'),
        password = config.get('DATABASE','password'),
        database = config.get('DATABASE','database')

    )

    try:
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO generated_text (text) VALUES (%s)"
            cursor.execute(insert_query, (generated_text,))
            connection.commit()
    finally:
        connection.close()
if __name__ == '__main__':
    main()
