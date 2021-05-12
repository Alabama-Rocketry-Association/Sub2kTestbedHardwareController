from loadcell import LoadCellManager, DataRecorder, LoadCellDataRecorderKeys
from net import NetworkServer
import pandas as pd
import websockets as ws
import RPi.GPIO as GPIO
import logging
import asyncio
import datetime
from pressurehypervisor import PressureHyperVisor
dtime = lambda : datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
from time import sleep
from errno import EWOULDBLOCK
import sh
GPIO.setmode(GPIO.BCM)
global LOGFILE
LOGFILE = f"SYSTEM_LOG-{dtime()}.log"
logging.basicConfig(filename=LOGFILE, level=logging.INFO)

"""
    CONTROLS 16CH RELAY BOARD FOR RP1/LOX TEST STAND
    4/15/2021
    JONATHAN MARTINI
"""
              #single board computer
global SYSTEMCONFIG     #testbed states

#GPIO STATES
"""
    Fine for basic proof-of-concept, move to .yaml/.json configuration for robust settings

"""
SYSTEMCONFIG = {
    #two ways
    "Solenoid1": {"GPIO": 1, "Mode": 0, "Name": "2 Way Tank Press", "Status": ""},
    "Solenoid2": {"GPIO": 20, "Mode": 0, "Name": "2 Way RP1 Vent","Status": ""},
    "Solenoid3": {"GPIO": 21, "Mode": 0, "Name": "2 Way LOX Vent","Status": ""},
    "Solenoid4": {"GPIO": 16, "Mode": 0, "Name": "2 Way RP1 Chamber","Status": ""},
    "Solenoid5": {"GPIO": 12, "Mode": 0, "Name": "2 Way Lox Chamber","Status": ""},
    #3 ways
    "Solenoid6": {"GPIO": 7, "Mode": 1, "Name": "TANK PRESS","Status": ""},
    "Solenoid7": {"GPIO": 8, "Mode": 1, "Name": "RP1 VENT","Status": ""},
    "Solenoid8": {"GPIO": 25, "Mode": 1, "Name": "LOX VENT","Status": ""},
    "Solenoid9": {"GPIO": 24, "Mode": 1, "Name": "RPI TO CHAMBER VALVE","Status": ""},
    "Solenoid10": {"GPIO": 23, "Mode": 1, "Name":"LOX TO CHAMBER VALVE", "Status":""},
    "Igniter": {"GPIO": 22, "Mode": 1, "Name": "Ignition", "Status": ""}
}

def event(msg, number, loggerName, status=""):
    #logging utility
    v = "Solenoid" + str(number)
    logger = logging.getLogger(loggerName)
    logger.info(f"{v}\t {SYSTEMCONFIG[v]['Name']}: {msg}")
    SYSTEMCONFIG[v]["Status"] = status


def init_gpio():
    #initializes all of the gpio pins from the system config dict
    logger = logging.getLogger("GPIO INITIALIZATION")
    global SYSTEMCONFIG
    
    
    for key in SYSTEMCONFIG.keys():
        print(key)
        if "Solenoid" in key:
            try:
                
                GPIO.setup(SYSTEMCONFIG[key]["GPIO"], GPIO.OUT)
                GPIO.output(SYSTEMCONFIG[key]["GPIO"], SYSTEMCONFIG[key]["Mode"])
                SYSTEMCONFIG[key]["Status"] = "Initialized"
                logger.info(f"Initialized Solenoid: {SYSTEMCONFIG[key]['Name']} GPIO {SYSTEMCONFIG[key]['GPIO']}")
            except BaseException as e:
                print(e)
                SYSTEMCONFIG[key]["Status"] = f"FAILED INIT {e}"
                logger.info(f"GPIO {SYSTEMCONFIG[key]['GPIO']} Failed to Initialize")
        if key == "Igniter":
            try:
                
                GPIO.setup(SYSTEMCONFIG[key]["GPIO"], GPIO.OUT)
                GPIO.output(SYSTEMCONFIG[key]["GPIO"], SYSTEMCONFIG[key]["Mode"])
                logger.info(f"Initialized Ignition GPIO {SYSTEMCONFIG[key]['GPIO']}")
            except BaseException as e:
                print(e)
                SYSTEMCONFIG[key]["Status"] = f"FAILED INIT {e}"
                logger.info(f"GPIO {SYSTEMCONFIG[key]['GPIO']} Failed to Initialize")
 
def reset_gpio():
    #resets all of the gpio states
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    

def press_tanks():
    GPIO.output(SYSTEMCONFIG["Solenoid7"]["GPIO"], GPIO.LOW)
    event("Pressed Tanks", 6, "Tank Pressing", "Pressed")

def depress_tanks():
    GPIO.output(SYSTEMCONFIG["Solenoid7"]["GPIO"], GPIO.HIGH)
    event("Tanks Unpressed", 6, "Tank Pressing", "Unpressed")

def LOXVentOn():
    GPIO.output(SYSTEMCONFIG["Solenoid7"]["GPIO"], GPIO.LOW)   
    event("Lox Venting In Progress", 7, "Lox Venting System", "Venting")

def LOXVentOff():
    GPIO.output(SYSTEMCONFIG["Solenoid8"]["GPIO"], GPIO.HIGH)  
    event("Lox Venting Ended", 7, "Lox Venting System", "Closed")

def RP1VentOn():
    GPIO.output(SYSTEMCONFIG["Solenoid8"]["GPIO"], GPIO.LOW) 
    event("Rp1 Venting In Progress", 8, "RP1 Venting System", "Venting")

def RP1VentOff():
    GPIO.output(SYSTEMCONFIG["Solenoid8"]["GPIO"], GPIO.HIGH)  
    event("RP1 Venting Ended", 8, "RP1 Venting System", "Closed")

def fail_safe():
    global SYSTEMCONFIG
    """
    Cuts all 3 way solenoids
    waits for reset time
    Cuts all 2 way solenoids

    3 way solenoids default to a "closed valve state" during NC
    2 way solenodis default kill pneumatic power to 3 ways locking the system
    """
    
    way3 = [str(i) for i in range(5,11,1)]
    for key in SYSTEMCONFIG.keys():
        for s in way3:
            if s in key:
                GPIO.output(SYSTEMCONFIG[key]["GPIO"], GPIO.HIGH)
                event("Killed 3 Way", s, "FAIL SAFE", "FAIL SAFE KILLED")
    sleep(0.5)
    way2 = ["1", "2", "3", "4", "5"]
    for key in SYSTEMCONFIG.keys():
        for s in way2:
            if s in key:
                GPIO.output(SYSTEMCONFIG[key]["GPIO"], GPIO.HIGH)
                event("Killed 2 Way", s, "FAIL SAFE", "FAIL SAFE KILLED")
    
def ignition():
    """
    INGITION SEQUENCE
    """
    global SYSTEMCONFIG
    logger = logging.getLogger("IGNITION SEQUENCE")
    for i in range(10):
        sleep(1)
        logger.info(f"Lighting in {i}")
   

    # ignition gpio code
    GPIO.output(SYSTEMCONFIG["Igniter"]["GPIO"], GPIO.HIGH)
    sleep(0.85)
    
    GPIO.output(SYSTEMCONFIG["Solenoid9"]["GPIO"], GPIO.LOW)
    event("Released", 9, "Ignition", "Open")
    GPIO.output(SYSTEMCONFIG["Solenoid10"]["GPIO"], GPIO.LOW)
    event("Released", 10, "Ignition", "OPEN")
    logger.info("Ignition")





"""
Parameters to determine how to turn error values into time on/off for venting valves of propellant tanks
TODO:
Needs calibration and expeirmental testing for pressurization
or Simulink simulation
"""
global LOXVENTPARAM
global RP1VENTPARAM
global RP1VENTVALUES
global LOXVENTVALUES
RP1VENTVALUES = (0, 0)
LOXVENTVALUES = (0, 0)

RP1TIME = lambda x: RP1VENTVALUES[0]*x + RP1VENTVALUES[1]
LOXTIME = lambda x: LOXVENTVALUES[0]*x + LOXVENTVALUES[1]

LOXVENTPARAM = {
    "error_to_time_func":LOXTIME,
    "open_func":LOXVentOn(),
    "close_func":LOXVentOff()
}
RP1VENTPARAM = {
    "error_to_time_func":RP1TIME,
    "open_func":RP1VentOn(),
    "close_func":RP1VentOff()
}

class TestBed:

    def __init__(self):
        global LOGFILE
        self.NETWORKSERVER = NetworkServer()
        self.LoadCellDataRecorder = DataRecorder(LoadCellDataRecorderKeys, "LoadCellVoltageData", network=self.NETWORKSERVER)
        self.LOGGER = logging.getLogger("TESTBED")
        self.Phypervisor = PressureHyperVisor(700, 700)
        init_gpio()
        self.LOGTAIL = sh.tail("-f", LOGFILE, _iter_noblock=True)
        self.report()
        
    def report(self):
        #non blocking logging file reporter
        try:
            while True:
                self.NETWORKSERVER.send({"LOG": self.LOGTAIL.next(), "Pressure": self.Phypervisor.report()})
        except BaseException as e:
            return
    
    async def system_handler(self):
        while 1:
            recv = self.NETWORKSERVER.recv()
            if recv != None:
                try:
                    if recv["cmd"].upper() == "IGNITION":
                        ignition()
                    if recv["cmd"].upper() == "FAILSAFE":
                        fail_safe()
                    if recv["cmd"].upper() == "VENTLOX_ON":
                        LOXVentOn()
                    if recv["cmd"].upper() == "VENTRP1_ON":
                        RP1VentOn()
                    if recv["cmd"].upper() == "VENTLOX_OFF":
                        LOXVentOff()
                    if recv["cmd"].upper() == "VENTRP1_OFF":
                        RP1VentOff()
                    if recv["cmd"].upper() == "PRESS":
                        press_tanks()
                    if recv["cmd"].upper() == "DEPRESS":
                        depress_tanks()
                    if recv["cmd"].upper() == "RESET":
                        reset_gpio()
                        init_gpio()
                    if recv["cmd"].upper() == "STATUS":
                        self.NETWORKSERVER.send({"status": SYSTEMCONFIG})
                except BaseException as e:
                    pass
            self.report()
            await asyncio.sleep(0.5)

    def run(self):
        l = asyncio.get_event_loop()
        l.run_until_complete(asyncio.gather(*[
            ws.serve(self.NETWORKSERVER.serverhandler, "::", 4444),
            LoadCellManager(self.LoadCellDataRecorder.logger_func),
            self.system_handler(),
            self.Phypervisor.PressureHandler()
        ]))
        l.run_forever()

if __name__ == "__main__":
    controller = TestBed()
    controller.run()



    

