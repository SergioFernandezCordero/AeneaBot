# -*- coding: utf-8 -*-
# ! /usr/bin/env python
#
#  Aenea - Service bot from ElAutoestopista
#  Based on work "AstroobeerBot" from ResetReboot
#

import logging
import sys

import requests
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
def tiempo(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        # WELL, PERHAPS SOME DAY
        # Get user location and data
        # user_location = update.message.location
        # print(user_location)
        # Register user location (just fot the lulz)
        # logger.info("Location: %f / %f"
        #            % (user_location.latitude, user_location.longitude))

        # Initalize coordinates
        # lon = update.message.location.latitude
        # lat = update.message.location.longitude
        lon = None
        lat = None

        if not lon or not lat:
            # Home sweet home
            lat = 40.372180
            lon = -3.759953

        # Building URL to query the service
        url_service = 'http://202.127.24.18/bin/astro.php'
        url_params = {'lon': str(lon), 'lat': str(lat), 'output': "json", 'tzshift': "0", 'unit': "metric", 'ac': "0"}

        # Query service
        timer7 = requests.get(url_service, params=url_params)
        if timer7.status_code > 299:
            bot.sendMessage(update.message.chat_id, text='No puedo recuperar la información meteorológica')
            return

        json_timer7 = timer7.json()

        # Data for today
        timer7_data = json_timer7["dataseries"][1]
        timer7_cloud = json_timer7["dataseries"][1]["cloudcover"]
        timer7_temp = json_timer7["dataseries"][1]["temp2m"]
        timer7_precipitation = json_timer7["dataseries"][1]["prec_type"]

        # Conditions where observation is imposible: 100% cloud or rain
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

        # Message about temperature
        mensaje_temp = " y habrá una temperatura de " + str(timer7_temp) + " grados celsius (via timer7)"

        # Tomorrow forecast
        timer7_data_tomorrow= json_timer7["dataseries"][7]
        timer7_cloud_tomorrow = json_timer7["dataseries"][7]["cloudcover"]
        timer7_temp_tomorrow = json_timer7["dataseries"][7]["temp2m"]
        timer7_precipitation_tomorrow = json_timer7["dataseries"][7]["prec_type"]

        # Conditions where observation is imposible: 100% cloud or rain
        if timer7_precipitation_tomorrow == "rain":
            mensaje_lluvia_tomorrow = " lloverá"
        else:
            mensaje_lluvia_tomorrow = " no lloverá"

        # Compose messages about clouds
        if 3 < timer7_cloud_tomorrow < 5:
            mensaje_cloud_tomorrow = " habrá bastantes nubes"
        elif 3 > timer7_cloud_tomorrow > 1:
            mensaje_cloud_tomorrow = " habrá pocas nubes"
        elif timer7_cloud_tomorrow == 1:
            mensaje_cloud_tomorrow = " habrá cielo despejado"
        elif timer7_cloud_tomorrow > 5:
            mensaje_cloud_tomorrow = " estará muy nublado"

        # Message about temperature
        mensaje_temp_tomorrow = " y habrá una temperatura de " + str(timer7_temp) + " grados celsius (via timer7)"

        # Now compose full message
        mensaje_today = "Hoy en casa" + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp
        mensaje_tomorrow = "Mañana en casa" + mensaje_lluvia_tomorrow + "," + mensaje_cloud_tomorrow + "," + mensaje_temp_tomorrow

        # Vomit the response
        bot.sendMessage(update.message.chat_id, text=mensaje_today)
        bot.sendMessage(update.message.chat_id, text=mensaje_tomorrow)
        return


def deploy(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        bot.sendMessage(update.message.chat_id, text="Ok, deplegando aplicación")

def nodeploy(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        bot.sendMessage(update.message.chat_id, text="Ok, cancelando")

def astrodeploy(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        reply_keyboard = [['Si', 'No']]
        bot.sendMessage(chat=update.message.chat_id,text="Esto desplegará la web de Astropirados desde Git. ¿Está seguro?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


start_handler = CommandHandler('Si', deploy)
start_handler = CommandHandler('No', nodeploy)
dispatcher.add_handler(deploy)
dispatcher.add_handler(nodeploy)


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
    dispatcher.add_handler(CommandHandler("astrodeploy", astrodeploy))

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
