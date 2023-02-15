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

from telegram import Update
from telegram.ext import Application, Updater, ContextTypes, CommandHandler, MessageHandler, filters

# Environment
token = os.getenv('TOKEN', default=None)
botname = os.getenv('BOTNAME', default="AeneaBot")
authuser = os.getenv('AUTHUSER', default="User")
loglevel = os.getenv('LOGLEVEL', default="INFO")
chatgpttoken = os.getenv('CHATGPTTOKEN', default=None)
chatgptperson = os.getenv('CHATGPTPERSON', default="Professional")
chatgptmodel = os.getenv('CHATGPTMODEL', default="text-davinci-003")

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


def auth(update, context):
    """
    Stupid auth function. dafuq
    """
    user = update.message.from_user.username  # Received username
    if user == authuser:
        logger.debug('User "%s" allowed' % user)
        return True
    else:
        logger.warning('User "%s" not allowed' % user)
        return False


# Telegram CommandHandlers

async def help(update, context):
    """
    Help Function
    """
    if auth(update, context):
        help_message = "Hi, I'm " + botname + ", service bot. Not any function defined yet."
        await update.effective_message.reply_text(help_message)


async def ruok(update, context):
    """
    Authentication Function
    """
    if auth(update, context):
        await update.effective_message.reply_text("imok")


async def dice(update, context):
    """
    Run a 6 sided dice
    """
    if auth(update, context):
        await update.effective_message.reply_text(random.randrange(1, 6))


async def man(update, context):
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
    await update.effective_message.reply_text(message)


async def unknown(update, context):
    """
    Fallback MessageHandler for unrecognized commands
    """
    await update.effective_message.reply_text("Sorry, I didn't understand.")
    logger.debug('Invalid command')


# ChatGPT Integration
def openAI(prompt):
    # Make the request to the OpenAI API
    response = requests.post(
        'https://api.openai.com/v1/completions',
        headers={'Authorization': f'Bearer {chatgpttoken}'},
        json={'model': chatgptmodel, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 200}
    )

    result = response.json()
    final_result = ''.join(choice['text'] for choice in result['choices'])
    return final_result


async def handle_message(update, context):
    # Use the OpenAI API to generate a response based on the user's input
    response = openAI(update.message.text)
    # Send the response back to the user
    await update.effective_message.reply_text(response)


def bot_routine():
    """
    Runs the bot logic
    """

    logger.info("Running " + botname + "...")
    # If no Telegram Token is defined, we cannot work
    if token is None:
        logger.error("TOKEN is not defined. Please, configure your token first")
        sys.exit(1)
    # If no ChatGPT Token is used, only defined responses here.
    if chatgpttoken is None:
        logger.warning("CHATGPTTOKEN is not defined. Bot will only answer to the commands and functiones specified in this code")

    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("ruok", ruok))
    application.add_handler(CommandHandler("man", man))
    # failover handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    # chatgpt when no command
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    logger.info(botname +" Bot Stopped")


def main():
    """
    Magic
    """
    
    bot_routine()


if __name__ == "__main__":
    main()
