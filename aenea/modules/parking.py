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

# Parking
sql_create_parking_table = """ CREATE TABLE IF NOT EXISTS parking (
                                        object text NOT NULL,
                                        add_date text
                                    ); """
sql_create_parking_query = '''INSERT INTO parking VALUES(?,?); '''


class TheValet:
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = sql_create_parking_table
        self.conn.execute(stmt)
        self.conn.commit()

    def park_object(self, item_text, date):
        stmt = sql_create_parking_query
        args = (item_text, date)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def list_objects(self):
        stmt = "SELECT description FROM items"
        return [x[0] for x in self.conn.execute(stmt)]
    
    def clear_object(self, item_text):
        stmt = "DELETE FROM items WHERE rowid = (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def empty_parking(self, item_text):
        stmt = "DELETE FROM parking"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

# Let's give the keys to the Valet

dbname = config.sqlitepath + '/' + 'aenea.db'
config.logger.info('Initializing PARKING database')
if os.path.exists(config.sqlitepath) and os.path.isdir(config.sqlitepath):
    try:
        valet = TheValet(dbname)
        config.logger.info('SQLITE ' + sqlite3.version + ' initialization successful on ' + dbname)
    except Error as e:
        config.logger.error('Unable to initialize PARKING: ' + str(e) )
else:
    config.logger.error('Unable to initialize PARKING: Path ' + dbname + ' is unavailable.' )

def prepare_parking_db():
    """ Initializes Parking table if doesn't exists """
    config.logger.info('Initializing Parking table')
    try:
        valet.setup
    except:
        config.logger.error('Unable to initialize Parking table')

async def park(update,context):
    """ Inserts a new Object in the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        try:
            # Insert values
            object = " ".join(context.args)
            current_date = datetime.today().strftime('%d-%m-%Y')
            valet.park_object(object,current_date)
            message = "Parked!"
        except:
            config.logger.error('Unable to park item')
            message = "Unable to park item"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


async def list(update,context):
    """ Lists a table with all the object in the Parking with its IDs """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        try:
            # Insert values
            object = " ".join(context.args)
            valet.list_objects(object)
        except:
            config.logger.error('Unable to park item')
            message == str(e)
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)

async def clear():
    """ Clears an object from the Parking """
    print()

def clearall():
    """ Clear all object in the Parking """
    print()
