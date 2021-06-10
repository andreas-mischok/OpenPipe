# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pipe_utils import *


class PackageManagerTxt:
    def __init__(self):
        self.dir_asset = self.dir_export = self.dir_pantry = self.dir_pipeline = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.dd_variation = \
            self.current_variation = self.default_padding = self.col_bt_fg_default = \
            self.col_bt_bg_blue = self.col_bt_blue_highlight = self.col_bt_bg_blue_highlight = \
            self.def_bt_relief = self.col_wdw_default = self.col_bt_bg_active = self.col_bt_bg_default = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.connections_default = self.frame_main = self.variations = self.connections = \
            self.connection_ui_elements = self.col_bt_red = self.col_bt_red_highlight = \
            self.col_bt_petrol = self.col_bt_petrol_highlight = self.col_bt_bg_green = \
            self.col_bt_bg_green_highlight = self.default_bt_bd = self.dict_connections = None

        self.user = os.getenv('PIPE_USER')
        self.current_root = os.getenv('PIPE_ROOT')
        self.current_project_name = os.getenv('PIPE_PROJECT')
        self.current_department = os.getenv('PIPE_DEPARTMENT')
        self.current_asset = os.getenv('PIPE_ASSET')

        generate_paths(self)
        self.dir_pipeline_txt = os.path.join(self.dir_pipeline, 'txt')
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.create_ui_package_manager_txt()

    def move_window_offset(self, event):
        window_x = self.ui_child.winfo_x()
        window_y = self.ui_child.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_window(self, event):
        x_new = event.x_root - self.x_offset
        y_new = event.y_root - self.y_offset
        self.ui_child.geometry(f'+{x_new}+{y_new}')

    def on_root_deiconify(self, _):
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def switch_connection(self, channel, dd_connection, key, external_channels):
        text = channel.split('.')[0]
        if channel in external_channels:
            bg = self.col_bt_red
            abg = self.col_bt_red_highlight
        else:
            bg = self.col_bt_petrol
            abg = self.col_bt_petrol_highlight

        if text == '':
            bg = self.col_bt_bg_default
            abg = self.col_wdw_default
        dd_connection.config(text=text, bg=bg, activebackground=abg)

        self.dict_connections[key] = text

    def switch_variation(self, variation):
        self.dd_variation.configure(text=variation)
        self.current_variation = variation

        if self.connection_ui_elements is not None:
            for elements in self.connection_ui_elements:
                for element in elements:
                    element.destroy()

        dir_variation = os.path.join(self.dir_pipeline_txt, variation)
        file_package_txt = os.path.join(dir_variation, 'txt_connections.json')

        row = 2

        with open(file_package_txt, 'r') as config_file:
            config_content = json.load(config_file)

        self.dict_connections = config_content
        self.connections = []
        self.connection_ui_elements = []

        for i, key in enumerate(config_content):
            # --- Label Connection ------------------------------------------------------------------------
            row = i + 2
            text = key.replace('_', ' ').capitalize()
            lbl_key = Label(self.frame_main, bd=1, text=f'{text}   ', anchor=W, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=17)
            lbl_key.grid(row=row, column=0, sticky=W, padx=3 * self.default_padding, pady=self.default_padding)

            # --- Dropdown Connection ---------------------------------------------------------------------
            dir_txt_package = os.path.join(dir_variation, 'txt_package')
            channels_json = [x for x in os.listdir(dir_txt_package)
                             if os.path.isfile(os.path.join(dir_txt_package, x))]
            channels_json_local = [x for x in channels_json
                                   if os.path.isdir(os.path.join(dir_txt_package, x.split('.')[0]))]
            channels_json_external = [x for x in channels_json if x not in channels_json_local]

            current_channel = config_content[key]
            dd_channel = Menubutton(self.frame_main, text=current_channel,
                                    bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                    highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                    anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                    relief=self.def_bt_relief, justify=RIGHT)
            dd_channel.menu = Menu(dd_channel, tearoff=0, bd=0, activeborderwidth=3,
                                   relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                   activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                   activebackground=self.col_bt_bg_blue_highlight)
            dd_channel['menu'] = dd_channel.menu

            for channel in channels_json:
                dd_channel.menu.add_command(label=channel.split('.')[0],
                                            command=lambda x=channel, y=dd_channel, z=key:
                                            self.switch_connection(x, y, z, channels_json_external))
            dd_channel.menu.add_command(label='',
                                        command=lambda x='', y=dd_channel, z=key:
                                        self.switch_connection(x, y, z, channels_json_external))

            dd_channel.grid(row=row, column=1, sticky=EW, padx=self.default_padding,
                            pady=self.default_padding)

            self.connections = []
            self.switch_connection(f'{current_channel}.json', dd_channel, key,
                                   channels_json_external)
            self.connection_ui_elements.append([lbl_key, dd_channel])

        return row

    def save_texture_connections(self):
        dir_variation = os.path.join(self.dir_pipeline_txt, self.current_variation)
        file_package_txt = os.path.join(dir_variation, 'txt_connections.json')

        with open(file_package_txt, 'w') as json_output:
            json.dump(self.dict_connections, json_output, indent=2)

        message = "Successfully updated default texture connections."
        messagebox.showinfo(title='', message=message)

    def create_ui_package_manager_txt(self):
        self.variations = [x for x in os.listdir(os.path.join(self.dir_pipeline_txt))
                           if os.path.isdir(os.path.join(self.dir_pipeline_txt, x))]
        if len(self.variations) != 0:
            self.current_variation = self.variations[0]

            dir_variation = str(os.path.join(self.dir_pipeline_txt, self.current_variation))
            file_package_txt = os.path.join(dir_variation, 'txt_connections.json')

            if os.path.isfile(file_package_txt):

                self.ui_proxy = Tk()
                ui_package_manager_txt = Toplevel()
                ui_package_manager_txt.lift()
                ui_package_manager_txt.attributes("-alpha", 0.0)
                ui_package_manager_txt.iconbitmap(r'.\ui\icon_pipe.ico')
                ui_package_manager_txt.title('Connection Manager')
                ui_title_bar(self, self.ui_proxy, ui_package_manager_txt, 'Connection Manager',
                             r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
                ui_package_manager_txt.configure(bg=self.col_wdw_default)

                self.frame_main = Frame(ui_package_manager_txt, bg=self.col_wdw_default)
                self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)

                # --- Label Connection ------------------------------------------------------------------------
                lbl_key = Label(self.frame_main, bd=1, text='Variation', anchor=W, justify=LEFT,
                                bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=17)
                lbl_key.grid(row=0, column=0, sticky=W, padx=3 * self.default_padding, pady=self.default_padding)
                # ---------------------------------------------------------------------------------------------

                # --- Dropdown Variations ---------------------------------------------------------------------
                self.dd_variation = Menubutton(self.frame_main, text=self.current_variation, width=5,
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
                    self.dd_variation.menu.add_command(label=variation,
                                                       command=lambda x=variation: self.switch_variation(x))

                self.dd_variation.grid(row=0, column=1, sticky=EW, padx=self.default_padding,
                                       pady=self.default_padding)
                # ---------------------------------------------------------------------------------------------

                # --- Separator -------------------------------------------------------------------------------
                frame_separator = Frame(self.frame_main, bg="gray60", height=1)
                frame_separator.grid(row=1, column=0, columnspan=2, sticky=NSEW, padx=self.default_padding, pady=3)
                # ---------------------------------------------------------------------------------------------

                # ---- Channel connections --------------------------------------------------------------------
                last_row = self.switch_variation(self.current_variation)
                # ---------------------------------------------------------------------------------------------

                # --- Separator -------------------------------------------------------------------------------
                frame_separator2 = Frame(self.frame_main, bg="gray60", height=1)
                frame_separator2.grid(row=last_row + 1, column=0, columnspan=2, sticky=NSEW,
                                      padx=self.default_padding, pady=3)
                # ---------------------------------------------------------------------------------------------

                # --- Button Save -----------------------------------------------------------------------------
                bt_save = Button(self.frame_main, text='Save', height=2,
                                 border=self.default_bt_bd,
                                 bg=self.col_bt_bg_green, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active,
                                 command=lambda: self.save_texture_connections())
                bt_save.grid(row=last_row + 2, column=0, columnspan=2, sticky=NSEW, padx=self.default_padding,
                             pady=self.default_padding)
                # ---------------------------------------------------------------------------------------------
                ui_package_manager_txt.geometry('+420+100')
                ui_package_manager_txt.geometry('')

                ui_package_manager_txt.attributes("-alpha", 1.0)
                ui_package_manager_txt.mainloop()

            else:
                self.ui_proxy = Tk()
                self.ui_proxy.attributes("-alpha", 0.0)
                message = f'No channel in assets texture package, no default connections have been established.'
                messagebox.showinfo(title='', message=message)
                self.ui_proxy.destroy()

        else:
            self.ui_proxy = Tk()
            self.ui_proxy.attributes("-alpha", 0.0)
            messagebox.showerror('Error', 'TXT package not found. Connections can only be modified after textures '
                                          'have been released.')
            self.ui_proxy.destroy()


PackageManagerTxt()
