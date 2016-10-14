# -*- coding: utf-8 -*-
# ! /usr/bin/env python
#
#  Aenea - Service bot from ElAutoestopista
#  Based on work "AstroobeerBot" from ResetReboot
#

import logging
import requests
import sys
import datetime
import random
import json

from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction

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
def tiempo(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        appkey = config.get('OWM')
        if not appkey:
            bot.sendMessage(update.message.chat_id, text='No tengo token de OWM')
            return

        # TODO: Accept parameters on this call
        city = None

        if not city:
            city = "Madrid,ES"

        params = {"q": city, "APPID": appkey, "units": "metric"}

        weatherdata = requests.get('http://api.openweathermap.org/data/2.5/forecast/city', params=params)
        if "list" in weatherdata.json():
            weather = weatherdata.json()['list']
            today = datetime.datetime.now()
            current_day = today
            for day in range(0, 3):
                if day > 0:
                    current_day = today + datetime.timedelta(days=day)
                    if current_day.hour > 5:
                        current_day -= datetime.timedelta(hours=3)

                    if day == 1:
                        date_string = "Mañana"

                    else:
                        date_string = "El {0}".format(WEEKDAYS[current_day.isoweekday()])

                else:
                    date_string = "Hoy"

                night = None
                for element in weather:
                    forecast_time = datetime.datetime.fromtimestamp(element['dt'])
                    if forecast_time.month == current_day.month and forecast_time.day == current_day.day and forecast_time.hour >= 5:
                        night = element

                if not night and day == 0:
                    weather_message = 'Asómate a la ventana, o sal del bar, que ya es de noche'

                else:
                    if night and night['main']:
                        weather_message = date_string + " tendremos unos {0}º con una humedad relativa de {1}%, ".format(
                            night['main']['temp'],
                            night['main']['humidity'])

                        if night['wind']:
                            weather_message += "vientos de {0} km\\h y una cobertura de nubes del {1}%".format(
                                night['wind']['speed'],
                                night['clouds']['all'])

                        else:
                            weather_message += "sin vientos y con una cobertura de nubes del {0}%".format(
                                night['clouds']['all'])

                        bot.sendMessage(update.message.chat_id, text=weather_message)

        else:
            weather_message = 'No puedo recuperar datos meteorológicos en este momento.'
            bot.sendMessage(update.message.chat_id, text=weather_message)


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
    dispatcher.add_handler(CommandHandler("tiempo", tiempo))


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
