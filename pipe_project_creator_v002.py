# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pipe_utils import *


class ProjectCreator:
    def __init__(self):
        self.project_name = self.project_abbreviation = self.i_project_ocio = self.col_bt_bg_default = \
            self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_active = self.col_bt_bg_green = \
            self.col_i_bg_default = self.default_bt_bd = self.default_padding = self.def_bt_relief = \
            self.tkvar_ocio = self.tkvar_project_abbreviation = self.tkvar_project_name = \
            self.frame_software_header = self.project_creator_ui = self.tkvar_root =  \
            self.col_bt_bg_blue = self.col_bt_bg_blue_active = self.col_bt_bg_blue_highlight = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.col_wdw_title = \
            self.col_wdw_border = self.col_wdw_border_background = self.col_dd_blue_default = None

        self.row_height = 29
        self.software_list_ui = []
        self.software_list_variables = []
        # self.version = os.path.basename(__file__).split('_')[-1][:-3]
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        # self.create_ui(None)

    def software_add(self):
        index = len(self.software_list_ui)
        row = 2 + index

        tkvar_label = StringVar()
        i_label = Entry(self.frame_software_header, bd=1, width=22, textvariable=tkvar_label,
                        bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                        insertbackground=self.col_bt_fg_default)

        tkvar_path = StringVar()
        i_path = Entry(self.frame_software_header, bd=1, textvariable=tkvar_path, width=14,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        bt_path_pick = Button(self.frame_software_header, text='pick', bg=self.col_bt_bg_default,
                              fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                              activeforeground=self.col_bt_fg_default, highlightthickness=0,
                              bd=self.default_bt_bd, relief=self.def_bt_relief,
                              command=lambda x=tkvar_path: pick_exe(x))

        tkvar_ocio_alternative = StringVar()
        i_ocio_alternative = Entry(self.frame_software_header, bd=1, textvariable=tkvar_ocio_alternative, width=14,
                                   bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                   insertbackground=self.col_bt_fg_default, disabledbackground='gray25')
        bt_ocio_pick = Button(self.frame_software_header, text='pick', bg=self.col_bt_bg_default,
                              fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                              activeforeground=self.col_bt_fg_default, highlightthickness=0,
                              bd=self.default_bt_bd, relief=self.def_bt_relief,
                              command=lambda x=tkvar_ocio_alternative: pick_ocio(x))

        tkvar_ocio_support = BooleanVar()
        tkvar_ocio_support.set(True)
        cb_support = Checkbutton(self.frame_software_header, text='', var=tkvar_ocio_support,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active,
                                 command=lambda x=[tkvar_ocio_support, i_ocio_alternative, bt_ocio_pick]:
                                 custom_ocio_state(x))

        bt_delete = Button(self.frame_software_header, text='-', bg=self.col_bt_bg_default,
                           fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                           activeforeground=self.col_bt_fg_default, highlightthickness=0,
                           bd=self.default_bt_bd, relief=self.def_bt_relief,
                           command=lambda x=index: self.software_remove(x))

        i_label.grid(row=row, column=0, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        i_path.grid(row=row, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        bt_path_pick.grid(row=row, column=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        cb_support.grid(row=row, column=3, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        i_ocio_alternative.grid(row=row, column=4, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        bt_ocio_pick.grid(row=row, column=5, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        bt_delete.grid(row=row, column=6, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)

        self.software_list_ui.append([i_label, i_path, bt_path_pick, cb_support, i_ocio_alternative, bt_ocio_pick,
                                      bt_delete])
        self.software_list_variables.append([[tkvar_label],
                                             [tkvar_path],
                                             [tkvar_ocio_support],
                                             [tkvar_ocio_alternative]])

    def software_remove(self, index):
        for ui_element in self.software_list_ui[index]:
            ui_element.destroy()

        del self.software_list_ui[index]
        del self.software_list_variables[index]

        for i, ui_elements in enumerate(self.software_list_ui):
            ui_elements[6].configure(command=lambda x=i: self.software_remove(x))
            # self.software_list_variables[i][0][0].set(str(i))  # sets index to label
            for ui_element in ui_elements:
                ui_element.grid(row=i+2)

    def load_show(self, config):
        with open(config, 'r') as config_file:
            config_file_content = json.load(config_file)
            name = config_file_content["name"]
            abbr = config_file_content["abbreviation"]
            ocio = config_file_content["ocio"]
            root = config_file_content["root"]

            self.tkvar_project_name.set(name)
            self.tkvar_project_abbreviation.set(abbr)
            self.project_name.configure(state=DISABLED)
            self.project_abbreviation.configure(state=DISABLED)
            self.tkvar_ocio.set(ocio)
            self.tkvar_root.set(root)

            software = config_file_content["software"]

            for x in range(len(software)-1):
                self.software_add()
            for i, program in enumerate(software):
                self.software_list_variables[i][0][0].set(program)
                self.software_list_variables[i][1][0].set(software[program]["exe"])
                supports_ocio = software[program]["support"]
                self.software_list_variables[i][2][0].set(supports_ocio)
                if supports_ocio is False:
                    self.software_list_ui[i][4].configure(state=DISABLED)
                    self.software_list_ui[i][5].configure(state=DISABLED)
                self.software_list_variables[i][3][0].set(software[program]["alternative_ocio"])

    def save_show(self):
        name = self.tkvar_project_name.get()
        abbr = self.tkvar_project_abbreviation.get()
        ocio = self.tkvar_ocio.get()
        root = self.tkvar_root.get()
        if len(root) > 0 and os.path.isdir(root):
            if len(name) > 0:
                if len(abbr) > 0:
                    dict_software = {}
                    for i, software_row in enumerate(self.software_list_variables):
                        label = software_row[0][0].get()
                        exe = software_row[1][0].get()
                        support = software_row[2][0].get()
                        alternative_ocio = software_row[3][0].get()
                        if len(label) > 0 and len(exe) > 0:
                            dict_software_info = {
                                "exe": exe,
                                "support": support,
                                "alternative_ocio": alternative_ocio
                            }
                            dict_software[label] = dict_software_info

                    if len(dict_software) > 0:
                        dict_project = {
                            "name": name,
                            "abbreviation": abbr,
                            "ocio": ocio,
                            "root": root,
                            "software": dict_software
                        }
                        name_abbr = f'{name}-{abbr}'
                        path_json_output = f'.\\projects\\{name_abbr}\\'
                        path_full_json_output = f'.\\projects\\{name_abbr}\\{name_abbr}.json'

                        existing_projects = [x for x in os.listdir(r'.\projects\\') if
                                             os.path.isdir(f'.\\projects\\{x}')]

                        if len(existing_projects) > 0:
                            existing_names = []
                            existing_abbreviations = []
                            for project in existing_projects:
                                existing_name, existing_abbr = project.split('.')[0].split('-')
                                existing_names.append(existing_name)
                                existing_abbreviations.append(existing_abbr)

                            if name in existing_names or abbr in existing_abbreviations:
                                if name in existing_names and abbr in existing_abbreviations:
                                    msg = messagebox.askquestion('Replace?',
                                                                 'Do you want to replace the existing config?')
                                    if msg == 'yes':
                                        create_folder_structure(name, root)
                                        self.write_file(path_json_output, path_full_json_output, dict_project)
                                else:
                                    message = "Project with same name OR abbreviation exists. Can't create project"
                                    messagebox.showerror(title='Error', message=message)
                            # If a new name is used
                            else:
                                create_folder_structure(name, root)
                                self.write_file(path_json_output, path_full_json_output, dict_project)
                        # If it is the first project that is being created
                        else:
                            create_folder_structure(name, root)
                            self.write_file(path_json_output, path_full_json_output, dict_project)
                    else:
                        message = 'No valid software input was given.'
                        messagebox.showerror(title='Error', message=message)
                else:
                    message = 'No valid project abbreviation was given.'
                    messagebox.showerror(title='Error', message=message)
            else:
                message = 'No valid project name was given.'
                messagebox.showerror(title='Error', message=message)
        else:
            message = 'No valid root directory was given.'
            messagebox.showerror(title='Error', message=message)

    def write_file(self, path_json_output, path_full_json_output, dict_project):
        if os.path.isdir(path_json_output) is False:
            os.makedirs(path_json_output)
        with open(path_full_json_output, 'w') as json_output:
            json.dump(dict_project, json_output, indent=2)

        close_sub_ui(self.project_creator_ui)
        close_sub_ui(self.ui_proxy)

        messagebox.showinfo(title='', message='Project configuration saved successfully.')

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

    def create_ui(self, config):
        # dimensions = '571x348+420+100'
        # dimensions = '571x148+420+100'
        # dimensions = '571x123+420+100'  # 29 px per line
        dimensions = '571x152+420+100'

        self.ui_proxy = Toplevel()
        self.project_creator_ui = Toplevel()
        self.project_creator_ui.lift()
        self.project_creator_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        title = 'Project Editor' if config is not None else 'Project Creator'
        self.project_creator_ui.title(title)
        self.project_creator_ui.attributes("-alpha", 0.0)
        self.project_creator_ui.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, self.project_creator_ui, title, r'.\ui\icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)
        self.project_creator_ui.resizable(width=False, height=True)
        self.project_creator_ui.configure(bg=self.col_wdw_default)

        # FRAMES
        frame_top = Frame(self.project_creator_ui, bg=self.col_wdw_default)
        frame_software = Frame(self.project_creator_ui, bg=self.col_wdw_default)
        self.frame_software_header = Frame(frame_software, bg=self.col_wdw_default)
        frame_software_list = Frame(frame_software, bg=self.col_wdw_default)

        frame_top.pack(fill=X, padx=self.default_padding, pady=2*self.default_padding)
        frame_software.pack(fill=X, padx=self.default_padding, pady=0)
        self.frame_software_header.pack(fill=X, padx=0, pady=0)
        frame_software_list.pack(fill=X, padx=0, pady=0)

        # UI ELEMENTS
        # ------- First Row ------------------------------------------------------------------------------
        # --- Name
        lbl_name = Label(frame_top, bd=1, text='Name ', anchor=W, width=5,
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        self.tkvar_project_name = StringVar()
        self.tkvar_project_name.set('')
        self.project_name = Entry(frame_top, bd=1, width=51, textvariable=self.tkvar_project_name,
                                  bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                  insertbackground=self.col_bt_fg_default, disabledbackground='gray25')
        # Placement
        lbl_name.grid(row=0, column=0, sticky=N, padx=self.default_padding, pady=self.default_padding)
        self.project_name.grid(row=0, column=1, sticky=NSEW, padx=self.default_padding, pady=3)

        # --- Abbreviation
        lbl_abbreviation = Label(frame_top, bd=1, text='abbr. ', anchor=W,
                                 bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        self.tkvar_project_abbreviation = StringVar()
        self.tkvar_project_abbreviation.set('')
        self.project_abbreviation = Entry(frame_top, bd=1, width=4, textvariable=self.tkvar_project_abbreviation,
                                          bg=self.col_i_bg_default, fg=self.col_bt_fg_default,
                                          relief=self.def_bt_relief, insertbackground=self.col_bt_fg_default,
                                          disabledbackground='gray25')
        # Placement
        lbl_abbreviation.grid(row=0, column=2, sticky=N, padx=self.default_padding, pady=self.default_padding)
        self.project_abbreviation.grid(row=0, column=3, sticky=NSEW, padx=self.default_padding, pady=3)

        # ------- Second Row ------------------------------------------------------------------------------
        # --- OCIO
        lbl_ocio = Label(frame_top, bd=1, text='OCIO ', anchor=W, width=5,
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)

        self.tkvar_ocio = StringVar()
        self.tkvar_ocio.set('')
        self.i_project_ocio = Entry(frame_top, bd=1, width=73, textvariable=self.tkvar_ocio,
                                    bg=self.col_i_bg_default, fg=self.col_bt_fg_default,
                                    relief=self.def_bt_relief, insertbackground=self.col_bt_fg_default)
        bt_ocio = Button(frame_top, text='pick', width=4, bg=self.col_bt_bg_default,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief,
                         command=lambda x=self.tkvar_ocio: pick_ocio(x))
        bt_save = Button(frame_top, text='save', width=4, bg=self.col_bt_bg_green,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief,
                         command=lambda: self.save_show())
        # Placement
        lbl_ocio.grid(row=2, column=0, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        self.i_project_ocio.grid(row=2, column=1, columnspan=1, sticky=NSEW, padx=self.default_padding,
                                 pady=self.default_padding)
        bt_ocio.grid(row=2, column=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        bt_save.grid(row=1, column=3, rowspan=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)

        # ------- Third Row ------------------------------------------------------------------------------
        # ------- Second Row
        # --- Root
        lbl_root = Label(frame_top, bd=1, text='Root ', anchor=W, width=5,
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)

        self.tkvar_root = StringVar()
        self.tkvar_root.set('')
        i_project_root = Entry(frame_top, bd=1, width=73, textvariable=self.tkvar_root,
                               bg=self.col_i_bg_default, fg=self.col_bt_fg_default,
                               relief=self.def_bt_relief, insertbackground=self.col_bt_fg_default)
        bt_root = Button(frame_top, text='pick', width=4, bg=self.col_bt_bg_default,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                         bd=self.default_bt_bd, relief=self.def_bt_relief,
                         command=lambda x=self.tkvar_root: pick_dir(x))
        # Placement
        lbl_root.grid(row=1, column=0, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        i_project_root.grid(row=1, column=1, columnspan=1, sticky=NSEW, padx=self.default_padding,
                            pady=self.default_padding)
        bt_root.grid(row=1, column=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)

        # ------ SEPARATOR
        frame_separator = Frame(self.frame_software_header, bg=self.col_bt_fg_default)
        # Placement
        frame_separator.grid(row=0, column=0, columnspan=7, sticky=NSEW, padx=2*self.default_padding,
                             pady=2*self.default_padding)

        # --- Headers
        lbl_label = Label(self.frame_software_header, bd=1, text='Software Label', width=21,
                          bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_path = Label(self.frame_software_header, bd=1, text='Path to EXE', width=19,
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_support = Label(self.frame_software_header, bd=1, text='supports OCIOs',
                            bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_ocio_alternative = Label(self.frame_software_header, bd=1, text='alternative OCIO', width=19,
                                     bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        bt_software_add = Button(self.frame_software_header, text='+', width=4, bg=self.col_bt_bg_default,
                                 fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                                 activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                 bd=self.default_bt_bd, relief=self.def_bt_relief,
                                 command=lambda: self.software_add())
        self.software_add()

        # Placement
        lbl_label.grid(row=1, column=0, sticky=N, padx=self.default_padding, pady=self.default_padding)
        lbl_path.grid(row=1, column=1, columnspan=2, sticky=N, padx=self.default_padding, pady=self.default_padding)
        lbl_support.grid(row=1, column=3, sticky=N, padx=self.default_padding, pady=self.default_padding)
        lbl_ocio_alternative.grid(row=1, column=4, columnspan=2, sticky=N, padx=self.default_padding,
                                  pady=self.default_padding)
        bt_software_add.grid(row=1, column=6, sticky=N, padx=self.default_padding, pady=self.default_padding)

        if config is not None:
            self.load_show(config)

        self.project_creator_ui.geometry('')

        self.project_creator_ui.attributes("-alpha", 1.0)
        self.project_creator_ui.wm_attributes("-topmost", 1)
        self.project_creator_ui.mainloop()
