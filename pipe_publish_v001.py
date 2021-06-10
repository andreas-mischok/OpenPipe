# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pipe_utils import *


class Publish:
    def __init__(self):
        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = \
            self.col_bt_bg_blue_highlight = self.def_bt_relief = self.default_padding = self.default_bt_bd = \
            self.col_bt_bg_default = self.col_bt_bg_blue_active = self.ui_proxy = \
            self.ui_child = self.x_offset = self.y_offset = \
            self.col_ui_bt_small = self.col_ui_bt_small_highlight = self.col_ui_dd_default = \
            self.col_wdw_border = self.col_wdw_border_background = self.col_wdw_title = self.col_bt_petrol = \
            self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight = self.col_bt_red = \
            self.col_bt_red_highlight = None

        self.current_root = self.current_project_name = self.user = self.current_asset = \
            self.current_discipline = self.current_department = self.parent = self.list_updates_pull = \
            self.frame_main = self.dir_asset = self.bt_publish = self.lbl_update_publish = None

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

    def on_root_deiconify(self, _):
        """ Iconifies the proxy window and deiconifies the child window.
        This is to bind the visible UI (child) to the taskbar without using the default title bar

        :return:
        """
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def ui_draw_labels_mdl(self):
        """ Modifies label to show the changes to be made and updates the publish button to use the correct command.
        Belongs to modeling discipline.

        :return:
        """
        dir_pipe_mdl = os.path.join(self.dir_asset, '.pipeline', 'mdl')
        file_mdl_package = os.path.join(dir_pipe_mdl, 'mdl_package.json')

        with open(file_mdl_package, 'r') as json_file:
            dict_json_content = json.load(json_file)

        mdl = dict_json_content["mdl"]
        mdl_publish = dict_json_content["mdl_publish"]

        # if there is no version
        if len(mdl) == 0:
            text_publish = 'No current model has been found.'
        # if any version exists
        else:
            # Current model is already published
            if mdl == mdl_publish:
                text_publish = f'MDL\n\n{mdl} is already published.'
            # If model needs to be published
            else:
                text_publish = f'MDL\n{mdl_publish}    ▶    {mdl}'
                self.bt_publish.configure(state=NORMAL, command=lambda x=file_mdl_package, y=dict_json_content,
                                          z=mdl, v=dir_pipe_mdl: self.execute_publish_mdl(x, y, z, v))

        self.lbl_update_publish.configure(text=text_publish)

    def execute_publish_mdl(self, file, json_file_content, mdl, dir_pipe_mdl):
        """ Command executed when publishing a model update

        :param file: Path to the json file storing the publish information.
        :param json_file_content: Dictionary of the pre-existing content of the json file
        :param mdl: Current version active in the modelling stream ('v001' format)
        :return:
        """

        # Save model package file
        json_file_content["mdl_publish"] = mdl
        with open(file, 'w') as json_file:
            json.dump(json_file_content, json_file, indent=2)

        # Update model version file
        file_mdl_version = os.path.join(dir_pipe_mdl, 'versions', f'{self.parent.current_asset}.{mdl}.json')

        with open(file_mdl_version, 'r') as json_file:
            dict_channel_version_content = json.load(json_file)

        dict_channel_version_content["published"] = True

        with open(file_mdl_version, 'w') as json_file:
            json.dump(dict_channel_version_content, json_file, indent=2)

        self.parent.check_for_outdated_packages()

        messagebox.showinfo(title='Info', message=f'{self.parent.current_asset} model {mdl} has been published')

        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def ui_draw_labels_txt(self):
        """ Modifies label to show the changes to be made and updates the publish button to use the correct command.
        Belongs to texturing discipline.

        :return:
        """

        list_updates = publish_required_txt(self.parent)
        if len(list_updates) == 0:
            pass
            text_publish = f'TXT\nNo updates to publish.'
            # no update to be found
        else:
            updates = []
            variables = []
            for channel_file in list_updates:
                with open(channel_file, 'r') as json_file:
                    dict_channel_content = json.load(json_file)
                txt = dict_channel_content["txt"]
                txt_publish = dict_channel_content["txt_publish"]

                channel = os.path.splitext(os.path.normpath(channel_file).split(os.sep)[-1])[0]
                variation = os.path.normpath(channel_file).split(os.sep)[-3]
                from_to = f'\n  - {channel}  ' \
                          f'({variation})        ' \
                          f'{txt_publish}  ▶  ' \
                          f'{txt}'

                updates.append(from_to)
                variables.append([channel_file, dict_channel_content, txt])
            updates_text = ''.join(updates)
            text_publish = 'TXT\n' + updates_text

            self.bt_publish.configure(text='Confirm', state=NORMAL, command=lambda: self.execute_publish_txt(variables))

        self.lbl_update_publish.configure(text=text_publish)

    def execute_publish_txt(self, list_variables):
        """ Command executed when publishing a texture update

        :param list_variables: list that includes variables per variation [file, dict_channel_content, txt]:
        file = path to the channel.json file
        dict_channel_content = content of said file
        txt = current version used by txt stream 'v001' format
        :return:
        """
        messages_partial = []
        for variables in list_variables:
            file, dict_channel_content, txt = variables
            channel = os.path.splitext(os.path.normpath(file).split(os.sep)[-1])[0]
            variation = os.path.normpath(file).split(os.sep)[-3]

            # Update texture package file
            dict_channel_content["txt_publish"] = txt
            with open(file, 'w') as json_file:
                json.dump(dict_channel_content, json_file, indent=2)

            # Update channel version file (for publishing status in the package manager)
            file_channel_version = os.path.join(self.parent.dir_pipeline_txt, variation, 'txt_package',
                                                channel, f'{channel}.{txt}.json')
            with open(file_channel_version, 'r') as json_file:
                dict_channel_version_content = json.load(json_file)

            dict_channel_version_content["published"] = True

            with open(file_channel_version, 'w') as json_file:
                json.dump(dict_channel_version_content, json_file, indent=2)

            # Add message output
            messages_partial. append(f'-  {channel} ({variation})')

        messages = '\n'.join(messages_partial)

        self.parent.check_for_outdated_packages()
        messagebox.showinfo(title='Info', message=f'The following texture updates have been published:\n{messages}')

        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def ui_draw_labels_shd(self):
        """ Modifies label to show the changes to be made and updates the publish button to use the correct command.
        Belongs to shading discipline.

        :return:
        """

        list_updates = publish_required_shd(self.parent)
        if len(list_updates) == 0:
            pass
            text_publish = f'SHD\nNo updates to publish.'
            # no update to be found
        else:
            updates = []
            variables = []
            for channel_file in list_updates:
                with open(channel_file, 'r') as json_file:
                    dict_channel_content = json.load(json_file)
                shd = dict_channel_content["shd"]
                shd_publish = dict_channel_content["shd_publish"]

                variation = os.path.normpath(channel_file).split(os.sep)[-2]
                from_to = f'\n  - TXT / SHD variation  ' \
                          f'{variation}        ' \
                          f'{shd_publish}  ▶  ' \
                          f'{shd}'

                updates.append(from_to)
                variables.append([channel_file, dict_channel_content, shd])
            updates_text = ''.join(updates)
            text_publish = 'SHD\n' + updates_text

            self.bt_publish.configure(text='Confirm', state=NORMAL, command=lambda: self.execute_publish_shd(variables))

        self.lbl_update_publish.configure(text=text_publish)

    def execute_publish_shd(self, list_variables):
        """ Command executed when publishing a texture update

        :param list_variables: list that includes variables per variation [file, dict_channel_content, shd]:
        file = path to the channel.json file
        dict_channel_content = content of said file
        shd = current version used by shd stream 'v001' format
        :return:
        """

        messages_partial = []
        for variables in list_variables:
            file, dict_channel_content, shd = variables
            channel = os.path.splitext(os.path.normpath(file).split(os.sep)[-1])[0]
            variation = os.path.normpath(file).split(os.sep)[-2]

            # Update texture package file
            dict_channel_content["shd_publish"] = shd
            with open(file, 'w') as json_file:
                json.dump(dict_channel_content, json_file, indent=2)

            # Update channel version file (for publishing status in the package manager)
            file_channel_version = os.path.join(self.parent.dir_pipeline_shd, variation, 'versions',
                                                f'{self.parent.current_asset}.{shd}.json')
            with open(file_channel_version, 'r') as json_file:
                dict_channel_version_content = json.load(json_file)

            dict_channel_version_content["published"] = True

            with open(file_channel_version, 'w') as json_file:
                json.dump(dict_channel_version_content, json_file, indent=2)

            # Add message output
            messages_partial.append(f'-  TXT / SHD variation {variation}')

        messages = '\n'.join(messages_partial)

        self.parent.check_for_outdated_packages()
        messagebox.showinfo(title='Info', message=f'The following shading updates have been published:\n{messages}')

        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def close(self):
        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def create_ui_publish(self, parent):
        """ Sets up the UI of this script. This is the function executed by the main parent class.

        :param parent: 'self' passed down from the class that calls this UI.
        Used to read variables such as the currently used asset.
        :return:
        """
        self.parent = parent
        self.dir_asset = os.path.join(self.parent.current_root, self.parent.current_project_name, 'build',
                                      self.parent.current_asset)

        dimensions = '662x103+420+100'

        self.ui_proxy = Tk()
        ui_pull_publish = Toplevel()
        ui_pull_publish.lift()
        ui_pull_publish.attributes("-alpha", 0.0)
        ui_pull_publish.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_pull_publish.title('Pull & Publish')
        ui_pull_publish.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, ui_pull_publish, 'Publish',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
        ui_pull_publish.configure(bg=self.col_wdw_default)

        self.frame_main = Frame(ui_pull_publish, bg=self.col_wdw_default)
        self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.lbl_update_publish = Label(self.frame_main, bd=1, text='', anchor=W, justify=LEFT, padx=4, pady=4,
                                        bg=self.col_wdw_title, fg=self.col_bt_fg_default, width=33, relief='solid')
        self.lbl_update_publish.grid(row=0, column=0, sticky=NSEW, padx=self.default_padding,
                                     pady=self.default_padding)

        self.bt_publish = Button(self.frame_main, text='Close', height=2, bg=self.col_bt_bg_blue, #state=DISABLED,
                                 fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                                 activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                 bd=self.default_bt_bd, relief=self.def_bt_relief, command=lambda: self.close())
        self.bt_publish.grid(row=1, column=0, columnspan=1, sticky=NSEW, padx=self.default_padding,
                             pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        if parent.current_discipline == 'mdl':
            self.ui_draw_labels_mdl()
        if parent.current_discipline == 'txt':
            self.ui_draw_labels_txt()
        if parent.current_discipline == 'shd':
            self.ui_draw_labels_shd()

        # ---------------------------------------------------------------------------------------------
        ui_pull_publish.geometry('')

        ui_pull_publish.attributes("-alpha", 1.0)
        ui_pull_publish.wm_attributes("-topmost", 1)
        ui_pull_publish.mainloop()
