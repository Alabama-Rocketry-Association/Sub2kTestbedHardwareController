import logging
import platform
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

def importGPIO():
    #imports either for deploy or virtual testing
    if platform.system().upper() == "WINDOWS":
        from RPiSim.GPIO import GPIO
    elif platform.system.upper() == "LINUX":
        from Rpi.GPIO import GPIO #check actual import name