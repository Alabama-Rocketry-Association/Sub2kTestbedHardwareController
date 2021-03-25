from gpiohandler import GPIOHandler
from util import LOGGER
from Rpi.GPIO import GPIO

class GPIOHypervisor(GPIOHandler):

    """
    All operation specific I/O will
    be managed by this class
    """

    def __init__(self, ):
        LOGGER.debug(f"{self}")
        super(GPIOHypervisor, self).__init__()
        self.cmd = Stack(maxsize=4)
        self.logger = logging.getLogger("GPIO Hypervisor")

    def put(self, cmd: CMD):
        self.cmd.put_nowait()

    def get_new_cmd(self):
        return self.cmd.get_nowait()

    def execute(self, cmd:CMD):
        newStates = cmd.get_new_states()
        pins = cmd.get_pins()
        GPIO.output(pins, list([GPIO.LOW if i == 0 else GPIO.HIGH for i in newStates]))
        for pin_states in self.states:
            for idx, pin in enumerate(pins):
                if pin_states == str(pin):
                    self.states[pin_states] = newStates[idx]

    def update_states(self, pin, output):
        self.states[str(pin)] = output

    async def handler(self):

        #in last revision these GPIOVALVES were a global bariable, make adjustment
        while 1:
            if not self.cmd.empty():
                cmd = self.get_new_cmd()
                if str(cmd) == "ENGINESTART":
                    GPIO.output(GPIOVALVES["lox_dump"]["pin"], GPIO.LOW)
                    self.update_states(GPIOVALVES["lox_dump"]["pin"], 0)
                    self.logger.info("DUMPING LOX")
                    sleep(GPIOVALVES["engine_start_delay"]["time_ms"])
                    GPIO.output(GPIOVALVES["kerosene_dump"]["pin"], GPIO.LOW)
                    self.update_states(GPIOVALVES["kerosene_dump"]["pin"], 0)
                    self.logger.info("DUMPING KEROSENE")
                    GPIO.output(GPIOVALVES["igniter"]["pin"], GPIO.HIGH)
                elif str(cmd) == "ENGINESTOP":
                    GPIO.output(GPIOVALVES["lox_dump"]["pin"], GPIO.HIGH)
                    self.update_states(GPIOVALVES["lox_dump"]["pin"], 1)
                    self.logger.info("STOPPING LOX")
                    GPIO.output(GPIOVALVES["kerosene_dump"]["pin"], GPIO.HIGH)
                    self.update_states(GPIOVALVES["kerosene_dump"]["pin"], 1)
                    self.logger.info("STOPPING KEROSENE")
                else:
                    #general non-mission critical gpio commands
                    self.execute(cmd)
            else:
                await asyncio.sleep(0.1)

    def report(self):
        return self.states