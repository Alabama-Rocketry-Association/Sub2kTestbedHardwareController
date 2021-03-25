from gpiohandler import GPIOHandler
import pandas as pd

class PressureMonitor(GPIOHandler):

    """
    All pressure-based I/O will solely be
    Managed by this class (venting)
    """

    class PID(object):

        """
        PID controller for venting management
        """

        def __init__(self, setvalue, k_values, ts):
            self.ts = ts #sample rate
            self.setvalue = setvalue
            self.error = 0
            self.ei = 0
            self.k = k_values
            self.ERR = lambda val: self.setvalue - val

        def _update(self, Input):
            err = self.ERR(Input)
            ep = self.k["P"] * err
            ed = self.k["D"] * (err - self.error) / self.ts
            self.ei += self.k["I"] * (self.ts * err)
            self.error = err
            return ep + ed + self.ei

        def evaluate(self, Input):
            if Input <= self.setvalue:
                self.error = 0
            return self._update(Input)

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
        self.logger = logging.getLogger("Pressure Monitor")

    async def handler(self):
        while 1:
            pass

    def backup(self):
        pass

    def report(self):
        self.backup()
        return self.data.iloc[-20:-1] #return last 20 entries
