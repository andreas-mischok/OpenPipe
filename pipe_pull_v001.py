# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pipe_utils import *


class Pull:
    def __init__(self):
        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = \
            self.col_bt_bg_blue_highlight = self.def_bt_relief = self.default_padding = self.default_bt_bd = \
            self.col_bt_bg_default = self.col_bt_bg_blue_active = self.ui_proxy = \
            self.ui_child = self.x_offset = self.y_offset = \
            self.col_ui_bt_small = self.col_ui_bt_small_highlight = self.col_ui_dd_default = \
            self.col_wdw_border = self.col_wdw_border_background = self.col_wdw_title = self.col_bt_petrol = \
            self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight = self.col_bt_red = \
            self.col_bt_red_highlight = self.file_mdl = self.dict_mdl = self.mdl_version_pub = None

        self.current_root = self.current_project_name = self.user = self.current_asset = self.frame_main = \
            self.current_discipline = self.current_department = self.parent = self.list_updates_pull = None

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

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

    def ui_draw_labels(self):
        # ---- PULL ----------------------------------------------------------------------------
        text_pull = ''
        self.list_updates_pull = pull_required(self.parent)
        # ---- MDL -----------------------------------------------------------------------------
        if self.list_updates_pull["mdl"] is not None:
            self.file_mdl = self.list_updates_pull["mdl"]["file"]
            self.dict_mdl = self.list_updates_pull["mdl"]["dict"]
            version_cur = self.list_updates_pull["mdl"]["version_cur"]
            self.mdl_version_pub = self.list_updates_pull["mdl"]["version_pub"]
            text_pull = text_pull + 'MDL \n' \
                                    f'  - {version_cur}    ▶    {self.mdl_version_pub}'

        # ---- ANM -----------------------------------------------------------------------------
        anm_updates = []
        if len(self.list_updates_pull["anm"]) > 0:
            for file_anm in self.list_updates_pull["anm"]:
                with open(file_anm, 'r') as json_file:
                    dict_channel_content = json.load(json_file)
                anm_name = os.path.splitext(os.path.normpath(file_anm).split(os.sep)[-1])[0]
                print(anm_name)

                from_to = f'\n  - {anm_name}      ' \
                          f'{dict_channel_content[self.parent.current_discipline]}  ▶  ' \
                          f'{dict_channel_content["anm_publish"]}'

                anm_updates.append(from_to)
        updates_text = ''.join(anm_updates)

        if len(updates_text) > 0:
            if len(text_pull) != 0:
                text_pull = text_pull + '\n\n'
            text_pull = text_pull + 'ANM' + updates_text

        # ---- TXT -----------------------------------------------------------------------------
        # Detect channels that need to be updated
        txt_updates = []
        if len(self.list_updates_pull["txt"]) > 0:
            for channel_file in self.list_updates_pull["txt"]:
                with open(channel_file, 'r') as json_file:
                    dict_channel_content = json.load(json_file)

                # channel = os.path.splitext(channel_file.split("/")[-1])[0]
                channel = os.path.splitext(os.path.normpath(channel_file).split(os.sep)[-1])[0]
                variation = os.path.normpath(channel_file).split(os.sep)[-3]

                from_to = f'\n  - {channel}  ' \
                          f'({variation})        ' \
                          f'{dict_channel_content[self.parent.current_discipline]}  ▶  ' \
                          f'{dict_channel_content["txt_publish"]}'

                txt_updates.append(from_to)
        updates_text = ''.join(txt_updates)

        if len(updates_text) > 0:
            if len(text_pull) != 0:
                text_pull = text_pull + '\n\n'
            text_pull = text_pull + 'TXT' + updates_text

        # ---- SHD -----------------------------------------------------------------------------
        shd_updates = []
        if len(self.list_updates_pull["shd"]) > 0:
            for variation_file in self.list_updates_pull["shd"]:
                with open(variation_file, 'r') as json_file:
                    dict_variation_content = json.load(json_file)

                shd = dict_variation_content["shd"]
                shd_publish = dict_variation_content["shd_publish"]
                variation = os.path.normpath(variation_file).split(os.sep)[-2]

                from_to = f'\n  - TXT / SHD variation  ' \
                          f'{variation}        ' \
                          f'{dict_variation_content[self.parent.current_discipline]}  ▶  ' \
                          f'{shd_publish}'
                shd_updates.append(from_to)
        updates_text = ''.join(shd_updates)
        if len(updates_text) > 0:
            if len(text_pull) != 0:
                text_pull = text_pull + '\n\n'
            text_pull = text_pull + 'SHD' + updates_text

        # ---- LABEL --------------------------------------------------------------------------
        lbl_update_pull = Label(self.frame_main, bd=1, text=text_pull, anchor=W, justify=LEFT, padx=4, pady=4,
                                bg=self.col_wdw_title, fg=self.col_bt_fg_default, relief='solid')
        lbl_update_pull.grid(row=0, column=0, sticky=NSEW, padx=self.default_padding,
                             pady=self.default_padding)
        # ---- BUTTON --------------------------------------------------------------------------
        text = 'Confirm' if len(text_pull) != 0 else 'Close'
        bt_pull = Button(self.frame_main, text=text, height=2, bg=self.col_bt_bg_blue,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief, width=33,
                         command=lambda: self.execute_pull())
        bt_pull.grid(row=1, column=0, columnspan=1, sticky=NSEW, padx=self.default_padding,
                     pady=self.default_padding)

    def execute_pull(self):
        update_required = False

        # anm update:
        if len(self.list_updates_pull["anm"]) > 0:
            update_required = True
            for file_anm in self.list_updates_pull["anm"]:
                with open(file_anm, 'r') as json_file:
                    dict_anm_content = json.load(json_file)

                dict_anm_content[self.parent.current_discipline] = dict_anm_content["anm_publish"]

                with open(file_anm, 'w') as json_file:
                    json.dump(dict_anm_content, json_file, indent=2)

        # txt update:
        if len(self.list_updates_pull["txt"]) > 0:
            update_required = True
            for channel_file in self.list_updates_pull["txt"]:
                with open(channel_file, 'r') as json_file:
                    dict_channel_content = json.load(json_file)

                dict_channel_content[self.parent.current_discipline] = dict_channel_content["txt_publish"]

                with open(channel_file, 'w') as json_file:
                    json.dump(dict_channel_content, json_file, indent=2)

        # mdl update
        if self.list_updates_pull["mdl"] is not None:
            update_required = True
            self.dict_mdl[self.parent.current_discipline] = self.mdl_version_pub

            with open(self.file_mdl, 'w') as json_file:
                json.dump(self.dict_mdl, json_file, indent=2)

        # shd update
        if len(self.list_updates_pull["shd"]) > 0:
            update_required = True
            for variation_file in self.list_updates_pull["shd"]:
                with open(variation_file, 'r') as json_file:
                    dict_variation_content = json.load(json_file)

                dict_variation_content[self.parent.current_discipline] = dict_variation_content["shd_publish"]

                with open(variation_file, 'w') as json_file:
                    json.dump(dict_variation_content, json_file, indent=2)

        # message
        if update_required:
            messagebox.showinfo(title='Info', message=f'Pull complete.')
            self.parent.check_for_outdated_packages()

        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def create_ui_pull(self, parent):
        self.parent = parent

        dimensions = '662x103+420+100'

        self.ui_proxy = Tk()
        ui_pull_publish = Toplevel()
        ui_pull_publish.lift()
        ui_pull_publish.attributes("-alpha", 0.0)
        ui_pull_publish.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_pull_publish.title('Pull & Publish')
        ui_pull_publish.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, ui_pull_publish, 'Pull',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
        ui_pull_publish.configure(bg=self.col_wdw_default)

        self.frame_main = Frame(ui_pull_publish, bg=self.col_wdw_default)
        self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.ui_draw_labels()
        # ---------------------------------------------------------------------------------------------
        ui_pull_publish.geometry('')

        ui_pull_publish.attributes("-alpha", 1.0)
        ui_pull_publish.wm_attributes("-topmost", 1)
        ui_pull_publish.mainloop()
