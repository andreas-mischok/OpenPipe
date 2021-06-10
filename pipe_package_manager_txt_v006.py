import shutil as sh
import string
from pipe_utils import *


class PackageManagerTxt:
    def __init__(self):
        self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.dd_variation = \
            self.current_variation = self.default_padding = self.col_bt_fg_default = \
            self.col_bt_bg_blue = self.col_bt_blue_highlight = self.col_bt_bg_blue_highlight = \
            self.def_bt_relief = self.col_wdw_default = self.col_bt_bg_active = self.col_bt_bg_default = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.connections_default = self.frame_main = self.variations = self.connections = \
            self.connection_ui_elements = self.frame_left = self.frame_right = self.ui_picker = \
            self.col_bt_red = self.col_bt_red_highlight = self.col_bt_petrol = self.ui_variation_creator = \
            self.col_bt_bg_green = self.col_bt_bg_green_highlight = self.dir_txt_package = self.dd_add_external = \
            self.col_bt_petrol_highlight = self.default_bt_bd = self.icon_delete = self.tkvar_publish = \
            self.icon_create = self.col_i_bg_default = self.parent = None

        self.dict_native_version = {}
        self.dict_external_channels = {}
        self.dict_procedural_ui_elements_external = {
            "nat": {},
            "ext": {}
        }
        self.dict_additions = {}
        self.current_floating_variation = {}

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

    def move_picker_offset(self, event):
        window_x = self.ui_picker.winfo_x()
        window_y = self.ui_picker.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_picker(self, event):
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_picker.geometry(f'+{x_new}+{y_new}')

    def move_variation_creator_offset(self, event):
        window_x = self.ui_variation_creator.winfo_x()
        window_y = self.ui_variation_creator.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_variation_creator(self, event):
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_variation_creator.geometry(f'+{x_new}+{y_new}')

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

    def switch_native_version(self, key, version, dd, latest):
        self.dict_native_version[key]["version"] = version
        if version == latest.split('.')[1]:
            bg = self.col_bt_petrol
            abg = self.col_bt_petrol_highlight
        else:
            bg = self.col_bt_red
            abg = self.col_bt_red_highlight

        dd.config(text=version, bg=bg, activebackground=abg)

    def add_external_channel(self, channel_json_external, proxy, color, source_directory):
        """ Adds a row to the section of external channel

        :param source_directory: directory from which the external 'channel.json' files are sourced
        :param channel_json_external:
        :param proxy: proxy name of this item to avoid duplicates
        :param color: the background colour used for the label of this channel.
                        petrol = saved in the txt package already
                        red = yet to be saved
        :return:
        """

        channel_external = channel_json_external.split('.')[0]
        i = len(self.dict_external_channels) + 1

        with open(os.path.join(source_directory, channel_json_external), 'r') as json_file:
            json_file_content = json.load(json_file)
        if 'txt' in json_file_content.keys():
            dir_parts = os.path.normpath(source_directory).split(os.sep)
            channel_content = [dir_parts[-5], dir_parts[-2], channel_json_external.split('.')[0]]
        else:
            channel_content = [json_file_content[x] for x in json_file_content]

        continue_adding = True
        if len(self.dict_external_channels) > 0:
            contents = [self.dict_external_channels[key]["content"] for key in self.dict_external_channels]
            channels = [self.dict_external_channels[key]["channel"] for key in self.dict_external_channels]
            if channel_content in contents or proxy in channels:
                continue_adding = False

        natives = [key for key in self.dict_native_version]
        if proxy in natives:
            continue_adding = False

        if continue_adding:
            text = '  -  '.join(channel_content)

            # --- Label ----------------------------------------------------------------------------
            lbl_channel_external = Label(self.frame_right, bd=1, text=text, anchor=W, justify=LEFT,
                                         bg=color, fg=self.col_bt_fg_default, width=38, relief='solid')
            lbl_channel_external.grid(row=i, column=0, sticky=NSEW, padx=self.default_padding,
                                      pady=self.default_padding)
            lbl_as = Label(self.frame_right, bd=1, text=' as ', anchor=W, justify=LEFT,
                           bg=self.col_wdw_title, fg=self.col_bt_fg_default)
            lbl_as.grid(row=i, column=1, sticky=W, padx=self.default_padding,
                        pady=self.default_padding)
            # --- Proxy ----------------------------------------------------------------------------
            tkvar_proxy = StringVar()
            tkvar_proxy.set(proxy)
            i_proxy = Entry(self.frame_right, bd=1, textvariable=tkvar_proxy, width=18,
                            bg='gray40', fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                            insertbackground=self.col_bt_fg_default)
            i_proxy.grid(row=i, column=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)

            # --- Delete Button  -------------------------------------------------------------------
            bt_delete = Button(self.frame_right, image=self.icon_delete, text='-', width=24, height=21,
                               border=self.default_bt_bd,
                               bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                               activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                               command=lambda x=channel_external, y=i: self.del_external_channel(x, y))
            bt_delete.grid(row=i, column=3, sticky=E, padx=self.default_padding, pady=self.default_padding)
            # ---------------------------------------------------------------------------------------------

            self.dict_procedural_ui_elements_external["ext"][channel_external] = [lbl_channel_external,
                                                                                  bt_delete, i_proxy, lbl_as]
            self.dict_external_channels[i] = {
                "content": channel_content,
                "proxy": tkvar_proxy,
                "channel": channel_external
            }

    def del_external_channel(self, channel_external, row):
        """ Deletes a row in the 'External Texture Layer' section.

        :param channel_external:
        :param row: Value of the row that needs to be deleted. Is used as a key of a dictionary.
        :return:
        """

        for element in self.dict_procedural_ui_elements_external["ext"][channel_external]:
            element.destroy()

        move_up = False
        for key in self.dict_external_channels:
            if move_up:
                for element in \
                        self.dict_procedural_ui_elements_external["ext"][self.dict_external_channels[key]["channel"]]:
                    cur_row = element.grid_info()["row"]
                    element.grid(row=cur_row - 1)
            if key == row:
                move_up = True

        del self.dict_procedural_ui_elements_external["ext"][channel_external]
        del self.dict_external_channels[row]

    def update_connections(self, dir_variation):
        config = r'.\config\config_release_tool_txt.json'
        with open(config, 'r') as json_file:
            config_file_content = json.load(json_file)
            connections_default = config_file_content["connections"]

        dir_txt_package = os.path.join(dir_variation, 'txt_package')
        file_name = 'txt_connections.json'
        full_path = os.path.join(dir_variation, file_name)
        channels = [x.split('.')[0] for x in os.listdir(dir_txt_package)
                    if os.path.isfile(os.path.join(dir_txt_package, x))]

        # file doesn't exist
        if os.path.isfile(full_path) is False:
            dict_connections = {}
            for key in connections_default:
                if connections_default[key] in channels:
                    dict_connections[key] = connections_default[key]
                else:
                    dict_connections[key] = ''
            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_connections, json_output_channel, indent=2)

        # file exists already
        else:
            with open(full_path, 'r') as json_output_channel:
                dict_connections = json.load(json_output_channel)

            for key in dict_connections:
                if dict_connections[key] == '':
                    if connections_default[key] in channels:
                        dict_connections[key] = connections_default[key]
            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_connections, json_output_channel, indent=2)

    def save(self):
        """ Saves all channels (native & external) of the currently selected variation,
         according to the current settings.

        :return:
        """
        variation = self.current_variation
        publish = self.tkvar_publish.get()

        natives = [key for key in self.dict_native_version]
        proxies = [self.dict_external_channels[key]["proxy"].get() for key in self.dict_external_channels]
        overlap = [x for x in natives if x in proxies]
        duplicates_in_proxies = len(proxies) != len(set(proxies))

        if len(overlap) != 0 or duplicates_in_proxies:
            overlaps_str = ', '.join(overlap)
            if len(overlap) == 1:
                message = f'Unable not save. Channel duplicate detected:\n\n{overlaps_str}'
            else:
                message = f'Unable not save. Channel duplicates detected:\n\n{overlaps_str}'
            messagebox.showerror(title='Error', message=message)
        else:
            channels_json = [x for x in os.listdir(self.dir_txt_package)
                             if os.path.isfile(os.path.join(self.dir_txt_package, x))]
            channels_json_native = [x for x in channels_json
                                    if os.path.isdir(os.path.join(self.dir_txt_package, x.split('.')[0]))]
            channels_json_external = [x for x in channels_json if x not in channels_json_native]

            # Update Native Channels
            for channel in self.dict_native_version:
                version = self.dict_native_version[channel]["version"]
                latest = self.dict_native_version[channel]["latest"]
                latest_version = latest.split('.')[1]

                dir_channel = os.path.join(self.dir_txt_package, channel)

                # Duplicate for rollback
                if version != latest_version and self.parent.current_discipline == 'txt':
                    version_cur_int = int(latest_version[1:]) + 1
                    new_version = 'v' + format(version_cur_int, '03d')

                    source = os.path.join(dir_channel, f'{channel}.{version}.json')
                    target = os.path.join(dir_channel, f'{channel}.{new_version}.json')
                    version = new_version

                    sh.copy2(source, target)

                # update publish state in channel version file
                if self.parent.current_discipline == 'txt':
                    version_json = os.path.join(dir_channel, f'{channel}.{version}.json')
                    with open(version_json, 'r') as json_input:
                        dict_channel_version = json.load(json_input)

                    dict_channel_version["published"] = publish

                    with open(version_json, 'w') as json_output:
                        json.dump(dict_channel_version, json_output, indent=2)

                full_path = os.path.join(self.dir_txt_package, f'{channel}.json')

                # update versions in channel file
                with open(full_path, 'r') as json_input_channel:
                    dict_channel = json.load(json_input_channel)

                dict_channel[self.parent.current_discipline] = version

                if publish:
                    dict_channel[f'{self.parent.current_discipline}_publish'] = version

                with open(full_path, 'w') as json_output_channel:
                    json.dump(dict_channel, json_output_channel, indent=2)

            # External Channels
            # Delete Previous External Channels
            for channel in channels_json_external:
                full_path = os.path.join(self.dir_txt_package, channel)
                os.remove(full_path)

            # Create External Channels
            for key in self.dict_external_channels:
                layer = self.dict_external_channels[key]
                proxy = layer["proxy"].get()

                dict_external_layer = {
                    "asset": layer["content"][0],
                    "variation": layer["content"][1],
                    "channel": layer["content"][2]
                }
                full_path = os.path.join(self.dir_txt_package, f'{proxy}.json')
                with open(full_path, 'w') as json_output_channel:
                    json.dump(dict_external_layer, json_output_channel, indent=2)

            self.ui_switch_variation(self.current_variation)
            self.update_connections(os.path.join(self.parent.dir_pipeline_txt, variation))
            message = f'Saved successfully.'
            messagebox.showinfo(title='', message=message)

    def apply_picker(self, source_directory):
        natives = [key for key in self.dict_native_version]
        proxies = [self.dict_external_channels[key]["proxy"].get() for key in self.dict_external_channels]

        additions = [self.dict_additions[key]["proxy"].get() for key in self.dict_additions
                     if self.dict_additions[key]["usage"].get()]
        overlap_1 = [x for x in additions if x in natives or x in proxies]

        content_additions = []
        for channel in self.dict_additions:
            if self.dict_additions[channel]["usage"].get():
                channel_json_external = f'{channel}.json'
                with open(os.path.join(source_directory, channel_json_external), 'r') as json_file:
                    json_file_content = json.load(json_file)
                if 'txt' in json_file_content.keys():
                    dir_parts = os.path.normpath(source_directory).split(os.sep)
                    channel_content = [dir_parts[-5], dir_parts[-2], channel_json_external.split('.')[0]]
                else:
                    channel_content = [json_file_content[x] for x in json_file_content]
                content_additions.append(channel_content)

        contents = [self.dict_external_channels[key]["content"] for key in self.dict_external_channels]
        overlap_2 = [x for x in content_additions if x in contents]

        if len(overlap_2) == 0:
            if len(overlap_1) == 0:
                for channel in self.dict_additions:
                    if self.dict_additions[channel]["usage"].get() is True:
                        self.add_external_channel(f'{channel}.json',
                                                  self.dict_additions[channel]["proxy"].get(), self.col_bt_red,
                                                  source_directory)
                close_sub_ui(self.ui_picker)
            else:
                channel_names = ', '.join(overlap_1)
                if len(overlap_1) == 1:
                    message = f'The following channel already exists in this texture package:\n\n{channel_names}'
                else:
                    message = f'The following channels already exists in this texture package:\n\n{channel_names}'
                messagebox.showerror(title='Error', message=message)
        else:
            message = f'At least one of the selected layers is already included in this texture package'
            messagebox.showerror(title='Error', message=message)

    def create_ui_picker_channels(self, dir_asset_pipe, variation, asset):
        if self.ui_picker is not None:
            if self.ui_picker.winfo_exists():
                close_sub_ui(self.ui_picker)

        title = f'{asset}  - {variation} '

        self.ui_picker = Toplevel(bg=self.col_wdw_default, bd=1, highlightcolor='black',
                                  highlightthickness=1, highlightbackground='black')
        self.ui_picker.attributes("-alpha", 0.0)
        self.ui_picker.iconbitmap(r'.\ui\icon_pipe.ico')
        self.ui_picker.title('Picker')
        self.ui_picker.overrideredirect(True)
        self.ui_picker.wm_attributes("-topmost", 1)

        frame = Frame(self.ui_picker, bg=self.col_wdw_default)
        frame.pack(side=TOP, anchor=NW, fill=BOTH, padx=self.default_padding, pady=self.default_padding)

        dir_txt_package = os.path.join(dir_asset_pipe, variation, 'txt_package')

        channels_json, channels_json_native, _ = txt_package_list_channels(dir_txt_package)
        '''channels_json = [x for x in os.listdir(dir_txt_package)
                         if os.path.isfile(os.path.join(dir_txt_package, x))]
        channels_json_native = [x for x in channels_json
                                if os.path.isdir(os.path.join(dir_txt_package, x.split('.')[0]))]'''

        x, y = self.ui_child.winfo_rootx(), self.ui_child.winfo_rooty()
        dimensions = f'311x{33+29*len(channels_json)+55}+{x+660}+{y+91}'
        self.ui_picker.geometry(dimensions)

        lbl_title = Label(frame, bd=1, text=title, anchor=N, justify=LEFT,
                          bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_title.grid(row=0, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                       pady=self.default_padding)

        self.dict_additions.clear()

        i = -1
        add_ttp = False
        for i, channel_json in enumerate(channels_json):
            if channel_json in channels_json_native:
                bg = self.col_bt_petrol
                abg = self.col_bt_petrol_highlight
                bg = self.col_wdw_title
                abg = self.col_wdw_title
            else:
                bg = self.col_bt_red
                abg = self.col_bt_red_highlight

                json_file_path = os.path.join(dir_txt_package, channel_json)
                with open(json_file_path, 'r') as json_file:
                    json_file_content = json.load(json_file)
                source_asset = json_file_content["asset"]
                source_variation = json_file_content["variation"]
                source_channel = json_file_content["channel"]
                add_ttp = True

            channel = channel_json.split('.')[0]

            tkvar_channel_usage = BooleanVar()
            tkvar_channel_usage.set(False)
            cb_channel = Checkbutton(frame, text=channel, var=tkvar_channel_usage, width=18,
                                     bg=bg, activebackground=abg,
                                     fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                     selectcolor=self.col_bt_bg_active, anchor=W)
            cb_channel.grid(row=i+1, column=0, sticky=NSEW, columnspan=1, padx=self.default_padding,
                            pady=self.default_padding)

            if add_ttp:
                CreateToolTip(cb_channel,
                              f"{channel} is an external channel in the source package too. True source:\n"
                              f"{source_asset} - {source_variation} - {source_channel}")

            lbl_as = Label(frame, bd=1, text=' as ', anchor=N, justify=LEFT,
                           bg=self.col_wdw_default, fg=self.col_bt_fg_default)
            lbl_as.grid(row=i+1, column=1, sticky=W, columnspan=1, padx=2 * self.default_padding,
                        pady=self.default_padding)

            tkvar_proxy = StringVar()
            tkvar_proxy.set(channel)
            i_proxy = Entry(frame, bd=1, textvariable=tkvar_proxy, width=18,
                            bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                            insertbackground=self.col_bt_fg_default)
            i_proxy.grid(row=i+1, column=2, sticky=NSEW, columnspan=1, padx=self.default_padding,
                         pady=1)

            self.dict_additions[channel] = {
                "proxy": tkvar_proxy,
                "usage": tkvar_channel_usage
            }

        bt_cancel = Button(frame, text='Cancel', width=12,
                           border=self.default_bt_bd,
                           bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                           activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                           command=lambda x=self.ui_picker: close_sub_ui(x))
        bt_cancel.grid(row=i+3, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                       pady=0)

        bt_apply = Button(frame, text='Add',
                          border=self.default_bt_bd,
                          bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                          activebackground=self.col_bt_bg_blue_highlight, activeforeground=self.col_bt_fg_default,
                          command=lambda x=dir_txt_package: self.apply_picker(x))
        bt_apply.grid(row=i+2, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                      pady=2*self.default_padding)

        for item in [frame, lbl_title]:
            item.bind('<Button-1>', self.move_picker_offset)
            item.bind('<B1-Motion>', self.move_picker)

        self.ui_picker.geometry('')

        self.ui_picker.attributes("-alpha", 1.0)
        self.ui_picker.mainloop()

    def pull_textures(self):
        """ Updates all version dropdown to the latest published version in.

        :return:
        """

        for channel in self.dict_native_version:
            full_path = os.path.join(self.dir_txt_package, f'{channel}.json')

            with open(full_path, 'r') as json_file:
                dict_channel = json.load(json_file)
            published_version = dict_channel["txt_publish"]
            dd = self.dict_native_version[channel]["dd"]

            self.switch_native_version(channel, published_version, dd, f'{channel}.{published_version}.json')

    def ui_switch_variation(self, variation):
        self.dd_variation.configure(text=variation)
        self.current_variation = variation
        bg_frame = self.col_wdw_title

        if len(self.dict_procedural_ui_elements_external) > 0:
            for category in self.dict_procedural_ui_elements_external:
                for elements in self.dict_procedural_ui_elements_external[category]:
                    for element in self.dict_procedural_ui_elements_external[category][elements]:
                        element.destroy()

        lbl_blank = Label(self.frame_left, bd=1, text='   ', anchor=W, justify=LEFT,
                          bg=bg_frame, fg=self.col_bt_fg_default, width=18)
        lbl_blank.grid(row=0, column=0, sticky=NSEW, padx=3*self.default_padding,
                       pady=self.default_padding)

        dir_variation = os.path.join(self.parent.dir_pipeline_txt, variation)
        self.dir_txt_package = os.path.join(dir_variation, 'txt_package')

        channels_json, channels_json_native, channels_json_external = txt_package_list_channels(self.dir_txt_package)

        self.dict_native_version.clear()
        self.dict_external_channels.clear()
        self.dict_procedural_ui_elements_external["nat"].clear()
        self.dict_procedural_ui_elements_external["ext"].clear()

        for i, channel_json_native in enumerate(channels_json_native):
            channel_native = channel_json_native.split('.')[0]
            # --- Native ---------------------------------------------------------------------------
            # --- Label ----------------------------------------------------------------------------
            lbl_channel_native = Label(self.frame_left, bd=1, text=channel_native, anchor=W, justify=LEFT,
                                       bg=bg_frame, fg=self.col_bt_fg_default, width=18)
            lbl_channel_native.grid(row=i, column=0, sticky=NSEW, padx=3*self.default_padding,
                                    pady=self.default_padding)

            # --- Dropdown -------------------------------------------------------------------------
            dir_channel_native = os.path.join(self.dir_txt_package, channel_native)
            channel_native_versions = os.listdir(dir_channel_native)
            channel_native_versions.sort()

            full_path = os.path.join(self.dir_txt_package, channel_json_native)
            with open(full_path, 'r') as json_output_channel:
                dict_channel = json.load(json_output_channel)

            current_channel = dict_channel[self.parent.current_discipline]

            # determine the latest version depending on the discipline
            if self.parent.current_discipline == 'txt':
                latest = channel_native_versions[-1]
            else:
                full_path = os.path.join(self.dir_txt_package, f'{channel_native}.json')

                with open(full_path, 'r') as json_file:
                    dict_channel = json.load(json_file)
                published_version = dict_channel["txt_publish"]

                latest = f'{channel_native}.{published_version}.json'

            if current_channel == latest.split('.')[1]:
                bg = self.col_bt_petrol
                abg = self.col_bt_petrol_highlight
            else:
                bg = self.col_bt_red
                abg = self.col_bt_red_highlight

            dd_version = Menubutton(self.frame_left, text=current_channel,
                                    bg=bg, fg=self.col_bt_fg_default,
                                    highlightthickness=0,
                                    activebackground=abg,
                                    anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                    relief=self.def_bt_relief, justify=RIGHT)
            dd_version.menu = Menu(dd_version, tearoff=0, bd=0, activeborderwidth=3,
                                   relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                   activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                   activebackground=self.col_bt_bg_blue_highlight)
            dd_version['menu'] = dd_version.menu

            # Add dropdown option per version
            for channel_native_version in channel_native_versions:
                version_number = channel_native_version.split('.')[1]

                # --- Metadata--------------------------------------------------------------------------
                full_path = os.path.join(self.dir_txt_package, channel_native,
                                         f'{channel_native}.{version_number}.json')
                with open(full_path, 'r') as json_output_channel:
                    dict_channel_current = json.load(json_output_channel)

                artist = dict_channel_current["artist"]
                time = dict_channel_current["time"]
                published = dict_channel_current["published"]

                publish_text = ''
                if published is True and self.parent.current_discipline == 'txt':
                    publish_text = '      previously published'

                metadata = f'artist: {artist}      time: {time}{publish_text}'
                # --------------------------------------------------------------------------------------
                text = '       '.join([version_number, metadata])

                if self.parent.current_discipline == 'txt' or published:
                    dd_version.menu.add_command(label=text,
                                                command=lambda x=channel_native, y=version_number, z=dd_version,
                                                a=latest:
                                                self.switch_native_version(x, y, z, a))

            if dd_version.menu.index("end") is None:
                CreateToolTip(dd_version,
                              "No version has yet been published")

            dd_version.grid(row=i, column=4, sticky=EW, padx=self.default_padding,
                            pady=self.default_padding)

            # --------------------------------------------------------------------------------------
            self.dict_native_version[channel_native] = {
                "version": current_channel,
                "latest": channel_native_versions[-1],
                "dd": dd_version
            }

            self.dict_procedural_ui_elements_external["nat"][channel_native] = [lbl_channel_native, dd_version]

        # EXTERNAL CHANNELS
        for i, channel_json_external in enumerate(channels_json_external):
            self.add_external_channel(channel_json_external,
                                      channel_json_external.split('.')[0], self.col_bt_petrol,
                                      self.dir_txt_package)  # bg_frame

        self.ui_menubutton_add_external()

    def switch_mt_variation(self, letter, dd, t):
        self.current_floating_variation[t] = letter
        dd.config(text=letter)

    def create_ui_add_variation(self):
        if self.ui_variation_creator is not None:
            if self.ui_variation_creator.winfo_exists():
                close_sub_ui(self.ui_variation_creator)

        title = f'Create Variation'

        self.ui_variation_creator = Toplevel(bg=self.col_wdw_default, bd=1, highlightcolor='black',
                                             highlightthickness=1, highlightbackground='black')
        self.ui_variation_creator.attributes("-alpha", 0.0)
        self.ui_variation_creator.iconbitmap(r'.\ui\icon_pipe.ico')
        self.ui_variation_creator.title(title)
        self.ui_variation_creator.overrideredirect(True)
        self.ui_variation_creator.wm_attributes("-topmost", 1)

        x, y = self.ui_child.winfo_rootx(), self.ui_child.winfo_rooty()
        dimensions = f'150x123+{x + -153}+{y}'
        self.ui_variation_creator.geometry(dimensions)

        frame = Frame(self.ui_variation_creator, bg=self.col_wdw_default)
        frame.pack(side=TOP, anchor=NW, fill=BOTH, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Model Variation -------------------------------------------------------------------------
        lbl_mdl_var = Label(frame, bd=1, text='Model Variation', anchor=N, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_mdl_var.grid(row=0, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                         pady=self.default_padding)

        letters = [x for x in string.ascii_uppercase]
        self.current_floating_variation['mdl'] = letters[0]
        dd_mdl_variation = Menubutton(frame, text=self.current_floating_variation['mdl'], width=4,
                                      bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                      highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                      anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                      relief=self.def_bt_relief, justify=RIGHT)
        dd_mdl_variation.menu = Menu(dd_mdl_variation, tearoff=0, bd=0, activeborderwidth=3,
                                     relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                     activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                     activebackground=self.col_bt_bg_blue_highlight)
        dd_mdl_variation['menu'] = dd_mdl_variation.menu

        for letter in letters:
            dd_mdl_variation.menu.add_command(label=letter,
                                              command=lambda l=letter, t='mdl',
                                              dd=dd_mdl_variation: self.switch_mt_variation(l, dd, t))

        dd_mdl_variation.grid(row=0, column=1, sticky=E, padx=1 * self.default_padding,
                              pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Texture Variation -----------------------------------------------------------------------
        lbl_txt_var = Label(frame, bd=1, text='Texture Variation', anchor=N, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_txt_var.grid(row=1, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                         pady=self.default_padding)

        self.current_floating_variation['txt'] = letters[0]
        dd_txt_variation = Menubutton(frame, text=self.current_floating_variation['txt'], width=4,
                                      bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                      highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                      anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                      relief=self.def_bt_relief, justify=RIGHT)
        dd_txt_variation.menu = Menu(dd_txt_variation, tearoff=0, bd=0, activeborderwidth=3,
                                     relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                     activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                     activebackground=self.col_bt_bg_blue_highlight)
        dd_txt_variation['menu'] = dd_txt_variation.menu

        for letter in letters:
            dd_txt_variation.menu.add_command(label=letter,
                                              command=lambda l=letter, t='txt',
                                              dd=dd_txt_variation: self.switch_mt_variation(l, dd, t))

        dd_txt_variation.grid(row=1, column=1, sticky=E, padx=1 * self.default_padding,
                              pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Button Cancel ---------------------------------------------------------------------------
        bt_cancel = Button(frame, text='Cancel', width=12,
                           border=self.default_bt_bd,
                           bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                           activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                           command=lambda z=self.ui_variation_creator: close_sub_ui(z))
        bt_cancel.grid(row=3, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                       pady=0)
        # ---------------------------------------------------------------------------------------------

        # --- Button Apply ----------------------------------------------------------------------------
        bt_apply = Button(frame, text='Add',
                          border=self.default_bt_bd,
                          bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                          activebackground=self.col_bt_bg_blue_highlight, activeforeground=self.col_bt_fg_default,
                          command=lambda: self.add_new_variation())
        bt_apply.grid(row=2, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                      pady=2 * self.default_padding)

        # ---------------------------------------------------------------------------------------------
        self.ui_variation_creator.attributes("-alpha", 1.0)
        for item in [frame, lbl_mdl_var, lbl_txt_var]:
            item.bind('<Button-1>', self.move_variation_creator_offset)
            item.bind('<B1-Motion>', self.move_variation_creator)

        self.ui_variation_creator.geometry('')

        self.ui_variation_creator.mainloop()

    def add_new_variation(self):
        new_variation = f"{self.current_floating_variation['mdl']}v{self.current_floating_variation['txt']}"

        dir_pipe_variation = os.path.join(self.parent.dir_asset, '.pipeline', new_variation)
        dir_export_variation = os.path.join(self.parent.dir_asset, 'txt', '_export', new_variation)

        dir_pipe_txt_package = os.path.join(dir_pipe_variation, 'txt_package')

        if os.path.isdir(dir_pipe_variation) or os.path.isdir(dir_export_variation):
            message = f'Variation {new_variation} already exists.'
            messagebox.showerror(title='Error', message=message)
        else:
            os.makedirs(dir_pipe_txt_package)
            os.makedirs(dir_export_variation)

            self.ui_switch_variation(new_variation)
            close_sub_ui(self.ui_variation_creator)
            self.dd_variation.menu.add_command(label=new_variation,
                                               command=lambda x=new_variation: self.ui_switch_variation(x))

    def ui_menubutton_add_external(self):
        if self.dd_add_external is not None:
            self.dd_add_external.destroy()
        self.dd_add_external = Menubutton(self.frame_main, image=self.icon_create, text=' +', width=26,
                                          bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                          highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                          anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                          relief=self.def_bt_relief, justify=RIGHT)
        self.dd_add_external.menu = Menu(self.dd_add_external, tearoff=0, bd=0, activeborderwidth=3,
                                         relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                         activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                         activebackground=self.col_bt_bg_blue_highlight)
        self.dd_add_external['menu'] = self.dd_add_external.menu

        dir_build = os.path.join(self.parent.current_root, self.parent.current_project_name, 'build')
        assets = os.listdir(dir_build)

        dict_assets = {
            "chr": [x for x in assets if x[0:3] == 'chr'],
            "veh": [x for x in assets if x[0:3] == 'veh'],
            "env": [x for x in assets if x[0:3] == 'env'],
            "prp": [x for x in assets if x[0:3] == 'prp'],
        }

        asset_types = []
        if len(dict_assets["chr"]) > 0:
            asset_types.append('chr')
        if len(dict_assets["veh"]) > 0:
            asset_types.append('veh')
        if len(dict_assets["env"]) > 0:
            asset_types.append('env')
        if len(dict_assets["prp"]) > 0:
            asset_types.append('prp')

        for asset_type in asset_types:
            type_menu = Menu(self.dd_add_external, tearoff=0, bd=0, activeborderwidth=3,
                             relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                             activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                             activebackground=self.col_bt_bg_blue_highlight)
            self.dd_add_external.menu.add_cascade(label=asset_type, menu=type_menu)

            assets_of_type = dict_assets[asset_type]
            for asset in assets_of_type:
                asset_menu = Menu(type_menu, tearoff=0, bd=0, activeborderwidth=3,
                                  relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                  activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                  activebackground=self.col_bt_bg_blue_highlight)
                type_menu.add_cascade(label=asset[3:], menu=asset_menu)

                #dir_asset_pipe = os.path.join(dir_build, asset, '.pipeline')

                variations = os.listdir(self.parent.dir_pipeline_txt)#dir_asset_pipe)

                for variation in variations:
                    if variation != self.current_variation:
                        asset_menu.add_command(label=variation,
                                               command=lambda x=self.parent.dir_pipeline_txt, y=variation,
                                               z=asset: self.create_ui_picker_channels(x, y, z))

        self.dd_add_external.grid(row=2, column=3, sticky=E, columnspan=1, padx=3 * self.default_padding,
                                  pady=self.default_padding)

    def create_ui_package_manager_txt(self, parent):
        dimensions = '662x103+420+100'
        self.parent = parent

        self.ui_proxy = Tk()
        ui_package_manager_txt = Toplevel()
        ui_package_manager_txt.lift()
        ui_package_manager_txt.attributes("-alpha", 0.0)
        ui_package_manager_txt.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_package_manager_txt.title('Texture Package Manager')
        ui_package_manager_txt.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, ui_package_manager_txt, 'Texture Package Manager',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
        ui_package_manager_txt.configure(bg=self.col_wdw_default)

        self.icon_create = PhotoImage(file=r'.\ui\bt_create.png')
        self.icon_delete = PhotoImage(file=r'.\ui\bt_delete.png')

        self.frame_main = Frame(ui_package_manager_txt, bg=self.col_wdw_default)
        self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Label Asset -----------------------------------------------------------------------------
        text = f'{self.parent.current_discipline.upper()}  //  {self.parent.current_asset}'
        lbl_asset = Label(self.frame_main, bd=1, text=text, anchor=W, justify=LEFT,
                          bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_asset.grid(row=0, column=0, sticky=W, columnspan=2, padx=3*self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Dropdown Variations ---------------------------------------------------------------------
        self.variations = [x for x in os.listdir(parent.dir_pipeline_txt)
                           if os.path.isdir(os.path.join(parent.dir_pipeline_txt, x))]
        self.current_variation = self.variations[0]
        self.dd_variation = Menubutton(self.frame_main, text=self.current_variation, width=4,
                                       bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                       highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                       anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                       relief=self.def_bt_relief, justify=RIGHT)
        self.dd_variation.menu = Menu(self.dd_variation, tearoff=0, bd=0, activeborderwidth=3,
                                      relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                      activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                      activebackground=self.col_bt_bg_blue_highlight)
        self.dd_variation['menu'] = self.dd_variation.menu

        for variation in self.variations:
            self.dd_variation.menu.add_command(label=variation, command=lambda x=variation: self.ui_switch_variation(x))

        self.dd_variation.menu.add_command(label='+', command=lambda: self.create_ui_add_variation())

        self.dd_variation.grid(row=0, column=1, sticky=E, padx=3*self.default_padding,
                               pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        frame_top_right = Frame(self.frame_main, bg=self.col_wdw_default)
        frame_top_right.grid(row=0, column=2, sticky=NSEW, columnspan=2, padx=2 * self.default_padding,
                             pady=self.default_padding)
        frame_top_right.grid_columnconfigure(0, weight=1)
        # --- Checkbox publish ------------------------------------------------------------------------
        self.tkvar_publish = BooleanVar()
        self.tkvar_publish.set(False)
        cb_publish = Checkbutton(frame_top_right, text='publish', var=self.tkvar_publish, anchor=E,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active)
        cb_publish.grid(row=0, column=0, sticky=E, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Save Button -----------------------------------------------------------------------------
        bt_save = Button(frame_top_right, text='Save', border=self.default_bt_bd, width=8,
                         bg=self.col_bt_bg_green, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                         activebackground=self.col_bt_bg_green_highlight, activeforeground=self.col_bt_fg_default,
                         command=lambda: self.save())
        bt_save.grid(row=0, column=1, sticky=NSEW, columnspan=1, padx=0,
                     pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # --- Separator -------------------------------------------------------------------------------
        frame_separator = Frame(self.frame_main, bg="gray60", height=1)
        frame_separator.grid(row=1, column=0, columnspan=4, sticky=NSEW, padx=self.default_padding, pady=3)
        # ---------------------------------------------------------------------------------------------
        width_boxes = 66
        # --- Headers ---------------------------------------------------------------------------------
        # --- Label Native Channels -------------------------------------------------------------------
        lbl_native = Label(self.frame_main, bd=1, text='Native Channel', anchor=CENTER, justify=LEFT,
                           bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=20)
        lbl_native.grid(row=2, column=0, sticky=W, columnspan=1, padx=self.default_padding, pady=self.default_padding)
        # --- Label External Channels ------------------------------------------------------------------
        lbl_external = Label(self.frame_main, bd=1, text='External Channels', anchor=CENTER, justify=LEFT,
                             bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=width_boxes-7)
        lbl_external.grid(row=2, column=2, sticky=NSEW, columnspan=1, padx=self.default_padding,
                          pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # -- Button - Non texturing--------------------------------------------------------------------
        if self.parent.current_discipline != 'txt':
            state = NORMAL
        else:
            state = DISABLED

        bt_pull_publish = Button(self.frame_main, text='pull', width=4, state=state,
                                 border=self.default_bt_bd,
                                 bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.pull_textures())
        bt_pull_publish.grid(row=2, column=1, sticky=E, columnspan=1, padx=3*self.default_padding,
                             pady=self.default_padding)

        # -- DD menu add external ---------------------------------------------------------------------
        self.ui_menubutton_add_external()
        # ---------------------------------------------------------------------------------------------

        # -- Frames -----------------------------------------------------------------------------------
        self.frame_left = Frame(self.frame_main, bg=self.col_wdw_title)
        self.frame_left.grid(row=4, column=0, sticky=NSEW, columnspan=2, padx=2*self.default_padding,
                             pady=self.default_padding)
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.frame_right = Frame(self.frame_main, bg=self.col_wdw_title)
        self.frame_right.grid(row=4, column=2, sticky=NSEW, columnspan=2, padx=2*self.default_padding,
                              pady=self.default_padding)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)
        # ---------------------------------------------------------------------------------------------

        # ---- Procedural Section ---------------------------------------------------------------------
        self.ui_switch_variation(self.current_variation)
        # ---------------------------------------------------------------------------------------------
        ui_package_manager_txt.geometry('')

        ui_package_manager_txt.attributes("-alpha", 1.0)
        ui_package_manager_txt.wm_attributes("-topmost", 1)
        ui_package_manager_txt.mainloop()


#PackageManagerTxt()
# TODO picker needs to show original of sub layers of external channel - TOOLTIP
# TODO move connection update to pipe utils and have it be used by the release tool as well

"""package manager model section: (recreate it)
model selection like native channel selection
texture package selection
texture roll back 
"""