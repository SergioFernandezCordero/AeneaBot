#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
initconfig - Initial Configuration modules
"""

import logging
import os
import sys
import requests
import yaml
from pathlib import Path


class ConfigLoader:
    def __init__(self):
        self.data = []

    @staticmethod
    def load_config(config_path: str = os.path.dirname(sys.argv[0]) + "/config/config.yml") -> dict:
        """Load and parse a YAML configuration file."""
        try:
            # Use Path to handle file paths cross-platform
            with open(Path(config_path), "r") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found at: {config_path}")
            raise RuntimeError(f"Config file not found at: {config_path}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise RuntimeError(f"Failed to parse YAML: {e}")


# Load configuration file
configLoad = ConfigLoader()
configuration = configLoad.load_config()

# Generate variables from config file
for key in configuration:
    exec(f"{key} = configuration['{key}']")

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=loglevel)
logger = logging.getLogger(__name__)


def url_checker(url, codes):
    try:
        # Get Url
        get = requests.get(url)
        # if the request succeeds
        if get.status_code in codes:
            message = f"is reachable"
        else:
            message = f"is NOT reachable with code: {get.status_code}"
    # Exception
    except requests.exceptions.RequestException as e:
        # print URL with Errs
        message = f"is NOT reachable \nErr: {e}"
    return message
