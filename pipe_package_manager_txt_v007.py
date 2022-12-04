import string
import shutil as sh
from pipe_utils import *


class PackageManager:
    def __init__(self):
        self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.dd_variation = \
            self.default_padding = self.col_bt_fg_default = self.frame_txt_left = \
            self.col_bt_bg_blue = self.col_bt_blue_highlight = self.col_bt_bg_blue_highlight = \
            self.def_bt_relief = self.col_wdw_default = self.col_bt_bg_active = self.col_bt_bg_default = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.connections_default = self.frame_main = self.variations = self.connections = \
            self.connection_ui_elements = self.frame_txt_right = self.ui_picker = \
            self.col_bt_red = self.col_bt_red_highlight = self.col_bt_petrol = self.ui_variation_creator = \
            self.col_bt_bg_green = self.col_bt_bg_green_highlight = self.dd_add_external = \
            self.col_bt_petrol_highlight = self.default_bt_bd = self.icon_delete = self.tkvar_publish_mdl = \
            self.icon_create = self.col_i_bg_default = self.parent = self.dd_mdl_version = self.frame_mdl = \
            self.mdl_version_current = self.dict_mdl_package = self.col_bt_yellow = self.col_bt_yellow_highlight = \
            self.temporary_ui_variations = self.frame_mdl_variations = self.dir_pipe_mdl_versions = \
            self.file_mdl_package = self.mdl_versions = self.mdl_items = self.txt_current_variation = \
            self.dd_txt_variation = self.dir_pipe_txt_package = self.frame_txt = self.frame_shd = self.shd_items = \
            self.dir_pipe_shd_versions = self.file_shd_package = self.dict_shd_package = self.shd_version_current = \
            self.shd_versions = self.dd_shd_version = self.shd_variations = self.tkvar_publish_shd = \
            self.ui_elements_shading = self.col_bt_bg_default_highlight = None

        self.mdl_variation_combinations = {}
        self.shd_variations_elements = {}

        self.dict_native_version = {}
        self.dict_txt_external_channels = {}
        self.dict_procedural_ui_elements_external = {
            "nat": {},
            "ext": {}
        }
        self.dict_txt_additions = {}
        self.current_floating_txt_variation = {}

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

    def move_window_offset(self, event):
        """ Returns the current window position in relation to the cursor.

        :return:
        """
        window_x = self.ui_child.winfo_x()
        window_y = self.ui_child.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_window(self, event):
        """ Moves the window when header is clicked.

        :return:
        """
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_child.geometry(f'+{x_new}+{y_new}')

    def move_txt_variation_creator_offset(self, event):
        window_x = self.ui_variation_creator.winfo_x()
        window_y = self.ui_variation_creator.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_txt_variation_creator(self, event):
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_variation_creator.geometry(f'+{x_new}+{y_new}')

    def on_root_deiconify(self, _):
        """ Iconifies the proxy window and deiconifies the child window.
        This is to bind the visible UI (child) to the taskbar without using the default title bar

        :return:
        """
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def save_mdl(self):
        dict_variation_combinations = {}
        success = True
        for mdl_var in self.mdl_variation_combinations:
            variable_content = self.mdl_variation_combinations[mdl_var].get()
            if '*' in variable_content:
                variable_content = '*'
            if len([x for x in variable_content if x.isdigit()]) != 0:
                success = False
                messagebox.showerror(title='Error', message=
                                     f"Illegal character given for texture variations for model variation {mdl_var}")
                break
            else:
                dict_variation_combinations[mdl_var] = variable_content
                #print(mdl_var, variable_content)

        # Only continue if no errors occurred during gathering of information
        if success:
            publish = self.tkvar_publish_mdl.get()

            # Edit MDL Package json file
            # update version of model package
            # if publishing is active
            new_version = self.mdl_version_current

            if self.parent.current_discipline == 'mdl':
                # If rollback
                if self.dict_mdl_package["mdl"] != self.mdl_version_current:
                    latest = self.mdl_versions[0]
                    version_cur_int = int(latest[1:]) + 1
                    new_version = 'v' + format(version_cur_int, '03d')

                    file_source = os.path.join(self.dir_pipe_mdl_versions,
                                               f'{self.parent.current_asset}.{self.mdl_version_current}.json')
                    file_target = os.path.join(self.dir_pipe_mdl_versions,
                                               f'{self.parent.current_asset}.{new_version}.json')
                    sh.copy2(file_source, file_target)

                    # Set publish status of version file to checkbox value
                    file_mdl_version = os.path.join(self.dir_pipe_mdl_versions,
                                                    f'{self.parent.current_asset}.{new_version}.json')
                    with open(file_mdl_version, 'r') as json_file:
                        dict_content_mdl_version = json.load(json_file)
                    dict_content_mdl_version["published"] = publish
                    with open(file_mdl_version, 'w') as json_file:
                        json.dump(dict_content_mdl_version, json_file, indent=2)

                if publish:
                    # Assign first MDL stream only settings
                    self.dict_mdl_package["mdl_publish"] = new_version

            self.dict_mdl_package["variations"] = dict_variation_combinations
            self.dict_mdl_package[self.parent.current_discipline] = new_version

            with open(self.file_mdl_package, 'w') as json_file:
                json.dump(self.dict_mdl_package, json_file, indent=2)

        # update dropdown
        self.ui_items_mdl()
        self.parent.check_for_outdated_packages()

    def save_shd(self):
        for var in self.shd_variations:
            """
                    "current_version": shd_version_current,
                    "dropdown": dd_shd_version,
                    dir_shd_variation
                    latest_version
                    "file_shd_package": file_shd_package,
                    "dir_pipe_shd_versions": dir_pipe_shd_versions,
                    "dict_shd_package": dict_shd_package"""

            dict_shd_package = self.shd_variations_elements[var]["dict_shd_package"]
            dir_pipe_shd_versions = self.shd_variations_elements[var]["dir_pipe_shd_versions"]
            file_shd_package = self.shd_variations_elements[var]["file_shd_package"]
            current_version = self.shd_variations_elements[var]["current_version"]
            latest_version = self.shd_variations_elements[var]["latest_version"]

            dict_shd_package[self.parent.current_discipline] = current_version

            if self.parent.current_discipline == 'shd':
                file_shd_version = os.path.join(dir_pipe_shd_versions,
                                                f'{self.parent.current_asset}.{current_version}.json')

                if current_version != latest_version:
                    version_cur_int = int(latest_version[1:]) + 1
                    new_version = 'v' + format(version_cur_int, '03d')

                    file_source = os.path.join(dir_pipe_shd_versions,
                                               f'{self.parent.current_asset}.{current_version}.json')
                    file_shd_version = os.path.join(dir_pipe_shd_versions,
                                                    f'{self.parent.current_asset}.{new_version}.json')
                    sh.copy2(file_source, file_shd_version)
                    current_version = new_version

                with open(file_shd_version, 'r') as json_file:
                    dict_shd_version = json.load(json_file)

                if self.tkvar_publish_shd.get():
                    dict_shd_package["shd_publish"] = current_version

                    dict_shd_version["published"] = True
                else:
                    dict_shd_version["published"] = False

                with open(file_shd_version, 'w') as json_file:
                    json.dump(dict_shd_version, json_file, indent=2)

            dict_shd_package[self.parent.current_discipline] = current_version

            with open(file_shd_package, 'w') as json_file:
                json.dump(dict_shd_package, json_file, indent=2)

        self.ui_items_shd()

    # TODO for SHD package: separate publish states for each variation
    # TODO FOR MDL package: if in model stream, colour needs to indicate whether the version is published, not if it is changed
    # TODO only allow save if all texture variations do exist (MDL package)
    # TODO update dropdown if rollback

    def pull_mdl(self):
        pull_version = self.dict_mdl_package["mdl_publish"]

        file_mdl_version = os.path.join(self.dir_pipe_mdl_versions,
                                        f'{self.parent.current_asset}.{pull_version}.json')
        with open(file_mdl_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)
        self.ui_switch_mdl_version(pull_version, dict_mdl_version)

    def pull_shd(self):
        for var in self.shd_variations:
            dict_shd_package = self.shd_variations_elements[var]["dict_shd_package"]
            #dir_pipe_shd_versions = self.shd_variations_elements[var]["dir_pipe_shd_versions"]

            pull_version = dict_shd_package["shd_publish"]

            #file_shd_version = os.path.join(dir_pipe_shd_versions,
            #                                f'{self.parent.current_asset}.{pull_version}.json')
            #with open(file_shd_version, 'r') as json_file:
            #    dict_shd_version = json.load(json_file)

            self.ui_switch_shd_version(pull_version, var)

    def ui_switch_mdl_version(self, mdl_version, dict_mdl_version):
        self.mdl_version_current = mdl_version

        bg = self.col_bt_petrol
        abg = self.col_bt_petrol_highlight

        # If the given mdl version differs from the version set for this stream
        if self.dict_mdl_package[self.parent.current_discipline] != self.mdl_version_current:
            bg = self.col_bt_yellow
            abg = self.col_bt_yellow_highlight
        # If not modelling discipline
        if self.parent.current_discipline != 'mdl':
            # if given != current publish
            if self.mdl_version_current != self.dict_mdl_package["mdl_publish"]:
                bg = self.col_bt_red
                abg = self.col_bt_red_highlight
            # if given version matches publish
            else:
                # If version is about to be changed
                if self.dict_mdl_package[self.parent.current_discipline] != self.mdl_version_current:
                    bg = self.col_bt_petrol
                    abg = self.col_bt_petrol_highlight

        self.dd_mdl_version.configure(text=mdl_version, bg=bg, activebackground=abg)

        self.ui_items_mdl_variations(dict_mdl_version)

    def ui_items_mdl_variations(self, dict_mdl_version):
        dict_variations = self.dict_mdl_package["variations"]
        variations = [key for key in dict_variations]

        if self.temporary_ui_variations is not None:
            for element in self.temporary_ui_variations:
                element.destroy()

        self.temporary_ui_variations = []
        self.mdl_variation_combinations.clear()

        for i, variation in enumerate(variations):
            state = NORMAL if variation in dict_mdl_version["variations"] else DISABLED

            row = int(i/3)
            column = i % 3

            label_variation = Label(self.frame_mdl_variations, bd=1, text=variation, anchor=CENTER, justify=CENTER,
                                    state=state, padx=2, width=3, pady=3,
                                    bg=self.col_wdw_default, fg=self.col_bt_fg_default)
            label_variation.grid(row=row, column=2*column, sticky=W, columnspan=1, padx=self.default_padding,
                                 pady=self.default_padding)
            if state == NORMAL:
                text = "This model variation exists in the current MDL package."
            else:
                text = "This model variation is not in the current MDL package."
            CreateToolTip(label_variation, text, None, None, False)

            tkvar_txt_vars = StringVar()
            tkvar_txt_vars.set(dict_variations[variation])

            i_txt_vars = Entry(self.frame_mdl_variations, bd=1, textvariable=tkvar_txt_vars, width=33,
                               disabledbackground=self.col_bt_bg_default,
                               bg='gray40', fg=self.col_bt_fg_default, relief=self.def_bt_relief, state=state,
                               insertbackground=self.col_bt_fg_default)
            i_txt_vars.grid(row=row, column=2*column+1, sticky=NSEW, padx=self.default_padding,
                            pady=self.default_padding)
            CreateToolTip(i_txt_vars,
                          #f"Texture variations used in conjunction with model variation {variation}.\n\n"
                          f"Texture variations that this model variation ({variation}) will be available to.\n\n"
                          f"Example: ABCDE\n"
                          f"* = use all variations\n"
                          f"No commas used for separation!", None, None, False)

            self.mdl_variation_combinations[variation] = tkvar_txt_vars

    def ui_switch_shd_version(self, shd_version, var):
        #self.shd_version_current[var] = shd_version
        self.shd_variations_elements[var]["current_version"] = shd_version
        dict_shd_package = self.shd_variations_elements[var]["dict_shd_package"]

        bg = self.col_bt_petrol
        abg = self.col_bt_petrol_highlight

        # If the given shd version differs from the version set for this stream
        if dict_shd_package[self.parent.current_discipline] != shd_version:
            bg = self.col_bt_yellow
            abg = self.col_bt_yellow_highlight
        # If not shading discipline
        if self.parent.current_discipline != 'shd':
            # if given != current publish
            if shd_version != dict_shd_package["shd_publish"]:
                bg = self.col_bt_red
                abg = self.col_bt_red_highlight
            # if given version matches publish
            else:
                # If version is about to be changed
                if dict_shd_package[self.parent.current_discipline] != shd_version:
                    bg = self.col_bt_petrol
                    abg = self.col_bt_petrol_highlight

        self.shd_variations_elements[var]["dropdown"].configure(text=shd_version, bg=bg,
                                                                activebackground=abg)

    def dd_add_shd_version(self, shd_version, var):
        dir_pipe_shd_versions = self.shd_variations_elements[var]["dir_pipe_shd_versions"]
        file_shd_version = os.path.join(dir_pipe_shd_versions,
                                        f'{self.parent.current_asset}.{shd_version}.json')
        with open(file_shd_version, 'r') as json_file:
            dict_shd_version = json.load(json_file)

        artist = dict_shd_version["artist"]
        time = dict_shd_version["time"]
        published = dict_shd_version["published"]

        publish_text = '                    '
        if published is True and self.parent.current_discipline == 'shd':
            publish_text = 'previously pushed'

        text = '         '.join([shd_version, artist, time, publish_text])

        if self.parent.current_discipline == 'shd' or published:
            dd = self.shd_variations_elements[var]["dropdown"]
            dd.menu.add_command(label=text, command=lambda x=shd_version, z=var:
                                self.ui_switch_shd_version(x, z))

    def dd_add_mdl_version(self, mdl_version):
        file_mdl_version = os.path.join(self.dir_pipe_mdl_versions,
                                        f'{self.parent.current_asset}.{mdl_version}.json')
        with open(file_mdl_version, 'r') as json_file:
            dict_mdl_version = json.load(json_file)

        artist = dict_mdl_version["artist"]
        time = dict_mdl_version["time"]
        published = dict_mdl_version["published"]
        variations_of_version = dict_mdl_version["variations"]
        str_variations_of_version = ', '.join(variations_of_version)

        publish_text = '                    '
        if published is True and self.parent.current_discipline == 'mdl':
            publish_text = 'previously published'

        text = '         '.join([mdl_version, artist, time, str_variations_of_version, publish_text])

        if self.parent.current_discipline == 'mdl' or published:
            self.dd_mdl_version.menu.add_command(label=text, command=lambda x=mdl_version, y=dict_mdl_version:
                                                 self.ui_switch_mdl_version(x, y))

    def on_bt_enter_grey(self, e):
        if e.widget["state"] in [NORMAL, ACTIVE]:
            e.widget['background'] = self.col_bt_bg_default_highlight

    def on_bt_leave_grey(self, e):
        if e.widget["state"] in [NORMAL, ACTIVE]:
            e.widget['background'] = self.col_bt_bg_default

    def on_bt_enter_green(self, e):
        if e.widget["state"] in [NORMAL, ACTIVE]:
            e.widget['background'] = self.col_bt_bg_green_highlight

    def on_bt_leave_green(self, e):
        if e.widget["state"] in [NORMAL, ACTIVE]:
            e.widget['background'] = self.col_bt_bg_green

    def ui_items_shd(self):
        if self.ui_elements_shading is not None:
            for item in self.ui_elements_shading:
                item.destroy()

        if len(os.listdir(self.parent.dir_pipeline_shd)) != 0:
            # --- Label SHD -------------------------------------------------------------------------------
            lbl_shd = Label(self.frame_shd, bd=1, text='SHD Package', anchor=W, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
            lbl_shd.grid(row=0, column=0, sticky=W, columnspan=1, padx=3*self.default_padding, pady=self.default_padding)

            self.frame_shd.columnconfigure(3, weight=1)
            # --- DD SHD version --------------------------------------------------------------------------
            frame_shd_variations = Frame(self.frame_shd, bg=self.col_wdw_title)
            frame_shd_variations.grid(row=1, column=0, sticky=NSEW, columnspan=6, padx=3*self.default_padding,
                                      pady=self.default_padding)

            self.shd_variations = [x for x in os.listdir(self.parent.dir_pipeline_shd)
                                   if os.path.isdir(os.path.join(self.parent.dir_pipeline_shd, x))]

            self.ui_elements_shading = []
            self.shd_variations_elements.clear()

            if len(self.shd_variations) != 0:
                for i, var in enumerate(self.shd_variations):
                    amount = 10
                    row = int(i / amount)
                    column = i % amount
                    lbl_shd_var = Label(frame_shd_variations, bd=1, text=var, anchor=CENTER, justify=CENTER, #state=state,
                                        padx=2, width=3,
                                        bg=self.col_wdw_default, fg=self.col_bt_fg_default)
                    lbl_shd_var.grid(row=row, column=2*column, sticky=NSEW, columnspan=1, padx=self.default_padding,
                                     pady=self.default_padding)

                    # DD SHD
                    dir_shd_variation = str(os.path.join(self.parent.dir_pipeline_shd, var))
                    dir_pipe_shd_versions = os.path.join(dir_shd_variation, 'versions')

                    file_shd_package = os.path.join(dir_shd_variation, 'shd_package.json')

                    with open(file_shd_package, 'r') as json_file:
                        dict_shd_package = json.load(json_file)
                    shd_version_current = dict_shd_package[self.parent.current_discipline]

                    dd_shd_version = Menubutton(frame_shd_variations, text='', width=4,
                                                bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                                highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                                anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                                relief=self.def_bt_relief, justify=RIGHT)
                    dd_shd_version.menu = Menu(dd_shd_version, tearoff=0, bd=0, activeborderwidth=3,
                                               relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                               activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                               activebackground=self.col_bt_bg_blue_highlight)
                    dd_shd_version['menu'] = dd_shd_version.menu

                    shd_versions = sorted([x.split('.')[1] for x in os.listdir(dir_pipe_shd_versions)])
                    shd_versions.reverse()

                    self.shd_variations_elements[var] = {
                        "current_version": shd_version_current,
                        "latest_version": shd_versions[0],
                        "dropdown": dd_shd_version,
                        "file_shd_package": file_shd_package,
                        "dir_shd_variation": dir_shd_variation,
                        "dir_pipe_shd_versions": dir_pipe_shd_versions,
                        "dict_shd_package": dict_shd_package
                    }

                    for shd_version in shd_versions:
                        self.dd_add_shd_version(shd_version, var)

                    dd_shd_version.grid(row=row, column=2*column+1, sticky=W, columnspan=1, padx=self.default_padding,
                                        pady=self.default_padding)

                    self.ui_switch_shd_version(shd_version_current, var)

                    for item in [dd_shd_version, lbl_shd_var]:
                        self.ui_elements_shading.append(item)

            # --- PULL BUTTON ------------------------------------------------------------------------------------
            state = DISABLED if self.parent.current_discipline == 'shd' else NORMAL
            bt_pull_shd = Button(self.frame_shd, text='Pull', border=self.default_bt_bd, width=6, state=state,
                                 bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.pull_shd())
            bt_pull_shd.grid(row=0, column=1, sticky=NSEW, columnspan=1, padx=3 * self.default_padding,
                             pady=self.default_padding)
            bt_pull_shd.bind('<Enter>', self.on_bt_enter_grey)
            bt_pull_shd.bind('<Leave>', self.on_bt_leave_grey)

            # --- MDL PUBLISH CHECKBOX --------------------------------------------------------------------------
            shd_state = NORMAL if self.parent.current_discipline == 'shd' else DISABLED
            self.tkvar_publish_shd = BooleanVar()
            self.tkvar_publish_shd.set(False)
            cb_publish_shd = Checkbutton(self.frame_shd, text='push', var=self.tkvar_publish_shd, state=shd_state,
                                         bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                         fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                         selectcolor=self.col_bt_bg_active)
            cb_publish_shd.grid(row=0, column=4, sticky=N, padx=self.default_padding, pady=self.default_padding)

            # --- SHD SAVE BUTTON -------------------------------------------------------------------------------
            bt_save_shd = Button(self.frame_shd, text='Save', border=self.default_bt_bd, width=8,
                                 bg=self.col_bt_bg_green, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_green_highlight,
                                 activeforeground=self.col_bt_fg_default, command=lambda: self.save_shd())
            bt_save_shd.grid(row=0, column=5, sticky=NSEW, columnspan=1, padx=3 * self.default_padding,
                             pady=self.default_padding)

            bt_save_shd.bind('<Enter>', self.on_bt_enter_green)
            bt_save_shd.bind('<Leave>', self.on_bt_leave_green)
        else:
            lbl_mdl = Label(self.frame_shd, bd=1, text='! SHD package not found !', anchor=W, justify=LEFT,
                            bg=self.col_wdw_title, fg=self.col_bt_fg_default, padx=4, pady=4)
            lbl_mdl.grid(row=2, column=0, sticky=NSEW, columnspan=1, padx=3*self.default_padding,
                         pady=self.default_padding)
    # TODO change colour of change button if anything is not as it currently is set

    def ui_items_mdl(self):
        if self.mdl_items is not None:
            for item in self.mdl_items:
                item.destroy()

        # --- Label MDL -------------------------------------------------------------------------------
        # text = f'{self.parent.current_discipline.upper()}  //  {self.parent.current_asset}'
        lbl_mdl = Label(self.frame_mdl, bd=1, text='MDL Package', anchor=W, justify=LEFT,
                        bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_mdl.grid(row=0, column=0, sticky=W, columnspan=1, padx=3*self.default_padding, pady=self.default_padding)

        # --- DD MDL version --------------------------------------------------------------------------
        self.dir_pipe_mdl_versions = os.path.join(self.parent.dir_pipeline_mdl, 'versions')
        self.file_mdl_package = os.path.join(self.parent.dir_pipeline_mdl, 'mdl_package.json')

        # If model package exists
        if os.path.isfile(self.file_mdl_package):
            with open(self.file_mdl_package, 'r') as json_file:
                self.dict_mdl_package = json.load(json_file)
            self.mdl_version_current = self.dict_mdl_package[self.parent.current_discipline]

            self.dd_mdl_version = Menubutton(self.frame_mdl, text='', width=4,
                                             bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                             highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                             anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                             relief=self.def_bt_relief, justify=RIGHT)
            self.dd_mdl_version.menu = Menu(self.dd_mdl_version, tearoff=0, bd=0, activeborderwidth=3,
                                            relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                            activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                            activebackground=self.col_bt_bg_blue_highlight)
            self.dd_mdl_version['menu'] = self.dd_mdl_version.menu

            self.mdl_versions = sorted([x.split('.')[1] for x in os.listdir(self.dir_pipe_mdl_versions)])
            self.mdl_versions.reverse()

            for mdl_version in self.mdl_versions:
                self.dd_add_mdl_version(mdl_version)

            self.dd_mdl_version.grid(row=0, column=1, sticky=W, columnspan=1, padx=self.default_padding,
                                     pady=self.default_padding)

            # --- PULL BUTTON ------------------------------------------------------------------------------------
            state = DISABLED if self.parent.current_discipline == 'mdl' else NORMAL
            bt_pull_mdl = Button(self.frame_mdl, text='Pull', border=self.default_bt_bd, width=6, state=state,
                                 bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.pull_mdl())
            bt_pull_mdl.grid(row=0, column=2, sticky=NSEW, columnspan=1, padx=3*self.default_padding,
                             pady=self.default_padding)

            bt_pull_mdl.bind('<Enter>', self.on_bt_enter_grey)
            bt_pull_mdl.bind('<Leave>', self.on_bt_leave_grey)
            # --- MDL FRAME FOR PROCEDURAL -----------------------------------------------------------------------
            self.frame_mdl_variations = Frame(self.frame_mdl, bg=self.col_wdw_title)
            self.frame_mdl_variations.grid(row=1, column=0, sticky=NSEW, columnspan=6,
                                           padx=3 * self.default_padding, pady=2*self.default_padding)
            self.frame_mdl.columnconfigure(3, weight=1)

            # --- MDL PUBLISH CHECKBOX --------------------------------------------------------------------------
            mdl_state = NORMAL if self.parent.current_discipline == 'mdl' else DISABLED
            self.tkvar_publish_mdl = BooleanVar()
            self.tkvar_publish_mdl.set(False)
            cb_publish_mdl = Checkbutton(self.frame_mdl, text='push', var=self.tkvar_publish_mdl, state=mdl_state,
                                         bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                         fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                         selectcolor=self.col_bt_bg_active)
            cb_publish_mdl.grid(row=0, column=4, sticky=N, padx=self.default_padding, pady=self.default_padding)

            # --- MDL SAVE BUTTON -------------------------------------------------------------------------------
            bt_save_mdl = Button(self.frame_mdl, text='Save', border=self.default_bt_bd, width=8,
                                 bg=self.col_bt_bg_green, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_green_highlight,
                                 activeforeground=self.col_bt_fg_default, command=lambda: self.save_mdl())
            bt_save_mdl.grid(row=0, column=5, sticky=NSEW, columnspan=1, padx=3*self.default_padding,
                             pady=self.default_padding)
            bt_save_mdl.bind('<Enter>', self.on_bt_enter_green)
            bt_save_mdl.bind('<Leave>', self.on_bt_leave_green)

            # --- MDL CREATE PROCEDURAL LINES -------------------------------------------------------------------

            file_mdl_version = os.path.join(self.dir_pipe_mdl_versions,
                                            f'{self.parent.current_asset}.{self.mdl_version_current}.json')
            if os.path.isfile(file_mdl_version):
                with open(file_mdl_version, 'r') as json_file:
                    dict_mdl_version = json.load(json_file)
                self.ui_switch_mdl_version(self.mdl_version_current, dict_mdl_version)

                self.mdl_items = [lbl_mdl, self.dd_mdl_version, bt_pull_mdl,
                                  self.frame_mdl_variations, cb_publish_mdl, bt_save_mdl]
            else:
                lbl_mdl = Label(self.frame_main, bd=1, text='! No active MDL version for this stream !', anchor=W,
                                justify=LEFT,
                                bg=self.col_wdw_title, fg=self.col_bt_fg_default, padx=4, pady=4)
                lbl_mdl.grid(row=2, column=0, sticky=NSEW, columnspan=1, padx=3*self.default_padding, pady=self.default_padding)

        else:
            lbl_mdl = Label(self.frame_main, bd=1, text='! MDL package not found !', anchor=W, justify=LEFT,
                            bg=self.col_wdw_title, fg=self.col_bt_fg_default, padx=4, pady=4)
            lbl_mdl.grid(row=2, column=0, sticky=NSEW, columnspan=1, padx=3*self.default_padding, pady=self.default_padding)

    def switch_txt_variation(self, txt_variation):
        bg_frame = self.col_wdw_title
        self.txt_current_variation = txt_variation
        self.dd_txt_variation.configure(text=txt_variation)

        if len(self.dict_procedural_ui_elements_external) > 0:
            for category in self.dict_procedural_ui_elements_external:
                for elements in self.dict_procedural_ui_elements_external[category]:
                    for element in self.dict_procedural_ui_elements_external[category][elements]:
                        element.destroy()

        lbl_blank = Label(self.frame_txt_left, bd=1, text='   ', anchor=W, justify=LEFT,
                          bg=bg_frame, fg=self.col_bt_fg_default, width=18)
        lbl_blank.grid(row=0, column=0, sticky=NSEW, padx=3 * self.default_padding,
                       pady=self.default_padding)

        self.dir_pipe_txt_package = os.path.join(self.parent.dir_pipeline_txt, txt_variation, 'txt_package')
        channels_json, channels_json_native, channels_json_external = txt_package_list_channels(
            self.dir_pipe_txt_package)

        self.dict_native_version.clear()
        self.dict_txt_external_channels.clear()
        self.dict_procedural_ui_elements_external["nat"].clear()
        self.dict_procedural_ui_elements_external["ext"].clear()

        if channels_json_native is None:
            channels_json_native = ['']
        for i, channel_json_native in enumerate(channels_json_native):
            channel_native = channel_json_native.split('.')[0]
            # --- Native ---------------------------------------------------------------------------
            # --- Label ----------------------------------------------------------------------------
            lbl_channel_native = Label(self.frame_txt_left, bd=1, text=channel_native, anchor=W, justify=LEFT,
                                       bg=bg_frame, fg=self.col_bt_fg_default, width=18)
            lbl_channel_native.grid(row=i, column=0, sticky=NSEW, padx=3*self.default_padding,
                                    pady=self.default_padding)

            # --- Dropdown -------------------------------------------------------------------------
            dir_channel_native = os.path.join(self.dir_pipe_txt_package, channel_native)
            channel_native_versions = os.listdir(dir_channel_native)
            channel_native_versions.sort()

            full_path = os.path.join(self.dir_pipe_txt_package, channel_json_native)
            with open(full_path, 'r') as json_output_channel:
                dict_channel = json.load(json_output_channel)

            current_channel = dict_channel[self.parent.current_discipline]

            if self.parent.current_discipline == 'txt':
                latest = channel_native_versions[-1]
            else:
                full_path = os.path.join(self.dir_pipe_txt_package, f'{channel_native}.json')

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

            dd_txt_version = Menubutton(self.frame_txt_left, text=current_channel,
                                        bg=bg, fg=self.col_bt_fg_default,
                                        highlightthickness=0,
                                        activebackground=abg,
                                        anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                        relief=self.def_bt_relief, justify=RIGHT)
            dd_txt_version.menu = Menu(dd_txt_version, tearoff=0, bd=0, activeborderwidth=3,
                                       relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                       activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                       activebackground=self.col_bt_bg_blue_highlight)
            dd_txt_version['menu'] = dd_txt_version.menu

            # Add dropdown option per version
            for channel_native_version in channel_native_versions:
                version_number = channel_native_version.split('.')[1]

                # --- Metadata--------------------------------------------------------------------------
                full_path = os.path.join(self.dir_pipe_txt_package, channel_native,
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
                    dd_txt_version.menu.add_command(label=text,
                                                    command=lambda x=channel_native, y=version_number, z=dd_txt_version,
                                                    a=latest:
                                                    self.switch_txt_native_version(x, y, z, a))

            if dd_txt_version.menu.index("end") is None:
                CreateToolTip(dd_txt_version,
                              "No version has yet been published")

            dd_txt_version.grid(row=i, column=4, sticky=EW, padx=self.default_padding,
                                pady=self.default_padding)

            self.dict_native_version[channel_native] = {
                "version": current_channel,
                "latest": channel_native_versions[-1],
                "dd": dd_txt_version
            }

            self.dict_procedural_ui_elements_external["nat"][channel_native] = [lbl_channel_native, dd_txt_version]

        # EXTERNAL CHANNELS
        for i, channel_json_external in enumerate(channels_json_external):
            self.txt_add_external_channel(channel_json_external,
                                          channel_json_external.split('.')[0], self.col_bt_petrol,
                                          self.dir_pipe_txt_package)  # bg_frame

        self.ui_txt_menubutton_add_external()

    def ui_txt_menubutton_add_external(self):
        if self.dd_add_external is not None:
            self.dd_add_external.destroy()

        self.dd_add_external = Menubutton(self.frame_txt, image=self.icon_create, text=' +', width=26,
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

                # dir_asset_pipe = os.path.join(dir_build, asset, '.pipeline')

                variations = os.listdir(self.parent.dir_pipeline_txt.replace(self.parent.current_asset, asset))
                # dir_asset_pipe)

                for variation in variations:
                    if variation != self.txt_current_variation or asset != self.parent.current_asset:
                        asset_menu.add_command(label=variation,
                                               command=lambda x=self.parent.dir_pipeline_txt, y=variation,
                                               z=asset: self.ui_txt_channel_picker(x, y, z))

        self.dd_add_external.grid(row=1, column=4, sticky=E, columnspan=1, padx=2 * self.default_padding,
                                  pady=self.default_padding)

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

    def ui_txt_channel_picker(self, dir_asset_pipe, variation, asset):
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

        dir_txt_package = os.path.join(dir_asset_pipe, variation, 'txt_package').replace(self.parent.current_asset,
                                                                                         asset)

        channels_json, channels_json_native, _ = txt_package_list_channels(dir_txt_package)

        x, y = self.ui_child.winfo_rootx(), self.ui_child.winfo_rooty()
        # dimensions = f'311x{33 + 29 * len(channels_json) + 55}+{x + 710}+{y + 91}'
        dimensions = f'311x{33 + 29 * len(channels_json) + 55}+{x + 710}+{y + 0}'
        self.ui_picker.geometry(dimensions)

        lbl_title = Label(frame, bd=1, text=title, anchor=N, justify=LEFT,
                          bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_title.grid(row=0, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                       pady=self.default_padding)

        self.dict_txt_additions.clear()

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
            cb_channel.grid(row=i + 1, column=0, sticky=NSEW, columnspan=1, padx=self.default_padding,
                            pady=self.default_padding)

            if add_ttp:
                CreateToolTip(cb_channel,
                              f"{channel} is an external channel in the source package too. True source:\n"
                              f"{source_asset} - {source_variation} - {source_channel}")

            lbl_as = Label(frame, bd=1, text=' as ', anchor=N, justify=LEFT,
                           bg=self.col_wdw_default, fg=self.col_bt_fg_default)
            lbl_as.grid(row=i + 1, column=1, sticky=W, columnspan=1, padx=2 * self.default_padding,
                        pady=self.default_padding)

            tkvar_proxy = StringVar()
            tkvar_proxy.set(channel)
            i_proxy = Entry(frame, bd=1, textvariable=tkvar_proxy, width=18,
                            bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                            insertbackground=self.col_bt_fg_default)
            i_proxy.grid(row=i + 1, column=2, sticky=NSEW, columnspan=1, padx=self.default_padding,
                         pady=1)

            self.dict_txt_additions[channel] = {
                "proxy": tkvar_proxy,
                "usage": tkvar_channel_usage
            }

        bt_cancel = Button(frame, text='Cancel', width=12,
                           border=self.default_bt_bd,
                           bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                           activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                           command=lambda x=self.ui_picker: close_sub_ui(x))
        bt_cancel.grid(row=i + 3, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                       pady=0)

        bt_apply = Button(frame, text='Add',
                          border=self.default_bt_bd,
                          bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                          activebackground=self.col_bt_bg_blue_highlight, activeforeground=self.col_bt_fg_default,
                          command=lambda x=dir_txt_package: self.txt_apply_picker(x))
        bt_apply.grid(row=i + 2, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                      pady=2 * self.default_padding)

        for item in [frame, lbl_title]:
            item.bind('<Button-1>', self.move_picker_offset)
            item.bind('<B1-Motion>', self.move_picker)

        self.ui_picker.geometry('')

        self.ui_picker.attributes("-alpha", 1.0)
        self.ui_picker.mainloop()

    def txt_apply_picker(self, source_directory):
        natives = [key for key in self.dict_native_version]
        proxies = [self.dict_txt_external_channels[key]["proxy"].get() for key in self.dict_txt_external_channels]

        additions = [self.dict_txt_additions[key]["proxy"].get() for key in self.dict_txt_additions
                     if self.dict_txt_additions[key]["usage"].get()]
        overlap_1 = [x for x in additions if x in natives or x in proxies]

        content_additions = []
        for channel in self.dict_txt_additions:
            if self.dict_txt_additions[channel]["usage"].get():
                channel_json_external = f'{channel}.json'
                with open(os.path.join(source_directory, channel_json_external), 'r') as json_file:
                    json_file_content = json.load(json_file)
                if 'txt' in json_file_content.keys():
                    dir_parts = os.path.normpath(source_directory).split(os.sep)
                    channel_content = [dir_parts[-5], dir_parts[-2], channel_json_external.split('.')[0]]
                else:
                    channel_content = [json_file_content[x] for x in json_file_content]
                content_additions.append(channel_content)

        contents = [self.dict_txt_external_channels[key]["content"] for key in self.dict_txt_external_channels]
        overlap_2 = [x for x in content_additions if x in contents]

        if len(overlap_2) == 0:
            if len(overlap_1) == 0:
                for channel in self.dict_txt_additions:
                    if self.dict_txt_additions[channel]["usage"].get() is True:
                        self.txt_add_external_channel(f'{channel}.json',
                                                      self.dict_txt_additions[channel]["proxy"].get(), self.col_bt_red,
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

    def txt_add_external_channel(self, channel_json_external, proxy, color, source_directory):
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
        i = len(self.dict_txt_external_channels) + 0

        with open(os.path.join(source_directory, channel_json_external), 'r') as json_file:
            json_file_content = json.load(json_file)
        if 'txt' in json_file_content.keys():
            dir_parts = os.path.normpath(source_directory).split(os.sep)
            channel_content = [dir_parts[-5], dir_parts[-2], channel_json_external.split('.')[0]]
        else:
            channel_content = [json_file_content[x] for x in json_file_content]

        continue_adding = True
        if len(self.dict_txt_external_channels) > 0:
            contents = [self.dict_txt_external_channels[key]["content"] for key in self.dict_txt_external_channels]
            channels = [self.dict_txt_external_channels[key]["channel"] for key in self.dict_txt_external_channels]
            if channel_content in contents or proxy in channels:
                continue_adding = False

        natives = [key for key in self.dict_native_version]
        if proxy in natives:
            continue_adding = False

        if continue_adding:
            text = '  -  '.join(channel_content)

            # --- Label ----------------------------------------------------------------------------
            lbl_channel_external = Label(self.frame_txt_right, bd=1, text=text, anchor=W, justify=LEFT,
                                         bg=color, fg=self.col_bt_fg_default, width=38, relief='solid')
            lbl_channel_external.grid(row=i, column=0, sticky=NSEW, padx=self.default_padding,
                                      pady=self.default_padding)
            lbl_as = Label(self.frame_txt_right, bd=1, text=' as ', anchor=W, justify=LEFT,
                           bg=self.col_wdw_title, fg=self.col_bt_fg_default)
            lbl_as.grid(row=i, column=1, sticky=N, padx=self.default_padding,
                        pady=self.default_padding)
            CreateToolTip(lbl_channel_external,
                          "This channel will be linked to the active TXT package. \n\nPublish and pull "
                          "are controlled by the source asset.")
            # --- Proxy ----------------------------------------------------------------------------
            tkvar_proxy = StringVar()
            tkvar_proxy.set(proxy)
            i_proxy = Entry(self.frame_txt_right, bd=1, textvariable=tkvar_proxy, width=18,
                            bg='gray40', fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                            insertbackground=self.col_bt_fg_default)
            i_proxy.grid(row=i, column=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
            CreateToolTip(i_proxy, 'The channels proxy name inside this TXT package')

            # --- Delete Button  -------------------------------------------------------------------
            bt_delete = Button(self.frame_txt_right, image=self.icon_delete, text='-', width=24, height=21,
                               border=self.default_bt_bd,
                               bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                               activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                               command=lambda x=channel_external, y=i: self.txt_del_external_channel(x, y))
            bt_delete.grid(row=i, column=3, sticky=E, padx=self.default_padding, pady=self.default_padding)
            # ---------------------------------------------------------------------------------------------

            self.dict_procedural_ui_elements_external["ext"][channel_external] = [lbl_channel_external,
                                                                                  bt_delete, i_proxy, lbl_as]
            self.dict_txt_external_channels[i] = {
                "content": channel_content,
                "proxy": tkvar_proxy,
                "channel": channel_external
            }

    def txt_del_external_channel(self, channel_external, row):
        """ Deletes a row in the 'External Texture Layer' section.

                :param channel_external:
                :param row: Value of the row that needs to be deleted. Is used as a key of a dictionary.
                :return:
                """

        for element in self.dict_procedural_ui_elements_external["ext"][channel_external]:
            element.destroy()

        move_up = False
        for key in self.dict_txt_external_channels:
            if move_up:
                for element in \
                        self.dict_procedural_ui_elements_external["ext"][self.dict_txt_external_channels[key]["channel"]]:
                    cur_row = element.grid_info()["row"]
                    element.grid(row=cur_row - 1)
            if key == row:
                move_up = True

        del self.dict_procedural_ui_elements_external["ext"][channel_external]
        del self.dict_txt_external_channels[row]

    def switch_txt_native_version(self, key, version, dd, latest):
        self.dict_native_version[key]["version"] = version

        if version == latest.split('.')[1]:
            bg = self.col_bt_petrol
            abg = self.col_bt_petrol_highlight
        else:
            bg = self.col_bt_red
            abg = self.col_bt_red_highlight

        dd.config(text=version, bg=bg, activebackground=abg)

    def pull_txt(self):
        """ Updates all version dropdown to the latest published version in.

        :return:
        """

        for channel in self.dict_native_version:
            full_path = os.path.join(self.dir_pipe_txt_package, f'{channel}.json')

            with open(full_path, 'r') as json_file:
                dict_channel = json.load(json_file)
            published_version = dict_channel["txt_publish"]
            dd = self.dict_native_version[channel]["dd"]

            self.switch_txt_native_version(channel, published_version, dd, f'{channel}.{published_version}.json')
    # TODO if no packages are found

    def ui_txt_add_variation(self):
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


        letters = [x for x in string.ascii_uppercase if not x in os.listdir(self.parent.dir_pipeline_txt)]

        # --- Texture Variation -----------------------------------------------------------------------
        lbl_txt_var = Label(frame, bd=1, text='Texture Variation', anchor=N, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_txt_var.grid(row=1, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                         pady=self.default_padding)

        self.current_floating_txt_variation['txt'] = letters[0]
        dd_txt_variation = Menubutton(frame, text=self.current_floating_txt_variation['txt'], width=4,
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
                                              dd=dd_txt_variation: self.switch_txt_variation_add(l, dd, t))

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
                          command=lambda: self.add_new_txt_variation())
        bt_apply.grid(row=2, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                      pady=2 * self.default_padding)

        # ---------------------------------------------------------------------------------------------
        self.ui_variation_creator.attributes("-alpha", 1.0)
        for item in [frame, lbl_txt_var]:
            item.bind('<Button-1>', self.move_txt_variation_creator_offset)
            item.bind('<B1-Motion>', self.move_txt_variation_creator)

        self.ui_variation_creator.geometry('')

        self.ui_variation_creator.mainloop()

    def add_new_txt_variation(self):
        new_variation = f"{self.current_floating_txt_variation['txt']}"

        dir_pipe_variation = os.path.join(self.parent.dir_pipeline_txt, new_variation)
        dir_export_variation = os.path.join(self.parent.dir_asset, 'txt', '_export', new_variation)

        dir_pipe_txt_package = os.path.join(dir_pipe_variation, 'txt_package')
        print("AAAA", dir_pipe_variation, dir_export_variation)
        if os.path.isdir(dir_pipe_variation) or (os.path.isdir(dir_export_variation) and new_variation != 'A'):
            message = f'Variation {new_variation} already exists.'
            messagebox.showerror(title='Error', message=message)
        else:
            os.makedirs(dir_pipe_txt_package)
            try:
                os.makedirs(dir_export_variation)
            except FileExistsError:
                pass

            try:
                self.switch_txt_variation(new_variation)
                #close_sub_ui(self.ui_variation_creator)
                self.dd_txt_variation.menu.add_command(label=new_variation,
                                                       command=lambda x=new_variation: self.switch_txt_variation(x))
            except AttributeError:
                self.ui_items_txt_header()
            close_sub_ui(self.ui_variation_creator)

    def switch_txt_variation_add(self, letter, dd, t):
        self.current_floating_txt_variation[t] = letter
        dd.config(text=letter)

    def ui_items_txt_header(self):
        try:  # rerun after initialising empty txt package
            for x in [self.lbl_message, self.bt_create_txt_variation]:
                x.destroy()
        except AttributeError:
            pass

        txt_variations = [x for x in os.listdir(self.parent.dir_pipeline_txt) if
                          os.path.isdir(os.path.join(self.parent.dir_pipeline_txt, x))]
        if len(txt_variations) != 0:

            # --- Label TXT -------------------------------------------------------------------------------
            # text = f'{self.parent.current_discipline.upper()}  //  {self.parent.current_asset}'
            lbl_txt = Label(self.frame_txt, bd=1, text='TXT Package', anchor=W, justify=LEFT,
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
            lbl_txt.grid(row=0, column=0, sticky=W, columnspan=1, padx=2 * self.default_padding,
                         pady=self.default_padding)

            # --- DD TXT version --------------------------------------------------------------------------
            self.dd_txt_variation = Menubutton(self.frame_txt, text=txt_variations[0], width=4,
                                               bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                               highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight,
                                               anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                               relief=self.def_bt_relief, justify=RIGHT)
            self.dd_txt_variation.menu = Menu(self.dd_txt_variation, tearoff=0, bd=0, activeborderwidth=3,
                                              relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                              activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                              activebackground=self.col_bt_bg_blue_highlight)
            self.dd_txt_variation['menu'] = self.dd_txt_variation.menu

            self.dd_txt_variation.menu.add_command(label='+', command=lambda: self.ui_txt_add_variation())

            for txt_variation in txt_variations:
                self.dd_txt_variation.menu.add_command(label=txt_variation,
                                                       command=lambda x=txt_variation: self.switch_txt_variation(x))

            self.dd_txt_variation.grid(row=0, column=2, sticky=E, padx=2 * self.default_padding,
                                       pady=self.default_padding)

            # --- PULL BUTTON ------------------------------------------------------------------------------------
            state = DISABLED if self.parent.current_discipline == 'txt' else NORMAL
            bt_pull_txt = Button(self.frame_txt, text='Pull', border=self.default_bt_bd, width=4, state=state,
                                 bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.pull_txt())
            bt_pull_txt.grid(row=1, column=2, sticky=NSEW, columnspan=1, padx=2 * self.default_padding,
                             pady=self.default_padding)

            bt_pull_txt.bind('<Enter>', self.on_bt_enter_grey)
            bt_pull_txt.bind('<Leave>', self.on_bt_leave_grey)
            # --- Headers ---------------------------------------------------------------------------------
            # --- Label Native Channels -------------------------------------------------------------------
            width_boxes = 66
            lbl_native = Label(self.frame_txt, bd=1, text='Native Channels', anchor=W, justify=LEFT,
                               bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=20)
            lbl_native.grid(row=1, column=0, sticky=W, columnspan=2, padx=2*self.default_padding, pady=self.default_padding)
            # --- Label External Channels ------------------------------------------------------------------
            lbl_external = Label(self.frame_txt, bd=1, text='External Channels', anchor=W, justify=LEFT,
                                 bg=self.col_wdw_default, fg=self.col_bt_fg_default, width=width_boxes-7)
            lbl_external.grid(row=1, column=3, sticky=NSEW, columnspan=1, padx=2*self.default_padding,
                              pady=self.default_padding)

            # --- Checkbox publish ------------------------------------------------------------------------
            self.tkvar_publish_txt = BooleanVar()
            self.tkvar_publish_txt.set(False)
            txt_state = NORMAL if self.parent.current_discipline == 'txt' else DISABLED
            cb_publish_txt = Checkbutton(self.frame_txt, text='push', var=self.tkvar_publish_txt, anchor=E,
                                         bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                         state=txt_state,
                                         fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                         selectcolor=self.col_bt_bg_active)
            cb_publish_txt.grid(row=0, column=3, sticky=E, padx=2*self.default_padding, pady=self.default_padding)
            # ---------------------------------------------------------------------------------------------

            # --- Save Button -----------------------------------------------------------------------------
            bt_save_txt = Button(self.frame_txt, text='Save', border=self.default_bt_bd, width=8,
                                 bg=self.col_bt_bg_green, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_green_highlight, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.save_txt())
            bt_save_txt.grid(row=0, column=4, sticky=NSEW, columnspan=1, padx=self.default_padding,
                             pady=self.default_padding)
            bt_save_txt.bind('<Enter>', self.on_bt_enter_green)
            bt_save_txt.bind('<Leave>', self.on_bt_leave_green)

            # --- Frames ----------------------------------------------------------------------------------
            self.frame_txt_left = Frame(self.frame_txt, bg=self.col_wdw_title)
            self.frame_txt_left.grid(row=2, column=0, sticky=NSEW, columnspan=3, padx=self.default_padding,
                                     pady=2*self.default_padding)
            self.frame_txt_right = Frame(self.frame_txt, bg=self.col_wdw_title)
            self.frame_txt_right.grid(row=2, column=3, sticky=NSEW, columnspan=3, padx=self.default_padding,
                                      pady=2*self.default_padding)
            self.frame_txt_left.grid_columnconfigure(0, weight=1)
            self.frame_txt_right.grid_columnconfigure(0, weight=1)
            self.frame_txt.grid_columnconfigure(3, weight=1)

            # --- Blank Right ----------------------------------------------------------------------------
            lbl_blank = Label(self.frame_txt_right, bd=1, text='   ', anchor=W, justify=LEFT,
                              bg=self.col_wdw_title, fg=self.col_bt_fg_default, width=18)
            lbl_blank.grid(row=0, column=0, sticky=NSEW, padx=3 * self.default_padding,
                           pady=self.default_padding)

            self.switch_txt_variation(txt_variations[0])

        else:
            self.lbl_message = Label(self.frame_txt, bd=1, text='! TXT package not found !', anchor=W, justify=LEFT,
                                bg=self.col_wdw_title, fg=self.col_bt_fg_default, padx=4, pady=4)
            self.lbl_message.grid(row=4, column=0, sticky=NSEW, columnspan=1, padx=3*self.default_padding,
                             pady=self.default_padding)

            self.bt_create_txt_variation = Button(self.frame_txt, text='+', border=self.default_bt_bd, width=6,
                                 bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.ui_txt_add_variation())
            self.bt_create_txt_variation.grid(row=4, column=1, sticky=NSEW, columnspan=1, padx=3 * self.default_padding,
                             pady=self.default_padding)

    def save_txt(self):
        """ Saves all channels (native & external) of the currently selected variation,
                 according to the current settings.

                :return:
                """
        variation = self.txt_current_variation
        publish = self.tkvar_publish_txt.get()

        natives = [key for key in self.dict_native_version]
        proxies = [self.dict_txt_external_channels[key]["proxy"].get() for key in self.dict_txt_external_channels]
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
            channels_json = [x for x in os.listdir(self.dir_pipe_txt_package)
                             if os.path.isfile(os.path.join(self.dir_pipe_txt_package, x))]
            channels_json_native = [x for x in channels_json
                                    if os.path.isdir(os.path.join(self.dir_pipe_txt_package, x.split('.')[0]))]
            channels_json_external = [x for x in channels_json if x not in channels_json_native]

            # Update Native Channels
            for channel in self.dict_native_version:
                version = self.dict_native_version[channel]["version"]
                latest = self.dict_native_version[channel]["latest"]
                latest_version = latest.split('.')[1]

                dir_channel = os.path.join(self.dir_pipe_txt_package, channel)

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

                full_path = os.path.join(self.dir_pipe_txt_package, f'{channel}.json')

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
                full_path = os.path.join(self.dir_pipe_txt_package, channel)
                os.remove(full_path)

            # Create External Channels
            for key in self.dict_txt_external_channels:
                layer = self.dict_txt_external_channels[key]
                proxy = layer["proxy"].get()

                dict_external_layer = {
                    "asset": layer["content"][0],
                    "variation": layer["content"][1],
                    "channel": layer["content"][2]
                }
                full_path = os.path.join(self.dir_pipe_txt_package, f'{proxy}.json')
                with open(full_path, 'w') as json_output_channel:
                    json.dump(dict_external_layer, json_output_channel, indent=2)

            #self.ui_switch_variation(self.txt_current_variation)
            self.switch_txt_variation(self.txt_current_variation)
            self.txt_update_connections(os.path.join(self.parent.dir_pipeline_txt, variation))
            message = f'Saved TXT Package successfully.'
            messagebox.showinfo(title='', message=message)
            self.parent.check_for_outdated_packages()

    def txt_update_connections(self, dir_variation):
        config = r'.\config\config_release_tool_txt.json'
        with open(config, 'r') as json_file:
            config_file_content = json.load(json_file)
            connections_default = config_file_content["connections"]["channels"]
            subchannels_default = config_file_content["connections"]["subchannels"]

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
            dict_out = {
                "channels": dict_connections,
                "subchannels": subchannels_default
            }
            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_out, json_output_channel, indent=2)

        # file exists already
        else:
            with open(full_path, 'r') as json_output_channel:
                json_content = json.load(json_output_channel)
                dict_connections = json_content["channels"]
                if 'subchannels' in json_content.keys():
                    subchannels = json_content["subchannels"]
                else:
                    subchannels = subchannels_default

            for key in dict_connections:
                if dict_connections[key] == '':
                    if connections_default[key] in channels:
                        dict_connections[key] = connections_default[key]
            dict_out = {
                "channels": dict_connections,
                "subchannels": subchannels
            }
            with open(full_path, 'w') as json_output_channel:
                json.dump(dict_out, json_output_channel, indent=2)

    def create_ui_package_manager(self, parent):
        dimensions = '662x103+420+100'
        self.parent = parent

        self.ui_proxy = Tk()
        ui_package_manager_txt = Toplevel()
        ui_package_manager_txt.lift()
        ui_package_manager_txt.attributes("-alpha", 0.0)
        ui_package_manager_txt.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_package_manager_txt.title('Package Manager')
        ui_package_manager_txt.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, ui_package_manager_txt, 'Package Manager',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
        ui_package_manager_txt.configure(bg=self.col_wdw_default)

        self.icon_create = PhotoImage(file=r'.\ui\bt_create.png')
        self.icon_delete = PhotoImage(file=r'.\ui\bt_delete.png')

        self.frame_main = Frame(ui_package_manager_txt, bg=self.col_wdw_default)
        self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)

        # --- HEADER ----------------------------------------------------------------------------------
        text = f'{self.parent.current_asset}  //  {self.parent.current_discipline.upper()} Stream'
        lbl_header = Label(self.frame_main, bd=1, text=text, anchor=W, justify=LEFT,
                           bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_header.grid(row=0, column=0, sticky=W, columnspan=1, padx=3*self.default_padding,
                        pady=2*self.default_padding)

        frame_separator = Frame(self.frame_main, bg="gray60", height=1)
        frame_separator.grid(row=1, column=0, columnspan=1, sticky=NSEW, padx=3*self.default_padding, pady=6)
        # ---------------------------------------------------------------------------------------------

        # --- MDL PACKAGE -----------------------------------------------------------------------------
        self.frame_mdl = Frame(self.frame_main, bg=self.col_wdw_default)
        self.frame_mdl.grid(row=2, column=0, sticky=NSEW, columnspan=1, padx=0, pady=2)

        self.ui_items_mdl()

        # ---------------------------------------------------------------------------------------------
        frame_separator = Frame(self.frame_main, bg="gray60", height=1)
        frame_separator.grid(row=3, column=0, columnspan=1, sticky=NSEW, padx=3*self.default_padding, pady=6)

        # --- TXT PACKAGE -----------------------------------------------------------------------------
        self.frame_txt = Frame(self.frame_main, bg=self.col_wdw_default)
        self.frame_txt.grid(row=4, column=0, sticky=NSEW, columnspan=1, padx=2*self.default_padding, pady=2)

        self.ui_items_txt_header()

        # ---------------------------------------------------------------------------------------------
        frame_separator = Frame(self.frame_main, bg="gray60", height=1)
        frame_separator.grid(row=5, column=0, columnspan=1, sticky=NSEW, padx=3 * self.default_padding, pady=6)

        # --- SHD PACKAGE -----------------------------------------------------------------------------
        self.frame_shd = Frame(self.frame_main, bg=self.col_wdw_default)
        self.frame_shd.grid(row=6, column=0, sticky=NSEW, columnspan=1, padx=0, pady=2)

        #self.frame_shd.columnconfigure(0, weight=1)
        self.ui_items_shd()

        # ---------------------------------------------------------------------------------------------
        ui_package_manager_txt.geometry('')

        ui_package_manager_txt.attributes("-alpha", 1.0)
        ui_package_manager_txt.wm_attributes("-topmost", 1)
        ui_package_manager_txt.mainloop()
