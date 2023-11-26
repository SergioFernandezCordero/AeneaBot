#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Aenea - Service bot from ElAutoestopista
"""

import sys
import random
import re
import requests
import uuid

from telegram import Update
from telegram.ext import Application, Updater, ContextTypes, CommandHandler, MessageHandler, filters

import modules.initconfig as config
import modules.security as security
import modules.parking as parking
import modules.llama as llama


# Tools

def error(update, context):
    """
    Logs execution errors
    """
    service = "TELEGRAM"
    trace_uuid= uuid.uuid1()
    config.logger.warning('%s uuid: %s - Update "%s" caused error "%s"' % (service, trace_uuid, update, context.error))


def check_telegram():
    codes = [200]
    try:
        message = config.url_checker("https://api.telegram.org/bot"+config.token+"/getMe", codes)
        message = "\U00002705  Telegram " + message
    except:
        message = "\U0000274C  Telegram " + message
    return message


async def health(update, context):
    """
    Run a healthcheck
    """
    auth_try= security.auth(update, context)
    message_list = []
    if auth_try[0]:
        message_list.append(parking.health())
        message_list.append(llama.check_ollama())
        message_list.append(check_telegram())
    elif not auth_try[0]:
        message_list.append(auth_try[1])
    message = "\n".join(message_list)
    await update.effective_message.reply_text(message)


async def dice(update, context):
    """
    Run a 6 sided dice
    """
    auth_try= security.auth(update, context)
    if auth_try[0]:
        message = random.randrange(1, 6)
    elif not auth_try[0]:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


async def man(update, context):
    """
    Lookup a command for selected distro and SO into manpages
    """
    service = "MAN"
    auth_try= security.auth(update, context)
    if auth_try[0] and 0 < len(context.args) < 3:
        command = context.args[0]
        command = command.lower()
        if len(context.args) == 2:
            distro = context.args[1]
        else:
            distro = "Debian"
        if not distro.isupper():
            distro = distro.capitalize()
        man_url = 'http://www.polarhome.com/service/man'
        man_params = {'qf': command, 'af': 0, 'sf': 0, 'of': distro, 'tf': 0}
        try:
            manpage = requests.get(man_url, params=man_params)
            if re.search('No man pages for', manpage.text):
                message = "No man pages for " + command + " on server " + distro + "."
            else:
                message = "Command " + command + " for " + distro + "\n" + manpage.text[62:500] + \
                          "\n Full page on: \n" + manpage.url
        except requests.exceptions.RequestException as requesterror:
            trace_uuid= uuid.uuid1()
            error_message = "MAN service unavailable at " + man_url
            config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, error_message))
            message = 'An error has occurred, UUID %s' % (trace_uuid)
    elif not auth_try[0]:
        message = auth_try[1]
    elif len(context.args) != 2:
        message = "Usage: /man command distro(optional, defaults to Debian)"
    await update.effective_message.reply_text(message)


async def unknown(update, context):
    """
    Fallback MessageHandler for unrecognized commands
    """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        message = "Sorry, I didn't understand."
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


def bot_routine():
    """
    Runs the bot logic
    """
    config.logger.info("Running " + config.botname + "...")
    # If no Telegram Token is defined, we cannot work
    if config.token is None:
        config.logger.error("TOKEN is not defined. Please, configure your token first")
        sys.exit(1)
    application = Application.builder().token(config.token).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("health", health))
    application.add_handler(CommandHandler("man", man))

    # Deploy Parking module DB
    parking.prepare_parking_db()

    # Parking commands
    application.add_handler(CommandHandler("park", parking.park))
    application.add_handler(CommandHandler("list_parking", parking.list))
    application.add_handler(CommandHandler("clear_object", parking.clear))
    application.add_handler(CommandHandler("clear_parking", parking.clearall))

    # fail over handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # Ollama will be invoked when no command is specified
    application.add_handler(MessageHandler(filters.TEXT, llama.handle_message))

    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

    # Run the bot until when you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # Close database connection gracefully
    parking.close_parking_db()
    config.logger.info(config.botname + " Bot Stopped")


def main():
    """
    Magic
    """
    
    bot_routine()


if __name__ == "__main__":
    main()
