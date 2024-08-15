import bpy
from bpy.types import Context

from .src import bpy_report

# ------------------------------------------------------------------------
#   One-file add-on to test the Better Report Message API
# ------------------------------------------------------------------------

bl_info = {
    "name": "Bpy Report",
    "author": "Rodrigo Gama",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "category": "3D View",
}

bpy_report.set_notification_config(
    bpy_report.BasicConfig(
        use_module_name=True,
        show_notification_type=True,
    )
)


class BRM_Properties(bpy.types.PropertyGroup):
    """Properties for the add-on"""

    message_type: bpy.props.EnumProperty(
        name="Message Type",
        description="Choose a message type",
        items=(
            ("INFO", "INFO", ""),
            ("WARNING", "WARNING", ""),
            ("ERROR", "ERROR", ""),
            ("RUNTIME_ERROR", "RUNTIME_ERROR", ""),
        ),
    )  # type: ignore

    message_text: bpy.props.StringProperty(
        default="This is a test message", name="Message Text"
    )  # type: ignore

    fix_message_index: bpy.props.IntProperty(default=0, name="Fix Message Index")  # type: ignore


class BRM_PT_BPYReportMessageTests(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Bpy Report Message Tests"
    bl_idname = "BRM_PT_BPYReportMessageTests"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BRM Test"

    def draw(self, context: Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.prop(context.scene.brm_test, "message_text")
        row = layout.row()
        row.prop(context.scene.brm_test, "message_type")
        row = layout.row()
        row.prop(context.scene.brm_test, "fix_message_index")

        box = layout.box()
        box.operator("brm.test_operator", text="Report").action = "REPORT"
        box.operator("brm.test_operator", text="Fix Message").action = (
            "FIX_MESSAGE"
        )

        row = layout.row()
        row.operator("brm.test_operator", text="Unregister").action = (
            "UNREGISTER"
        )


class BRM_OT_TestOperator(bpy.types.Operator):
    """Test Operator"""

    bl_idname = "brm.test_operator"
    bl_label = "My Operator"

    action: bpy.props.EnumProperty(
        name="Action",
        description="Choose an action",
        default="REPORT",
        items=(
            ("REPORT", "", ""),
            ("FIX_MESSAGE", "", ""),
            ("UNREGISTER", "", ""),
        ),
    )  # type: ignore

    def execute(self, context: Context):

        props = context.scene.brm_test

        if self.action in ["FIX_MESSAGE", "REPORT"]:

            display_time = 0 if self.action == "FIX_MESSAGE" else 5

            match props.message_type:
                case "INFO":
                    bpy_report.info(
                        props.message_text,
                        display_time=display_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "WARNING":
                    bpy_report.warning(
                        props.message_text,
                        display_time=display_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "ERROR":
                    bpy_report.error(
                        props.message_text,
                        display_time=display_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "RUNTIME_ERROR":
                    bpy_report.runtime_error(
                        props.message_text,
                        display_time=display_time,
                        fix_message_index=props.fix_message_index,
                    )
                case _:
                    bpy_report.info(
                        props.message_text,
                        display_time=display_time,
                        fix_message_index=props.fix_message_index,
                    )

        if self.action == "UNREGISTER":
            bpy_report.unregister_messages()

        return {"FINISHED"}


def register():
    """Register the add-on"""

    bpy.utils.register_class(BRM_Properties)
    bpy.types.Scene.brm_test = bpy.props.PointerProperty(type=BRM_Properties)

    bpy.utils.register_class(BRM_PT_BPYReportMessageTests)
    bpy.utils.register_class(BRM_OT_TestOperator)


def unregister():
    """Unregister the add-on"""

    bpy.utils.unregister_class(BRM_Properties)
    del bpy.types.Scene.brm_test

    bpy.utils.unregister_class(BRM_PT_BPYReportMessageTests)
    bpy.utils.unregister_class(BRM_OT_TestOperator)

    # Unregister the message system
    bpy_report.unregister_messages()


if __name__ == "__main__":
    register()
