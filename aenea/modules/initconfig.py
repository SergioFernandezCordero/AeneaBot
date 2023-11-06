#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
initconfig - Initial Configuration modules
"""

import logging
import os
import requests


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

def url_checker(url,codes):
	try:
		#Get Url
		get = requests.get(url)
		# if the request succeeds 
		if get.status_code in codes:
			message = f"{url}: is reachable"
		else:
			message = f"{url}: is not reachable, status_code: {get.status_code}"
	#Exception
	except requests.exceptions.RequestException as e:
        # print URL with Errs
		message = f"{url}: is Not reachable \nErr: {e}"
	return message
