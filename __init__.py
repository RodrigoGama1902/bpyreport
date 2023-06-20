import bpy

__all__ = [
    "NotificationType",
    "report_message",
    "add_fix_message",
    "unregister_drawn_handler",
    ]

from .draw import (
    NotificationType,
    report_message,
    add_fix_message,
    unregister_drawn_handler,
    )

# ------------------------------------------------------------------------
#   One-file add-on to test the Better Report Message API
# ------------------------------------------------------------------------

bl_info = {
    "name": "Better Report Message",
    "author": "Rodrigo Gama",
    "version": (0, 0, 1),
    "blender": (3, 5, 0),
    "category": "3D View",
}

class BRM_Properties(bpy.types.PropertyGroup):
    message_type: bpy.props.EnumProperty(
        name="Message Type",
        description="Choose a message type",
        items=(
            ('INFO', "INFO", ""),
            ('WARNING', "WARNING", ""),
            ('ERROR', "ERROR", ""),
            ('RUNTIME_ERROR', "RUNTIME_ERROR", ""),
        )
    )

    message_text : bpy.props.StringProperty(default = "This is a test message", name = "Message Text")

class BRM_PT_BetterReportMessageTests(bpy.types.Panel):
    bl_label = "Better Report Message Tests"
    bl_idname = "BRM_PT_BetterReportMessageTests"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Add-on'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.prop(context.scene.brm_test, "message_text")
        row = layout.row()
        row.prop(context.scene.brm_test, "message_type")

        box = layout.box()
        box.operator("brm.test_operator", text="Report").action = 'REPORT'
        box.operator("brm.test_operator", text="Fix Message").action = 'FIX_MESSAGE'
        
        row = layout.row()
        row.operator("brm.test_operator", text="Unregister").action = 'UNREGISTER'

class BRM_OT_TestOperator(bpy.types.Operator):
    bl_idname = "brm.test_operator"
    bl_label = "My Operator"

    action : bpy.props.EnumProperty(
        name="Action",
        description="Choose an action",
        default='REPORT',
        items=(
            ('REPORT', "", ""),
            ('FIX_MESSAGE', "", ""),
            ('UNREGISTER', "", ""),
        ),
    )

    def execute(self, context):

        props = context.scene.brm_test
        message_type = NotificationType.INFO

        match props.message_type:
            case 'INFO':
                message_type = NotificationType.INFO
            case 'WARNING':
                message_type = NotificationType.WARNING
            case 'ERROR':
                message_type = NotificationType.ERROR
            case 'RUNTIME_ERROR':
                message_type = NotificationType.RUNTIME_ERROR

        # Message system call
        if self.action == 'REPORT':
            report_message(props.message_text, type = message_type)
        if self.action == 'FIX_MESSAGE':
            add_fix_message(props.message_text, type = message_type, index = 0)
        if self.action == 'UNREGISTER':
            unregister_drawn_handler()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(BRM_Properties)
    bpy.types.Scene.brm_test = bpy.props.PointerProperty(type=BRM_Properties)

    bpy.utils.register_class(BRM_PT_BetterReportMessageTests)
    bpy.utils.register_class(BRM_OT_TestOperator)

def unregister():
    bpy.utils.unregister_class(BRM_Properties)
    del bpy.types.Scene.brm_test

    bpy.utils.unregister_class(BRM_PT_BetterReportMessageTests)
    bpy.utils.unregister_class(BRM_OT_TestOperator)

    # Unregister the message system
    unregister_drawn_handler()

if __name__ == "__main__":
    register()