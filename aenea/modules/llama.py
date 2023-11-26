#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
llama - Resources to allow Aeneabot contact with sidecar running Ollama
"""

import requests
import uuid
import json


import modules.initconfig as config
import modules.security as security


def ollama(prompt):
    # Make the request to the OLLAMA API
    # Look, we use a fixed context to try to force all contact as a single conversation
    service = "OLLAMA"
    try:
        config.logger.info('Calling OLLAMA API')
        request_url = config.ollama_url + "/api/generate"
        response = requests.post(
            request_url,
            headers={
                'Content-Type': f'application/json',
                'Connection': f'keep-alive'
            },
            json={
                  "model": config.ollama_model,
                  "prompt": prompt,
                  "stream": False,
                  "context": [
                      31822, 13, 8458, 31922, 3244, 31871, 13, 13, 17160, 1382, 322, 308, 1611, 31825, 31843, 864,
                      397, 260, 2085, 8825, 31843, 864, 3619, 2724, 266, 1153, 365, 473, 31843, 864, 397, 1483,
                      27288, 31844, 5610, 289, 955, 31843, 1408, 266, 3109, 1988, 260, 2061, 31844, 365, 499, 553,
                      1153, 289, 3619, 11092, 291, 1556, 609, 31843, 13, 13, 13, 8458, 31922, 9779, 31871, 13,
                      31918, 31839, 31846, 31881, 31838, 13, 13, 8458, 31922, 13166, 31871, 13, 312, 31876, 31836,
                      10157, 31844, 504, 635, 2666, 289, 333, 363, 4447, 288, 553, 2061, 31843, 9410, 365, 3281,
                      1673, 515, 351, 541, 1132, 405, 19460, 553, 2061, 560, 342, 312, 473, 2803, 365, 1481,
                      31902
                  ],
                }
        )
        print(response.status_code, response.json())
        if response.status_code != 200:
            result = response.json()
            trace_uuid = uuid.uuid1()
            api_error_message = (result['error'])
            config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, api_error_message))
            final_result = 'AI interface not available - %s - UUID %s' % (api_error_message, trace_uuid)
        else:
            result = response.json()
            final_result = (result['response'])
            total_duration = (result['total_duration']/1000000000)
            config.logger.info('%s request took %s secs in total.' % (service, total_duration))
    except RuntimeError as e:
        trace_uuid = uuid.uuid1()
        config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, e))
        final_result = 'AI interface not available. Unexpected error UUID %s' % trace_uuid
    return final_result


async def handle_message(update, context):
    # Use the OpenAI API to generate a response based on the user's input
    auth_try = security.auth(update, context)
    if auth_try[0]:
        response = ollama(update.message.text)
        # Send the response back to the user
        message = response
    elif not auth_try[0]:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


def check_ollama():
    # Simple connectivity checkout
    codes = [200, 401]
    try:
        message = config.url_checker(config.ollama_url, codes)
        message = "\U00002705  Ollama " + message
    except:
        message = "\U0000274C  Ollama " + message
    return message
