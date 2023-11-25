#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
llama - Resources to allow Aeneabot contact with sidecar running Ollama
"""

import requests
import uuid


import modules.initconfig as config
import modules.security as security


# ChatGPT Integration
def ollama(prompt):
    # Make the request to the OLLAMA API
    # TODO: Put this in a generic error with uuid function
    service = "OLLAMA"
    try:
        config.logger.info('Calling OLLAMA API')
        response = requests.post(
            config.ollama_url,
            headers={
                'Content-Type': f'application/json',
                'Connection': f'keepalive'
            },
            json={
                  "model": config.ollama_model,
                  "prompt": prompt,
                  "stream": 'false'
                }
        )

        result = response.json()
        result_code = response.status_code
        if result_code != "200":
            raise RuntimeError
        else:
            final_result = (result['response'])
            load_duration = (result['load_duration'])
            sample_duration = (result['sample_duration'])
            config.logger.info('%s Time spent in load %s - Time spent in generating sample %s' % (load_duration, sample_duration))
    except RuntimeError:
        trace_uuid = uuid.uuid1()
        api_error_message = (result['response'])
        config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, api_error_message))
        final_result = 'An error has occurred, UUID %s' % trace_uuid
    return final_result


async def handle_message(update, context):
    # Use the OpenAI API to generate a response based on the user's input
    auth_try= security.auth(update, context)
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
