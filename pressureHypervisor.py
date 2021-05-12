from pressure_controller import PressureController
from pressureADC import read_pressure
import asyncio
from collections import deque

class PressureHyperVisor():

    """
        Manages pressure data aquisition and PID calculations for the LOX and Rp1 tanks

    """

    def __init__(self, setpoint_rp1, setpoint_lox, gain_rp1:list, gain_lox:list):
        self.LOXVENTPID = PressureController(setpoint_lox, gain_lox, 0.1, lambda x: 0 if (x < 0) else x)
        self.RP1VENTPID = PressureController(setpoint_rp1, gain_rp1, 0.1, lambda x: 0 if (x < 0) else x)
        self.LOX = deque(maxlen=512)
        self.RP1 = deque(maxlen=512)
        self.ERR_LOX = deque(maxlen=512)
        self.ERR_RP1 = deque(maxlen=512)

    async def PressureHandler(self):
        """
        asynchronous function for monitoring pressure in a separate thread
        """
        while 1:
            data = read_pressure()
            self.ERR_LOX.append(self.LOXVENTPID(data["LOX_1"]))
            self.ERR_RP1.append(self.RP1VENTPID(data["RP1_1"]))
            self.LOX.append(data["LOX_1"])
            self.RP1.append(data["RP1_1"])
            await asyncio.sleep(0.1)
    
    def report(self):
        """
        reports pressure state values in dictionary pairs
        LOX -> current lox pressure
        RP1 -> current rp1 pressure
        LOX_ERR -> current LOX pid error
        RP1_ERR -> current RP1 pid error
        """
        
        return {
            "LOX":self.LOX[-1], 
            "RP1":self.RP1[-1],
            "LOX_ERR":self.ERR_LOX[-1],
            "RP1_ERR":self.RP1_ERR[-1] 
            }


