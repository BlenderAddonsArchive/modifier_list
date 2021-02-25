import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import PropertyGroup

from . import modifier_categories
from .utils import get_ml_active_object


# Callbacks
# ======================================================================

def active_object_modifier_active_index_get(self):
    """Function for reading ob.ml_modifier_active_index indirectly
    to avoid problems when using library overrides.
    """
    ob = get_ml_active_object()

    if not ob:
        return 0

    return ob.ml_modifier_active_index


def active_object_modifier_active_index_set(self, value):
    """Function for writing ob.ml_modifier_active_index indirectly
    to avoid problems when using library overrides.
    """
    ob = get_ml_active_object()

    if ob:
        ob.ml_modifier_active_index = value


def set_active_modifier(self, context):
    """Sets the active modifier which is used for node editor context"""
    ob = get_ml_active_object()
    mods = ob.modifiers

    if mods:
        mods[ob.ml_modifier_active_index].is_active = True


def pinned_object_ensure_users(scene):
    """Handler for making sure a pinned object which is only used by
    pinned_object, i.e. an object which was deleted while it was
    pinned, really gets deleted + the property gets reset.
    """
    ml_props = scene.modifier_list
    
    if ml_props.pinned_object:
        if ml_props.pinned_object.users == 1 and not ml_props.pinned_object.use_fake_user:
            bpy.data.objects.remove(ml_props.pinned_object)
            ml_props.pinned_object = None


def on_pinned_object_change(self, context):
    """Callback function for pinned_object"""
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_pre

    if context.scene.modifier_list.pinned_object:
        depsgraph_handlers.append(pinned_object_ensure_users)
    else:
        try:
            depsgraph_handlers.remove(pinned_object_ensure_users)
        except ValueError:
            pass


def set_all_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    all_modifiers = bpy.context.window_manager.modifier_list.all_modifiers

    if not all_modifiers:
        for name, _, mod in modifier_categories.ALL_MODIFIERS_NAMES_ICONS_TYPES:
            item = all_modifiers.add()
            item.name = name
            item.value = mod


def set_mesh_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    mesh_modifiers = bpy.context.window_manager.modifier_list.mesh_modifiers

    if not mesh_modifiers:
        for name, _, mod in modifier_categories.MESH_ALL_NAMES_ICONS_TYPES:
            item = mesh_modifiers.add()
            item.name = name
            item.value = mod


def set_curve_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    curve_modifiers = bpy.context.window_manager.modifier_list.curve_modifiers

    if not curve_modifiers:
        for name, _, mod in modifier_categories.CURVE_ALL_NAMES_ICONS_TYPES:
            item = curve_modifiers.add()
            item.name = name
            item.value = mod


def set_lattice_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    lattice_modifiers = bpy.context.window_manager.modifier_list.lattice_modifiers

    if not lattice_modifiers:
        for name, _, mod in modifier_categories.LATTICE_ALL_NAMES_ICONS_TYPES:
            item = lattice_modifiers.add()
            item.name = name
            item.value = mod


def set_pointcloud_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    pointcloud_modifiers = bpy.context.window_manager.modifier_list.pointcloud_modifiers

    if not pointcloud_modifiers:
        for name, _, mod in modifier_categories.POINTCLOUD_ALL_NAMES_ICONS_TYPES:
            item = pointcloud_modifiers.add()
            item.name = name
            item.value = mod


def set_volume_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    volume_modifiers = bpy.context.window_manager.modifier_list.volume_modifiers

    if not volume_modifiers:
        for name, _, mod in modifier_categories.VOLUME_ALL_NAMES_ICONS_TYPES:
            item = volume_modifiers.add()
            item.name = name
            item.value = mod


@persistent
def on_file_load(dummy):
    set_all_modifier_collection_items()
    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()
    set_pointcloud_modifier_collection_items()
    set_volume_modifier_collection_items()


def add_modifier(self, context):
    # Add modifier
    ml_props = bpy.context.window_manager.modifier_list
    mod_name = ml_props.modifier_to_add_from_search

    if mod_name == "":
        return None

    mod_type = ml_props.all_modifiers[mod_name].value
    bpy.ops.object.ml_modifier_add(modifier_type=mod_type)

    # Executing an operator via a function doesn't create an undo event,
    # so it needs to be added manually.
    bpy.ops.ed.undo_push(message="Add Modifier")


# Modifier collections
# ======================================================================

class AllModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class MeshModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class CurveModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class LatticeModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class PointcloudModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class VolumeModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


# Property groups
# ======================================================================

class ML_SceneProperties(PropertyGroup):
    pinned_object: PointerProperty(
        type=bpy.types.Object,
        update=on_pinned_object_change)


class ML_PreferencesUIProperties(PropertyGroup):
    favourite_modifiers_expand: BoolProperty(name="", default=True)
    favourite_modifiers_menu_expand: BoolProperty(name="", default=True)
    general_expand: BoolProperty(name="")
    popup_expand: BoolProperty(name="")
    gizmo_expand: BoolProperty(name="")


class ML_WindowManagerProperties(PropertyGroup):
    # Property to access ob.ml_modifier_active_index through, to avoid
    # the problem of modifier_active_index not being possible to be
    # changed directly by the modifier list when using library
    # overrides.
    active_object_modifier_active_index: IntProperty(
        get=active_object_modifier_active_index_get,
        set=active_object_modifier_active_index_set
    )
    modifier_to_add_from_search: StringProperty(
        name="Modifier to add",
        update=add_modifier,
        description="Search for a modifier and add it to the stack")
    all_modifiers: CollectionProperty(type=AllModifiersCollection)
    mesh_modifiers: CollectionProperty(type=MeshModifiersCollection)
    curve_modifiers: CollectionProperty(type=CurveModifiersCollection)
    lattice_modifiers: CollectionProperty(type=LatticeModifiersCollection)
    pointcloud_modifiers: CollectionProperty(type=PointcloudModifiersCollection)
    volume_modifiers: CollectionProperty(type=VolumeModifiersCollection)
    popup_tabs_items = [
        ("MODIFIERS", "Modifiers", "Modifiers", 'MODIFIER', 1),
        ("OBJECT_DATA", "Object Data", "Object Data", 'MESH_DATA', 2),
    ]
    popup_active_tab: EnumProperty(
        items=popup_tabs_items,
        name="Popup Tabs",
        default='MODIFIERS')
    preferences_ui_props: PointerProperty(type=ML_PreferencesUIProperties)
    active_favourite_modifier_slot_index: IntProperty()


# Registering
# ======================================================================

classes = (
    AllModifiersCollection,
    MeshModifiersCollection,
    CurveModifiersCollection,
    LatticeModifiersCollection,
    PointcloudModifiersCollection,
    VolumeModifiersCollection,
    ML_SceneProperties,
    ML_PreferencesUIProperties,
    ML_WindowManagerProperties
)


def register():
    # === Properties ===
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.ml_modifier_active_index = IntProperty(
        options={'LIBRARY_EDITABLE'},
        update=set_active_modifier)
    
    wm = bpy.types.WindowManager
    wm.modifier_list = PointerProperty(type=ML_WindowManagerProperties)

    bpy.types.Scene.modifier_list = PointerProperty(type=ML_SceneProperties)
    
    bpy.app.handlers.load_post.append(on_file_load)

    set_all_modifier_collection_items()
    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()
    set_pointcloud_modifier_collection_items()
    set_volume_modifier_collection_items()


def unregister():
    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.ml_modifier_active_index
    del bpy.types.WindowManager.modifier_list
    del bpy.types.Scene.modifier_list

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
