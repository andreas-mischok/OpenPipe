import os
import bpy
import json

root = os.getenv('PIPE_ROOT')
project = os.getenv('PIPE_PROJECT')
department = os.getenv('PIPE_DEPARTMENT')
discipline = os.getenv('PIPE_DISCIPLINE')
asset = os.getenv('PIPE_ASSET')
user = os.getenv('PIPE_USER')


def gather_variation_combinations():
    global root, project, asset
    dir_asset = os.path.join(root, project, 'build', asset)
    dir_pipe = os.path.join(dir_asset, '.pipeline')

    dir_pipe_txt = os.path.join(dir_pipe, 'txt')

    txt_variations = os.listdir(dir_pipe_txt)

    dir_pipe_mdl = os.path.join(dir_pipe, 'mdl')
    file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')
    with open(file_mdl_package, 'r') as json_file:
        dict_mdl_package = json.load(json_file)

    dict_mdl_variations = dict_mdl_package["variations"]
    #mdl_variations = [key for key in dict_mdl_variations]

    initialise_texture_variation(dir_asset, dict_mdl_package, dict_mdl_variations, txt_variations[0], dir_pipe_txt)
    # TODO check if files and directories even exist.


def initialise_texture_variation(dir_asset, dict_mdl_package, dict_mdl_variations, txt_variation, dir_pipe_txt):
    global root, project, asset, discipline

    mdl_version = dict_mdl_package[discipline]
    dir_mdl_version = os.path.join(dir_asset, 'mdl', '.pantry', mdl_version)
    blend_mdl_version = os.path.join(dir_mdl_version, f'{asset}.blend')
    blend_mdl_collection = os.path.join(blend_mdl_version, 'Collection', asset)
    #blend_mdl_collection = os.path.join(blend_mdl_version, 'Object', "*")

    print(blend_mdl_collection)
    bpy.ops.wm.append(directory=f'{blend_mdl_version}\\Collection\\', filepath=f'{asset}.blend', filename=asset,
                      autoselect=True)
    objects = [x for x in bpy.context.selected_objects]

    # link to main scene collection instead of sub-collection
    for col in bpy.data.collections:
        if asset in col.children:
            col.children.unlink(bpy.data.collections[asset])
    bpy.context.scene.collection.children.link(bpy.data.collections[asset])

    #for obj in objects:

    # Create collections and scenes for model variations
    mdl_variations_of_txt_var = [key for key in dict_mdl_variations
                                 if txt_variation in dict_mdl_variations[key] or
                                 '*' in dict_mdl_variations[key]]
    print(mdl_variations_of_txt_var)

    # CREATE COLLECTIONS AND SCENES
    for mdl_var in mdl_variations_of_txt_var:
        scene_var = bpy.data.scenes.new(mdl_var)

        new_col = bpy.data.collections.new(mdl_var)
        new_col.use_fake_user = True

        scene_var.collection.children.link(new_col)
    # TODO create scenes


    # TODO remove empty collections
    # TODO bpy.context replace for context from script

    # TODO assign variation based invisible collections

    # ADD VERSION NUMBER TO COLLECTION NAME
    bpy.data.collections[asset].name = f'{asset}.{mdl_version}'

    # CREATE DEFAULT MATERIAL
    mat = bpy.data.materials.new(name=f'{asset}.{txt_variation}.main')
    mat.use_nodes = True
    #mat.node_tree.new()
    #setattr(bpy.data.materials[mat],"use_vertex_color_paint",True)


    #mat = bpy.data.materials.get('tst')


    # ASSIGN COLLECTIONS, SCENES AND MATERIAL
    for obj in objects:
        obj_mdl_var = [x for x in obj.name.split('.')[1]]
        mdl_var_overlap = [x for x in obj_mdl_var if x in mdl_variations_of_txt_var]
        if '*' in obj_mdl_var or len(mdl_var_overlap) != 0:
            # ASSIGN OBJECTS TO MODEL VARIATION COLLECTIONS
            if '*' in obj_mdl_var:
                for mdl_var in mdl_variations_of_txt_var:
                    bpy.data.collections[mdl_var].objects.link(obj)
                # TODO assign to all collections
            elif len(mdl_var_overlap) != 0:
                for mdl_var in mdl_var_overlap:
                    bpy.data.collections[mdl_var].objects.link(obj)
                # TODO assign to all specific collections

            # ASSIGN MATERIAL
            if obj.data.materials:
                for i, material_slot in enumerate(obj.data.materials):
                    obj.data.materials[i] = mat
            else:
                obj.data.materials.append(mat)
        else:
            obj.hide_set(True)

    # CONNECTIONS FILE
    # READ FILE
    file_connections = os.path.join(dir_pipe_txt, txt_variation, 'txt_connections.json')
    with open(file_connections, 'r') as json_file:
        dict_connections = json.load(json_file)

    #active_connections = [key for key in dict_connections if len(dict_connections[key]) != 0]
    #print(active_connections)

    dir_txt_package = os.path.join(dir_pipe_txt, txt_variation, 'txt_package')

    """
    (0, 'Base Color')
    (1, 'Subsurface')
    (2, 'Subsurface Radius')
    (3, 'Subsurface Color')
    (4, 'Metallic')
    (5, 'Specular')
    (6, 'Specular Tint')
    (7, 'Roughness')
    (8, 'Anisotropic')
    (9, 'Anisotropic Rotation')
    (10, 'Sheen')
    (11, 'Sheen Tint')
    (12, 'Clearcoat')
    (13, 'Clearcoat Roughness')
    (14, 'IOR')
    (15, 'Transmission')
    (16, 'Transmission Roughness')
    (17, 'Emission')
    (18, 'Alpha')
    (19, 'Normal')
    (20, 'Clearcoat Normal')
    (21, 'Tangent')
    """
    count = 0
    if dict_connections["base_color"] != "":
        clr_channel = dict_connections["base_color"]
        dir_channel_textures = get_channel_dir(dir_asset, dir_txt_package, txt_variation, clr_channel)
        load_texture(dir_channel_textures, mat, 0, count)
        count +=1
    else:
        print('skip clr ')

    if dict_connections["metallic"] != "":
        mtl_channel = dict_connections["metallic"]
        dir_channel_textures = get_channel_dir(dir_asset, dir_txt_package, txt_variation, mtl_channel)
        load_texture(dir_channel_textures, mat, 4, count)
        count +=1
    else:
        print('skip mtl ')

    if dict_connections["specular_roughness"] != "":
        spr_channel = dict_connections["specular_roughness"]
        dir_channel_textures = get_channel_dir(dir_asset, dir_txt_package, txt_variation, spr_channel)
        load_texture(dir_channel_textures, mat, 7, count)
        count +=1
    else:
        print('skip roughness ')

    if dict_connections["normal"] != "":
        nrm_channel = dict_connections["normal"]
        dir_channel_textures = get_channel_dir(dir_asset, dir_txt_package, txt_variation, nrm_channel)
        load_texture(dir_channel_textures, mat, 20, count)
        count += 1
    else:
        print('nrm roughness ')

    # EMI
    # TRANSIMISSION
# TODO use_nodes=True makes texture inaccessible via UI


def get_channel_dir(dir_asset, dir_txt_package, txt_variation, channel):
    global discipline
    channels_json = [x for x in os.listdir(dir_txt_package)
                     if os.path.isfile(os.path.join(dir_txt_package, x))]

    channels_json_native = [x for x in channels_json
                            if os.path.isdir(os.path.join(dir_txt_package, x.split('.')[0]))]
    # channels_json_external = [x for x in channels_json if x not in channels_json_native]

    file_channel = os.path.join(dir_txt_package, f'{channel}.json')

    # Modify source file
    if channel not in [x.split('.')[0] for x in channels_json_native]:
        with open(file_channel, 'r') as json_file:
            dict_external = json.load(json_file)

        src_asset = dict_external["asset"]
        txt_variation = dict_external["variation"]
        channel = dict_external["channel"]

        global root, project
        dir_txt_package = os.path.join(root, project, 'build', src_asset, '.pipeline', 'txt',
                                       txt_variation, 'txt_package')
        file_channel = os.path.join(dir_txt_package, f'{channel}.json')

    with open(file_channel, 'r') as json_file:
        dict_channel = json.load(json_file)

    file_channel_version = os.path.join(dir_txt_package, channel, f'{channel}.{dict_channel[discipline]}.json')

    with open(file_channel_version, 'r') as json_file:
        dict_channel_version = json.load(json_file)

    dir_channel_textures = os.path.join(dir_asset, 'txt', '.pantry', txt_variation, channel,
                                        dict_channel_version["channel_version"])

    return dir_channel_textures


def load_texture(dir_textures, mat, slot, count):
    textures = os.listdir(dir_textures)
    # TODO split by filetype
    tmp = [x.split('.')[-1] for x in textures]# if x.split('.')[-1] not in filetypes]
    filetypes = list(set(tmp))

    if 'tx' in filetypes:
        filetype = 'tx'
    elif 'exr' in filetypes:
        filetype = 'exr'
    elif 'tif' in filetypes:
        filetype = 'tif'
    elif 'tiff' in filetypes:
        filetype = 'tiff'
    elif 'png' in filetypes:
        filetype = 'png'
    else:
        filetype = filetypes[0]

    textures_of_filetype = [x for x in textures if x.split('.')[-1] == filetype]

    # Set variables for import of textures
    filepath = os.path.join(dir_textures, textures_of_filetype[0])
    files = [{"name": texture} for texture in textures_of_filetype]
    # Import textures
    bpy.ops.image.open(filepath=filepath, directory=dir_textures, files=files, relative_path=False, show_multiview=False)
    texture_import = bpy.data.images[textures_of_filetype[0]]#([x.name for x in bpy.data.images])

    colour_space = textures_of_filetype[0].split('.')[1]
    spaces = [x.name for x in
              type(texture_import).bl_rna.properties['colorspace_settings'].fixed_type.properties['name'].enum_items]
    if colour_space in spaces:
        texture_import.colorspace_settings.name = colour_space

    # Create New Texture node
    material_nodes = mat.node_tree.nodes
    texture_node = material_nodes.new("ShaderNodeTexImage")
    texture_node.location = (-550, 420 + count * -280)
    texture_node.image = texture_import

    # Connect Texture
    shader_node = material_nodes["Principled BSDF"]
    if slot != 20:
        mat.node_tree.links.new(texture_node.outputs[0], shader_node.inputs[slot])
    else:
        normal_node = material_nodes.new("ShaderNodeNormalMap")
        normal_node.location = (-300, 420 + count * -280)
        mat.node_tree.links.new(texture_node.outputs[0], normal_node.inputs[1])
        mat.node_tree.links.new(normal_node.outputs[0], shader_node.inputs[slot])

    #material_nodes["Principled BSDF"].inputs[0].link(texture_node)


# TODO how can I smartly deal with material overrides? (for other texture variations)

#bpy.ops.object.make_override_library()
#print([x.name for x in bpy.data.collections])
#print(asset)
#print([x for x in bpy.data.collections[asset].objects])
#bpy.data.collections[asset].name = 'AAA'#f'{asset}.{mdl_version}
#bpy.data.collections['Collection'].name = 'AAA'#f'{asset}.{mdl_version}'
#bpy.data.collections['prpChair2'].name = 'AAB'#f'{asset}.{mdl_version}'
# No need to rename, link contains the version
'''print([x.name for x in bpy.data.collections])
for x in bpy.data.collections:
    if x.name == asset:
        x.name = f'{asset}.{mdl_version}'
print([x.name for x in bpy.data.collections])'''


#for col in bpy.data.collections:
#    col.name = 'AA'


gather_variation_combinations()

