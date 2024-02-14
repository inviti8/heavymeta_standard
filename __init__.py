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
import math
import os
from os import path
from typing import Dict
from bpy.app.handlers import persistent
from rna_prop_ui import PropertyPanel
from bpy.types import (Panel,
                       PointerProperty,
                       BoolProperty,
                       StringProperty,
                       FloatProperty,
                       EnumProperty,
                       CollectionProperty,
                       Collection,
                       Operator,
                       Header,
                       Menu,
                       PropertyGroup,
                       UIList,
                       Gizmo,
                       GizmoGroup,)
from bpy.props import (FloatVectorProperty)
from bpy_extras.io_utils import ExportHelper

preview_collections = {}

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
#   Widget Elements
# ------------------------------------------------------------------- 
# Coordinates (each one is a triangle).
custom_shape_verts = (
(8.1198, 1.4937, 6.2683),
(6.1198, -1.4792, 6.2683),
(8.1198, -1.4792, 6.2683),
(7.3821, -1.4792, 4.8495),
(6.1198, -1.4792, 6.2683),
(5.3821, -1.4792, 4.8495),
(5.3821, -1.4792, 4.8495),
(6.1198, 1.4937, 6.2683),
(5.3821, 1.4937, 4.8495),
(4.2032, 1.4937, -1.0000),
(2.8227, -1.4792, -1.0000),
(2.8227, 1.4937, -1.0000),
(8.1198, 1.4937, 6.2683),
(7.3821, -1.4792, 4.8495),
(7.3821, 1.4937, 4.8495),
(6.1198, 1.4937, 6.2683),
(7.3821, 1.4937, 4.8495),
(5.3821, 1.4937, 4.8495),
(5.3821, 1.4937, 4.8495),
(6.8035, 1.4937, 3.7998),
(4.8035, 1.4937, 3.7998),
(7.3821, 1.4937, 4.8495),
(6.8035, -1.4792, 3.7998),
(6.8035, 1.4937, 3.7998),
(2.8975, -1.4823, 4.8288),
(4.8035, -1.4792, 3.7998),
(5.3821, -1.4792, 4.8495),
(6.8035, -1.4792, 3.7998),
(5.3821, -1.4792, 4.8495),
(4.8035, -1.4792, 3.7998),
(6.1852, -1.4792, 2.7344),
(4.8035, -1.4792, 3.7998),
(3.8207, -1.4792, 2.0111),
(4.8035, -1.4792, 3.7998),
(3.8207, 1.4937, 2.0111),
(3.8207, -1.4792, 2.0111),
(6.8035, 1.4937, 3.7998),
(6.1852, -1.4792, 2.7344),
(6.1852, 1.4937, 2.7344),
(4.8035, 1.4937, 3.7998),
(6.1852, 1.4937, 2.7344),
(3.8207, 1.4937, 2.0111),
(3.1367, 1.4937, 0.8203),
(4.2032, 1.4937, -1.0000),
(2.8227, 1.4937, -1.0000),
(4.8490, 1.4937, 0.2253),
(4.2032, -1.4792, -1.0000),
(4.2032, 1.4937, -1.0000),
(1.5256, 1.4905, 2.9190),
(3.1367, -1.4792, 0.8203),
(3.1367, 1.4937, 0.8203),
(4.2032, -1.4792, -1.0000),
(3.1367, -1.4792, 0.8203),
(2.8227, -1.4792, -1.0000),
(1.6357, 1.4905, 6.2476),
(2.2461, -1.4823, 6.2476),
(2.2461, 1.4905, 6.2476),
(1.5079, -1.4823, 4.8288),
(1.6357, -1.4823, 6.2476),
(0.8975, -1.4823, 4.8288),
(0.8975, -1.4823, 4.8288),
(1.6357, 1.4905, 6.2476),
(0.8975, 1.4905, 4.8288),
(-1.2244, 1.4905, -0.1691),
(-1.6392, -1.4823, 0.1978),
(-1.6355, 1.4905, 0.2047),
(3.6357, 1.4905, 6.2476),
(2.8975, -1.4823, 4.8288),
(2.8975, 1.4905, 4.8288),
(2.2461, 1.4905, 6.2476),
(2.8975, 1.4905, 4.8288),
(1.5079, 1.4905, 4.8288),
(1.5079, 1.4905, 4.8288),
(2.3188, 1.4905, 3.7791),
(0.9292, 1.4905, 3.7791),
(2.8975, 1.4905, 4.8288),
(5.3821, -1.4792, 4.8495),
(5.3821, 1.4937, 4.8495),
(0.8975, -1.4823, 4.8288),
(0.3188, 1.4905, 3.7791),
(0.3188, -1.4823, 3.7791),
(0.9292, -1.4823, 3.7791),
(0.8975, -1.4823, 4.8288),
(0.3188, -1.4823, 3.7791),
(0.4147, -1.4823, 2.8418),
(0.3188, -1.4823, 3.7791),
(-0.1957, -1.4823, 2.8418),
(0.3188, -1.4823, 3.7791),
(-0.1957, 1.4905, 2.8418),
(-0.1957, -1.4823, 2.8418),
(3.4209, 1.4937, 1.2814),
(4.8490, 1.4937, 0.2253),
(3.1367, 1.4937, 0.8203),
(0.4147, 1.4905, 2.8418),
(0.9292, 1.4905, 3.7791),
(1.5256, 1.4905, 2.9190),
(5.4209, 1.4937, 1.2814),
(7.4764, 1.4937, 0.7244),
(6.7691, 1.4937, -1.0095),
(0.3645, 1.4905, 0.2047),
(-0.2810, -1.4823, -1.0207),
(-0.2810, 1.4905, -1.0207),
(6.1852, -1.4792, 2.7344),
(7.4764, 1.4937, 0.7244),
(6.1852, 1.4937, 2.7344),
(7.4764, 1.4937, 0.7244),
(6.7691, -1.4792, -1.0095),
(6.7691, 1.4937, -1.0095),
(2.8975, 1.4905, 4.8288),
(4.8035, 1.4937, 3.7998),
(2.3188, 1.4905, 3.7791),
(2.3188, 1.4905, 3.7791),
(4.8035, -1.4792, 3.7998),
(2.3188, -1.4823, 3.7791),
(-0.1001, 1.4905, 1.9394),
(0.3645, 1.4905, 0.2047),
(-1.0251, 1.4905, 0.2047),
(0.9203, 1.4905, 1.3842),
(0.3645, -1.4823, 0.2047),
(0.3645, 1.4905, 0.2047),
(-0.6633, -1.4823, 1.9919),
(-1.6355, 1.4905, 0.2047),
(-1.6355, -1.4823, 0.2047),
(-1.0251, -1.4823, 0.2047),
(-0.6633, -1.4823, 1.9919),
(-1.6355, -1.4823, 0.2047),
(0.4147, 1.4905, 2.8418),
(0.9203, 1.4905, 1.3842),
(-0.1001, 1.4905, 1.9394),
(0.9203, 1.4905, 1.3842),
(3.1367, 1.4937, 0.8203),
(2.8227, 1.4937, -1.0000),
(-0.6633, -1.4823, 1.9919),
(-0.1957, 1.4905, 2.8418),
(-0.6633, 1.4905, 1.9919),
(-0.1001, -1.4823, 1.9394),
(-0.1957, -1.4823, 2.8418),
(-0.6633, -1.4823, 1.9919),
(0.9203, 1.4905, 1.3842),
(2.8227, -1.4792, -1.0000),
(0.9203, -1.4823, 1.3842),
(0.9203, -1.4823, 1.3842),
(3.1367, -1.4792, 0.8203),
(1.5256, -1.4823, 2.9190),
(0.9203, -1.4823, 1.3842),
(0.4147, -1.4823, 2.8418),
(-0.1001, -1.4823, 1.9394),
(-0.1957, 1.4905, 2.8418),
(-0.1001, 1.4905, 1.9394),
(-0.6633, 1.4905, 1.9919),
(0.3645, -1.4823, 0.2047),
(-0.1001, -1.4823, 1.9394),
(-1.0251, -1.4823, 0.2047),
(-0.6633, 1.4905, 1.9919),
(-1.0251, 1.4905, 0.2047),
(-1.6355, 1.4905, 0.2047),
(-0.2810, 1.4905, -1.0207),
(-1.2268, -1.4823, -0.1736),
(-1.2244, 1.4905, -0.1691),
(0.3188, 1.4905, 3.7791),
(0.4147, 1.4905, 2.8418),
(-0.1957, 1.4905, 2.8418),
(1.5256, -1.4823, 2.9190),
(0.9292, -1.4823, 3.7791),
(0.4147, -1.4823, 2.8418),
(2.3188, -1.4823, 3.7791),
(1.5079, -1.4823, 4.8288),
(0.9292, -1.4823, 3.7791),
(0.8975, 1.4905, 4.8288),
(0.9292, 1.4905, 3.7791),
(0.3188, 1.4905, 3.7791),
(1.6357, 1.4905, 6.2476),
(1.5079, 1.4905, 4.8288),
(0.8975, 1.4905, 4.8288),
(5.4209, -1.4792, 1.2814),
(6.7691, 1.4937, -1.0095),
(6.7691, -1.4792, -1.0095),
(2.8975, -1.4823, 4.8288),
(2.2461, -1.4823, 6.2476),
(1.5079, -1.4823, 4.8288),
(2.2461, 1.4905, 6.2476),
(3.6357, -1.4823, 6.2476),
(3.6357, 1.4905, 6.2476),
(5.4209, 1.4937, 1.2814),
(4.8490, -1.4792, 0.2253),
(4.8490, 1.4937, 0.2253),
(0.9292, -1.4823, 3.7791),
(2.3188, 1.4905, 3.7791),
(2.3188, -1.4823, 3.7791),
(1.5256, -1.4823, 2.9190),
(0.9292, 1.4905, 3.7791),
(0.9292, -1.4823, 3.7791),
(3.4209, -1.4792, 1.2814),
(3.1367, 1.4937, 0.8203),
(3.1367, -1.4792, 0.8203),
(4.8490, -1.4792, 0.2253),
(3.4209, -1.4792, 1.2814),
(3.1367, -1.4792, 0.8203),
(3.8207, 1.4937, 2.0111),
(5.4209, 1.4937, 1.2814),
(3.4209, 1.4937, 1.2814),
(5.4209, -1.4792, 1.2814),
(7.4764, -1.4792, 0.7244),
(6.1852, -1.4792, 2.7344),
(3.8207, -1.4792, 2.0111),
(3.4209, 1.4937, 1.2814),
(3.4209, -1.4792, 1.2814),
(5.4209, -1.4792, 1.2814),
(3.8207, -1.4792, 2.0111),
(3.4209, -1.4792, 1.2814),
(-0.2810, -1.4823, -1.0207),
(-1.0251, -1.4823, 0.2047),
(-1.2268, -1.4823, -0.1736),
(-1.2268, -1.4823, -0.1736),
(-1.6355, -1.4823, 0.2047),
(-1.6392, -1.4823, 0.1978),
(-0.2810, 1.4905, -1.0207),
(-1.0251, 1.4905, 0.2047),
(0.3645, 1.4905, 0.2047),
(-1.2244, 1.4905, -0.1691),
(-1.6355, 1.4905, 0.2047),
(-1.0251, 1.4905, 0.2047),
(8.1198, 1.4937, 6.2683),
(6.1198, 1.4937, 6.2683),
(6.1198, -1.4792, 6.2683),
(7.3821, -1.4792, 4.8495),
(8.1198, -1.4792, 6.2683),
(6.1198, -1.4792, 6.2683),
(5.3821, -1.4792, 4.8495),
(6.1198, -1.4792, 6.2683),
(6.1198, 1.4937, 6.2683),
(4.2032, 1.4937, -1.0000),
(4.2032, -1.4792, -1.0000),
(2.8227, -1.4792, -1.0000),
(8.1198, 1.4937, 6.2683),
(8.1198, -1.4792, 6.2683),
(7.3821, -1.4792, 4.8495),
(6.1198, 1.4937, 6.2683),
(8.1198, 1.4937, 6.2683),
(7.3821, 1.4937, 4.8495),
(5.3821, 1.4937, 4.8495),
(7.3821, 1.4937, 4.8495),
(6.8035, 1.4937, 3.7998),
(7.3821, 1.4937, 4.8495),
(7.3821, -1.4792, 4.8495),
(6.8035, -1.4792, 3.7998),
(2.8975, -1.4823, 4.8288),
(2.3188, -1.4823, 3.7791),
(4.8035, -1.4792, 3.7998),
(6.8035, -1.4792, 3.7998),
(7.3821, -1.4792, 4.8495),
(5.3821, -1.4792, 4.8495),
(6.1852, -1.4792, 2.7344),
(6.8035, -1.4792, 3.7998),
(4.8035, -1.4792, 3.7998),
(4.8035, -1.4792, 3.7998),
(4.8035, 1.4937, 3.7998),
(3.8207, 1.4937, 2.0111),
(6.8035, 1.4937, 3.7998),
(6.8035, -1.4792, 3.7998),
(6.1852, -1.4792, 2.7344),
(4.8035, 1.4937, 3.7998),
(6.8035, 1.4937, 3.7998),
(6.1852, 1.4937, 2.7344),
(3.1367, 1.4937, 0.8203),
(4.8490, 1.4937, 0.2253),
(4.2032, 1.4937, -1.0000),
(4.8490, 1.4937, 0.2253),
(4.8490, -1.4792, 0.2253),
(4.2032, -1.4792, -1.0000),
(1.5256, 1.4905, 2.9190),
(1.5256, -1.4823, 2.9190),
(3.1367, -1.4792, 0.8203),
(4.2032, -1.4792, -1.0000),
(4.8490, -1.4792, 0.2253),
(3.1367, -1.4792, 0.8203),
(1.6357, 1.4905, 6.2476),
(1.6357, -1.4823, 6.2476),
(2.2461, -1.4823, 6.2476),
(1.5079, -1.4823, 4.8288),
(2.2461, -1.4823, 6.2476),
(1.6357, -1.4823, 6.2476),
(0.8975, -1.4823, 4.8288),
(1.6357, -1.4823, 6.2476),
(1.6357, 1.4905, 6.2476),
(-1.2244, 1.4905, -0.1691),
(-1.2268, -1.4823, -0.1736),
(-1.6392, -1.4823, 0.1978),
(3.6357, 1.4905, 6.2476),
(3.6357, -1.4823, 6.2476),
(2.8975, -1.4823, 4.8288),
(2.2461, 1.4905, 6.2476),
(3.6357, 1.4905, 6.2476),
(2.8975, 1.4905, 4.8288),
(1.5079, 1.4905, 4.8288),
(2.8975, 1.4905, 4.8288),
(2.3188, 1.4905, 3.7791),
(2.8975, 1.4905, 4.8288),
(2.8975, -1.4823, 4.8288),
(5.3821, -1.4792, 4.8495),
(0.8975, -1.4823, 4.8288),
(0.8975, 1.4905, 4.8288),
(0.3188, 1.4905, 3.7791),
(0.9292, -1.4823, 3.7791),
(1.5079, -1.4823, 4.8288),
(0.8975, -1.4823, 4.8288),
(0.4147, -1.4823, 2.8418),
(0.9292, -1.4823, 3.7791),
(0.3188, -1.4823, 3.7791),
(0.3188, -1.4823, 3.7791),
(0.3188, 1.4905, 3.7791),
(-0.1957, 1.4905, 2.8418),
(3.4209, 1.4937, 1.2814),
(5.4209, 1.4937, 1.2814),
(4.8490, 1.4937, 0.2253),
(5.4209, 1.4937, 1.2814),
(6.1852, 1.4937, 2.7344),
(7.4764, 1.4937, 0.7244),
(0.3645, 1.4905, 0.2047),
(0.3645, -1.4823, 0.2047),
(-0.2810, -1.4823, -1.0207),
(6.1852, -1.4792, 2.7344),
(7.4764, -1.4792, 0.7244),
(7.4764, 1.4937, 0.7244),
(7.4764, 1.4937, 0.7244),
(7.4764, -1.4792, 0.7244),
(6.7691, -1.4792, -1.0095),
(2.8975, 1.4905, 4.8288),
(5.3821, 1.4937, 4.8495),
(4.8035, 1.4937, 3.7998),
(2.3188, 1.4905, 3.7791),
(4.8035, 1.4937, 3.7998),
(4.8035, -1.4792, 3.7998),
(-0.1001, 1.4905, 1.9394),
(0.9203, 1.4905, 1.3842),
(0.3645, 1.4905, 0.2047),
(0.9203, 1.4905, 1.3842),
(0.9203, -1.4823, 1.3842),
(0.3645, -1.4823, 0.2047),
(-0.6633, -1.4823, 1.9919),
(-0.6633, 1.4905, 1.9919),
(-1.6355, 1.4905, 0.2047),
(-1.0251, -1.4823, 0.2047),
(-0.1001, -1.4823, 1.9394),
(-0.6633, -1.4823, 1.9919),
(0.4147, 1.4905, 2.8418),
(1.5256, 1.4905, 2.9190),
(0.9203, 1.4905, 1.3842),
(0.9203, 1.4905, 1.3842),
(1.5256, 1.4905, 2.9190),
(3.1367, 1.4937, 0.8203),
(-0.6633, -1.4823, 1.9919),
(-0.1957, -1.4823, 2.8418),
(-0.1957, 1.4905, 2.8418),
(-0.1001, -1.4823, 1.9394),
(0.4147, -1.4823, 2.8418),
(-0.1957, -1.4823, 2.8418),
(0.9203, 1.4905, 1.3842),
(2.8227, 1.4937, -1.0000),
(2.8227, -1.4792, -1.0000),
(0.9203, -1.4823, 1.3842),
(2.8227, -1.4792, -1.0000),
(3.1367, -1.4792, 0.8203),
(0.9203, -1.4823, 1.3842),
(1.5256, -1.4823, 2.9190),
(0.4147, -1.4823, 2.8418),
(-0.1957, 1.4905, 2.8418),
(0.4147, 1.4905, 2.8418),
(-0.1001, 1.4905, 1.9394),
(0.3645, -1.4823, 0.2047),
(0.9203, -1.4823, 1.3842),
(-0.1001, -1.4823, 1.9394),
(-0.6633, 1.4905, 1.9919),
(-0.1001, 1.4905, 1.9394),
(-1.0251, 1.4905, 0.2047),
(-0.2810, 1.4905, -1.0207),
(-0.2810, -1.4823, -1.0207),
(-1.2268, -1.4823, -0.1736),
(0.3188, 1.4905, 3.7791),
(0.9292, 1.4905, 3.7791),
(0.4147, 1.4905, 2.8418),
(2.3188, -1.4823, 3.7791),
(2.8975, -1.4823, 4.8288),
(1.5079, -1.4823, 4.8288),
(0.8975, 1.4905, 4.8288),
(1.5079, 1.4905, 4.8288),
(0.9292, 1.4905, 3.7791),
(1.6357, 1.4905, 6.2476),
(2.2461, 1.4905, 6.2476),
(1.5079, 1.4905, 4.8288),
(5.4209, -1.4792, 1.2814),
(5.4209, 1.4937, 1.2814),
(6.7691, 1.4937, -1.0095),
(2.8975, -1.4823, 4.8288),
(3.6357, -1.4823, 6.2476),
(2.2461, -1.4823, 6.2476),
(2.2461, 1.4905, 6.2476),
(2.2461, -1.4823, 6.2476),
(3.6357, -1.4823, 6.2476),
(5.4209, 1.4937, 1.2814),
(5.4209, -1.4792, 1.2814),
(4.8490, -1.4792, 0.2253),
(0.9292, -1.4823, 3.7791),
(0.9292, 1.4905, 3.7791),
(2.3188, 1.4905, 3.7791),
(1.5256, -1.4823, 2.9190),
(1.5256, 1.4905, 2.9190),
(0.9292, 1.4905, 3.7791),
(3.4209, -1.4792, 1.2814),
(3.4209, 1.4937, 1.2814),
(3.1367, 1.4937, 0.8203),
(4.8490, -1.4792, 0.2253),
(5.4209, -1.4792, 1.2814),
(3.4209, -1.4792, 1.2814),
(3.8207, 1.4937, 2.0111),
(6.1852, 1.4937, 2.7344),
(5.4209, 1.4937, 1.2814),
(5.4209, -1.4792, 1.2814),
(6.7691, -1.4792, -1.0095),
(7.4764, -1.4792, 0.7244),
(3.8207, -1.4792, 2.0111),
(3.8207, 1.4937, 2.0111),
(3.4209, 1.4937, 1.2814),
(5.4209, -1.4792, 1.2814),
(6.1852, -1.4792, 2.7344),
(3.8207, -1.4792, 2.0111),
(-0.2810, -1.4823, -1.0207),
(0.3645, -1.4823, 0.2047),
(-1.0251, -1.4823, 0.2047),
(-1.2268, -1.4823, -0.1736),
(-1.0251, -1.4823, 0.2047),
(-1.6355, -1.4823, 0.2047),
(-0.2810, 1.4905, -1.0207),
(-1.2244, 1.4905, -0.1691),
(-1.0251, 1.4905, 0.2047),
)


class HVYM_MenuTransform(Gizmo):
    bl_idname = "VIEW3D_GT_hvym_menu_transform_widget"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    __slots__ = (
        "custom_shape",
        "init_value",
    )

    def _update_offset_matrix(self):
        # set mesh position
        self.matrix_offset.col[3][2] = 0

    def draw(self, context):
        if self.use_draw_modal:
            self._update_offset_matrix()
            self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        if self.use_draw_modal:
            self._update_offset_matrix()
            self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', custom_shape_verts)

    def invoke(self, context, event):
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)


    def modal(self, context, event, tweak):
        return {'RUNNING_MODAL'}


class HVYM_MenuTransformGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_hvym_menu_transform_grp"
    bl_label = "HVYM Menu Transform Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'EMPTY')

    def handle_custom_mesh_flag(self, context):
        ob = context.object
        if ob.hvym_menu_index == -1:
            self._gizmo.use_draw_modal = False
        else:
            self._gizmo.use_draw_modal = True

    def setup(self, context):
        # Assign the 'offset' target property to the light energy.
        ob = context.object
        gz = self.gizmos.new(HVYM_MenuTransform.bl_idname)

        gz.color = 0.617, 0.017, 0.082
        gz.alpha = 0.7

        gz.color_highlight = 0.325, 0.501, 0.379
        gz.alpha_highlight = 0.5

        # units are large, so shrink to something more reasonable.
        gz.scale_basis = 0.1
        gz.use_draw_modal = False
        
        self._gizmo = gz
        self.handle_custom_mesh_flag(context)

    def refresh(self, context):
        ob = context.object
        gz = self._gizmo
        gz.matrix_basis = ob.matrix_world.normalized()



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

def linear_to_srgb8(c):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
        
    if srgb > 1: srgb = 1

    return round(255*srgb)


def Hex(r, g, b):
    return "#"+"%02x%02x%02x" % (
        linear_to_srgb8(r),
        linear_to_srgb8(g),
        linear_to_srgb8(b),
    )

def color_to_hex(color):
    return Hex(color[0], color[1], color[2])


def setCollectionId(collection):
    if collection.hvym_id == '':
        collection.hvym_id = random_id()

def lockObj(obj):
    obj.hide_select = True
    for i in range(3):
        obj.lock_location[i] = True
        obj.lock_rotation[i] = True
        obj.lock_scale[i] = True


def RebuildMaterialSets(context):
    hvym_meta_data = context.collection.hvym_meta_data
    
    verts = [( 0.001,  0.001,  0.0), 
         ( 0.001, -0.001,  0.0),
         (-0.001, -0.001,  0.0),
         ]
         
    edges = []
    faces = []

    for i in range(len(hvym_meta_data)):
        if hvym_meta_data[i].trait_type == 'mat_set':
            name = hvym_meta_data[i].type+'_'+context.collection.hvym_id
            col_name = 'HVYM_OBJ_DATA'
            obj = bpy.context.scene.objects.get(name)
            mesh = bpy.data.meshes.new('MESH_'+name)  # add the new mesh
                
            obj = bpy.context.scene.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj)
                    
            data_col = bpy.data.collections.get(col_name)
            if data_col is None:
                data_col = bpy.data.collections.new(col_name)
                data_col.hide_select = True 
                data_col.color_tag = 'COLOR_01'      
                bpy.context.scene.collection.children.link(data_col)
                    
            obj = bpy.data.objects.new(name, mesh)
            lockObj(obj)
            data_col.objects.link(obj)
                    
            for m in hvym_meta_data[i].mat_set:
                bpy.data.materials.new(name=m.mat_ref.name)
                obj.data.materials.append(m.mat_ref)
                faces.append([0,1,2])
                    
            mesh.from_pydata(verts, edges, faces)

            i=0
            for mat in obj.data.materials:
                obj.data.polygons[i].material_index = i
                i+=1


def updateNftData(context):
    #Update all the props on any change
    #put them into a single structure
    if context.collection.name == 'Scene Collection':
        return
        
    hvym_meta_data = context.collection.hvym_meta_data
    setCollectionId(context.collection)
    #valProps = []
    valProps = {}
    #meshProps = []
    meshProps = {}
    meshSets = {}
    morphProps = []
    animProps = []
    #materials = []
    materials = {}
    materialSets = {}
    nodes = []
    menu_data = {'name': None, 'primary_color': None, 'secondary_color': None, 'text_color': None}

    for i in range(len(hvym_meta_data)):
        #data={}
        #data[hvym_meta_data[i].type] = hvym_meta_data[i].values
        int_props = {
            'default': hvym_meta_data[i].int_default, 
            'min': hvym_meta_data[i].int_min, 
            'max': hvym_meta_data[i].int_max,
            'prop_slider_type': hvym_meta_data[i].prop_slider_type,
            'prop_action_type': hvym_meta_data[i].prop_action_type
            }

        if hvym_meta_data[i].prop_value_type == 'Float':
            int_props = {
                'default': hvym_meta_data[i].float_default, 
                'min': hvym_meta_data[i].float_min, 
                'max': hvym_meta_data[i].float_max,
                'prop_slider_type': hvym_meta_data[i].prop_slider_type,
                'prop_action_type': hvym_meta_data[i].prop_action_type
                }

        if hvym_meta_data[i].trait_type == 'property':
            #data[hvym_meta_data[i].type] = int_props
            #valProps.append(data)
            valProps[hvym_meta_data[i].type] = int_props

        elif hvym_meta_data[i].trait_type == 'mesh':
            if hvym_meta_data[i].model_ref != None:
                mesh_data = {
                            'name': hvym_meta_data[i].model_ref.name,
                            'type': hvym_meta_data[i].type, 
                            'visible': hvym_meta_data[i].visible
                            }
                #data[hvym_meta_data[i].type] = mesh_data
                #meshProps.append(data)
                meshProps[hvym_meta_data[i].type] = mesh_data

        elif hvym_meta_data[i].trait_type == 'mesh_set':
            mesh_data = []
            for m in hvym_meta_data[i].mesh_set:
                if m.model_ref != None:
                    mesh_data.append(m.model_ref)
            #data[hvym_meta_data[i].type] = mesh_data
            meshSets[hvym_meta_data[i].type] = mesh_data

        elif hvym_meta_data[i].trait_type == 'morph_set':
            morph_obj = {}
            morph_sets = []

            if hvym_meta_data[i].model_ref != None:
                for m in hvym_meta_data[i].morph_set:
                    morph_data = {}
                    morph_data['name'] = m.name
                    morph_data['default'] = m.float_default
                    morph_data['min'] = m.float_min
                    morph_data['max'] = m.float_max
                    morph_sets.append(morph_data)
                morph_obj['model_ref'] = hvym_meta_data[i].model_ref
                morph_obj['set'] = morph_sets
                data[hvym_meta_data[i].type] = morph_obj
                morphProps.append(data)

        elif hvym_meta_data[i].trait_type == 'anim':
            data[hvym_meta_data[i].type] = hvym_meta_data[i].anim_loop
            animProps.append(data)

        elif hvym_meta_data[i].trait_type == 'material':
            if hvym_meta_data[i].mat_ref != None:
                mat_data = {
                            'name': hvym_meta_data[i].mat_ref.name,
                            'type': hvym_meta_data[i].mat_type
                            }
                #data[hvym_meta_data[i].type] = mat_data
                #materials.append(data)
                materials[hvym_meta_data[i].type] = mat_data

        elif hvym_meta_data[i].trait_type == 'mat_set':
            mat_obj = {}
            mat_sets = []
            mesh_set = []
            for m in hvym_meta_data[i].mat_set:
                if m.mat_ref != None:
                    mat_data = {}
                    mat_data['name'] = m.name
                    mat_data['mat_ref'] = m.mat_ref
                    mat_data['material_id'] = m.material_id
                    mat_sets.append(mat_data)

            for m in hvym_meta_data[i].mesh_set:
                if m.model_ref != None:
                    mesh_set.append(m.model_ref)

            mat_obj['mesh_set'] = mesh_set
            mat_obj['set'] = mat_sets
            #data[hvym_meta_data[i].type] = mat_obj
            materialSets[hvym_meta_data[i].type] = mat_obj

    for obj in context.collection.objects:
        nodes.append(obj.name)
        obj.hvym_id = context.collection.hvym_id

    for i in range(len(context.scene.hvym_menu_meta_data)):
        data = context.scene.hvym_menu_meta_data[i]
        col_id = data['collection_id']
        if col_id == context.collection.hvym_id:
            menu_data['name'] = data.menu_name
            menu_data['primary_color'] = color_to_hex(data.menu_primary_color)
            menu_data['secondary_color'] = color_to_hex(data.menu_secondary_color)
            menu_data['text_color'] = color_to_hex(data.menu_text_color)
        

    context.scene.hvym_collections_data.nftData['contract'] =                   {'nftType': context.scene.hvym_nft_type,
                                                                                'nftPrice': round(context.scene.hvym_nft_price, 4),
                                                                                'premNftPrice': round(context.scene.hvym_prem_nft_price, 4),
                                                                                'maxSupply': context.scene.hvym_max_supply,
                                                                                'minterType': context.scene.hvym_minter_type,
                                                                                'minterName': context.scene.hvym_minter_name,
                                                                                'minterDesc': context.scene.hvym_minter_description,
                                                                                'minterImage': context.scene.hvym_minter_image,
                                                                                'minterVersion': context.scene.hvym_minter_version,
                                                                                'contractABI': context.scene.hvym_contract_abi,
                                                                                'contractAddress': context.scene.hvym_contract_address
                                                                                }

    context.scene.hvym_collections_data.nftData[context.collection.hvym_id] = {'collectionType': context.collection.hvym_collection_type,
                                                                                'valProps': valProps,
                                                                                'meshProps': meshProps,
                                                                                'meshSets': meshSets,
                                                                                'morphProps': morphProps,
                                                                                'animProps': animProps,
                                                                                'materials': materials,
                                                                                'materialSets': materialSets,
                                                                                "collection_name": context.collection.name,
                                                                                "menu_data": menu_data,
                                                                                "nodes": nodes
                                                                                }
    


def onUpdate(self, context):
    updateNftData(context)

    #this flag is used when props are updated by the user
    #This is so values can be pulled in from built in props
    if hasattr(self, 'no_update') and self.no_update:
        self.no_update = False #reset the flag
    else:
        #handle meshes and mesh set model ref visiblity
        if hasattr(self, 'model_ref') and hasattr(self, 'visible'):
            if self.model_ref != None:
                self.model_ref.hide_set(not self.visible)

        #handle meshes morph settings
        if hasattr(self, 'model_ref') and hasattr(self, 'float_default') and hasattr(self, 'float_min') and hasattr(self, 'float_max'):
            if self.model_ref != None:
                index = self.model_ref.data.shape_keys.key_blocks.find(self.name)
                morph = self.model_ref.data.shape_keys.key_blocks[index]
                if morph != None:
                    morph.slider_min = self.float_min
                    morph.slider_max = self.float_max
                    morph.value = self.float_default


    for col in bpy.data.collections:
        if len(col.objects) > 0:
            for obj in col.objects:
                if obj.hvym_menu_index < 0:
                    context.collection.hvym_menu_index = -1


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


def collectionTypes(self, context):
    #get the default enum, used to set enum on import
    first_enum = context.collection.hvym_col_type_enum 

    tup = (
            ('multi', "Multi-Meshes-Visible", ""),
            ('single', "Single-Mesh-Visible", ""))

    result = setEnum(tup, first_enum, 'multi')

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
    ('hvym_nft_type', bpy.props.EnumProperty(
        name='NFT-Type',
        items=nftTypes,
        description ="Heavymeta NFT type, see docs for more detail.",
        update=onUpdate)),
    ('hvym_nft_price', bpy.props.FloatProperty(name='NFT-Price', default=0.01, description ="Price of NFT in eth.", update=onUpdate)),
    ('hvym_prem_nft_price', bpy.props.FloatProperty(name='Premium-NFT-Price', default=0.01, description ="Premium price of customized NFT in eth.", update=onUpdate)),
    ('hvym_max_supply', bpy.props.IntProperty(name='Max-Supply', default=-1, description ="Max number that can be minted, if -1 supply is infinite.", update=onUpdate)),
    ('hvym_minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=minterTypes,
        description ="Minted by creator only, or public.",
        update=onUpdate)),
    ('hvym_minter_name', bpy.props.StringProperty(name='Minter-Name', default='', description ="Name of minter.", update=onUpdate)),
    ('hvym_minter_description', bpy.props.StringProperty(name='Minter-Description', default='', description ="Details about the NFT.", update=onUpdate)),
    ('hvym_minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='', description ="Custom header image for the minter ui.", update=onUpdate)),
    ('hvym_add_version', bpy.props.BoolProperty(name='Minter-Version', description ="Enable versioning for this NFT minter.", default=False)),
    ('hvym_minter_version', bpy.props.IntProperty(name='Version', default=-1, description ="Version of the NFT minter.", update=onUpdate)),
    ('hvym_contract_abi', bpy.props.StringProperty(name='ABI', default='', description ="ABI for compiled contract.", update=onUpdate)),
    ('hvym_contract_address', bpy.props.StringProperty(name='Address', default='', description ="The address for the contract.", update=onUpdate)),
    ('hvym_pinata_jwt', bpy.props.StringProperty(name='Pinata-JWT', default='', description ="JWT key for uploads.", update=onUpdate)),
    ('hvym_pinata_gateway', bpy.props.StringProperty(name='Pinata-Gateway', default='', description ="Pinata Gatway url.", update=onUpdate))
]

COL_PROPS = [
    ('hvym_collection_type', bpy.props.EnumProperty(
        name='Type',
        items=collectionTypes,
        description ="Heavymeta Collection type, see docs for more detail.",
        update=onUpdate))
]


class HVYM_MenuDataItem(bpy.types.PropertyGroup):
    """Group of properties representing per collection menu meta data."""

    collection_id: bpy.props.StringProperty(
           name="Collection ID",
           description="Id of the collection this property group is linked to.",
           default="",
           update=onUpdate)

    menu_name: bpy.props.StringProperty(
           name="Name",
           description="Set name of the menu for collection.",
           default="",
           update=onUpdate)

    menu_primary_color: bpy.props.FloatVectorProperty(
           name="Primary Color",
           description="Set primary color.",
           subtype = "COLOR",
           default = (0.038,0.479,0.342,1.0),
           min=0, 
           max=100,
           size = 4,
           update=onUpdate)

    menu_secondary_color: bpy.props.FloatVectorProperty(
           name="Secondary Color",
           description="Set secondary color.",
           subtype = "COLOR",
           default = (0.325,0.501,0.379,1.0),
           min=0, 
           max=100,
           size = 4,
           update=onUpdate)

    menu_text_color: bpy.props.FloatVectorProperty(
           name="Text Color",
           description="Set text color.",
           subtype = "COLOR",
           default = (0.617,0.0082,0.159,1.0),
           min=0, 
           max=100,
           size = 4,
           update=onUpdate)

    menu_index: bpy.props.IntProperty(
           name="Menu Index",
           default=-1,
           update=onUpdate)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)


class HVYM_MeshSet(bpy.types.PropertyGroup):
    """Group of properties representing a set of meshes."""

    name: bpy.props.StringProperty(
           name="Name",
           description="Name of the mesh set.",
           default="",
           update=onUpdate)

    model_ref: bpy.props.PointerProperty(
        name="Model Reference",
        type=bpy.types.Object)

    visible: bpy.props.BoolProperty(
           name="Visible",
           description="Object visiblility.",
           default=True,
           update=onUpdate)

    enabled: bpy.props.BoolProperty(
           name="Enabled",
           description="Object Interactive.",
           default=True,
           update=onUpdate)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)


class HVYM_UL_MeshSetList(bpy.types.UIList):
    """Heavymeta mesh set list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.enabled = item.enabled
            layout.prop(item, "model_ref")
            layout.prop(item, "visible")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.enabled = item.enabled
            layout.prop(item, "model_ref")
            layout.prop(item, "visible")


class HVYM_MaterialSet(bpy.types.PropertyGroup):
    """Group of properties representing a set of materials."""

    name: bpy.props.StringProperty(
           name="Name",
           description="Name of the material set.",
           default="",
           update=onUpdate)

    material_id: bpy.props.IntProperty(
           name="ID",
           description="ID for material.",
           default=0,
           update=onUpdate)

    mat_ref: bpy.props.PointerProperty(
        name="Material Reference",
        type=bpy.types.Material)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)
    

class HVYM_UL_MaterialSetList(bpy.types.UIList):
    """Heavymeta material set list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "mat_ref")
            layout.prop(item, "material_id")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "mat_ref")
            layout.prop(item, "material_id")


class HVYM_MorphSet(bpy.types.PropertyGroup):
    """Group of properties representing a set of morphs."""

    name: bpy.props.StringProperty(
           name="Name",
           description="Name of the morph set.",
           default="",
           update=onUpdate)

    float_default: bpy.props.FloatProperty(
           name="Default",
           description="Add default value.",
           default=0,
           update=onUpdate)

    float_min: bpy.props.FloatProperty(
           name="Min",
           description="Add minimum value.",
           default=0,
           update=onUpdate)

    float_max: bpy.props.FloatProperty(
           name="Max",
           description="Add maximum value.",
           default=1,
           update=onUpdate)

    model_ref: bpy.props.PointerProperty(
        name="Morph Reference",
        type=bpy.types.Object)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)
    

class HVYM_UL_MorphSetList(bpy.types.UIList):
    """Heavymeta morph set list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
    
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = 'SHAPEKEY_DATA')
            layout.prop(item, "float_default")
            layout.prop(item, "float_min")
            layout.prop(item, "float_max")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon = 'SHAPEKEY_DATA')
            layout.prop(item, "float_default")
            layout.prop(item, "float_min")
            layout.prop(item, "float_max")


class HVYM_DataItem(bpy.types.PropertyGroup):
    """Group of properties representing various meta data."""

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

    prop_value_type: bpy.props.EnumProperty(
            name='Value Type',
            description ="Set value type of property.",
            items=(('Int', 'Integer', ""),
                ('Float', 'Float', ""),),
            update=onUpdate)

    prop_slider_type: bpy.props.EnumProperty(
            name='Widget Type',
            description ="Set ui widget for property.",
            items=(('TextBox', 'Text Box', ""),
                ('Slider', 'Slider', ""),
                ('Meter', 'Meter', ""),),
            update=onUpdate)

    prop_action_type: bpy.props.EnumProperty(
            name='Action Type',
            description ="Set property action type.",
            items=(('Immutable', 'Immutable', ""),
                ('Incremental', 'Incremental', ""),
                ('Mintable', 'Mintable', ""),),
            update=onUpdate)

    values: bpy.props.StringProperty(
           name="Values",
           description="Add '(default, min, max)'",
           default="",
           update=onUpdate)

    list_expanded: bpy.props.BoolProperty(
           name="List Collapsed",
           description="Bool for collapsing a list.",
           default=False,
           update=onUpdate)

    int_default: bpy.props.IntProperty(
           name="Default",
           description="Add default value.",
           default=0,
           update=onUpdate)

    int_min: bpy.props.IntProperty(
           name="Min",
           description="Add minimum value.",
           default=0,
           update=onUpdate)

    int_max: bpy.props.IntProperty(
           name="Max",
           description="Add maximum value.",
           default=1,
           update=onUpdate)

    float_default: bpy.props.FloatProperty(
           name="Default",
           description="Add default value.",
           default=0.0,
           update=onUpdate)

    float_min: bpy.props.FloatProperty(
           name="Min",
           description="Add minimum value.",
           default=0.0,
           update=onUpdate)

    float_max: bpy.props.FloatProperty(
           name="Max",
           description="Add maximum value.",
           default=1.0,
           update=onUpdate)

    visible: bpy.props.BoolProperty(
           name="Visible",
           description="Object visiblility.",
           default=True,
           update=onUpdate)

    anim_loop: bpy.props.EnumProperty(
            name='Loop',
            description ="Animation Looping.",
            items=(('NONE', 'None', ""),
                ('LoopOnce', 'Loop Once', ""),
                ('LoopRepeat', 'Loop Forever', ""),
                ('PingPongRepeat', 'Ping Pong', ""),),
            update=onUpdate)

    mat_type: bpy.props.EnumProperty(
            name='Material Type',
            description ="Animation Looping.",
            items=(('STANDARD', 'Standard', ""),
                ('PBR', 'PBR', ""),
                ('Toon', 'Toon', ""),),
            update=onUpdate)

    model_ref: bpy.props.PointerProperty(
        name="Model Reference",
        type=bpy.types.Object)

    mat_ref: bpy.props.PointerProperty(
        name="Material Reference",
        type=bpy.types.Material)

    morph_ref: bpy.props.PointerProperty(
        name="Morph Reference",
        type=bpy.types.Key)

    use_menu: bpy.props.BoolProperty(
           name="Use Menu",
           description="Enable to add data menu to exported model.",
           default=False,
           update=onUpdate)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)

    note: bpy.props.StringProperty(
           name="Note",
           description="Add a note, (not exported).",
           default="",
           update=onUpdate)

    test: bpy.props.StringProperty(
           name="Test",
           description="Add a test, (not exported).",
           default="",
           update=onUpdate)

    mesh_set: bpy.props.CollectionProperty(type = HVYM_MeshSet)

    mesh_set_index: bpy.props.IntProperty(
           name="Mesh Set Index",
           description="Index of selected item in the mesh set list.",
           default=-1,
           update=onUpdate)

    mat_set: bpy.props.CollectionProperty(type = HVYM_MaterialSet)

    mat_set_index: bpy.props.IntProperty(
           name="Mesh Set Index",
           description="Index of selected item in the material set list.",
           default=-1,
           update=onUpdate)

    morph_set: bpy.props.CollectionProperty(type = HVYM_MorphSet)

    morph_set_index: bpy.props.IntProperty(
           name="Morph Set Index",
           description="Index of selected item in the morph set list.",
           default=-1,
           update=onUpdate)


class HVYM_UL_DataList(bpy.types.UIList):
    """Heavymeta data list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'FUND'

        if item.trait_type == 'mesh':
            custom_icon = 'MESH_ICOSPHERE'
        if item.trait_type == 'mesh_set':
            custom_icon = 'FILE_3D'
        elif item.trait_type == 'morph_set':
            custom_icon = 'SHAPEKEY_DATA'
        elif item.trait_type == 'anim':
            custom_icon = 'ACTION_TWEAK'
        elif item.trait_type == 'material':
            custom_icon = 'SHADING_RENDERED'
        elif item.trait_type == 'mat_set':
            custom_icon = 'OVERLAY'
        elif item.trait_type == 'toggle':
            custom_icon = 'CHECKMARK'

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
class HVYM_MENU_NewMenuTransform(bpy.types.Operator):
    """Add a new Empty Transform, for menu properties associated with this collection."""

    bl_idname = "hvym_menu_meta_data.new_menu_transform"
    bl_label = "Add a new menu transform"

    def execute(self, context):
        setCollectionId(context.collection)
        menu_data = context.scene.hvym_menu_meta_data
        hvym_id = context.collection.hvym_id
        menu_id = 'menu_'+hvym_id
        index = 0
        active_obj = context.active_object
        transform = None

        if active_obj != None:
            if context.collection.name in [c.name for c in bpy.data.objects[active_obj.name].users_collection]:
                context.active_object.select_set(False)

        for obj in context.collection.all_objects:
            if obj.hvym_menu_index >= 0:
                transform = obj

        if transform == None:
            data_updated = False
            for data in menu_data:
                if data.collection_id == hvym_id:
                    menu_data.remove(index)
                    data_updated = True
                    break
                index+=1

            if data_updated:
                for col in bpy.data.collections:
                    if len(col.objects) > 0:
                        for obj in col.objects:
                            if obj.hvym_menu_index > index:
                                obj.hvym_menu_index -=1
                
            data = context.scene.hvym_menu_meta_data.add()
            data.menu_name = context.collection.name + ' Menu'
            data.collection_id = hvym_id
            data.menu_index = len(context.scene.hvym_menu_meta_data)-1

            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            context.active_object.name = menu_id
            context.active_object.hvym_menu_id = menu_id
            context.active_object.empty_display_size = 1
            context.active_object.hvym_menu_index = data.menu_index
            context.collection.hvym_menu_index = data.menu_index

        return{'FINISHED'}

class HVYM_LIST_NewPropItem(bpy.types.Operator):
    """Add a new numeric property item to the list."""

    bl_idname = "hvym_meta_data.new_property_item"
    bl_label = "Add a new property item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'property'
        item.type = '*'
        item.values = 'Value Property'
        item.int_default = 0
        item.int_min = 0
        item.int_max = 1
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMeshItem(bpy.types.Operator):
    """Add a new mesh item to the list."""

    bl_idname = "hvym_meta_data.new_mesh_item"
    bl_label = "Add a new mesh item"

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None and context.active_object.type == 'MESH' and active_object_in_col())

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mesh'
        item.type = '*'
        item.values = 'Object'
        item.model_ref = context.active_object
        item.visible = (not context.active_object.hide_get())
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMeshSet(bpy.types.Operator):
    """Add a new mesh set to the list."""

    bl_idname = "hvym_meta_data.new_mesh_set"
    bl_label = "Add a new mesh set item"

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None and context.active_object.type == 'MESH' and active_object_in_col())

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mesh_set'
        item.type = '*'
        item.values = 'Mesh Set'
        mesh_item = item.mesh_set.add()
        mesh_item.model_ref = context.active_object
        mesh_item.visible = (not context.active_object.hide_get())
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMeshSetItem(bpy.types.Operator):
    """Add a new mesh set to the set."""

    bl_idname = "hvym_meta_data.new_mesh_set_item"
    bl_label = "Add a new mesh set item"

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None and context.active_object.type == 'MESH' and active_object_in_col())

    def execute(self, context):
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]

        if item != None and item.trait_type != 'mesh_set':
            return

        mesh_item = item.mesh_set.add()
        mesh_item.type = '*'
        mesh_item.values = 'Mesh Set'
        mesh_item.model_ref = context.active_object

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_AddMeshSetItemToSet(bpy.types.Operator):
    """Add a new mesh set to the set."""

    bl_idname = "hvym_meta_data.add_mesh_set_item_to_set"
    bl_label = "Add a new mesh set item to a set"

    @classmethod
    def poll(cls, context):
        item = None
        if len(context.collection.hvym_meta_data)>0 and context.active_object.type == 'MESH' and active_object_in_col():
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]

        if item != None and item.trait_type == 'mesh_set' and len(item.mesh_set)>0:
            result = True
            for m in item.mesh_set:
                if m.model_ref == None:
                    result = False
                    break

            if active_object_in_meshset(item.mesh_set):
                result = False

            return result

    def execute(self, context):
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]

        if item == None or item.trait_type != 'mesh_set' or context.active_object.type != 'MESH':
            return{'FINISHED'}

        mesh_item = item.mesh_set.add()
        mesh_item.type = '*'
        mesh_item.values = 'Mesh Set'
        mesh_item.model_ref = context.active_object
        mesh_item.visible = (not context.active_object.hide_get())

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_DeleteMeshSetItem(bpy.types.Operator):
    """Delete a mesh from the set."""

    bl_idname = "hvym_meta_data.delete_mesh_set_item"
    bl_label = "Delete a mesh set item"

    @classmethod
    def poll(cls, context):
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        return item != None and len(item.mesh_set)>0

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'mesh_set':
            return

        index = item.mesh_set_index

        item.mesh_set.remove(index)
        item.mesh_set_index = min(max(0, index - 1), len(item.mesh_set) - 1)

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMorphSet(bpy.types.Operator):
    """Add a new morph set to the list."""

    bl_idname = "hvym_meta_data.new_morph_set"
    bl_label = "Add a new morph item"

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None and context.active_object.type == 'MESH' and active_object_in_col())

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'morph_set'
        item.type = '*'
        item.values = 'Morph Set'
        item.model_ref = context.active_object
        updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_DeleteMorphSetItem(bpy.types.Operator):
    """Delete a morph slot from the set. Morph is not deleted"""

    bl_idname = "hvym_meta_data.delete_morph_set_item"
    bl_label = "Delete a morph set item"

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'morph_set':
            return

        index = item.morph_set_index

        item.morph_set.remove(index)
        item.morph_set_index = min(max(0, index - 1), len(item.morph_set) - 1)

        updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_NewAnimItem(bpy.types.Operator):
    """Add a new animation item to the list."""

    bl_idname = "hvym_meta_data.new_anim_item"
    bl_label = "Add a new animation item"

    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.animation_data)

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'anim'
        item.type = '*'
        item.values = 'Animation'
        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMatItem(bpy.types.Operator):
    """Add a new material item to the list."""

    bl_idname = "hvym_meta_data.new_mat_item"
    bl_label = "Add a new material item"

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None and context.active_object.type == 'MESH' and active_object_in_col())

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'material'
        item.type = '*'
        item.values = 'Material'
        item.mat_ref = context.active_object.active_material

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMatSet(bpy.types.Operator):
    """Add a new material set to the list."""

    bl_idname = "hvym_meta_data.new_mat_set"
    bl_label = "Add a new material set item"

    @classmethod
    def poll(cls, context):
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item != None and item.trait_type == 'mesh_set' and len(item.mesh_set)>0:
            result = True
            for m in item.mesh_set:
                if m.model_ref == None:
                    result = False
                    break

            return result


    def execute(self, context):
        ref_set_item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if ref_set_item.trait_type != 'mesh_set':
            return

        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mat_set'
        item.type = '*'
        item.values = 'Material Set'
        for m in ref_set_item.mesh_set:
            mesh_set = item.mesh_set.add()
            mesh_set.name = m.name
            mesh_set.model_ref = m.model_ref
            mesh_set.enabled = False

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMatSetItem(bpy.types.Operator):
    """Add a new material to the set."""

    bl_idname = "hvym_meta_data.new_mat_set_item"
    bl_label = "Add a new material set item"

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'mat_set':
            return

        mat_item = item.mat_set.add()

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_NewMatSetMaterial(bpy.types.Operator):
    """Add a new material to the set."""

    bl_idname = "hvym_meta_data.new_mat_set_material"
    bl_label = "Add a new material set material"

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'mat_set':
            return

        mat_item = item.mat_set.add()
        mat = bpy.data.materials.new(name='Material'+str(len(bpy.data.materials)-1))  # Create a material.
        mat_item.mat_ref = mat

        updateNftData(context)

        return{'FINISHED'}

class HVYM_LIST_DeleteMatSetItem(bpy.types.Operator):
    """Delete a material slot from the set. Material is not deleted"""

    bl_idname = "hvym_meta_data.delete_mat_set_item"
    bl_label = "Delete a material set item"

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'mat_set':
            return

        index = item.mat_set_index

        item.mat_set.remove(index)
        item.mat_set_index = min(max(0, index - 1), len(item.mat_set) - 1)

        updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_DeleteMatSetMaterial(bpy.types.Operator):
    """Delete a material slot and material from the set."""

    bl_idname = "hvym_meta_data.delete_mat_set_material"
    bl_label = "Delete a material set item"

    def execute(self, context):
        item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item.trait_type != 'mat_set':
            return

        index = item.mat_set_index
        if item.mat_ref != None:
            mat_dict = {mat.name: i for i, mat in enumerate(bpy.data.materials)}
            mat_idx = mat_dict[item.mat_ref.name]
            bpy.context.object.active_material_index = mat_idx
            bpy.ops.object.material_slot_remove()

        item.mat_set.remove(index)
        item.mat_set_index = min(max(0, index - 1), len(item.mat_set) - 1)

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
        elif item.trait_type == 'mesh_set':
            item.values = '[...]'
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
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item != None:
            if item.trait_type == 'mesh' and item.model_ref != None:
                item.no_update = True
                item.model_ref.hide_set(item.visible)
            if item.trait_type == 'mesh_set' and len(item.mesh_set)>0:
                for m in item.mesh_set:
                    if m.model_ref != None:
                        m.no_update = True
                        m.visible = (not m.model_ref.hide_get())
            if item.trait_type == 'morph_set' and len(item.morph_set)>0:
                for m in item.morph_set:
                    if m.model_ref != None:
                        index = m.model_ref.data.shape_keys.key_blocks.find(m.name)
                        morph = m.model_ref.data.shape_keys.key_blocks[index]
                        if morph != None:
                            m.no_update = True
                            m.name = morph.name
                            m.no_update = True
                            m.float_min = morph.slider_min
                            m.no_update = True
                            m.float_max = morph.slider_max
                            m.no_update = True
                            m.float_default = morph.value

        return {'FINISHED'}

class HVYM_DataOrder(bpy.types.Operator):
    bl_idname = "hvym_data.order"
    bl_label = "Order Data"
    bl_description ="Reorder the data for this collection."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        hvym_meta_data = bpy.context.collection.hvym_meta_data
        valProps = []
        meshProps = []
        morphProps = []
        animProps = []
        materials = []

        for data in hvym_meta_data:
            obj = {'trait_type':data.trait_type, 'type':data.type, 'values':data.values}
            if obj['trait_type'] == 'property':
                valProps.append(obj)
            elif obj['trait_type'] == 'mesh':
                meshProps.append(obj)
            elif obj['trait_type'] == 'morph':
                morphProps.append(obj)
            elif obj['trait_type'] == 'anim':
                animProps.append(obj)
            elif obj['trait_type'] == 'material':
                materials.append(obj)

        allProps = [valProps, meshProps, morphProps, animProps, materials]

        for i in range(len(hvym_meta_data)):
            bpy.ops.hvym_meta_data.delete_item()
        
        for arr in allProps:
            for item in arr:
                new_item = bpy.context.collection.hvym_meta_data.add()
                for key in new_item.keys():
                    new_item[key] = item[key]
                # new_item.trait_type = item['trait_type']
                # new_item.type = item['type']
                # new_item.values = item['values']
                

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


class HVYM_ExportHelper(bpy.types.Operator, ExportHelper):
    bl_idname = "hvym_deploy.gltf"
    bl_label = "Export glTF"
    filename_ext = ".gltf"
    export_types = (('GLB', ".glb", "Exports a single file, with all data packed in binary form. Most efficient and portable, but more difficult to edit later"),
                   ('GLTF_SEPARATE', ".gltf + .bin + textures", "Separate (.gltf + .bin + textures) – Exports multiple files, with separate JSON, binary and texture data. Easiest to edit later."),
                   ('GLTF_EMBEDDED', ".gltf", "Exports a single file, with all data packed in JSON. Less efficient than binary, but easier to edit later."),
                   )

    export_copyright: bpy.props.StringProperty(name="Copyright", description="Legal rights and conditions for the model.")

    check_existing: bpy.props.BoolProperty(
            name="Check Existing",
            description="Check Existing, Check and warn on overwriting existing files",
            default=False)

    export_format: bpy.props.EnumProperty(
        name='Format',
        items=export_types,
        description ="Minted by creator only, or public.")

    use_selection: bpy.props.BoolProperty(
            name="Selected Objects",
            description="Export selected objects only.",
            default=False)

    use_visible: bpy.props.BoolProperty(
            name="Visible Objects",
            description="Export visible objects only.",
            default=False)

    use_renderable: bpy.props.BoolProperty(
            name="Renderable Objects",
            description="Export renderable objects only.",
            default=False)

    use_active_collection: bpy.props.BoolProperty(
            name="Active Collection",
            description="Export objects in the active collection only.",
            default=False)

    use_active_scene: bpy.props.BoolProperty(
            name="Active Scene",
            description="Export active scene only.",
            default=False)

    use_custom_props: bpy.props.BoolProperty(
            name="Custom Properties",
            description="Export custom properties.",
            default=False)

    export_cameras: bpy.props.BoolProperty(
            name="Cameras",
            description="Export cameras.",
            default=False)

    export_lights: bpy.props.BoolProperty(
            name="Punctual Lights",
            description="Export directional, point, and spot lights. Uses “KHR_lights_punctual” glTF extension.",
            default=False)

    export_yup : bpy.props.BoolProperty(
            name="+Y Up",
            description="Export using glTF convention, +Y up.",
            default=True)

    use_mesh_modifiers : bpy.props.BoolProperty(
            name="Apply Modifiers",
            description=" Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys.",
            default=False)

    export_texcoords : bpy.props.BoolProperty(
            name="UVs",
            description="Export UVs (texture coordinates) with meshes.",
            default=True)

    export_normals : bpy.props.BoolProperty(
            name="Normals",
            description="Export vertex normals with meshes.",
            default=True)

    export_tangents : bpy.props.BoolProperty(
            name="Tangents",
            description="Export vertex tangents with meshes.",
            default=False)

    export_colors : bpy.props.BoolProperty(
            name="Vertex Colors",
            description="Export vertex colors with meshes.",
            default=True)

    use_mesh_edges : bpy.props.BoolProperty(
            name="Loose Edges",
            description="Export loose edges as lines, using the material from the first material slot.",
            default=False)

    use_mesh_vertices : bpy.props.BoolProperty(
            name="Loose Points",
            description="Export loose points as glTF points, using the material from the first material slot.",
            default=False)

    export_frame_range : bpy.props.BoolProperty(
            name="Limit to Playback Range",
            description="Clips animations to selected playback range.",
            default=True)

    export_frame_step: bpy.props.IntProperty(
            name="Sampling Rate",
            min=1, max=120,
            default=1,
            )

    export_force_sampling : bpy.props.BoolProperty(
            name="Always Sample Animations",
            description="Apply sampling to all animations.",
            default=True)

    export_nla_strips : bpy.props.BoolProperty(
            name="Group by NLA Track",
            description=" When on, multiple actions become part of the same glTF animation if they’re pushed onto NLA tracks with the same name. When off, all the currently assigned actions become one glTF animation.",
            default=True)

    export_optimize_animation_size : bpy.props.BoolProperty(
            name="Optimize Animation Size",
            description=" Reduce exported file-size by removing duplicate keyframes(can cause problems with stepped animation).",
            default=False)

    export_def_bones : bpy.props.BoolProperty(
            name="Export Deformation Bones Only",
            description="Export Deformation bones only.",
            default=False)

    export_morph_normal : bpy.props.BoolProperty(
            name="Shape Key Normals",
            description="Export vertex normals with shape keys (morph targets).",
            default=True)

    export_morph_tangent : bpy.props.BoolProperty(
            name="Shape Key Tangents",
            description="Export vertex tangents with shape keys (morph targets).",
            default=False)

    export_all_influences : bpy.props.BoolProperty(
            name=" Include All Bone Influence",
            description="Allow >4 joint vertex influences. Models may appear incorrectly in many viewers.",
            default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_format")
        layout.prop(self, "export_types")
        layout.prop(self, "export_copyright")
        layout.prop(self, "check_existing")
        # Add an expandable UI list for visibility settings
        box0 = layout.box()
        box0.label(text="Visibility")
        row = box0.row()
        row.prop(self, "use_selection")
        row.prop(self, "use_visible")
        row = box0.row()
        row.prop(self, "use_renderable")
        row.prop(self, "use_active_collection")
        row = box0.row()
        row.prop(self, "use_active_scene")
        row.prop(self, "use_custom_props")
        row = box0.row()
        row.prop(self, "export_cameras")
        row.prop(self, "export_lights")

        box1 = layout.box()
        box1.label(text="Transform")
        row = box1.row()
        row.prop(self, "export_yup")

        box2 = layout.box()
        box2.label(text="Geometry")
        row = box2.row()
        row.prop(self, "use_mesh_modifiers")
        row.prop(self, "export_texcoords")
        row = box2.row()
        row.prop(self, "export_normals")
        row.prop(self, "export_tangents")
        row = box2.row()
        row.prop(self, "export_colors")
        row.prop(self, "use_mesh_edges")
        row = box2.row()
        row.prop(self, "use_mesh_vertices")

        box3 = layout.box()
        box3.label(text="Animation")
        row = box3.row()
        row.prop(self, "export_frame_range")
        row.prop(self, "export_frame_step")
        row = box3.row()
        row.prop(self, "export_force_sampling")
        row.prop(self, "export_nla_strips")
        row = box3.row()
        row.prop(self, "export_optimize_animation_size")
        row.prop(self, "export_def_bones")

        box4 = layout.box()
        box4.label(text="Shape Keys")
        row = box4.row()
        row.prop(self, "export_morph_normal")
        row.prop(self, "export_morph_tangent")

        box5 = layout.box()
        box5.label(text="Skinning")
        row = box5.row()
        row.prop(self, "export_all_influences")

    def execute(self, context):
        filepath = self.filepath
        bpy.context.scene.hvym_collections_data.enabled = True
        #bpy.ops.export_scene.gltf(filepath=filepath)
        bpy.ops.export_scene.gltf(filepath=filepath, check_existing=self.check_existing, export_format=self.export_format, export_copyright=self.export_copyright, export_texcoords=self.export_texcoords, export_normals=self.export_normals, export_tangents=self.export_tangents, export_colors=self.export_colors, use_mesh_edges=self.use_mesh_edges, use_mesh_vertices=self.use_mesh_vertices, export_cameras=self.export_cameras, use_selection=self.use_selection, use_visible=self.use_visible, use_renderable=self.use_renderable, use_active_collection=self.use_active_collection, use_active_scene=self.use_active_scene, export_yup=self.export_yup, export_frame_range=self.export_frame_range, export_frame_step=self.export_frame_step, export_force_sampling=self.export_force_sampling, export_nla_strips=self.export_nla_strips, export_def_bones=self.export_def_bones, export_all_influences=self.export_all_influences, export_morph_normal=self.export_morph_normal, export_morph_tangent=self.export_morph_tangent, export_lights=self.export_lights)
        print("Exported glTF to: ", filepath)
        return {'FINISHED'}


class HVYM_DeployMinter(bpy.types.Operator):
    bl_idname = "hvym_deploy.minter"
    bl_label = "Launch Deploy Minter UI"
    bl_description ="Deploy NFT minter."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Deploy Minter")
        bpy.ops.hvym_deploy.gltf('INVOKE_DEFAULT')
        return {'FINISHED'}


class HVYM_DeployConfirmMinterDeployDialog(bpy.types.Operator):
    """Really?"""
    bl_idname = "hvym_deploy.confirm_minter_deploy_dialog"
    bl_label = "Ready to deploy Minter?"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, "YES")
        bpy.ops.hvym_deploy.minter()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class HVYM_DeployNFT(bpy.types.Operator):
    bl_idname = "hvym_deploy.nft"
    bl_label = "Launch Deploy Minter UI"
    bl_description ="Deploy NFT minter."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Deploy Minter")
        bpy.ops.hvym_deploy.gltf('INVOKE_DEFAULT')
        return {'FINISHED'}


class HVYM_DeployConfirmNFTDeploytDialog(bpy.types.Operator):
    """Really?"""
    bl_idname = "hvym_deploy.confirm_nft_deploy_dialog"
    bl_label = "Ready to deploy NFT?"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, "YES")
        bpy.ops.hvym_deploy.nft()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class HVYM_Menu_Transform_Panel(bpy.types.Panel):
    """
    Panel for empty transform, used to define menu, and menu position for 
    a given collection. There should be only asingle menu tranform, per 
    collection, as the created menu uses HVYM collection data.
    """
    bl_label = "Heavymeta Standard Menu Properties"
    bl_idname = "COLLECTION_PT_heavymeta_standard_transform"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return (ob is not None and ob.type == 'EMPTY')

    def draw_header(self, context):
        col = self.layout.column()
        box = col.row()
        row = box.row()
        pcoll = preview_collections["main"]
        logo = pcoll["logo"]
        row.label(text="", icon_value=logo.icon_id)

    def draw(self, context):
        layout = self.layout
        hvym_id = context.collection.hvym_id
        obj = context.active_object
        ctx = context.collection
        scn = context.scene
        col = self.layout.column()
        box = col.row()
        row = box.row()
        if scn.hvym_menu_meta_data and obj.hvym_menu_index != None:
            item = scn.hvym_menu_meta_data[obj.hvym_menu_index]
            row.prop(item, "menu_name")
            box = col.row()
            row = box.row()
            row.prop(item, "menu_primary_color")
            box = col.row()
            row = box.row()
            row.prop(item, "menu_secondary_color")
            box = col.row()
            row = box.row()
            row.prop(item, "menu_text_color")
            box = col.row()
            row = box.row()
            row.label(text='Menu #: '+str(item.menu_index))

            

class HVYM_DataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Heavymeta Standard Data"
    bl_idname = "COLLECTION_PT_heavymeta_standard_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    @classmethod
    def poll(cls, context):
        return (context.collection.name != 'HVYM_OBJ_DATA')

    def draw_header(self, context):
        col = self.layout.column()
        box = col.row()
        row = box.row()
        pcoll = preview_collections["main"]
        logo = pcoll["logo"]
        row.label(text="", icon_value=logo.icon_id)

    def draw(self, context):

        col = self.layout.column()
        box = col.row()
        row = box.row()
        row.operator('hvym_data.reload', text='', icon='FILE_REFRESH')
        ctx = context.collection
        # for (prop_name, _) in COL_PROPS:
        #     row = col.row()
        #     if prop_name == 'minter_version':
        #         row = row.row()
        #         row.enabled = ctx.add_version
        #     row.prop(ctx, prop_name)
        row.separator()
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="NFT Data:")
        row = box.row()
        row.operator('hvym_data.order', text='', icon='LINENUMBERS_ON')
        row.template_list("HVYM_UL_DataList", "", ctx,
                          "hvym_meta_data", ctx, "hvym_list_index")

        row = box.row()
        row.operator('hvym_meta_data.new_property_item', text='+', icon='FUND')
        row.operator('hvym_meta_data.new_mesh_item', text='+', icon='MESH_ICOSPHERE')
        row.operator('hvym_meta_data.new_mesh_set', text='+', icon='FILE_3D')
        row.operator('hvym_meta_data.new_morph_set', text='+', icon='SHAPEKEY_DATA')
        row.operator('hvym_meta_data.new_anim_item', text='+', icon='ACTION_TWEAK')
        row.operator('hvym_meta_data.new_mat_item', text='+', icon='SHADING_RENDERED')
        row.operator('hvym_meta_data.new_mat_set', text='+', icon='OVERLAY')
        row.operator('hvym_meta_data.delete_item', text='', icon='CANCEL')
        row.operator('hvym_meta_data.set_direction_up', text='', icon='SORT_DESC')
        row.operator('hvym_meta_data.set_direction_down', text='', icon='SORT_ASC')
        row.operator('hvym_meta_data.default_values', text='', icon='CON_TRANSLIKE')

        if ctx.hvym_list_index >= 0 and ctx.hvym_meta_data:
            item = ctx.hvym_meta_data[ctx.hvym_list_index]
            row = box.row()
            row.prop(item, "type")
            row = box.row()
            if item.trait_type == 'property':
                row.prop(item, "prop_value_type")
                row.prop(item, "prop_slider_type")
                row.prop(item, "prop_action_type")
                row = box.row()
                if item.prop_value_type == 'Int':
                    row.prop(item, "int_default")
                    row.prop(item, "int_min")
                    row.prop(item, "int_max")
                elif item.prop_value_type == 'Float':
                    row.prop(item, "float_default")
                    row.prop(item, "float_min")
                    row.prop(item, "float_max")
            elif item.trait_type == 'morph_set':
                row.enabled = False
                row.prop(item, "model_ref")
                row = box.row()
                row.template_list("HVYM_UL_MorphSetList", "", item,
                          "morph_set", item, "morph_set_index")
                row = box.row()
                row.operator('hvym_meta_data.delete_morph_set_item', text='', icon='REMOVE')
            elif item.trait_type == 'mesh':
                row.prop(item, "model_ref")
                row.prop(item, "visible")
            elif item.trait_type == 'mesh_set':
                row.template_list("HVYM_UL_MeshSetList", "", item,
                          "mesh_set", item, "mesh_set_index")
                row = box.row()
                row.operator('hvym_meta_data.new_mesh_set_item', text='', icon='ADD')
                row.operator('hvym_meta_data.delete_mesh_set_item', text='', icon='REMOVE')
            elif item.trait_type == 'anim':
                row.prop(item, "anim_loop")
            elif item.trait_type == 'material':
                row.prop(item, "mat_ref")
                row.prop(item, "mat_type")
            elif item.trait_type == 'mat_set':
                row.template_list("HVYM_UL_MaterialSetList", "", item,
                          "mat_set", item, "mat_set_index")
                col = self.layout.column()
                row.template_list("HVYM_UL_MeshSetList", "", item,
                          "mesh_set", item, "mesh_set_index")
                row = box.row()
                row.operator('hvym_meta_data.new_mat_set_material', text='+', icon='MATERIAL')
                row.operator('hvym_meta_data.delete_mat_set_material', text='-', icon='CANCEL')
                row.operator('hvym_meta_data.new_mat_set_item', text='Slot', icon='ADD')
                row.operator('hvym_meta_data.delete_mat_set_item', text='Slot', icon='REMOVE')
            else:
                row.prop(item, "values")
            row = box.row()
            row.prop(item, "note")
        box = col.box()
        row = box.row()
        name = 'menu_'+ctx.hvym_id
        row.enabled = (bpy.data.objects.get(name) == None)
        row.operator('hvym_menu_meta_data.new_menu_transform', text='Add Menu Transform', icon='OBJECT_ORIGIN')



class HVYM_ScenePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Heavymeta Standard NFT Data"
    bl_idname = "SCENE_PT_heavymeta_standard_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw_header(self, context):
        col = self.layout.column()
        box = col.row()
        row = box.row()
        pcoll = preview_collections["main"]
        logo = pcoll["logo"]
        row.label(text="", icon_value=logo.icon_id)

    def draw(self, context):
        col = self.layout.column()
        box = col.row()
        row = box.row()
        row.operator('hvym_data.reload', text='', icon='FILE_REFRESH')
        for (prop_name, _) in PROPS:
            row = col.row()
            if prop_name == 'minter_version':
                row = row.row()
                row.enabled = context.scene.add_version
            if prop_name != 'hvym_pinata_jwt' and prop_name != 'hvym_pinata_gateway' and prop_name != 'hvym_contract_abi' and prop_name != 'hvym_contract_address':
                row.prop(context.scene, prop_name)
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
        row.label(text="Pinata:")
        for (prop_name, _) in PROPS:
            if prop_name == 'hvym_pinata_jwt' or prop_name == 'hvym_pinata_gateway':
                row = box.row()
                row.prop(context.scene, prop_name)
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="Deploy:")
        row = box.row()
        row.operator('hvym_deploy.confirm_minter_deploy_dialog', text="Deploy Minter", icon="URL")
        # row = box.row()
        # row.operator('hvym_deploy.confirm_nft_deploy_dialog', text="Deploy NFT", icon="URL")
        box = col.box()
        row = box.row()
        row.label(text="Contract Info:")
        for (prop_name, _) in PROPS:
            if prop_name == 'hvym_contract_abi' or prop_name == 'hvym_contract_address':
                row = box.row()
                row.prop(context.scene, prop_name)


# -------------------------------------------------------------------
#   Heavymeta Standards Panel
# ------------------------------------------------------------------- 
class HVYM_NFTDataExtensionProps(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="enabled", default=True)
    nftData: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)
    colData: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)
    menuData: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)


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
        pcoll = preview_collections["main"]
        logo = pcoll["logo"]
        self.layout.prop(props, 'enabled', text="", icon_value=logo.icon_id)

    def draw(self, context):
        pass

def dump_obj(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

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
class WM_OT_button_context_test(bpy.types.Operator):
    """Right click entry test"""
    bl_idname = "wm.button_context_test"
    bl_label = "Run Context Test"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        value = getattr(context, "button_pointer", None)
        if value is not None:
            dump(value, "button_pointer")

        value = getattr(context, "button_prop", None)
        if value is not None:
            dump(value, "button_prop")

        value = getattr(context, "button_operator", None)
        if value is not None:
            dump(value, "button_operator")

        return {'FINISHED'}

def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(WM_OT_button_context_test.bl_idname)

def panel_types():
    basetype = bpy.types.Panel
    for typename in dir(bpy.types):
        btype = getattr(bpy.types, typename)
        if issubclass(btype, basetype):
            yield btype

def panels_by_label(label):
    for ptype in panel_types():
        if getattr(ptype.bl_rna, "bl_label", None) == label:
            yield ptype

def btn_menu_func(self, context):
    layout = self.layout
    # layout.separator()
    # layout.operator(TestOp.bl_idname)
    layout.separator()
    pcoll = preview_collections["main"]
    logo = pcoll["logo"]
    layout.operator(HVYM_AddMorph.bl_idname, icon_value=logo.icon_id)
    layout.operator(HVYM_LIST_NewMatSet.bl_idname, icon_value=logo.icon_id)

def outliner_menu_func(self, context):
    layout = self.layout
    layout.separator()
    pcoll = preview_collections["main"]
    logo = pcoll["logo"]
    layout.operator(HVYM_AddModel.bl_idname, icon_value=logo.icon_id)
    layout.operator(HVYM_LIST_AddMeshSetItemToSet.bl_idname, icon_value=logo.icon_id)
    layout.separator()
    layout.operator(HVYM_AddMaterial.bl_idname, icon_value=logo.icon_id)
    layout.operator(HVYM_AddMaterialToSet.bl_idname, icon_value=logo.icon_id)

def nla_menu_func(self, context):
    layout = self.layout
    layout.separator()
    pcoll = preview_collections["main"]
    logo = pcoll["logo"]
    layout.operator(HVYM_AddAnim.bl_idname, icon_value=logo.icon_id)

def has_hvym_data(trait_type, type_str):
        result = False
        for data in bpy.context.collection.hvym_meta_data:
            if trait_type == data.trait_type and type_str == data.type:
                result = True
                break

        return result

def active_object_in_col():
    result = False
    for obj in bpy.context.collection.objects:
        if obj == bpy.context.active_object:
            result = True
            break

    return result

def active_object_in_meshset(mesh_set):
    result = False
    for m in mesh_set:
        if m.model_ref == bpy.context.active_object:
            result = True
            break

    return result

def active_material_in_matset(mat_set):
    result = False
    for m in mat_set:
        if m.mat_ref == bpy.context.active_object.active_material:
            result = True
            break

    return result

def material_in_matset(material, mat_set):
    result = False
    for m in mat_set:
        if m.mat_ref == material:
            result = True
            break

    return result

class HVYM_AddMorph(bpy.types.Operator):
    """Add this morph to the Heavymeta Data list."""
    bl_idname = "hvym_add.morph"
    bl_label = "Add Morph Data to Set"

    @classmethod
    def poll(cls, context):
        if context.space_data.context == 'DATA':
            if context.active_object is not None:
                return True

    def execute(self, context):
        print(context.space_data.context)
        if hasattr(context, 'button_pointer'):
            btn = context.button_pointer
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
            if item.trait_type == 'morph_set':
                morph = item.morph_set.add()
                morph.name = btn.active_shape_key.name
                morph.float_default = btn.active_shape_key.value
                morph.float_min = btn.active_shape_key.slider_min
                morph.float_max = btn.active_shape_key.slider_max
                morph.model_ref = item.model_ref

            else:
                print("Invalid data selection.")
    

        return {'FINISHED'}


class HVYM_AddModel(bpy.types.Operator):
    """Add a model to the Heavymeta Data list."""
    bl_idname = "hvym_add.model"
    bl_label = "Add Model Data"

    @classmethod
    def poll(cls, context):
        if isinstance(context.space_data, bpy.types.SpaceOutliner) and context.active_object.type == 'MESH':
            if context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Object':
                return True

    def execute(self, context):
        if bpy.context.selected_objects[0] != None:
            obj = bpy.context.selected_objects[0]
            print('add model to data')
            if has_hvym_data('model', obj.name) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'mesh'
                item.type = obj.name
                item.values = 'Object'
                item.model_ref = context.active_object
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}

class HVYM_AddAnim(bpy.types.Operator):
    """Add a NLA animation to the Heavymeta Data list."""
    bl_idname = "hvym_add.anim"
    bl_label = "Add Animation Data"

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
    bl_label = "Add Material Data"

    @classmethod
    def poll(cls, context):
        if isinstance(context.space_data, bpy.types.SpaceOutliner):
            if context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Material':
                return True

    def execute(self, context):
        matName  = context.selected_ids[0].name
        if matName != None:
            if has_hvym_data('material', matName) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'material'
                item.type = matName
                item.values = 'Material'
                item.mat_ref = bpy.data.materials[matName]
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}

class HVYM_AddMaterialToSet(bpy.types.Operator):
    """Add a material to the Heavymeta Data list."""
    bl_idname = "hvym_add.material_to_set"
    bl_label = "Add Material Data to Set"

    @classmethod
    def poll(cls, context):
        item = None
        if len(context.collection.hvym_meta_data)>0:
            item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
        if item != None and isinstance(context.space_data, bpy.types.SpaceOutliner) and item.trait_type == 'mat_set':
            if context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Material':
                matName  = context.selected_ids[0].name
                if not material_in_matset(bpy.data.materials[matName], item.mat_set):
                    return True

    def execute(self, context):
        matName  = context.selected_ids[0].name
        if matName != None:
            if has_hvym_data('material', matName) == False:
                item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
                if item.trait_type == 'mat_set':
                    mat_item = item.mat_set.add()
                    item.values = 'Material Set'
                    mat_item.mat_ref = bpy.data.materials[matName]
                    
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}



# -------------------------------------------------------------------
#   Class Registration
# -------------------------------------------------------------------
blender_classes = [
    HVYM_MenuTransform,
    HVYM_MenuTransformGroup,
    HVYM_MenuDataItem,
    HVYM_MeshSet,
    HVYM_MaterialSet,
    HVYM_MorphSet,
    HVYM_DataItem,
    HVYM_UL_DataList,
    HVYM_UL_MeshSetList,
    HVYM_UL_MaterialSetList,
    HVYM_UL_MorphSetList,
    HVYM_MENU_NewMenuTransform,
    HVYM_LIST_NewPropItem,
    HVYM_LIST_NewMeshItem,
    HVYM_LIST_NewMeshSet,
    HVYM_LIST_NewMeshSetItem,
    HVYM_LIST_AddMeshSetItemToSet,
    HVYM_LIST_DeleteMeshSetItem,
    HVYM_LIST_NewMorphSet,
    HVYM_LIST_DeleteMorphSetItem,
    HVYM_LIST_NewAnimItem,
    HVYM_LIST_NewMatItem,
    HVYM_LIST_NewMatSet,
    HVYM_LIST_NewMatSetItem,
    HVYM_LIST_NewMatSetMaterial,
    HVYM_LIST_DeleteMatSetItem,
    HVYM_LIST_DeleteMatSetMaterial,
    HVYM_LIST_DeleteItem,
    HVYM_LIST_MoveItem,
    HVYM_LIST_DirectionUp,
    HVYM_LIST_DirectionDown,
    HVYM_LIST_DefaultValues,
    HVYM_DebugMinter,
    HVYM_DebugModel,
    HVYM_DataReload,
    HVYM_DataOrder,
    HVYM_ExportHelper,
    HVYM_DeployMinter,
    HVYM_DeployConfirmMinterDeployDialog,
    HVYM_DeployNFT,
    HVYM_DeployConfirmNFTDeploytDialog,
    HVYM_Menu_Transform_Panel,
    HVYM_DataPanel,
    HVYM_ScenePanel,
    HVYM_NFTDataExtensionProps,
    HVYMGLTF_PT_export_user_extensions,
    TestOp,
    WM_OT_button_context_test,
    HVYM_AddMorph,
    HVYM_AddModel,
    HVYM_AddAnim,
    HVYM_AddMaterial,
    HVYM_AddMaterialToSet
    ]

def register():
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load("logo", os.path.join(icons_dir, "hvym_logo_128.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    BlenderNode.create_object = patched_create_object

    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for (prop_name, prop_value) in COL_PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    
    bpy.types.Scene.hvym_collections_data = bpy.props.PointerProperty(type=HVYM_NFTDataExtensionProps)
    bpy.types.Scene.hvym_menu_meta_data = bpy.props.CollectionProperty(type = HVYM_MenuDataItem)
    bpy.types.Collection.hvym_meta_data = bpy.props.CollectionProperty(type = HVYM_DataItem)
    bpy.types.Collection.hvym_menu_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data menus", default = -1)
    bpy.types.Object.hvym_menu_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data menus", default = -1)
    bpy.types.Object.hvym_menu_id = bpy.props.StringProperty(name = "Unique id for menu derived from collection id", default='')
    bpy.types.Collection.hvym_list_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data", default = 0)
    bpy.types.Collection.hvym_nft_type_enum = bpy.props.StringProperty(name = "Used to set nft type enum on import", default='HVYC')
    bpy.types.Collection.hvym_col_type_enum = bpy.props.StringProperty(name = "Used to set collection type enum on import", default='multi')
    bpy.types.Collection.hvym_minter_type_enum = bpy.props.StringProperty(name = "Used to set minter type enum on import", default='payable')
    bpy.types.OUTLINER_MT_asset.append(outliner_menu_func)
    bpy.types.NLA_MT_channel_context_menu.append(nla_menu_func)
    bpy.types.UI_MT_button_context_menu.append(btn_menu_func)

    if not hasattr(bpy.types.Collection, 'hvym_id'):
        bpy.types.Collection.hvym_id = bpy.props.StringProperty(default = '')

    if not hasattr(bpy.types.Object, 'hvym_id'):
        bpy.types.Object.hvym_id = bpy.props.StringProperty(default = '')


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Scene.hvym_collections_data
    del bpy.types.Scene.hvym_menu_meta_data
    del bpy.types.Collection.hvym_meta_data
    del bpy.types.Collection.hvym_menu_index
    del bpy.types.Object.hvym_menu_index
    del bpy.types.Object.hvym_menu_id
    del bpy.types.Collection.hvym_list_index
    del bpy.types.Collection.hvym_nft_type_enum
    del bpy.types.Collection.hvym_col_type_enum
    del bpy.types.Collection.hvym_minter_type_enum
    bpy.types.OUTLINER_MT_asset.remove(outliner_menu_func)
    bpy.types.NLA_MT_channel_context_menu.remove(nla_menu_func)
    bpy.types.UI_MT_button_context_menu.remove(btn_menu_func)

    if hasattr(bpy.types.Collection, 'hvym_id'):
        del bpy.types.Collection.hvym_id

    if hasattr(bpy.types.Object, 'hvym_id'):
        del bpy.types.Object.hvym_id

    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for (prop_name, _) in COL_PROPS:
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
    valProps = None
    meshProps = None
    morphNodes = None
    animProps = None
    collections = {}

    def set_col_data(type, prop, dct):
        item = collection.hvym_meta_data.add()
        item.trait_type = type
        item.type = prop
        #item.values = prop.values
        #item.values = dct[prop]
        updateNftData(bpy.context)

    for id in ext_data.keys():
        if id == 'contract':
            bpy.context.scene.hvym_nft_price = ext_data[id]['nftPrice']
            #bpy.context.scene.hvym_nft_type_enum = ext_data[id]['nftType']
            bpy.context.collection.hvym_nft_type_enum = ext_data[id]['nftType']
            #bpy.context.scene.hvym_minter_type_enum = ext_data[id]['minterType']
            bpy.context.collection.hvym_minter_type_enum = ext_data[id]['minterType']
            bpy.context.scene.hvym_minter_name = ext_data[id]['minterName']
            bpy.context.scene.hvym_minter_description = ext_data[id]['minterDesc']
            bpy.context.scene.hvym_minter_image = ext_data[id]['minterImage']
            bpy.context.scene.hvym_minter_version = ext_data[id]['minterVersion']
            bpy.context.scene.hvym_contract_abi = ext_data[id]['contractABI']
            bpy.context.scene.hvym_contract_address = ext_data[id]['contractAddress']

            if bpy.context.scene.hvym_minter_version > 0:
                bpy.context.scene.hvym_add_version = True

            updateNftData(bpy.context)

        else:
            name = ext_data[id]['collection_name']
            collection = bpy.data.collections.new(name)
            collection.hvym_id = id
            collection.hvym_collection_type = ext_data[id]['collectionType']
            collections[id] = collection

            if 'valProps' in ext_data[id].keys():
                valProps = ext_data[id]['valProps']
                item = collection.hvym_meta_data.add()
                item.trait_type = "property"
                for t in valProps.keys():
                    item.int_default = valProps[t]["default"]
                    item.int_min = valProps[t]["min"]
                    item.int_min = valProps[t]["min"]
                    item.prop_slider_type = valProps[t]["prop_slider_type"]
                    item.prop_action_type = valProps[t]["prop_action_type"]
                    #set_col_data('property', t, valProps)
                updateNftData(bpy.context)
                
            if 'meshProps' in ext_data[id].keys():
                meshProps = ext_data[id]['meshProps']
                for t in meshProps:
                    set_col_data('mesh', t, meshProps)

            if 'morphProps' in ext_data[id].keys():
                morphProps = ext_data[id]['morphProps']
                for t in morphProps:
                    set_col_data('morph', t, morphProps)

            if 'animProps' in ext_data[id].keys():
                animProps = ext_data[id]['animProps']
                for t in animProps:
                    set_col_data('anim', t, animProps)

            
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

    #print(type(bpy.data.collections))
    for col in bpy.data.collections.keys():
    #for col in bpy.data.collections:
        hvym_coll = bpy.data.collections.get(col) #.hvym_id
        if hvym_coll.hvym_id != None:
        #if col.hvym_id != None:
            id = hvym_coll.hvym_id
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
class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    # Gather export data
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if len(bpy.data.collections) == 0:
            return

        # Compile data objects in sets by collection
        mappings = []
        for col in bpy.data.collections:
            mappings.append(col.name)

        if bpy.types.Scene.hvym_collections_data.enabled:
            if gltf2_object.extensions is None:
                gltf2_object.extensions = {glTF_extension_name : None}
            gltf2_object.extensions[glTF_extension_name] = self.Extension(
                name = glTF_extension_name,
                extension = mappings,
                required = False
            )

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
                        data[id]['collectionType'] = col.hvym_collection_type
                        data[id]['nodes'] = nodes
                            
    

            gltf2_object.extensions[glTF_extension_name] = data