# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import shutil as sh
from datetime import datetime
from pipe_utils import *


class ReleaseTextures:
    """ Creates a UI to move textures into new version folders and creates pipeline specific json files.
    """

    def __init__(self):
        self.version = os.path.basename(__file__).split('_')[-1][:-3]

        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = None
        self.i_tx_path = self.bt_release = self.default_padding = None
        self.var_publish = self.var_overwrite = self.path = self.path_root = self.filetypes = self.artist = \
            self.time = self.current_asset = self.overwrite = self.dir_asset = self.dir_export_txt = self.dir_pipeline = \
            self.publish = self.dir_pantry_txt = self.connections_default = self.def_bt_relief = self.default_bt_bd = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.variations = \
            self.variation_bools = self.col_wdw_border = self.col_wdw_border_background = \
            self.col_wdw_title = None

        self.user = os.getenv('PIPE_USER')
        self.current_root = os.getenv('PIPE_ROOT')
        self.current_project_name = os.getenv('PIPE_PROJECT')
        self.current_department = os.getenv('PIPE_DEPARTMENT')
        self.current_discipline = os.getenv('PIPE_DISCIPLINE')
        self.current_asset = os.getenv('PIPE_ASSET')

        generate_paths(self)
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.json_load_variables(r'.\config\config_release_tool_txt.json')
        self.create_ui_texture_release()

    def json_load_variables(self, config):
        with open(config, 'r') as config_file:
            config_file_content = json.load(config_file)
        try:  # variables in config_release_tool_txt.json
            self.filetypes = config_file_content["filetypes"]
            self.connections_default = config_file_content["connections"]
        except KeyError:
            pass

    def json_store_channel_version(self, dir_pipe_channel, channel, channel_version, layer_version):
        file_name = f'{channel}.{layer_version}.json'
        dict_channel_version = {
            "artist": self.user,
            "time": str(datetime.now()).split('.')[0],
            "channel_version": channel_version,
            "published": self.publish
        }
        #    "published": self.publish
        full_path = os.path.join(dir_pipe_channel, file_name)
        with open(full_path, 'w') as json_output_channel:
            json.dump(dict_channel_version, json_output_channel, indent=2)

    def json_store_channel(self, dir_pipe_channel, channel, layer_version):
        file_name = f'{channel}.json'
        full_path = os.path.join(dir_pipe_channel, file_name)

        if os.path.isfile(full_path) is True:
            with open(full_path, 'r') as json_content:
                dict_channel = json.load(json_content)
            if "txt" in dict_channel:
                dict_channel["txt"] = layer_version
            else:
                message = f"An external channel called >> {channel} << is already linked to this texture package. " \
                          "It will be replaced with your native channel."
                messagebox.showinfo('Replace?', message)

                dict_channel.clear()
                dict_channel = {
                    "mdl": '',
                    "txt": layer_version,
                    "txt_publish": '',
                    "shd": '',
                    "anm": '',
                    "sht": ''
                }
        else:
            dict_channel = {
                "mdl": '',
                "txt": layer_version,
                "txt_publish": '',
                "shd": '',
                "anm": '',
                "sht": ''
            }

        if self.publish:
            dict_channel["txt_publish"] = layer_version

        with open(full_path, 'w') as json_output_channel:
            json.dump(dict_channel, json_output_channel, indent=2)

    def json_create_txt_connections(self, dir_pipe_variation, variation):
        file_name = f'txt_connections.json'
        full_path = os.path.join(dir_pipe_variation, file_name)

        channels = [x.split('.')[0] for x in os.listdir(os.path.join(dir_pipe_variation, 'txt_package'))
                    if os.path.isfile(os.path.join(dir_pipe_variation, 'txt_package', x))]
        if os.path.isfile(full_path) is False:
            dict_connections = {}
            for key in self.connections_default['channels']:
                #print(self.connections_default[key])
                if self.connections_default['channels'][key] in channels:
                    dict_connections[key] = self.connections_default['channels'][key]
                else:
                    dict_connections[key] = ''

            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_connections, json_output_channel, indent=2)
        else:
            with open(full_path, 'r') as json_output_channel:
                dict_connections = json.load(json_output_channel)

            for key in dict_connections:
                if dict_connections[key] == '':
                    if self.connections_default['channels'][key] in channels:
                        dict_connections[key] = self.connections_default['channels'][key]
            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_connections, json_output_channel, indent=2)

    def release_textures(self):
        skip_copy = False
        self.publish = self.var_publish.get()
        self.overwrite = self.var_overwrite.get()

        variations_for_export = [x for i, x in enumerate(self.variations) if self.variation_bools[i].get()]

        if len(variations_for_export) > 0:
            for variation in variations_for_export:
                dir_variation = os.path.join(self.dir_export_txt, variation)
                dir_variation_pantry = os.path.join(self.dir_pantry_txt, variation)
                if os.path.isdir(dir_variation_pantry) is False:
                    os.makedirs(dir_variation_pantry)

                dir_pipe_variation = os.path.join(self.dir_pipeline, 'txt', variation)
                dir_pipe_channels = str(os.path.join(dir_pipe_variation, 'txt_package'))
                if os.path.isdir(dir_pipe_variation) is False:
                    os.makedirs(dir_pipe_variation)
                if os.path.isdir(dir_pipe_channels) is False:
                    os.makedirs(dir_pipe_channels)
                #self.json_create_txt_connections(dir_pipe_variation, variation)

                files = [x for x in os.listdir(dir_variation) if os.path.isfile(os.path.join(dir_variation, x))]
                if len(files) > 0:
                    channels = []
                    for file in files:
                        channel = file.split('.')[0]
                        if channel not in channels:
                            channels.append(channel)

                    for channel in channels:
                        dir_channel = os.path.join(self.dir_pantry_txt, variation, channel)
                        if os.path.isdir(dir_channel) is False:
                            os.makedirs(dir_channel)

                        dir_pipe_channel = os.path.join(dir_pipe_channels, str(channel))
                        if os.path.isdir(dir_pipe_channel) is False:
                            os.makedirs(dir_pipe_channel)
                        existing_channel_versions = os.listdir(dir_pipe_channel)

                        existing_versions = [x for x in os.listdir(dir_channel) if
                                             os.path.isdir(os.path.join(dir_channel, x))]

                        if len(existing_versions) == 0:
                            dir_version_current = os.path.join(dir_channel, 'v001')
                            os.makedirs(dir_version_current)
                            channel_version_cur = 'v001'
                            channel_current_version = 'v001'
                            self.json_store_channel_version(dir_pipe_channel, channel,
                                                            channel_version_cur, channel_current_version)
                            self.json_store_channel(dir_pipe_channels, channel, channel_current_version)

                        else:
                            existing_versions.sort()
                            latest_existing_version = existing_versions[-1]

                            if self.overwrite is False:
                                version_cur_int = int(latest_existing_version[1:]) + 1
                                channel_version_cur = 'v' + format(version_cur_int, '03d')
                                dir_version_previous = str(os.path.join(dir_channel, latest_existing_version))
                                dir_version_current = os.path.join(dir_channel, channel_version_cur)
                                os.makedirs(dir_version_current)

                                """ JSON FILE GENERATION
                                - channel: Folder that contains all channel_versions
                                - channel_version: json file that stores which version of textures is used
                                  (allows rollback without new texture file duplicates)
                                - txt_package: json file that links channel to a specific channel type for 
                                automatic shader creation
                                - stream_package(_txt): json file that defines which version is actively being used."""
                                channel_current_version_int = len(existing_channel_versions) + 1
                                channel_current_version = 'v' + format(channel_current_version_int, '03d')
                                self.json_store_channel_version(dir_pipe_channel, channel,
                                                                channel_version_cur, channel_current_version)
                                self.json_store_channel(dir_pipe_channels, channel, channel_current_version)

                                # Copy missing UDIMs from previous version
                                # generate list of UDIMs in new version
                                udims_new = []
                                for file in files:
                                    if channel in file:
                                        udims_new.append(file.split('.')[-2])

                                files_previous = [x for x in os.listdir(dir_version_previous)
                                                  if os.path.isfile(os.path.join(dir_version_previous, x))]

                                textures_missing_udims = [x for x in files_previous
                                                          if x.split('.')[-2] not in udims_new]
                                if skip_copy is False:
                                    for file_prv in textures_missing_udims:
                                        sh.copy2(os.path.join(dir_version_previous, file_prv),
                                                 os.path.join(dir_version_current, file_prv))
                            else:
                                dir_version_current = latest_existing_version
                                # print(f'Overwriting version: {dir_version_current}')

                                # DONT WRITE NEW JSON FILES IF OVERWRITE EXISTING
                                channel_current_version_int = len(existing_channel_versions) #+ 1
                                channel_current_version = 'v' + format(channel_current_version_int, '03d')
                                self.json_store_channel_version(dir_pipe_channel, channel,
                                                                dir_version_current, channel_current_version)
                                self.json_store_channel(dir_pipe_channels, channel, channel_current_version)

                        textures_of_channel = [x for x in files if channel == x.split('.')[0]]

                        for texture in textures_of_channel:
                            full_path_source = str(os.path.join(dir_variation, texture))
                            full_path_target = str(os.path.join(dir_version_current, texture))
                            if skip_copy is False:
                                sh.move(full_path_source, full_path_target)
                            else:
                                sh.copy2(full_path_source, full_path_target)

                    self.json_create_txt_connections(dir_pipe_variation, variation)

            message = 'Successfully released textures.'
            messagebox.showinfo(title='', message=message)
            #self.parent.check

            close_sub_ui(self.ui_child)
            close_sub_ui(self.ui_proxy)

        else:
            message = 'No valid output has been selected.'
            messagebox.showerror(title='Error', message=message)

    # TODO NEEDS TO CHECK FOR REQUIRED PUBLISHED

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

    def ui_variation(self, frame, variations):
        self.variations = []
        self.variation_bools = []
        row = 1
        for i, variation in enumerate(variations):
            dir_variation = os.path.join(self.dir_export_txt, variation)
            textures = [x for x in os.listdir(dir_variation) if os.path.join(dir_variation, x)]
            state = NORMAL if len(textures) > 0 else DISABLED

            width_limit = 8
            row = 1
            column = i
            while column > width_limit-1:
                row += 1
                column -= width_limit
            row = int(i/width_limit)
            column = i%width_limit

            tkvar_variation = BooleanVar()
            tkvar_variation.set(len(textures) > 0)
            cb_variation = Checkbutton(frame, text=variation, var=tkvar_variation, state=state,
                                       bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                       fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                       selectcolor=self.col_bt_bg_active)
            cb_variation.grid(row=row, column=column, sticky=W, padx=self.default_padding, pady=self.default_padding)
            if state == DISABLED:
                CreateToolTip(cb_variation,
                              "no new textures have been detected")

            if len(textures) > 0:
                self.variations.append(variation)
                self.variation_bools.append(tkvar_variation)

        if len(self.variations) > 0:
            return row

    def create_ui_texture_release(self):
        self.ui_proxy = Tk()
        ui_texture_release = Toplevel()
        ui_texture_release.lift()
        ui_texture_release.attributes("-alpha", 0.0)
        ui_texture_release.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_texture_release.title('Release Textures')
        ui_texture_release.geometry('+420+100')
        ui_title_bar(self, self.ui_proxy, ui_texture_release, 'Release Textures', r'../ui/icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)

        ui_texture_release.resizable(width=True, height=True)
        ui_texture_release.configure(bg=self.col_wdw_default)

        frame_main = Frame(ui_texture_release, bg=self.col_wdw_default)
        frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)

        # ---------------------------------------------------------------------------------------------
        text = f'{self.current_asset}  //  {self.current_discipline.upper()} Stream'
        lbl_source_directory = Label(frame_main, bd=1, text=text, anchor=W,
                                     bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_source_directory.grid(row=0, column=0, columnspan=3, sticky=W, padx=2.5 * self.default_padding,
                                  pady=2.5 * self.default_padding)
        CreateToolTip(lbl_source_directory,
                      f'Source directory:    \n{self.current_project_name}  /  build  /  '
                      f'{self.current_asset}  /  txt  /  _export')
        # ---------------------------------------------------------------------------------------------

        # --- Variations ------------------------------------------------------------------------------
        variations = [x for x in os.listdir(self.dir_export_txt) if os.path.isdir(os.path.join(self.dir_export_txt, x))]

        frame_variations = Frame(frame_main, bg=self.col_wdw_default)
        frame_variations.grid(row=1, column=0, columnspan=3, sticky=W, padx=2.5 * self.default_padding,
                              pady=2.5 * self.default_padding)
        last_row = self.ui_variation(frame_variations, variations)
        cur_dim = [ui_texture_release.winfo_width(), ui_texture_release.winfo_height()]
        #ui_texture_release.geometry(f'{cur_dim[0]}x{cur_dim[1] + 29 * last_row}')
        # ---------------------------------------------------------------------------------------------
        self.var_overwrite = BooleanVar()
        self.var_overwrite.set(False)
        cb_overwrite = Checkbutton(frame_main, text='overwrite existing', var=self.var_overwrite,
                                   bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                   fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                   selectcolor=self.col_bt_bg_active)
        cb_overwrite.grid(row=2, column=0, sticky=N, padx=self.default_padding, pady=self.default_padding)
        CreateToolTip(cb_overwrite,
                      "Also skips update of .json files used by the pipeline.\n\n"
                      "You should not use this feature if the current version has already been published.")

        self.var_publish = BooleanVar()
        self.var_publish.set(False)
        cb_publish = Checkbutton(frame_main, text='push result', var=self.var_publish,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active)
        cb_publish.grid(row=2, column=1, sticky=N, padx=7*self.default_padding, pady=self.default_padding)

        self.bt_release = Button(frame_main, text='Release textures into the wild', width=24, border=self.default_bt_bd,
                                 bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.release_textures())
        # self.bt_release.config(state=DISABLED)
        self.bt_release.grid(row=2, column=2, sticky=N, padx=self.default_padding, pady=self.default_padding)

        ui_texture_release.geometry('')

        ui_texture_release.attributes("-alpha", 1.0)
        ui_texture_release.mainloop()

# Todo Issue if you are releasing a channel similarly named to external linked channel


ReleaseTextures()
