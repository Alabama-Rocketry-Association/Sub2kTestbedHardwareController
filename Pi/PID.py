import numpy as np

class PID:

    def __init__(self,sp:float,gains:list, ts:float, windup_handler):
        """

        PID Pressure Tank Controller

        gains:
        [0] -> proportional
        [1] -> integral
        [2] -> derivative


        windup_handler -> manages error (for tanks we want greater than 0 error)
        """
        self.kp = gains[0]
        self.ki = gains[1]
        self.kd = gains[2]
        self.error = 0
        self.errI = 0
        self.sp = sp
        self.ts = ts
        self.windup_handler = windup_handler
    
    def update(self, nstate):
        #updating functions
        err = self.sp - nstate
        Perr = self.kp * err
        self.errI += self.ts*err
        Derr = (err - self.error)/self.ts
        self.error = Perr + self.errI + Derr
        return self.windup_handler(self.error)

    def __call__(self,x):
        return self.update(x)

