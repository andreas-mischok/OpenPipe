# Import built-in modules
import os
import json
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

# Import local modules
from pipe_utils import ui_title_bar, json_load_ui_variables, CreateToolTip, close_sub_ui
from pipe_dd import Dropdown


class SequenceCreator:
    def __init__(self):
        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_active = self.col_bt_bg_green = \
            self.default_padding = self.col_i_bg_default = self.def_bt_relief = self.default_bt_bd = \
            self.col_bt_bg_blue = self.col_bt_bg_blue_highlight = self.col_bt_bg_default = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.col_bt_bg_blue_active = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.col_dd_blue_default = self.parent = None

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.col_ui_dd_default = self.col_bt_petrol
        self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight

    def execute(self):
        nm = self.tkvar_sequence_nm.get()
        if nm:
            if re.match("^[A-Za-z0-9_-]*$", nm):
                self.parent.tkvar_shot.set("layout")
                self.parent.sequences.insert(-1, nm)
                self.parent.create_sequence_dd()
                self.parent.dd_sequence.config(text=nm)
                close_sub_ui(self.sequence_creator_ui)
            else:
                print("\nERROR: Sequence name contains illegal character(s).")
        else:
            print("\nERROR: No name was entered.")

    def limit_input_length(self):
        """Automatically shortens the shot-name if user tries to enter too long name."""
        cur_text = self.tkvar_sequence_nm.get()
        if len(cur_text) > 10:
            self.tkvar_sequence_nm.set(cur_text[:10])

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

    def create_ui(self, parent):
        self.parent = parent
        parent.open_dd.close()
        # dimensions = '330x75+420+155'
        dimensions = '330x75+420+195'
        self.ui_proxy = Toplevel()
        self.sequence_creator_ui = Toplevel()
        self.sequence_creator_ui.lift()
        self.sequence_creator_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        self.sequence_creator_ui.title('Project Duplicator')
        self.sequence_creator_ui.attributes("-alpha", 0.0)
        self.sequence_creator_ui.geometry(dimensions)
        ui_title_bar(
            self, self.ui_proxy, self.sequence_creator_ui,
            'Sequence Creator', r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title
        )
        self.sequence_creator_ui.resizable(width=False, height=True)
        self.sequence_creator_ui.configure(bg=self.col_wdw_default)

        frame = Frame(self.sequence_creator_ui, bg=self.col_wdw_default)
        frame.pack(fill=X, padx=self.default_padding, pady=2 * self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.tkvar_sequence_nm = StringVar()
        self.tkvar_sequence_nm.set('')
        i_name = Entry(frame, bd=1, textvariable=self.tkvar_sequence_nm, width=11,
                       bg=self.col_i_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                       insertbackground=self.col_bt_fg_default)
        i_name.grid(row=0, column=0, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        self.tkvar_sequence_nm.trace("w", lambda name, index, mode: self.limit_input_length())
        CreateToolTip(
            i_name,
            "Sequence name.\n\nOnly use letters, numbers, -, _",
            self.col_i_bg_default,
            self.col_i_bg_default
        )

        b_save = Button(
            frame, text=" Create Sequence", bg=self.col_bt_bg_green, fg=self.col_bt_fg_default,
            activebackground=self.col_bt_bg_active,
            highlightthickness=0, bd=self.default_bt_bd, relief=self.def_bt_relief,
            command=lambda: self.execute()
        )
        b_save.grid(row=0, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        self.sequence_creator_ui.geometry('')

        self.sequence_creator_ui.attributes("-alpha", 1.0)
        self.sequence_creator_ui.wm_attributes("-topmost", 1)
        self.sequence_creator_ui.mainloop()


class ShotCreator:
    def __init__(self, edit_mode):
        self.edit_mode = False  # edit_mode

        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_active = self.col_bt_bg_green = \
            self.default_padding = self.col_i_bg_default = self.def_bt_relief = self.default_bt_bd = \
            self.col_bt_bg_blue = self.col_bt_bg_blue_highlight = self.col_bt_bg_default = \
            self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = self.col_bt_bg_blue_active = \
            self.col_wdw_title = self.col_wdw_border = self.col_wdw_border_background = \
            self.col_dd_blue_default = self.parent = self.dd_sequence = None

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.col_ui_dd_default = self.col_bt_petrol
        self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight

    def update_dropdowns(self):
        self.switch_sequence(self.dd_sequence.cget('text'))

    def switch_sequence(self, sequence_nm):
        if sequence_nm == "+":
            self.dd_sequence.config(text="")
            # given_nm = simpledialog.askstring(title="Create Sequence", prompt="TEST")
            # messagebox.askquestion(title="", message="test")
            # simpledialog.askstring(title="", prompt="test")

            SequenceCreator().create_ui(self)

    def create_sequence_dd(self):
        """Extracted from main block as it needs to be replaced when a new sequence is created."""
        if self.dd_sequence:
            self.dd_sequence.destroy()

        self.dd_sequence = Button(
            self.frame, text="", bg=self.col_ui_dd_default, anchor=W, fg=self.col_bt_fg_default,
            relief=self.def_bt_relief, bd=1, width=10
        )
        self.dd_sequence.configure(
            command=lambda bt=self.dd_sequence, options=self.sequences: self.dd_ui(bt, options)
        )
        self.dd_sequence.grid(
            row=1, column=0, columnspan=1, sticky=EW, padx=self.default_padding, pady=self.default_padding
        )
        self.dd_sequence.bind('<Enter>', self.on_dd_enter)
        self.dd_sequence.bind('<Leave>', self.on_dd_leave)

        CreateToolTip(
            self.dd_sequence,
            "Sequence",
            self.col_ui_dd_default_highlight,
            self.col_ui_dd_default
        )

    def limit_input_length(self):
        """Automatically shortens the shot-name if user tries to enter too long name."""
        cur_text = self.tkvar_shot.get()
        if len(cur_text) > 6:
            self.tkvar_shot.set(cur_text[:6])

    def execute(self):
        """Called by the 'Create Shot'-button."""
        self.shot_nm = self.tkvar_shot.get()
        self.seq_nm = self.dd_sequence.cget('text')

        shot_length = len(self.shot_nm)
        if shot_length >= 2:
            if self.seq_nm:
                if re.match("^[A-Za-z0-9_-]*$", self.shot_nm):
                    self.dir_seq = os.path.join(self.parent.dir_sequences, self.seq_nm)
                    self.dir_shot = os.path.join(self.parent.dir_sequences, self.seq_nm, self.shot_nm)
                    if os.path.isdir(self.dir_shot) is False:
                        print("Creating Sq/Sh")
                        self.create_directory_structure()
                        # Update Main UI
                        self.parent.switch_department('sequence')
                        self.parent.switch_sequence(self.seq_nm)
                        self.parent.switch_shot(self.shot_nm)
                        close_sub_ui(self.ui_child)
                    else:
                        print("\nERROR: This shot already exists.")
                else:
                    print("\nERROR: Illegal characters in shot name. Only letters, number, -, _ are allowed.")
            else:
                print("\nERROR: No sequence was given.")
        else:
            print(f"\nERROR: The name of the SHOT is too SHORT. ({shot_length}<2)")

    def create_directory_structure(self):
        # TODO update dropdowns in mainwindow
        # Create Directories
        directories = []
        directories.append(self.dir_shot)

        dir_pipeline = os.path.join(self.dir_seq, ".pipeline")
        dir_pipeline_shot = os.path.join(dir_pipeline, self.shot_nm)
        directories.append(dir_pipeline_shot)
        dir_pipeline_shot_versions = os.path.join(dir_pipeline_shot, 'versions')
        directories.append(dir_pipeline_shot_versions)

        dir_pantry = os.path.join(self.dir_shot, ".pantry")
        directories.append(dir_pantry)

        dir_files = os.path.join(self.dir_shot, "files")
        directories.append(dir_files)
        dir_fl_blender = os.path.join(dir_files, "blender")
        directories.append(dir_fl_blender)

        for directory in directories:
            # print(directory)
            if os.path.isdir(directory) is False:
                os.makedirs(directory)
            if '.' not in directory.split(os.sep)[-1]:
                continue
        # Create Package file
        dict_package = {
            "version": ""
        }
        file_shot_package = os.path.join(dir_pipeline_shot, "shot_package.json")
        with open(file_shot_package, 'w') as package_file:
            json.dump(dict_package, package_file, indent=2)

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

    def dd_ui(self, bt, options):
        self.dd = Dropdown(self, bt, options).create_ui_dropdown()

    def on_dd_enter(self, e):
        e.widget['background'] = self.col_ui_dd_default_highlight

    def on_dd_leave(self, e):
        e.widget['background'] = self.col_ui_dd_default

    def create_ui(self, parent):
        # --- PROLOGUE ---
        self.parent = parent
        self.sequences = [x for x in self.parent.sequences] + ["+"]

        dimensions = '240x59+420+100'
        self.ui_proxy = Toplevel()
        self.shot_creator_ui = Toplevel()
        self.shot_creator_ui.lift()
        self.shot_creator_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        title = 'Shot Editor' if self.edit_mode else 'Shot Creator'
        self.shot_creator_ui.title(title)
        self.shot_creator_ui.attributes("-alpha", 0.0)
        self.shot_creator_ui.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, self.shot_creator_ui, title, r'.\ui\icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)

        self.shot_creator_ui.resizable(width=False, height=True)
        self.shot_creator_ui.configure(bg=self.col_wdw_default)

        self.frame = Frame(self.shot_creator_ui, bg=self.col_wdw_default)
        self.frame.pack(fill=X, padx=self.default_padding, pady=2*self.default_padding)

        shots = ["", "+"]

        # --- STORY ---
        # Sequence
        l_sequence = Label(
            self.frame, text="Sequence", bg=self.col_wdw_default, fg=self.col_bt_fg_default
        )  # self.wrap_length)
        # l_sequence.grid(row=0, column=0, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        self.create_sequence_dd()

        # Shot
        l_shot = Label(
            self.frame, text="Shot", bg=self.col_wdw_default, fg=self.col_bt_fg_default
        )  # self.wrap_length)
        # l_shot.grid(row=0, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        self.tkvar_shot = StringVar()
        self.tkvar_shot.set('')
        self.tkvar_shot.trace("w", lambda name, index, mode: self.limit_input_length())
        i_shot = Entry(
            self.frame, bd=1, textvariable=self.tkvar_shot, bg=self.col_i_bg_default, fg=self.col_bt_fg_default,
            relief=self.def_bt_relief, insertbackground=self.col_bt_fg_default, width=7
        )
        i_shot.grid(row=1, column=1, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        CreateToolTip(
            i_shot,
            "Shot.\n\nShould Either be a 4 digit number or the phrase 'layout'.",
            self.col_i_bg_default,
            self.col_i_bg_default
        )

        # Create Button
        bt_create = Button(
            self.frame, text="Create Shot", bg=self.col_bt_bg_green, fg=self.col_bt_fg_default,
            activebackground=self.col_bt_bg_active,
            highlightthickness=0, bd=self.default_bt_bd, relief=self.def_bt_relief,
            command=lambda: self.execute()
        )
        bt_create.grid(row=2, column=0, columnspan=2, sticky=NSEW, padx=self.default_padding, pady=self.default_padding)

        # --- EPILOGUE ---
        self.shot_creator_ui.geometry('')
        self.shot_creator_ui.attributes("-alpha", 1.0)
        self.shot_creator_ui.wm_attributes("-topmost", 1)
        self.shot_creator_ui.mainloop()


# TODO camera packages?
