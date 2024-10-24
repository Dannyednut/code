from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler, MessageHandler,filters
import requests
from pybit.unified_trading import HTTP
from telegram import Update
from datetime import datetime

from quart import Quart, request
from telegram import Update
import asyncio
import os
TOKEN = os.getenv('BOTAPIKEY')
WEBHOOK = os.getenv('WEBHOOK')


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
def trend():
    try:
        # Get the tickers for all symbols
        li = {}
        string =''
        symbol_width = 12
        price_width = 15
        change_width = 2
        tickers = session.get_tickers(category="spot").get('result')['list']
        # Filter the tickers to get the gainer pairs
        gainer_pairs = [ticker['symbol'] for ticker in tickers if float(ticker['price24hPcnt']) > 0 and ticker['symbol'][-4:] == ('USDT' or 'USDC')]
        for i in gainer_pairs:
            for n in tickers:
                if i in n['symbol']:
                    li[n['symbol']] = (float(n['price24hPcnt']))
        # Print the gainer pairs
        top_five_keys = [item[0] for item in sorted(li.items(), key=lambda item: item[1], reverse=True)[:5]]
        # Add a header for clarity
        string += f"{'Symbol':<{symbol_width}} {'Last Price':<{price_width}} {'24h Change':<{change_width}}\n"
        string += "-" * (symbol_width + price_width + change_width) + "\n"

        for i in top_five_keys:
            pair = session.get_tickers(category="spot", symbol=i).get('result')['list'][0]
            # Format the output with specified widths
            string += f"{pair['symbol']:<{symbol_width}} {pair['lastPrice']:<{price_width}} {round(float(pair['price24hPcnt']) * 100, 2):<{change_width}}%\n"

        return string

    except Exception:
        flag = False
        return flag

PRICE = range(1)
def return_time():
    return f'Hello. The current time is: {datetime.now().strftime("%H:%M")} UTC.'

def get_price(symbol: str):
    try:
        print('getting price')
        return session.get_tickers(category='spot', symbol=symbol)['result']['list'][0]['lastPrice']
    except Exception:
         return None

def return_rates():
    return trend()
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


# ... (keep your existing imports and configurations)
app = Quart(__name__)
application = None
# ... (keep your existing command handlers and conversation logic)


def main():
    global application
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get_price", symbol)],
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

    return application

async def setup_webhook():
    try:
        webhook_info = await application.bot.get_webhook_info()
        if webhook_info.url != f'https://{WEBHOOK}/{TOKEN}':
            await application.bot.set_webhook(url=f'https://{WEBHOOK}/{TOKEN}')
            print(f"Webhook set to https://{WEBHOOK}/{TOKEN}")
        else:
            print("Webhook is already set correctly")
    except Exception as e:
        print(f"Failed to set webhook: {e}")

@app.before_serving
async def startup():
    global application
    application = main()  # Call main() to set up the application
    await application.initialize()
    await setup_webhook()

@app.route('/')
async def index():
    return 'Hello, this is my Telegram bot!'

@app.route('/health')
async def health_check():
    return 'OK', 200

@app.route('/' + TOKEN, methods=['POST'])
async def webhook():
    update = Update.de_json(await request.get_json(), application.bot)
    await application.process_update(update)
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
