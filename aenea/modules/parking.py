#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Parking - Tools for Parking funtionality
"""

import os
import sqlite3
from sqlite3 import Error
from datetime import datetime

import modules.initconfig as config
import modules.security as security

# Parking Queries
sql_create_parking_table = """CREATE TABLE IF NOT EXISTS parking (
                                        object text NOT NULL,
                                         add_date text
                                    );"""
sql_check_parking_exists = """SELECT name FROM sqlite_master WHERE type='table' AND name='parking'"""
sql_create_parking_query = """INSERT INTO parking VALUES(?,?);"""
sql_list_parking_objects = """SELECT rowid,object,add_date FROM parking ORDER BY add_date"""
sql_clear_parking_object = """DELETE FROM parking WHERE rowid = (?)"""
sql_clear_parking = """DELETE FROM parking"""

class TheValet:
    def __init__(self, dbname):
        """ Open connection to local database file. Create it if doesn't exist """
        try:
            self.dbname = dbname
            self.conn = sqlite3.connect(dbname)
        except ConnectionError as e:
            config.logger.error('Unable to conect Database: ' + str(e))

    def closedb(self):
        """ Close connection to local database """
        self.conn.close()

    def check(self):
        """ Run some checks to determine the correct working of the database """
        try:
            stmt = sql_check_parking_exists
            self.conn.execute(stmt)
            self.conn.commit()
        except Error as e:
            config.logger.error('Parking table not available: ' + str(e))
 

    def setup(self):
        """ Initialize Parking database at startup creating table parking if it doesn't exists """
        try:
            stmt = sql_create_parking_table
            self.conn.execute(stmt)
            self.conn.commit()
        except Error as e:
            config.logger.error('Unable to create Parking table: ' + str(e))

    def park_object(self, item_text, date):
        """ Insert and object in parking table based on user input """
        try:
            stmt = sql_create_parking_query
            args = (item_text, date,)
            self.conn.execute(stmt, args)
            self.conn.commit()
        except Error as e:
            config.logger.error('Unable to Park object: ' + str(e))

    def list_objects(self):
        """ List all objects in the parking table. Return a tuple """
        try:
            stmt = sql_list_parking_objects
            self.conn.commit()
            return self.conn.execute(stmt)
        except Error as e:
            config.logger.error('Unable to list parked objects: ' + str(e))

    
    def clear_object(self, rowid):
        """ Delete an object in the parking table based on input """
        try:
            stmt = sql_clear_parking_object
            args = (rowid,)
            self.conn.execute(stmt, args)
            self.conn.commit()
        except Error as e:
            config.logger.error('Unable to clear object from parking: ' + str(e))


    def empty_parking(self):
        """ Deletes al rows in parking table """
        try:
            stmt = sql_clear_parking
            self.conn.execute(stmt)
            self.conn.commit()
        except Error as e:
            config.logger.error('Unable to empty Parking: ' + str(e))


# Let's give the keys to the Valet

dbname = config.sqlitepath + '/' + 'aenea.db'
config.logger.info('Initializing PARKING database')
if os.path.exists(config.sqlitepath) and os.path.isdir(config.sqlitepath):
    try:
        valet = TheValet(dbname)
        config.logger.info('SQLITE ' + sqlite3.version + ' initialization successful on ' + dbname)
    except:
        config.logger.error('Unable to initialize PARKING')
else:
    config.logger.error('Unable to initialize PARKING: Path ' + dbname + ' is unavailable.' )

def health():
    """ Runs healthcheck """
    try:
        try:
            valet.check()
            message = "\U00002705  Parking table is available"
        except:
            message = "\U0000274C  Parking table doesn't exists"
    except:
        config.logger.error('Unknown error accessing database')
        message = "\U0001F605  Unknown error accessing database"
    return message

def prepare_parking_db():
    """ Initializes Parking table if doesn't exists """
    try:
        valet.setup()
        config.logger.info('Initialized Parking table')
    except:
        config.logger.error('Unable to initialize Parking table')

def close_parking_db():
    """ Closes DB connections explicitly to avoid corruption """
    try:
        valet.closedb()
        config.logger.info('Parking Database connection correctly done.')
    except Error as e:
        config.logger.error('There was a problem closing connection to Parking Database')

async def park(update,context):
    """ Inserts a new Object in the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        if len(context.args) > 0:
            # Insert values
            object = " ".join(context.args)
            current_date = datetime.today().strftime('%d-%m-%Y')
            try:
                valet.park_object(object,current_date)
                config.logger.info('Object successfully parked')
                message = "Parked!"
            except:
                config.logger.error('Unable to park object')
                message = "Unable to park item"
        else:
            message = "Nothing to park!"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


async def list(update,context):
    """ Lists a table with all the object in the Parking with its IDs """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        try:
            # Get values
            message = []
            if valet.list_objects():
                objects = valet.list_objects()
                objects = objects.fetchall()
                if len(objects) > 0:
                    message.append('This is a list of the objects currently in the parking:\n')
                    for row in objects:
                        message.append('| ' + str(row[0]) + ' | ' + row[2] + ' | ' + row[1] + ' |')
                    message =  "\n".join(message)
                else:
                    message = "Parking is currently empty."
        except:
            config.logger.error('Unable to list parked objects')
            message == message.append('Unable to list parked objects')
            message =  "\n".join(message)
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)

async def clear(update,context):
    """ Clears an object from the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        if len(context.args) > 0:
            # Insert values
            rowid = context.args[0]
            try:
                valet.clear_object(rowid)
                message = "Object " + rowid + " cleared from Parking!"
            except:
                config.logger.error('Unable to clear item from the Parking')
                message = "Unable to clear item from the Parking"
        else:
            message = "Nothing to clear!"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)
    
async def clearall(update,context):
    """ Clear all object in the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        try:
            valet.empty_parking()
            config.logger.info('Parking emptied successfully.')
            message = "Parking emptied! See you soon!"
        except:
            config.logger.error('Unable to empty the Parking')
            message = "Unable to empty the Parking"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)
