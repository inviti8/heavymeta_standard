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

class MetaTrait(bpy.types.PropertyGroup):
    trait_type = bpy.props.StringProperty()
    value = bpy.props.StringProperty()

# ------------------------------------------------------------------------
#    Heavymeta Operators
# ------------------------------------------------------------------------

class OpAddTrait(bpy.types.Operator):
    """Print object name in Console"""
    bl_idname = "collection.add_trait_operator"
    bl_label = "Add Trait Operator"

    def execute(self, context):
        print (context.collection)
        return {'FINISHED'}


class OpRemoveTrait(bpy.types.Operator):
    """Print object name in Console"""
    bl_idname = "collection.remove_trait_operator"
    bl_label = "Remove Trait Operator"

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

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    bpy.utils.register_class(OpAddTrait)
    bpy.utils.register_class(OpRemoveTrait)
    bpy.utils.register_class(COLLECTION_PT_collection_custom_props)
    bpy.utils.register_class(HeavymetaStandardDataPanel)


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Collection, prop_name)

    bpy.utils.unregister_class(OpAddTrait)
    bpy.utils.unregister_class(OpRemoveTrait)
    bpy.utils.unregister_class(COLLECTION_PT_collection_custom_props)
    bpy.utils.unregister_class(HeavymetaStandardDataPanel)


if __name__ == "__main__":
    register()