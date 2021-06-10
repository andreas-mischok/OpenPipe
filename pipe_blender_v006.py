import os
import bpy
from bpy.app.handlers import persistent
from mathutils import Euler

import json
from datetime import datetime
from bpy.props import IntProperty, PointerProperty, StringProperty, FloatProperty, BoolProperty, EnumProperty
import string
import math
from collections import Counter

python_root = os.getenv('PIPE_PYTHON_ROOT')
root = os.getenv('PIPE_ROOT')
project = os.getenv('PIPE_PROJECT')
project_abbr = os.getenv('PIPE_PROJECT_ABBR')
department = os.getenv('PIPE_DEPARTMENT')
discipline = os.getenv('PIPE_DISCIPLINE')
asset = os.getenv('PIPE_ASSET')
user = os.getenv('PIPE_USER')

config_file = f'{python_root}/projects/{project}-{project_abbr}/{project}-{project_abbr}.json'
with open(config_file, 'r') as json_content:
    dict_project_config = json.load(json_content)

dir_asset = str(os.path.join(root, project, 'build', asset))
dir_pipe = str(os.path.join(dir_asset, '.pipeline'))
dir_pipe_mdl = str(os.path.join(dir_pipe, 'mdl'))
dir_pipe_txt = str(os.path.join(dir_pipe, 'txt'))
dir_pipe_shd = str(os.path.join(dir_pipe, 'shd'))
dir_pipe_anm = str(os.path.join(dir_pipe, 'anm'))
dir_mdl = str(os.path.join(dir_asset, 'mdl'))
dir_txt = str(os.path.join(dir_asset, 'txt'))
dir_shd = str(os.path.join(dir_asset, 'shd'))

bl_info = {
    "name": "Open Pipeline Addon",
    "blender": (2, 91, 0),
    "category": "Pipeline",
}


def get_list_variations(variations):
    variations = variations.replace(' ', '')
    if ',' in variations:
        list_variations = variations.split(',')
    else:
        list_variations = [variations]
    return list_variations


def create_get_asset_collection():
    global asset
    if asset in bpy.data.collections:
        return bpy.data.collections[asset]
    else:
        collection_asset = bpy.data.collections.new(asset)
        collection_asset.use_fake_user = True
        return collection_asset


def get_all_variations():
    global asset
    prefixes = []
    if asset in bpy.data.collections:
        for obj in bpy.data.collections[asset].objects:
            prefix = [x for x in obj.name.split('.')[1] if x not in prefixes]
            prefixes += prefix
    return prefixes


def add_variation(obj, asset_collection, list_variations, replace_existing):
    if obj.type == 'MESH' or obj.type == 'EMPTY':
        current_name = obj.name
        # If object has previously been assigned to the asset
        if obj.name in [x.name for x in asset_collection.objects]:
            parts = current_name.split('.')
            name_without_prefix = '.'.join(parts[2:])

            if '*' not in list_variations:
                current_variations = [x for x in parts[1]]

                if replace_existing:
                    list_variations_combined = list_variations
                else:
                    if '*' in current_variations:
                        list_variations_combined = ['*']
                    else:
                        list_variations_combined = \
                            list_variations + [x for x in current_variations if x not in list_variations]
                        list_variations_combined.sort()

                prefix = ''.join(list_variations_combined)

                new_name = f'{asset}.{prefix}.{name_without_prefix}'
            else:
                new_name = f'{asset}.*.{name_without_prefix}'

        else:
            if '*' not in list_variations:
                prefix = ''.join(list_variations)
                new_name = f'{asset}.{prefix}.{current_name}'
            else:
                new_name = f'{asset}.*.{current_name}'
            asset_collection.objects.link(obj)

        obj.name = new_name


def remove_obj_from_variations(obj, list_variations, asset_collection, delete_not_remove):
    if obj.type == 'MESH' or obj.type == 'EMPTY':
        current_name = obj.name
        parts = current_name.split('.')
        name_without_prefix = '.'.join(parts[2:])
        current_prefix = parts[1]

        # remove all variations
        if '*' in list_variations:
            obj.name = name_without_prefix
            asset_collection.objects.unlink(obj)

        # Remove specific variations
        else:
            # Remove single from one that is in all
            if '*' == current_prefix:
                if delete_not_remove:
                    new_prefix = '*'
                else:
                    prefixes = get_all_variations()
                    prefixes.sort()
                    new_prefix = ''.join([x for x in prefixes if x not in list_variations
                                          and x != '' and x != '*'])

            # Remove from sparse list
            else:
                new_prefix = ''.join([x for x in current_prefix if x not in list_variations and x != ''])

            if len(new_prefix) > 0:
                obj.name = f'{asset}.{new_prefix}.{name_without_prefix}'
            else:
                obj.name = name_without_prefix
                asset_collection.objects.unlink(obj)


def build_directories():
    global root, project, asset
    dir_pantry = '/'.join([root, project, 'build', asset, 'mdl', '.pantry'])
    existing_versions = [x for x in os.listdir(dir_pantry) if os.path.isdir('/'.join([dir_pantry, x]))]
    if len(existing_versions) == 0:
        version_cur = 'v001'
    else:
        existing_versions.sort()
        latest_existing_version = existing_versions[-1]

        version_cur_int = int(latest_existing_version[1:]) + 1
        version_cur = 'v' + format(version_cur_int, '03d')

    dir_version_cur = '/'.join([dir_pantry, version_cur])
    os.makedirs(dir_version_cur)

    return [dir_pantry, version_cur, dir_version_cur]


def write_json_files(version_cur, publish):
    global dir_pipe_mdl
    dir_pipe_mdl_versions = os.path.join(dir_pipe_mdl, 'versions')

    if os.path.isdir(dir_pipe_mdl_versions):
        existing_versions = [x.split('.')[1] for x in os.listdir(dir_pipe_mdl_versions)]

        if len(existing_versions) > 0:
            existing_versions.sort()
            latest_existing_version = existing_versions[-1]
            version_cur_int = int(latest_existing_version[1:]) + 1
            json_version_cur = 'v' + format(version_cur_int, '03d')
        else:
            json_version_cur = 'v001'
    else:
        json_version_cur = 'v001'
        os.makedirs(dir_pipe_mdl_versions)

    variations = sorted([x for x in get_all_variations() if x != '*'])
    full_path_mdl_version = os.path.join(dir_pipe_mdl_versions, f'{asset}.{json_version_cur}.json')

    dict_version = {
        "artist": user,
        "time": str(datetime.now()).split('.')[0],
        "version": version_cur,
        "published": publish,
        "variations": variations
    }

    with open(full_path_mdl_version, 'w') as json_output:
        json.dump(dict_version, json_output, indent=2)

    full_path_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')
    if os.path.isfile(full_path_mdl_package):
        with open(full_path_mdl_package, 'r') as json_input:
            dict_mdl_var = json.load(json_input)

        dict_mdl_var["mdl"] = json_version_cur
        dict_previous_variations = dict_mdl_var["variations"]
        for variation in variations:
            if variation not in dict_previous_variations:
                dict_previous_variations[variation] = '*'

        dict_mdl_var["variations"] = dict_previous_variations

    else:
        dict_variations = {}
        for var in variations:
            dict_variations[var] = '*'

        dict_mdl_var = {
            "mdl": json_version_cur,
            "mdl_publish": '',
            "txt": '',
            "shd": '',
            "anm": '',
            "variations": dict_variations
        }

    if publish:
        dict_mdl_var["mdl_publish"] = json_version_cur

    with open(full_path_mdl_package, 'w') as json_output:
        json.dump(dict_mdl_var, json_output, indent=2)


def remove_ghosts(context):
    global asset
    if asset in bpy.data.collections:
        asset_collection = bpy.data.collections[asset]
        for obj in asset_collection.objects:
            if obj.name not in [x.name for x in context.scene.objects]:
                asset_collection.objects.unlink(obj)


def create_assign_material(nm, obj):
    mat = bpy.data.materials.get(nm)
    if mat is None:
        mat = bpy.data.materials.new(name=nm)
        mat.use_nodes = True

    if obj.data.materials:
        for i, material_slot in enumerate(obj.data.materials):
            obj.data.materials[i] = mat
    else:
        obj.data.materials.append(mat)


# --- MDL STREAM -------------------------------------------------------------------------------------------------------
class PipeSettingsMdl(bpy.types.PropertyGroup):
    variation: StringProperty(
        name='',
        description='The variation setting is used to determine which packages will be using which geo.'
                    'This is done by assigning them to collections. Geos can be linked to more than one variation.'
                    'The name of each variation is limited to a single letter.\n'
                    'e.g.: A or B\n'
                    'Multiple variations can be assigned at once using an asterisk (assign to all variations) or '
                    'by separating variations with commas.\n'
                    'e.g. * or A, B',
        default='*',
        options={'SKIP_SAVE'})
    # length_max=1)

    spacing: FloatProperty(
        name='Spacing',
        description='Space between variations in the exploded alembic, supplied for baking',
        default=2.0)

    publish: BoolProperty(
        name='publish',
        description='Whether this asset should immediately published',
        default=False,
        options={'SKIP_SAVE'})

    include_hidden: BoolProperty(
        name='include hidden',
        description='Whether hidden objects should be included \n\nCURRENTLY BROKEN',
        default=False,
        options={'SKIP_SAVE'})

    spoiler_var: BoolProperty(
        name='Variation Management',
        default=True)

    spoiler_sub: BoolProperty(
        name='Sub-Collection Management',
        default=False)

# TODO include hidden is broken


class MdlUiVariation(bpy.types.Panel):
    bl_idname = 'PIPE_PT_mdl_variation'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Variation Management")

    def draw(self, context):
        scene = context.scene
        pipe_tool = scene.pipe_tool

        layout = self.layout

        row1 = layout.row()
        #row1.prop(pipe_tool, 'spoiler_var', icon="TRIA_DOWN" if pipe_tool.spoiler_var else "TRIA_RIGHT", emboss=False)
        #if pipe_tool.spoiler_var:

        row0 = layout.row()
        row0.label(text='Model Based')
        #row0.label.alignment('EXPAND')

        box1_row1 = layout.row()
        box1_row1.prop(pipe_tool, 'variation')
        box1_row1.operator('pipe.mdl_variation_set')

        row2 = layout.row()
        row2.operator('pipe.mdl_remove_from')
        row2.operator('pipe.mdl_prefix_add')

        row3 = layout.row()
        #row3.separator()

        row4 = layout.row()
        row4.label(text='Variation Based')

        row5 = layout.row()
        row5.operator('pipe.mdl_delete')
        row5.operator('pipe.mdl_select_exclusive')

        row6 = layout.row()
        row6.separator()


class MdlUiExport(bpy.types.Panel):
    bl_idname = 'PIPE_PT_mdl_export'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 2

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Export")

    def draw(self, context):
        scene = context.scene
        pipe_tool = scene.pipe_tool

        layout = self.layout

        row2 = layout.row()
        row2.prop(pipe_tool, 'spacing')

        row1 = layout.row()
        row1colum1 = row1.column()
        row1colum2 = row1.column()
        row1colum1.prop(pipe_tool, 'publish')
        row1colum2.prop(pipe_tool, 'include_hidden')
        row1colum2.enabled = False

        row3 = layout.row()
        row3.operator('pipe.mdl_export')


class MdlVariationApply(bpy.types.Operator):
    bl_idname = 'pipe.mdl_variation_set'
    bl_label = 'Set'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Sets variations. Drops all previous assignments'

    def execute(self, context):
        remove_ghosts(context)
        global asset
        sel = [x for x in context.selected_objects]  # if x.type == 'MESH']
        pipe_tool = context.scene.pipe_tool
        variations = pipe_tool.variation.upper()
        list_variations = get_list_variations(variations)

        # TODO check for illegal characters
        # check if objects are selected
        if len(sel) == 0:
            self.report({'ERROR'}, 'No objects selected.')
            return {'CANCELLED'}
        else:
            if len(list_variations) == 1 and len(list_variations[0]) == 0:
                self.report({'ERROR'}, 'No variation input given.')
                return {'CANCELLED'}
            else:
                if len([x for x in list_variations if len(x) > 1]) != 0:
                    self.report({'ERROR'}, 'Variation names are limited to a length of one character. '
                                           'If you wish to set multiple variations, separate them by comma')
                    return {'CANCELLED'}
                else:
                    if len([x for x in list_variations if x.isdigit()]) != 0:
                        self.report({'ERROR'}, 'Variation names are limited to a letters.')
                        return {'CANCELLED'}
                    else:
                        # Check if unlinked asset collection exists
                        asset_collection = create_get_asset_collection()

                        for obj in sel:
                            add_variation(obj, asset_collection, list_variations, True)

                        return {'FINISHED'}


class MdlVariationAdd(bpy.types.Operator):
    bl_idname = 'pipe.mdl_prefix_add'
    bl_label = 'Add'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Sets variations. Keeps all previous assignments'

    def execute(self, context):
        remove_ghosts(context)
        global asset
        sel = [x for x in context.selected_objects]
        pipe_tool = context.scene.pipe_tool
        variations = pipe_tool.variation.upper()
        list_variations = get_list_variations(variations)

        # TODO check for illegal characters
        # check if objects are selected
        if len(sel) == 0:
            self.report({'ERROR'}, 'No objects selected.')
            return {'CANCELLED'}
        else:
            if len(list_variations) == 1 and len(list_variations[0]) == 0:
                self.report({'ERROR'}, 'No variation input given.')
                return {'CANCELLED'}
            else:
                if len([x for x in list_variations if len(x) > 1]) != 0:
                    self.report({'ERROR'}, 'Variation names are limited to a length of one character. '
                                           'If you wish to set multiple variations, separate them by comma')
                    return {'CANCELLED'}
                else:
                    if len([x for x in list_variations if x.isdigit()]) != 0:
                        self.report({'ERROR'}, 'Variation names are limited to a letters.')
                        return {'CANCELLED'}
                    else:
                        # Check if unlinked asset collection exists
                        asset_collection = create_get_asset_collection()

                        for obj in sel:
                            add_variation(obj, asset_collection, list_variations, False)

                        return {'FINISHED'}
# TODO convert objects which are included in all into star? (Only if there are more than two variations


class MdlRemoveFrom(bpy.types.Operator):
    bl_idname = 'pipe.mdl_remove_from'
    bl_label = 'Remove from'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Removes the selected objects from the given variations'

    def execute(self, context):
        remove_ghosts(context)
        global asset
        sel = [x for x in context.selected_objects]
        pipe_tool = context.scene.pipe_tool
        variations = pipe_tool.variation.upper()
        list_variations = get_list_variations(variations)

        if len(sel) == 0:
            self.report({'ERROR'}, 'No objects selected.')
            return {'CANCELLED'}
        else:
            for obj in sel:
                if asset in bpy.data.collections:
                    asset_collection = bpy.data.collections[asset]

                    if obj.name in [x.name for x in asset_collection.objects]:
                        remove_obj_from_variations(obj, list_variations, asset_collection, False)

            return {'FINISHED'}


class MdlVariationDelete(bpy.types.Operator):
    bl_idname = 'pipe.mdl_delete'
    bl_label = 'Delete'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = "Deletes the given variation"

    def execute(self, context):
        remove_ghosts(context)
        global asset
        pipe_tool = context.scene.pipe_tool
        variations = pipe_tool.variation.upper()
        list_variations = get_list_variations(variations)
        if asset in bpy.data.collections:
            asset_collection = bpy.data.collections[asset]
            for obj in asset_collection.objects:
                remove_obj_from_variations(obj, list_variations, asset_collection, True)

        return {'FINISHED'}


class MdlSelectExclusive(bpy.types.Operator):
    bl_idname = 'pipe.mdl_select_exclusive'
    bl_label = 'Select'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Selects all objects that belong exclusively to the given variation. ' \
                     'If asterisk (*) is given, it will select the geometry present in all variations.'

    def execute(self, context):
        remove_ghosts(context)
        global asset
        pipe_tool = context.scene.pipe_tool
        variations = pipe_tool.variation.upper()
        list_variations = get_list_variations(variations)

        bpy.ops.object.select_all(action='DESELECT')

        if asset not in bpy.data.collections:
            self.report({'ERROR'}, 'Asset management has not been set up.')
            return {'CANCELLED'}
        else:
            asset_collection = bpy.data.collections[asset]
            all_objects = asset_collection.objects
            if len(all_objects) == 0:
                self.report({'ERROR'}, 'No variations were found.')
                return {'CANCELLED'}
            else:
                invalid_variations = [x for x in list_variations if x not in get_all_variations()]
                if len(invalid_variations) == 0:
                    for obj in all_objects:
                        current_name = obj.name
                        parts = current_name.split('.')
                        current_prefix = parts[1]

                        overlap = [x for x in current_prefix if x in list_variations or '*' == current_prefix]

                        if len(overlap) != 0:
                            obj.select_set(True)
                    return {'FINISHED'}
                else:
                    for invalid in invalid_variations:
                        self.report({'ERROR'}, f'{invalid} is not a valid variation.')
                    return {'CANCELLED'}


def get_all_objects(parent, previous_parents):
    ch_cols = bpy.data.collections[parent].children
    ch_objs = bpy.data.collections[parent].objects

    # previous_parents.append(parent)
    previous_parents = previous_parents + [parent]

    objects = {}

    for obj in ch_objs:
        objects[obj.name] = {
            "object": obj,
            "parents": previous_parents
        }

    if len(ch_cols) != 0:
        for ch_col in ch_cols:
            objects_child = get_all_objects(ch_col.name, previous_parents)
            if len(objects_child) != 0:
                objects.update(objects_child)

    return objects


class MdlExport(bpy.types.Operator):
    bl_idname = 'pipe.mdl_export'
    bl_label = 'Release'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Exports variation collections as separate alembic files. ' \
                     'Deactivated collections are excluded.'

    def execute(self, context):
        remove_ghosts(context)
        global asset
        pipe_tool = context.scene.pipe_tool
        offset = pipe_tool.spacing
        publish = pipe_tool.publish
        include_hidden = (pipe_tool.include_hidden is False)

        if asset not in bpy.data.collections:
            self.report({'ERROR'}, 'Asset management has not been set up.')
            return {'CANCELLED'}
        else:
            asset_collection = bpy.data.collections[asset]
            all_asset_objects = [x for x in asset_collection.objects if x.type == 'MESH']
            if len(all_asset_objects) == 0:
                self.report({'ERROR'}, 'No variations were found.')
                return {'CANCELLED'}

            # ACTUALLY EXPORT
            else:
                # Detect if all objects are named correctly (include asset name)
                collection_objs = get_all_objects(asset, [''])
                objects_with_correct_name = [x for x in collection_objs if asset in x]

                if len(collection_objs) == len(objects_with_correct_name):
                    bpy.ops.object.select_all(action='DESELECT')

                    # Build directories
                    [_, version_cur, dir_version_cur] = build_directories()

                    # JSON FILE CREATION
                    write_json_files(version_cur, publish)

                    # Add subdivision surface modifier level to mesh name
                    for obj in [x for x in bpy.data.objects if asset in x.name]:
                        name_base = obj.name
                        if name_base.split('.')[-1][0:2] == 'sd':
                            name_base = '.'.join(name_base.split('.')[:-1])

                        if obj.name in [x.name for x in bpy.context.view_layer.objects]:
                            bpy.context.view_layer.objects.active = obj
                            if 'Subdivision' in [x.name for x in bpy.context.object.modifiers]:
                                sd_level = str(max([bpy.context.object.modifiers["Subdivision"].render_levels,
                                               bpy.context.object.modifiers["Subdivision"].levels]))
                                obj.name = '.'.join([name_base, f'sd{sd_level}'])

                    bpy.ops.object.select_all(action='DESELECT')

                    # Save blend file
                    full_path_blend = '/'.join([dir_version_cur, f'{asset}.blend'])
                    bpy.ops.wm.save_as_mainfile(filepath=full_path_blend, copy=True)

                    # Get variation combinations
                    collections_variations = []
                    for obj in all_asset_objects:
                        prefix = obj.name.split('.')[1]
                        if prefix not in collections_variations:
                            collections_variations.append(prefix)

                    # Export Alembic 0 - Alternative for blend file
                    for obj in all_asset_objects:
                        if include_hidden:
                            obj.hide_set(False)
                        obj.select_set(True)
                    full_path_abc = '/'.join([dir_version_cur, f'{asset}.abc'])
                    bpy.ops.wm.alembic_export(filepath=full_path_abc, selected=True, uvs=True,
                                              packuv=False, apply_subdiv=False,
                                              face_sets=True, use_instancing=False)
                    # Export Alembic 0 subdivided
                    full_path_abc = '/'.join([dir_version_cur, f'{asset}_subdivided.abc'])
                    bpy.ops.wm.alembic_export(filepath=full_path_abc, selected=True, uvs=True,
                                              packuv=False, apply_subdiv=True,
                                              face_sets=True, use_instancing=False)
                    bpy.ops.object.select_all(action='DESELECT')

                    # Assign material per variation of combinations
                    for variation_combination in collections_variations:
                        nm = '_'.join([x for x in variation_combination])

                        for obj in [x for x in all_asset_objects if x.name.split('.')[1] == variation_combination]:
                            create_assign_material(nm, obj)

                    # Export Alembic 1 - All in one position, split materials
                    for obj in all_asset_objects:
                        obj.select_set(True)
                    full_path_abc_txt_additions = '/'.join([dir_version_cur, f'{asset}_txt_addition_combined.abc'])
                    bpy.ops.wm.alembic_export(filepath=full_path_abc_txt_additions, selected=True, uvs=True, packuv=False,
                                              face_sets=True, use_instancing=False, apply_subdiv=True)

                    # Create offset
                    bpy.ops.object.select_all(action='DESELECT')
                    for variation_combination in collections_variations:
                        for obj in [x for x in all_asset_objects if x.name.split('.')[1] == variation_combination]:
                            prefix = obj.name.split('.')[1]

                            if '*' != prefix:
                                alphabet_index = string.ascii_lowercase.index(prefix[0].lower()) + 1

                                spread = len(prefix) - 1

                                obj.select_set(True)
                                # Move objects according to their variation setting
                                bpy.ops.transform.translate(value=(offset * alphabet_index, offset * spread, 0.0),
                                                            orient_matrix_type='GLOBAL',
                                                            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
                                obj.select_set(False)

                    # Select asset objects
                    for obj in all_asset_objects:
                        obj.select_set(True)

                    # Export 2 and 3: Exploded - With Materials & Exploded without materials
                    full_path_abc_txt_additions_bake = '/'.join(
                        [dir_version_cur, f'{asset}_txt_addition_exploded_bake.abc'])
                    bpy.ops.wm.alembic_export(filepath=full_path_abc_txt_additions_bake, selected=True, uvs=True,
                                              packuv=False, face_sets=True, use_instancing=False, apply_subdiv=True)

                    full_path_abc_txt_exp = '/'.join([dir_version_cur, f'{asset}_txt_replacement_exploded.abc'])
                    bpy.ops.wm.alembic_export(filepath=full_path_abc_txt_exp, selected=True, uvs=True, packuv=False,
                                              face_sets=False, use_instancing=False, apply_subdiv=True)

                    self.report({"WARNING"}, "Models exported successfully. PRESS CTRL + Z ONCE TO UNDO ALL CHANGES.")
                    return {'FINISHED'}

                else:
                    self.report({'ERROR'}, 'Some objects assigned to the asset are not named correctly.')
                    return {'CANCELLED'}


# --- TXT STREAM -------------------------------------------------------------------------------------------------------
class PipeSettingsTxt(bpy.types.PropertyGroup):
    pass


class AllUiTurntable(bpy.types.Panel):
    bl_idname = 'PIPE_PT_all'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 1

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Turntable Setup")

    def draw(self, context):
        global scene_has_been_loaded, scene_has_been_loaded, scene_is_turntable, txt_var

        layout = self.layout
        row0 = layout.row()

        if scene_has_been_loaded is False or (scene_has_been_loaded is True and scene_is_turntable is True):
            scene = context.scene
            pipe_tool_all = scene.pipe_tool_all

            row0.label(text='MDL / ANM')
            row0.prop(pipe_tool_all, "model_selector")

            row1 = layout.row()
            column1 = row1.column()
            column2 = row1.column()
            column1.label(text='TXT Variation')

            if scene_has_been_loaded:
                column2.enabled = False
            column2.prop(pipe_tool_all, "variation_selector")

            row2 = layout.row()
            if scene_has_been_loaded:
                row2.operator('pipe.turntable_update')
            else:
                row2.operator('pipe.turntable_setup')

            row_separator = layout.row()
            row_separator.separator()

            row_title = layout.row()
            row_title.label(text='Rotation')

            row3 = layout.row()
            row3.prop(pipe_tool_all, 'turntable_frames')

            row4 = layout.row()
            row4.prop(pipe_tool_all, 'turntable_yaw_offset')
            row4.prop(pipe_tool_all, 'turntable_pitch_offset')

            row_separator = layout.row()
            row_separator.separator()

            row5 = layout.row()
            if scene_has_been_loaded:
                row5.enabled = False
            row5.prop(pipe_tool_all, 'render_flat_textures')
            if pipe_tool_all.render_flat_textures:
                row5.prop(pipe_tool_all, 'render_shading')

            if pipe_tool_all.render_flat_textures is False or pipe_tool_all.render_shading:
                enabled = True
            else:
                enabled = False
            row_separator = layout.row()
            row_separator.separator()

            # HDRIs
            row_title = layout.row()
            row_title.label(text='HDRIs')

            # HDRI 1
            row_hdri = layout.row()
            row_hdri.prop(pipe_tool_all, 'turntable_hdri_1_bool')
            row_hdri.enabled = enabled
            if pipe_tool_all.turntable_hdri_1_bool:
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_1_selector')
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_1_rotation')
            else:
                row_hdri.label(text='activate to select')

            # HDRI 2
            if len(dict_project_config['hdris']) >= 2:
                row_hdri = layout.row()
                row_hdri.enabled = enabled
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_2_bool')
                if pipe_tool_all.turntable_hdri_2_bool:
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_2_selector')
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_2_rotation')
                else:
                    row_hdri.label(text='activate to select')

            # HDRI 3
            if len(dict_project_config['hdris']) >= 3:
                row_hdri = layout.row()
                row_hdri.enabled = enabled
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_3_bool')
                if pipe_tool_all.turntable_hdri_3_bool:
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_3_selector')
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_3_rotation')
                else:
                    row_hdri.label(text='activate to select')

            # HDRI 4
            if len(dict_project_config['hdris']) >= 4:
                row_hdri = layout.row()
                row_hdri.enabled = enabled
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_4_bool')
                if pipe_tool_all.turntable_hdri_4_bool:
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_4_selector')
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_4_rotation')
                else:
                    row_hdri.label(text='activate to select')

            # HDRI 5
            if len(dict_project_config['hdris']) >= 5:
                row_hdri = layout.row()
                row_hdri.enabled = enabled
                row_hdri.prop(pipe_tool_all, 'turntable_hdri_5_bool')
                if pipe_tool_all.turntable_hdri_5_bool:
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_5_selector')
                    row_hdri.prop(pipe_tool_all, 'turntable_hdri_5_rotation')
                else:
                    row_hdri.label(text='activate to select')

            row_separator = layout.row()
            row_separator.separator()
            row_last = layout.row()

            if scene_has_been_loaded is False:
                row_last.enabled = False

            row_last.operator('pipe.output_directory')
            row_last.operator('pipe.turntable_render')

        else:
            row0.label(text='Tool deactivated')
            row0.enabled = False


def clear_scene():
    bpy.context.scene.name = '.old'

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # bpy.data.objects.remove(obj)
            try:
                bpy.data.meshes.remove(bpy.data.meshes[obj.name])
            except KeyError:
                pass
        elif obj.type == 'CAMERA':
            # print('aaaaa',bpy.data.cameras[obj.name])
            bpy.data.cameras.remove(bpy.data.cameras[obj.name])
            # bpy.data.objects.remove(obj)
            pass
        elif obj.type == 'LIGHT':
            bpy.data.lights.remove(bpy.data.lights[obj.name])

    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

    for world in bpy.data.worlds:
        bpy.data.worlds.remove(world)


class AllTurntableRender(bpy.types.Operator):
    bl_idname = 'pipe.turntable_render'
    bl_label = 'Render'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Renders animation sequence. (CTRL + F12)'

    def execute(self, context):
        # Set output directory
        AllTurntableFunctions().setup_output_directory()
        bpy.ops.render.render(animation=True)
        return {'FINISHED'}


class AllTurntableFunctions:
    def __init__(self):
        pass

    def read_shd_package(self, txt_var):
        dir_pipe_shd_variation = str(os.path.join(dir_pipe_shd, txt_var))
        json_file_package = os.path.join(dir_pipe_shd_variation, 'shd_package.json')

        if os.path.isfile(json_file_package):
            with open(json_file_package, 'r') as json_content:
                dict_shd_package = json.load(json_content)
            active_shd_version = dict_shd_package[discipline]
            json_file_version = os.path.join(dir_pipe_shd_variation, 'versions', f'{asset}.{active_shd_version}.json')

            with open(json_file_version, 'r') as json_content:
                shd_version_blend = json.load(json_content)['version']

            blend_file = os.path.join(dir_shd, '.pantry', txt_var, shd_version_blend, f'{asset}.blend')
            return blend_file, shd_version_blend, active_shd_version
        else:
            return None, None, None

    def copy_ui_settings(self, parent, pipe_tool_all):
        parent.hdri_1_bool = pipe_tool_all.turntable_hdri_1_bool
        parent.hdri_2_bool = pipe_tool_all.turntable_hdri_2_bool
        parent.hdri_3_bool = pipe_tool_all.turntable_hdri_3_bool
        parent.hdri_4_bool = pipe_tool_all.turntable_hdri_4_bool
        parent.hdri_5_bool = pipe_tool_all.turntable_hdri_5_bool

        parent.hdri_1 = pipe_tool_all.turntable_hdri_1_selector
        parent.hdri_2 = pipe_tool_all.turntable_hdri_2_selector
        parent.hdri_3 = pipe_tool_all.turntable_hdri_3_selector
        parent.hdri_4 = pipe_tool_all.turntable_hdri_4_selector
        parent.hdri_5 = pipe_tool_all.turntable_hdri_5_selector

        parent.hdri_1_rotation = pipe_tool_all.turntable_hdri_1_rotation
        parent.hdri_2_rotation = pipe_tool_all.turntable_hdri_2_rotation
        parent.hdri_3_rotation = pipe_tool_all.turntable_hdri_3_rotation
        parent.hdri_4_rotation = pipe_tool_all.turntable_hdri_4_rotation
        parent.hdri_5_rotation = pipe_tool_all.turntable_hdri_5_rotation

        parent.frames = pipe_tool_all.turntable_frames

        parent.asset_yaw = pipe_tool_all.turntable_yaw_offset
        parent.asset_pitch = pipe_tool_all.turntable_pitch_offset

        parent.render_flat_textures = pipe_tool_all.render_flat_textures
        parent.render_shading = pipe_tool_all.render_shading

        parent.mdl = pipe_tool_all.model_selector

    def paste_ui_settings(self, parent, pipe_tool_all):
        pipe_tool_all.turntable_hdri_1_bool = parent.hdri_1_bool
        pipe_tool_all.turntable_hdri_2_bool = parent.hdri_2_bool
        pipe_tool_all.turntable_hdri_3_bool = parent.hdri_3_bool
        pipe_tool_all.turntable_hdri_4_bool = parent.hdri_4_bool
        pipe_tool_all.turntable_hdri_5_bool = parent.hdri_5_bool

        pipe_tool_all.turntable_hdri_1_selector = parent.hdri_1
        pipe_tool_all.turntable_hdri_2_selector = parent.hdri_2
        pipe_tool_all.turntable_hdri_3_selector = parent.hdri_3
        pipe_tool_all.turntable_hdri_4_selector = parent.hdri_4
        pipe_tool_all.turntable_hdri_5_selector = parent.hdri_5

        pipe_tool_all.turntable_hdri_1_rotation = parent.hdri_1_rotation
        pipe_tool_all.turntable_hdri_2_rotation = parent.hdri_2_rotation
        pipe_tool_all.turntable_hdri_3_rotation = parent.hdri_3_rotation
        pipe_tool_all.turntable_hdri_4_rotation = parent.hdri_4_rotation
        pipe_tool_all.turntable_hdri_5_rotation = parent.hdri_5_rotation

        pipe_tool_all.turntable_yaw_offset = parent.asset_yaw
        pipe_tool_all.turntable_pitch_offset = parent.asset_pitch
        pipe_tool_all.turntable_frames = parent.frames

        pipe_tool_all.render_flat_textures = parent.render_flat_textures
        pipe_tool_all.render_shading = parent.render_shading

        pipe_tool_all.model_selector = parent.mdl

    def gather_hdris(self, parent):
        if parent.hdri_1_bool is True:
            parent.hdris.append(parent.hdri_1)
            parent.rotation_offsets.append(parent.hdri_1_rotation)
        if parent.hdri_2_bool is True:
            parent.hdris.append(parent.hdri_2)
            parent.rotation_offsets.append(parent.hdri_2_rotation)
        if parent.hdri_3_bool is True:
            parent.hdris.append(parent.hdri_3)
            parent.rotation_offsets.append(parent.hdri_3_rotation)
        if parent.hdri_4_bool is True:
            parent.hdris.append(parent.hdri_4)
            parent.rotation_offsets.append(parent.hdri_4_rotation)
        if parent.hdri_5_bool is True:
            parent.hdris.append(parent.hdri_5)
            parent.rotation_offsets.append(parent.hdri_5_rotation)

    def setup_output_directory(self):
        global dir_mdl, dir_txt, dir_shd

        if discipline == 'mdl':
            dir_base = dir_mdl
        elif discipline == 'txt':
            dir_base = dir_txt
        else:
            dir_base = dir_shd

        dir_output_base = str(os.path.join(dir_base, 'renders', 'turntables'))
        dir_childs = os.listdir(dir_output_base)
        if len(dir_childs) == 0:
            dir_output_version = str(os.path.join(dir_output_base, 'v001'))
            cur_version = 'v001'
            os.makedirs(dir_output_version)
        else:
            dir_childs.sort()
            latest = dir_childs[-1]

            dir_latest = str(os.path.join(dir_output_base, latest))

            if len(os.listdir(dir_latest)) != 0:
                latest_int = int(latest[1:])
                cur_version = 'v' + format(latest_int + 1, '03d')
                dir_output_version = str(os.path.join(dir_output_base, cur_version))
                os.makedirs(dir_output_version)
            else:
                dir_output_version = dir_latest
                cur_version = latest

        file_output = os.path.join(dir_output_version, f'{asset}.{discipline}.{cur_version}.####')
        bpy.context.scene.render.filepath = file_output

    def update_asset(self, pipe_tool_all):
        global dir_pipe_mdl, txt_var
        txt_var = pipe_tool_all.variation_selector

        mdl_collections = [x for x in bpy.data.collections if x.name.split('.')[0] == asset
                           and x.name.count('.') >= 4]
        if len(mdl_collections) != 0:
            new_col = mdl_collections[0]
        else:
            '''str([x.name.split('.')[2] for x in bpy.data.collections if x.name.split('.')[0] == asset
                           and x.name.count('.') >= 4][0])'''
            # Create New Collection
            asset_collections = [x for x in bpy.data.collections if f'{asset}.*.{txt_var}.mdl.v' in x.name]
            if len(asset_collections) == 0:
                new_col = bpy.data.collections.new(f'{asset}.*.{txt_var}.mdl.v000')
                new_col.use_fake_user = True

                # Assign objects to collection
                objects_of_asset = [x for x in bpy.data.objects if asset in x.name and x.library is None]
                for obj in objects_of_asset:
                    new_col.objects.link(obj)

        # UPDATE ASSET
        remove_empty_collections()
        file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

        with open(file_mdl_package, 'r') as json_file:
            dict_mdl_package = json.load(json_file)
        dict_mdl_variations = dict_mdl_package["variations"]

        selected_model = pipe_tool_all.model_selector
        if selected_model == 'MDL':
            update_model('mdl', dict_mdl_package, dict_mdl_variations)
        else:
            file_anm_package = os.path.join(dir_pipe_anm, selected_model, f'{selected_model}.json')
            print(file_anm_package)
            with open(file_anm_package, 'r') as json_file:
                dict_mdl_package = json.load(json_file)

            update_model(selected_model, dict_mdl_package, dict_mdl_variations)

        update_textures()

        bpy.ops.object.select_all(action='DESELECT')

    def setup_asset_turntable(self, parent, context, pipe_tool_all):
        # Create empty/locator for rotational parent
        empty = bpy.data.objects.new('rotation_parent', None)
        context.scene.collection.objects.link(empty)
        empty.empty_display_type = 'SINGLE_ARROW'
        # empty.empty_display_size = 1
        empty.rotation_mode = 'ZYX'
        pitch = math.radians(90 + parent.asset_pitch)
        empty.rotation_euler = (pitch, 0, 0)
        bpy.context.view_layer.update()

        objects_of_asset = [x for x in bpy.data.objects if asset in x.name and x.library is None]

        #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Parent objects to locator
        for obj in objects_of_asset:
            matrix_copy = empty.matrix_world.inverted() * 0.1
            obj_matrix = obj.matrix_world.copy()

            obj.parent = empty
            #obj.matrix_world = matrix_copy
            #obj.matrix_parent_inverse = matrix_copy
            obj.matrix_world = obj_matrix

        if pipe_tool_all.render_flat_textures and pipe_tool_all.render_shading is False:
            lightrig_rotation_factor = 1
            rotation_iterations = 1
            # frame_length = parent.frames
        else:
            lightrig_rotation_factor = 2
            rotation_iterations = len(parent.hdris)
            # frame_length = parent.frames * 2 * len(parent.hdris)

        frame_length = parent.frames * lightrig_rotation_factor * rotation_iterations
        bpy.context.scene.frame_end = frame_length

        # Setup Object Rotations
        for i in range(rotation_iterations):
            empty.rotation_euler = (pitch, math.radians(i * 360 + parent.asset_yaw), 0)
            empty.keyframe_insert(data_path="rotation_euler", frame=1 + 2 * parent.frames * i)
            empty.rotation_euler = (pitch, math.radians(360 + i * 360 + parent.asset_yaw), 0)
            empty.keyframe_insert(data_path="rotation_euler", frame=parent.frames + 1 + 2 * parent.frames * i)

        # Linear Curves for Object Rotation
        fcurves = empty.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

        return objects_of_asset

    def update_asset_turntable(self, parent, pipe_tool_all):
        empty = bpy.data.objects['rotation_parent']

        # Remove previous rotation from locator/empty
        fcurves = empty.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                # kf.interpolation = 'LINEAR'
                pass
            fcurves.remove(fcurve)

        # Create new Rotation
        pitch = math.radians(90 + parent.asset_pitch)
        empty.rotation_euler = (pitch, 0, 0)
        bpy.context.view_layer.update()

        if pipe_tool_all.render_flat_textures and pipe_tool_all.render_shading is False:
            lightrig_rotation_factor = 1
            rotation_iterations = 1
            # frame_length = parent.frames
        else:
            lightrig_rotation_factor = 2
            rotation_iterations = len(parent.hdris)
            # frame_length = parent.frames * 2 * len(parent.hdris)

        frame_length = parent.frames * lightrig_rotation_factor * rotation_iterations
        bpy.context.scene.frame_end = frame_length

        # Setup Object Rotations
        for i in range(rotation_iterations):
            empty.rotation_euler = (pitch, math.radians(i * 360 + parent.asset_yaw), 0)
            empty.keyframe_insert(data_path="rotation_euler", frame=1 + 2 * parent.frames * i)
            empty.rotation_euler = (pitch, math.radians(360 + i * 360 + parent.asset_yaw), 0)
            empty.keyframe_insert(data_path="rotation_euler", frame=parent.frames + 1 + 2 * parent.frames * i)

        # Linear Curves for Object Rotation
        fcurves = empty.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

    def setup_hdri_turntable(self, parent, context, pipe_tool_all):
        # Create Lights
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes

        for node in nodes:
            world.node_tree.nodes.remove(node)

        # World Output
        node_pos_x_spacing = 60
        node_pos_y_default = 300
        node_output = nodes.new("ShaderNodeOutputWorld")
        node_output.name = 'WorldOutput'
        node_output.label = 'WorldOutput'
        node_output.select = False
        node_output.location = (140 + node_pos_x_spacing, node_pos_y_default)

        # Background
        node_background = nodes.new("ShaderNodeBackground")
        node_background.name = 'Background'
        node_background.label = 'Background'
        node_background.select = False
        node_background.location = (0, node_pos_y_default)

        world.node_tree.links.new(node_background.outputs[0], node_output.inputs[0])

        if pipe_tool_all.render_flat_textures is False or pipe_tool_all.render_shading:
            # Add mix nodes
            if len(parent.hdris) <= 1:
                node_pos_x_offset = 0
            else:
                node_pos_x_offset = -140 - node_pos_x_spacing
                for i in range(len(parent.hdris) - 1):
                    node_mix = nodes.new("ShaderNodeMixRGB")
                    node_mix.name = f'Mix_{i + 1}'
                    node_mix.label = f'Mix_{i + 1}'
                    node_mix.select = False
                    node_mix.location = (node_pos_x_offset,
                                         node_pos_y_default + i * -180 - i * node_pos_x_spacing * 0.5)

            # HDRI position x
            node_pos_x_hdris = -240 + node_pos_x_offset - node_pos_x_spacing
            node_pos_x_mapping_2 = -140 + node_pos_x_hdris - node_pos_x_spacing

            # Rotation Mapping
            node_pos_x_mapping = -140 + node_pos_x_mapping_2 - node_pos_x_spacing
            node_mapping = hdri_node_creator(context, 'pipe_rotation', "ShaderNodeMapping",
                                             (node_pos_x_mapping, node_pos_y_default))

            # Texture Coordinates
            node_pos_x_texture_coordinates = -140 + node_pos_x_mapping - node_pos_x_spacing
            node_texture_coordinates = hdri_node_creator(context, 'pipe_coordinates', "ShaderNodeTexCoord",
                                                         (node_pos_x_texture_coordinates, node_pos_y_default))

            # Create HDRIs
            for i, hdri in enumerate(parent.hdris):
                node_hdri = hdri_node_creator(context, f'pipe_HDRI_{i + 1}', "ShaderNodeTexEnvironment",
                                              (node_pos_x_hdris,
                                               node_pos_y_default - i * 200 - i * node_pos_x_spacing * 0.5))

                # Rotation Offset
                node_mapping_2 = hdri_node_creator(context, f'pipe_rotation_offset{i + 1}', "ShaderNodeMapping",
                                                   (node_pos_x_mapping_2,
                                                    node_pos_y_default - i * 200 - i * node_pos_x_spacing * 0.5))
                node_mapping_2.inputs[2].default_value[2] = math.radians(parent.rotation_offsets[i])
                node_mapping_2.hide = True

                world.node_tree.links.new(node_mapping.outputs[0], node_mapping_2.inputs[0])
                world.node_tree.links.new(node_mapping_2.outputs[0], node_hdri.inputs[0])

                # Import and set HDRI file
                hdri_name = parent.hdris[i]
                dict_hdri = dict_project_config["hdris"][hdri_name]
                file_hdr = dict_hdri["path"]

                if hdri_name in [x.name for x in bpy.data.images]:
                    hdr = bpy.data.images[hdri_name]
                else:
                    hdr = bpy.data.images.load(file_hdr)
                    hdr.name = hdri_name
                    colour_space = file_hdr.split('.')[1]
                    spaces = [x.name for x in
                              type(hdr).bl_rna.properties['colorspace_settings'].fixed_type.properties[
                                  'name'].enum_items]
                    if colour_space in spaces:
                        hdr.colorspace_settings.name = colour_space
                    elif 'lin_srgb' in spaces:
                        hdr.colorspace_settings.name = 'lin_srgb'

                node_hdri.image = hdr

            # Remaining Connections
            world.node_tree.links.new(node_texture_coordinates.outputs[0], node_mapping.inputs[0])

            if len(parent.hdris) <= 1:
                world.node_tree.links.new(node_hdri.outputs[0], node_background.inputs[0])
            else:
                nodes = world.node_tree.nodes
                for i in range(len(parent.hdris) - 1):
                    mix_node = nodes[f'Mix_{i + 1}']

                    if i == 0:
                        input_1 = nodes[f'pipe_HDRI_{i + 1}']
                        input_2 = nodes[f'pipe_HDRI_{i + 2}']
                    else:
                        input_1 = nodes[f'Mix_{i}']
                        input_2 = nodes[f'pipe_HDRI_{i + 2}']

                    world.node_tree.links.new(input_1.outputs[0], mix_node.inputs[1])
                    world.node_tree.links.new(input_2.outputs[0], mix_node.inputs[2])

                    # Last mix node
                    if i == (len(parent.hdris) - 2):
                        world.node_tree.links.new(mix_node.outputs[0], node_background.inputs[0])

            # Animate HDRIs
            # Rotation of HDRI
            for i in range(len(parent.hdris)):
                node_mapping.inputs[2].default_value[2] = -math.radians(0 + i * 360)
                node_mapping.inputs[2].keyframe_insert(data_path="default_value",
                                                       frame=parent.frames + 1 + 2 * parent.frames * i)
                node_mapping.inputs[2].default_value[2] = -math.radians(360 + i * 360)
                node_mapping.inputs[2].keyframe_insert(data_path="default_value",
                                                       frame=1+2 * parent.frames * (i + 1))

                if i != (len(parent.hdris) - 1):
                    mix_node = nodes[f'Mix_{i + 1}']
                    mix_node.inputs[0].default_value = 0.0
                    mix_node.inputs[0].keyframe_insert(data_path="default_value", frame=2 * parent.frames * (i + 1))
                    mix_node.inputs[0].default_value = 1.0
                    mix_node.inputs[0].keyframe_insert(data_path="default_value", frame=2 * parent.frames * (i + 1) + 1)

            fcurves = world.node_tree.animation_data.action.fcurves

            for fcurve in fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'LINEAR'
        else:
            node_background.inputs[0].default_value = (0, 0, 0, 1)

    def setup_flat_texture_aovs(self):
        global asset
        textures = []
        for mat in [x for x in bpy.data.materials if asset in x.name]:
            nodes = mat.node_tree.nodes

            output_location = [x for x in nodes if x.type == 'OUTPUT_MATERIAL'][0].location

            for node in nodes:
                # print(node)
                # print(node.type)
                if node.type == 'TEX_IMAGE':
                    if node.name not in textures:
                        textures.append(node.name)
                    # print(node.name)
                    node_aov_output = bpy.data.materials.get(f'txt_{node.name}')
                    if node_aov_output is None:
                        node_aov_output = nodes.new("ShaderNodeOutputAOV")
                        node_aov_output.name = f'txt_{node.name}'
                        node_aov_output.label = f'{node.name}_aov'

                    texture_location = node.location
                    node_aov_output.location = (output_location[0] + 240, texture_location[1])

                    mat.node_tree.links.new(node.outputs[0], node_aov_output.inputs[0])

        default_view_layer = bpy.context.window.view_layer

        for vl in [x for x in bpy.context.scene.view_layers if len(x.name) == 1]:
            bpy.context.window.view_layer = vl

            for i, texture in enumerate(textures):
                try:  # Blender 2.91
                    bpy.ops.cycles.add_aov()
                    aov = bpy.context.view_layer.cycles.aovs[i]
                except AttributeError:  # Blender 2.92
                    bpy.ops.scene.view_layer_add_aov()
                    aov = bpy.context.view_layer.aovs[i]

                # aov.type = 'VALUE'
                aov.name = f'txt_{texture}'

                vl.use_pass_combined = False
                vl.use_pass_z = False

        bpy.context.window.view_layer = default_view_layer


class AllOpenOutput(bpy.types.Operator):
    bl_idname = 'pipe.output_directory'
    bl_label = 'Output Directory'
    bl_description = 'Opens the directory the frames will be rendered to'

    def execute(self, context):
        os.startfile(os.path.split(context.scene.render.filepath)[0])
        return {'FINISHED'}


class AllTurntableUpdate(bpy.types.Operator):
    bl_idname = 'pipe.turntable_update'
    bl_label = 'Update'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Updates the MDL & TXT versions based on your stream'

    def __init__(self):
        self.hdri_1_bool = self.hdri_2_bool = self.hdri_3_bool = self.hdri_4_bool = self.hdri_5_bool = \
            self.hdri_1 = self.hdri_2 = self.hdri_3 = self.hdri_4 = self.hdri_5 = self.hdri_1_rotation = \
            self.hdri_2_rotation = self.hdri_3_rotation = self.hdri_4_rotation = self.hdri_5_rotation = \
            self.frames = self.asset_yaw = self.asset_pitch = self.render_flat_textures = self.render_shading = \
            self.mdl = None

        self.hdris = []
        self.rotation_offsets = []

    def execute(self, context):
        global root, project, asset, dir_asset, dir_pipe, dir_pipe_mdl, dir_pipe_txt, txt_var

        scene = context.scene
        pipe_tool_all = scene.pipe_tool_all
        txt_var = pipe_tool_all.variation_selector

        dir_pipe_shd_variation = str(os.path.join(dir_pipe_shd, txt_var))
        json_file_package = os.path.join(dir_pipe_shd_variation, 'shd_package.json')

        with open(json_file_package, 'r') as json_content:
            dict_shd_package = json.load(json_content)
        new_shd_version = dict_shd_package[discipline]

        # Get SHD version
        current_shd_version = context.window.scene.name.split('.')[-1]

        if new_shd_version != current_shd_version:
            current_scene = context.window.scene
            AllTurntableFunctions().copy_ui_settings(self, pipe_tool_all)

            context.window.scene = bpy.data.scenes['.old']
            AllTurntableFunctions().paste_ui_settings(self, bpy.context.scene.pipe_tool_all)
            bpy.data.scenes.remove(current_scene)

            for col in bpy.data.collections:
                bpy.data.collections.remove(col)
            clear_scene()

            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh)
            bpy.ops.pipe.turntable_setup()

            # TODO create fake user for old shd library
            # delete old shading library
            return {'FINISHED'}
        else:
            AllTurntableFunctions().copy_ui_settings(self, pipe_tool_all)

            if self.hdri_1_bool or self.hdri_2_bool or self.hdri_3_bool or self.hdri_4_bool or self.hdri_5_bool or \
                    pipe_tool_all.render_flat_textures:
                #  -- UPDATE TEXTURES --
                # Read Lights
                AllTurntableFunctions().gather_hdris(self)

                # Update Asset rotation
                AllTurntableFunctions().update_asset_turntable(self, pipe_tool_all)

                # Update HDRI turntable
                AllTurntableFunctions().setup_hdri_turntable(self, context, pipe_tool_all)

                # -- UPDATE MODEL --
                # UPDATE ASSET
                AllTurntableFunctions().update_asset(pipe_tool_all)

                empty = bpy.data.objects['rotation_parent']
                current_rotation = empty.matrix_world.copy()

                pitch = math.radians(90 + self.asset_pitch)
                empty.rotation_euler = (pitch, 0, 0)
                bpy.context.view_layer.update()

                objects_of_asset = [x for x in bpy.data.objects if asset in x.name and x.library is None]

                # Parent objects to locator
                for obj in objects_of_asset:
                    #matrix_copy = empty.matrix_world.copy() * 0.1
                    matrix_copy = obj.matrix_world.copy()
                    obj.parent = empty
                    obj.matrix_world = matrix_copy

                empty.matrix_world = current_rotation

                '''# Set up clean render camera
                for camera in bpy.data.cameras:
                    bpy.data.cameras.remove(camera)

                for obj in objects_of_asset:
                    obj.select_set(True)
                create_camera()
                bpy.ops.object.select_all(action='DESELECT')'''

                # Set output directory
                AllTurntableFunctions().setup_output_directory()

                return {'FINISHED'}

            else:
                self.report({'ERROR'},
                            'Scene has not been updated as no HDRIs have been selected and flat rendering is '
                            'disabled.')
                return {'CANCELLED'}


class AllSetupTurntable(bpy.types.Operator):
    bl_idname = 'pipe.turntable_setup'
    bl_label = 'Setup Turntable'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Creates a turntable'

    def __init__(self):
        self.hdri_1_bool = self.hdri_2_bool = self.hdri_3_bool = self.hdri_4_bool = self.hdri_5_bool = \
            self.hdri_1 = self.hdri_2 = self.hdri_3 = self.hdri_4 = self.hdri_5 = self.hdri_1_rotation = \
            self.hdri_2_rotation = self.hdri_3_rotation = self.hdri_4_rotation = self.hdri_5_rotation = \
            self.frames = self.asset_pitch = self.asset_yaw = self.render_shading = self.render_flat_textures = \
            self.mdl = None

        self.hdris = []
        self.rotation_offsets = []

    def execute(self, context):
        # load currently published shading file
        # change variable to be loaded
        # load update operator
        global root, project, asset, dir_asset, dir_pipe, dir_pipe_mdl, dir_pipe_txt, txt_var

        scene = context.scene
        pipe_tool_all = scene.pipe_tool_all
        txt_var = pipe_tool_all.variation_selector

        # Read and store UI settings
        AllTurntableFunctions().copy_ui_settings(self, pipe_tool_all)

        if self.hdri_1_bool or self.hdri_2_bool or self.hdri_3_bool or self.hdri_4_bool or self.hdri_5_bool or \
                pipe_tool_all.render_flat_textures:
            # Read Shd Package
            blend_file, shd_version_blend, active_shd_version = AllTurntableFunctions().read_shd_package(txt_var)

            if blend_file is None and shd_version_blend is None and active_shd_version is None:
                self.report({'ERROR'}, "Scene has not been created as shd has not been set up for this variation.")
                return {'CANCELLED'}
            else:
                # Delete all previously existing collections, objects, cameras and more
                clear_scene()

                # Import latest SHD file
                bpy.ops.wm.append(directory=f'{blend_file}\\Scene\\', filepath=f'{asset}.blend',
                                  filename=f'Scene',
                                  autoselect=True)

                # Switch active scene
                context.window.scene = bpy.data.scenes['Scene']
                context.window.scene.name = f'SHD.{active_shd_version}'

                # Look through render camera
                area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
                area.spaces[0].region_3d.view_perspective = 'CAMERA'

                # Paste UI properties from default scene
                pipe_tool_all = bpy.context.scene.pipe_tool_all
                AllTurntableFunctions().paste_ui_settings(self, pipe_tool_all)

                # Read Lights
                AllTurntableFunctions().gather_hdris(self)

                # Update RenderSettings
                if pipe_tool_all.render_flat_textures and pipe_tool_all.render_shading is False:
                    pipe_tool_all.render_settings = 'cycles,flat'
                else:
                    pipe_tool_all.render_settings = 'cycles,turntable'

                # UPDATE ASSET
                AllTurntableFunctions().update_asset(pipe_tool_all)

                # Asset rotation
                objects_of_asset = AllTurntableFunctions().setup_asset_turntable(self, context, pipe_tool_all)

                # Create HDRI turntable
                AllTurntableFunctions().setup_hdri_turntable(self, context, pipe_tool_all)

                '''# Set up clean render camera
                for camera in bpy.data.cameras:
                    bpy.data.cameras.remove(camera)
    
                for obj in objects_of_asset:
                    obj.select_set(True)
                create_camera()
                bpy.ops.object.select_all(action='DESELECT')'''

                # Add flat texture AOVs
                if pipe_tool_all.render_flat_textures:
                    AllTurntableFunctions().setup_flat_texture_aovs()

                pipe_tool_all.filetype = 'EXR'
                pipe_tool_all.compositing_passes = False

                # Set output directory
                AllTurntableFunctions().setup_output_directory()

                # Change UI based on state of UI
                catch_loading_scene('')

                return {'FINISHED'}

        else:
            self.report({'ERROR'}, 'Scene has not been set up as no HDRIs have been selected and flat rendering is '
                                   'disabled.')
            return {'CANCELLED'}

# TODO bind loading image with colourspace detection script
# TODO blender script for IOR controlling group
# TODO release tool for .abc
# TODO MDL release does smooth? (only for texturing meshes please)
# TODO needs to detect whether shading has been released on per texture variation basis

# TODO needs to copy default configs for projects if copying or creating

# TODO add possibility to load ABC files (how to handle subdiv models? change behaviour to save in name?)
# TODO add turntable to MDL discipline
# TODO clean up ''' areas

# TODO report message when finishing publish on shd pipeline
# TODO shd setup script, delete udim materials?

# TODO check for HDRI duplicates
# TODO tool that automatically splits turntable renders into videosequences of all individual passes
# TODO enable options but make it a force full reload of scene


# TODO package manager for anims
# TODO anim material?
# TODO anim off freeze transforms in turntable tool
# TODO tooltips for stream pantries in main UI
# TODO Enable publishing and pulling for anm discipline
# TODO fix materials on animations

# --- SHD STREAM -------------------------------------------------------------------------------------------------------
scene_has_been_loaded = False
scene_is_turntable = False
txt_var = None
mdl_variations = None


@persistent
def catch_loading_scene(_):
    global scene_has_been_loaded, scene_is_turntable, asset, txt_var, mdl_variations
    #pipe_tool_all = bpy.context.scene.pipe_tool_all

    reverse = True
    #current_render_settings = f'cycles,shading'
    for col in bpy.data.collections:
        if asset in col.name:
            scene_has_been_loaded = True
            try:
                txt_var = str([x.name.split('.')[2] for x in bpy.data.collections if x.name.split('.')[0] == asset
                               and x.name.count('.') >= 4][0])
            except IndexError:
                txt_var = None
            mdl_variations = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
            reverse = False
            #pipe_tool_all.filetype =

            break

    if reverse:
        scene_has_been_loaded = False
        txt_var = None
    else:
        if 'rotation_parent' in [obj.name for obj in bpy.data.objects]:
            scene_is_turntable = True
            #current_render_settings = f'cycles,turntable'

    #pipe_tool_all.render_settings = current_render_settings


class PipeSettingsShd(bpy.types.PropertyGroup):
    txt_var: StringProperty(
        name='',
        description="TXT/SHD variation used by this scene. \n\n Each variation needs a separate .blend file",
        default='A',
        options={'SKIP_SAVE'})

    publish: BoolProperty(
        name='publish',
        description='Whether this asset should immediately published',
        default=False,
        options={'SKIP_SAVE'})


def hdri_update(self, context):
    world = context.scene.world
    world.use_nodes = True
    #nodes = context.scene.world.node_tree.nodes
    nodes = world.node_tree.nodes

    node_world_output = nodes['World Output']
    # create/get nodes
    if 'Background' in nodes:
        node_background = nodes['Background']
    else:
        node_background = nodes.new("ShaderNodeBackground")
        node_background.name = 'Background'
        node_background.label = 'Background'
        node_background.select = False
        node_background.location = (10, 300)

    # custom nodes
    node_img = hdri_node_creator(context, 'pipe_HDRI', "ShaderNodeTexEnvironment", (-300, 300))
    node_mapping = hdri_node_creator(context, 'pipe_rotation', "ShaderNodeMapping", (-500, 300))
    node_mapping_offset = hdri_node_creator(context, 'pipe_offset', "ShaderNodeMapping", (-700, 300))
    node_texture_coordinates = hdri_node_creator(context, 'pipe_coordinates', "ShaderNodeTexCoord", (-900, 300))

    # link nodes
    world.node_tree.links.new(node_background.outputs[0], node_world_output.inputs[0])
    world.node_tree.links.new(node_img.outputs[0], node_background.inputs[0])
    world.node_tree.links.new(node_mapping.outputs[0], node_img.inputs[0])
    world.node_tree.links.new(node_mapping_offset.outputs[0], node_mapping.inputs[0])
    world.node_tree.links.new(node_texture_coordinates.outputs[0], node_mapping_offset.inputs[0])

    # setting values
    hdri_name = bpy.context.scene.pipe_tool_all.hdri_selector
    dict_hdri = dict_project_config["hdris"][hdri_name]
    file_hdr = dict_hdri["path"]

    #load_image(dir_channel_textures, file_hdr, files, name, file_1)
    if hdri_name in [x.name for x in bpy.data.images]:
        hdr = bpy.data.images[hdri_name]
    else:
        hdr = bpy.data.images.load(file_hdr)
        hdr.name = hdri_name
        colour_space = file_hdr.split('.')[1]
        spaces = [x.name for x in
                  type(hdr).bl_rna.properties['colorspace_settings'].fixed_type.properties[
                      'name'].enum_items]
        if colour_space in spaces:
            hdr.colorspace_settings.name = colour_space
        elif 'lin_srgb' in spaces:
            hdr.colorspace_settings.name = 'lin_srgb'

    node_img.image = hdr
    node_mapping_offset.inputs[2].default_value[2] = math.radians(dict_hdri["rotation"])
    node_mapping.inputs[2].default_value[2] = math.radians(bpy.context.scene.pipe_tool_all.hdri_rotation)


def hdri_node_creator(context, name, node_type, coordinates):
    nodes = context.scene.world.node_tree.nodes

    if name in [x.name for x in nodes]:
        return nodes[name]

    node = nodes.new(node_type)
    node.name = name
    node.label = name[5:]
    node.select = False
    node.location = coordinates

    return node


def hdri_update_rotation(self, context):
    world = context.scene.world
    world.use_nodes = True
    nodes = context.scene.world.node_tree.nodes

    if 'pipe_rotation' in [x.name for x in nodes]:
        node_rotation = nodes['pipe_rotation']
        rotation_value = bpy.context.scene.pipe_tool_all.hdri_rotation
        node_rotation.inputs[2].default_value[2] = math.radians(rotation_value)


def apply_render_settings(self, context):
    bpy.ops.pipe.all_settings_apply()


def apply_filetype(self, context):
    global scene_has_been_loaded
    if scene_has_been_loaded:
        bpy.ops.pipe.all_filetype_apply()


def update_compositing_passes(self, context):
    global root, project, asset, dir_asset, dir_pipe, dir_pipe_mdl, dir_pipe_txt, txt_var

    scene = context.scene
    pipe_tool_all = scene.pipe_tool_all

    view_layers = [x for x in bpy.context.scene.view_layers]  # if len(x.name) == 1]

    if bpy.context.scene.render.engine == 'CYCLES':
        # Activate Passes
        if pipe_tool_all.compositing_passes:
            #file_config = '.\\config\\config_render_passes.json'
            file_config = f'.\\projects\\{project}-{project_abbr}\\config_render_passes.json'

            with open(file_config, 'r') as json_file:
                dict_config_render_passes = json.load(json_file)["render_passes"]

            for view_layer in view_layers:
                view_layer.use_pass_z = dict_config_render_passes["use_pass_z"]
                view_layer.use_pass_mist = dict_config_render_passes["use_pass_mist"]
                view_layer.use_pass_normal = dict_config_render_passes["use_pass_normal"]

                view_layer.use_pass_diffuse_direct = dict_config_render_passes["use_pass_diffuse_direct"]
                view_layer.use_pass_diffuse_indirect = dict_config_render_passes["use_pass_diffuse_indirect"]
                view_layer.use_pass_diffuse_color = dict_config_render_passes["use_pass_diffuse_color"]

                view_layer.use_pass_glossy_direct = dict_config_render_passes["use_pass_glossy_direct"]
                view_layer.use_pass_glossy_indirect = dict_config_render_passes["use_pass_glossy_indirect"]
                view_layer.use_pass_glossy_color = dict_config_render_passes["use_pass_glossy_color"]

                view_layer.use_pass_transmission_direct = dict_config_render_passes["use_pass_transmission_direct"]
                view_layer.use_pass_transmission_indirect = dict_config_render_passes["use_pass_transmission_indirect"]
                view_layer.use_pass_transmission_color = dict_config_render_passes["use_pass_transmission_color"]

                view_layer.use_pass_emit = dict_config_render_passes["use_pass_emit"]
                view_layer.use_pass_environment = dict_config_render_passes["use_pass_environment"]
                view_layer.use_pass_shadow = dict_config_render_passes["use_pass_shadow"]
                view_layer.use_pass_ambient_occlusion = dict_config_render_passes["use_pass_ambient_occlusion"]

                # Incorrect commands given by blender info:
                #bpy.context.scene.denoising_store_passes = True
                #view_layer.use_pass_volume_direct = False
                #view_layer.use_pass_volume_indirect = False

        # Deactivate Passes
        else:
            for view_layer in view_layers:
                view_layer.use_pass_z = False
                view_layer.use_pass_mist = False
                view_layer.use_pass_normal = False

                view_layer.use_pass_diffuse_direct = False
                view_layer.use_pass_diffuse_indirect = False
                view_layer.use_pass_diffuse_color = False

                view_layer.use_pass_glossy_direct = False
                view_layer.use_pass_glossy_indirect = False
                view_layer.use_pass_glossy_color = False

                view_layer.use_pass_transmission_direct = False
                view_layer.use_pass_transmission_indirect = False
                view_layer.use_pass_transmission_color = False

                view_layer.use_pass_emit = False
                view_layer.use_pass_environment = False
                view_layer.use_pass_shadow = False
                view_layer.use_pass_ambient_occlusion = False

    else:
        pass
        # report that this is not an eevee
        #self.report({"INFO"}, "Bladiblablubdiblub.")

# TODO z pass conflict with flat rendering setup
# TODO trigger disable when creating scene


class PipeSettingsAll(bpy.types.PropertyGroup):
    # model option is mandatory
    # add all animations to list
    dir_pipe_anim = os.path.join(root, project, 'build', asset, '.pipeline', 'anm')
    list_animations = [('MDL', f'MDL', '')]

    for animation in os.listdir(dir_pipe_anim):
        list_animations.append((animation, f'ANM    {animation}', ''))

    model_selector: EnumProperty(
        items=list_animations,
        description='Select the model or animation you want to use',
        name=''
    )

    list_hdris = []
    hdri_names = [x for x in dict_project_config['hdris'] if x == dict_project_config["hdri_default"]] + \
                 [x for x in dict_project_config['hdris'] if x != dict_project_config["hdri_default"]]

    for i, hdri in enumerate(hdri_names):
        value = (hdri, f"{hdri}      {dict_project_config['hdris'][hdri]['contrast']} contrast", '')
        list_hdris.append(value)

    hdri_spoiler: BoolProperty(
        name='Lighting',
        default=True
    )

    hdri_selector: EnumProperty(
        items=list_hdris,
        description='HDRI',
        name='',
        update=hdri_update
    )

    hdri_rotation: FloatProperty(
        name="Rotation",
        description='',
        default=0,
        soft_min=-360,
        soft_max=360,
        update=hdri_update_rotation
    )

    list_variations = [(x, x, '') for x in os.listdir(dir_pipe_txt) if os.path.isdir(os.path.join(dir_pipe_txt, x))]

    variation_selector: EnumProperty(
        items=list_variations,
        description='TXT variation.\nCan only be used before initial setup.',
        name=''
    )

    turntable_frames: IntProperty(
        name="Frames per Rotation",
        description='Number of frames used for setting up object and HDRI rotation',
        default=16,
        min=1,
        soft_max=120
    )

    turntable_hdri_1_selector: EnumProperty(
        items=list_hdris,
        description='HDRI #1',
        name=''
    )

    turntable_hdri_2_selector: EnumProperty(
        items=list_hdris,
        description='HDRI #2',
        name=''
    )

    turntable_hdri_3_selector: EnumProperty(
        items=list_hdris,
        description='HDRI #3',
        name=''
    )

    turntable_hdri_4_selector: EnumProperty(
        items=list_hdris,
        description='HDRI #4',
        name=''
    )

    turntable_hdri_5_selector: EnumProperty(
        items=list_hdris,
        description='HDRI #5',
        name=''
    )

    turntable_hdri_1_bool: BoolProperty(
        name='',
        default=True
    )

    turntable_hdri_2_bool: BoolProperty(
        name='',
        default=False
    )

    turntable_hdri_3_bool: BoolProperty(
        name='',
        default=False
    )

    turntable_hdri_4_bool: BoolProperty(
        name='',
        default=False
    )

    turntable_hdri_5_bool: BoolProperty(
        name='',
        default=False
    )

    turntable_hdri_1_rotation: FloatProperty(
        name="Rot",
        description='Rotation offset for this HDRI',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_hdri_2_rotation: FloatProperty(
        name="Rot",
        description='Rotation offset for this HDRI',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_hdri_3_rotation: FloatProperty(
        name="Rot",
        description='Rotation offset for this HDRI',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_hdri_4_rotation: FloatProperty(
        name="Rot",
        description='Rotation offset for this HDRI',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_hdri_5_rotation: FloatProperty(
        name="Rot",
        description='Rotation offset for this HDRI',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_yaw_offset: FloatProperty(
        name="Yaw",
        description='Rotation offset on the yaw axis used for the asset',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    turntable_pitch_offset: FloatProperty(
        name="Pitch",
        description='Rotation offset on the pitch axis used for the asset',
        default=0,
        soft_min=-360,
        soft_max=360
    )

    view_layers: StringProperty(
        name='',
        description="Each texture variation can apply to more than one model variation. \n"
                    "Which of the existing model variations do you want to use? \n\n separate by comma",
        default='*'
    )

    file_config = f'.\\projects\\{project}-{project_abbr}\\config_render_settings.json'

    with open(file_config, 'r') as json_file:
        dict_config_render_settings = json.load(json_file)

    list_render_settings_parts = []
    for engine in dict_config_render_settings:
        for settings in dict_config_render_settings[engine]:
            list_render_settings_parts.append((f'{engine},{settings}', f'{engine.capitalize()} {settings.capitalize()}',
                                               ''))

    render_settings: EnumProperty(
        items=list_render_settings_parts,
        description='Applies render settings according to settings stored in the config_render_settings.json',
        name='',
        update=apply_render_settings
    )

    filetype: EnumProperty(
        items=[('EXR', 'EXR', ''), ('PNG', 'PNG', ''), ('JPEG', 'JPEG', '')],
        description='Changes the filetype that is used for rendering a sequence',
        name='',
        update=apply_filetype
    )

    render_flat_textures: BoolProperty(
        name=' Flat Textures',
        description='If this is enabled, the turntable will add a flat pass for each texture',
        default=False
    )

    render_shading: BoolProperty(
        name=' Render Shaded',
        description='If this is disabled, only the flat textures will be rendered.',
        default=True
    )

    compositing_passes: BoolProperty(
        name=' render passes',
        description='If this is enabled, render passes such as Z-Depth, Diffuse, Specular and others will be rendered.',
        default=False,
        update=update_compositing_passes
    )


class ShdUiPackageManagement(bpy.types.Panel):
    bl_idname = 'PIPE_PT_shd'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Package Management")

    def draw(self, context):
        global scene_has_been_loaded, txt_var, scene_is_turntable
        scene = context.scene
        pipe_tool = scene.pipe_tool
        pipe_tool_all = scene.pipe_tool_all

        layout = self.layout

        row0 = layout.row()
        if scene_has_been_loaded is False or scene_is_turntable is False:
            row0.label(text='MDL / ANM')
            row0.prop(pipe_tool_all, "model_selector")

            row1 = layout.row()

            column1 = row1.column()
            column2 = row1.column()
            column1.label(text='TXT Variation')

            row2 = layout.row()
            #column2.prop(pipe_tool, 'txt_var')
            column2.prop(pipe_tool_all, 'variation_selector')

            #txt_var = pipe_tool.txt_var
            if scene_has_been_loaded is False:
                row2.operator('pipe.shd_setup')
            else:
                column2.enabled = False
                #column2.label(text=txt_var)
                row2.operator('pipe.shd_update')
        else:
            row0.label(text='Tool disabled - turntable scenes detected')
            #row1.label(text='Disabled as current scene is a turntable.')
            row0.enabled = False


# TODO remove redundant txt_variation query


class AllUiRenderSettings(bpy.types.Panel):
    bl_idname = 'PIPE_PT_all_render_settings'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 2

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Render Settings")

    def draw(self, context):
        global scene_has_been_loaded, scene_is_turntable, txt_var, mdl_variations

        scene = context.scene
        pipe_tool_all = scene.pipe_tool_all
        txt_var = pipe_tool_all.variation_selector

        layout = self.layout

        row1 = layout.row()
        if scene_has_been_loaded:
            column1 = row1.column()
            #column2 = row1.column()

            column1.prop(pipe_tool_all, 'render_settings')

            row3 = layout.row()

            if scene_has_been_loaded and scene_is_turntable and \
                    pipe_tool_all.render_flat_textures and pipe_tool_all.render_shading is False:
                column1.enabled = False

            row3_column1 = row3.column()
            row3_column2 = row3.column()
            row3_column1.prop(pipe_tool_all, 'filetype')

            row3_column2.prop(pipe_tool_all, 'compositing_passes')
            if pipe_tool_all.filetype != 'EXR' or pipe_tool_all.render_settings.split(',')[0] != 'cycles':
                row3_column2.enabled = False

            row = layout.row()

            if discipline == 'shd' or scene_is_turntable:
                row.prop(pipe_tool_all, 'view_layers')
                row.operator('pipe.shd_settings_variation_get')
                row.operator('pipe.shd_settings_variation_set')

            if scene_is_turntable is False:
                row3 = layout.row()
                row3.separator()

                row4 = layout.row()
                row4.prop(pipe_tool_all, 'hdri_spoiler', icon="TRIA_DOWN" if pipe_tool_all.hdri_spoiler else
                          "TRIA_RIGHT", emboss=False)
                # row4.label(text='HDRI')

                if pipe_tool_all.hdri_spoiler:
                    row5 = layout.row()
                    row5.prop(pipe_tool_all, "hdri_selector")
                    row6 = layout.row()
                    row6.prop(pipe_tool_all, "hdri_rotation")

        else:
            row1.label(text="available after scene setup")
            row1.enabled = False


class ShdUiExport(bpy.types.Panel):
    bl_idname = 'PIPE_PT_shd_export'
    bl_label = ''
    bl_category = f'Open Pipe {discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 3

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Export")

    def draw(self, context):
        global scene_has_been_loaded, scene_is_turntable
        scene = context.scene
        pipe_tool = scene.pipe_tool

        layout = self.layout
        row1 = layout.row()
        if scene_has_been_loaded and scene_is_turntable is False:
            row1.prop(pipe_tool, 'publish')
            row1.operator('pipe.shd_export')
        else:
            row1.label(text='Only available in an active SHD file.')
            row1.enabled = False


def remove_empty_collections():
    for col in bpy.data.collections:
        if len(col.children) == 0 and len(col.objects) == 0:
            bpy.data.collections.remove(col)
# TODO update asset is broken


class AllSettingsVariationGet(bpy.types.Operator):
    bl_idname = 'pipe.shd_settings_variation_get'
    bl_label = 'Get'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Update the input to the currently used variations'

    def execute(self, context):
        mdl_variations = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
        pipe_tool_all = context.scene.pipe_tool_all

        used = []

        for mdl_var in mdl_variations:
            if bpy.context.scene.view_layers[mdl_var].use:
                used.append(mdl_var)

        if len(mdl_variations) == len(used):
            print('*')
            pipe_tool_all.view_layers = '*'
        else:
            print(''.join(used))
            pipe_tool_all.view_layers = ''.join(used)

        return {'FINISHED'}


class AllSettingsVariationSet(bpy.types.Operator):
    bl_idname = 'pipe.shd_settings_variation_set'
    bl_label = 'Set'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Update the input to the currently used variations'

    def execute(self, context):
        mdl_variations = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
        pipe_tool_all = context.scene.pipe_tool_all
        view_layers = pipe_tool_all.view_layers

        if '*' in view_layers:
            for mdl_var in mdl_variations:
                bpy.context.scene.view_layers[mdl_var].use = True
            return {'FINISHED'}

        # if only legal characters are used
        elif view_layers.isalpha():
            for mdl_var in mdl_variations:
                if mdl_var in view_layers:
                    use = True
                else:
                    use = False

                bpy.context.scene.view_layers[mdl_var].use = use

            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'Invalid input.')
            return {'CANCELLED'}


class AllSettingsApply(bpy.types.Operator):
    bl_idname = 'pipe.all_settings_apply'
    bl_label = 'Apply given render settings'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Updates the render settings according to the default settings for this purpose'

    def execute(self, context):
        global scene_has_been_loaded
        catch_loading_scene('')
        if scene_has_been_loaded:
            scene = context.scene
            pipe_tool_all = scene.pipe_tool_all
            engine, settings = pipe_tool_all.render_settings.split(',')

            if engine != 'cycles':
                pipe_tool_all.compositing_passes = False
            RenderSettings().apply_external(engine, settings)
        return {'FINISHED'}


class AllFiletypeApply(bpy.types.Operator):
    bl_idname = 'pipe.all_filetype_apply'
    bl_label = 'Use selected output filetype'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Changes the filetype according to the selected option.'

    def execute(self, context):
        global scene_has_been_loaded
        catch_loading_scene('')
        if scene_has_been_loaded:
            scene = context.scene
            pipe_tool_all = scene.pipe_tool_all
            filetype = pipe_tool_all.filetype
            if filetype == 'EXR':
                scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
                scene.render.image_settings.color_mode = 'RGBA'
                scene.render.image_settings.color_depth = '16'
                scene.render.image_settings.exr_codec = 'PIZ'
            elif filetype == 'PNG':
                scene.render.image_settings.file_format = 'PNG'
                scene.render.image_settings.color_depth = '16'
                pipe_tool_all.compositing_passes = False
            elif filetype == 'JPEG':
                scene.render.image_settings.file_format = 'JPEG'
                scene.render.image_settings.quality = 100
                pipe_tool_all.compositing_passes = False
        return {'FINISHED'}


class ShdExport(bpy.types.Operator):
    bl_idname = 'pipe.shd_export'
    bl_label = 'Release'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Updates MDL/TXT packages used by this scene.'

    def execute(self, context):
        pipe_tool = context.scene.pipe_tool
        publish = pipe_tool.publish
        ShdExportFunctions.export_shd(self, publish)
        return {'FINISHED'}


class RenderSettings:
    def __init__(self):
        #file_config = '.\\config\\config_render_settings.json'
        file_config = f'.\\projects\\{project}-{project_abbr}\\config_render_settings.json'

        with open(file_config, 'r') as json_file:
            self.dict_config = json.load(json_file)
        self.cycles_settings = self.eevee_settings = None

    def apply_external(self, engine, settings):
        if engine == 'cycles':
            bpy.context.scene.render.engine = engine.upper()
            self.cycles_settings = self.dict_config[engine][settings]
            self.apply_cycles()
        elif engine == 'eevee':
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'
            self.eevee_settings = self.dict_config[engine][settings]
            self.apply_eevee()

    def cycles_turntable(self):
        bpy.context.scene.render.engine = 'CYCLES'
        self.cycles_settings = self.dict_config["cycles"]["turntable"]
        self.apply_cycles()

    def cycles_shading(self):
        bpy.context.scene.render.engine = 'CYCLES'
        self.cycles_settings = self.dict_config["cycles"]["shading"]
        self.apply_cycles()

    def apply_eevee(self):
        bpy.context.scene.eevee.taa_render_samples = self.eevee_settings["taa_render_samples"]
        bpy.context.scene.eevee.taa_samples = self.eevee_settings["taa_samples"]

        bpy.context.scene.eevee.use_gtao = self.eevee_settings["use_gtao"]
        bpy.context.scene.eevee.gtao_distance = self.eevee_settings["gtao_distance"]
        bpy.context.scene.eevee.use_bloom = self.eevee_settings["use_bloom"]
        bpy.context.scene.eevee.bloom_threshold = self.eevee_settings["bloom_threshold"]
        bpy.context.scene.eevee.bloom_intensity = self.eevee_settings["bloom_intensity"]
        bpy.context.scene.eevee.use_ssr = self.eevee_settings["use_ssr"]
        bpy.context.scene.eevee.use_ssr_halfres = self.eevee_settings["use_ssr_halfres"]
        bpy.context.scene.eevee.ssr_border_fade = self.eevee_settings["ssr_border_fade"]
        bpy.context.scene.eevee.ssr_thickness = self.eevee_settings["ssr_thickness"]
        bpy.context.scene.render.use_high_quality_normals = True

    def apply_cycles(self):
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.samples = self.cycles_settings["samples"]
        bpy.context.scene.cycles.preview_samples = self.cycles_settings["preview_samples"]
        bpy.context.scene.cycles.use_animated_seed = self.cycles_settings["use_animated_seed"]

        bpy.context.scene.cycles.max_bounces = self.cycles_settings["max_bounces"]
        bpy.context.scene.cycles.diffuse_bounces = self.cycles_settings["diffuse_bounces"]
        bpy.context.scene.cycles.glossy_bounces = self.cycles_settings["glossy_bounces"]
        bpy.context.scene.cycles.transparent_max_bounces = self.cycles_settings["transparent_max_bounces"]
        bpy.context.scene.cycles.transmission_bounces = self.cycles_settings["transmission_bounces"]
        bpy.context.scene.cycles.sample_clamp_indirect = self.cycles_settings["sample_clamp_indirect"]

        bpy.context.scene.render.film_transparent = self.cycles_settings["film_transparent"]

        bpy.context.scene.render.tile_x = self.cycles_settings["tile_x"]
        bpy.context.scene.render.tile_y = self.cycles_settings["tile_y"]

        bpy.context.scene.cycles.blur_glossy = self.cycles_settings["blur_glossy"]

        bpy.context.scene.render.resolution_x = self.cycles_settings["resolution_x"]
        bpy.context.scene.render.resolution_y = self.cycles_settings["resolution_y"]

        bpy.context.scene.cycles.use_adaptive_sampling = self.cycles_settings["use_adaptive_sampling"]
        bpy.context.scene.cycles.adaptive_threshold = self.cycles_settings["adaptive_threshold"]
        bpy.context.scene.cycles.adaptive_min_samples = self.cycles_settings["adaptive_min_samples"]

# TODO use transparency and rendered backdrop? (not flexibel in terms of HDRI usage)


class ShdExportFunctions:
    def __init__(self):
        global asset, discipline, root, project, dir_shd, dir_pipe_shd, user, txt_var

    def create_export_directories(self):
        dir_shd_variation = str(os.path.join(dir_shd, '.pantry', str(txt_var)))
        dir_pipe_shd_variation = str(os.path.join(dir_pipe_shd, str(txt_var)))

        # PANTRY
        if os.path.isdir(dir_shd_variation) is False:
            os.makedirs(dir_shd_variation)
            version_cur = 'v001'
        else:
            existing_versions = [x for x in os.listdir(dir_shd_variation)
                                 if os.path.isdir('/'.join([dir_shd_variation, x]))]
            existing_versions.sort()
            latest_existing_version = existing_versions[-1]
            version_cur_int = int(latest_existing_version[1:]) + 1
            version_cur = 'v' + format(version_cur_int, '03d')

        dir_shd_variation_version = os.path.join(dir_shd_variation, version_cur)
        os.makedirs(dir_shd_variation_version)

        # PIPELINE
        dir_pipe_shd_versions = os.path.join(dir_pipe_shd_variation, 'versions')

        if os.path.isdir(dir_pipe_shd_versions):
            existing_versions_json = [x.split('.')[1] for x in os.listdir(dir_pipe_shd_versions)]

            if len(existing_versions_json) > 0:
                existing_versions_json.sort()
                latest_existing_version_json = existing_versions_json[-1]
                version_cur_int = int(latest_existing_version_json[1:]) + 1
                json_version_cur = 'v' + format(version_cur_int, '03d')
            else:
                json_version_cur = 'v001'
        else:
            json_version_cur = 'v001'
            os.makedirs(dir_pipe_shd_versions)

        return dir_shd_variation, dir_pipe_shd_variation, dir_pipe_shd_versions, version_cur, json_version_cur

    def export_shd(self, publish):
        dir_shd_variation, dir_pipe_shd_variation, dir_pipe_shd_versions, version_cur, json_version_cur = \
            ShdExportFunctions.create_export_directories(self)

        # SAVE BLEND FILE
        file_blend_shd = os.path.join(dir_shd_variation, version_cur, f'{asset}.blend')
        bpy.ops.wm.save_as_mainfile(filepath=file_blend_shd, copy=True)

        # JSON FILE - VERSION
        file_json_version = os.path.join(dir_pipe_shd_versions, f'{asset}.{json_version_cur}.json')

        dict_version_info = {
            "artist": user,
            "time": str(datetime.now()).split('.')[0],
            "version": version_cur,
            "published": publish
        }

        with open(file_json_version, 'w') as json_file:
            json.dump(dict_version_info, json_file, indent=2)

        file_json_shd_package = os.path.join(dir_pipe_shd_variation, 'shd_package.json')

        if os.path.isfile(file_json_shd_package):
            with open(file_json_shd_package, 'r') as json_file:
                dict_shd_package = json.load(json_file)
                dict_shd_package["shd"] = json_version_cur
        else:
            dict_shd_package = {
                "mdl": "",
                "txt": "",
                "shd": json_version_cur,
                "shd_publish": "",
                "anm": ""
            }
        if publish:
            dict_shd_package["shd_publish"] = json_version_cur

        with open(file_json_shd_package, 'w') as json_file:
            json.dump(dict_shd_package, json_file, indent=2)


class ShdUpdateAsset(bpy.types.Operator):
    bl_idname = 'pipe.shd_update'
    bl_label = 'Update Asset'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Updates MDL/TXT packages used by this scene.'

    def execute(self, context):
        global root, project, asset, dir_asset, dir_pipe, dir_pipe_mdl, dir_pipe_txt, txt_var

        remove_empty_collections()
        file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

        with open(file_mdl_package, 'r') as json_file:
            dict_mdl_package = json.load(json_file)

        dict_mdl_variations = dict_mdl_package["variations"]

        scene = context.scene
        pipe_tool_all = scene.pipe_tool_all
        selected_model = pipe_tool_all.model_selector
        if selected_model == 'MDL':
            update_model('mdl', dict_mdl_package, dict_mdl_variations)
        else:
            file_anm_package = os.path.join(dir_pipe_anm, selected_model, f'{selected_model}.json')
            with open(file_anm_package, 'r') as json_file:
                dict_mdl_package = json.load(json_file)
            update_model(selected_model, dict_mdl_package, dict_mdl_variations)
        update_textures()

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


# TODO render view layer checkboxes in pipeline
def create_camera():
    cam_data = bpy.data.cameras.new('render_cam')
    cam_obj = bpy.data.objects.new('render_cam', cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    bpy.context.scene.camera = cam_obj

    cam_obj.data.lens = 50

    # TODO set focal length
    # checks distances and heights for turntable rotation, so that object always is in frame
    distances = []
    heights = []
    steps = 12
    for step in range(1, steps+1, 1):
        cam_obj.rotation_euler = (3.141592654 * 0.5, 0, 3.141592654 * 2 * step / steps)
        bpy.ops.view3d.camera_to_view_selected()
        distance = math.sqrt(cam_obj.location[0] ** 2 + cam_obj.location[1] ** 2)
        distances.append(distance)
        heights.append(cam_obj.location[2])

    distance = max(distances)

    # Left/Right centering and framing compensation
    fov_default = math.degrees(cam_data.angle)
    fov_factor = 1 if bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y else bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y
    fov = fov_default * fov_factor * 0.5
    offset = abs(cam_obj.location[0] / math.tan(math.radians(fov)))
    cam_obj.location[0] = 0

    cam_obj.location[1] = -distance * 1.05 - offset
    cam_obj.location[2] = sum(heights) / len(heights)

    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    area.spaces[0].region_3d.view_perspective = 'CAMERA'


class ShdSetup(bpy.types.Operator):
    bl_idname = 'pipe.shd_setup'
    bl_label = 'Setup Shading'
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_description = 'Imports the active model variation, hides model variations not required by the given ' \
                     'txt/shd variation.\n' \
                     'Imports active texture and sets up basic shader.'

    def execute(self, context):
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
        for col in bpy.data.collections:
            if len(col.children) == 0 and len(col.objects) == 0:
                bpy.data.collections.remove(col)

        # RENDER SETTINGS
        RenderSettings().cycles_shading()

        global root, project, asset, dir_pipe_mdl, dir_pipe_txt, txt_var
        pipe_tool_all = context.scene.pipe_tool_all

        txt_var = pipe_tool_all.variation_selector

        file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

        txt_variations = os.listdir(dir_pipe_txt)

        if os.path.isdir(dir_pipe_txt) is False:
            self.report({'ERROR'}, 'No active TXT version could be found for the SHD stream.')
            return {'CANCELLED'}
        else:
            if os.path.isfile(file_mdl_package) is False:
                self.report({'ERROR'}, 'No active MDL version could be found for the SHD stream.')
                return {'CANCELLED'}
            else:
                if len(txt_var) == 1 and (txt_var.isupper() or txt_var.islower()):
                    if txt_var in txt_variations:
                        with open(file_mdl_package, 'r') as json_file:
                            dict_mdl_package = json.load(json_file)

                        dict_mdl_variations = dict_mdl_package["variations"]

                        # Detect animations:
                        selected_model = pipe_tool_all.model_selector
                        if selected_model != 'MDL':
                            file_anm_package = os.path.join(dir_pipe_anm, selected_model, f'{selected_model}.json')
                            with open(file_anm_package, 'r') as json_file:
                                dict_mdl_package = json.load(json_file)

                        initialise_texture_variation(dict_mdl_package, dict_mdl_variations, selected_model)

                        pipe_tool_all.render_settings = 'cycles,shading'

                        # CREATE CAMERA
                        objects_of_asset = [x for x in bpy.data.objects if asset in x.name and x.library is None]
                        for obj in objects_of_asset:
                            obj.select_set(True)
                        create_camera()

                        hdri_update(self, context)

                        bpy.ops.object.select_all(action='DESELECT')
                        catch_loading_scene('')
                        return {'FINISHED'}

                    else:
                        self.report({'ERROR'}, "Given TXT variation doesn't exist.")
                        return {'CANCELLED'}

                else:
                    self.report({'ERROR'}, 'Invalid input given for TXT variation.')
                    return {'CANCELLED'}


def archive_for_update(mdl_version, current_mdl_collection):
    global dir_asset, dir_mdl
    dir_mdl_version = os.path.join(dir_mdl, '.pantry', mdl_version)
    blend_mdl_version = os.path.join(dir_mdl_version, f'{asset}.blend')
    blend_mdl_collection = os.path.join(blend_mdl_version, 'Collection', asset)

    # Archive existing objects and their material
    dict_previous_objects = {}

    # Store information about objects and delete object containers
    for obj in current_mdl_collection.objects:
        material_information = []
        for i, material_slot in enumerate(obj.data.materials):
            material_information.append([i, material_slot])
            material_slot.use_fake_user = True
        name_parts = obj.name.split('.')
        print(name_parts)
        print(name_parts[-1][0:1])
        print('sd' == name_parts[-1][0:2])
        if 'sd' == name_parts[-1][0:2]:
            name_short = '.'.join(name_parts[0:-1])
        else:
            name_short = obj.name
            print('nameing False')
        print('ARCHIVING', name_short)
        dict_previous_objects[name_short] = {"mat": material_information}

        bpy.data.objects.remove(obj)

    # Deletes ghost meshes that resulted from deleting the object containers
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    remove_empty_collections()
    # TODO assign fake user to materials

    return dict_previous_objects


def assign_missing_mat(obj):
    missing_mat = bpy.data.materials.get('missing_mat')
    if missing_mat is None:
        missing_mat = bpy.data.materials.new(name='missing_mat')
        missing_mat.use_nodes = True
        missing_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.9, 0.1, 1)

    if obj.data.materials:
        for i, material_slot in enumerate(obj.data.materials):
            obj.data.materials[i] = missing_mat
    else:
        obj.data.materials.append(missing_mat)


def update_model(new_mdl_package_type, dict_mdl_package, dict_mdl_variations):
    global asset, dir_asset, txt_var
    current_variation_collections = [x for x in bpy.data.collections
                                     if x.name.split('.')[0] == asset
                                     and x.name.split('.')[1] == '*']
    current_mdl_collection = current_variation_collections[0]
    current_mdl_version = current_mdl_collection.name.split('.')[-1]

    current_mdl_package_type = current_mdl_collection.name.split('.')[3]

    pipe_tool_all = bpy.context.scene.pipe_tool_all

    mdl_version = dict_mdl_package[discipline]
    if new_mdl_package_type == 'mdl':
        file_anm_version = os.path.join(dir_pipe_mdl, 'versions', f'{asset}.{mdl_version}.json')

        with open(file_anm_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)
        mdl_version = dict_mdl_version['version']

        previous_mdl_variations_of_txt_var = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
        mdl_variations_of_txt_var = [key for key in dict_mdl_variations
                                     if txt_var in dict_mdl_variations[key]
                                     or '*' in dict_mdl_variations[key]]
        # IF UPDATE IS REQUIRED
        if new_mdl_package_type != current_mdl_package_type \
                or mdl_version != current_mdl_version \
                or previous_mdl_variations_of_txt_var != mdl_variations_of_txt_var:

            # Archive Data about objects
            dict_previous_objects = archive_for_update(mdl_version, current_mdl_collection)

            # Import objects and update data
            objects, _ = import_model(dict_mdl_package, dir_asset, dict_mdl_variations, txt_var, 'MDL')

            for obj in objects:
                name_parts = obj.name.split('.')
                if 'sd' == name_parts[-1][0:2]:
                    name_short = '.'.join(name_parts[0:-1])
                else:
                    name_short = obj.name
                if name_short in dict_previous_objects and obj.data.materials:
                    materials_new = [[i, material_slot] for i, material_slot in enumerate(obj.data.materials)]
                    materials_archive = dict_previous_objects[name_short]["mat"]
                    if len(materials_new) == len(materials_archive):
                        for i, material_slot in materials_new:
                            obj.data.materials[i] = materials_archive[i][1]
                    else:
                        assign_missing_mat(obj)
                else:
                    assign_missing_mat(obj)

    else:
        selected_model = pipe_tool_all.model_selector
        file_anm_version = os.path.join(dir_pipe_anm, selected_model,
                                        'versions', f'{selected_model}.{mdl_version}.json')

        with open(file_anm_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)
        mdl_version = dict_mdl_version['version']
        # TODO is previous model version json version or .blend version?

        previous_mdl_variations_of_txt_var = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
        mdl_variations_of_txt_var = [key for key in dict_mdl_variations
                                     if txt_var in dict_mdl_variations[key]
                                     or '*' in dict_mdl_variations[key]]

        # IF UPDATE IS REQUIRED
        if new_mdl_package_type != current_mdl_package_type \
                or mdl_version != current_mdl_version \
                or previous_mdl_variations_of_txt_var != mdl_variations_of_txt_var:

            # Archive Data about objects
            dict_previous_objects = archive_for_update(mdl_version, current_mdl_collection)

            # Import objects and update data
            objects, _ = import_model(dict_mdl_package, dir_asset, dict_mdl_variations, txt_var, new_mdl_package_type)

            for obj in objects:
                name_parts = obj.name.split('.')
                if 'sd' == name_parts[-1][0:2]:
                    name_short = '.'.join(name_parts[0:-1])
                else:
                    name_short = obj.name
                print(name_short)
                print(dict_previous_objects)
                if name_short in dict_previous_objects and obj.data.materials:
                    materials_new = [[i, material_slot] for i, material_slot in enumerate(obj.data.materials)]
                    materials_archive = dict_previous_objects[name_short]["mat"]
                    if len(materials_new) == len(materials_archive):
                        for i, material_slot in materials_new:
                            obj.data.materials[i] = materials_archive[i][1]
                    else:
                        assign_missing_mat(obj)
                else:
                    assign_missing_mat(obj)

# TODO also update if switching from MDL to ANM or reverse


def update_textures():
    global root, project, asset, discipline, dir_asset, dir_pipe_txt, txt_var

    #asset_collections = [x for x in bpy.data.collections if x.name.split('.')[0] == asset]

    dir_txt_package = os.path.join(dir_pipe_txt, str(txt_var), 'txt_package')

    global discipline
    channels_json = [x for x in os.listdir(dir_txt_package)
                     if os.path.isfile(os.path.join(dir_txt_package, x))]

    existing_textures = bpy.data.images

    for channel_json in channels_json:
        channel = channel_json.split('.')[0]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)

        if dir_channel_textures is not None:
            textures = os.listdir(dir_channel_textures)
            tmp = [x.split('.')[-1] for x in textures]  # if x.split('.')[-1] not in filetypes]
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

            filepath = os.path.join(dir_channel_textures, textures_of_filetype[0])
            if channel in existing_textures:
                image = bpy.data.images[channel]
                previous_filepath = image.filepath
                previous_filepath_parts = [str(x) for x in os.path.normpath(image.filepath).split(os.sep)]
                new_filepath = os.path.join(dir_channel_textures, textures_of_filetype[0]) #previous_filepath_parts[-1])

                # Don't update if the source directory is the same
                if previous_filepath != new_filepath:
                    image.filepath = new_filepath

            else:
                files = [{"name": texture} for texture in textures_of_filetype]
                load_image(dir_channel_textures, filepath, files, channel, textures_of_filetype[0])


def load_remaining_textures(dir_txt_package, previously_loaded_channels, ):
    global discipline, dir_asset
    channels_json = [x for x in os.listdir(dir_txt_package)
                     if os.path.isfile(os.path.join(dir_txt_package, x))]

    for channel_json in channels_json:
        channel = channel_json.split('.')[0]
        if channel not in previously_loaded_channels:
            dir_channel_textures = get_channel_dir(dir_txt_package, channel)
            if dir_channel_textures is not None:
                setup_texture(dir_channel_textures, None, None, None, channel)


def import_model(dict_mdl_package, dir_asset, dict_mdl_variations, txt_variation, mdl_type):
    global asset, discipline, project, root

    #~file_anm_version = os.path.join(dir_pipe_mdl, 'versions', f'{asset}.{mdl_version}.json')
    # --- MODEL ---------
    mdl_version = dict_mdl_package[discipline]
    pipe_tool_all = bpy.context.scene.pipe_tool_all
    selected_model = pipe_tool_all.model_selector

    if mdl_type == 'MDL':
        file_anm_version = os.path.join(dir_pipe_mdl, 'versions', f'{asset}.{mdl_version}.json')

        with open(file_anm_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)
        mdl_version = dict_mdl_version['version']
        dir_mdl_version = os.path.join(dir_asset, 'mdl', '.pantry', mdl_version)
        blend_mdl_version = os.path.join(dir_mdl_version, f'{asset}.blend')
    else:
        file_anm_version = os.path.join(dir_pipe_anm, selected_model,
                                        'versions', f'{selected_model}.{mdl_version}.json')

        with open(file_anm_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)
        mdl_version = dict_mdl_version['version']
        dir_mdl_version = os.path.join(dir_asset, 'anm', '.pantry', mdl_type, mdl_version)
        blend_mdl_version = os.path.join(dir_mdl_version, f'{mdl_type}.blend')

    blend_mdl_collection = os.path.join(blend_mdl_version, 'Collection', asset)

    bpy.ops.wm.append(directory=f'{blend_mdl_version}\\Collection\\', filepath=f'{asset}.blend', filename=asset,
                      autoselect=True)
    objects = [x for x in bpy.context.selected_objects]

    # link to main scene collection instead of sub-collection
    for col in bpy.data.collections:
        if asset in col.children:
            col.children.unlink(bpy.data.collections[asset])
    bpy.data.collections[asset].use_fake_user = True
    try:
        bpy.context.scene.collection.children.unlink(bpy.data.collections[asset])
    except RuntimeError:
        pass

    mdl_variations_of_txt_var = create_collections_and_view_layers(dict_mdl_variations, txt_variation, objects)

    # ADD VERSION NUMBER TO COLLECTION NAME
    if mdl_type == 'MDL':
        bpy.data.collections[asset].name = f'{asset}.*.{txt_variation}.mdl.{mdl_version}'
    else:
        bpy.data.collections[asset].name = f'{asset}.*.{txt_variation}.{mdl_type}.{mdl_version}'

    # Set up clean render camera
    for camera in bpy.data.cameras:
        bpy.data.cameras.remove(camera)

    objects_of_asset = [x for x in bpy.data.objects if asset in x.name and x.library is None]
    for obj in objects_of_asset:
        obj.select_set(True)
    create_camera()
    bpy.ops.object.select_all(action='DESELECT')

    return objects, mdl_variations_of_txt_var


def create_collections_and_view_layers(dict_mdl_variations, txt_variation, objects):
    # Create collections and scenes for model variations
    mdl_variations_of_txt_var = [key for key in dict_mdl_variations
                                 if txt_variation in dict_mdl_variations[key] or
                                 '*' in dict_mdl_variations[key]]
    collections = []
    # CREATE COLLECTIONS AND VIEW LAYERS
    for mdl_var in mdl_variations_of_txt_var:
        new_col = bpy.data.collections.new(f'{asset}.{mdl_var}.{txt_variation}')
        new_col.use_fake_user = True

        bpy.context.scene.collection.children.link(new_col)
        collections.append(new_col)
        if mdl_var not in [x.name for x in bpy.context.scene.view_layers]:
            bpy.context.scene.view_layers.new(name=mdl_var)

    default_view_layer = bpy.context.view_layer
    default_view_layer.use = False

    # VIEW LAYER COLLECTION VISIBILITY
    for mdl_var in mdl_variations_of_txt_var:
        variation_layer = bpy.context.scene.view_layers[mdl_var]
        bpy.context.window.view_layer = variation_layer

        for col_var in collections:
            bpy.context.view_layer.active_layer_collection = \
                bpy.context.view_layer.layer_collection.children[col_var.name]
            if col_var.name == f'{asset}.{mdl_var}.{txt_variation}':
                bpy.context.view_layer.active_layer_collection.exclude = False
            else:
                bpy.context.view_layer.active_layer_collection.exclude = True

    # DELETE UNUSED VARIATION VIEW LAYERS
    view_layer_names = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
    for view_layer_name in view_layer_names:
        if view_layer_name not in mdl_variations_of_txt_var:
            bpy.context.scene.view_layers.remove(bpy.context.scene.view_layers[view_layer_name])

    bpy.context.window.view_layer = default_view_layer

    # Assign objects to collections
    for obj in objects:
        obj_mdl_var = [x for x in obj.name.split('.')[1]]
        mdl_var_overlap = [x for x in obj_mdl_var if x in mdl_variations_of_txt_var]
        if '*' in obj_mdl_var or len(mdl_var_overlap) != 0:
            # ASSIGN OBJECTS TO MODEL VARIATION COLLECTIONS
            if '*' in obj_mdl_var:
                for mdl_var in mdl_variations_of_txt_var:
                    bpy.data.collections[f'{asset}.{mdl_var}.{txt_variation}'].objects.link(obj)
            elif len(mdl_var_overlap) != 0:
                for mdl_var in mdl_var_overlap:
                    bpy.data.collections[f'{asset}.{mdl_var}.{txt_variation}'].objects.link(obj)

    # Deselect all items assigned to view layers
    for vl in bpy.context.scene.view_layers:
        bpy.context.window.view_layer = vl
        bpy.ops.object.select_all(action='DESELECT')

    bpy.context.window.view_layer = default_view_layer

    return mdl_variations_of_txt_var

# TODO model export ignore the modifiers after exporting the .blend file, include SD level in name? Or have it set up in
# TODO allow linking of materials from other shading variations (like texture linking)


def initialise_texture_variation(dict_mdl_package, dict_mdl_variations, mdl_type):
    global root, project, asset, discipline, dir_asset, dir_pipe_txt, txt_var

    objects, mdl_variations_of_txt_var = import_model(dict_mdl_package, dir_asset, dict_mdl_variations, txt_var,
                                                      mdl_type)

    # CREATE DEFAULT MATERIAL
    mat = bpy.data.materials.new(name=f'{asset}.{txt_var}.main')
    mat.use_nodes = True

    # ASSIGN MATERIAL
    for obj in objects:
        obj_mdl_var = [x for x in obj.name.split('.')[1]]
        mdl_var_overlap = [x for x in obj_mdl_var if x in mdl_variations_of_txt_var]
        if '*' in obj_mdl_var or len(mdl_var_overlap) != 0:
            # ASSIGN MATERIAL
            if obj.data.materials:
                for i, material_slot in enumerate(obj.data.materials):
                    obj.data.materials[i] = mat
            else:
                obj.data.materials.append(mat)
        else:
            pass
            # obj.hide_set(True)

    # --- TEXTURE ---------
    # CONNECTIONS FILE
    # READ FILE
    file_connections = os.path.join(dir_pipe_txt, str(txt_var), 'txt_connections.json')
    with open(file_connections, 'r') as json_file:
        dict_connections = json.load(json_file)

    dir_txt_package = os.path.join(dir_pipe_txt, str(txt_var), 'txt_package')

    previously_loaded_channels = []
    if dict_connections["base_color"] != "":
        channel = dict_connections["base_color"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 0, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    if dict_connections["metallic"] != "":
        channel = dict_connections["metallic"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 4, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    if dict_connections["specular_roughness"] != "":
        channel = dict_connections["specular_roughness"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 7, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    if dict_connections["transmission"] != "":
        channel = dict_connections["transmission"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 15, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    if dict_connections["emission"] != "":
        channel = dict_connections["emission"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 17, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    if dict_connections["normal"] != "":
        channel = dict_connections["normal"]
        dir_channel_textures = get_channel_dir(dir_txt_package, channel)
        if dir_channel_textures is not None:
            setup_texture(dir_channel_textures, mat, 20, len(previously_loaded_channels), channel)
            previously_loaded_channels.append(channel)

    load_remaining_textures(dir_txt_package, previously_loaded_channels)

# TODO restructure definitions into classes


def get_channel_dir(dir_txt_package, channel):
    global discipline, dir_asset, dir_txt, txt_var
    txt_variation = txt_var  # necessary to avoid switching TXT variation of this scene, by linking external
    channels_json = [x for x in os.listdir(dir_txt_package)
                     if os.path.isfile(os.path.join(dir_txt_package, x))]

    channels_json_native = [x for x in channels_json
                            if os.path.isdir(os.path.join(dir_txt_package, x.split('.')[0]))]

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
    version = dict_channel[discipline]
    if version != '':
        file_channel_version = os.path.join(dir_txt_package, channel, f'{channel}.{version}.json')

        with open(file_channel_version, 'r') as json_file:
            dict_channel_version = json.load(json_file)

        dir_channel_textures = os.path.join(dir_txt, '.pantry', str(txt_variation), channel,
                                            dict_channel_version["channel_version"])

        return dir_channel_textures

    else:
        return None


def load_image(dir_channel_textures, filepath, files, name, file_1):
    bpy.ops.image.open(filepath=filepath, directory=dir_channel_textures, files=files, relative_path=False,
                       show_multiview=False)
    texture_import = bpy.data.images[file_1]

    texture_import.name = name
    texture_import.use_fake_user = True

    colour_space = file_1.split('.')[1]
    spaces = [x.name for x in
              type(texture_import).bl_rna.properties['colorspace_settings'].fixed_type.properties['name'].enum_items]
    if colour_space in spaces:
        texture_import.colorspace_settings.name = colour_space

    return texture_import


def setup_texture(dir_channel_textures, mat, slot, count, name):
    textures = os.listdir(dir_channel_textures)
    tmp = [x.split('.')[-1] for x in textures]  # if x.split('.')[-1] not in filetypes]
    filetypes = list(set(tmp))
    if len(filetypes) != 0:

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

        texture_import = bpy.data.images.get(textures_of_filetype[0])
        if texture_import is None:
            # Set variables for import of textures
            filepath = os.path.join(dir_channel_textures, textures_of_filetype[0])
            files = [{"name": texture} for texture in textures_of_filetype]
            # Import textures
            texture_import = load_image(dir_channel_textures, filepath, files, name, textures_of_filetype[0])

        if mat is not None:
            # Create New Texture node
            material_nodes = mat.node_tree.nodes

            texture_node = material_nodes.get(name)

            if texture_node is None:
                texture_node = material_nodes.new("ShaderNodeTexImage")
                texture_node.location = (-690, 420 + count * -280)
                texture_node.image = texture_import
                texture_node.name = name
                texture_node.label = name

            # Connect Texture
            shader_node = material_nodes["Principled BSDF"]
            if slot != 20:
                mat.node_tree.links.new(texture_node.outputs[0], shader_node.inputs[slot])
            else:
                normal_node = material_nodes.new("ShaderNodeNormalMap")
                normal_node.location = (-300, 420 + count * -280)
                mat.node_tree.links.new(texture_node.outputs[0], normal_node.inputs[1])
                mat.node_tree.links.new(normal_node.outputs[0], shader_node.inputs[slot])

# TODO create UI for selecting model variations
# TODO import all textures, even those that don't need to be connected by default
# TODO set default render settings
# TODO set default light setup
# TODO ui for selecting which variations to actively render

# TODO texture variation as scene? (needs separate geo... or can it do material overridees?)

# TODO update colourspace when textures are updated and it differs


all_classes = (PipeSettingsAll, AllOpenOutput, AllUiRenderSettings, AllTurntableRender, AllSettingsApply,
               AllSetupTurntable, AllFiletypeApply,
               AllTurntableUpdate, AllUiTurntable)
mdl_classes = (MdlRemoveFrom, AllSettingsVariationGet, AllSettingsVariationSet, MdlSelectExclusive,
               MdlVariationDelete, MdlVariationAdd, MdlVariationApply,
               MdlExport, MdlUiVariation, MdlUiExport)
txt_classes = (AllSettingsVariationGet, AllSettingsVariationSet)
shd_classes = (ShdExport, ShdUpdateAsset, ShdSetup,
               ShdUiPackageManagement, AllSettingsVariationGet, AllSettingsVariationSet, ShdUiExport)


def register():
    """ Is run when enabling the plugin
    """
    global discipline

    for item in all_classes:
        bpy.utils.register_class(item)

    bpy.types.Scene.pipe_tool_all = PointerProperty(type=PipeSettingsAll)

    if discipline == 'mdl':
        bpy.utils.register_class(PipeSettingsMdl)
        bpy.types.Scene.pipe_tool = PointerProperty(type=PipeSettingsMdl)
        for mdl_class in mdl_classes:
            bpy.utils.register_class(mdl_class)

    if discipline == 'txt':
        if catch_loading_scene not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(catch_loading_scene)
        if catch_loading_scene not in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.append(catch_loading_scene)

        bpy.utils.register_class(PipeSettingsTxt)
        bpy.types.Scene.pipe_tool = PointerProperty(type=PipeSettingsTxt)

        for txt_class in txt_classes:
            bpy.utils.register_class(txt_class)

    if discipline == 'shd':
        catch_loading_scene('a')
        if catch_loading_scene not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(catch_loading_scene)
        if catch_loading_scene not in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.append(catch_loading_scene)

        bpy.utils.register_class(PipeSettingsShd)
        bpy.types.Scene.pipe_tool = PointerProperty(type=PipeSettingsShd)

        for shd_class in shd_classes:
            bpy.utils.register_class(shd_class)

    catch_loading_scene('')


def unregister():
    """ Is run when disabling the plugin
    """
    global discipline

    for item in all_classes:
        bpy.utils.unregister_class(item)

    if discipline == 'mdl':
        bpy.utils.unregister_class(PipeSettingsMdl)
        for mdl_class in mdl_classes:
            bpy.utils.unregister_class(mdl_class)

    if discipline == 'txt':
        bpy.utils.unregister_class(PipeSettingsTxt)
        for txt_class in txt_classes:
            bpy.utils.unregister_class(txt_class)

    if discipline == 'shd':
        if catch_loading_scene in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(catch_loading_scene)
        if catch_loading_scene in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.remove(catch_loading_scene)

        bpy.utils.unregister_class(PipeSettingsShd)

        for shd_class in shd_classes:
            bpy.utils.unregister_class(shd_class)


if __name__ == '__main__':
    pass
    register()
    # unregister()

# only export visible
# create * collection if missing for both add and set?
# if removed from sub collection it won't be added to star

# TODO is previous model version json version or .blend version?