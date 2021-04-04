from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.Manager import *
import asyncio


async def LoadCellManager(logger_func, **kwargs):
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
            asyncio.gather(LoadCellManager(logger_func=logger_func, m = 230/(-0.0002 - 2.3E-5), b=-24.4))
        )\
            .run_forever()

        

            
