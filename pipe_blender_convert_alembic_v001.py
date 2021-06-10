import os
import bpy
import json

# GET VARIABLES
file_abc = os.getenv('PIPE_ALEMBIC')
dir_out = os.getenv('PIPE_OUTPUT')
animation = os.getenv('PIPE_ANIMATION')

python_root = os.getenv('PIPE_PYTHON_ROOT')
root = os.getenv('PIPE_ROOT')
project = os.getenv('PIPE_PROJECT')
project_abbr = os.getenv('PIPE_PROJECT_ABBR')
asset = os.getenv('PIPE_ASSET')

# DELETE OLD COLLECTIONS AND SCENES
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # bpy.data.objects.remove(obj)
        try:
            bpy.data.meshes.remove(bpy.data.meshes[obj.name])
        except KeyError:
            pass
    elif obj.type == 'CAMERA':
        bpy.data.cameras.remove(bpy.data.cameras[obj.name])
        pass
    elif obj.type == 'LIGHT':
        bpy.data.lights.remove(bpy.data.lights[obj.name])

for col in bpy.data.collections:
    bpy.data.collections.remove(col)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)
for world in bpy.data.worlds:
    bpy.data.worlds.remove(world)

# OPEN ALEMBIC
bpy.ops.wm.alembic_import(filepath=file_abc, filter_alembic=True, relative_path=False, scale=1.0, set_frame_range=True,
                          as_background_job=False)

# OPEN CONFIGURATION FILE REGARDING MODEL SUBDIVISION
file_config_sd = os.path.join(python_root, 'projects', f'{project}-{project_abbr}', 'config_subdivision.json')
with open(file_config_sd, 'r') as json_file:
    dict_sd = json.load(json_file)['subdivision']

# RENAMING
objects = [[x, x.name] for x in bpy.data.objects if asset in x.name]

for obj, name in objects:
    name_mod_0 = name.split(':')[1] if ':' in name else name
    name_mod_1 = name_mod_0.replace('___', '_*_')

    letters = []
    underscores = 0
    if '.' not in name_mod_1:
        for i, letter in enumerate(name_mod_1):
            if letter == '_':
                if underscores in [0, 1]:
                    letter = '.'
                elif name_mod_1[i + 1:-1] == 'sd':
                    letter = '.'
                underscores = underscores + 1
            letters.append(letter)

        name_mod_2 = ''.join(letters)
    else:
        name_mod_2 = name_mod_1
    obj.name = name_mod_2

    # Add subdivision modifiers
    if name_mod_2.split('.')[-1][0:2] == 'sd':
        sd_level = int(name_mod_2.split('.')[-1][2:])
        bpy.context.view_layer.objects.active = obj

        if sd_level != 0 and 'Subdivision' not in [x.name for x in bpy.context.object.modifiers]:
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].render_levels = sd_level
            if sd_level > 2:
                bpy.context.object.modifiers["Subdivision"].levels = dict_sd["preview_limit"]
            else:
                bpy.context.object.modifiers["Subdivision"].levels = sd_level

            bpy.context.object.modifiers["Subdivision"].uv_smooth = dict_sd["uv_smooth"]
            bpy.context.object.modifiers["Subdivision"].use_creases = dict_sd["use_creases"]

# Assign objects to invisible collection
asset_collections = [x for x in bpy.data.collections if asset in x.name]
if len(asset_collections) == 0:
    collection = bpy.data.collections.new(asset)
else:
    collection = asset_collections[0]
collection.use_fake_user = True

for obj in [x for x in bpy.context.view_layer.objects if asset in x.name]:
    if obj.name not in [x.name for x in collection.objects]:
        collection.objects.link(obj)

file_blend = os.path.join(dir_out, f'{animation}.blend')
bpy.ops.wm.save_as_mainfile(filepath=file_blend, copy=True)
