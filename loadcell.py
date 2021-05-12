from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.Manager import *
import asyncio
import pandas as pd
import datetime
from net import NetworkServer
import time

dtime = lambda : datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
ts = lambda :  datetime.datetime.now().timestamp()

class DataRecorder:

    def __init__(self, name:str, network: NetworkServer,keys = ["time", "voltage"]):
        self.network = network
        self.dataframe = pd.DataFrame(columns = keys)
        self.keys = keys
        self.cursor = 0
        self.dfile = f"{name}-{dtime()}-datalog.data"
        self.dataframe.to_csv(self.dfile, header=True)

    def logger_func(self, data: dict):
        assert data.keys() == self.keys
        packet = {
            "LoadCellData": data
        }
        self.network.send(packet)
        self.dataframe = dataframe.append(data, ignore_index=True)
        self.dataframe.iloc[self.cursor].to_csv(self.dfile, mode="a", header=False)
        self.cursor = len(self.dataframe.index)


LoadCellDataRecorderKeys = ["timestamp","voltage"]

async def LoadCellManager(logger_func, **kwargs):
    """
        Generic Function for DataRecorderClass Format
    """
    #voltage_func = lambda V: kwargs["m"]*V + kwargs["b"]
    manager = Manager()
    def onVoltage(self, vr):
        data = {
                "timestamp":ts(),
                "voltage": vr
                }
        logger_func(data)
    volr = VoltageRatioInput()
    volr.setOnVoltageRatioChangeHandler(onVoltage)
    volr.openWaitForAttachment(5000)
    while 1:
        pass

async def LoadCellManagerTest(logger_func, **kwargs):
    """
        First Prototype Function
    """
    voltage_func = lambda V: kwargs["m"]*V + kwargs["b"]
    manager = Manager()
    def onVoltage(self, vr):
        logger_func(voltage_func, vr)
    volr = VoltageRatioInput()
    volr.setOnVoltageRatioChangeHandler(onVoltage)
    volr.openWaitForAttachment(5000)
    while 1:
        pass

if __name__ == "__main__":
    logger_func = lambda v_func, vr: print(f"\rVoltage {vr} Volts Load: {v_func(vr)}")
    asyncio.get_event_loop()\
        .run_until_complete(
            asyncio.gather(LoadCellManagerTest(logger_func=logger_func, m = 230/(-0.0002 - 2.3E-5), b=-24.4))
        )\
            .run_forever()

        

            
