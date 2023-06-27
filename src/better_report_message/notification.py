import json

from enum import Enum
from pathlib import Path

import bpy  
import blf
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

class Settings:
    '''Load the settings from the json file'''

    def __init__(self, json_path):
        self.json_path = json_path
        self.data = json.load(open(json_path, "r"))

    def basic(self, key):
        return self.data["basic"][key]
    
    def notification_draw(self, key):
        return self.data["notification_draw"][key]
    
    def colors(self, key):
        return self.data["colors"][key]

SETTINGS = Settings(Path(__file__).parent / "settings.json")

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



       
    



