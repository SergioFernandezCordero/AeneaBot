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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


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
    dispatcher.add_handler(CommandHandler("dado", dado, pass_args=False))
    dispatcher.add_handler(CommandHandler("ruok", ruok, pass_args=False))
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
