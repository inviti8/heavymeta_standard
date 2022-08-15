"""
[Blender and Python] Heavymeta Standard 
Meta-Cronos - August 2022
Email: comicronos@gmail.com
Addon to add standardized meta-data to the scene at the API level.  Standard
Heavmeta Data are offered as a proposed framework that is based on standards
defined here: https://www.nftstandards.wtf/NFT/NFT+Metadata.  Additional att-
ributes have been added to support properties used in 3D art and Animation. 
I have opted to make all NFT related data adsignable at the Collection level.
This seems to make the most sense, given that 3D elements usually a hierarchy
of several object types.
--------
MIT License
Copyright (c) 2022 Heavymeta
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    # required
    'name': 'Heavymeta Standard NFT Data',
    'blender': (3, 2, 0),
    'category': 'Collections',
    # optional
    'version': (0, 0, 0),
    'author': 'Meta-Cronos',
    'description': 'Assign Heavymeta Standard properties and meta-data at the Collection level.',
}

import bpy
import re
from rna_prop_ui import PropertyPanel
from bpy.types import (Panel,
                       BoolProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       Collection)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

# -------------------------------------------------------------------
#   Heavymeta Standards Panel
# -------------------------------------------------------------------
PROPS = [
    ('minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=(
            ('HVYC', "Character", ""),
            ('HVYI', "Immortal", ""),
            ('HVYA', "Animal", ""),
            ('HVYW', "Weapon", ""),
            ('HVYO', "Object", ""),
            ('HVYG', "Generic", ""),
            ('HVYAU', "Auricle", "")))),
    ('minter_name', bpy.props.StringProperty(name='Minter-Name', default='')),
    ('minter_description', bpy.props.StringProperty(name='Minter-Description', default='')),
    ('minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='')),
    ('add_version', bpy.props.BoolProperty(name='Minter-Version', default=False)),
    ('minter_version', bpy.props.IntProperty(name='Version', default=1)),
]

# ------------------------------------------------------------------------
#    Heavymeta Traits
# ------------------------------------------------------------------------
#mesh trait getters
def mesh_trait(self):
    return self['mesh']
#
def mesh_list_label(self):
    return self['Mesh-Traits']


#morph trait getters
def morph_trait(self):
    return self['morph']
#
def morph_list_label(self):
    return self['Morph-Traits']


#anim trait getters
def anim_trait(self):
    return self['anim']
#
def anim_list_label(self):
    return self['Anim-Traits']


class ObjectPointer(PropertyGroup):
    """Pointer Object, for collections inside of collections."""
    obj: bpy.props.PointerProperty(type = bpy.types.Object)


#mesh traits
class MeshTrait(bpy.types.PropertyGroup):
    """Standard mesh meta-data trait object"""
    trait_type = bpy.props.StringProperty(get=mesh_trait)
    value = bpy.props.StringProperty()
#
class MeshTraitList(bpy.types.PropertyGroup):
    """List of mesh meta-data trait objects"""
    name: bpy.props.StringProperty(get=mesh_list_label)
    object_group: bpy.props.CollectionProperty(type = ObjectPointer)


# #morph traits
class MorphTrait(bpy.types.PropertyGroup):
    """Standard morph meta-data trait object"""
    trait_type = bpy.props.StringProperty(get=morph_trait)
    value = bpy.props.StringProperty()
#
class MorphTraitList(bpy.types.PropertyGroup):
    """List of morph meta-data trait objects"""
    name: bpy.props.StringProperty(get=morph_list_label)
    object_group: bpy.props.CollectionProperty(type = ObjectPointer)


#animation traits
class AnimTrait(bpy.types.PropertyGroup):
    """Standard animation meta-data trait object"""
    trait_type = bpy.props.StringProperty(get=anim_trait)
    value = bpy.props.StringProperty()
#
class AnimTraitList(bpy.types.PropertyGroup):
    """List of animation meta-data trait objects"""
    name: bpy.props.StringProperty(get=anim_list_label)
    object_group: bpy.props.CollectionProperty(type = ObjectPointer)

class ListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    name: bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    random_prop: bpy.props.StringProperty(
           name="Any other property you want",
           description="",
           default="")


class MY_UL_List(UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)


class LIST_OT_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.collection.my_list.add()

        return{'FINISHED'}


class LIST_OT_DeleteItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.collection.my_list

    def execute(self, context):
        my_list = context.collection.my_list
        index = context.collection.list_index

        my_list.remove(index)
        context.collection.list_index = min(max(0, index - 1), len(my_list) - 1)

        return{'FINISHED'}

class LIST_OT_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "my_list.move_item"
    bl_label = "Move an item in the list"

    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.collection.my_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.collection.list_index
        list_length = len(bpy.context.collection.my_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.collection.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.collection.my_list
        index = context.collection.list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index(self)

        return{'FINISHED'}

class LIST_OT_DirectionUp(bpy.types.Operator):
    """Set direction of LIST_OT_MoveItem.deirection to UP."""
    bl_idname = "my_list.set_direction_up"
    bl_label = "Set the move direction to up"

    @classmethod
    def poll(cls, context):
        return context.collection.my_list

    def execute(self, context):
        
        LIST_OT_MoveItem.direction = "UP"
        LIST_OT_MoveItem.execute(LIST_OT_MoveItem, context)
        return{'FINISHED'}


class LIST_OT_DirectionDown(bpy.types.Operator):
    """Set direction of LIST_OT_MoveItem.deirection to Down."""
    bl_idname = "my_list.set_direction_down"
    bl_label = "Set the move direction to down"

    @classmethod
    def poll(cls, context):
        return context.collection.my_list

    def execute(self, context):
        
        LIST_OT_MoveItem.direction = "DOWN"
        LIST_OT_MoveItem.execute(LIST_OT_MoveItem, context)
        return{'FINISHED'}

# ------------------------------------------------------------------------
#    Heavymeta Operators
# ------------------------------------------------------------------------

class OpAddTrait(bpy.types.Operator):
    """Print object name in Console"""
    bl_idname = "collection.add_trait_operator"
    bl_label = "Add Trait Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print (context.collection)
        my_item = bpy.context.collection.hvym_mesh_list.add()
        my_item.value = "100"
        return {'FINISHED'}


class OpRemoveTrait(bpy.types.Operator):
    """Print object name in Console"""
    bl_idname = "collection.remove_trait_operator"
    bl_label = "Remove Trait Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print (context.collection)
        return {'FINISHED'}

class HeavymetaStandardDataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Heavymeta Standard"
    bl_idname = "COLLECTION_PT_heavymeta_standard_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        col = self.layout.column()
        ctx = context.collection
        for (prop_name, _) in PROPS:
            row = col.row()
            if prop_name == 'minter_version':
                row = row.row()
                row.enabled = context.collection.add_version
            row.prop(context.collection, prop_name)
        row = col.row()
        row.separator()
        row.label(text="Traits:")
        row.operator(OpAddTrait.bl_idname, text="Add", icon="ADD")
        row.operator(OpRemoveTrait.bl_idname, text="Remove", icon="REMOVE")
        row = col.row()
        row.template_list("MY_UL_List", "The_List", ctx,
                          "my_list", ctx, "list_index")

        row = col.row()
        row.operator('my_list.new_item', text='NEW')
        row.operator('my_list.delete_item', text='REMOVE')
        row.operator('my_list.set_direction_up', text='UP')
        row.operator('my_list.set_direction_down', text='DOWN')

        if ctx.list_index >= 0 and ctx.my_list:
            item = ctx.my_list[ctx.list_index]

            row = col.row()
            row.prop(item, "name")
            row.prop(item, "random_prop")



# -------------------------------------------------------------------
#   Custom Properties Panel
# -------------------------------------------------------------------
class CollectionButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

class COLLECTION_PT_collection_custom_props(CollectionButtonsPanel, PropertyPanel, Panel): 
    
    _context_path = "collection"
    _property_type = Collection

# -------------------------------------------------------------------
#   Class Registration
# -------------------------------------------------------------------
blender_classes = [
    ObjectPointer,
    MeshTrait,
    MeshTraitList,
    OpAddTrait,
    OpRemoveTrait,
    ListItem,
    MY_UL_List,
    LIST_OT_NewItem,
    LIST_OT_DeleteItem,
    LIST_OT_MoveItem,
    LIST_OT_DirectionUp,
    LIST_OT_DirectionDown,
    HeavymetaStandardDataPanel,
    COLLECTION_PT_collection_custom_props
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    bpy.types.Collection.hvym_mesh_list = bpy.props.CollectionProperty(type = MeshTrait)
    bpy.types.Collection.my_list = bpy.props.CollectionProperty(type = ListItem)
    bpy.types.Collection.list_index = bpy.props.IntProperty(name = "Index for my_list",
                                             default = 0)


def unregister():
    del bpy.types.Collection.my_list
    del bpy.types.Collection.list_index
    del bpy.types.Collection.hvym_mesh_list

    for (prop_name, _) in PROPS:
        delattr(bpy.types.Collection, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

if __name__ == "__main__":
    register()