from gpiohandler import GPIOHandler
import pandas as pd
from util import importGPIO, LOGGER

importGPIO()

class PressureMonitor(GPIOHandler):

    """
    All pressure-based I/O will solely be
    Managed by this class (venting)
    """

            

    data = pd.DataFrame(["time", "pressure_lox", "pressure_kerosene"])

    def vent(self, valve, time_ms:float):
        GPIO.output(valve, GPIO.LOW)
        super().states[f"pin{valve}"] = 0
        self.logger.info(f"VENTING {valve}, time:{time_ms}ms")
        sleep(time_ms/1000)
        GPIO.output(valve, GPIO.HIGH)
        self.logger.info(f"FINISHED VENTING {valve}")
        super().states[f"pin{valve}"] = 1

    def __init__(self, GPIOPRESSURE):
        super(PressureMonitor, self).__init__()
        self.KerosenePID = self.PID(
            setvalue=GPIOPRESSURE["Kerosene"]["Threshold"],
            ts=GPIOPRESSURE["sampling"]["ts"]
        )
        self.RP1PID = self.PID(
            setvalue=GPIOPRESSURE["RP1"]["Threshold"],
            ts=GPIOPRESSURE["sampling"]["ts"]
        )
        self.logger = LOGGER

    async def handler(self):
        #implement control scheme
        while 1:
            pass

    def backup(self):
        pass

    def report(self):
        self.backup()
        return self.data.iloc[-20:-1] #return last 20 entries
