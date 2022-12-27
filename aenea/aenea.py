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

import re
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Environment
token = os.getenv('TOKEN', default=None)
botname = os.getenv('BOTNAME', default="AeneaBot")
authuser = os.getenv('AUTHUSER', default="User")
loglevel = os.getenv('LOGLEVEL', default="INFO")

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=loglevel)

logger = logging.getLogger(__name__)

# Tools

def error(update, context):
    """
    Logs execution errors
    """
    logger.warning('Update "%s" caused error "%s"' % (update, context.error))


def sendmessage(update, context, message):
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def auth(update, context):
    """
    Stupid auth function. dafuq
    """
    user = update.message.from_user.username  # Received username
    if user == authuser:
        logger.debug('User "%s" allowed' % user)
        return True
    else:
        auth_message = 'You are not allowed to use this bot, ' + str(user)
        sendmessage(update, context, auth_message)
        logger.warning('User "%s" not allowed' % user)
        return False


# Telegram CommandHandlers

def help(update, context):
    """
    Help Function
    """
    if auth(update, context):
        help_message = "Hi, I'm " + botname + ", service bot. Not any function defined yet."
        sendmessage(update, context, help_message)


def ruok(update, context):
    """
    Authenticatin Function
    """
    if auth(update, context):
        sendmessage(update, context, "imok")


def dice(update, context):
    """
    Run a 6 sided dice
    """
    if auth(update, context):
        sendmessage(update, context, random.randrange(1, 6))


def man(update, context):
    """
    Lookup a command for selected distro and SO into manpages
    """
    if auth(update, context) and 0 < len(context.args) < 3:
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
            message = "MAN service unavailable!"
            logger.error('Failed to connect to MAN service: "%s"' % requesterror)
    else:
        message = "Usage: /man command distro(optional, defaults to Debian)"
    sendmessage(update, context, message)


def unknown(update, context):
    """
    Fallback MessageHandler for unrecognized commands
    """
    sendmessage(update, context, "Sorry, I didn't understand that command.")
    logger.debug('Invalid command')

def bot_routine():
    """
    Runs the bot logic
    """

    logger.info("Running " + botname + "...")
    if token is None:
        logger.error("TOKEN is not defined. Please, configure your token first")
        sys.exit(1)

    updater = Updater(token, use_context=True)

    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("dice", dice, pass_args=False))
    dispatcher.add_handler(CommandHandler("ruok", ruok, pass_args=False))
    dispatcher.add_handler(CommandHandler("man", man, pass_args=True))
    # failover handler
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    logger.info(botname +" Bot Running")
    updater.idle()


def main():
    """
    Magic
    """
    
    bot_routine()


if __name__ == "__main__":
    main()
