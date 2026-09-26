bl_info = {
    "name": "Quick Vertex Color",
    "author": "OpenAI",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Vertex Color",
    "description": "Quickly assign a chosen color to selected mesh vertices",
    "category": "Mesh",
}

import bpy
import bmesh
from bpy.props import EnumProperty, FloatVectorProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup


class QVC_Settings(PropertyGroup):
    attribute_name: StringProperty(
        name="Color Attribute",
        description="Color attribute to edit; it will be created automatically if missing",
        default="Color",
    )

    color: FloatVectorProperty(
        name="Color",
        description="Color assigned to the selected vertices",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    new_domain: EnumProperty(
        name="Domain",
        description="Domain used only when creating a new color attribute",
        items=(
            ("CORNER", "Face Corner", "Store one color per face corner (typical vertex color workflow)"),
            ("POINT", "Point", "Store one color per mesh vertex"),
        ),
        default="CORNER",
    )

    new_data_type: EnumProperty(
        name="Storage",
        description="Storage used only when creating a new color attribute",
        items=(
            ("BYTE_COLOR", "Byte Color", "8-bit per channel color"),
            ("FLOAT_COLOR", "Float Color", "32-bit floating-point per channel color"),
        ),
        default="BYTE_COLOR",
    )


def _selected_vertex_indices(obj):
    """Return selected BMVert indices while the object is in Edit Mode."""
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    return {v.index for v in bm.verts if v.select}


def _write_color(mesh, attr, selected_vertices, color):
    """Write color and return the number of attribute elements changed."""
    changed = 0

    if attr.domain == "POINT":
        data_len = len(attr.data)
        for vertex_index in selected_vertices:
            if 0 <= vertex_index < data_len:
                attr.data[vertex_index].color = color
                changed += 1

    elif attr.domain == "CORNER":
        selected = selected_vertices
        for loop_index, loop in enumerate(mesh.loops):
            if loop.vertex_index in selected:
                attr.data[loop_index].color = color
                changed += 1
    else:
        raise RuntimeError(f"Unsupported color attribute domain: {attr.domain}")

    return changed


class MESH_OT_quick_assign_vertex_color(Operator):
    bl_idname = "mesh.quick_assign_vertex_color"
    bl_label = "Assign to Selected"
    bl_description = "Assign the chosen color to currently selected vertices"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.edit_object
        return obj is not None and obj.type == "MESH" and obj.mode == "EDIT"

    def execute(self, context):
        obj = context.edit_object
        settings = context.scene.qvc_settings

        if obj is None or obj.type != "MESH" or obj.mode != "EDIT":
            self.report({"ERROR"}, "Enter Mesh Edit Mode first")
            return {"CANCELLED"}

        name = settings.attribute_name.strip()
        if not name:
            self.report({"ERROR"}, "Color attribute name cannot be empty")
            return {"CANCELLED"}

        selected_vertices = _selected_vertex_indices(obj)
        if not selected_vertices:
            self.report({"WARNING"}, "No vertices selected")
            return {"CANCELLED"}

        mesh = obj.data
        color = tuple(settings.color)
        changed = 0
        created = False
        attr = None

        try:
            bpy.ops.object.mode_set(mode="OBJECT")

            attr = mesh.color_attributes.get(name)
            if attr is None:
                attr = mesh.color_attributes.new(
                    name=name,
                    type=settings.new_data_type,
                    domain=settings.new_domain,
                )
                created = True

            if attr.data_type not in {"BYTE_COLOR", "FLOAT_COLOR"}:
                raise RuntimeError(
                    f"Attribute '{name}' exists but is not a color attribute "
                    f"(type: {attr.data_type})"
                )

            if attr.domain not in {"POINT", "CORNER"}:
                raise RuntimeError(
                    f"Attribute '{name}' uses unsupported domain: {attr.domain}"
                )

            changed = _write_color(mesh, attr, selected_vertices, color)

            mesh.color_attributes.active_color_name = attr.name
            mesh.update()
            context.view_layer.update()

        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        finally:
            if obj and obj.name in bpy.data.objects and obj.mode != "EDIT":
                try:
                    context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.mode_set(mode="EDIT")
                except Exception:
                    pass

        if changed == 0 and attr and attr.domain == "CORNER":
            self.report(
                {"WARNING"},
                "Selected vertices have no face corners to color (loose vertices?)",
            )
            return {"FINISHED"}

        action = "Created and colored" if created else "Colored"
        self.report(
            {"INFO"},
            f"{action} {len(selected_vertices)} selected vertices "
            f"({changed} {attr.domain.lower()} values)",
        )
        return {"FINISHED"}


class MESH_OT_quick_vertex_color_white(Operator):
    bl_idname = "mesh.quick_vertex_color_white"
    bl_label = "White"
    bl_description = "Set the quick color picker to white"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.qvc_settings.color = (1.0, 1.0, 1.0, 1.0)
        return {"FINISHED"}


class MESH_OT_quick_vertex_color_black(Operator):
    bl_idname = "mesh.quick_vertex_color_black"
    bl_label = "Black"
    bl_description = "Set the quick color picker to black"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.qvc_settings.color = (0.0, 0.0, 0.0, 1.0)
        return {"FINISHED"}


class MESH_OT_quick_vertex_color_red(Operator):
    bl_idname = "mesh.quick_vertex_color_red"
    bl_label = "Red"
    bl_description = "Set the quick color picker to red"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.qvc_settings.color = (1.0, 0.0, 0.0, 1.0)
        return {"FINISHED"}


class MESH_OT_quick_vertex_color_green(Operator):
    bl_idname = "mesh.quick_vertex_color_green"
    bl_label = "Green"
    bl_description = "Set the quick color picker to green"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.qvc_settings.color = (0.0, 1.0, 0.0, 1.0)
        return {"FINISHED"}


class MESH_OT_quick_vertex_color_blue(Operator):
    bl_idname = "mesh.quick_vertex_color_blue"
    bl_label = "Blue"
    bl_description = "Set the quick color picker to blue"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.qvc_settings.color = (0.0, 0.0, 1.0, 1.0)
        return {"FINISHED"}


class VIEW3D_PT_quick_vertex_color(Panel):
    bl_label = "Quick Vertex Color"
    bl_idname = "VIEW3D_PT_quick_vertex_color"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Vertex Color"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.qvc_settings
        obj = context.active_object

        layout.prop(settings, "attribute_name")
        layout.prop(settings, "color")

        row = layout.row(align=True)
        row.operator("mesh.quick_vertex_color_black", text="Black")
        row.operator("mesh.quick_vertex_color_white", text="White")

        row = layout.row(align=True)
        row.operator("mesh.quick_vertex_color_red", text="Red")
        row.operator("mesh.quick_vertex_color_green", text="Green")
        row.operator("mesh.quick_vertex_color_blue", text="Blue")

        layout.separator()

        box = layout.box()
        box.label(text="When creating a new attribute:")
        box.prop(settings, "new_domain")
        box.prop(settings, "new_data_type")

        layout.separator()
        col = layout.column()
        col.scale_y = 1.35
        col.operator("mesh.quick_assign_vertex_color", icon="BRUSH_DATA")

        if obj is None or obj.type != "MESH":
            layout.label(text="Select a mesh object", icon="INFO")
        elif obj.mode != "EDIT":
            layout.label(text="Enter Edit Mode and select vertices", icon="INFO")
        else:
            attr = obj.data.color_attributes.get(settings.attribute_name.strip())
            if attr is not None:
                layout.label(
                    text=f"Using: {attr.name} / {attr.domain} / {attr.data_type}",
                    icon="COLOR",
                )


classes = (
    QVC_Settings,
    MESH_OT_quick_assign_vertex_color,
    MESH_OT_quick_vertex_color_white,
    MESH_OT_quick_vertex_color_black,
    MESH_OT_quick_vertex_color_red,
    MESH_OT_quick_vertex_color_green,
    MESH_OT_quick_vertex_color_blue,
    VIEW3D_PT_quick_vertex_color,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.qvc_settings = PointerProperty(type=QVC_Settings)


def unregister():
    if hasattr(bpy.types.Scene, "qvc_settings"):
        del bpy.types.Scene.qvc_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
