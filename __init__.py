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

import collections
from configparser import InterpolationDepthError
from contextvars import Context
from socket import has_dualstack_ipv6
from time import time
import bpy
import re
import random
from os import path
from typing import Dict
from bpy.app.handlers import persistent
from rna_prop_ui import PropertyPanel
from bpy.types import (Panel,
                       BoolProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       Collection,
                       Operator,
                       Header,
                       Menu,
                       PropertyGroup,
                       UIList)


glTF_extension_name = "HVYM_nft_data"

# Custom hooks. Defined here and registered/unregistered in register()/unregister().
# Note: If other installed addon have custom hooks on the same way at the same places
#       they can be conflicted. Ex: There are two addons A and B which have custom hooks.
#       Imagine A is installed, B is installed, and then A is removed. B is still installed
#       But removing A resets the hooks in unregister().

# The glTF2 importer doesn't provide a hook mechanism for user extensions so
# manually extend a function to import the extension
from io_scene_gltf2.blender.imp.gltf2_blender_node import BlenderNode
orig_create_obj = BlenderNode.create_object
def patched_create_object(gltf, vnode_id):
    print('patched_create_object + '+str(vnode_id))
    obj = orig_create_obj(gltf, vnode_id)
    length = len(gltf.data.nodes)-1

    if vnode_id == 0:
        create_collections(gltf)

    assign_collections_hvym_data(obj, gltf)

    print("length is: " + str(length) + " index: " + str(vnode_id))
    if vnode_id == length:
        cleanup_scene_collection()

    return obj



# -------------------------------------------------------------------
#   Heavymeta Standards Panel
# -------------------------------------------------------------------
def random_id(length = 8):
    """ Generates a random alphanumeric id string.
    """
    tlength = int(length / 2)
    rlength = int(length / 2) + int(length % 2)

    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    text = ""
    for i in range(0, rlength):
        text += random.choice(chars)
    text += str(hex(int(time())))[2:][-tlength:].rjust(tlength, '0')[::-1]
    return text

def setCollectionId(collection):
    if collection.hvym_id == '':
        collection.hvym_id = random_id()


def updateNftData(context):
    #Update all the props on any change
    #put them into a single structure
    if context.collection.name == 'Scene Collection':
        return
        
    hvym_meta_data = context.collection.hvym_meta_data
    setCollectionId(context.collection)
    intProps = []
    meshProps = []
    morphProps = []
    animProps = []
    materials = []
    nodes = []

    for i in range(len(hvym_meta_data)):
        if hvym_meta_data[i].trait_type == 'property':
            data={}
            data[hvym_meta_data[i].type] = hvym_meta_data[i].values
            intProps.append(data)
        elif hvym_meta_data[i].trait_type == 'mesh':
            data={}
            data[hvym_meta_data[i].type] = hvym_meta_data[i].values
            meshProps.append(data)
        elif hvym_meta_data[i].trait_type == 'morph':
            data={}
            data[hvym_meta_data[i].type] = hvym_meta_data[i].values
            morphProps.append(data)
        elif hvym_meta_data[i].trait_type == 'anim':
            animProps.append(hvym_meta_data[i].type)
        elif hvym_meta_data[i].trait_type == 'material':
            materials.append(hvym_meta_data[i].type)

    for obj in context.collection.objects:
        nodes.append(obj.name)
        obj.hvym_id = context.collection.hvym_id
        

    context.scene.hvym_collections_data.nftData[context.collection.hvym_id] = {'nftType': context.collection.nft_type,
                                                                                'nftPrice': round(context.collection.nft_price, 4),
                                                                                'premNftPrice': round(context.collection.prem_nft_price, 4),
                                                                                'maxSupply': context.collection.max_supply,
                                                                                'minterType': context.collection.minter_type,
                                                                                'minterName': context.collection.minter_name,
                                                                                'minterDesc': context.collection.minter_description,
                                                                                'minterImage': context.collection.minter_image,
                                                                                'minterVersion': context.collection.minter_version,
                                                                                'intProps': intProps,
                                                                                'meshProps': meshProps,
                                                                                'morphProps': morphProps,
                                                                                'animProps': animProps,
                                                                                'materials': materials,
                                                                                "collection_name": context.collection.name,
                                                                                "nodes": nodes
                                                                                }
    


def onUpdate(self, context):
    updateNftData(context)


def setEnum(tup, set_enum, default_enum):

    result = tup

    def get_index(tup, enum_val):
        index = 0
        for item in tup:
            if enum_val == item[0]:
                break
            index += 1
        
        return index

    def set_start_index(tup, enum_val):
        
        if enum_val != default_enum:
            index = get_index(tup, enum_val)
            item = tup[index]
            tup = tup[ : 0] + (item, ) + tup[0 : ]
            # Delete the element at old index 
            tup = tup[ : index] + tup[index+2: ]

        return tup

    result = set_start_index(result, set_enum)

    return result


def nftTypes(self, context):
    #get the default enum, used to set enum on import
    first_enum = context.collection.hvym_nft_type_enum 

    tup = (
            ('HVYC', "Character", ""),
            ('HVYI', "Immortal", ""),
            ('HVYA', "Animal", ""),
            ('HVYW', "Weapon", ""),
            ('HVYO', "Object", ""),
            ('HVYG', "Generic", ""),
            ('HVYAU', "Auricle", ""))

    result = setEnum(tup, first_enum, 'HVYC')

    return result


def minterTypes(self, context):
    #get the default enum, used to set enum on import
    first_enum = context.collection.hvym_minter_type_enum 

    tup = (
            ('payable', "Publicly Mintable", ""),
            ('onlyOnwner', "Privately Mintable", ""))


    result = result = setEnum(tup, first_enum, 'payable')

    return result


PROPS = [
    ('nft_type', bpy.props.EnumProperty(
        name='NFT-Type',
        items=nftTypes,
        description ="Heavymeta NFT type, see docs for more detail.",
        update=onUpdate)),
    ('nft_price', bpy.props.FloatProperty(name='NFT-Price', default=0.01, description ="Price of NFT in eth.", update=onUpdate)),
    ('prem_nft_price', bpy.props.FloatProperty(name='Premium-NFT-Price', default=0.01, description ="Premium price of customized NFT in eth.", update=onUpdate)),
    ('max_supply', bpy.props.IntProperty(name='Max-Supply', default=-1, description ="Max number that can be minted, if -1 supply is infinite.", update=onUpdate)),
    ('minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=minterTypes,
        description ="Minted by creator only, or public.",
        update=onUpdate)),
    ('minter_name', bpy.props.StringProperty(name='Minter-Name', default='', description ="Name of minter.", update=onUpdate)),
    ('minter_description', bpy.props.StringProperty(name='Minter-Description', default='', description ="Details about the NFT.", update=onUpdate)),
    ('minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='', description ="Custom header image for the minter ui.", update=onUpdate)),
    ('add_version', bpy.props.BoolProperty(name='Minter-Version', description ="Enable versioning for this NFT minter.", default=False)),
    ('minter_version', bpy.props.IntProperty(name='Version', default=-1, description ="Version of the NFT minter.", update=onUpdate)),
]


class HVYM_ListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    trait_type: bpy.props.StringProperty(
           name="Type",
           description="meta-data trait type",
           default="",
           update=onUpdate)

    type: bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="",
           update=onUpdate)

    values: bpy.props.StringProperty(
           name="Values",
           description="Add '(default, min, max)'",
           default="",
           update=onUpdate)

    note: bpy.props.StringProperty(
           name="Note",
           description="Add a note, (not exported).",
           default="",
           update=onUpdate)


class HVYM_UL_DataList(bpy.types.UIList):
    """Heavymet data list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'FUND'

        if item.trait_type == 'mesh':
            custom_icon = 'MESH_ICOSPHERE'
        elif item.trait_type == 'morph':
            custom_icon = 'SHAPEKEY_DATA'
        elif item.trait_type == 'anim':
            custom_icon = 'ACTION_TWEAK'
        elif item.trait_type == 'material':
            custom_icon = 'SHADING_RENDERED'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.values)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.values)

# ------------------------------------------------------------------------
#    Heavymeta Operators
# ------------------------------------------------------------------------
class HVYM_LIST_NewPropItem(bpy.types.Operator):
    """Add a new nft property item to the list."""

    bl_idname = "hvym_meta_data.new_property_item"
    bl_label = "Add a new property item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'property'
        item.type = '*'
        item.values = '(0,0,1)'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMeshItem(bpy.types.Operator):
    """Add a new mesh item to the list."""

    bl_idname = "hvym_meta_data.new_mesh_item"
    bl_label = "Add a new mesh item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mesh'
        item.type = '*'
        item.values = 'visible'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMorphItem(bpy.types.Operator):
    """Add a new morph item to the list."""

    bl_idname = "hvym_meta_data.new_morph_item"
    bl_label = "Add a new morph item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'morph'
        item.type = '*'
        item.values = '(0,0,1)'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewAnimItem(bpy.types.Operator):
    """Add a new animation item to the list."""

    bl_idname = "hvym_meta_data.new_anim_item"
    bl_label = "Add a new animation item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'anim'
        item.type = '*'
        item.values = 'N/A'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMatItem(bpy.types.Operator):
    """Add a new animation item to the list."""

    bl_idname = "hvym_meta_data.new_mat_item"
    bl_label = "Add a new material item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'material'
        item.values = 'N/A'
        updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_DeleteItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "hvym_meta_data.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index

        hvym_meta_data.remove(index)
        context.collection.hvym_list_index = min(max(0, index - 1), len(hvym_meta_data) - 1)

        return{'FINISHED'}

class HVYM_LIST_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "hvym_meta_data.move_item"
    bl_label = "Move an item in the list"

    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.collection.hvym_list_index
        list_length = len(bpy.context.collection.hvym_meta_data) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.collection.hvym_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        hvym_meta_data.move(neighbor, index)
        self.move_index(self)

        return{'FINISHED'}

class HVYM_LIST_DirectionUp(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveItem.deirection to UP."""
    bl_idname = "hvym_meta_data.set_direction_up"
    bl_label = "Set the move direction to up"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveItem.direction = "UP"
        HVYM_LIST_MoveItem.execute(HVYM_LIST_MoveItem, context)
        return{'FINISHED'}


class HVYM_LIST_DirectionDown(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveItem.deirection to Down."""
    bl_idname = "hvym_meta_data.set_direction_down"
    bl_label = "Set the move direction to down"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveItem.direction = "DOWN"
        HVYM_LIST_MoveItem.execute(HVYM_LIST_MoveItem, context)
        return{'FINISHED'}


class HVYM_LIST_DefaultValues(bpy.types.Operator):
    """Set default values for item."""

    bl_idname = "hvym_meta_data.default_values"
    bl_label = "Set default values for item in the list."

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index

        item = hvym_meta_data[index]

        if item.trait_type == 'property':
            item.values = '(0,0,1)'
        elif item.trait_type == 'mesh':
            item.values = 'visible'
        elif item.trait_type == 'morph':
            item.values = '(0,0,1)'
        elif item.trait_type == 'anim':
            item.values = 'N/A'
        elif item.trait_type == 'material':
            item.values = 'N/A'

        return{'FINISHED'}

class HVYM_DataReload(bpy.types.Operator):
    bl_idname = "hvym_data.reload"
    bl_label = "Reload Data"
    bl_description ="Reload the data for this collection."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Update NFT Data")
        updateNftData(bpy.context)
        return {'FINISHED'}

class HVYM_DataOrder(bpy.types.Operator):
    bl_idname = "hvym_data.order"
    bl_label = "Order Data"
    bl_description ="Reorder the data for this collection."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        hvym_meta_data = bpy.context.collection.hvym_meta_data
        intProps = []
        meshProps = []
        morphProps = []
        animProps = []
        materials = []

        for data in hvym_meta_data:
            obj = {'trait_type':data.trait_type, 'type':data.type, 'values':data.values}
            if obj['trait_type'] == 'property':
                intProps.append(obj)
            elif obj['trait_type'] == 'mesh':
                meshProps.append(obj)
            elif obj['trait_type'] == 'morph':
                morphProps.append(obj)
            elif obj['trait_type'] == 'anim':
                animProps.append(obj)
            elif obj['trait_type'] == 'material':
                materials.append(obj)

        allProps = [intProps, meshProps, morphProps, animProps, materials]

        for i in range(len(hvym_meta_data)):
            bpy.ops.hvym_meta_data.delete_item()
        
        for arr in allProps:
            for item in arr:
                new_item = bpy.context.collection.hvym_meta_data.add()
                new_item.trait_type = item['trait_type']
                new_item.type = item['type']
                new_item.values = item['values']
                

        return {'FINISHED'}

class HVYM_DebugMinter(bpy.types.Operator):
    bl_idname = "hvym_debug.minter"
    bl_label = "Launch Minter Debug UI"
    bl_description ="Launch minter UI debug."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Debug Minter")
        for data in context.collection.hvym_meta_data:
            print(data.type)
        return {'FINISHED'}


class HVYM_DebugModel(bpy.types.Operator):
    bl_idname = "hvym_debug.model"
    bl_label = "Launch Model Debug UI"
    bl_description ="Launch model UI debug."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Debug Model")
        return {'FINISHED'}


class HVYM_DeployMinter(bpy.types.Operator):
    bl_idname = "hvym_deploy.minter"
    bl_label = "Launch Deploy Minter UI"
    bl_description ="Deploy NFT minter."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Deploy Minter")
        return {'FINISHED'}


class HVYM_DataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Heavymeta Standard"
    bl_idname = "COLLECTION_PT_heavymeta_standard_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        col = self.layout.column()
        box = col.row()
        row = box.row()
        row.operator('hvym_data.reload', text='', icon='FILE_REFRESH')
        ctx = context.collection
        for (prop_name, _) in PROPS:
            row = col.row()
            if prop_name == 'minter_version':
                row = row.row()
                row.enabled = context.collection.add_version
            row.prop(context.collection, prop_name)
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="NFT Data:")
        row = box.row()
        row.operator('hvym_data.order', text='', icon='LINENUMBERS_ON')
        row.template_list("HVYM_UL_DataList", "The_List", ctx,
                          "hvym_meta_data", ctx, "hvym_list_index")

        row = box.row()
        row.operator('hvym_meta_data.new_property_item', text='+', icon='FUND')
        row.operator('hvym_meta_data.new_mesh_item', text='+', icon='MESH_ICOSPHERE')
        row.operator('hvym_meta_data.new_morph_item', text='+', icon='SHAPEKEY_DATA')
        row.operator('hvym_meta_data.new_anim_item', text='+', icon='ACTION_TWEAK')
        row.operator('hvym_meta_data.new_mat_item', text='+', icon='SHADING_RENDERED')
        row.operator('hvym_meta_data.delete_item', text='', icon='CANCEL')
        row.operator('hvym_meta_data.set_direction_up', text='', icon='SORT_DESC')
        row.operator('hvym_meta_data.set_direction_down', text='', icon='SORT_ASC')
        row.operator('hvym_meta_data.default_values', text='', icon='CON_TRANSLIKE')

        if ctx.hvym_list_index >= 0 and ctx.hvym_meta_data:
            item = ctx.hvym_meta_data[ctx.hvym_list_index]

            row = box.row()
            row.prop(item, "type")
            row.prop(item, "values")
            row = box.row()
            row.prop(item, "note")
        row = col.row()
        row.separator()
        box = col.box()
        row = box.row()
        row.label(text="Debugging:")
        row = box.row()
        row.operator('hvym_debug.minter', text="Debug Minter", icon="CONSOLE")
        row.operator('hvym_debug.model', text="Debug Model", icon="CONSOLE")
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="Deploy:")
        row = box.row()
        row.operator('hvym_deploy.minter', text="Deploy", icon="URL")


# -------------------------------------------------------------------
#   Heavymeta Standards Panel
# ------------------------------------------------------------------- 
class HVYM_NFTDataExtensionProps(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="enabled", default=True)
    nftData: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)
    colData: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)


# -------------------------------------------------------------------
#   DEBUG RIGHT CLICK MENU
# ------------------------------------------------------------------- 
bpy.types.GLTF_PT_export_user_extensions.bl_id = 'GLTF_PT_export_user_extensions'
class HVYMGLTF_PT_export_user_extensions(bpy.types.Panel):
    bl_id = 'HVYMGLTF_PT_export_user_extensions'
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Heavymeta Extensions"
    bl_parent_id = "FILE_PT_operator"
    #bl_parent_id = "GLTF_PT_export_user_extensions"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        HVYMGLTF_PT_export_user_extensions.bl_parent_id = "hvym_ext_parent"
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = context.scene.hvym_collections_data
        self.layout.prop(props, 'enabled', text="")

    def draw(self, context):
        self.layout.label(text="test")
        pass

def dump(obj, text):
    print('-'*40, text, '-'*40)
    for attr in dir(obj):
        if hasattr( obj, attr ):
            print( "obj.%s = %s" % (attr, getattr(obj, attr)))

class TestOp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.test_op"
    bl_label = "Execute a custom action"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if hasattr(context, 'button_pointer'):
            btn = context.button_pointer 
            dump(btn, 'button_pointer')

        if hasattr(context, 'button_prop'):
            prop = context.button_prop
            dump(prop, 'button_prop')

        if hasattr(context, 'button_operator'):
            op = context.button_operator
            dump(op, 'button_operator')     

        return {'FINISHED'}


# -------------------------------------------------------------------
#   Panel Right Click operators
# ------------------------------------------------------------------- 
def btn_menu_func(self, context):
    layout = self.layout
    # layout.separator()
    # layout.operator(TestOp.bl_idname)
    layout.separator()
    layout.operator(HVYM_AddMorph.bl_idname)

def outliner_menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(HVYM_AddModel.bl_idname)
    layout.separator()
    layout.operator(HVYM_AddMaterial.bl_idname)

def nla_menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(HVYM_AddAnim.bl_idname)

def has_hvym_data(trait_type, type_str):
        result = False
        for data in bpy.context.collection.hvym_meta_data:
            if trait_type == data.trait_type and type_str == data.type:
                result = True
                break

        return result

# This class has to be exactly named like that to insert an entry in the right click menu
class WM_MT_button_context(Menu):
    bl_label = "Add Viddyoze Tag"

    def draw(self, context):
        pass

class HVYM_AddMorph(bpy.types.Operator):
    """Add this morph to the Heavymeta Data list."""
    bl_idname = "hvym_add.morph"
    bl_label = "[HVYM]:Add Morph Data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if hasattr(context, 'button_pointer'):
            btn = context.button_pointer
            print(btn.active_shape_key.name)
            if has_hvym_data('morph', btn.active_shape_key.name) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'morph'
                item.type = btn.active_shape_key.name
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}


class HVYM_AddModel(bpy.types.Operator):
    """Add a model to the Heavymeta Data list."""
    bl_idname = "hvym_add.model"
    bl_label = "[HVYM]:Add Model Data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Object'

    def execute(self, context):
        if bpy.context.selected_objects[0] != None:
            obj = bpy.context.selected_objects[0]
            print('add model to data')
            if has_hvym_data('model', obj.name) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'model'
                item.type = obj.name
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}

class HVYM_AddAnim(bpy.types.Operator):
    """Add a NLA animation to the Heavymeta Data list."""
    bl_idname = "hvym_add.anim"
    bl_label = "[HVYM]:Add Animation Data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        ob = context.object
        ad = ob.animation_data
        active_track = None

        if ad:
            for i, track in enumerate(ad.nla_tracks):
                if track.active:
                    active_track = track
                    break

        if active_track != None and has_hvym_data('anim', active_track.name) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'anim'
                item.type = active_track.name
        else:
            print("Item already exists in data.")


class HVYM_AddMaterial(bpy.types.Operator):
    """Add a material to the Heavymeta Data list."""
    bl_idname = "hvym_add.material"
    bl_label = "[HVYM]:Add Material Data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Material'

    def execute(self, context):
        matName  = context.selected_ids[0].name
        if matName != None:
            if has_hvym_data('material', matName) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'material'
                item.type = matName
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}



# -------------------------------------------------------------------
#   Class Registration
# -------------------------------------------------------------------
blender_classes = [
    HVYM_ListItem,
    HVYM_UL_DataList,
    HVYM_LIST_NewPropItem,
    HVYM_LIST_NewMeshItem,
    HVYM_LIST_NewMorphItem,
    HVYM_LIST_NewAnimItem,
    HVYM_LIST_NewMatItem,
    HVYM_LIST_DeleteItem,
    HVYM_LIST_MoveItem,
    HVYM_LIST_DirectionUp,
    HVYM_LIST_DirectionDown,
    HVYM_LIST_DefaultValues,
    HVYM_DebugMinter,
    HVYM_DebugModel,
    HVYM_DataReload,
    HVYM_DataOrder,
    HVYM_DeployMinter,
    HVYM_DataPanel,
    HVYM_NFTDataExtensionProps,
    HVYMGLTF_PT_export_user_extensions,
    TestOp,
    WM_MT_button_context,
    HVYM_AddMorph,
    HVYM_AddModel,
    HVYM_AddAnim,
    HVYM_AddMaterial
    ]


def register():
    BlenderNode.create_object = patched_create_object

    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    
    bpy.types.Scene.hvym_collections_data = bpy.props.PointerProperty(type=HVYM_NFTDataExtensionProps)
    bpy.types.Collection.hvym_meta_data = bpy.props.CollectionProperty(type = HVYM_ListItem)
    bpy.types.Collection.hvym_list_index = bpy.props.IntProperty(name = "Index for hvym_meta_data", default = 0)
    bpy.types.Collection.hvym_nft_type_enum = bpy.props.StringProperty(name = "Used to set nft type enum on import", default='HVYC')
    bpy.types.Collection.hvym_minter_type_enum = bpy.props.StringProperty(name = "Used to set minter type enum on import", default='payable')
    bpy.types.WM_MT_button_context.append(btn_menu_func)
    bpy.types.OUTLINER_MT_asset.append(outliner_menu_func)
    bpy.types.NLA_MT_channel_context_menu.append(nla_menu_func)

    if not hasattr(bpy.types.Collection, 'hvym_id'):
        bpy.types.Collection.hvym_id = bpy.props.StringProperty(default = '')

    if not hasattr(bpy.types.Object, 'hvym_id'):
        bpy.types.Object.hvym_id = bpy.props.StringProperty(default = '')


def unregister():
    del bpy.types.Scene.hvym_collections_data
    del bpy.types.Collection.hvym_meta_data
    del bpy.types.Collection.hvym_list_index
    del bpy.Types.Collection.hvym_nft_type_enum
    del bpy.Types.Collection.hvym_minter_type_enum
    bpy.types.WM_MT_button_context.remove(btn_menu_func)
    bpy.types.OUTLINER_MT_asset.remove(outliner_menu_func)
    bpy.types.NLA_MT_channel_context_menu.remove(nla_menu_func)

    if hasattr(bpy.types.Collection, 'hvym_id'):
        del bpy.types.Collection.hvym_id

    if hasattr(bpy.types.Object, 'hvym_id'):
        del bpy.types.Object.hvym_id

    for (prop_name, _) in PROPS:
        delattr(bpy.types.Collection, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

if __name__ == "__main__":
    register()

# IMPORT
def create_collections(gltf):
    if gltf.data.extensions is None or glTF_extension_name not in gltf.data.extensions:
        return

    ext_data = gltf.data.extensions[glTF_extension_name]
    ctx = bpy.context
    intProps = None
    meshProps = None
    morphNodes = None
    animProps = None
    collections = {}

    def set_col_data(type, prop):
        item = collection.hvym_meta_data.add()
        item.trait_type = type
        item.type = prop
        updateNftData(bpy.context)

    for id in ext_data.keys():
        name = ext_data[id]['collection_name']
        collection = bpy.data.collections.new(name)
        collection.hvym_id = id
        collections[id] = collection
        collection.nft_price = ext_data[id]['nftPrice']
        collection.hvym_nft_type_enum = ext_data[id]['nftType']
        collection.hvym_minter_type_enum = ext_data[id]['minterType']
        collection.minter_name = ext_data[id]['minterName']
        collection.minter_description = ext_data[id]['minterDesc']
        collection.minter_image = ext_data[id]['minterImage']
        collection.minter_version = ext_data[id]['minterVersion']

        if collection.minter_version > 0:
            collection.add_version = True

        if 'intProps' in ext_data[id].keys():
            intProps = ext_data[id]['intProps']
            for t in intProps:
                set_col_data('property', t)
            
        if 'meshProps' in ext_data[id].keys():
            meshProps = ext_data[id]['meshProps']
            for t in meshProps:
                set_col_data('mesh', t)

        if 'morphProps' in ext_data[id].keys():
            morphProps = ext_data[id]['morphProps']
            for t in morphProps:
                set_col_data('morph', t)

        if 'animProps' in ext_data[id].keys():
            animProps = ext_data[id]['animProps']
            for t in animProps:
                set_col_data('anim', t)

        
        bpy.context.scene.collection.children.link(collection)

        updateNftData(bpy.context)
            

    return collections
        

def assign_collections_hvym_data(obj, gltf):
    if gltf.data.extensions is None or glTF_extension_name not in gltf.data.extensions:
        return

    data = gltf.data.extensions[glTF_extension_name]
    ext_data = gltf.data.extensions[glTF_extension_name]
    collection_dict = {}
    linked = bpy.context.scene.hvym_collections_data.colData

    for col in bpy.data.collections:
        if col.hvym_id != None:
            id = col.hvym_id
            mapping = ext_data[id]['nodes']

        if obj.name not in linked and obj.name in mapping:
            col.objects.link(obj)
            linked[obj.name] = obj


def cleanup_scene_collection():
    linked = bpy.context.scene.hvym_collections_data.colData
    for ob in bpy.context.scene.collection.objects:
        if ob.name in linked.keys():
            bpy.context.scene.collection.objects.unlink(ob)

#EXPORT
# Use glTF-Blender-IO User extension hook mechanism
class glTF2ExportHVYMExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    # Gather export data
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if len(bpy.data.collections) == 0:
            return

        # Compile data objects in sets by collection
        # mappings = []
        # for col in bpy.data.collections:
        #     print(col.name)
        #     mappings.append(col.name)

        # if bpy.types.Scene.hvym_collections_data.enabled:
        #     if gltf2_object.extensions is None:
        #         gltf2_object.extensions = {}
        #     gltf2_object.extensions[glTF_extension_name] = self.Extension(
        #         name = glTF_extension_name,
        #         extension = mappings,
        #         required = False
        #     )

    def gather_gltf_extensions_hook(self, gltf2_object, export_settings):

        ctx = bpy.context.scene

        if ctx.hvym_collections_data.enabled:
            data = {}

            for id in ctx.hvym_collections_data.nftData.keys():
                data[id] = ctx.hvym_collections_data.nftData[id].to_dict()

                for col in bpy.data.collections:
                    if id == col.hvym_id:
                        nodes = []
                        for obj in col.objects:
                            nodes.append(obj.name)

                        data[id]['collection_name'] = col.name
                        data[id]['nodes'] = nodes
                            
    

            gltf2_object.extensions[glTF_extension_name] = data