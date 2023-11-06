#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
chatgpt - Resources to allow Aeneabot contact with ChatGPT
"""

import requests
import uuid


import modules.initconfig as config
import modules.security as security


# ChatGPT Integration
def openAI(prompt):
    # Make the request to the OpenAI API
    # Patch to deal with OpenAI error like, in my case, quota errors.
    # TODO: Put this in a generic error with uuid function
    service = "OPENAI"
    try:
        config.logger.info('Calling OpenAI API')
        response = requests.post(
            'https://api.openai.com/v1/completions',
            headers={'Authorization': f'Bearer {config.chatgpttoken}'},
            json={'model': config.chatgptmodel, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 200, 'user': config.authuser}
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
        config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        final_result = 'An error has occurred, UUID %s' % (trace_uuid)
    return final_result


async def handle_message(update, context):
    # Use the OpenAI API to generate a response based on the user's input
    auth_try= security.auth(update, context)
    if auth_try[0] == True:
        response = openAI(update.message.text)
        # Send the response back to the user
        message = response
    elif auth_try[0] == False:
        message = auth_try[1]
    await update.effective_message.reply_text(message)

def check_chatgpt():
    codes = [200, 401]
    try:
        message = config.url_checker("https://api.openai.com/v1/completions", codes)
        message = "\U00002705  " + message
    except:
        message = "\U0000274C  " + message
