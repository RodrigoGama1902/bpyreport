from enum import Enum

class NotificationType(Enum):
    '''Enum for the notification type'''

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"