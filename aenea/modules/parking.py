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
sql_create_parking_table = """ CREATE TABLE IF NOT EXISTS parking (
                                        object text NOT NULL,
                                        add_date text
                                    ); """
sql_create_parking_query = """INSERT INTO parking VALUES(?,?);"""
sql_list_parking_objects = """SELECT rowid,object,add_date FROM parking ORDER BY add_date"""
sql_clear_parking_object = """DELETE FROM parking WHERE rowid = (?)"""
sql_clear_parking = """DELETE FROM parking"""

class TheValet:
    def __init__(self, dbname):
        try:
            self.dbname = dbname
            self.conn = sqlite3.connect(dbname)
        except Error as e:
            return e


    def setup(self):
        try:
            stmt = sql_create_parking_table
            self.conn.execute(stmt)
            self.conn.commit()
        except Error as e:
            return e

    def park_object(self, item_text, date):
        try:
            stmt = sql_create_parking_query
            args = (item_text, date)
            self.conn.execute(stmt, args)
            self.conn.commit()
        except Error as e:
            return e

    def list_objects(self):
        try:
            stmt = sql_list_parking_objects
            return self.conn.execute(stmt)
        except Error as e:
            return e
    
    def clear_object(self, rowid):
        try:
            stmt = sql_clear_parking_object
            args = (rowid)
            self.conn.execute(stmt, args)
            self.conn.commit()
        except Error as e:
            return e

    def empty_parking(self):
        try:
            stmt = sql_clear_parking
            self.conn.execute(stmt)
            self.conn.commit()
        except Error as e:
            return e

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
    except Error as e:
        config.logger.error('Unable to initialize Parking table: ' + str(e))

async def park(update,context):
    """ Inserts a new Object in the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        if len(context.args) > 0:
            try:
                # Insert values
                object = " ".join(context.args)
                current_date = datetime.today().strftime('%d-%m-%Y')
                valet.park_object(object,current_date)
                message = "Parked!"
            except Error as e:
                config.logger.error('Unable to park object: ' + str(e))
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
            rawmessage = valet.list_objects()
            if rawmessage.rowcount > 0:
                message.append('This is a list of the objects currently in the parking:\n')
                for row in rawmessage.fetchall():
                    message.append('| ' + str(row[0]) + ' | ' + row[2] + ' | ' + row[1] + ' |')
                message =  "\n".join(message)
            else:
                message = "Parking is currently empty."
        except Error as e:
            config.logger.error('Unable to list parked objects: ' + str(e))
            message == 'Unable to list parked objects'
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)

async def clear(update,context):
    """ Clears an object from the Parking """
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        if len(context.args) > 0:
            try:
                # Insert values
                rowid = context.args[0]
                valet.clear_object(rowid)
                message = "Object " + rowid + " cleared from Parking!"
            except Error as e:
                config.logger.error('Unable to clear item from the Parking: ' + str(e))
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
            # Insert values
            valet.empty_parking()
            config.logger.info('Parking emptied successfully.')
            message = "Parking emptied! See you soon!"
        except Error as e:
            config.logger.error('Unable to empty the Parking: ' + str(e))
            message = "Unable to empty the Parking"
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)
