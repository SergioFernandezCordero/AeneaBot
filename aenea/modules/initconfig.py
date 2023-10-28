#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
initconfig - Initial Configuration modules
"""

import logging
import os

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
