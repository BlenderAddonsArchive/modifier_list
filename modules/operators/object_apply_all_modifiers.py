"""
This operator is inspired by Modifier Tools add-on, thanks for the authors
meta-androcto, saidenka and lijenstina.
https://wiki.blender.org/wiki/Extensions:2.6/Py/Scripts/3D_interaction/modifier_tools
"""

import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator


class OBJECT_OT_ml_apply_all_modifiers(Operator):
    bl_idname = "object.ml_apply_all_modifiers"
    bl_label = "Apply All Modifiers"
    bl_description = "Apply all modifiers of the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        obs = context.selected_objects

        if not obs:
            self.report({'INFO'}, "No selection")
            return {'CANCELLED'}

        obs_have_mods = False
        obs_with_mods_failed_to_apply = []


        is_edit_mode = context.mode in {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE',
                                        'EDIT_TEXT', 'EDIT_LATTICE'}

        if is_edit_mode:
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push(message="Toggle Editmode")

        override = context.copy()

        for ob in obs:
            override['object'] = ob
            mods = ob.modifiers
            for mod in mods:
                if prefs.disallow_applying_hidden_modifiers and not mod.show_viewport:
                    continue

                try:
                    bpy.ops.object.modifier_apply(override, apply_as='DATA', modifier=mod.name)
                except:
                    if ob.name not in obs_with_mods_failed_to_apply:
                        obs_with_mods_failed_to_apply.append(ob.name)

                obs_have_mods = True

            # Make sure some modifier is always active even if all
            # modifiers can't be applied
            mods_len = len(mods) - 1
            new_index = np.clip(mods_len, 0, 99)
            ob.ml_modifier_active_index = new_index

        if is_edit_mode:
            bpy.ops.ed.undo_push(message="Apply All Modifiers")
            bpy.ops.object.editmode_toggle()

        if not obs_have_mods:
            self.report({'INFO'}, "No modifiers to apply")
            return {'CANCELLED'}

        if obs_with_mods_failed_to_apply:
            failed_obs = ", ".join(obs_with_mods_failed_to_apply)
            if len(obs_with_mods_failed_to_apply) < 8:
                self.report({'INFO'}, f"Some modifier(s) couldn't be applied on {failed_obs}")
            else:
                self.report({'INFO'}, "Some modifier(s) couldn't be applied. Check the system "
                                      "console for a list of the objects.")
                print(f"Some modifier(s) couldn't be applied on {failed_obs}")
        else:
            if 'APPLY' in prefs.batch_ops_reports:
                if prefs.disallow_applying_hidden_modifiers:
                    self.report({'INFO'}, "Applied all visible modifiers")
                else:
                    self.report({'INFO'}, "Applied all modifiers")

        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if prefs.show_confirmation_popups:
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)