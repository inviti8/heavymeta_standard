"""
[Blender and Python] Heavymeta Standard 
Fibo Metavinci - August 2022
Email: comicronos@gmail.com
Addon to add standardized meta-data to the scene at the API level.  Standard
Heavmeta Data are offered as a proposed framework that is based on standards
defined here: https://www.nftstandards.wtf/NFT/NFT+Metadata.  Additional att-
ributes have been added to support properties used in 3D art and Animation. 
I have opted to make all NFT related data assignable at the Collection level.
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
from time import time
import bpy
import re
import random
import math
import os
import subprocess
import threading
from subprocess import run, Popen, PIPE
import concurrent.futures
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
from pathlib import Path
from _thread import start_new_thread
import webbrowser
import ast
import json

HOME = os.path.expanduser("~").replace('\\', '/') if os.name == 'nt' else os.path.expanduser("~")

preview_collections = {}

glTF_extension_name = "HVYM_nft_data"

SCRIPT_PATH = bpy.utils.user_resource('SCRIPTS')
ADDON_PATH = os.path.join(SCRIPT_PATH, 'addons', 'heavymeta_standard')
#CLI = os.path.join(ADDON_PATH, 'hvym')
CLI = os.path.join(HOME, '.local', 'share', 'heavymeta-cli', 'hvym')
CLI_INSTALLED = False
#print(bpy.data.filepath.lower())
#FILE_NAME = Path(bpy.data.filepath).stem
FILE_NAME = 'NOT SET'
ICP_PATH = 'NOT SET'
DAEMON_RUNNING = False
LOADING = False

FILE_PATH = Path(__file__).parent

if os.path.isfile(CLI):
    result = subprocess.run([CLI, 'icp-project-path'], capture_output=True, text=True, check=False)

    if result.returncode != 0:
        ICP_PATH = result.stderr
    else:
        ICP_PATH = result.stdout
        CLI_INSTALLED = True

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

def update_progress():
    global LOADING
    wm = bpy.context.window_manager
    tot = 1000  # progress from [0 - 1000]
    wm.progress_begin(0, tot)
    i = 0
    while True:
        if not LOADING:  # break the loop when loading is False
            print("Loading cancelled.")
            wm.progress_end()
            break
        wm.progress_update(i % tot)  # update progress bar
        i += 1

def run_futures_cmds(cmds):
    result = None
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run, cmd, shell=True): cmd for cmd in cmds}
        
        for future in concurrent.futures.as_completed(futures):
            cmd = futures[future]
            
            try:
                result = future.result()  # Get the result from Future object
                # print("Command output: ", result.stdout)
                
            except Exception as e:   # Checking for any exception raised by the command
                print("Command failed with error:", str(e))
            # else:
            #     print(future.result().stdout)
            #     print(f"{cmd} completed successfully")

        return result

def run_command(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:   # Checking the return code
        print("Command failed with error:", error.decode('utf-8'))
    else:
        print(output.decode('utf-8'))
        return output.decode('utf-8')

def call_cli_threaded(command):
    if os.path.isfile(CLI):
        command = CLI + ' ' + command
        print(command)
        thread = threading.Thread(target=run_command, args=(command,))
        thread.start()
        print('thread.start()')
        # thread.join()
        # print('thread.join()')

def call_cli(call_arr):
    result = None
    arr = []
    for p in call_arr:
        arr.append(str(p))

    if os.path.isfile(CLI):
        cli_call = [CLI]
        cli_call = cli_call+arr

        call = subprocess.run(cli_call, capture_output=True, text=True, check=False)

        if call.returncode != 0:
            print("Command failed with error:")
            print(call.stderr)
            result = call.stderr
        else:
            result = call.stdout
            # print(result)

    return result

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

def UpdateAnimData(context):
    hvym_meta_data = context.collection.hvym_meta_data

    for i in range(len(hvym_meta_data)):
        if hvym_meta_data[i].trait_type == 'anim':
            model = hvym_meta_data[i].model_ref
            print(model)
            if model is not None:
                print(model.animation_data.action_blend_type)
                name = hvym_meta_data[i].type
                hvym_meta_data[i].anim_start = bpy.data.actions[name].frame_start
                hvym_meta_data[i].anim_end = bpy.data.actions[name].frame_end
                hvym_meta_data[i].anim_blending = model.animation_data.action_blend_type


def RebuildMaterialSets(context):
    hvym_meta_data = context.collection.hvym_meta_data

    for i in range(len(hvym_meta_data)):
        verts = []    
        edges = []
        faces = []
        if hvym_meta_data[i].trait_type == 'mat_set':
            name = 'mat_set'+context.collection.hvym_id+'_'+hvym_meta_data[i].type
            col_name = 'HVYM_OBJ_DATA'
            obj = bpy.context.scene.objects.get(name)
            mesh = bpy.data.meshes.new('MESH_'+name)  # add the new mesh
                
            obj = hvym_meta_data[i].mat_lib_ref
            if obj:
                bpy.data.meshes.remove(obj.data)
                    
            data_col = bpy.data.collections.get(col_name)
            if data_col is None:
                data_col = bpy.data.collections.new(col_name)
                data_col.hide_select = True 
                data_col.color_tag = 'COLOR_01'      
                bpy.context.scene.collection.children.link(data_col)
                    
            obj = bpy.data.objects.new(name, mesh)
            lockObj(obj)
            data_col.objects.link(obj)
            hvym_meta_data[i].mat_lib_ref = obj
            j=0       
            for m in hvym_meta_data[i].mat_set:
                size = 0.01
                bpy.data.materials.new(name=m.name)
                obj.data.materials.append(m.mat_ref)
                verts.append(( size,  size,  size*j))
                verts.append(( size,  -size,  size*j))
                verts.append(( -size,  -size,  size*j))
                faces.append([j,j+1,j+2])
                j+=1
                    
            mesh.from_pydata(verts, edges, faces)

            j=0
            for mat in obj.data.materials:
                obj.data.polygons[j].material_index = j
                j+=1

def get_material_properties(mat):
    data = {}
    valid_props = ['diffuse_color', 'specular_color', 'specular', 'specular_intensity', 'roughness', 'metallic']
    for attr in dir(mat):
       if hasattr( mat, attr ) and attr in valid_props:
        value = getattr(mat, attr)
        if attr == 'diffuse_color':
            value = color_to_hex(mat.diffuse_color)
        elif attr == 'specular_color':
            value = color_to_hex(value)
        data[attr] = value

    return data

def handle_mat_props(item, mat_props):
    item.mat_emissive = False
    item.mat_sheen = False
    item.mat_type = mat_props['mat_type']

    if mat_props['mat_type'] == 'PBR':

        if mat_props['emissiveIntensity'] > 0:
            item.mat_emissive = True

        if mat_props['sheen'] > 0:
            item.mat_sheen = True


def create_mat_ref(value):
    mat_props = {'name': value.name, 'color': color_to_hex(value.diffuse_color), 'type': 'Material'}

    for node in value.node_tree.nodes:
        node_type = str(node.type)
        if node_type == 'EEVEE_SPECULAR':
            mat_props['mat_type'] = 'PBR'

            if 'Specular Tint' in node.inputs.keys():
                    mat_props['specularColor'] = color_to_hex(node.inputs['Specular Tint'].default_value)

            if 'Specular' in node.inputs.keys():
                    mat_props['specularIntensity'] = node.inputs['Specular'].default_value

            if 'Roughness' in node.inputs.keys():
                    mat_props['roughness'] = node.inputs['Roughness'].default_value

            if 'Emissive Color' in node.inputs.keys():
                    mat_props['emissive_color'] = color_to_hex(node.inputs['Emissive Color'].default_value)

            if 'Transparency' in node.inputs.keys():
                    mat_props['transparency'] = node.inputs['Transparency'].default_value

            if 'Clear Coat' in node.inputs.keys():
                    mat_props['clearcoat'] = node.inputs['Clear Coat'].default_value

            if 'Clear Coat Roughness' in node.inputs.keys():
                    mat_props['clearcoatRoughness'] = node.inputs['Clear Coat Roughness'].default_value

        elif str(node.type) == 'BSDF_DIFFUSE' or str(node.type) == 'BSDF_SHEEN':
            mat_props['mat_type'] = 'STANDARD'

            if 'Color' in node.inputs.keys():
                    mat_props['color'] = color_to_hex(node.inputs['Color'].default_value)

            if 'Roughness' in node.inputs.keys():
                    mat_props['roughness'] = node.inputs['Roughness'].default_value 

            if 'Metallic' in node.inputs.keys():
                mat_props['metalness'] = node.inputs['Metallic'].default_valu

        elif str(node.type) == 'BSDF_TOON':
            mat_props['type'] = 'TOON'

            if 'Color' in node.inputs.keys():
                    mat_props['color'] = color_to_hex(node.inputs['Color'].default_value)

            if 'Size' in node.inputs.keys():
                mat_props['size'] = node.inputs['Size'].default_value

            if 'Smooth' in node.inputs.keys():
                mat_props['smooth'] = node.inputs['Smooth'].default_value     

        elif str(node.type) == 'BSDF_PRINCIPLED':
            mat_props['mat_type'] = 'PBR'

            if 'Roughness' in node.inputs.keys():
                mat_props['roughness'] = node.inputs['Roughness'].default_value

            if 'Metallic' in node.inputs.keys():
                mat_props['metalness'] = node.inputs['Metallic'].default_value

            if 'Specular Tint' in node.inputs.keys():
                    mat_props['specularColor'] = color_to_hex(node.inputs['Specular Tint'].default_value)

            if 'Specular IOR Level' in node.inputs.keys():
                mat_props['ior'] = node.inputs['Specular IOR Level'].default_value

            if 'Anisotropic' in node.inputs.keys():
                mat_props['anisotropy'] = node.inputs['Anisotropic'].default_value

            if 'Anisotropic Rotation' in node.inputs.keys():
                mat_props['anisotropyRotation'] = node.inputs['Anisotropic Rotation'].default_value

            if 'Coat Weight' in node.inputs.keys():
                mat_props['coat'] = node.inputs['Coat Weight'].default_value

            if 'Emission Color' in node.inputs.keys():
                    mat_props['emissive'] = color_to_hex(node.inputs['Emission Color'].default_value)

            if 'Emission Strength' in node.inputs.keys():
                strength = node.inputs['Emission Strength'].default_value
                mat_props['emissiveIntensity'] = strength

            if 'Sheen Tint' in node.inputs.keys():
                mat_props['sheenColor'] = color_to_hex(node.inputs['Sheen Tint'].default_value)

            if 'Sheen Weight' in node.inputs.keys():
                weight = node.inputs['Sheen Weight'].default_value
                mat_props['sheen'] = weight

    return mat_props


def property_group_to_dict(pg):
    result = {}
    
    if len(pg) == 0:
        return result 
        
    for i in range(len(pg)):
        item_result = {}
        
        for attr in dir(pg[i]):
            if hasattr( pg[i], attr ):
                value = getattr(pg[i], attr)

                if(attr == 'model_ref'):
                    if value != None:
                        value = {'name': value.name}
                if(attr == 'action_set'):
                    if value != None:
                        a_set = []
                        for a in pg[i].action_set:
                            a_set.append(a.string)
                    value = a_set
                if(attr == 'mesh_set'):
                    if value != None:
                        m_set = []
                        for m in pg[i].mesh_set:
                            if m.model_ref != None:
                                visible = not m.model_ref.hide_select
                                mesh_data = {
                                        'name': m.model_ref.name,
                                        'visible': visible
                                        }
                                m_set.append(mesh_data)

                        value = m_set
                if(attr == 'morph_set'):
                    if value != None:
                        m_set = []
                        for m in pg[i].morph_set:
                            morph_data = {
                                'name': m.name,
                                'default': m.float_default,
                                'min': m.float_min,
                                'max': m.float_max
                            }
                            m_set.append(morph_data)
                        value = m_set

                if(attr == 'anim_blending'):
                    if hasattr( pg[i], 'model_ref' ) and pg[i].model_ref != None and pg[i].model_ref.animation_data != None:
                        pg[i].anim_blending = pg[i].model_ref.animation_data.action_blend_type

                if(attr == 'mat_ref'):
                    if value != None:
                        value = create_mat_ref(value)
                        handle_mat_props(pg[i], value)

                if(attr == 'mat_set'):
                    if value != None:
                        mat_sets = []
                        for m in value:
                            if m.mat_ref != None:
                                mat_sets.append(create_mat_ref(m.mat_ref))

                        value = mat_sets

                if(attr == 'menu_primary_color' or attr == 'menu_secondary_color' or attr == 'menu_text_color'):
                    if value != None:
                        value = color_to_hex(value)
                
                if isinstance(value, (str, int, float, bool, list, dict)):
                    try:
                        json.dumps(value)   # Try converting value into json format
                    except (TypeError, OverflowError):  # If it fails due to these reasons
                        pass  # Ignore this value
                    else:
                        item_result[attr] = value  # Only add the value to `item_result` if it is serializable.
            
        result[i] = item_result

    
    return result


def property_group_to_json(pg):
    #print(json.dumps(property_group_to_dict(pg)))
    return json.dumps(property_group_to_dict(pg))


def updateNftData(context):
    #Update all the props on any change
    #put them into a single structure
    if context.collection.name == 'Scene Collection':
        return
        
    hvym_meta_data = context.collection.hvym_meta_data
    hvym_action_meta_data = context.scene.hvym_action_meta_data
    setCollectionId(context.collection)
    nodes = []

    for obj in context.collection.objects:
        node = {'name': obj.name, 'type': obj.type}
        nodes.append(node)

    params = [
        'contract-data',
        context.scene.hvym_mintable,
        context.scene.hvym_nft_type, 
        context.scene.hvym_nft_chain, 
        round(context.scene.hvym_nft_price, 4), 
        round(context.scene.hvym_prem_nft_price, 4), 
        context.scene.hvym_max_supply, 
        context.scene.hvym_minter_type,
        context.scene.hvym_minter_name,
        context.scene.hvym_minter_description,
        context.scene.hvym_minter_image,
        context.scene.hvym_minter_version
    ]

    context.scene.hvym_collections_data.nftData['contract'] =json.loads(call_cli(params))

    params = [
        'parse-blender-hvym-collection', 
        context.collection.name, 
        context.collection.hvym_collection_type, 
        context.collection.hvym_id, 
        property_group_to_json(hvym_meta_data), 
        property_group_to_json(context.scene.hvym_menu_meta_data), 
        json.dumps(nodes),
        property_group_to_json(hvym_action_meta_data)
    ]

    context.scene.hvym_collections_data.nftData[context.collection.hvym_id] = json.loads(call_cli(params))
    # print(json.loads(call_cli(params)))
    


def onUpdate(self, context):
    RebuildMaterialSets(context)
    updateNftData(context)
    if context.scene.hvym_project_type == 'model':
        context.scene.hvym_daemon_path = call_cli(['icp-model-path'])
    elif context.scene.hvym_project_type == 'minter':
        context.scene.hvym_daemon_path = call_cli(['icp-minter-path'])

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
            if self.model_ref != None and self.model_ref.data.shape_keys != None:
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


def nftChains(self, context):
    #get the default enum, used to set enum on import
    first_enum = context.collection.hvym_nft_chain_enum 

    tup = (
            ('ICP', "Internet Computer", ""),
            ('AR', "Aweave", ""),
            ('BTCL', "Bitcoin Lightning", ""))

    result = setEnum(tup, first_enum, 'ICP')

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
    ('hvym_nft_chain', bpy.props.EnumProperty(
        name='Chain',
        items=nftChains,
        description ="Chain to mint to, see docs for more detail.",
        update=onUpdate)),
    ('hvym_nft_type', bpy.props.EnumProperty(
        name='NFT-Type',
        items=nftTypes,
        description ="Heavymeta NFT type, see docs for more detail.",
        update=onUpdate)),
    ('hvym_nft_price', bpy.props.FloatProperty(name='NFT-Price', default=0.01, description ="Price of NFT in eth.", update=onUpdate)),
    ('hvym_mintable', bpy.props.BoolProperty(name='Mintable', description ="If true, this model is a mintable NFT.", default=True)),
    ('hvym_prem_nft_price', bpy.props.FloatProperty(name='Premium-NFT-Price', default=0.01, description ="Premium price of customized NFT in eth.", update=onUpdate)),
    ('hvym_max_supply', bpy.props.IntProperty(name='Max-Supply', default=100, description ="Max number that can be minted, if -1 supply is infinite.", update=onUpdate)),
    ('hvym_minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=minterTypes,
        description ="Minted by creator only, or public.",
        update=onUpdate)),
    ('hvym_minter_name', bpy.props.StringProperty(name='Minter-Name', default='', description ="Name of minter.", update=onUpdate)),
    ('hvym_minter_description', bpy.props.StringProperty(name='Minter-Description', default='', description ="Details about the NFT.", update=onUpdate)),
    ('hvym_minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='', description ="Custom header image for the minter ui.", update=onUpdate)),
    ('hvym_project_name', bpy.props.StringProperty(name='Project-Name', default='NOT-SET!!!!', description ="Collection name for asset deployement.", update=onUpdate)),
    ('hvym_project_path', bpy.props.StringProperty(name=':', default='NOT-SET!!!!', description ="Current working project path.", update=onUpdate)),
    ('hvym_project_type', bpy.props.EnumProperty(
        name='Project-Type',
        items=(
            ('model', "Model", ""),
            ('minter', "Minter", "")),
        description ="Type of Project.",
        update=onUpdate)),
    ('hvym_daemon_path', bpy.props.StringProperty(name=':', default='NOT-SET!!!!', description ="Current active daemon project path.")),
    ('hvym_debug_url', bpy.props.StringProperty(name='Url', default='', description ="Current running debug url.", update=onUpdate)),
    ('hvym_daemon_running', bpy.props.BoolProperty(name="Daemon Running", description="Toggle the test daemon.", default=False)),
    ('hvym_add_version', bpy.props.BoolProperty(name='Minter-Version', description ="Enable versioning for this NFT minter.", default=False)),
    ('hvym_minter_version', bpy.props.IntProperty(name='Version', default=0, description ="Version of the NFT minter.", update=onUpdate)),
    ('hvym_export_name', bpy.props.StringProperty(name='Export-Name', default=FILE_NAME, description ="Gltf export path for debug & deploy.", update=onUpdate)),
    ('hvym_export_path', bpy.props.StringProperty(name='Export-Path', subtype='FILE_PATH', default='', description ="Gltf export path for debug & deploy.", update=onUpdate)),
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

    menu_alignment: bpy.props.EnumProperty(
            name='Alignment',
            description ="Set alignment for menu relative to transform.",
            items=(('CENTER', 'Center', ""),
                ('LEFT', 'Left', ""),
                ('RIGHT', 'Right', ""),),
            update=onUpdate)

    no_update: bpy.props.BoolProperty(
           name="Flag to stop auto update in the case of needing to update list values",
           description="",
           default=False)


class HVYM_StringSet(bpy.types.PropertyGroup):
    """Group of properties representing a set of strings."""

    string: bpy.props.StringProperty(
           name="String",
           description="String reference.",
           default="",
           update=onUpdate)


class HVYM_UL_StringSetList(bpy.types.UIList):
    """Heavymeta string set list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.string, icon = 'NLA')


        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.string, icon = 'NLA')


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

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "mat_ref")


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


def GetPropWidgetType(item):
    result = 'meter'
    if item.trait_type == 'property':
        result = 'prop_slider_type'
    elif item.trait_type == 'mat_set' or item.trait_type == 'mesh_set':
        result = 'prop_selector_type'
    elif item.trait_type == 'anim':
        result = 'prop_toggle_type'
        if item.anim_loop == 'Clamp':
            result = 'prop_anim_slider_type'
    elif item.trait_type == 'mesh':
        result = 'prop_toggle_type'
    elif item.trait_type == 'mat_prop' or item.trait_type == 'morph_set':
        result = 'prop_multi_widget_type'

    return result


class HVYM_ActionDataItem(bpy.types.PropertyGroup):
    """Group of properties representing various meta data."""

    trait_type: bpy.props.StringProperty(
           name="Type",
           description="action meta-data trait type",
           default="",
           update=onUpdate)

    type: bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="",
           update=onUpdate)

    values: bpy.props.StringProperty(
           name="Values",
           description="",
           default="",
           update=onUpdate)

    anim_interaction_type: bpy.props.EnumProperty(
            name='Interaction',
            description ="Set interaction for this action animation.",
            items=(('none', 'None', ""),
                ('click', 'Click', ""),
                ('double_click', 'Double Click', ""),
                ('mouse_wheel', 'Mouse Wheel', ""),),
            update=onUpdate)

    mesh_interaction_type: bpy.props.EnumProperty(
            name='Interaction',
            description ="Set interaction for this action animation.",
            items=(('none', 'None', ""),
                ('click', 'Click', ""),
                ('double_click', 'Double Click', ""),
                ('mouse_over', 'Mouse Over', ""),),
            update=onUpdate)

    sequence_type: bpy.props.EnumProperty(
            name='Sequence',
            description ="Set sequence type for this action animation.",
            items=(('loop', 'Loop', ""),
                ('one_shot', 'One Shot', ""),),
            update=onUpdate)

    set_index: bpy.props.IntProperty(
           name="Set Index",
           description="Items sharing the same index are grouped together.",
           default=0,
           update=onUpdate)

    action_set: bpy.props.CollectionProperty(type = HVYM_StringSet)

    additive: bpy.props.BoolProperty(
           name="Additive Blending",
           description="If true, blending set to additive.",
           default=False,
           update=onUpdate)

    model_ref: bpy.props.PointerProperty(
        name="Model Reference",
        type=bpy.types.Object)


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

    show: bpy.props.BoolProperty(
           name="Show Widget",
           description="If true widget should be rendered.",
           default=True,
           update=onUpdate)

    prop_value_type: bpy.props.EnumProperty(
            name='Value Type',
            description ="Set value type of property.",
            items=(('Int', 'Integer', ""),
                ('Float', 'Float', ""),),
            update=onUpdate)

    prop_slider_type: bpy.props.EnumProperty(
            name='Widget',
            description ="Set ui widget for property.",
            items=(('value_meter', 'Text Box Meter', ""),
                ('slider', 'Slider', ""),
                ('meter', 'Meter', ""),
                ('none', 'None', ""),),
            update=onUpdate)

    prop_anim_slider_type: bpy.props.EnumProperty(
            name='Widget',
            description ="Set ui widget for property.",
            items=(('slider', 'Slider', ""),
                ('none', 'None', ""),),
            update=onUpdate)

    prop_selector_type: bpy.props.EnumProperty(
            name='Widget',
            description ="Set ui selector widget for property.",
            items=(('selector', 'Selector', ""),
                ('none', 'None', ""),),
            update=onUpdate)

    prop_toggle_type: bpy.props.EnumProperty(
            name='Widget',
            description ="Set ui toggle widget for property.",
            items=(('toggle', 'Toggle', ""),
                ('none', 'None', ""),),
            update=onUpdate)

    prop_multi_widget_type: bpy.props.EnumProperty(
            name='Multi-Widget',
            description ="Set ui multi widget for property.",
            items=(('multi_widget', 'Multi-Widget', ""),
                ('none', 'None', ""),),
            update=onUpdate)

    prop_immutable: bpy.props.BoolProperty(
           name="Immutable",
           description="If a propety is immutable, it is minted, and can't be updated after minting.",
           default=True,
           update=onUpdate)

    prop_action_type: bpy.props.EnumProperty(
            name='Action Type',
            description ="Set property action type.",
            items=(('Incremental', 'Incremental', ""),
                ('Decremental', 'Decremental', ""),
                ('Bicremental', 'Bicremental', ""),
                ('Setter', 'Setter', ""),
                ('Static', 'Static', ""),),
            update=onUpdate)

    prop_use_case: bpy.props.EnumProperty(
            name='Action Type',
            description ="Set property action type.",
            items=(('stats', 'Stats', ""),
                ('appearence', 'Appearence', ""),),
            update=onUpdate)

    values: bpy.props.StringProperty(
           name="Values",
           description="Add '(default, min, max)'",
           default="",
           update=onUpdate)

    call_param: bpy.props.EnumProperty(
            name='Call Parameter',
            description ="Set accepted parameter type for method call.",
            items=(('NONE', 'None', ""),
                ('STRING', 'String', ""),
                ('INT', 'Int', ""),),
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

    int_amount: bpy.props.IntProperty(
           name="Amount",
           description="Amount to increment or decrement.",
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

    float_amount: bpy.props.IntProperty(
           name="Amount",
           description="Amount to increment or decrement.",
           default=1,
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
                ('LoopRepeat', 'Loop Forever', ""),
                ('LoopOnce', 'Loop Once', ""),
                ('ClampToggle', 'Clamp Toggle', ""),
                ('Clamp', 'Clamp', ""),
                ('PingPong', 'Ping Pong', ""),),
            update=onUpdate)

    anim_start: bpy.props.FloatProperty(
           name="Frame Start",
           description="Start frame of animation.",
           default=0,
           update=onUpdate)

    anim_end: bpy.props.FloatProperty(
           name="Frame End",
           description="End frame of animation.",
           default=0,
           update=onUpdate)

    anim_blending: bpy.props.StringProperty(
           name="Blending",
           description="Blending mode for animation.",
           default="additive")

    anim_weight: bpy.props.FloatProperty(
           name="Weight",
           description="Weight for animation value.",
           default=1.0,
           min=0,
           max=1.0,
           update=onUpdate)

    anim_play: bpy.props.BoolProperty(
           name="Play",
           description="If animation is playing or not.",
           default=False,
           update=onUpdate)

    mat_type: bpy.props.StringProperty(
           name="Material Type",
           description="Type of material",
           default="STANDARD")

    model_ref: bpy.props.PointerProperty(
        name="Model Reference",
        type=bpy.types.Object)

    mat_ref: bpy.props.PointerProperty(
        name="Material Reference",
        type=bpy.types.Material)

    mat_emissive: bpy.props.BoolProperty(
           name="Emissive",
           description="Object emissive.",
           default=False)

    mat_reflective: bpy.props.BoolProperty(
           name="Reflective",
           description="Object reflective.",
           default=False,
           update=onUpdate)

    mat_iridescent: bpy.props.BoolProperty(
           name="Irridescent",
           description="Object irridescence.",
           default=False,
           update=onUpdate)

    mat_sheen: bpy.props.BoolProperty(
           name="Sheen",
           description="Object sheen.",
           default=False)

    morph_ref: bpy.props.PointerProperty(
        name="Morph Reference",
        type=bpy.types.Key)

    mat_lib_ref: bpy.props.PointerProperty(
        name="Model Reference with all materials assigned.",
        type=bpy.types.Object)

    material_id: bpy.props.IntProperty(
           name="ID",
           description="ID for material.",
           default=0,
           update=onUpdate)

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

    mesh_set_name: bpy.props.StringProperty(
           name="Mesh Set Name",
           description="name of the mesh set",
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

    value_prop_label: bpy.props.StringProperty(
           name="Value Property Label",
           description="Re-map name for value properties in this collection.",
           default="Value Properties",
           update=onUpdate)

    call_prop_label: bpy.props.StringProperty(
           name="Call Property Label",
           description="Re-map name for value properties in this collection.",
           default="Call Properties",
           update=onUpdate)

    mesh_prop_label: bpy.props.StringProperty(
           name="Mesh Property Label",
           description="Re-map name for mesh properties in this collection.",
           default="Mesh Properties",
           update=onUpdate)

    mat_prop_label: bpy.props.StringProperty(
           name="Material Property Label",
           description="Re-map name for material properties in this collection.",
           default="Material Properties",
           update=onUpdate)

    anim_prop_label: bpy.props.StringProperty(
           name="Animation Property Label",
           description="Re-map name for animation properties in this collection.",
           default="Animation Properties",
           update=onUpdate)

    mesh_set_label: bpy.props.StringProperty(
           name="Mesh Set Label",
           description="Re-map name for mesh sets in this collection.",
           default="Mesh Sets",
           update=onUpdate)

    morph_set_label: bpy.props.StringProperty(
           name="Morph Set Label",
           description="Re-map name for morph sets in this collection.",
           default="Morph Sets",
           update=onUpdate)

    mat_set_label: bpy.props.StringProperty(
           name="Material Set Label",
           description="Re-map name for material sets in this collection.",
           default="Material Sets",
           update=onUpdate)


class HVYM_UL_DataList(bpy.types.UIList):
    """Heavymeta data list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'FUND'

        if item.trait_type == 'mesh':
            custom_icon = 'MESH_ICOSPHERE'
        elif item.trait_type == 'call':
            custom_icon = 'SETTINGS'
        elif item.trait_type == 'mesh_set':
            custom_icon = 'FILE_3D'
        elif item.trait_type == 'morph_set':
            custom_icon = 'SHAPEKEY_DATA'
        elif item.trait_type == 'anim':
            custom_icon = 'ACTION_TWEAK'
        elif item.trait_type == 'mat_prop':
            custom_icon = 'SHADING_RENDERED'
        elif item.trait_type == 'mat_set':
            custom_icon = 'OVERLAY'
        elif item.trait_type == 'toggle':
            custom_icon = 'CHECKMARK'
        elif item.trait_type == 'action':
            custom_icon = 'DRIVER_TRANSFORM'
        elif item.trait_type == 'mesh_action':
            custom_icon = 'MESH_ICOSPHERE'

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


class HVYM_LIST_AddTrackToActionProp(bpy.types.Operator):
    """Add a new action property item to the list."""

    bl_idname = "hvym_meta_data.add_track_to_property_item"
    bl_label = "Add a new track to property item"

    def execute(self, context):
        ob = context.active_object

        if (ob is not None and ob.animation_data is not None and ob.animation_data.nla_tracks is not None and ob.animation_data.nla_tracks.active is not None):
            action_name = ob.animation_data.nla_tracks.active.name
            in_list = False
            active_track = ob.animation_data.nla_tracks.active
            hvym_action_list_index = context.scene.hvym_action_list_index 
            item = context.scene.hvym_action_meta_data[hvym_action_list_index]

            for i in range(len(item.action_set)):
                if (item.action_set[i].string == action_name):
                    in_list = True

            if(in_list == False):
                action_set = item.action_set.add()
                action_set.string = action_name
                item.set_index += 1

        return{'FINISHED'}


class HVYM_LIST_DeleteTrackFromActionProp(bpy.types.Operator):
    """Delete a morph slot from the set. Morph is not deleted"""

    bl_idname = "hvym_meta_data.delete_track_from_property_item"
    bl_label = "Delete track from property item"

    def execute(self, context):
        ob = context.active_object

        if (ob is not None and ob.animation_data is not None and ob.animation_data.nla_tracks is not None and ob.animation_data.nla_tracks.active is not None):
            action_name = ob.animation_data.nla_tracks.active.name
            in_list = False
            for i in range(len(context.scene.hvym_action_meta_data)):
                if (context.scene.hvym_action_meta_data[i].type == action_name):
                    in_list = True
            if(in_list == False):
                hvym_action_list_index = context.scene.hvym_action_list_index
                active_track = ob.animation_data.nla_tracks.active    
                item = context.scene.hvym_action_meta_data[hvym_action_list_index]

                item.action_set.remove(item.set_index)
                item.set_index = min(max(0, item.set_index - 1), len(item.action_set) - 1)


        return{'FINISHED'}


class HVYM_LIST_MoveTrack(bpy.types.Operator):
    """Move a track in the list."""

    bl_idname = "hvym_meta_data.move_track"
    bl_label = "Move an item in the list"

    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.scene.hvym_action_meta_data

    def move_index(self):
        hvym_action_list_index = bpy.context.scene.hvym_action_list_index   
        item = bpy.context.scene.hvym_action_meta_data[hvym_action_list_index]
        index = item.set_index
        list_length = len(item.action_set) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        item.set_index = max(0, min(new_index, list_length))

    def execute(self, context):
        hvym_action_list_index = context.scene.hvym_action_list_index
        item = context.scene.hvym_action_meta_data[hvym_action_list_index]
        index = item.set_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        item.action_set.move(neighbor, index)
        self.move_index(self)

        return{'FINISHED'}

class HVYM_LIST_TrackDirectionUp(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveTrack.direction to UP."""
    bl_idname = "hvym_meta_data.set_track_direction_up"
    bl_label = "Set the move direction to up"

    @classmethod
    def poll(cls, context):
        return context.scene.hvym_action_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveTrack.direction = "UP"
        HVYM_LIST_MoveTrack.execute(HVYM_LIST_MoveTrack, context)
        return{'FINISHED'}


class HVYM_LIST_TrackDirectionDown(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveTrack.direction to Down."""
    bl_idname = "hvym_meta_data.set_track_direction_down"
    bl_label = "Set the move direction to down"

    @classmethod
    def poll(cls, context):
        return context.scene.hvym_action_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveTrack.direction = "DOWN"
        HVYM_LIST_MoveTrack.execute(HVYM_LIST_MoveTrack, context)
        return{'FINISHED'}


class HVYM_LIST_NewActionPropItem(bpy.types.Operator):
    """Add a new action property item to the list."""

    bl_idname = "hvym_meta_data.new_action_property_item"
    bl_label = "Add a new action property item"

    def execute(self, context):
        ob = context.active_object

        if (ob is not None and ob.animation_data is not None and ob.animation_data.nla_tracks is not None and ob.animation_data.nla_tracks.active is not None):
            action_name = ob.animation_data.nla_tracks.active.name
            in_list = False
            active_track = ob.animation_data.nla_tracks.active    
            item = context.scene.hvym_action_meta_data.add()
            for i in range(len(item.action_set)):
                if (item.action_set[i].string == action_name):
                    in_list = True

            if(in_list == False):
                item.type = '*'
                item.trait_type = 'action'
                action_set = item.action_set.add()
                action_set.string = action_name
                item.values = 'Action Property'

                # updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_NewActionMeshPropItem(bpy.types.Operator):
    """Add a new mesh action property item to the list."""

    bl_idname = "hvym_meta_data.new_action_mesh_property_item"
    bl_label = "Add a new action mesh property item"

    def execute(self, context):
        ob = context.active_object

        if (ob is not None and ob.animation_data is not None and ob.animation_data.nla_tracks is not None and ob.animation_data.nla_tracks.active is not None):
            action_name = ob.animation_data.nla_tracks.active.name
            in_list = False
            for i in range(len(context.scene.hvym_action_meta_data)):
                if (context.scene.hvym_action_meta_data[i].type == action_name):
                    in_list = True
            if(in_list == False):      
                item = context.scene.hvym_action_meta_data.add()
                item.trait_type = 'mesh_action'
                item.type = '*'
                action_set = item.action_set.add()
                action_set.string = action_name
                item.values = 'Action Property'
                context.scene.hvym_action_list_index += 1

                # updateNftData(context)

        return{'FINISHED'}


class HVYM_LIST_DeleteActionItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "hvym_meta_data.delete_nav_item"
    bl_label = "Deletes an action item"

    @classmethod
    def poll(cls, context):
        return context.scene.hvym_action_meta_data

    def execute(self, context):
        ctx = context.scene
        hvym_action_meta_data = context.scene.hvym_action_meta_data
        index = context.scene.hvym_action_list_index
        item = ctx.hvym_action_meta_data[index]

        hvym_action_meta_data.remove(index)
        context.scene.hvym_action_list_index = min(max(0, index - 1), len(hvym_action_meta_data) - 1)

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


class HVYM_LIST_NewCallItem(bpy.types.Operator):
    """Add a new method call property item to the list."""

    bl_idname = "hvym_meta_data.new_call_item"
    bl_label = "Add a new call item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'call'
        item.type = '*'
        item.values = 'Call Property'
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
        item.values = 'Animation Property'
        item.anim_start = active_action.frame_start
        item.anim_end = active_action.frame_end
        item.anim_blending = ad.action_blend_type
        item.model_ref = context.active_object
        UpdateAnimData(context)
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
        item.trait_type = 'mat_prop'
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
        item.mesh_set_name = ref_set_item.type
        for m in ref_set_item.mesh_set:
            mesh_set = item.mesh_set.add()
            mesh_set.name = m.name
            mesh_set.model_ref = m.model_ref
            mesh_set.enabled = False
            
        RebuildMaterialSets(context)
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
        ctx = context.collection
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index
        item = ctx.hvym_meta_data[ctx.hvym_list_index]

        if item.mat_lib_ref != None:
            bpy.data.meshes.remove(item.mat_lib_ref.data)

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
        elif item.trait_type == 'mat_prop':
            item.values = 'N/A'

        return{'FINISHED'}

class HVYM_DataReload(bpy.types.Operator):
    bl_idname = "hvym_data.reload"
    bl_label = "Reload Data"
    bl_description ="Reload the data for this collection."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Update NFT Data")
        RebuildMaterialSets(context)
        updateNftData(context)
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

class HVYM_DebugMinter(bpy.types.Operator):
    bl_idname = "hvym_debug.minter"
    bl_label = "Launch Minter Debug UI"
    bl_description ="Launch minter UI debug."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Debug Minter")
        file_path = bpy.data.filepath
        file_name = bpy.context.scene.hvym_export_name

        if context.scene.hvym_nft_chain == 'ICP':
            print('gets here 1')
            if context.scene.hvym_project_path is not None:
                print('gets here 2!')
                project_path = bpy.context.scene.hvym_daemon_path.rstrip()
                print('project_path')
                print(project_path)
                #export gltf to project folder
                if os.path.exists(project_path):
                    print('should export!')
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, 88)
                    wm.progress_update(88)
                    model_dir = call_cli(['icp-minter-model-path']).rstrip()
                    out_file = os.path.join(model_dir, file_name)
                    #Clear old file
                    for filename in os.listdir(model_dir):
                        file_path = os.path.join(model_dir, filename)
                        if os.path.isfile(file_path) and '.glb' in file_path:
                            os.unlink(file_path)

                    bpy.ops.export_scene.gltf(filepath=out_file,  check_existing=False, export_format='GLB')
                    run_command(CLI+' icp-debug-model-minter '+file_name+'.glb')
                    project_type = context.scene.hvym_project_type
                    urls = run_command(CLI+f' icp-deploy-assets {project_type}')
                    context.scene.hvym_debug_url = ast.literal_eval(urls)[3]
                    wm.progress_end()


        return {'FINISHED'}


class HVYM_DebugModel(bpy.types.Operator):
    bl_idname = "hvym_debug.model"
    bl_label = "Launch Model Debug UI"
    bl_description ="Launch model UI debug."
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("Debug Model")
        file_path = bpy.data.filepath
        file_name = bpy.context.scene.hvym_export_name

        cli = os.path.join(ADDON_PATH, 'heavymeta_cli')
        if context.scene.hvym_nft_chain == 'ICP':
            if context.scene.hvym_project_path is not None:
                project_path = bpy.context.scene.hvym_daemon_path.rstrip()
                #export gltf to project folder
                if os.path.exists(project_path):
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, 88)
                    wm.progress_update(88)
                    src_dir = os.path.join(project_path, 'Assets', 'src')
                    out_file = os.path.join(src_dir, file_name)
                    #Clear old file
                    for filename in os.listdir(src_dir):
                        file_path = os.path.join(src_dir, filename)
                        if os.path.isfile(file_path) and '.glb' in file_path:
                            os.unlink(file_path)

                    bpy.ops.export_scene.gltf(filepath=out_file,  check_existing=False, export_format='GLB')
                    run_command(CLI+' icp-debug-model '+file_name+'.glb')
                    project_type = context.scene.hvym_project_type
                    urls = run_command(CLI+f' icp-deploy-assets {project_type}')
                    wm.progress_end()
                    context.scene.hvym_debug_url = ast.literal_eval(urls)[0]

        return {'FINISHED'}


class HVYM_DebugModelConfirmDialog(bpy.types.Operator):
    """Deploys debug model Editor."""
    bl_idname = "hvym_debug.model_confirm_dialog"
    bl_label = "Deploy debug model?"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, "YES")
        bpy.ops.hvym_debug.model()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class HVYM_SetProject(bpy.types.Operator):
    bl_idname = "hvym_set.project"
    bl_label = "Set Heavymeta project"
    bl_description ="Sets the current working project for the heavymeta cli."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Set Project")
        print(context.scene.hvym_project_name)
        if context.scene.hvym_nft_chain == 'ICP':
            call_cli(['icp-project', context.scene.hvym_project_name])
            ICP_PATH = call_cli(['icp-project-path'])
            context.scene.hvym_project_path = ICP_PATH.rstrip()
            if context.scene.hvym_project_type == 'model':
                context.scene.hvym_daemon_path = call_cli(['icp-model-path'])
            elif context.scene.hvym_project_type == 'minter':
                context.scene.hvym_daemon_path = call_cli(['icp-minter-path'])
            else:
                context.scene.hvym_daemon_path = os.path.join(ICP_PATH, context.scene.hvym_project_type)
            call_cli(['icp-init', '-f'])


        return {'FINISHED'}

class HVYM_SetConfirmDialog(bpy.types.Operator):
    """Sets the current Heavymeta prject based on settings."""
    bl_idname = "hvym_set.project_confirm_dialog"
    bl_label = "Set the current working project?"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, "YES")
        bpy.ops.hvym_set.project()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class HVYM_ToggleAssetDaemon(bpy.types.Operator):
    bl_idname = "hvym_toggle_asset.daemon"
    bl_label = "Toggle the test daemon."
    bl_description ="Enables and disables the asset daemon for testing."
    bl_options = {'REGISTER'}

    def execute(self, context):
        wm = bpy.context.window_manager
        
        if context.scene.hvym_daemon_running == True:
            call_cli(['icp-stop-assets'])
            context.scene.hvym_debug_url = ''
        elif context.scene.hvym_daemon_running == False:
            wm.progress_begin(0, 88)
            wm.progress_update(88)
            project_type = context.scene.hvym_project_type
            output = run_futures_cmds([CLI+f' icp-start-assets {project_type}'])
            wm.progress_update(88)
            wm.progress_end()
            print(output)
            print('------------------------------------')

        context.scene.hvym_daemon_running = not context.scene.hvym_daemon_running


        return {'FINISHED'}


class HVYM_ToggleMinterDaemon(bpy.types.Operator):
    bl_idname = "hvym_toggle_minter.daemon"
    bl_label = "Toggle the test daemon."
    bl_description ="Enables and disables the minter daemon for testing."
    bl_options = {'REGISTER'}

    def execute(self, context):
        wm = bpy.context.window_manager
        
        if context.scene.hvym_daemon_running == True:
            call_cli(['icp-stop-assets'])
            context.scene.hvym_debug_url = ''
        elif context.scene.hvym_daemon_running == False:
            wm.progress_begin(0, 88)
            wm.progress_update(88)
            output = run_futures_cmds([CLI+' icp-start-assets'])
            wm.progress_update(88)
            wm.progress_end()
            print(output)
            print('------------------------------------')

        context.scene.hvym_daemon_running = not context.scene.hvym_daemon_running


        return {'FINISHED'}

class HVYM_OpenDebugUrl(bpy.types.Operator):
    bl_idname = "hvym_open_debug.url"
    bl_label = "Open Debug URL."
    bl_description ="Open the currently active debug url.."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Open Url")
        webbrowser.open(context.scene.hvym_debug_url)
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
            row.prop(item, "menu_alignment")
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


class HVYM_NLA_DataPanel(bpy.types.Panel):
    """Creates a New Tab & Panel in the Action Editor"""
    bl_label = "Heavymeta Standard Data"
    bl_idname = "OBJECT_PT_heavymeta_standard_data"
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Heavy Meta' # This will create a new tab in the Action editor with this name
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob is not None and ob.animation_data is not None and ob.animation_data.nla_tracks is not None and len(ob.animation_data.nla_tracks.keys())>0 and ob.animation_data.nla_tracks.active is not None)

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
        ctx = context.scene
        row.separator()
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="Action:")
        row = box.row()
        row.template_list("HVYM_UL_DataList", "", ctx,
                          "hvym_action_meta_data", ctx, "hvym_action_list_index")
        row = box.row()
        row.operator('hvym_meta_data.new_action_property_item', text='+', icon='DRIVER_TRANSFORM')
        row.operator('hvym_meta_data.new_action_mesh_property_item', text='+', icon='MESH_ICOSPHERE')
        row.operator('hvym_meta_data.delete_nav_item', text='', icon='CANCEL')
        if ctx.hvym_action_list_index >= 0 and ctx.hvym_action_meta_data:
            item = ctx.hvym_action_meta_data[ctx.hvym_action_list_index]
            row = box.row()
            row.prop(item, "type")
            box = col.box()
            row = box.row()
            row.separator()
            row.label(text="Tracks:")
            row = box.row()
            row.template_list("HVYM_UL_StringSetList", "", item,
                        "action_set", item, "set_index")
            row = box.row()
            row.operator('hvym_meta_data.add_track_to_property_item', text='', icon='ADD')
            row.operator('hvym_meta_data.delete_track_from_property_item', text='', icon='REMOVE')
            row.operator('hvym_meta_data.set_track_direction_up', text='', icon='SORT_DESC')
            row.operator('hvym_meta_data.set_track_direction_down', text='', icon='SORT_ASC')
            row = box.row()
            if item.trait_type == 'action':
                row.prop(item, "anim_interaction_type")
            elif item.trait_type == 'mesh_action':
                row.prop(item, "model_ref")
                row = box.row()
                row.prop(item, "mesh_interaction_type")
            row = box.row()
            row.prop(item, "sequence_type")
            row.prop(item, "additive")
            

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
        row.separator()
        box = col.box()
        row = box.row()
        row.separator()
        row.label(text="NFT Data:")
        row = box.row()
        row.template_list("HVYM_UL_DataList", "", ctx,
                          "hvym_meta_data", ctx, "hvym_list_index")

        row = box.row()
        row.operator('hvym_meta_data.new_property_item', text='+', icon='FUND')
        row.operator('hvym_meta_data.new_call_item', text='+', icon='SETTINGS')
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
            if item.trait_type != 'call':
                row.prop(item, GetPropWidgetType(item))
                row.prop(item, "show")
                row = box.row()
            if item.trait_type == 'property':
                row.prop(item, "prop_value_type")
                row.prop(item, "prop_action_type")
                row.prop(item, "prop_immutable")
                row = box.row()
                if item.prop_value_type == 'Int':
                    row.prop(item, "int_default")
                    row.prop(item, "int_min")
                    row.prop(item, "int_max")
                    if item.prop_action_type != 'Static':
                        row.prop(item, "int_amount")
                elif item.prop_value_type == 'Float':
                    row.prop(item, "float_default")
                    row.prop(item, "float_min")
                    row.prop(item, "float_max")
                    if item.prop_action_type != 'Static':
                        row.prop(item, "float_amount")
            elif item.trait_type == 'call':
                row = box.row()
                row.prop(item, "call_param")
                row = box.row()
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
                row.prop(item, "anim_weight")
                row.prop(item, "anim_play")
            elif item.trait_type == 'mat_prop':
                row.prop(item, "mat_ref")
                row = box.row()
                row.prop(item, "mat_reflective")
                row.prop(item, "mat_iridescent")
            elif item.trait_type == 'mat_set':
                row.prop(item, "material_id")
                row = box.row()
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
        box = col.box()
        row = box.row()
        
        if ctx.hvym_list_index >= 0 and ctx.hvym_meta_data:
            item = ctx.hvym_meta_data[ctx.hvym_list_index]
            row.label(text="Property Names:")
            row = box.row()
            row.prop(item, "value_prop_label")
            row = box.row()
            row.prop(item, "mesh_prop_label")
            row = box.row()
            row.prop(item, "mat_prop_label")
            row = box.row()
            row.prop(item, "anim_prop_label")
            row = box.row()
            row.prop(item, "mesh_set_label")
            row = box.row()
            row.prop(item, "morph_set_label")
            row = box.row()
            row.prop(item, "mat_set_label")




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
        filter_props = ['hvym_mintable','hvym_daemon_running','hvym_contract_address','hvym_prem_nft_price','hvym_nft_price','hvym_export_name','hvym_export_path','hvym_project_name','hvym_project_path','hvym_daemon_path','hvym_project_type','hvym_debug_url']
        col = self.layout.column()
        box = col.row()
        row = box.row()
        row.operator('hvym_data.reload', text='', icon='FILE_REFRESH')
        box = col.row()
        row = box.row()
        row.separator()
        row.prop(context.scene, 'hvym_mintable')
        if context.scene.hvym_mintable:
            for (prop_name, _) in PROPS:
                row = col.row()
                if prop_name == 'minter_version':
                    row = row.row()
                    row.enabled = context.scene.add_version
                if context.scene.hvym_nft_chain == 'ICP' or context.scene.hvym_nft_chain == 'AR':
                    if prop_name not in filter_props:
                        row.prop(context.scene, prop_name)
        row = col.row()
        box = col.box()
        row = box.row()
        row.label(text="Project Settings:")
        row = box.row()
        row.prop(context.scene, 'hvym_project_name')
        row = box.row()
        row.prop(context.scene, 'hvym_project_type')
        row = box.row()
        row.operator('hvym_set.project_confirm_dialog', text="Set Project", icon="CONSOLE")
        row = box.row()
        row.label(text="Internet Computer Project Path:")
        row = box.row()
        row.label(text=context.scene.hvym_project_path)
        row = box.row()
        row.label(text=context.scene.hvym_daemon_path)
        box = col.row()
        row = box.row()
        row.separator()
        box = col.box()
        row = box.row()
        row.label(text="Debugging:")
        row = box.row()
        if context.scene.hvym_daemon_running == False:
            row.operator('hvym_toggle_asset.daemon', text="Daemon Off", icon="COLORSET_01_VEC")
        elif context.scene.hvym_daemon_running == True:
            row.operator('hvym_toggle_asset.daemon', text="Daemon On", icon="COLORSET_03_VEC")
            row = box.row()
            if context.scene.hvym_project_type == 'minter':
                row.operator('hvym_debug.minter', text="Debug Minter", icon="CONSOLE")
            elif context.scene.hvym_project_type == 'model':
                row.operator('hvym_debug.model_confirm_dialog', text="Debug Model", icon="CONSOLE")
        row = box.row()
        if context.scene.hvym_debug_url != '':
            row.prop(context.scene, 'hvym_debug_url')
            row = box.row()
            row.operator('hvym_open_debug.url', text="Debug URL", icon="URL")
        box = col.box()
        row = box.row()
        row.prop(context.scene, 'hvym_export_name')
        row = box.row()
        row.prop(context.scene, 'hvym_export_path')
        if context.scene.hvym_mintable:
            box = col.box()
            row = box.row()
            row.separator()
            row.label(text="Deploy:")
            row = box.row()
            row.operator('hvym_deploy.confirm_minter_deploy_dialog', text="Deploy Minter", icon="URL")
            # row = box.row()
            # row.operator('hvym_deploy.confirm_nft_deploy_dialog', text="Deploy NFT", icon="URL")
        



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
class HVYMGLTF_PT_export_user_extensions(bpy.types.Panel):
    bl_id = 'HVYMGLTF_PT_export_user_extensions'
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Heavymeta Extensions"
    bl_parent_id = "FILE_PT_operator"

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
    layout.operator(HVYM_AddAllMeshMaterialsToSet.bl_idname, icon_value=logo.icon_id)

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
        ob = context.active_object
        return (ob is not None and ob.animation_data.action is not None)

    def execute(self, context):
        ob = context.active_object
        ad = ob.animation_data
        active_action = ob.animation_data.action

        if ob != None and active_action != None and has_hvym_data('anim', active_action.name) == False:
            item = context.collection.hvym_meta_data.add()
            item.trait_type = 'anim'
            item.values = 'Animation Property'
            item.type = active_action.name
            item.anim_start = active_action.frame_start
            item.anim_end = active_action.frame_end
            item.anim_blending = ad.action_blend_type
            item.model_ref = ob
            UpdateAnimData(context)
            updateNftData(context)

        else:
            print("Item already exists in data.")

        return {'FINISHED'}


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
            if has_hvym_data('mat_prop', matName) == False:
                item = context.collection.hvym_meta_data.add()
                item.trait_type = 'mat_prop'
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
            if has_hvym_data('mat_prop', matName) == False:
                item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
                if item.trait_type == 'mat_set':
                    mat_item = item.mat_set.add()
                    item.values = 'Material Set'
                    mat_item.mat_ref = bpy.data.materials[matName]
                    RebuildMaterialSets(context)
                    
            else:
                print("Item already exists in data.")
    

        return {'FINISHED'}

class HVYM_AddAllMeshMaterialsToSet(bpy.types.Operator):
    """Add all materials in mesh to the Heavymeta Data list."""
    bl_idname = "hvym_add.all_materials_to_set"
    bl_label = "Add All Material Data to Set"

    @classmethod
    def poll(cls, context):
        if isinstance(context.space_data, bpy.types.SpaceOutliner) and context.active_object.type == 'MESH':
            if context.active_object is not None and context.selected_ids[0].bl_rna.identifier == 'Object':
                return True

    def execute(self, context):
        obj = context.active_object
        for slot in obj.material_slots:
            matName  = slot.material.name
            if matName != None:
                if has_hvym_data('material', matName) == False:
                    item = context.collection.hvym_meta_data[context.collection.hvym_list_index]
                    if item.trait_type == 'mat_set':
                        mat_item = item.mat_set.add()
                        item.values = 'Material Set'
                        mat_item.mat_ref = slot.material
                    RebuildMaterialSets(context)
                    
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
    HVYM_StringSet,
    HVYM_MeshSet,
    HVYM_MaterialSet,
    HVYM_MorphSet,
    HVYM_ActionDataItem,
    HVYM_DataItem,
    HVYM_UL_DataList,
    HVYM_UL_StringSetList,
    HVYM_UL_MeshSetList,
    HVYM_UL_MaterialSetList,
    HVYM_UL_MorphSetList,
    HVYM_MENU_NewMenuTransform,
    HVYM_LIST_AddTrackToActionProp,
    HVYM_LIST_DeleteTrackFromActionProp,
    HVYM_LIST_MoveTrack,
    HVYM_LIST_TrackDirectionUp,
    HVYM_LIST_TrackDirectionDown,
    HVYM_LIST_NewActionPropItem,
    HVYM_LIST_NewActionMeshPropItem,
    HVYM_LIST_DeleteActionItem,
    HVYM_LIST_NewPropItem,
    HVYM_LIST_NewCallItem,
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
    HVYM_DebugModelConfirmDialog,
    HVYM_SetProject,
    HVYM_SetConfirmDialog,
    HVYM_ToggleAssetDaemon,
    HVYM_OpenDebugUrl,
    HVYM_DataReload,
    HVYM_ExportHelper,
    HVYM_DeployMinter,
    HVYM_DeployConfirmMinterDeployDialog,
    HVYM_DeployNFT,
    HVYM_DeployConfirmNFTDeploytDialog,
    HVYM_Menu_Transform_Panel,
    HVYM_NLA_DataPanel,
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
    HVYM_AddMaterialToSet,
    HVYM_AddAllMeshMaterialsToSet
    ]

@persistent
def post_file_load(file_path):
    if bpy.context.scene.hvym_project_name == 'NOT-SET!!!!':
        return

    if CLI_INSTALLED and ( bpy.context.scene.hvym_project_path != "NOT-SET!!!!" or bpy.context.scene.hvym_project_path != ICP_PATH):
        print(f"Heavymeta CLI current project is: {ICP_PATH}!!, being changed to: {bpy.context.scene.hvym_project_name}")
        bpy.ops.hvym_set.project()


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

    # BlenderNode.create_object = patched_create_object

    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for (prop_name, prop_value) in COL_PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    
    bpy.types.Scene.hvym_collections_data = bpy.props.PointerProperty(type=HVYM_NFTDataExtensionProps)
    bpy.types.Scene.hvym_menu_meta_data = bpy.props.CollectionProperty(type = HVYM_MenuDataItem)
    bpy.types.Scene.hvym_action_meta_data = bpy.props.CollectionProperty(type = HVYM_ActionDataItem)
    bpy.types.Scene.hvym_action_list_index = bpy.props.IntProperty(name = "Index for active hvym_action_meta_data", default = 0)
    bpy.types.Collection.hvym_meta_data = bpy.props.CollectionProperty(type = HVYM_DataItem)
    bpy.types.Collection.hvym_menu_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data menus", default = -1)
    bpy.types.Object.hvym_menu_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data menus", default = -1)
    bpy.types.Object.hvym_menu_id = bpy.props.StringProperty(name = "Unique id for menu derived from collection id", default='')
    bpy.types.Collection.hvym_list_index = bpy.props.IntProperty(name = "Index for active hvym_meta_data", default = 0)
    bpy.types.Collection.hvym_nft_chain_enum = bpy.props.StringProperty(name = "Used to set chain enum on import", default='ICP')
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

    bpy.app.handlers.load_post.append(post_file_load)


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Scene.hvym_collections_data
    del bpy.types.Scene.hvym_menu_meta_data
    del bpy.types.Scene.hvym_action_meta_data
    del bpy.types.Scene.hvym_action_list_index
    del bpy.types.Collection.hvym_meta_data
    del bpy.types.Collection.hvym_menu_index
    del bpy.types.Object.hvym_menu_index
    del bpy.types.Object.hvym_menu_id
    del bpy.types.Collection.hvym_list_index
    del bpy.types.Collection.hvym_nft_chain_enum
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

        gltf2_object.extensions[glTF_extension_name] = self.Extension(
            name=glTF_extension_name,
            extension={
                "foo": 1.5
            },
            required=False
        )


    def gather_gltf_extensions_hook(self, gltf2_object, export_settings):

        ctx = bpy.context.scene

        if ctx.hvym_collections_data.enabled:
            data = {}

            for id in ctx.hvym_collections_data.nftData.keys():
                data[id] = ctx.hvym_collections_data.nftData[id].to_dict()
                            
            gltf2_object.extensions[glTF_extension_name] = data