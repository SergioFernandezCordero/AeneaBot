#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Security - Authentication utils
"""

import uuid

import modules.initconfig as config


def auth(update, context):
    """
    Stupid auth function. dafuq
    """
    service = "AUTH"
    trace_uuid= uuid.uuid1()
    user = update.message.from_user.username  # Received username
    if user == config.authuser:
        error_message = 'User "%s" allowed' % user
        config.logger.debug('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        auth = True
    else:
        error_message = 'User "%s" not allowed' % user
        config.logger.warning('%s uuid: %s - %s' % (service, trace_uuid, error_message))
        auth = False
    return auth, error_message
