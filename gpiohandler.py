from abc import ABC, abstractclassmethod

class GPIOHandler(ABC):
    states = {}
    LOX_Vent = False
    KEROSENE_Vent = False

    def __init__(self):
        pass

    @abstractclassmethod
    async def handler(self):
        while 1:
            pass