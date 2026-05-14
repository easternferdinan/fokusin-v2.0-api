import enum

class TaskCategory(str, enum.Enum):
    STUDY = 'study'
    PROJECT = 'project'
    ASSIGNMENT = 'assignment'

class TaskPriority(str, enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'