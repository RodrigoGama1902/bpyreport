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


class BRM_ConfigPlayground(bpy.types.PropertyGroup):
    """Config Playground"""

    module_name: bpy.props.StringProperty(default="My Module", name="Module Name", update=lambda self, context: self.update_report_settings(context))  # type: ignore
    use_module_name: bpy.props.BoolProperty(default=True, name="Use Module Name", update=lambda self, context: self.update_report_settings(context))  # type: ignore
    show_notification_type: bpy.props.BoolProperty(default=True, name="Show Notification Type", update=lambda self, context: self.update_report_settings(context))  # type: ignore

    text_size: bpy.props.IntProperty(default=40, name="Text Size", update=lambda self, context: self.update_report_settings(context))  # type: ignore

    end_x: bpy.props.FloatProperty(default=1, name="End X", update=lambda self, context: self.update_report_settings(context))  # type: ignore
    start_x: bpy.props.FloatProperty(default=0.8, name="Start X", update=lambda self, context: self.update_report_settings(context))  # type: ignore

    spacing: bpy.props.IntProperty(default=5, name="Spacing", update=lambda self, context: self.update_report_settings(context))  # type: ignore
    first_y_location: bpy.props.IntProperty(default=50, name="First Y Location", update=lambda self, context: self.update_report_settings(context))  # type: ignore

    info: bpy.props.FloatVectorProperty(
        default=(0.1, 0.1, 0.1, 0.7),
        min=0.0,
        max=1.0,
        name="Info",
        subtype="COLOR",
        size=4,
        update=lambda self, context: self.update_report_settings(context),  # type: ignore
    )  # type: ignore
    warning: bpy.props.FloatVectorProperty(
        default=(1.0, 0.5, 0.0, 0.3),
        min=0.0,
        max=1.0,
        name="Warning",
        subtype="COLOR",
        size=4,
        update=lambda self, context: self.update_report_settings(context),  # type: ignore
    )  # type: ignore
    error: bpy.props.FloatVectorProperty(
        default=(1.0, 0.0, 0.0, 0.15),
        min=0.0,
        max=1.0,
        name="Error",
        subtype="COLOR",
        size=4,
        update=lambda self, context: self.update_report_settings(context),  # type: ignore
    )  # type: ignore
    runtime_error: bpy.props.FloatVectorProperty(
        default=(1.0, 0.0, 0.0, 0.3),
        min=0.0,
        max=1.0,
        name="Runtime Error",
        subtype="COLOR",
        size=4,
        update=lambda self, context: self.update_report_settings(context),  # type: ignore
    )  # type: ignore

    def draw(self, layout: bpy.types.UILayout):
        """Draw the properties in the UI"""

        col = layout.column(align=True)
        col.prop(self, "module_name")
        col.prop(self, "use_module_name")
        col.prop(self, "show_notification_type")

        col = layout.column(align=True)
        col.prop(self, "text_size")
        col.prop(self, "start_x")
        col.prop(self, "end_x")
        col.prop(self, "spacing")
        col.prop(self, "first_y_location")

        col = layout.column(align=True)
        col.prop(self, "info")
        col.prop(self, "warning")
        col.prop(self, "error")
        col.prop(self, "runtime_error")

    def update_report_settings(self, context: Context):
        """Update the report settings"""

        bpy_report.set_notification_config(
            bpy_report.BasicConfig(
                use_module_name=self.use_module_name,
                show_notification_type=self.show_notification_type,
                module_name=self.module_name,
            ),
            bpy_report.NotificationDrawConfig(
                text_size=self.text_size,
                end_x=self.end_x,
                spacing=self.spacing,
                first_y_location=self.first_y_location,
                start_x=self.start_x,
            ),
            bpy_report.NotificationColorConfig(
                info=self.info,
                warning=self.warning,
                error=self.error,
                runtime_error=self.runtime_error,
            ),
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

    config_playground: bpy.props.PointerProperty(type=BRM_ConfigPlayground)  # type: ignore


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

        props = context.scene.brm_test

        row = layout.row()
        row.prop(props, "message_text")
        row = layout.row()
        row.prop(props, "message_type")
        row = layout.row()
        row.prop(props, "fix_message_index")

        box = layout.box()
        box.operator("brm.test_operator", text="Report").action = "REPORT"
        box.operator("brm.test_operator", text="Fix Message").action = (
            "FIX_MESSAGE"
        )

        row = layout.row()
        row.operator("brm.test_operator", text="Unregister").action = (
            "UNREGISTER"
        )

        box = layout.box()
        props.config_playground.draw(box)


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

            remove_in_time = 0 if self.action == "FIX_MESSAGE" else 5

            match props.message_type:
                case "INFO":
                    bpy_report.info(
                        props.message_text,
                        remove_in_time=remove_in_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "WARNING":
                    bpy_report.warning(
                        props.message_text,
                        remove_in_time=remove_in_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "ERROR":
                    bpy_report.error(
                        props.message_text,
                        remove_in_time=remove_in_time,
                        fix_message_index=props.fix_message_index,
                    )
                case "RUNTIME_ERROR":
                    bpy_report.runtime_error(
                        props.message_text,
                        remove_in_time=remove_in_time,
                        fix_message_index=props.fix_message_index,
                    )
                case _:
                    bpy_report.info(
                        props.message_text,
                        remove_in_time=remove_in_time,
                        fix_message_index=props.fix_message_index,
                    )

        if self.action == "UNREGISTER":
            bpy_report.unregister_messages()

        return {"FINISHED"}


def register():
    """Register the add-on"""

    bpy.utils.register_class(BRM_ConfigPlayground)
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
    bpy.utils.unregister_class(BRM_ConfigPlayground)

    # Unregister the message system
    bpy_report.unregister_messages()


if __name__ == "__main__":
    register()
