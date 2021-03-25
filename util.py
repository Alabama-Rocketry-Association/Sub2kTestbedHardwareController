import logging

global LOGGER 

LOGGER = logging.getLogger()

from ruamel.yaml import YAML
import logging
import asyncio
import os
from queue import LifoQueue as stack
import json
from sys import getsizeof as sizeof
import threading
import pickle

def load_config(cfg = "config.yaml"):
    y = YAML()
    with open(cfg, "r") as f:
        config = y.load(f)
        return config

def init_logger(logfile:str, level = logging.INFO):
    logging.basicConfig(filename=logfile, level=level)
    logging.getLogger("init_logger").info(f"Logger initialized, logging to {logfile} @level={level}")
