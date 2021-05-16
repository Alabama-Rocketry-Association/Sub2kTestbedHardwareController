import sys
import os
from pipyadc.ADS1256_definitions import *
from pipyadc import ADS1256
import numpy as np
from collections import deque

MOVAVERAGE = lambda x, w: np.convolve(x, np.ones(w), mode="valid")/w

def MAFilter(updated_value, n=45):
    """
    Moving Average Filter of ADC Data stream
    """
    MA = lambda data: MOVAVERAGE(data, w=n)
    values= deque(maxlen=n)
    if len(values) < n:
        values.append(updated_value)
        yield None
    elif len(values) == n:
        values.popleft()
        values.append(updated_value)
        yield MA(values)

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")

#differential channels on the ADS1256
DIFF1 = POS_AIN0|NEG_AIN1 #LOX1
DIFF2 = POS_AIN2|NEG_AIN3 #LOX2
DIFF3 = POS_AIN4|NEG_AIN5 #RP11
DIFF4 = POS_AIN6|NEG_AIN7 #RP12

#post read processing
global CHANNELS
global CALIBRATION
global ADS
ADS = ADS1256()
ADS.cal_self()
CHANNELS = (DIFF1, DIFF2, DIFF3, DIFF4)
CALIBRATION = [0,0] #(m, b) in y = mx+b
CALIBRATE = lambda val: CALIBRATION[0]*val + CALIBRATION[1]
CALIBRATE_MAP = lambda vals: map(CALIBRATE, vals)

def read_pressure(ch = CHANNELS, keys = ["LOX_1", "LOX_2", "RP1_1", "RP1_2"]):
    global ADS
    readings = map(MAFilter, CALIBRATE_MAP(ADS.read_sequence(ch)))
    if readings[0] ==None:
        return None
    data = dict.fromkeys(keys)
    for reading, key in zip(readings, keys):
        data[key] = reading
    return data 













