
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
        self.error = ep + ed + self.ei
        return self.error

    def evaluate(self, Input):
        if Input <= self.setvalue:
            self.error = 0
            return self._update(Input)
