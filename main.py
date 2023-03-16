import os
import telegram
import configparser
import redis
import logging
from flask import Flask, request

app = Flask(__name__)

# Load your token and create a bot instance
config = configparser.ConfigParser()
config.read('config.ini')
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
redis1 = redis.Redis(host=config['REDIS']['HOST'], password=config['REDIS']['PASSWORD'], port=config['REDIS']['REDISPORT'])

# Handle incoming telegram messages
@app.route(f"/{config['TELEGRAM']['ACCESS_TOKEN']}", methods=['POST'])
def handle_telegram_message():
    # Retrieve the message in JSON format and convert it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    logging.info(f"Received message: {update.message.text}")

    # Echo the message back to the user
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

    return 'ok'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
@app.route('/add')
def add_keyword():
    try:
        keyword = request.args.get('keyword')
        if keyword is None:
            return 'Keyword not found', 400
        redis1.incr(keyword)
        return f"You have said {keyword} for {redis1.get(keyword).decode('UTF-8')} times.", 200
    except:
        return 'Error occurred while processing your request', 500

@app.route('/help')
def help_command():
    return 'Helping you helping you.', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
