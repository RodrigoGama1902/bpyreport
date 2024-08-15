from dataclasses import dataclass, field

# -------------------------------------------------
# Notification Config Dataclasses
# -------------------------------------------------


@dataclass
class BasicConfig:
    """Basic configuration for the notification system"""

    module_name: str = field(default="My Module")
    use_module_name: bool = field(default=False)
    show_notification_type: bool = field(default=False)


@dataclass
class NotificationDrawConfig:
    """Draw configuration for the notification system"""

    text_size: int = field(default=40)
    width_percentage: float = field(default=1)
    spacing: int = field(default=5)
    first_y_location: int = field(default=50)
    x_start_position: float = field(default=0.8)


@dataclass
class NotificationColorConfig:
    """Color configuration for the notification system"""

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
