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
import uuid

import sqlite3
from sqlite3 import Error

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
sqlitepath = os.getenv('AENEADB', default="/sqlite")

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=loglevel)
logger = logging.getLogger(__name__)

# Tools

def error(update, context):
    """
    Logs execution errors
    """
    service = "TELEGRAM"
    trace_uuid= uuid.uuid1()
    logger.warning('%s uuid: %s - Update "%s" caused error "%s"' % (service, trace_uuid, update, context.error))

def auth(update, context):
    """
    Stupid auth function. dafuq
    """
    service = "AUTH"
    trace_uuid= uuid.uuid1()
    user = update.message.from_user.username  # Received username
    if user == authuser:
        error_message = 'User "%s" allowed' % user
        logger.debug('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        auth = True
    else:
        error_message = 'User "%s" not allowed' % user
        logger.warning('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        auth = False
    return auth, error_message
    
# Database manager

def create_sqlite_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    logger.info('Initializing SQLITE database on '+ db_file)
    if os.path.exists(sqlitepath) and os.path.isdir(sqlitepath):
        try:
            conn = sqlite3.connect(db_file)
            logger.info(sqlite3.version + ' initialization successful')
        except Error as e:
            logger.error('Unable to initialize SQLITE: ' + str(e) )
        finally:
            if conn:
                conn.close()
    else:
        logger.error('Unable to initialize SQLITE: Path ' + db_file + ' is unavailable.' )
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logger.error("Error creating table: " + str(e))

# Tables definition

# Parking
sql_create_parking_table = """ CREATE TABLE IF NOT EXISTS parking (
                                        object text NOT NULL,
                                        add_date text
                                    ); """
            
# Telegram CommandHandlers

async def ruok(update, context):
    """
    Authentication Function
    """
    auth_try= auth(update, context)
    if auth_try[0] == True:
        message = "imok"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


async def dice(update, context):
    """
    Run a 6 sided dice
    """
    auth_try= auth(update, context)
    if auth_try[0] == True:
        message = random.randrange(1, 6)
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


async def man(update, context):
    """
    Lookup a command for selected distro and SO into manpages
    """
    service = "MAN"
    auth_try= auth(update, context)
    if auth_try[0] == True and 0 < len(context.args) < 3:
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
            logger.error('%s uuid: %s - %s' % (service, trace_uuid, error_message))
            message = 'An error has occurred, UUID %s' % (trace_uuid)
    elif auth_try[0] == False:
            message = auth_try[1]
    elif len(context.args) != 2:
            message = "Usage: /man command distro(optional, defaults to Debian)"
    await update.effective_message.reply_text(message)


async def unknown(update, context):
    """
    Fallback MessageHandler for unrecognized commands
    """
    auth_try= auth(update, context)
    if auth_try[0] == True:
        message = "Sorry, I didn't understand."
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


# ChatGPT Integration
def openAI(prompt):
    # Make the request to the OpenAI API
    # Patch to deal with OpenAI error like, in my case, quota errors.
    # TODO: Put this in a generic error with uuid function
    service = "OPENAI"
    try:
        logger.info('Calling OpenAI API')
        response = requests.post(
            'https://api.openai.com/v1/completions',
            headers={'Authorization': f'Bearer {chatgpttoken}'},
            json={'model': chatgptmodel, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 200, 'user': authuser}
        )

        result = response.json()
        result_code = response.status_code
        if result_code !="200":
            raise RuntimeError
        else:
            final_result = ''.join(choice['text'] for choice in result['choices'])
    except RuntimeError:
        trace_uuid= uuid.uuid1()
        api_error_type = (result['error']['type'])
        api_error_message =  (result['error']['message'])
        error_message = api_error_type+": "+api_error_message
        logger.error('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        final_result = 'An error has occurred, UUID %s' % (trace_uuid)
    return final_result


async def handle_message(update, context):
    # Use the OpenAI API to generate a response based on the user's input
    auth_try= auth(update, context)
    if auth_try[0] == True:
        response = openAI(update.message.text)
        # Send the response back to the user
        message = response
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


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

    ########################################
    # Initialize SQLite Database Connection#
    ########################################
    #Initialize databse connection
    aeneadb = create_sqlite_connection(sqlitepath + "/aenea.db")

    #Parking table nitialization
    logger.info('Initializing PARKING table')
    create_table(aeneadb, sql_create_parking_table)

    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
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
