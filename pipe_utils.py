# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import json
import shutil
import ctypes
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox


def extend_path(list_parts):
    """ Allows for autocomplete of this often used variation of '.join'

    :param list_parts: List of the parts that need to be joined into a path.
    :return:
    """

    return '/'.join(list_parts)


def json_load_ui_variables(parent, config):
    """ Loads colours from a json file to allow users to modify the colours of the UI without accessing the code.

    :param parent: Class that is calling this function.
    :param config:
    :return:
    """

    with open(config, 'r') as config_file:
        config_file_content = json.load(config_file)

    try:  # variables in ui_defaults.json
        parent.col_bt_bg_default = config_file_content["col_bt_bg_default"]
    except KeyError:
        parent.col_bt_bg_default = '#3d3d3d'

    try:
        parent.col_dd_blue_default = config_file_content["col_dd_blue_default"]
        parent.col_bt_bg_blue = config_file_content["col_bt_bg_blue"]
        parent.col_bt_bg_blue_active = config_file_content["col_bt_bg_blue_active"]
        parent.col_bt_bg_blue_highlight = config_file_content["col_bt_bg_blue_highlight"]
    except KeyError:
        parent.col_bt_bg_blue = '#434359'
        parent.col_dd_blue_default = "#3e4959"
        parent.col_bt_bg_blue_active = "#525265"
        parent.col_bt_bg_blue_highlight = "#484859"

    try:
        parent.col_bt_bg_green = config_file_content["col_bt_bg_green"]
        parent.col_bt_bg_green_highlight = config_file_content["col_bt_bg_green_highlight"]
    except KeyError:
        parent.col_bt_bg_green = '#435943'
        parent.col_bt_bg_green_highlight = '#485948'

    try:
        parent.col_bt_red = config_file_content["col_bt_red"]
        parent.col_bt_red_highlight = config_file_content["col_bt_red_highlight"]
    except KeyError:
        parent.col_bt_red = '#594343'
        parent.col_bt_red_highlight = '#655252'

    try:
        parent.col_bt_petrol = config_file_content["col_bt_petrol"]
        parent.col_bt_petrol_highlight = config_file_content["col_bt_petrol_highlight"]
    except KeyError:
        parent.col_bt_petrol = '#435959'
        parent.col_bt_petrol_highlight = '#526565'

    try:
        parent.col_bt_yellow = config_file_content["col_bt_yellow"]
        parent.col_bt_yellow_highlight = config_file_content["col_bt_yellow_highlight"]
    except KeyError:
        parent.col_bt_petrol = '#808054'
        parent.col_bt_petrol_highlight = '#999965'

    try:
        parent.col_wdw_default = config_file_content["col_wdw_default"]
    except KeyError:
        parent.col_wdw_default = '#333333'

    try:
        parent.col_wdw_title = config_file_content["col_wdw_title"]
    except KeyError:
        parent.col_wdw_title = '#525252'

    try:
        parent.col_wdw_border = config_file_content["col_wdw_border"]
        parent.col_wdw_border_background = config_file_content["col_wdw_border_background"]

    except KeyError:
        parent.col_wdw_border = 'gray10'
        parent.col_wdw_border_background = 'gray15'
    try:
        parent.col_bt_fg_default = config_file_content["col_bt_fg_default"]
    except KeyError:
        parent.col_bt_fg_default = '#d9d9d9'

    try:
        parent.col_bt_bg_active = config_file_content["col_bt_bg_active"]
    except KeyError:
        parent.col_bt_bg_active = '#525252'

    try:
        parent.def_bt_relief = config_file_content["def_bt_relief"]
    except KeyError:
        parent.def_bt_relief = 'solid'

    try:
        parent.default_padding = config_file_content["default_padding"]
    except KeyError:
        parent.default_padding = 2

    try:
        parent.default_bt_bd = config_file_content["default_bt_bd"]
    except KeyError:
        parent.default_bt_bd = 1

    try:
        parent.col_i_bg_default = config_file_content["col_i_bg_default"]
    except KeyError:
        parent.col_i_bg_default = '#525252'


def create_folder_structure(name, root):
    """ Creates basic project folder structure. Used by the ProjectCreator and ProjectDuplicator-classes.

    :param name: Name of the new project.
    :param root: Root directory in which the project structure will be created.
    :return:
    """

    project_dir = '/'.join([root, name])
    if os.path.isdir(project_dir) is False:
        os.makedirs(project_dir)
        os.makedirs('/'.join([project_dir, 'build']))
        os.makedirs('/'.join([project_dir, 'sequences']))


def pick_hdri(text_var):
    """ Calls tk.filedialog with settings according to selecting .hdri & .exr files.
    Used by the ProjectCreator.

    :param text_var: Tkinter text-variable of the entry that will be filled with the result.
    :return:
    """

    initial_dir = r'.\resources\hdris'

    file = filedialog.askopenfilename(title='select', initialdir=initial_dir,
                                      filetypes=[('HDRI', '*.exr *.hdr *.tx')])

    if len(file) != 0:
        text_var.set(f'{file}')


def pick_exe(text_var):
    """ Calls tk.filedialog with settings according to selecting .exe files.
    Used by the ProjectCreator.

    :param text_var: Tkinter text-variable of the entry that will be filled with the result.
    :return:
    """

    initial_dir = r'C:\Program Files\\'

    file = filedialog.askopenfilename(title='select', initialdir=initial_dir,
                                      filetypes=[('EXE', '*.exe')])

    if len(file) != 0:
        text_var.set(f'"{file}"')


def pick_dir(text_var):
    """ Calls tk.filedialog with settings according to selecting directories.
    Used by the ProjectCreator and ProjectDuplicator.

    :param text_var: Tkinter text-variable of the entry that will be filled with the result.
    :return:
    """

    directory = filedialog.askdirectory(title='select', initialdir=r'')

    if len(directory) != 0:
        text_var.set(f'{directory}')


def pick_ocio(text_var):
    """ Calls tk.filedialog with settings according to selecting .ocio files.
    Used by the ProjectCreator.

    :param text_var: Tkinter text-variable of the entry that will be filled with the result.
    :return:
    """

    previous = text_var.get()
    print(len(previous) > 0 and os.path.isfile(previous))
    if len(previous) > 0 and os.path.isfile(previous):
        initial_dir = os.path.split(previous)[0]
    else:
        initial_dir = r'.\ocio\\'

    file = filedialog.askopenfilename(title='select', initialdir=initial_dir, filetypes=[('OCIO', '*.ocio')])

    if len(file) != 0:
        text_var.set(file)


def close_sub_ui(ui):
    ui.quit()
    ui.destroy()


def generate_paths(parent):
    parent.dir_asset = os.path.join(parent.current_root, parent.current_project_name, 'build', parent.current_asset)
    if os.path.isdir(parent.dir_asset):
        #dir_export_txt previously known as dir_export
        parent.dir_export_txt = os.path.join(parent.dir_asset, 'txt', '_export')
        parent.dir_export_anm = os.path.join(parent.dir_asset, 'anm', '_export')
        parent.dir_pantry_mdl = os.path.join(parent.dir_asset, 'mdl', '.pantry')
        parent.dir_pantry_txt = os.path.join(parent.dir_asset, 'txt', '.pantry')
        parent.dir_pantry_shd = os.path.join(parent.dir_asset, 'shd', '.pantry')
        parent.dir_pantry_anm = os.path.join(parent.dir_asset, 'anm', '.pantry')
        #parent.dir_pantry= os.path.join(parent.dir_asset, 'txt', '.pantry')
        parent.dir_pipeline = os.path.join(parent.dir_asset, '.pipeline')
        parent.dir_pipeline_mdl = os.path.join(parent.dir_pipeline, 'mdl')
        parent.dir_pipeline_txt = os.path.join(parent.dir_pipeline, 'txt')
        parent.dir_pipeline_shd = os.path.join(parent.dir_pipeline, 'shd')
        parent.dir_pipeline_anm = os.path.join(parent.dir_pipeline, 'anm')
    else:
        parent.dir_export_txt = None
        parent.dir_export_anm = None
        parent.dir_pantry_txt = None
        parent.dir_pipeline = None
        parent.dir_pipeline_mdl = None
        parent.dir_pipeline_txt = None
        parent.dir_pipeline_anm = None


def publish_required_mdl(parent):
    update_required = False

    dir_pipe_mdl = os.path.join(parent.dir_pipeline, 'mdl')
    file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

    if os.path.isfile(file_mdl_package):
        with open(file_mdl_package, 'r') as json_file:
            dict_json_content = json.load(json_file)

        mdl = dict_json_content["mdl"]
        mdl_publish = dict_json_content["mdl_publish"]

        # if there is no version
        if len(mdl) != 0:
            # Current model is already published
            if mdl != mdl_publish:
                update_required = True

    return update_required


def publish_required_txt(parent):
    list_updates = []

    if parent.dir_pipeline_txt is not None:
    #if os.path.isdir(parent.dir_pipeline_txt):
        variations = [x for x in os.listdir(parent.dir_pipeline_txt) if
                      os.path.isdir(os.path.join(parent.dir_pipeline_txt, x))]

        for variation in variations:
            dir_variation = os.path.join(parent.dir_pipeline_txt, variation)

            dir_txt_package = os.path.join(dir_variation, 'txt_package')

            for channel in [x for x in os.listdir(dir_txt_package) if os.path.isdir(os.path.join(dir_txt_package, x))]:
                file_channel = os.path.join(dir_txt_package, f'{channel}.json')

                with open(file_channel, 'r') as json_file:
                    json_file_content = json.load(json_file)
                if json_file_content["txt"] != '':
                    if json_file_content["txt"] != json_file_content["txt_publish"]:
                        list_updates.append(file_channel)

    return list_updates


def publish_required_shd(parent):
    list_updates = []

    dir_pipe_shd = str(os.path.join(parent.dir_pipeline, 'shd'))
    shd_variations = [x for x in os.listdir(dir_pipe_shd) if os.path.isdir(os.path.join(dir_pipe_shd, x))]

    for shd_var in shd_variations:
        file_shd_package = os.path.join(dir_pipe_shd, shd_var, 'shd_package.json')

        if os.path.isfile(file_shd_package):
            with open(file_shd_package, 'r') as json_file:
                dict_json_content = json.load(json_file)

            shd = dict_json_content["shd"]
            shd_publish = dict_json_content["shd_publish"]

            # if there is no version
            if len(shd) != 0:
                # Current model is already published
                if shd != shd_publish:
                    list_updates.append(file_shd_package)

    return list_updates


def txt_package_list_channels(dir_txt_package):
    try:
        channels_json = [x for x in os.listdir(dir_txt_package)
                         if os.path.isfile(os.path.join(dir_txt_package, x))]
        channels_json_native = [x for x in channels_json
                                if os.path.isdir(os.path.join(dir_txt_package, x.split('.')[0]))]
        channels_json_external = [x for x in channels_json if x not in channels_json_native]

        return channels_json, channels_json_native, channels_json_external

    except FileNotFoundError:
        return None, None, None


def pull_required(parent):
    #dir_asset = os.path.join(parent.current_root, parent.current_project_name, 'build', parent.current_asset)
    list_updates = {
        "mdl": None,
        "txt": [],
        "shd": []
    }
    if parent.dir_pipeline_txt is not None:
    #if os.path.isdir(parent.dir_pipeline_txt):

        if parent.current_discipline != 'mdl':
            dir_pipe_mdl = os.path.join(parent.dir_asset, '.pipeline', 'mdl')
            file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

            if os.path.isfile(file_mdl_package):
                with open(file_mdl_package, 'r') as json_file:
                    dict_content_mdl_package = json.load(json_file)

                current_version = dict_content_mdl_package[parent.current_discipline]
                mdl_publish = dict_content_mdl_package["mdl_publish"]

                if len(mdl_publish) != 0:
                    if current_version != mdl_publish:
                        # text_pull = text_pull + ''
                        list_updates["mdl"] = {
                            "file": file_mdl_package,
                            "dict": dict_content_mdl_package,
                            "version_cur": current_version,
                            "version_pub": mdl_publish
                        }

        txt_variation_directories = [x for x in os.listdir(parent.dir_pipeline_txt)]
        if parent.current_discipline != 'txt':
            for dir_variation in txt_variation_directories:
                dir_txt_package = os.path.join(parent.dir_pipeline_txt, dir_variation, 'txt_package')
                channels_json, channels_json_native, channels_json_external = txt_package_list_channels(dir_txt_package)

                if channels_json is not None:
                    for channel_json in channels_json_native:
                        full_path = os.path.join(dir_txt_package, channel_json)

                        with open(full_path, 'r') as json_file:
                            dict_channel_file_content = json.load(json_file)

                        published = dict_channel_file_content['txt_publish']
                        used = dict_channel_file_content[parent.current_discipline]

                        if used != published:
                            list_updates["txt"].append(full_path)

        shd_variation_directories = [x for x in os.listdir(parent.dir_pipeline_shd)]
        if parent.current_discipline != 'shd':
            for dir_variation in shd_variation_directories:
                file_txt_package = os.path.join(parent.dir_pipeline_shd, dir_variation, 'shd_package.json')

                with open(file_txt_package, 'r') as json_file:
                    dict_variation_content = json.load(json_file)

                published = dict_variation_content['shd_publish']
                used = dict_variation_content[parent.current_discipline]

                if used != published:
                    list_updates["shd"].append(file_txt_package)

    return list_updates


def custom_ocio_state(elements):
    if elements[0].get():
        elements[1].configure(state=NORMAL)
        elements[2].configure(state=NORMAL)
    else:
        elements[1].configure(state=DISABLED)
        elements[2].configure(state=DISABLED)


def ui_title_bar(parent, proxy, ui, title, img_path, color):
    """ Enables override redirect for your class to allow for a custom title-bar. Furthermore adds custom
    title-bar and recreates link to window task-bar using an invisible proxy UI. Functions bound at the
    bottom of the function are handled externally in each class individually.

    :param parent: The class which is used to call this definition. Default is 'self'
    :param proxy: Root window of this application. Will be invisible but is required as a ghost
    for the software to show in the taskbar.
    :param ui: UI that is shown to the user.
    :param title: Title used for the title-bar
    :param img_path: path to the image used as an icon at the top-left of the UI.
    :param color: Background colour of the taskbar. Default is 'self.col_wdw_title'
    :return:
    """
    parent.ui_proxy = proxy
    parent.ui_child = ui
    ui.overrideredirect(True)
    proxy.iconify()
    proxy.attributes("-alpha", 0.0)
    proxy.iconbitmap(r'.\ui\icon_pipe.ico')
    proxy.title(title)
    proxy.bind("<Map>", parent.on_root_deiconify)

    ui.configure(highlightcolor=parent.col_wdw_border, highlightthickness=1,
                 highlightbackground=parent.col_wdw_border_background)
    cur_dim = [ui.winfo_width(), ui.winfo_height()]
    ui.geometry(f'{cur_dim[0]+2}x{cur_dim[1]+30}')
    proxy.geometry(f'{cur_dim[0]+2}x{cur_dim[1]+30}')

    frame_title_bar = Frame(ui, bg=color)
    frame_title_bar.pack(fill=X)

    img_icon = PhotoImage(file=img_path)
    img_close = PhotoImage(file=r'.\ui\bt_close.png')

    proxy.configure(bg=parent.col_wdw_default)

    icon = Label(frame_title_bar, image=img_icon, bg=color)
    icon.photo = img_icon
    icon.pack(side="left", padx=2, pady=2)

    lbl_title = Label(frame_title_bar, bd=1, text=title, anchor=W, bg=color, fg=parent.col_bt_fg_default)
    lbl_title.pack(side="left", padx=0, pady=2)

    bt_close = Button(frame_title_bar, image=img_close, text='a', bg=color, width=35, height=1,
                      fg=parent.col_bt_fg_default, activebackground='red',
                      activeforeground=parent.col_bt_fg_default, highlightthickness=0,
                      bd=0, relief=parent.def_bt_relief, justify=CENTER,
                      command=lambda: (ui.destroy(), proxy.destroy()))
    bt_close.photo = img_close
    bt_close.pack(side=RIGHT, fill=Y)

    icon.bind('<Button-1>', parent.move_window_offset)
    icon.bind('<B1-Motion>', parent.move_window)

    lbl_title.bind('<Button-1>', parent.move_window_offset)
    lbl_title.bind('<B1-Motion>', parent.move_window)

    frame_title_bar.bind('<Button-1>', parent.move_window_offset)
    frame_title_bar.bind('<B1-Motion>', parent.move_window)


class CreateToolTip(object):
    """ create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.wait_time = 500     # miliseconds
        self.wrap_length = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.showtip)

    def unschedule(self):
        id_temp = self.id
        self.id = None
        if id_temp:
            self.widget.after_cancel(id_temp)

    def showtip(self, event=None):
        x_offset, y_offset, cx, cy = self.widget.bbox("insert")
        width_src = self.widget.winfo_width()
        min_width = 220
        width = width_src if width_src >= min_width else min_width
        height_src = self.widget.winfo_height()

        x_offset += self.widget.winfo_rootx() + 0
        y_offset += self.widget.winfo_rooty() + height_src - 1

        self.tw = Toplevel(self.widget)
        self.tw.wm_attributes("-topmost", 1)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x_offset, y_offset))
        label = Label(self.tw, text=self.text, justify='left', fg='#d9d9d9',
                      background="#525252", relief='solid', borderwidth=1,
                      wraplength=width)  # self.wrap_length)
        label.pack(ipadx=4, ipady=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.wm_attributes("-topmost", 0)
            tw.destroy()


class AssetCreator:
    def __init__(self):
        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_active = self.col_bt_bg_green = \
            self.default_padding = self.col_i_bg_default = self.def_bt_relief = self.default_bt_bd = \
            self.col_bt_bg_blue = self.col_bt_bg_blue_highlight = self.col_bt_bg_default = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.col_bt_bg_blue_active = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.col_dd_blue_default = self.parent = None

        self.asset_creator_ui = self.tkvar_name = self.dd_type = self.current_type = self.directory_build = None

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

    def save(self):
        asset_type = self.current_type
        asset_name = self.tkvar_name.get()

        if len(asset_name) > 0:
            if asset_type == 'prop':
                prefix = 'prp'
            elif asset_type == 'environment':
                prefix = 'env'
            elif asset_type == 'vehicle':
                prefix = 'veh'
            else:
                prefix = 'chr'

            asset_name_full = prefix + (asset_name[0].upper() + asset_name[1:]).replace(' ', '_')
            dir_asset = os.path.join(self.directory_build, asset_name_full)
            directories = [dir_asset]

            if os.path.isdir(dir_asset) is False:
                # create model directory
                dir_mdl = os.path.join(dir_asset, 'mdl')
                directories.append(dir_mdl)
                dir_mdl_pantry = os.path.join(dir_mdl, '.pantry')
                directories.append(dir_mdl_pantry)
                dir_mdl_export = os.path.join(dir_mdl, '_export')
                directories.append(dir_mdl_export)
                dir_mdl_variation = os.path.join(dir_mdl_export, 'A')
                directories.append(dir_mdl_variation)
                dir_mdl_files = os.path.join(dir_mdl, 'files')
                directories.append(dir_mdl_files)
                dir_mdl_files_zbrush = os.path.join(dir_mdl_files, 'zbrush')
                directories.append(dir_mdl_files_zbrush)
                dir_mdl_files_blender = os.path.join(dir_mdl_files, 'blender')
                directories.append(dir_mdl_files_blender)
                dir_mdl_files_maya = os.path.join(dir_mdl_files, 'maya')
                directories.append(dir_mdl_files_maya)
                dir_mdl_geo = os.path.join(dir_mdl, 'geo')
                directories.append(dir_mdl_geo)
                dir_mdl_geo_blender = os.path.join(dir_mdl_geo, 'blender_out')
                directories.append(dir_mdl_geo_blender)
                dir_mdl_geo_maya = os.path.join(dir_mdl_geo, 'maya_out')
                directories.append(dir_mdl_geo_maya)
                dir_mdl_geo_zbrush = os.path.join(dir_mdl_geo, 'zbrush_out')
                directories.append(dir_mdl_geo_zbrush)
                dir_mdl_misc = os.path.join(dir_mdl, 'misc')
                directories.append(dir_mdl_misc)
                dir_mdl_ref = os.path.join(dir_mdl, 'ref')
                directories.append(dir_mdl_ref)

                # create texture directory
                dir_txt = os.path.join(dir_asset, 'txt')
                directories.append(dir_txt)
                dir_txt_export = os.path.join(dir_txt, '_export')
                directories.append(dir_txt_export)
                dir_txt_export_a = os.path.join(dir_txt_export, 'A')
                directories.append(dir_txt_export_a)
                dir_txt_pantry = os.path.join(dir_txt, '.pantry')
                directories.append(dir_txt_pantry)
                dir_txt_renders = os.path.join(dir_txt, 'renders')
                directories.append(dir_txt_renders)
                dir_txt_renders_turntables = os.path.join(dir_txt_renders, 'turntables')
                directories.append(dir_txt_renders_turntables)
                dir_txt_files = os.path.join(dir_txt, 'files')
                directories.append(dir_txt_files)
                dir_txt_files_blender = os.path.join(dir_txt_files, 'blender')
                directories.append(dir_txt_files_blender)
                dir_txt_files_mari = os.path.join(dir_txt_files, 'mari')
                directories.append(dir_txt_files_mari)
                dir_txt_files_substance_painter = os.path.join(dir_txt_files, 'substance_painter')
                directories.append(dir_txt_files_substance_painter)
                dir_txt_files_zbrush = os.path.join(dir_txt_files, 'zbrush')
                directories.append(dir_txt_files_zbrush)
                dir_txt_geo = os.path.join(dir_txt, 'geo')
                directories.append(dir_txt_geo)
                dir_txt_geo_blender = os.path.join(dir_txt_geo, 'blender_out')
                directories.append(dir_txt_geo_blender)
                dir_txt_geo_zbrush = os.path.join(dir_txt_geo, 'zbrush_out')
                directories.append(dir_txt_geo_zbrush)
                dir_txt_geo_maya = os.path.join(dir_txt_geo, 'maya_out')
                directories.append(dir_txt_geo_maya)
                dir_txt_ref = os.path.join(dir_txt, 'ref')
                directories.append(dir_txt_ref)
                dir_txt_img = os.path.join(dir_txt, 'images')
                directories.append(dir_txt_img)
                dir_txt_img_textures = os.path.join(dir_txt_img, 'source_textures')
                directories.append(dir_txt_img_textures)
                dir_txt_img_transfer = os.path.join(dir_txt_img, 'transfer')
                directories.append(dir_txt_img_transfer)
                dir_txt_img_transfer_source = os.path.join(dir_txt_img_transfer, 'source')
                directories.append(dir_txt_img_transfer_source)
                dir_txt_img_transfer_target = os.path.join(dir_txt_img_transfer, 'target')
                directories.append(dir_txt_img_transfer_target)
                dir_txt_misc = os.path.join(dir_txt, 'misc')
                directories.append(dir_txt_misc)

                # create shading directory
                dir_shd = os.path.join(dir_asset, 'shd')
                directories.append(dir_shd)
                dir_shd_pantry = os.path.join(dir_shd, '.pantry')
                directories.append(dir_shd_pantry)
                dir_shd_files = os.path.join(dir_shd, 'files')
                directories.append(dir_shd_files)
                dir_shd_misc = os.path.join(dir_shd, 'misc')
                directories.append(dir_shd_misc)
                dir_shd_renders = os.path.join(dir_shd, 'renders')
                directories.append(dir_shd_renders)
                dir_shd_renders_wip = os.path.join(dir_shd_renders, 'wip')
                directories.append(dir_shd_renders_wip)
                dir_shd_renders_wip = os.path.join(dir_shd_renders, 'presentation')
                directories.append(dir_shd_renders_wip)
                dir_shd_renders_turntable = os.path.join(dir_shd_renders, 'turntables')
                directories.append(dir_shd_renders_turntable)

                # anim
                dir_anim = os.path.join(dir_asset, 'anm')
                directories.append(dir_anim)
                dir_anim_pantry = os.path.join(dir_anim, '.pantry')
                directories.append(dir_anim_pantry)
                dir_anim_export = os.path.join(dir_anim, '_export')
                directories.append(dir_anim_export)
                dir_anim_files = os.path.join(dir_anim, 'files')
                directories.append(dir_anim_files)

                # create references directory
                dir_ref = os.path.join(dir_asset, 'ref')
                directories.append(dir_ref)

                # create pipeline directory
                dir_pipe = os.path.join(dir_asset, '.pipeline')
                directories.append(dir_pipe)
                dir_pipe_mdl = os.path.join(dir_pipe, 'mdl')
                directories.append(dir_pipe_mdl)
                dir_pipe_mdl_versions = os.path.join(dir_pipe_mdl, 'versions')
                directories.append(dir_pipe_mdl_versions)
                dir_pipe_txt = os.path.join(dir_pipe, 'txt')
                directories.append(dir_pipe_txt)
                dir_pipe_shd = os.path.join(dir_pipe, 'shd')
                directories.append(dir_pipe_shd)
                dir_pipe_anm = os.path.join(dir_pipe, 'anm')
                directories.append(dir_pipe_anm)

                for directory in directories:
                    # print(directory)
                    os.makedirs(directory)
                    if '.' not in directory.split(os.sep)[-1]:
                        continue
                    print()
                    print(directory)
                    print(directory.split('/')[-1])
                    ctypes.windll.kernel32.SetFileAttributesW(directory, 0x02)

                # Update Dropdown in main class
                self.parent.dd_asset.menu.add_command(label=asset_name_full,
                                                      command=lambda x=asset_name_full: self.parent.switch_asset(x))
                self.parent.switch_asset(asset_name_full)

                close_sub_ui(self.asset_creator_ui)
                close_sub_ui(self.ui_proxy)

                message = "Successfully created asset directory."
                messagebox.showinfo(title='', message=message)

            else:
                message = "Asset already exists."
                messagebox.showerror(title='Error', message=message)
        else:
            message = "No name given."
            messagebox.showerror(title='Error', message=message)

    def switch_type(self, asset_type):
        self.dd_type.configure(text=asset_type)
        self.current_type = asset_type

    def move_window_offset(self, event):
        window_x = self.ui_child.winfo_x()
        window_y = self.ui_child.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_window(self, event):
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_child.geometry(f'+{x_new}+{y_new}')

    def on_root_deiconify(self, _):
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def create_ui(self, directory, parent):
        self.parent = parent
        self.directory_build = directory

        dimensions = '240x59+420+100'
        # dimensions = '244x89+42+100'
        self.ui_proxy = Toplevel()
        self.asset_creator_ui = Toplevel()
        self.asset_creator_ui.lift()
        self.asset_creator_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        self.asset_creator_ui.title('Asset Creator')
        self.asset_creator_ui.attributes("-alpha", 0.0)
        self.asset_creator_ui.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, self.asset_creator_ui, 'Asset Creator', r'.\ui\icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)

        self.asset_creator_ui.resizable(width=False, height=True)
        self.asset_creator_ui.configure(bg=self.col_wdw_default)

        frame = Frame(self.asset_creator_ui, bg=self.col_wdw_default)
        frame.pack(fill=X, padx=self.default_padding, pady=2*self.default_padding)
        # ---------------------------------------------------------------------------------------------
        # --- First Row ---
        # ---------------------------------------------------------------------------------------------
        lbl_type = Label(frame, bd=1, text='Type',
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_type.grid(row=0, column=0, sticky=W, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.current_type = 'character'
        self.dd_type = Menubutton(frame, text=self.current_type,
                                  width=8, bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                  highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                  anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                  relief=self.def_bt_relief, justify=RIGHT)
        self.dd_type.menu = Menu(self.dd_type, tearoff=0, bd=0, activeborderwidth=3,
                                 relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                 activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                 activebackground=self.col_bt_bg_blue_highlight)
        self.dd_type['menu'] = self.dd_type.menu

        self.dd_type.menu.add_command(label='character', command=lambda: self.switch_type('character'))
        self.dd_type.menu.add_command(label='prop', command=lambda: self.switch_type('prop'))
        self.dd_type.menu.add_command(label='environment', command=lambda: self.switch_type('environment'))
        self.dd_type.menu.add_command(label='vehicle', command=lambda: self.switch_type('vehicle'))

        self.dd_type.grid(row=0, column=1, columnspan=1, sticky=EW, padx=self.default_padding,
                          pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        # --- Second Row ---
        # ---------------------------------------------------------------------------------------------
        lbl_name = Label(frame, bd=1, text='Name',
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_name.grid(row=1, column=0, sticky=W, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.tkvar_name = StringVar()
        self.tkvar_name.set('')
        i_abbr = Entry(frame, bd=1, textvariable=self.tkvar_name,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        i_abbr.grid(row=1, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        bt_save = Button(frame, text=f'Save', bg=self.col_bt_bg_green, width=8,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief,
                         command=lambda: self.save())
        bt_save.grid(row=0, column=2, rowspan=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.asset_creator_ui.geometry('')

        self.asset_creator_ui.attributes("-alpha", 1.0)
        self.asset_creator_ui.wm_attributes("-topmost", 1)
        self.asset_creator_ui.mainloop()


class ProjectDuplicator:
    def __init__(self):
        self.project_name = self.project_abbreviation = self.col_bt_bg_default = \
            self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_active = self.col_bt_bg_green = \
            self.col_i_bg_default = self.default_bt_bd = self.default_padding = self.def_bt_relief = \
            self.tkvar_ocio = self.tkvar_project_abbreviation = self.tkvar_project_name = \
            self.project_duplicator_ui = self.tkvar_root = self.ui_child = self.x_offset = \
            self.ui_proxy = self.y_offset = self.col_wdw_title = self.col_wdw_border = \
            self.col_wdw_border_background = self.col_bt_bg_blue = self.col_bt_bg_blue_active = \
            self.col_dd_blue_default = self.col_bt_bg_blue_highlight = self.parent = None

        self.software_list_ui = []
        self.software_list_variables = []
        self.version = os.path.basename(__file__).split('_')[-1][:-3]
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

    def duplicate_project_config(self, config):
        name = self.tkvar_project_name.get()
        abbr = self.tkvar_project_abbreviation.get()
        root = self.tkvar_root.get()

        if len(name) > 0:
            if len(abbr) > 0:
                existing_projects = [x for x in os.listdir(r'.\projects\\') if os.path.isdir(f'.\\projects\\{x}')]

                if len(existing_projects) > 0:
                    existing_names = []
                    existing_abbreviations = []
                    for project in existing_projects:
                        existing_name, existing_abbr = project.split('.')[0].split('-')
                        existing_names.append(existing_name)
                        existing_abbreviations.append(existing_abbr)

                    if name in existing_names or abbr in existing_abbreviations:
                        message = "Project with same name or abbreviation exists. Can't create project"
                        messagebox.showerror(title='Error', message=message)
                    else:
                        self.write_duplicate(config, name, abbr, root)
                        create_folder_structure(name, root)
                else:
                    messagebox.showerror(title='Error', message='Show already exists.')
            else:
                message = 'No valid project abbreviation was given.'
                messagebox.showerror(title='Error', message=message)
        else:
            message = 'No valid project name was given.'
            messagebox.showerror(title='Error', message=message)

    def write_duplicate(self, config, name, abbr, root):
        source_dir, source_file = os.path.split(config)
        target_dir = f'.\\projects\\{name}-{abbr}'
        target_file = f'{name}-{abbr}.json'
        target = '/'.join([target_dir, target_file])

        shutil.copytree(source_dir, target_dir)
        os.rename('/'.join([target_dir, source_file]), target)

        with open(target, 'r') as config_file:
            config_file_content = json.load(config_file)
            config_file_content["name"] = name
            config_file_content["abbreviation"] = abbr
            config_file_content["root"] = root

        with open(target, 'w') as config_file:
            json.dump(config_file_content, config_file, indent=2)

        create_folder_structure(name, root)

        # update variables and dropdown in main class
        self.parent.dd_projects.menu.add_command(label=name, command=lambda x=name: self.parent.switch_project(x))
        self.parent.projects = [x for x in os.listdir(r'.\projects\\') if os.path.isdir(f'.\\projects\\{x}')]
        self.parent.projects_parts = [x.split('-') for x in self.parent.projects]
        self.parent.project_names = [x[0] for x in self.parent.projects_parts]
        self.parent.project_abbreviations = [x[1] for x in self.parent.projects_parts]
        self.parent.switch_project(name)

        close_sub_ui(self.project_duplicator_ui)
        close_sub_ui(self.ui_proxy)
        messagebox.showinfo(title='', message='File saved successfully.')

    def move_window_offset(self, event):
        window_x = self.ui_child.winfo_x()
        window_y = self.ui_child.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_window(self, event):
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_child.geometry(f'+{x_new}+{y_new}')

    def on_root_deiconify(self, _):
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def create_ui(self, config, parent):
        self.parent = parent
        dimensions = '330x75+420+100'

        self.ui_proxy = Toplevel()
        self.project_duplicator_ui = Toplevel()
        self.project_duplicator_ui.lift()
        self.project_duplicator_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        self.project_duplicator_ui.title('Project Duplicator')
        self.project_duplicator_ui.attributes("-alpha", 0.0)
        self.project_duplicator_ui.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, self.project_duplicator_ui, 'Project Duplicator',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)

        self.project_duplicator_ui.resizable(width=False, height=True)
        self.project_duplicator_ui.configure(bg=self.col_wdw_default)

        frame = Frame(self.project_duplicator_ui, bg=self.col_wdw_default)
        frame.pack(fill=X, padx=self.default_padding, pady=2 * self.default_padding)
        # ---------------------------------------------------------------------------------------------
        lbl_name = Label(frame, bd=1, text='New Name',
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_name.grid(row=0, column=0, sticky=W, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        lbl_abbr = Label(frame, bd=1, text='New Abbreviation',
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_abbr.grid(row=1, column=0, sticky=W, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        lbl_root = Label(frame, bd=1, text='New Root',
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_root.grid(row=2, column=0, sticky=W, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.tkvar_project_name = StringVar()
        self.tkvar_project_name.set('')
        i_name = Entry(frame, bd=1, textvariable=self.tkvar_project_name, width=18,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        i_name.grid(row=0, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.tkvar_project_abbreviation = StringVar()
        self.tkvar_project_abbreviation.set('')
        i_abbr = Entry(frame, bd=1, textvariable=self.tkvar_project_abbreviation,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        i_abbr.grid(row=1, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        with open(config, 'r') as config_file:
            config_file_content = json.load(config_file)
            root = config_file_content["root"]
        self.tkvar_root = StringVar()
        self.tkvar_root.set(root)
        i_root = Entry(frame, bd=1, textvariable=self.tkvar_root,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        i_root.grid(row=2, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        source_name = os.path.basename(os.path.splitext(config)[0]).split('-')[0]
        bt_save = Button(frame, text=f'Duplicate\n{source_name}', bg=self.col_bt_bg_green, width=12,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief,
                         command=lambda x=config: self.duplicate_project_config(x))
        bt_save.grid(row=0, column=2, rowspan=3, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.project_duplicator_ui.geometry('')

        self.project_duplicator_ui.attributes("-alpha", 1.0)
        self.project_duplicator_ui.wm_attributes("-topmost", 1)
        self.project_duplicator_ui.mainloop()

# ProjectCreator().create_ui(None)
