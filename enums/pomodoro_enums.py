import enum

class PomodoroStatus(str, enum.Enum):
    ACTIVE = "active"
    REST = "rest"
    PAUSED = "paused"
    STOPPED = "stopped"