#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
AeneaSQL - Tools to work with SQLite
"""
import os
import sqlite3
from sqlite3 import Error


import modules.initconfig as config

# Database manager
# Initialization

def create_sqlite_database(db_file,path):
    """ create a database connection to a SQLite database """
    conn = None
    config.logger.info('Initializing SQLITE database on '+ db_file)
    if os.path.exists(path) and os.path.isdir(path):
        try:
            conn = sqlite3.connect(db_file)
            config.logger.info(sqlite3.version + ' initialization successful')
        except Error as e:
            config.logger.error('Unable to initialize SQLITE: ' + str(e) )
        finally:
            if conn:
                conn.close()
    else:
        config.logger.error('Unable to initialize SQLITE: Path ' + db_file + ' is unavailable.' )
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
        config.logger.error("Error creating table: " + str(e))
