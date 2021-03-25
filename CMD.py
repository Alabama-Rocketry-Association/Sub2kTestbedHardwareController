from enum import Enum

class CMD(Enum):
    """
    List of Commands for the Hardware Controller
    """
    Dump = "DUMP"
    Begin = "BEGIN"
    Vent = "VENT"
    Shutdown = "SHUTDOWN"
    Kill = "KILL"



