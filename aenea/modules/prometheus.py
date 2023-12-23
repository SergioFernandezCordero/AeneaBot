#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Prometheus - Instrumentation and metrics
"""

from prometheus_client import start_http_server, Counter, Summary, Info
import modules.initconfig as config

# Startup server
if config.prometheus_enabled:
    try:
        start_http_server(config.prometheus_port)
        config.logger.info('Prometheus-exporter up at port ' + str(config.prometheus_port))
    except:
        config.logger.error('Unable to run prometheus-exporter at port' + str(config.prometheus_port))
        pass

# Metrics definitions
# Configuration settings
aeneabot_build = Info('aeneabot_build', 'Running version of AeneaBot')
ollama_model = Info('ollama_model', "Ollama model name")
ollama_url = Info('ollama_url', "Ollama model URL")
# Bot Calls Count
bot_call = Counter('bot_call_total', 'Bot Calls Total')
bot_call_success = Counter('bot_call_success', 'Bot Calls resulting in success')
bot_call_error = Counter('bot_call_error', 'Bot Calls resulting in error')
