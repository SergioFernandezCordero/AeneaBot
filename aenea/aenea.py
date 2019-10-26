#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Aenea - Service bot from ElAutoestopista
Based on work "AstroobeerBot" from ResetReboot
"""

import logging
import sys
import random
import os

import requests
import wikipedia

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
botname = (os.environ['BOTNAME'])


def auth(bot, update):
    """
    Stupid auth function. dafuq
    """
    user = update.message.from_user.username  # Received username
    authorized_user = (os.environ['AUTHUSER'])  # Authorized username, you know...
    if user != authorized_user:
        auth_message = 'No está autorizado a utilizar este bot, ' + str(user)
        bot.sendMessage(update.message.chat_id, text=auth_message)
        return 1
    else:
        return 0


def start(bot, update):
    """
    Runs the bot
    """
    authorization = auth(bot, update)
    user = update.message.from_user.username
    if authorization is 0:
        mensaje = botname + " lista, " + user + ". ¿En qué puedo ayudarte hoy?"
        bot.sendMessage(update.message.chat_id, text=mensaje)


def ayuda(bot, update):
    """
    Funcion de ayuda.

    """
    authorization = auth(bot, update)
    if authorization is 0:
        mensaje = "Soy " + botname + ", bot de servicio. Aún no tengo funciones definidas"
        bot.sendMessage(update.message.chat_id, text=mensaje)


def error(update, errors):
    """
    Logs execution errors
    """
    logger.warning('Update "%s" caused error "%s"' % (update, errors))


# This is were the fun begins
def tiempo(bot, update, args):
    """
    Prevision meteorológica para hoy y mañana
    """
    authorization = auth(bot, update)
    if authorization is 0:
        # Check input
        if not args:
            # No input, no way
            mensaje = "¿De dónde?"
            bot.sendMessage(update.message.chat_id, text=mensaje)
            return
        else:
            # screw it!
            lugar = ' '.join(args)
            dataargs = lugar.lower()

        # Let's do some mapgeo magic...
        apikey = (os.environ['MAPREQUEST'])
        if not apikey:
            mensaje = "No tengo clave de API para geolocalizacion"
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
            mapgeo_lat = json_mapgeo["results"][0]["locations"][0]["latLng"]["lat"]
            mapgeo_lon = json_mapgeo["results"][0]["locations"][0]["latLng"]["lng"]
            lat = mapgeo_lat
            lon = mapgeo_lon
        except ConnectionError:
            # Something went wrong?
            mensaje = "Servicio de geolocalización no disponible"
            return

        # Building URL to query the service
        url_service = 'http://www.7timer.info/bin/astro.php'  # Should this go outta here?
        url_params = {'lon': str(lon), 'lat': str(lat), 'output': "json", 'tzshift': "0", 'unit': "metric", 'ac': "0"}

        # Query service
        try:
            timer7 = requests.get(url_service, params=url_params)
        except requests.exceptions.RequestException:
            mensaje = "¡No puedo recuperar la información meteorológica!"
            return

        json_timer7 = timer7.json()

        # Recover data for today (dataseries 1) and tomorrow (dataseries 7)
        for data in range(1, 13, 6):
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
            if timer7_temp == 1:
                mensaje_temp = " y habrá una temperatura de " + str(timer7_temp) + " grado."
            else:
                mensaje_temp = " y habrá una temperatura de " + str(timer7_temp) + " grados."

            # Now compose full message
            if data is 1:
                mensaje = "Hoy en " + lugar + ", " + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp
            else:
                mensaje1 = "Mañana en " + lugar + ", " + mensaje_lluvia + "," + mensaje_cloud + "," + mensaje_temp

        # Vomit the response
        bot.sendMessage(update.message.chat_id, text=mensaje)
        bot.sendMessage(update.message.chat_id, text=mensaje1)
    return


def info(bot, update, args):
    """
        Simple job for wikipedia info searches
    """
    authorization = auth(bot, update)
    if authorization is 0:
        language = (os.environ['LANG'])
        wikipedia.set_lang(language)
        searchstring = ' '.join(args)
        try:
            searchresult = wikipedia.page(searchstring)
            search_url = searchresult.url
            mensaje = search_url
        except requests.exceptions.RequestException:
            mensaje = "Wikipedia no está disponible"
        except wikipedia.exceptions.DisambiguationError as disambiguation:
            mensaje = "Se han encontrado varios resultados. Sea más específico"
        except wikipedia.exceptions.PageError as wikierror:
            mensaje = wikierror + "para" + searchstring
        bot.sendMessage(update.message.chat_id, text=mensaje)


def jerigonzo(bot, update, args):
    """
    Traduce un texto a jerigonzo
    Ver: https://es.wikipedia.org/wiki/Jerigonza
    """
    authorization = auth(bot, update)
    if authorization is 0:
        if not args:
            bot.sendMessage(update.message.chat_id, text="[cries in jeriogonzo]")
        else:
            translatestring = ' '.join(args).lower()
            vocales = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
            for vocal in vocales:
                translatestring = translatestring.replace(vocal, vocal + "p" + vocal)
            bot.sendMessage(update.message.chat_id, text="[JERIGONZO] - " + translatestring)


def buscar(bot, update):
    """
    Busca información en un buscador de internet
    """
    try:
        bot.sendPhoto(update.message.chat_id, photo='https://www.fernandezcordero.net/imagenes/api_buscador.jpg')
    except ConnectionError:
        bot.sendMessage(update.message.chat_id, text="Ni la imagen te puedo mostrar...")


def ruok(bot, update):
    """
        Silly function to check if it's online
    """
    authorization = auth(bot, update)
    if authorization is 0:
        bot.sendMessage(update.message.chat_id, text="imok")


def dado(bot, update):
    """
        Lanza un dado de 6 caras
    """
    authorization = auth(bot, update)
    if authorization is 0:
        dadillo = random.randrange(1, 6)
        bot.sendMessage(update.message.chat_id, text=dadillo)


def man(bot, update, args):
    """
    Busca la pagina man del comando indicado
    Permite especificar el sistema y distro en una amplia lista.
    """
    authorization = auth(bot, update)
    if authorization is 0:
        # Comprueba solo dos argumentos
        if len(args) > 2 or len(args) == 0:
            message = "Uso de man: comando distro(opcional, por defecto Debian)"
        else:
            # Ponemos el comando en minusculas
            command = args[0].lower()
            if len(args) == 2 and args[1]:
                # Apaño para facilitar la búsqueda:
                if not args[1][0].isupper():
                    # Si la primera es minúscula, capitalizamos
                    distro = args[1].capitalize()
                else:
                    # Si no, asumimos que se ha escrito así a conciencia y pasamos literalmente
                    distro = args[1]
            else:
                # Por defecto, si no hay segundo argumento
                distro = "Debian"
            # Construimos la URL con ls parametros
            man_url = 'http://www.polarhome.com/service/man'
            man_params = {'qf': command, 'af': 0, 'sf': 0, 'of': distro, 'tf': 0}
            # ARRE!
            try:
                man_page = requests.get(man_url, params=man_params)
            except requests.exceptions.RequestException as requesterror:
                message = "¡El servicio MAN no está disponible!"
                print(requesterror)
            # Valoramos, construimos el mensaje chachipiruli
            if "No man pages for" in man_page.text:
                message = "No hay paginas man para " + command + " en el servidor " + distro + "."
            else:
                message = "Comando " + command + " para " + distro + "\n" + man_page.text[62:500] + \
                          "\n Página completa en: \n" + man_page.url
        # Habla por esa boca
        bot.sendMessage(update.message.chat_id, text=message)


def abogadochat(bot, update):
    """
       Grosería inspirada en una broma del trabajo
    """
    authorization = auth(bot, update)
    if authorization is 0:
        msg = update.message.text.lower()
        if msg[-3:] == "ado" and "colgado" not in msg:
            bot.sendMessage(update.message.chat_id, text="Como lo que tengo aquí colgado...")
            bot.sendPhoto(update.message.chat_id, photo='https://www.fernandezcordero.net/imagenes/colgado.jpg')
            bot.sendMessage(update.message.chat_id, text="Lo siento, me han programado así...")

        if "colgado" in msg and "abogado" not in msg:
            bot.sendMessage(update.message.chat_id, text="Como el abogado...")
            bot.sendPhoto(update.message.chat_id, photo='https://www.fernandezcordero.net/imagenes/imean.jpg')
            bot.sendMessage(update.message.chat_id, text="Lo siento, me han programado así...")


def main():
    """
    Lanza la lógica del programa
    """

    token = (os.environ['TOKEN'])

    if token is None:
        print("Please, configure your token first")
        sys.exit(1)

    updater = Updater(token)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", ayuda))
    dispatcher.add_handler(CommandHandler("tiempo", tiempo, pass_args=True))
    dispatcher.add_handler(CommandHandler("info", info, pass_args=True))
    dispatcher.add_handler(CommandHandler("buscar", buscar, pass_args=True))
    dispatcher.add_handler(CommandHandler("dado", dado, pass_args=False))
    dispatcher.add_handler(CommandHandler("ruok", ruok, pass_args=False))
    dispatcher.add_handler(CommandHandler("jerigonzo", jerigonzo, pass_args=True))
    dispatcher.add_handler(CommandHandler("man", man, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler([Filters.text], abogadochat))

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
