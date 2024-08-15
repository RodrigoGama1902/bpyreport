from dataclasses import dataclass
from enum import Enum
from typing import Any

import blf
import bpy
import gpu
from bpy.types import Context
from gpu_extras.batch import batch_for_shader

from .config import (
    BasicConfig,
    NotificationColorConfig,
    NotificationConfig,
    NotificationDrawConfig,
)

# -------------------------------------------------
# Notification System
# -------------------------------------------------


@dataclass
class SceneNotificationData:
    """Dataclass to store the notification data"""

    handler: Any | None
    notifications: list["NotificationInfo"]
    fix_messages: dict[int, "NotificationInfo"]


# Global variable responsible for storing the notification data
notification_data = SceneNotificationData(
    handler=None,
    notifications=[],
    fix_messages={},
)

# Global variable responsible for storing the notification configuration
notification_config = NotificationConfig()


class DrawHelper:
    """Helper class to redraw the viewport"""

    @staticmethod
    def redraw():
        """Redraw the viewport"""

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


class NotificationType(Enum):
    """Enum for the notification type"""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"


class NotificationInfo:
    """Class to store the notification data"""

    def __init__(
        self,
        raw_text: str,
        notification_type: NotificationType,
        module_name: str = "",
        text_size: int = 40,
    ):

        self.raw_text = raw_text
        self.type = notification_type
        self.module_name = module_name
        self.text_size = text_size

    def get_text(self):
        """Return the final text to be displayed"""

        final_text = self.raw_text

        if notification_config.basic.show_notification_type:
            if self.type == NotificationType.INFO:
                final_text = "INFO: " + self.raw_text
            if self.type == NotificationType.WARNING:
                final_text = "WARNING: " + self.raw_text
            if self.type == NotificationType.ERROR:
                final_text = "ERROR: " + self.raw_text
            if self.type == NotificationType.RUNTIME_ERROR:
                final_text = "<RUNTIME ERROR>: " + self.raw_text

        if self.module_name and notification_config.basic.use_module_name:
            final_text = f"({self.module_name}) " + final_text

        return final_text

    def get_color(self):
        """Return the color of the notification"""

        if self.type == NotificationType.INFO:
            return notification_config.color.info
        if self.type == NotificationType.WARNING:
            return notification_config.color.warning
        if self.type == NotificationType.ERROR:
            return notification_config.color.error
        if self.type == NotificationType.RUNTIME_ERROR:
            return notification_config.color.runtime_error

        return notification_config.color.info


class NotificationDraw:
    """Generates a notification with fix width and dynamic height"""

    def __init__(
        self,
        box_width: float,
        color: tuple[float, float, float, float],
        text: str,
        text_size: float,
        y_location: int,
        start_x: float,
    ):

        self.dpi = bpy.context.preferences.system.dpi

        self.box_width = box_width
        self.y_location = y_location
        self.start_x = start_x

        self.font_id = 0
        self.color = color
        self.text = text
        self.text_size = text_size

        self.box_height_px = self.generate_notification_text_paramenters()

    def generate_notification_text_paramenters(self) -> int:
        """Generate the notification text parameters, and return the corret height box value"""

        blf.enable(self.font_id, blf.WORD_WRAP)  # type: ignore
        blf.enable(self.font_id, blf.SHADOW)  # type: ignore

        max_text_width = int(self.box_width - (self.dpi * 0.3))

        blf.word_wrap(self.font_id, max_text_width)
        blf.size(self.font_id, self.text_size)

        text_real_height = blf.dimensions(self.font_id, self.text)[1]
        text_one_line_height = blf.dimensions(self.font_id, "(")[1]

        box_height_px = text_real_height + (self.dpi * 0.2)

        self.text_y_location = (
            self.y_location + (box_height_px / 2) - (text_real_height / 2)
        )

        if (
            text_real_height > text_one_line_height * 1.5
        ):  # If the text is more than 1.5 lines, it needs to be moved up
            self.text_y_location += text_real_height - text_one_line_height

        return box_height_px

    def draw_notification_box(self) -> int:
        """Draw a single notification box and return the value of the next y location"""

        vertices = (
            (self.start_x, self.y_location),
            (self.start_x, self.y_location + self.box_height_px),
            (self.box_width, self.y_location + self.box_height_px),
            (self.box_width, self.y_location),
        )

        indices = ((0, 1, 2), (2, 3, 0))

        gpu.state.blend_set("ALPHA")

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        batch = batch_for_shader(
            shader, "TRIS", {"pos": vertices}, indices=indices
        )

        gpu.state.blend_set("ALPHA")

        shader.bind()
        shader.uniform_float("color", self.color)

        batch.draw(shader)

        gpu.state.blend_set("NONE")

        return self.box_height_px + notification_config.draw.spacing

    def draw_notification_text(self):
        """Draw the notification text"""

        blf.position(self.font_id, self.start_x + 20, self.text_y_location, 0)
        blf.color(self.font_id, 1.0, 1.0, 1.0, 1.0)
        blf.shadow(self.font_id, 5, 0.0, 0.0, 0.0, 1)
        blf.shadow_offset(self.font_id, 1, -1)

        blf.draw(self.font_id, self.text)

        blf.disable(self.font_id, blf.WORD_WRAP)  # type: ignore
        blf.disable(self.font_id, blf.SHADOW)  # type: ignore


def _draw_all_notifications(self: Any, context: Context):
    """Draws all current notifications on the viewports"""

    y_current_location = notification_config.draw.first_y_location
    start_x = bpy.context.area.width * notification_config.draw.start_x
    notification_width = (
        bpy.context.area.width * notification_config.draw.end_x
    )

    for notification in notification_data.notifications:

        notification_draw = NotificationDraw(
            box_width=notification_width,
            color=notification.get_color(),
            text=notification.get_text(),
            text_size=notification.text_size,
            y_location=y_current_location,
            start_x=start_x,
        )

        y_current_location += notification_draw.draw_notification_box()
        notification_draw.draw_notification_text()

    for fix_notification in notification_data.fix_messages.values():

        fix_message_draw = NotificationDraw(
            box_width=notification_width,
            color=fix_notification.get_color(),
            text=fix_notification.get_text(),
            text_size=fix_notification.text_size,
            y_location=y_current_location,
            start_x=start_x,
        )

        y_current_location += fix_message_draw.draw_notification_box()
        fix_message_draw.draw_notification_text()


def _timer_remove_text():
    """Remove the first notification from the list"""

    notification_data.notifications = notification_data.notifications[1:]
    DrawHelper.redraw()


def _create_drawn_handler():

    handler = notification_data.handler

    if not handler:
        notification_data.handler = bpy.types.SpaceView3D.draw_handler_add(
            _draw_all_notifications, (None, None), "WINDOW", "POST_PIXEL"
        )


def update_fix_message(
    new_text: str | None = None,
    new_type: NotificationType | None = None,
    index: int = 0,
):
    """Update a fix message from the list"""

    if len(notification_data.fix_messages) <= index:
        raise IndexError("Better Report Message: The index is out of range")

    current_text = notification_data.fix_messages[index].raw_text
    current_type = notification_data.fix_messages[index].type

    print("New text", current_text)
    print("New Type", current_type)

    if new_text:
        current_text = new_text
    if new_type:
        current_type = new_type

    _create_drawn_handler()

    notification = NotificationInfo(
        current_text,
        current_type,
        module_name=notification_config.basic.module_name,
        text_size=notification_config.draw.text_size,
    )
    notification_data.fix_messages[index] = notification

    DrawHelper.redraw()


def remove_fix_message(index: int = 0):
    """Remove a fix message from the list"""

    _create_drawn_handler()

    if index in notification_data.fix_messages:
        del notification_data.fix_messages[index]
        DrawHelper.redraw()


def clear_fix_messages():
    """Clear all fix messages from the list"""

    _create_drawn_handler()

    notification_data.fix_messages = {}
    DrawHelper.redraw()


def unregister_messages():
    """Unregister the draw handler and clear the notifications"""

    handler = notification_data.handler

    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")
        notification_data.handler = None
        notification_data.notifications = []
        notification_data.fix_messages = {}
        DrawHelper.redraw()


def message(
    text: str,
    notification_type: NotificationType = NotificationType.INFO,
    remove_in_time: int = 5,
    print_console: bool = True,
    fix_message_index: int = 0,
):
    """Add a message notification to the list

    Args:
        text (str): The text of the notification
        notification_type (NotificationType, optional): The type of the notification. Defaults to NotificationType.INFO.
        remove_in_time (int, optional): The time in seconds that the notification will be removed. If 0, the message will be a fix message. Defaults to 5.
        print_console (bool, optional): If the message will be printed on the console. Defaults to True.
        fix_message_index (int, optional): The index of the fix message. Defaults to 0. Used only if remove_in_time is 0.
    """

    _create_drawn_handler()

    notification = NotificationInfo(
        text,
        notification_type,
        module_name=notification_config.basic.module_name,
        text_size=notification_config.draw.text_size,
    )

    if remove_in_time <= 0:  # FIX MESSAGE
        notification_data.fix_messages[fix_message_index] = notification
        DrawHelper.redraw()
        return

    notification_data.notifications.append(notification)
    print(notification_config.basic.module_name)

    bpy.app.timers.register(
        _timer_remove_text, first_interval=remove_in_time, persistent=True
    )
    DrawHelper.redraw()

    if print_console:
        print(text)


def info(
    text: str,
    remove_in_time: int = 5,
    print_console: bool = True,
    fix_message_index: int = 0,
):
    """Info wrapper for the message function

    Args:
        text (str): The text of the notification
        remove_in_time (int, optional): The time in seconds that the notification will be removed. Defaults to 5.
        print_console (bool, optional): If the message will be printed on the console. Defaults to True.
        fix_message_index (int, optional): The index of the fix message. Defaults to 0. Used only if remove_in_time is 0.
    """

    message(
        text=text,
        notification_type=NotificationType.INFO,
        remove_in_time=remove_in_time,
        print_console=print_console,
        fix_message_index=fix_message_index,
    )


def warning(
    text: str,
    remove_in_time: int = 5,
    print_console: bool = True,
    fix_message_index: int = 0,
):
    """Warning wrapper for the message function

    Args:
        text (str): The text of the notification
        remove_in_time (int, optional): The time in seconds that the notification will be removed. Defaults to 5.
        print_console (bool, optional): If the message will be printed on the console. Defaults to True.
        fix_message_index (int, optional): The index of the fix message. Defaults to 0. Used only if remove_in_time is 0.
    """

    message(
        text=text,
        notification_type=NotificationType.WARNING,
        remove_in_time=remove_in_time,
        print_console=print_console,
        fix_message_index=fix_message_index,
    )


def error(
    text: str,
    remove_in_time: int = 5,
    print_console: bool = True,
    fix_message_index: int = 0,
):
    """Error wrapper for the message function

    Args:
        text (str): The text of the notification
        remove_in_time (int, optional): The time in seconds that the notification will be removed. Defaults to 5.
        print_console (bool, optional): If the message will be printed on the console. Defaults to True.
        fix_message_index (int, optional): The index of the fix message. Defaults to 0. Used only if remove_in_time is 0.
    """

    message(
        text=text,
        notification_type=NotificationType.ERROR,
        remove_in_time=remove_in_time,
        print_console=print_console,
        fix_message_index=fix_message_index,
    )


def runtime_error(
    text: str,
    remove_in_time: int = 5,
    print_console: bool = True,
    fix_message_index: int = 0,
):
    """Runtime Error wrapper for the message function

    Args:
        text (str): The text of the notification
        remove_in_time (int, optional): The time in seconds that the notification will be removed. Defaults to 5.
        print_console (bool, optional): If the message will be printed on the console. Defaults to True.
        fix_message_index (int, optional): The index of the fix message. Defaults to 0. Used only if remove_in_time is 0.
    """

    message(
        text=text,
        notification_type=NotificationType.RUNTIME_ERROR,
        remove_in_time=remove_in_time,
        print_console=print_console,
        fix_message_index=fix_message_index,
    )


def set_notification_config(
    basic: BasicConfig | None = None,
    draw: NotificationDrawConfig | None = None,
    color: NotificationColorConfig | None = None,
) -> None:
    """Update the notification configuration"""

    notification_config.basic = basic or notification_config.basic
    notification_config.draw = draw or notification_config.draw
    notification_config.color = color or notification_config.color
