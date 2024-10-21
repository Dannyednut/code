from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler, MessageHandler,filters
import requests
from pybit.unified_trading import HTTP
from telegram import Update
from datetime import datetime
from flask import Flask, request 
from telegram import Update
import os
TOKEN = os.getenv('BOTAPIKEY')
WEBHOOK = os.getenv('WEBHOOK')
application = Application.builder().token(TOKEN).build()

flag = True
session = HTTP( 
    demo=True,
    api_key='MH9CARj5M78qkOx9fV',
    api_secret='hNRvPbbxZZuEs5rarLnD4DD9r50dh13dHBWa'
)
session.url = 'https://demo-api.bybit.com'

'''
url = 'YOUR-URL-HERE/GET'
data = requests.get(url) # requests data from API
data = data.json() # converts return data to json
'''
# Retrieve values from API
try:
    btc_rate = session.get_tickers(category='spot', symbol='BTCUSDT')['result']['list'][0]['lastPrice']
    eth_rate = session.get_tickers(category='spot', symbol='ETHUSDT')['result']['list'][0]['lastPrice']
    ton_rate = session.get_tickers(category='spot', symbol='TONUSDT')['result']['list'][0]['lastPrice']
except Exception:
     flag = False

PRICE = range(1)
def return_time():
    return f'Hello. The current time is: {datetime.now().time()}.'

def get_price(symbol: str):
    try:
        return session.get_tickers(category='spot', symbol=symbol)['result']['list'][0]['lastPrice']
    except Exception:
         return None

def return_rates():
    return 'Hello. Today, USDT quote prices are as follows:\n BTCUSDT = $'+str(btc_rate)+'\n ETHUSDT = $'+str(eth_rate)+'\n TONUSDT = $'+str(ton_rate)

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=return_time())

async def symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Please enter symbol e.g BTCUSDT')
        return PRICE
async def coins(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=return_rates())

async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if not flag:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Internet Connection Error. Restart bot with /start')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! I respond to /time,  /trending and /get_price. Try these!')

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['symbol'] = (update.message.text)
        ticker = get_price(update.message.text)
        if ticker:
            await update.message.reply_text(f'{update.message.text}: ${ticker}')
            return ConversationHandler.END
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Error. Restart bot with /start')
            return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('cancelled.')
        return ConversationHandler.END


def main():

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get_price", symbol)
            ],
            states={
                PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)]
            },
            fallbacks=[CommandHandler("cancel", cancel)],

    )
    weather_handler = CommandHandler('time', time)
    currency_handler = CommandHandler('trending', coins)
    start_handler = CommandHandler('start', start)

    application.add_handler(weather_handler)
    application.add_handler(conv_handler)
    application.add_handler(currency_handler)
    application.add_handler(start_handler)

    application.bot.set_webhook(url=f'https://crest-jj18.onrender.com/{TOKEN}')

    return app

app = Flask(__name__)

async def webhook(update, context):
    await application.process_update(update)

@app.route('/' + TOKEN, methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), application.bot)
    webhook(update, None)
    return 'OK'

@app.route('/')
def index():
    return 'Hello, this is my Telegram bot!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    main()
    app.run(host='0.0.0.0', port=port)
