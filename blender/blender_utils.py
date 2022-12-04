import bpy
import os
import json
import blender.blender_variables as b_vars
from bpy.app.handlers import persistent


def duplicate_linked_obj(obj_src):
    """Duplicates a linked external object."""
    obj_new = obj_src.copy()
    # obj_new.data = obj_src.data.copy()
    bpy.data.collections['Assets'].objects.link(obj_new)
    return obj_new


def link_asset(dir_build, asset_name, mdl_var, txt_var):
    """Links the given collection of an Asset into the current scene.

    Args:
        dir_build(str): Path to the projects build directory.
        asset_name(str): Name of the asset to be imported.
        mdl_var(str): Letter of the MDL variation to be used.
        txt_var(str): Letter of the TXT/SHD variation to be used.
    """
    dict_version, pipe_version = get_current_pipe_dict(dir_build, asset_name, 'shd', 'shd_publish', txt_var)
    file_version = dict_version['version']

    fl_shd = os.path.join(dir_build, asset_name, 'shd', '.pantry', txt_var, file_version, f'{asset_name}.blend')
    link_dir = f'{fl_shd}\Collection\\'
    link_filepath = f'{asset_name}.blend'
    link_filename = f'{asset_name}.{mdl_var}.{txt_var}'

    # Check if this version of this asset is already in the scene.
    existing_name = '.'.join([link_filename, pipe_version])
    existing_objects = [x for x in bpy.data.objects if existing_name in x.name]
    if len(existing_objects):
        obj_new = duplicate_linked_obj(existing_objects[0])
        return obj_new
    else:
        other_objs_old = [x for x in bpy.data.objects]

        bpy.ops.wm.link(
            directory=link_dir,
            filepath=link_filepath,
            filename=link_filename,
            autoselect=True
        )
        objs2 = [x for x in bpy.data.objects if x not in other_objs_old]
        if objs2:
            obj_new = [x for x in bpy.data.objects if x not in other_objs_old][0]
            obj_new.name = f'{obj_new.name}.{pipe_version}'
        else:
            obj_new = None

        return obj_new


def get_current_pipe_dict(dir_build, asset_name, discipline, stream, txt_var):
    """Gathers the content of the current asset.version.json. E.g. .pipeline/mdl/versions/prpAnduril.v001.json

    Args:
        dir_build(str):  Path to the projects build directory.
        asset_name(str): Name of the asset. E.g.: prpAnduril
        discipline(str): Type of discipline for which the version is being looked up. E.g.: mdl
        stream(str): For which stream the active version should be gathered.
        txt_var: TXT/SHD variation that should be looked up. None if not applicable.

    Returns:
        dict_version(dict): Contains the information of the json file.
    """
    if txt_var is None:
        dir_pipe = os.path.join(dir_build, asset_name, '.pipeline', discipline)
    else:
        dir_pipe = os.path.join(dir_build, asset_name, '.pipeline', discipline, txt_var)
    fl_package = os.path.join(dir_pipe, f'{discipline}_package.json')

    with open(fl_package, 'r') as fl_content:
        dict_package = json.load(fl_content)
    version = dict_package[stream]
    fl_version = os.path.join(dir_pipe, 'versions', f'{asset_name}.{version}.json')

    with open(fl_version, 'r') as fl_content:
        dict_version = json.load(fl_content)

    return dict_version, version


def apply_sensor_preset(pipe_tool_all, engine, preset):
    """Called only on initial automatic initiation of render settings preset."""
    render_settings = b_vars.dict_render_settings[engine][preset]
    sensor_setting = [
        x for x in b_vars.dict_sensors["sensors"] if render_settings['sensor'] in x
    ][0]
    pipe_tool_all.resolution = sensor_setting


class RenderSettings:
    def __init__(self):
        #file_config = '.\\config\\config_render_settings.json'
        file_config = f'.\\projects\\{b_vars.project}-{b_vars.project_abbr}\\config_render_settings.json'

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

    def cycles_layout(self):
        bpy.context.scene.render.engine = 'CYCLES'
        self.cycles_settings = self.dict_config["cycles"]["layout"]
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
        bpy.context.space_data.lock_camera = self.eevee_settings["lock_camera_to_view"]

        # self.always_apply()

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
        bpy.context.scene.cycles.caustics_reflective = self.cycles_settings["caustics_reflective"]
        bpy.context.scene.cycles.caustics_refractive = self.cycles_settings["caustics_refractive"]

        bpy.context.scene.render.film_transparent = self.cycles_settings["film_transparent"]

        try:  # 2.93
            bpy.context.scene.render.tile_x = self.cycles_settings["tile_x"]
            bpy.context.scene.render.tile_y = self.cycles_settings["tile_y"]
            bpy.context.scene.cycles.use_auto_tile = True

        except:  # 3.0
            bpy.context.scene.cycles.tile_size = self.cycles_settings["tile_x"]
            bpy.context.scene.cycles.use_auto_tile = False

        bpy.context.scene.cycles.blur_glossy = self.cycles_settings["blur_glossy"]

        # self.always_apply()
        bpy.context.space_data.lock_camera = self.cycles_settings["lock_camera_to_view"]

        bpy.context.scene.cycles.use_adaptive_sampling = self.cycles_settings["use_adaptive_sampling"]
        bpy.context.scene.cycles.adaptive_threshold = self.cycles_settings["adaptive_threshold"]
        bpy.context.scene.cycles.adaptive_min_samples = self.cycles_settings["adaptive_min_samples"]

    #def always_apply(self):
        #bpy.context.space_data.lock_camera = True

        # bpy.context.scene.render.resolution_x = self.cycles_settings["resolution_x"]
        # bpy.context.scene.render.resolution_y = self.cycles_settings["resolution_y"]


@persistent
def catch_loading_scene(_):
    global scene_has_been_loaded, txt_var, mdl_variations  # asset, scene_is_turntable
    #pipe_tool_all = bpy.context.scene.pipe_tool_all

    reverse = True
    #current_render_settings = f'cycles,shading'
    for col in bpy.data.collections:
        if b_vars.department == 'build':
            if b_vars.asset in col.name:
                b_vars.scene_has_been_loaded = True
                try:
                    txt_var = str([x.name.split('.')[2] for x in bpy.data.collections if x.name.split('.')[0] == b_vars.asset
                                   and x.name.count('.') >= 4][0])
                except IndexError:
                    txt_var = None
                mdl_variations = [x.name for x in bpy.context.scene.view_layers if len(x.name) == 1]
                reverse = False
                #pipe_tool_all.filetype =
                break
        else:  # Sequence
            if 'Assets' in col.name:
                b_vars.scene_has_been_loaded = True
                reverse = False

    if reverse:
        b_vars.scene_has_been_loaded = False
        txt_var = None
    else:
        print("AAA", [obj.name for obj in bpy.data.objects])
        if 'rotation_parent' in [obj.name for obj in bpy.data.objects]:
            print("C")
            b_vars.scene_is_turntable = True
            #current_render_settings = f'cycles,turntable'

    #pipe_tool_all.render_settings = current_render_settings
