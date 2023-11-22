#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
bard - Resources to allow Aeneabot contact with Google Bard
"""

import uuid

import modules.initconfig as config
import modules.security as security
import google_bard


# Google Bard Integration
def Bard(prompt):
    # Make the request to the Google Bard API
    service = "GOOGLE BARD"
    try:
        config.logger.info('Calling Google BARD API')
        response = google_bard.generate_text(prompt, api_key=config.bardapikey)
        final_result = response
    except RuntimeError:
        trace_uuid = uuid.uuid1()
        config.logger.error('%s uuid: %s' % (service, trace_uuid))
        final_result = ('An error has occurred, UUID %s' %
                        trace_uuid)
    return final_result


async def handle_message(update, context):
    # Use the Google Bard API to generate a response based on the user's input
    auth_try = security.auth(update, context)
    if auth_try[0]:
        response = Bard(update.message.text)
        # Send the response back to the user
        message = response
    elif not auth_try[0]:
        message = auth_try[1]
    await update.effective_message.reply_text(message)


def check_googlebard():
    codes = [200, 401]
    try:
        message = config.url_checker("https://api.openai.com/v1/completions", codes)
        message = "\U00002705  GoogleBard " + message
    except:
        message = "\U0000274C  GoogleBard " + message
    return message
