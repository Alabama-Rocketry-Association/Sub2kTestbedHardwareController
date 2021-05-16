import asyncio

class PIDController:

    def __init__(self, sp, ks, ts, anti_windup_func = lambda x: x):
        self.windup = anti_windup_func
        self.ts = ts
        self.K = ks
        self.sp = sp
        self.ierr = 0
        self.anti_wind_wrapper = lambda func: func(self.ierr)
        self.P = lambda val: self.K[0] * (self.sp-val)
        self.I = lambda val: self.K[1] * (self.sp-val)*ts
        self.D = lambda val: self.K[2] * (self.sp-val)/ts

    def update(self, val):
        self.ierr = self.anti_wind_wrapper(self.windup)
        self.ierr += self.I(val)
        return self.P(val) + self.ierr + self.D(val)

    def __call__(self, x):
        return self.update(x)

class PressureController():

    def __init__(self, setpoint, K, ts, anti_wind = lambda x: 0 if (x < 0) else x , threshold_time = 0.5):
        self.PID = PIDController(setpoint, K, ts, anti_wind)
        self.threshold = threshold_time #protects solenoids
        self.venting_in_progress = False

    def update(self, val, kwargs):
        #spins off a new thread to run the venting process
        loop = asyncio.new_event_loop()
        self.venting_in_progress = True
        loop.run_until_complete(asyncio.gather([self.venting_function(self.PID(val), **kwargs)]))
        self.venting_in_progress = False
        loop.close()

    async def venting_function(self, err, **kwargs):
        #non blocking venting
        #redfine for default open, close and out pressure to time function
        """
            error_to_time() calculates the time the vent should be open to correct the error
            it is dependent on the valve diameter, volume, and thermodynamic qualities of the tank mixtures and compositions
            goal is to create a linear function for each tank
        """
        keys = ["open_func", "close_func", "error_to_time_func"]
        assert set(keys) == set(kwargs.keys())
        if err == 0:
            await asyncio.sleep(0.01)
            return
        venttime = kwargs["error_to_time_func"](err)
        if venttime > self.threshold and not self.venting_in_progress:
            kwargs["open_func"]()
            await asyncio.sleep(venttime)
            kwargs["close_func"]()
        await asyncio.sleep(0.01)
        return
    
    def __call__(self, x, args):
        print(args)
        return self.update(x, args)

def pressure_model(pressure):
    #error pressure to time valve open
    return 0.36*pressure

if __name__ == "__main__":
    #test script
    open_test = lambda : print("open")
    close_test = lambda: print("close")
    error_to_time = lambda p: pressure_model(p)
    controller = PressureController(700, [0.3, 0.5, 0], 0.1)
    PID = PIDController(100, [0.3,0.7,0], 0.1)
    from random import random
    from time import sleep
    a = 0
    while 1:
        a = controller(a + random(), {"open_func":open_test, "close_func":close_test, "error_to_time_func":error_to_time})
        print(a)
        sleep(0.1)