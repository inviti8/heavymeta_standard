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

from configparser import InterpolationDepthError
from contextvars import Context
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
                       Collection)

from bpy.types import (Operator,
                       Panel,
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
orig_create_mesh_object = BlenderNode.create_mesh_object
def patched_create_mesh_object(gltf, vnode):
    obj = orig_create_mesh_object(gltf, vnode)
    if vnode.mesh_node_idx == 0:
        create_collections(gltf, vnode)
    assign_collections_hvym_data(obj, gltf, vnode)
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

    print("THIS IS GETTING CALLED!!!!!!")
    hvym_meta_data = context.collection.hvym_meta_data
    setCollectionId(context.collection)
    intProps = []
    meshProps = []
    morphProps = []
    animProps = []

    for i in range(len(hvym_meta_data)):
        if hvym_meta_data[i].trait_type == 'property':
            intProps.append(hvym_meta_data[i].type)
        elif hvym_meta_data[i].trait_type == 'mesh':
            meshProps.append(hvym_meta_data[i].type)
        elif hvym_meta_data[i].trait_type == 'morph':
            morphProps.append(hvym_meta_data[i].type)
        elif hvym_meta_data[i].trait_type == 'anim':
            animProps.append(hvym_meta_data[i].type)
        

    context.scene.hvym_collections_data.nftData[context.collection.hvym_id] = {'nftType': context.collection.nft_type,
                                                                                'minterType': context.collection.minter_type,
                                                                                'minterName': context.collection.minter_name,
                                                                                'minterImage': context.collection.minter_image,
                                                                                'minterVersion': context.collection.minter_version,
                                                                                'intProps': intProps,
                                                                                'meshProps': meshProps,
                                                                                'morphProps': morphProps,
                                                                                'animProps': animProps
                                                                                }
    
    print(context.scene.hvym_collections_data.nftData[context.collection.hvym_id].to_dict())


def onUpdate(self, context):
    updateNftData(context)
    

PROPS = [
    ('nft_type', bpy.props.EnumProperty(
        name='NFT-Type',
        items=(
            ('HVYC', "Character", ""),
            ('HVYI', "Immortal", ""),
            ('HVYA', "Animal", ""),
            ('HVYW', "Weapon", ""),
            ('HVYO', "Object", ""),
            ('HVYG', "Generic", ""),
            ('HVYAU', "Auricle", "")),
            update=onUpdate)),
    ('minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=(
            ('payable', "Publicly Mintable", ""),
            ('onlyOnwner', "Privately Mintable", "")),
            update=onUpdate)),
    ('minter_name', bpy.props.StringProperty(name='Minter-Name', default='', update=onUpdate)),
    ('minter_description', bpy.props.StringProperty(name='Minter-Description', default='', update=onUpdate)),
    ('minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='', update=onUpdate)),
    ('add_version', bpy.props.BoolProperty(name='Minter-Version', default=False)),
    ('minter_version', bpy.props.IntProperty(name='Version', default=-1, update=onUpdate)),
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
        if item.trait_type == 'anim':
            custom_icon = 'ACTION_TWEAK'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.note)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.note)

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
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMeshItem(bpy.types.Operator):
    """Add a new mesh item to the list."""

    bl_idname = "hvym_meta_data.new_mesh_item"
    bl_label = "Add a new mesh item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mesh'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMorphItem(bpy.types.Operator):
    """Add a new morph item to the list."""

    bl_idname = "hvym_meta_data.new_morph_item"
    bl_label = "Add a new morph item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'morph'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewAnimItem(bpy.types.Operator):
    """Add a new animation item to the list."""

    bl_idname = "hvym_meta_data.new_anim_item"
    bl_label = "Add a new animation item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'anim'
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


class HVYM_DebugMinter(bpy.types.Operator):
    bl_idname = "hvym_debug.minter"
    bl_label = "Launch Minter Debug UI"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Debug Minter")
        for data in context.collection.hvym_meta_data:
            print(data.type)
        return {'FINISHED'}


class HVYM_DebugModel(bpy.types.Operator):
    bl_idname = "hvym_debug.model"
    bl_label = "Launch Model Debug UI"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Debug Model")
        return {'FINISHED'}


class HVYM_DeployMinter(bpy.types.Operator):
    bl_idname = "hvym_deploy.minter"
    bl_label = "Launch Deploy Minter UI"
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
        row.template_list("HVYM_UL_DataList", "The_List", ctx,
                          "hvym_meta_data", ctx, "hvym_list_index")

        row = box.row()
        row.operator('hvym_meta_data.new_property_item', text='+', icon='FUND')
        row.operator('hvym_meta_data.new_mesh_item', text='+', icon='MESH_ICOSPHERE')
        row.operator('hvym_meta_data.new_morph_item', text='+', icon='SHAPEKEY_DATA')
        row.operator('hvym_meta_data.new_anim_item', text='+', icon='ACTION_TWEAK')
        row.operator('hvym_meta_data.delete_item', text='', icon='CANCEL')
        row.operator('hvym_meta_data.set_direction_up', text='', icon='SORT_DESC')
        row.operator('hvym_meta_data.set_direction_down', text='', icon='SORT_ASC')

        if ctx.hvym_list_index >= 0 and ctx.hvym_meta_data:
            item = ctx.hvym_meta_data[ctx.hvym_list_index]

            row = box.row()
            row.prop(item, "type")
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
    HVYM_LIST_DeleteItem,
    HVYM_LIST_MoveItem,
    HVYM_LIST_DirectionUp,
    HVYM_LIST_DirectionDown,
    HVYM_DebugMinter,
    HVYM_DebugModel,
    HVYM_DeployMinter,
    HVYM_DataPanel,
    HVYM_NFTDataExtensionProps,
    HVYMGLTF_PT_export_user_extensions
    ]


def register():
    BlenderNode.create_mesh_object = patched_create_mesh_object

    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    bpy.types.Scene.hvym_collections_data = bpy.props.PointerProperty(type=HVYM_NFTDataExtensionProps)
    bpy.types.Collection.hvym_meta_data = bpy.props.CollectionProperty(type = HVYM_ListItem)
    bpy.types.Collection.hvym_list_index = bpy.props.IntProperty(name = "Index for hvym_meta_data", default = 0)

    if not hasattr(bpy.types.Collection, 'hvym_id'):
        bpy.types.Collection.hvym_id = bpy.props.StringProperty(default = '')
    



def unregister():
    del bpy.types.Scene.hvym_collections_data
    del bpy.types.Collection.hvym_meta_data
    del bpy.types.Collection.hvym_list_index

    if hasattr(bpy.types.Collection, 'hvym_id'):
        del bpy.types.Collection.hvym_id

    for (prop_name, _) in PROPS:
        delattr(bpy.types.Collection, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

if __name__ == "__main__":
    register()

# IMPORT
def create_collections(gltf, vnode):
    if gltf.data.extensions is None or glTF_extension_name not in gltf.data.extensions:
        return
    #Collections array just created once
    if vnode.mesh_node_idx > 0:
        return

    ext_data = gltf.data.extensions[glTF_extension_name]
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
            

    return collections
        

def assign_collections_hvym_data(obj, gltf, vnode):
    print("This works!!")
    print("sssss")
    print(vnode.mesh_node_idx)
    if gltf.data.extensions is None or glTF_extension_name not in gltf.data.extensions:
        return

    data = gltf.data.extensions[glTF_extension_name]
    pynode = gltf.data.nodes[vnode.mesh_node_idx]
    pymesh = gltf.data.meshes[pynode.mesh]
    ext_data = gltf.data.extensions[glTF_extension_name]
    collection_dict = {}
    linked = bpy.context.scene.hvym_collections_data.colData
    unlinked = []


    for col in bpy.data.collections:
        if col.hvym_id != None:
            id = col.hvym_id
            mapping = ext_data[id]['nodes']

        if obj.name not in linked and obj.name in mapping:
            col.objects.link(obj)
            linked[obj.name] = obj
        
        






            

    # for col in bpy.data.collections:
    #     if col.hvym_id != None:
    #         id = col.hvym_id
    #         print(id)
    #         hvym_id = ext_data[id]
    #         mapping = ext_data[id]['nodes']
 
    #         for ob_name in mapping:
    #             #print('obj.name = '+obj.name)
    #             #print('ob_name'+ob_name)
    #             if obj.name in mapping:
    #                 print('Should add object to collection.')
    #                 if obj.name not in linked:
    #                     col.objects.link(obj)
    #                     linked.append(obj.name)

    #                 # for o in bpy.context.scene.collection.objects:
    #                 #     if o.name == ob_name:
    #                 #         print(o.name)
    #                 #         bpy.context.scene.collection.objects.unlink(o)

    #         for o in bpy.context.scene.collection.objects:
    #             if o.name in mapping and o.name not in linked and o.name not in unlinked:
    #                 print('should remove from scene collection.')
    #                 bpy.context.scene.collection.objects.unlink(o)
    #                 unlinked.append(o.name)
    

    # collection = bpy.data.collections.new("MyTestCollection")
    # collection.objects.link(obj)
    # bpy.context.scene.collection.children.link(collection)

    # for node in gltf.data.nodes:
    #     print(node.name)

    # vnodes = [gltf.vnodes[i] for i in range(0, len(gltf.vnodes)-1)]
    # for i, n in enumerate(vnodes):
    #     node = gltf.data.nodes[i]
    #     print("import descending...", i, node, n.blender_object)

    # for id in data.keys():
    #     col_data = data[id]


#EXPORT
# Use glTF-Blender-IO User extension hook mechanism
class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    # Gather export data
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if len(bpy.data.collections) > 0:
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

                        if len(nodes) > 0:
                            data[id]['collection_name'] = col.name
                            data[id]['nodes'] = nodes
    

            gltf2_object.extensions[glTF_extension_name] = data