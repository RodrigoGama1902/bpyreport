from dataclasses import dataclass, field

# -------------------------------------------------
# Notification Config Dataclasses
# -------------------------------------------------


@dataclass
class BasicConfig:
    """Basic configuration for the notification system

    Attributes:
        module_name (str): The name of the module
        use_module_name (bool): Show the module name in the notification text
        show_notification_type (bool): Show the notification type in the notification text
    """

    module_name: str = field(default="My Module")
    use_module_name: bool = field(default=False)
    show_notification_type: bool = field(default=False)


@dataclass
class NotificationDrawConfig:
    """Draw configuration for the notification system

    Attributes:
        text_size (int): The size of the text
        start_x (float): The X start position factor in relation
            to the current area width. Must be between 0 and 1
        end_x (float): The X end position factor in relation
            to the current area width. Must be between 0 and 1
        spacing (int): The vertical spacing between each notification
        first_y_location (int): The Y location of the first notification
    """

    text_size: int = field(default=40)

    start_x: float = field(default=0.8)
    end_x: float = field(default=1)

    spacing: int = field(default=5)
    first_y_location: int = field(default=50)


@dataclass
class NotificationColorConfig:
    """Color configuration for the notification system

    Attributes:
        info (tuple[float, float, float, float]): RGBA color for info notifications
        warning (tuple[float, float, float, float]): RGBA color for warning notifications
        error (tuple[float, float, float, float]): RGBA color for error notifications
        runtime_error (tuple[float, float, float, float]): RGBA color for runtime error
    """

    info: tuple[float, float, float, float] = field(
        default=(0.1, 0.1, 0.1, 0.7)
    )
    warning: tuple[float, float, float, float] = field(
        default=(1.0, 0.5, 0.0, 0.3)
    )
    error: tuple[float, float, float, float] = field(
        default=(1.0, 0.0, 0.0, 0.15)
    )
    runtime_error: tuple[float, float, float, float] = field(
        default=(1.0, 0.0, 0.0, 0.3)
    )


class NotificationConfig:
    """Notification configuration for the notification system"""

    basic: BasicConfig
    draw: NotificationDrawConfig
    color: NotificationColorConfig

    def __init__(self):
        self.basic = BasicConfig()
        self.draw = NotificationDrawConfig()
        self.color = NotificationColorConfig()
