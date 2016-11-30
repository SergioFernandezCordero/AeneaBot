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
import subprocess
import os
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

# Identify your bot
botname = config.get('BOTNAME')


# Stupid auth function. dafuq
def auth(bot, update):
    user = update.message.from_user.username  # Received username
    authorized_user = config.get('AUTHUSER')  # Authorized username, you know...
    if user != authorized_user:
        auth_message = 'No está autorizado a utilizar este bot, ' + str(user)
        bot.sendMessage(update.message.chat_id, text=auth_message)
        return 1
    else:
        return 0


def start(bot, update):
    authorization = auth(bot, update)
    user = update.message.from_user.username
    if authorization is 0:
        mensaje = botname + " lista, " + user + ". ¿En qué puedo ayudarte hoy?"
        bot.sendMessage(update.message.chat_id, text=mensaje)


def help(bot, update):
    authorization = auth(bot, update)
    if authorization is 0:
        mensaje = "Soy " + botname + ", bot de servicio. Aún no tengo funciones definidas"
        bot.sendMessage(update.message.chat_id, text=mensaje)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


# This is were the fun begins
def tiempo(bot, update, args):
    authorization = auth(bot, update)
    if authorization is 0:
        # Check input
        if not args:
            # No input, no way
            bot.sendMessage(update.message.chat_id, text='¿De dónde?')
            return
        else:
            # screw it!
            lugar = ' '.join(args)
            dataargs = lugar.lower()

        # Let's do some mapgeo magic...
        apikey = config.get('MAPREQUEST')
        if not apikey:
            bot.sendMessage(update.message.chat_id, text='No tengo clave de API para geolocalizacion')
            return
        # Build URL as usual
        map_url = 'http://www.mapquestapi.com/geocoding/v1/address'
        map_params = {'key': apikey, 'location': str(dataargs), 'maxResults': 1}
        # Get LAT/LON for a location
        try:
            # WARNING: Note that MapRequestApi doesn't test if location exists. Instead of this it does
            # some kind of heuristic-holistic matching with some kind of last-resort database.
            # This means that, as if you pass random characters as input, you always get a valid response.
            # Weirdo...
            mapgeo = requests.get(map_url, params=map_params)
            json_mapgeo = mapgeo.json()
            # This will be used to know from where the results are (F.E. locality names that exists in different cities
            mapgeo_location = json_mapgeo["results"][0]["locations"][0]["adminArea3"]
            mapgeo_lat = json_mapgeo["results"][0]["locations"][0]["latLng"]["lat"]
            mapgeo_lon = json_mapgeo["results"][0]["locations"][0]["latLng"]["lng"]
            lat = mapgeo_lat
            lon = mapgeo_lon
        except ConnectionError:
            # Something went wrong?
            bot.sendMessage(update.message.chat_id, text="Servicio de geolocalización no disponible")
            return

        # Building URL to query the service
        url_service = 'http://202.127.24.18/bin/astro.php'
        url_params = {'lon': str(lon), 'lat': str(lat), 'output': "json", 'tzshift': "0", 'unit': "metric", 'ac': "0"}

        # Query service
        timer7 = requests.get(url_service, params=url_params)
        if timer7.status_code > 299:
            bot.sendMessage(update.message.chat_id, text='¡No puedo recuperar la información meteorológica!')
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
                mensaje = "Hoy en " + lugar + ", " + mapgeo_location + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp
            else:
                mensaje = "Mañana en " + lugar + ", " + mapgeo_location + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp

            # Vomit the response
            bot.sendMessage(update.message.chat_id, text=mensaje)
    return


# Simple job for wikipedia info searches
def info(bot, update, args):
    authorization = auth(bot, update)
    if authorization is 0:
        language = config.get('LANG')
        wikipedia.set_lang(language)
        searchstring = ' '.join(args)
        try:
            searchresult = wikipedia.page(searchstring)
            search_content = searchresult.content
            search_url = searchresult.url
            bot.sendMessage(update.message.chat_id, text=search_url)
        except ConnectionError:
            bot.sendMessage(update.message.chat_id, text="Wikipedia no está disponible")
        except wikipedia.exceptions.DisambiguationError as disambiguation:
            disambiguation_options = disambiguation.options[0:-2]
            disambiguation_string = "Se han encontrado resultados para " + ', '.join(disambiguation_options) + ". Por favor, especifique"
            bot.sendMessage(update.message.chat_id, text=disambiguation_string)
        except wikipedia.exceptions.PageError as wikierror:
            bot.sendMessage(update.message.chat_id, text="Sin resultados para " + searchstring)


def buscar(bot, update, args):
    try:
        bot.sendPhoto(update.message.chat_id, photo='https://www.fernandezcordero.net/imagenes/api_buscador.jpg')
    except:
        bot.sendMessage(update.message.chat_id, text="Ni la imagen te puedo mostrar...")


# Talk capabilities proof of concept
# (Here I can say PoC, not at work)
def habla(bot, update, args):
    authorization = auth(bot, update)
    if authorization is 0:
        language = config.get('LANG')
        talkstring = ' '.join(args)
        print(talkstring)
        tmpfile = "/tmp/aenea-speech.ogg"
        # TODO: Error controls, Check if espeak and vorbis-tools (oggenc) are installed, Audio format suitable for android client, perhaps voice tunning.
        subprocess.call("espeak -v {0}+f4 \"{1}\" --stdout | oggenc -o {2} -".format(language, talkstring, tmpfile), shell=True)
        bot.sendVoice(update.message.chat_id, voice=open(tmpfile, 'rb'))
        os.remove(tmpfile)



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
    dispatcher.add_handler(CommandHandler("buscar", buscar, pass_args=True))
    dispatcher.add_handler(CommandHandler("habla", habla, pass_args=True))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    print("Arrancando " + botname + "...")
    main()
