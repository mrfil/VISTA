# File to generate a blender FBX from the SEEG data
# Load libraries
import argparse
import os
import bpy
from random import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as signal
from sklearn.preprocessing import normalize


def generate_fbx(obj_directory, out_name):
    def delete_object(obj_name):
        object_to_delete = bpy.data.objects[obj_name]
        bpy.data.objects.remove(object_to_delete, do_unlink=True)

    delete_object('Cube')
    delete_object('Camera')
    delete_object('Light')


    for filename in os.listdir(obj_directory):
        f = os.path.join(obj_directory, filename)
        # checking if it is a file
        obj = None
        mat = None
        fname = None
        if os.path.isfile(f):
            # isolate the filename as it is the object name
            fname = os.path.splitext(f)[0]
            fname = fname.rsplit('/', 1)[1]
            # import obj files
            bpy.ops.import_scene.obj(filepath=f)
            # generate new material
            mat = bpy.data.materials.new(name=fname + '_mat')
            mat.diffuse_color = (random(), random(), random(), 0.1)
            # # activate new material
            obj = bpy.data.objects[fname]
            obj.active_material = mat

        # Apply the transform
        obj.data.update()
        # Resize the object
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    bpy.ops.wm.save_mainfile(filepath=f'{out_name}.blend')
    bpy.ops.export_scene.fbx(filepath=f"{out_name}.fbx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn data into object files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_dir", help="Directory of input object files")
    parser.add_argument("out_name", help="Outfile animation file name")
    args = parser.parse_args()
    generate_fbx(args.in_dir, args.out_name)
