from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time
%import_functions%

token = '%token%'

updater = Updater(token=token)

dispatcher = updater.dispatcher

last_question = {}
answers = {}

%single_choice_functions%

%functions_blocks_functions%

def start(bot, update):
    global last_question
    global answers
    answers[bot.message.chat_id] = {}
    last_question[bot.message.chat_id] = ''
%first_blocks%


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def buttons(bot, update):
    global last_question
    global answers
    query = bot.callback_query
    answer = query.data
    answers[query.message.chat_id][last_question[query.message.chat_id]] = answer
%inline_handlers%


def text(bot, update):
    global last_question
    global answers
    got_answer = False
%text_handlers%
text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)

buttons_handler = CallbackQueryHandler(buttons)
dispatcher.add_handler(buttons_handler)

while True:
    try:
        updater.start_polling()
        updater.idle()

    except Exception as e:
        time.sleep(5)