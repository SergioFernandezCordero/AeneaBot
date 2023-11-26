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
ollama_url = os.getenv('OLLAMA_URL', default="http://localhost:11434")
ollama_model = os.getenv('OLLAMA_MODEL', default="aenea")
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
			message = f"is reachable"
		else:
			message = f"is NOT reachable with code: {get.status_code}"
	#Exception
	except requests.exceptions.RequestException as e:
        # print URL with Errs
		message = f"is NOT reachable \nErr: {e}"
	return message
