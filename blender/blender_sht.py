import bpy
import os
from pipe_utils_file_management import list_assets
from pipe_utils_file_management import get_build_dir
from .blender_utils import link_asset, get_current_pipe_dict, RenderSettings, apply_sensor_preset
import blender.blender_variables as b_vars

asset = os.getenv('PIPE_ASSET')
sequence = os.getenv('PIPE_SEQUENCE')
shot = os.getenv('PIPE_SHOT')
user = os.getenv('PIPE_USER')

dir_build = get_build_dir(b_vars.root, b_vars.project)

mdl_variations = []
txt_variations = []

var_items = [
        ("A", "A", ""),
        ("B", "B", ""),
        ("C", "C", ""),
        ("D", "D", ""),
        ("E", "E", ""),
        ("F", "F", ""),
        ("G", "G", ""),
        ("H", "H", ""),
        ("I", "I", ""),
        ("J", "J", ""),
        ("K", "K", ""),
        ("L", "L", ""),
        ("M", "M", ""),
        ("N", "N", ""),
        ("O", "O", ""),
        ("P", "P", ""),
        ("Q", "Q", ""),
        ("R", "R", ""),
        ("S", "S", ""),
        ("T", "T", ""),
        ("U", "U", ""),
        ("V", "V", ""),
        ("W", "W", ""),
        ("X", "X", ""),
        ("Y", "Y", ""),
        ("Z", "Z", "")
    ]


def get_applicable_assets():
    """Filters for assets that actually have a shading pantry directory."""
    # rough exclusion of unpublished items
    assets_unfiltered = list_assets(b_vars.root, dir_build)
    assets_filtered = [
        asset_name for asset_name in assets_unfiltered
        if os.listdir(os.path.join(dir_build, asset_name, 'shd', '.pantry'))
    ]
    return assets_filtered


class ShotUiMain(bpy.types.Panel):
    bl_idname = 'PIPE_PT_all'
    bl_label = ''
    bl_category = f'Open Pipe {b_vars.discipline.upper()}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Scene Management")

    def draw(self, context):
        # global scene_has_been_loaded

        layout = self.layout
        row01 = layout.row()
        row01.label(text=f'Current Sequence & Shot')
        row02 = layout.row()
        row02.label(text=f'{sequence} / {shot}')

        row_separator1 = layout.row()
        row_separator1.separator()

        row10 = layout.row()
        row10.label(text='Asset Control')
        row11 = layout.row()
        row11.operator('pipe.sht_add_asset')
        row20 = layout.row()
        #row2.label(text=f'{sequence} / {shot}')
        row20.operator('pipe.sht_replace_asset')
        row21 = layout.row()
        row21.operator('pipe.sht_list_variations')
        row21.operator('pipe.sht_change_var')
        #row2.menu('pipe.mdl_var_menu')

        row_separator2 = layout.row()
        row_separator2.separator()

        row31 = layout.row()
        row31.label(text='Version Control')
        row32 = layout.row()
        row32.operator('pipe.sht_update_asset')
        row33 = layout.row()
        row33.operator('pipe.sht_update_assets')


class ShotAddAsset(bpy.types.Operator):
    bl_idname = 'pipe.sht_add_asset'
    bl_label = 'Add Asset'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Adds an asset to the scene.'

    #global scene_has_been_loaded

    assets_filtered = get_applicable_assets()
    items_assets = [(asset, asset, '') for asset in assets_filtered]

    # text: bpy.props.StringProperty(name="Enter Text", default="")
    asset: bpy.props.EnumProperty(name='Asset', items=items_assets)

    #mdl_var: bpy.props.StringProperty(name='MDL Variation', default='A')
    mdl_var: bpy.props.EnumProperty(name='MDL Variation', items=var_items)
    txt_var: bpy.props.EnumProperty(name='TXT Variation', items=var_items)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        global mdl_variations, txt_variations, asset
        b_vars.asset = self.asset
        dict_pipe_mdl, _ = get_current_pipe_dict(dir_build, self.asset, 'mdl', 'shd', None)
        mdl_variations = dict_pipe_mdl['variations']
        txt_variations = [x for x in os.listdir(os.path.join(dir_build, self.asset, '.pipeline', 'shd'))]
        # print(f"Available MDL variations: {mdl_variations}")
        if self.mdl_var in mdl_variations and self.txt_var in txt_variations:
            print(f"LINK {self.asset}.{self.mdl_var}.{self.txt_var}")
            asset_collection = check_main_collections()
            bpy.context.view_layer.active_layer_collection = get_layer_collection(
                bpy.context.view_layer.layer_collection, asset_collection.name
            )
            obj_new = link_asset(dir_build, self.asset, self.mdl_var, self.txt_var)
            if obj_new is not None:
                cursor = bpy.context.scene.cursor
                obj_new.location = cursor.location

                if b_vars.scene_has_been_loaded is False:
                    scene = context.scene
                    pipe_tool_all = scene.pipe_tool_all
                    pipe_tool_all.render_settings = 'cycles,layout'
                    apply_sensor_preset(pipe_tool_all, 'cycles', 'layout')
                #    RenderSettings().cycles_layout()

                b_vars.scene_has_been_loaded = True
                if len(mdl_variations) > 1 or len(txt_variations) > 1:
                    mdl_vars = ', '.join(mdl_variations)
                    txt_vars = ', '.join(txt_variations)
                    msg = f"Import successful.\nMultiple variations available for this asset: "
                    if len(mdl_variations) > 1:
                        msg = msg + f"\nMDL:  {mdl_vars} "
                    if len(txt_variations) > 1:
                        msg = msg + f"\nTXT:  {txt_vars}"

                    self.report({'ERROR'}, msg)

                return {'FINISHED'}
            else:
                self.report(
                    {'ERROR'},
                    f"Import not successful."
                )
                return {'CANCELLED'}

        else:
            self.report(
                {'ERROR'},
                f"This combination of variations ({self.mdl_var}.{self.txt_var}) doesn't exist for this asset."
                f"Available variations: MDL: {mdl_variations} TXT: {txt_variations}"
            )
            return {'CANCELLED'}


"""
class SequenceSettingsVariations(bpy.types.PropertyGroup):
    mdl_var: bpy.props.EnumProperty(
        name='MDL Variation',
        items=[("A", "A", "")],
        default=None
    )
"""


class MdlVarMenu(bpy.types.Menu):
    bl_idname = 'pipe.mdl_var_MT_menu'
    bl_label = "TESTESTSET"

    def draw(self, context):
        global mdl_variations
        # mdl_var_items = [(mdl_var, mdl_var, '') for mdl_var in mdl_variations]
        layout = self.layout()

        for mdl_var in mdl_variations:
            layout.label(text=f"scene.{mdl_var}")


class ShotChangeVariation(bpy.types.Operator):
    bl_idname = 'pipe.sht_change_var'
    bl_label = 'Swap Variation'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Replaces the selected asset with another MDL.TXT variation of the same asset.'

    #pipe_tool_sht = bpy.context.scene.pipe_tool_sht

    #mdl_var: pipe_tool_sht.mdl_var
    #mdl_var: bpy.props.EnumProperty(name='MDL Variation', items=mdl_var_items, default=None)
    #mdl_var: bpy.props.StringProperty(name='MDL Variation', default='A')
    mdl_var: bpy.props.EnumProperty(name='MDL Variation', items=var_items)
    txt_var: bpy.props.EnumProperty(name='TXT Variation', items=var_items)

    def invoke(self, context, event):
        #self.mdl_var_items = [(mdl_var, mdl_var, '') for mdl_var in mdl_variations]
        # success = context.window_manager.invoke_props_dialog(self)
        #self.mdl_var_items = [(mdl_var, mdl_var, '') for mdl_var in mdl_variations]
        #print("IAIS", self.mdl_var_items)
        #test = self.mdl_var.add()
        #self.mdl_var_items.append(mdl_var_items[0])
        obj_old = bpy.context.view_layer.objects.active
        # print([x.name for x in bpy.data.collections])
        # print('.'.join(obj_old.name.split('.')[:3]))
        if obj_old is not None:
            if '.'.join(obj_old.name.split('.')[:3]) in [x.name for x in bpy.data.collections]:
                obj_old_name = obj_old.name
                asset = obj_old_name.split('.')[0]

                dict_pipe_mdl, _ = get_current_pipe_dict(dir_build, asset, 'mdl', 'shd', None)
                mdl_variations = dict_pipe_mdl['variations']
                txt_variations = [x for x in os.listdir(os.path.join(dir_build, b_vars.asset, '.pipeline', 'shd'))]
                if len(mdl_variations) > 1 or len(txt_variations) > 1:
                    self.report(
                        {'INFO'},
                        f'MDL: {mdl_variations}, TXT: {txt_variations}'
                    )
                    return context.window_manager.invoke_props_dialog(self)
                else:
                    self.report({'ERROR'}, "This asset has no other MDL or TXT variations.")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, "Given selection is not a linked asset.")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No active selection.")
            return {'CANCELLED'}

    def execute(self, context):

        return replace_asset(self, 1, bpy.context.view_layer.objects.active)


class ShotReplaceAsset(bpy.types.Operator):
    bl_idname = 'pipe.sht_replace_asset'
    bl_label = 'Replace Asset'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Replaces the selected asset with a different one.'

    mdl_var_items = [(mdl_var, mdl_var, '') for mdl_var in mdl_variations]
    txt_var_items = [(txt_var, txt_var, '') for txt_var in txt_variations]
    # pipe_tool_sht = bpy.context.scene.pipe_tool_sht

    # mdl_var: pipe_tool_sht.mdl_var
    # mdl_var: bpy.props.EnumProperty(name='MDL Variation', items=mdl_var_items, default=None)
    assets_filtered = get_applicable_assets()
    items_assets = [(asset_old, asset_old, '') for asset_old in assets_filtered]
    asset: bpy.props.EnumProperty(name='Asset', items=items_assets)  # , default=1)
    # mdl_var: bpy.props.StringProperty(name='MDL Variation', default='A')
    mdl_var: bpy.props.EnumProperty(name='MDL Variation', items=var_items)
    txt_var: bpy.props.EnumProperty(name='TXT Variation', items=var_items)

    def invoke(self, context, event):
        obj_old = bpy.context.view_layer.objects.active
        if obj_old is not None:
            if '.'.join(obj_old.name.split('.')[:3]) in [x.name for x in bpy.data.collections]:
                return context.window_manager.invoke_props_dialog(self)
            else:
                self.report({'ERROR'}, "Given selection is not a linked asset.")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No active selection.")
            return {'CANCELLED'}

    def execute(self, context):
        return replace_asset(self, False, bpy.context.view_layer.objects.active)


class ShotUpdateAsset(bpy.types.Operator):
    bl_idname = 'pipe.sht_update_asset'
    bl_label = 'Update Selected'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Checks if the selected asset needs to be updated to a different version.'

    def execute(self, context):
        obj_old = bpy.context.view_layer.objects.active
        if obj_old is not None:
            if bpy.context.object.mode == 'OBJECT':
                if obj_old.name.count('.') >= 3:
                    obj_old_name = obj_old.name
                    b_vars.asset = obj_old_name.split('.')[0]
                    self.mdl_var = obj_old_name.split('.')[1]
                    self.txt_var = obj_old_name.split('.')[2]
                    pipe_version_old = obj_old_name.split('.')[3]

                    dict_version, pipe_version = get_current_pipe_dict(
                        dir_build, b_vars.asset, 'shd', 'shd_publish', self.txt_var
                    )

                    if pipe_version_old != pipe_version:
                        return replace_asset(self, 2, obj_old)
                    else:
                        self.report({'ERROR'}, "No updates for this asset.")
                        return {'CANCELLED'}
                else:
                    self.report({'ERROR'}, "No valid linked asset has been selected.")
                    return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No active selection.")
            return {'CANCELLED'}


class ShotUpdateAssets(bpy.types.Operator):
    bl_idname = 'pipe.sht_update_assets'
    bl_label = 'Update All'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Checks if any of the assets in the scene need to be updated to a different version.'

    def execute(self, context):
        objs = bpy.data.objects
        if b_vars.scene_has_been_loaded:
            updated_assets = []
            qualifying_objs = []
            for obj in objs:
                if obj.name.count('.') >= 3:
                    assets_filtered = get_applicable_assets()
                    b_vars.asset = obj.name.split('.')[0]
                    self.mdl_var = obj.name.split('.')[1]
                    self.txt_var = obj.name.split('.')[2]
                    pipe_version_old = obj.name.split('.')[3]
                    if b_vars.asset in assets_filtered and len(self.mdl_var) == 1 and len(self.txt_var) == 1:
                        qualifying_objs.append(obj.name)
                        dict_version, pipe_version = get_current_pipe_dict(
                            dir_build, b_vars.asset, 'shd', 'shd_publish', self.txt_var
                        )
                        if pipe_version_old != pipe_version:
                            updated_assets.append(f'{obj.name} -> {pipe_version}')
                            replace_asset(self, 2, obj)
            if updated_assets:
                print('\n---------------------------------------------')
                print('The following assets were found in the scene:')
                print(qualifying_objs)
                print('\n')
                updates = '\n'.join(updated_assets)
                print(updates)

                self.report(
                    {'INFO'},
                    f"The following assets were out of date and have been updated:\n{updates}"
                )
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "No updates required.")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No scene has been loaded.")
            return {'CANCELLED'}


class ShotListVariations(bpy.types.Operator):
    bl_idname = 'pipe.sht_list_variations'
    bl_label = 'List Variations'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Lists all the available MDL and TXT variations for the selected asset.'

    def execute(self, context):
        obj_old = bpy.context.view_layer.objects.active
        if obj_old is not None:
            if '.'.join(obj_old.name.split('.')[:3]) in [x.name for x in bpy.data.collections]:
                assets_filtered = get_applicable_assets()
                b_vars.asset = obj_old.name.split('.')[0]
                if b_vars.asset in assets_filtered:
                    dict_pipe_mdl, _ = get_current_pipe_dict(dir_build, b_vars.asset, 'mdl', 'shd', None)
                    l_mdl_variations = dict_pipe_mdl['variations']
                    l_txt_variations = [x for x in os.listdir(os.path.join(dir_build, b_vars.asset, '.pipeline', 'shd'))]
                    mdl_variations = ', '.join(l_mdl_variations)
                    txt_variations = ', '.join(l_txt_variations)
                    self.report(
                        {'ERROR'},
                        f'{b_vars.asset} Variations:  \nMDL: {mdl_variations}  \nTXT: {txt_variations}'
                    )
                    return {'FINISHED'}
                else:
                    self.report({'ERROR'}, "Selected object is not an asset.")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, "Selected object is not an asset.")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No asset has been selected.")
            return {'CANCELLED'}


def get_layer_collection(layer_collection, asset_collection):
    found = None
    if layer_collection.name == asset_collection:
        return layer_collection
    for layer in layer_collection.children:
        found = get_layer_collection(layer, asset_collection)
        if found:
            return found


def check_main_collections():
    """Checks for the existence of the 'Assets' and 'Lights' collections and creates them if necessary."""
    collections = [x for x in bpy.data.collections if x.library is None]
    collection_names = [x.name for x in collections]

    if 'Assets' not in collection_names:
        if 'Collection' in collection_names:
            asset_collection = bpy.data.collections['Collection']
            asset_collection.name = 'Assets'
        else:
            bpy.data.collections.new('Assets')
            asset_collection = bpy.data.collections['Assets']
            bpy.context.scene.collection.children.link(asset_collection)
    else:
        asset_collection = bpy.data.collections['Assets']

    if 'Lights' not in collection_names:
        bpy.data.collections.new('Lights')
        light_collection = bpy.data.collections['Lights']
        bpy.context.scene.collection.children.link(light_collection)

    return asset_collection


def replace_asset(parent, only_var_change, obj_old):
    """Replaces a linked in Asset with a different one.

    Args:
        parent(class): Reference to parent operator-class.
        only_var_change(int): 0 = full asset change, 1 = only var change, 2 = only version update
    :return:
    """
    con = False
    if bpy.context.object is None:
        con = True
    else:
        if bpy.context.object.mode == 'OBJECT':
            con = True
    if con:
        obj_old_name = obj_old.name
        b_vars.asset = obj_old_name.split('.')[0] if only_var_change else parent.asset
        mdl_var_old = obj_old_name.split('.')[1]
        txt_var_old = obj_old_name.split('.')[2]

        dict_pipe_mdl, _ = get_current_pipe_dict(dir_build, b_vars.asset, 'mdl', 'shd', None)
        mdl_variations = dict_pipe_mdl['variations']
        txt_variations = [x for x in os.listdir(os.path.join(dir_build, b_vars.asset, '.pipeline', 'shd'))]

        if parent.mdl_var in mdl_variations and parent.txt_var in txt_variations:
            if ((parent.mdl_var != mdl_var_old or parent.txt_var != txt_var_old)
                    or obj_old_name.split('.')[0] != b_vars.asset
                    or only_var_change == 2):
                loc = obj_old.location
                rot = obj_old.rotation_euler
                scl = obj_old.scale
                obj_new = link_asset(dir_build, b_vars.asset, parent.mdl_var, parent.txt_var)

                obj_new.location = loc
                obj_new.rotation_euler = rot
                obj_new.scale = scl

                # Keep file clean by deleting old linked asset
                old_asset_collection = bpy.data.collections['.'.join(obj_old.name.split('.')[:3])]
                if (old_asset_collection.users <= 2
                        and (only_var_change != 1 or parent.txt_var != txt_var_old)):
                    bpy.data.libraries.remove(old_asset_collection.library)
                bpy.data.objects.remove(obj_old)

                return {'FINISHED'}
            else:
                parent.report({'ERROR'}, "Given variation is the same as before.")
                return {'CANCELLED'}
        else:
            parent.report({'ERROR'}, "Invalid variation selection given.")
            return {'CANCELLED'}
    else:
        parent.report({'ERROR'}, "Switch to object mode.")
        return {'CANCELLED'}

# TODO set render path?


# TODO auto select asset after import/replace
