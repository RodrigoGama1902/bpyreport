import bpy  
import blf
import gpu
import bgl

from gpu_extras.batch import batch_for_shader
from enum import Enum

MODULE_NAME = "VN CORE" # Module name to be displayed in the notifications

NOTIFICATION_TEXT_SIZE = 30 # Text size in pixels
NOTIFICATION_WIDTH_PERCENTAGE = 1 # Percentage of the screen width
NOTIFICATION_SPACING = 5 # Spacing between notifications in pixels 
NOTIFICATION_FIRST_Y_LOCATION = 0 # Y location of the first notification in pixels

NOTIFICATION_X_START_POSITION = 0.5

NOTIFICATION_INFO_COLOR = (0.1, 0.1, 0.1, 0.7)
NOTIFICATION_WARNING_COLOR = (1.0, 0.5, 0.0, 0.3)
NOTIFICATION_ERROR_COLOR = (1.0, 0.0, 0.0, 0.15)
NOTIFICATION_RUNTIME_ERROR_COLOR = (1.0, 0.0, 0.0, 0.3)

notification_data = {
    "handler": None,
    "notifications": [],
}

class DrawHelper():

    @staticmethod
    def redraw():
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()   

class NotificationType(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"

class NotificationInfo():
    
    module_name = MODULE_NAME
    text_size = NOTIFICATION_TEXT_SIZE
        
    def __init__(self, 
                 raw_text : str,
                 type : NotificationType,
                 display_time : int):
        
        self.display_time = display_time
        self.raw_text = raw_text
        self.type = type
    
    def get_text(self):
        
        final_text = self.raw_text
        
        if self.type == NotificationType.INFO:
            final_text = "INFO: " + self.raw_text
        if self.type == NotificationType.WARNING:
            final_text = "WARNING: " + self.raw_text
        if self.type == NotificationType.ERROR:
            final_text = "ERROR: " + self.raw_text
        if self.type == NotificationType.RUNTIME_ERROR:
            final_text = "<RUNTIME ERROR>: " + self.raw_text
        
        if self.module_name:
            final_text = f"({self.module_name}) " + final_text
        
        return final_text
  
    def get_color(self):
        
        if self.type == NotificationType.INFO:
            return NOTIFICATION_INFO_COLOR
        if self.type == NotificationType.WARNING:
            return NOTIFICATION_WARNING_COLOR
        if self.type == NotificationType.ERROR:
            return NOTIFICATION_ERROR_COLOR 
        if self.type == NotificationType.RUNTIME_ERROR:
            return NOTIFICATION_RUNTIME_ERROR_COLOR
            
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
        
        return self.box_height_px + NOTIFICATION_SPACING

    def draw_notification_text(self):
        
        blf.position(self.font_id, self.x_start_position + 20, self.text_y_location, 0)  
        blf.color(self.font_id, 1.0, 1.0, 1.0, 1.0)
        blf.shadow(self.font_id, 5, 0.0, 0.0, 0.0, 1)
        blf.shadow_offset(self.font_id, 1, -1)
        
        blf.draw(self.font_id, self.text)
        
        blf.disable(self.font_id, blf.WORD_WRAP)
        blf.disable(self.font_id, blf.SHADOW)
    
def draw_all_notifications(self, context):
    """Draws all current notifications on the viewports"""
    
    y_current_location = NOTIFICATION_FIRST_Y_LOCATION
    x_start_position = bpy.context.area.width * NOTIFICATION_X_START_POSITION
    notification_width = bpy.context.area.width * NOTIFICATION_WIDTH_PERCENTAGE
    
    for notification in notification_data["notifications"]:
        
        notification_draw = NotificationDraw(box_width = notification_width,
                                             color = notification.get_color(), 
                                             text = notification.get_text(),
                                             text_size = notification.text_size,
                                             y_location = y_current_location,
                                             x_start_position = x_start_position)
        
        y_current_location += notification_draw.draw_notification_box()
        notification_draw.draw_notification_text()

def timer_remove_text():
    '''Remove the first notification from the list'''
    
    notification_data["notifications"] = notification_data["notifications"][1:]
    DrawHelper.redraw()

def create_drawn_handler():
    
    handler = notification_data["handler"]
    
    if not handler:
        notification_data["handler"] = bpy.types.SpaceView3D.draw_handler_add(
        draw_all_notifications, (None, None), 'WINDOW', 'POST_PIXEL')

def report_message(text : str,
                   type : NotificationType = NotificationType.INFO,
                   display_time = 5,
                   print_console = True):
    '''Add a notification to the list'''
    
    if not isinstance(text, str):
        raise TypeError("Better Report Message: The text must be a string")
    
    create_drawn_handler()
    
    notification = NotificationInfo(text, type, display_time)
    notification_data["notifications"].append(notification)
    
    bpy.app.timers.register(timer_remove_text, first_interval= notification.display_time, persistent=True)
    DrawHelper.redraw()
    
    if print_console:
        print(text)
       
    



