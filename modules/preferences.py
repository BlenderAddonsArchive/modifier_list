import math

import bpy
import addon_utils
import rna_keymap_ui
from bpy.props import *
from bpy.types import AddonPreferences

from .ui.properties_editor import register_DATA_PT_modifiers


class Preferences(AddonPreferences):
    bl_idname = "modifier_list"

    use_popup: BoolProperty(name="Popup", description="Enable/disable popup", default=True)

    use_sidebar: BoolProperty(name="Sidebar Tab",
                              description="Enable/disable sidebar tab", default=True)

    use_properties_editor: BoolProperty(name="Properties Editor",
                                       description="Enable/disable inside Properties Editor",
                                       default=True, update=register_DATA_PT_modifiers)

    modifier_01: StringProperty(description="Add a favourite modifier")
    modifier_02: StringProperty(description="Add a favourite modifier")
    modifier_03: StringProperty(description="Add a favourite modifier")
    modifier_04: StringProperty(description="Add a favourite modifier")
    modifier_05: StringProperty(description="Add a favourite modifier")
    modifier_06: StringProperty(description="Add a favourite modifier")
    modifier_07: StringProperty(description="Add a favourite modifier")
    modifier_08: StringProperty(description="Add a favourite modifier")
    modifier_09: StringProperty(description="Add a favourite modifier")
    modifier_10: StringProperty(description="Add a favourite modifier")
    modifier_11: StringProperty(description="Add a favourite modifier")
    modifier_12: StringProperty(description="Add a favourite modifier")

    mod_list_def_len: IntProperty(
        name="",
        description="Default/min number of rows to display in the modifier list in the popup",
        default=7)

    use_props_dialog: BoolProperty(
        name="Use Dialog Type Popup",
        description="Use a dialog type popup which doesn't close when you are not hovering over it")

    parent_new_gizmo_to_object: BoolProperty(
        name="Auto Parent Gizmos To Active Object",
        description="Automatically parent gizmos to the active object on addition")

    def draw(self, context):
        layout = self.layout

        # === Enable/disable popup and sidebar
        row = layout.row()

        # Disabled for now because of a bug in 2.8.
        # https://developer.blender.org/T60766
        # row.prop(self, "use_popup")

        # wm = bpy.context.window_manager
        # km = wm.keyconfigs.addon.keymaps['3D View']
        # kmi = km.keymap_items["view3d.modifier_popup"]
        # kmi.active = self.use_popup

        row.prop(self, "use_sidebar")
        row.prop(self, "use_properties_editor")

        layout.separator()

        # === Favourite modifiers selection ===
        layout.label(text="Favourite Modifiers:")

        col = layout.column(align=True)

        attr_iter = iter(get_pref_mod_attr_name())

        wm = bpy.context.window_manager

        # Draw two property searches per row
        for attr in attr_iter:
            row = col.split(factor=0.5, align=True)
            row.prop_search(self, attr, wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "ml_mesh_modifiers", text="", icon='MODIFIER')

        layout.separator()

        # === Popup settings ===
        row = layout.row()
        row.label(text="Modifier List Default/Min Height in Popup")
        row.prop(self, "mod_list_def_len")

        row = layout.row()
        row.prop(self, "use_props_dialog")

        layout.separator()

        # Disabled for now because of a bug in 2.8.
        # # === Hotkey ===
        # layout.label(text="Hotkey:")

        # col = layout.column()
        # kc = bpy.context.window_manager.keyconfigs.addon
        # for km, kmi in addon_keymaps:
        #     km = km.active()
        #     col.context_pointer_set("keymap", km)
        #     rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        # layout.separator()

        # === Gizmo object settings ===
        layout.prop(self, "parent_new_gizmo_to_object")

        # === Info ===
        _, is_enabled = addon_utils.check("space_view3d_modifier_tools")
        if not is_enabled:
            layout.label(icon='INFO',
                         text="Enable Modifier Tools addon for modifier batch operators.")


def get_pref_mod_attr_name():
    """List of the names of favourite modifier attributes in Preferences
    class for making drawing favourite modifier selection rows in
    preferences easy.
    """
    attr_name_list = [attr for attr in Preferences.__annotations__ if "modifier_" in attr]
    return attr_name_list