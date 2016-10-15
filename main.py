# -*- coding: utf-8 -*-
# ! /usr/bin/env python
#
#  Aenea - Service bot from ElAutoestopista
#  Based on work "AstroobeerBot" from ResetReboot
#

import logging
import sys

import requests
import wikipedia
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import git

from config import config

# Constants
WEEKDAYS = {
    1: "lunes",
    2: "martes",
    3: "miércoles",
    4: "jueves",
    5: "viernes",
    6: "sábado",
    7: "domingo"
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

# Stupid auth function. dafuq
def auth(bot, update):
    user = update.message.from_user.username  # Received username
    authorized_user = "ElAutoestopista"  # Authorized username, you know...
    if user != authorized_user:
        auth_message = 'No está autorizado a utilizar este bot, ' + str(user)
        bot.sendMessage(update.message.chat_id, text=auth_message)
        return 1
    else:
        return 0


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Aenea lista')


def help(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        bot.sendMessage(update.message.chat_id, text="""Soy Aenea, bot de servicio. Aún no tengo funciones definidas.
                    """)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


# This is were the fun begins
def tiempo(bot, update, args):
    lugar = args[0]
    dataargs = lugar.lower()
    authorization = auth(bot, update)
    if authorization is 0:
        if dataargs == "casa":
            lat = 40.372180
            lon = -3.759953
        elif dataargs == "yebes":
            lat = 40.582964
            lon = -3.116039
        elif dataargs == "alfa":
            lat = 40.444795
            lon = -4.245248
        elif dataargs == "stratio":
            lat = 40.440842
            lon = -3.786091
        else:
            mensaje = "Lo siento, localizacion no contemplada"
            bot.sendMessage(update.message.chat_id, text=mensaje)
            return

        # Building URL to query the service
        url_service = 'http://202.127.24.18/bin/astro.php'
        url_params = {'lon': str(lon), 'lat': str(lat), 'output': "json", 'tzshift': "0", 'unit': "metric", 'ac': "0"}

        # Query service
        timer7 = requests.get(url_service, params=url_params)
        if timer7.status_code > 299:
            bot.sendMessage(update.message.chat_id, text='No puedo recuperar la información meteorológica')
            return

        json_timer7 = timer7.json()

        # Recover data for today (dataseries 1) and tomorrow (dataseries 7)
        for data in range(1, 13, 6):
            timer7_data = json_timer7["dataseries"][data]
            timer7_cloud = json_timer7["dataseries"][data]["cloudcover"]
            timer7_temp = json_timer7["dataseries"][data]["temp2m"]
            timer7_precipitation = json_timer7["dataseries"][data]["prec_type"]

            # Test if it will rain or not (important for laundry day!)
            if timer7_precipitation == "rain":
                mensaje_lluvia = " lloverá"
            else:
                mensaje_lluvia = " no lloverá"

            # Compose messages about clouds
            if 3 < timer7_cloud < 5:
                mensaje_cloud = " habrá bastantes nubes"
            elif 3 > timer7_cloud > 1:
                mensaje_cloud = " habrá pocas nubes"
            elif timer7_cloud == 1:
                mensaje_cloud = " habrá cielo despejado"
            elif timer7_cloud > 5:
                mensaje_cloud = " estará muy nublado"
            else:
                mensaje_cloud = " no habrá nubes"

            # Message about temperature
            mensaje_temp = " y habrá una temperatura de " + str(timer7_temp) + " grados."

            # Now compose full message
            if data is 1:
                mensaje = "Hoy en " + lugar + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp
            else:
                mensaje = "Mañana en " + lugar + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp

            # Vomit the response
            bot.sendMessage(update.message.chat_id, text=mensaje)
    return


# Simple job for wikipedia info searches
def info(bot, update, args):
    authorization = auth(bot, update)
    if authorization is 0:
        wikipedia.set_lang("es")  # Hey, I'm spanish
        searchstring = ' '.join(args)
        searchresult = wikipedia.page(searchstring)
        search_content = searchresult.content
        search_url = searchresult.url
        bot.sendMessage(update.message.chat_id, text=search_url)

def main():
    token = config.get('TOKEN')

    if token is None:
        print("Please, configure your token first")
        sys.exit(1)

    updater = Updater(token)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("tiempo", tiempo, pass_args=True))
    dispatcher.add_handler(CommandHandler("info", info, pass_args=True))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    print("Arrancando Aenea...")
    main()
