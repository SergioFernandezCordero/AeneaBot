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
import modules.prometheus as prometheus


def ollama(prompt):
    # Make the request to the OLLAMA API
    # Look, we use a fixed context to try to force all contact as a single conversation
    prometheus.bot_call.inc(1)
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
            prometheus.bot_call_error.inc(1)
            result = response.json()
            trace_uuid = uuid.uuid1()
            api_error_message = (result['error'])
            config.logger.error('%s uuid: %s - %s' % (service, trace_uuid, api_error_message))
            final_result = 'AI interface not available - %s - UUID %s' % (api_error_message, trace_uuid)
        else:
            result = response.json()
            final_result = (result['response'])
            total_duration = float((result['total_duration']/1000000000))
            load_duration = float((result['load_duration']/1000000000))
            eval_duration = float((result['eval_duration']/1000000000))
            try:
                prometheus.bot_call_success.inc(1)
                prometheus.ollama_response_total.observe(total_duration)
                prometheus.ollama_response_load.observe(load_duration)
                prometheus.ollama_response_eval.observe(eval_duration)
            except:
                config.logger.error('Error in generating prometheus metrics')
            config.logger.info('%s request took %s secs in total.' % (service, total_duration))
    except (RuntimeError, requests.RequestException) as e:
        prometheus.bot_call_error.inc(1)
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
        service_url = config.ollama_url + "/api/tags"
        check_service = requests.get(
            service_url
        )
        check_service.raise_for_status()
        message_service = "\U00002705  Ollama service is ready"
    except requests.exceptions.HTTPError as err:
        message_service = "\U0000274C  Ollama service is not available: " + err
    except requests.exceptions.Timeout:
        message_service = "\U0000274C  Ollama service is unreachable: Timeout"
    except requests.exceptions.RequestException:
        message_service = "\U0000274C  Ollama service is down"
    try:
        model_url = config.ollama_url + "/api/show"
        check_model = requests.post(
            model_url,
            headers={
                'Content-Type': f'application/json',
                'Connection': f'keep-alive'
            },
            json={
                 "name": config.ollama_model
            }
        )
        check_model.raise_for_status()
        message_model = "\U00002705  Ollama model " + config.ollama_model + " is loaded and ready."
    except requests.exceptions.HTTPError as err:
        message_model = "\U0000274C  Ollama model " + config.ollama_model + " is not loaded."
    except requests.exceptions.RequestException as e:
        message_model = "\U0000274C  Ollama model cannot be checked, Ollama service down or unreachable."
    message = message_service + "\n" + message_model
    return message
