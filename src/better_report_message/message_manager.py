import bpy
import bpy  
import blf
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

from enum import Enum
from pathlib import Path

from .settings import Settings

SETTINGS = Settings(Path(__file__).parent / "settings.json") # Customizable settings path

class DrawHelper():
    '''Helper class to redraw the viewport'''

    @staticmethod
    def redraw():
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()   

class NotificationType(Enum):
    '''Enum for the notification type'''

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"

class NotificationInfo():
    
    module_name =  SETTINGS.basic("module_name")
    text_size = SETTINGS.notification_draw("notification_text_size")
        
    def __init__(self, 
                 raw_text : str,
                 type : NotificationType,
                 ):
        
        self.raw_text = raw_text
        self.type = type
    
    def get_text(self):
        
        final_text = self.raw_text

        if SETTINGS.basic("show_notification_type"):
            if self.type == NotificationType.INFO:
                final_text = "INFO: " + self.raw_text
            if self.type == NotificationType.WARNING:
                final_text = "WARNING: " + self.raw_text
            if self.type == NotificationType.ERROR:
                final_text = "ERROR: " + self.raw_text
            if self.type == NotificationType.RUNTIME_ERROR:
                final_text = "<RUNTIME ERROR>: " + self.raw_text
        
        if self.module_name and SETTINGS.basic("use_module_name"):
            final_text = f"({self.module_name}) " + final_text
        
        return final_text
  
    def get_color(self):
        
        if self.type == NotificationType.INFO:
            return SETTINGS.colors("notification_info_color")
        if self.type == NotificationType.WARNING:
            return SETTINGS.colors("notification_warning_color")
        if self.type == NotificationType.ERROR:
            return SETTINGS.colors("notification_error_color")
        if self.type == NotificationType.RUNTIME_ERROR:
            return SETTINGS.colors("notification_runtime_error_color")
            
class NotificationDraw():
    '''Generates a notification with fix width and dynamic height'''
    
    def __init__(self, box_width , color, text, text_size, y_location, x_start_position):
        
        self.dpi = bpy.context.preferences.system.dpi
        
        self.box_width = box_width
        self.y_location = y_location
        self.x_start_position = x_start_position
        
        self.font_id = 0 
        self.color = color
        self.text = text
        self.text_size = text_size
        
        self.box_height_px = self.generate_notification_text_paramenters()
    
    def generate_notification_text_paramenters(self) -> int:
        '''Generate the notification text parameters, and return the corret height box value'''
        
        blf.enable(self.font_id, blf.WORD_WRAP)
        blf.enable(self.font_id, blf.SHADOW)
        
        max_text_width = int(self.box_width - (self.dpi * 0.3))
        
        blf.word_wrap(self.font_id, max_text_width)
        blf.size(self.font_id, self.text_size, 40) 
                   
        text_real_height = blf.dimensions(self.font_id, self.text)[1]
        text_one_line_height = blf.dimensions(self.font_id, "(")[1]
        
        box_height_px = text_real_height + (self.dpi * 0.2) 
        
        self.text_y_location = self.y_location + (box_height_px / 2) - (text_real_height / 2)
        
        if (text_real_height > text_one_line_height * 1.5): # If the text is more than 1.5 lines, it needs to be moved up  
            self.text_y_location += text_real_height - text_one_line_height
                
        return box_height_px
  
    def draw_notification_box(self) -> int:
        """Draw a single notification box and return the value of the next y location"""

        vertices = (
            (self.x_start_position, self.y_location),
            (self.x_start_position, self.y_location + self.box_height_px),
            (self.box_width, self.y_location + self.box_height_px),
            (self.box_width, self.y_location),
        )
        
        indices = ((0, 1, 2), (2, 3, 0))
        
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(1)
        
        shader.bind()
        shader.uniform_float("color", self.color)
        
        batch.draw(shader)
        
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_LINE_SMOOTH)
        
        return self.box_height_px + SETTINGS.notification_draw("notification_spacing")

    def draw_notification_text(self):
        
        blf.position(self.font_id, self.x_start_position + 20, self.text_y_location, 0)  
        blf.color(self.font_id, 1.0, 1.0, 1.0, 1.0)
        blf.shadow(self.font_id, 5, 0.0, 0.0, 0.0, 1)
        blf.shadow_offset(self.font_id, 1, -1)
        
        blf.draw(self.font_id, self.text)
        
        blf.disable(self.font_id, blf.WORD_WRAP)
        blf.disable(self.font_id, blf.SHADOW)


notification_data = {
    "handler": None,
    "notifications": [],
    "fix_messages": {},
}


def _draw_all_notifications(self, context):
    """Draws all current notifications on the viewports"""
    
    y_current_location = SETTINGS.notification_draw("notification_first_y_location")
    x_start_position = bpy.context.area.width * SETTINGS.notification_draw("notification_x_start_position")
    notification_width = bpy.context.area.width * SETTINGS.notification_draw("notification_width_percentage")
    
    for notification in notification_data["notifications"]:
        
        notification_draw = NotificationDraw(box_width = notification_width,
                                             color = notification.get_color(), 
                                             text = notification.get_text(),
                                             text_size = notification.text_size,
                                             y_location = y_current_location,
                                             x_start_position = x_start_position)
        
        y_current_location += notification_draw.draw_notification_box()
        notification_draw.draw_notification_text()

    for fix_message in notification_data["fix_messages"].values():
        
        fix_message_draw = NotificationDraw(box_width = notification_width,
                                             color = fix_message.get_color(), 
                                             text = fix_message.get_text(),
                                             text_size = fix_message.text_size,
                                             y_location = y_current_location,
                                             x_start_position = x_start_position)
        
        y_current_location += fix_message_draw.draw_notification_box()
        fix_message_draw.draw_notification_text()


def _timer_remove_text():
    '''Remove the first notification from the list'''
    
    notification_data["notifications"] = notification_data["notifications"][1:]
    DrawHelper.redraw()


def _create_drawn_handler():
    
    handler = notification_data["handler"]
    
    if not handler:
        notification_data["handler"] = bpy.types.SpaceView3D.draw_handler_add(
        _draw_all_notifications, (None, None), 'WINDOW', 'POST_PIXEL')


def fix_message(text : str, type : NotificationType = NotificationType.INFO, index = 0):
    
    if not isinstance(text, str):
        raise TypeError("Better Report Message: The text must be a string")
    
    _create_drawn_handler()
    
    notification = NotificationInfo(text, type)
    notification_data["fix_messages"][index] = notification
    
    DrawHelper.redraw()

def update_fix_message(text : str = "", type : NotificationType = NotificationType.INFO, index = 0):

    new_message = ""
    new_type = NotificationType.INFO

    if not text:
        new_message = notification_data["fix_messages"][index].raw_text
    if not type:
        new_type = notification_data["fix_messages"][index].type

    _create_drawn_handler()

    notification = NotificationInfo(new_message, new_type)
    notification_data["fix_messages"][index] = notification

    DrawHelper.redraw()

def remove_fix_message(index = 0):

    _create_drawn_handler()
        
    if index in notification_data["fix_messages"]:
        del notification_data["fix_messages"][index]
        DrawHelper.redraw()


def clear_fix_messages():

    _create_drawn_handler()
        
    notification_data["fix_messages"] = {}
    DrawHelper.redraw()


def unregister_messages():

    handler = notification_data["handler"]
    
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        notification_data["handler"] = None
        notification_data["notifications"] = []
        notification_data["fix_messages"] = {}
        DrawHelper.redraw()


def message(text : str,
                   type : NotificationType = NotificationType.INFO,
                   display_time = 5,
                   print_console = True
                   ):
    '''Add a notification to the list'''
    
    if not isinstance(text, str):
        raise TypeError("Better Report Message: The text must be a string")
    
    _create_drawn_handler()
    
    notification = NotificationInfo(text, type)
    notification_data["notifications"].append(notification)
    
    bpy.app.timers.register(_timer_remove_text, first_interval= display_time, persistent=True)
    DrawHelper.redraw()
    
    if print_console:
        print(text)