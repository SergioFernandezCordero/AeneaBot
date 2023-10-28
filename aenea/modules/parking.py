#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Parking - Tools for Parking funtionality
"""

import modules.initconfig as config
import modules.aeneasql as aeneasql

# Parking
sql_create_parking_table = """ CREATE TABLE IF NOT EXISTS parking (
                                        object text NOT NULL,
                                        add_date text
                                    ); """