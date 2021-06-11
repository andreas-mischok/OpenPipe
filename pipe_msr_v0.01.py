# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
from tkinter import *
from tkinter import filedialog
from pipe_utils import *


class MundaneSequenceRenamer:
    def __init__(self):
        self.version = os.path.basename(__file__).split('_')[-1][:-3]

        self.tkvar_in_files = self.tkvar_out_files = self.files_in_full_path = self.files_in = self.tkvar_replace = \
            self.i_tx_replace_in = self.i_tx_replace_out = self.tkvar_replace_in = self.tkvar_replace_out = \
            self.path = self.files_out = self.tkvar_udim2mb = self.tkvar_mb2udim = self.i_tx_offset_in = \
            self.tkvar_offset_in = self.tkvar_offset = self.ui_proxy = self.ui_child = self.x_offset = \
            self.y_offset = self.col_wdw_border = self.col_wdw_border_background = self.col_wdw_title = \
            self.col_i_bg_default = self.def_bt_relief = self.default_padding = self.col_bt_bg_default = None

        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = \
            self.col_wdw_bright = None
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.ui_msr()

    def load_files_dialogue(self):
        root = os.getenv('PIPE_ROOT')
        project = os.getenv('PIPE_PROJECT')
        department = os.getenv('PIPE_DEPARTMENT')
        asset = os.getenv('PIPE_ASSET')
        #initial_dir = '/'.join([root, project, department, asset])
        try:
            initial_dir = os.path.join(root, project, department, asset)
        except TypeError:
            initial_dir = os.path.join(root, project)

        self.files_in_full_path = filedialog.askopenfilenames(title='select', initialdir=initial_dir,
                                                              filetypes=[('ALL', '*.*'), ('PNG', '*.png')])
        self.files_in_full_path = [x for x in self.files_in_full_path]
        self.load_files()

    def load_files(self):
        if len(self.files_in_full_path) > 0:
            self.files_in = [x.split('/')[-1] for x in self.files_in_full_path]
            self.path = '/'.join(self.files_in_full_path[0].split('/')[:-1]) + '/'
            self.tkvar_in_files.set('\n'.join(self.files_in))
            self.update_outputs()

    def update_outputs(self):
        if self.files_in is not None:
            if len(self.files_in) > 0:
                do_replace = self.tkvar_replace.get()
                replace_in = self.tkvar_replace_in.get()
                replace_out = self.tkvar_replace_out.get()
                do_offset = self.tkvar_offset.get()

                udim_to_mudbox = self.tkvar_udim2mb.get()
                mudbox_to_udim = self.tkvar_mb2udim.get()

                offset = self.tkvar_offset_in.get()
                if len(offset) > 0 and offset is not '-':
                    try:
                        offset = int(offset)
                    except ValueError:
                        offset = 0
                        print(f'{offset} is not a valid input. Integer expected')
                else:
                    offset = 0

                self.files_out = [x for x in self.files_in]

                for i, file in enumerate(self.files_in):
                    if do_replace and replace_in in file:
                        self.files_out[i] = self.files_out[i].replace(replace_in, replace_out)

                    if udim_to_mudbox:
                        udim = file.split('.')[-2]
                        if len(udim) > 4 and udim[-5] is '_':
                            udim = udim[-4:]

                        if len(udim) == 4 and udim.isdecimal():
                            v = int(str(int(udim) - 1001 + 10)[:-1])
                            u = int(udim[3:])
                            if u == 0:
                                u = 10
                            mudbox = f'u{u}_v{v}'
                            file_out = self.files_out[i]
                            file_parts = file_out.split('.')
                            file_name, filetype = '.'.join(file_parts[:-1]), file_parts[-1]  # removes filetype and UDIM
                            file_out = file_name[:-4] + mudbox + '.' + filetype
                            self.files_out[i] = file_out

                    if mudbox_to_udim:
                        mudbox = file.split('.')[-2].split('_')
                        if len(mudbox) > 2:
                            mudbox = mudbox[-2:]
                        if 'u' in mudbox[0][0] and 'v' in mudbox[1][0]:
                            u = mudbox[0][1:]
                            v = mudbox[1][1:]
                            udim = 1000 + int(u) + (int(v) - 1) * 10
                            file_out = self.files_out[i]
                            file_parts = file_out.split('.')
                            file_name, filetype = '.'.join(file_parts[:-1]), file_parts[-1]

                            for x in range(len(file_name)):
                                if file_name[len(file_name)-1-x] is 'u':
                                    file_out = file_name[:len(file_name)-1-x] + str(udim) + '.' + filetype
                                    self.files_out[i] = file_out
                                    break

                    if do_offset:
                        frame = file.split('.')[-2]
                        if len(frame) > 4 and frame[-5] is '_':
                            frame = frame[-4:]
                        if frame.isdecimal():
                            file_out = self.files_out[i]
                            file_parts = file_out.split('.')
                            file_name, filetype = '.'.join(file_parts[:-1]), file_parts[-1]  # removes filetype and UDIM
                            file_out = file_name[:-4] + format(int(frame)+offset, '04d') + '.' + filetype
                            self.files_out[i] = file_out

                self.tkvar_out_files.set('\n'.join(self.files_out))

    def update_udim_to_mudbox(self):
        if self.tkvar_udim2mb.get():
            self.tkvar_mb2udim.set(False)
        self.update_outputs()

    def update_mudbox_to_udim(self):
        if self.tkvar_mb2udim.get():
            self.tkvar_udim2mb.set(False)
        self.update_outputs()

    def update_replace(self, _1, _2, _3):
        self.tkvar_replace.set(True)
        self.update_outputs()

    def update_offset(self, _1, _2, _3):
        self.tkvar_offset.set(True)
        self.update_outputs()

    def rename(self):
        if self.files_out is not None:
            if len(self.files_out) > 0:
                for i, (file_out, file_full_path) in enumerate(zip(self.files_out, self.files_in_full_path)):
                    os.rename(file_full_path, file_full_path + '.tmp')
                for i, (file_out, file_full_path) in enumerate(zip(self.files_out, self.files_in_full_path)):
                    os.rename(file_full_path + '.tmp', self.path + file_out)
                    self.files_in_full_path[i] = self.path + file_out
                    self.load_files()

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

    def ui_msr(self):
        default_bt_bd = 1
        def_bt_relief = 'solid'
        default_dimension = '880x222+420+100'  # '390x190'  # '310x215'
        default_padding = 2

        self.ui_proxy = Tk()
        ui_msr = Toplevel()
        ui_msr.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_msr.title('Mundane Sequence Renamer %s' % self.version)
        ui_msr.geometry(default_dimension)
        ui_title_bar(self, self.ui_proxy, ui_msr, 'Mundane Sequence Renamer', r'.\ui\icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)

        icon_mundane = PhotoImage(file=r'.\ui\bt_mundane.png')

        ui_msr.resizable(width=True, height=True)
        ui_msr.configure(bg=self.col_wdw_default)

        frame_main = Frame(ui_msr, bg=self.col_wdw_default)
        frame_main.pack(fill=X, padx=default_padding, pady=default_padding)

        frame_left = Frame(frame_main, bg=self.col_wdw_default)
        frame_left.grid(row=0, column=0, padx=default_padding, pady=default_padding, sticky=NSEW)

        frame_right = Frame(frame_main, bg=self.col_wdw_default)
        frame_right.grid(row=0, column=1, sticky=NSEW, padx=default_padding, pady=default_padding)
        frame_right.grid_rowconfigure(0, weight=1)

        bt_load = Button(frame_left, text='Load Files', width=10, bg=self.col_bt_bg_blue,
                         fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                         activeforeground=self.col_bt_fg_default,
                         highlightthickness=0, bd=default_bt_bd, relief=def_bt_relief,
                         command=lambda: self.load_files_dialogue(), height=1)
        bt_load.grid(row=0, column=0, padx=default_padding, pady=default_padding)

        # UDIM AND MUDBOX
        # CHECKBOX UDIM2MB
        self.tkvar_udim2mb = BooleanVar()
        self.tkvar_udim2mb.set(False)
        cb_udim2mb = Checkbutton(frame_left, text='UDIM to Mudbox', var=self.tkvar_udim2mb,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active,
                                 command=lambda: self.update_udim_to_mudbox())
        cb_udim2mb.grid(row=0, column=1, sticky=N, padx=default_padding, pady=default_padding)

        # CHECKBOX MB2UDIM
        self.tkvar_mb2udim = BooleanVar()
        self.tkvar_mb2udim.set(False)
        cb_mb2udim = Checkbutton(frame_left, text='Mudbox to UDIM', var=self.tkvar_mb2udim,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active,
                                 command=lambda: self.update_mudbox_to_udim())
        cb_mb2udim.grid(row=0, column=2, sticky=N, padx=default_padding, pady=default_padding)

        # Replace Options
        # Replace Checkbox
        self.tkvar_replace = BooleanVar()
        self.tkvar_replace.set(False)
        cb_replace = Checkbutton(frame_left, text='replace', var=self.tkvar_replace,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active,
                                 command=lambda: self.update_outputs())
        cb_replace.grid(row=1, column=0, sticky=NW, padx=default_padding, pady=default_padding)

        # Replace Input
        self.tkvar_replace_in = StringVar()
        self.tkvar_replace_in.set('')
        self.i_tx_replace_in = Entry(frame_left, textvariable=self.tkvar_replace_in, bd=1, width=18,
                                     bg='gray28', fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                     insertbackground=self.col_bt_fg_default, disabledbackground='gray25')
        self.i_tx_replace_in.grid(row=1, column=1, sticky=N, padx=2.5 * default_padding,
                                  pady=2.5 * default_padding)
        self.tkvar_replace_in.trace('w', self.update_replace)

        # Replace Output
        self.tkvar_replace_out = StringVar()
        self.tkvar_replace_out.set('')
        self.i_tx_replace_out = Entry(frame_left, textvariable=self.tkvar_replace_out, bd=1, width=18,
                                      bg='gray28', fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                      insertbackground=self.col_bt_fg_default, disabledbackground='gray25')
        self.i_tx_replace_out.grid(row=1, column=2, sticky=N, padx=2.5 * default_padding,
                                   pady=2.5 * default_padding)
        self.tkvar_replace_out.trace('w', self.update_replace)

        # Offset Options
        # Offset Checkbox
        self.tkvar_offset = BooleanVar()
        self.tkvar_offset.set(False)
        cb_offset = Checkbutton(frame_left, text='offset', var=self.tkvar_offset,
                                bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                selectcolor=self.col_bt_bg_active,
                                command=lambda: self.update_outputs())
        cb_offset.grid(row=2, column=0, sticky=NW, padx=default_padding, pady=default_padding)

        # Offset Input
        self.tkvar_offset_in = StringVar()
        self.tkvar_offset_in.set('')
        self.i_tx_offset_in = Entry(frame_left, textvariable=self.tkvar_offset_in, bd=1, width=39,
                                    justify=RIGHT,
                                    bg='gray28', fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                    insertbackground=self.col_bt_fg_default, disabledbackground='gray25')
        self.i_tx_offset_in.grid(row=2, column=1, columnspan=2, sticky=N, padx=2.5 * default_padding,
                                 pady=2.5 * default_padding)
        self.tkvar_offset_in.trace('w', self.update_offset)

        # Rename Button
        bt_execute = Button(frame_left, image=icon_mundane, text='Rename', width=14, bg=self.col_bt_bg_default,
                            fg=self.col_bt_fg_default, activebackground='gray26',
                            activeforeground=self.col_bt_fg_default, height=325,
                            highlightthickness=0, bd=default_bt_bd, relief=def_bt_relief,
                            command=lambda: self.rename())
        bt_execute.grid(row=3, column=0, columnspan=3, sticky=NSEW,
                        padx=default_padding, pady=default_padding)
        CreateToolTip(bt_execute,
                      "Say hello to Mundane Man. He is here to help you rename your files. It's a pretty mundane task "
                      "so he should be perfect for the job.")  # \n\n"
                      # "History: Mundane Man is a reference to the Superhero-button that Super-Sequence-Renamer uses.")

        # SEPARATOR
        fr_separator = Frame(frame_right, bg='gray60', width=2)
        fr_separator.grid(row=0, column=0, rowspan=6, padx=2*default_padding, pady=self.default_padding, sticky=NS)

        # Inputs and Outputs display
        # Input column
        lbl_in = Label(frame_right, bd=1, text='Input', anchor=W, width=36, justify=LEFT,
                       bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_in.grid(row=0, column=1, sticky=N, padx=default_padding, pady=default_padding)
        # Input list
        self.tkvar_in_files = StringVar()
        lbl_in_files = Label(frame_right, bd=1, textvariable=self.tkvar_in_files, anchor=NW, width=36, justify=LEFT,
                             bg='gray28', fg=self.col_bt_fg_default)
        lbl_in_files.grid(row=1, column=1, rowspan=5, sticky=NSEW, padx=3*default_padding, pady=2*default_padding)

        # Output column
        lbl_out = Label(frame_right, bd=1, text='Output', anchor=W, width=36, justify=LEFT,
                        bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_out.grid(row=0, column=2, sticky=N, padx=default_padding, pady=default_padding)
        # Output list
        self.tkvar_out_files = StringVar()
        lbl_out_files = Label(frame_right, bd=1, textvariable=self.tkvar_out_files, anchor=NW, width=37, justify=LEFT,
                              bg='gray28', fg=self.col_bt_fg_default, height=25)
        lbl_out_files.grid(row=1, column=2, rowspan=1, sticky=NSEW, padx=default_padding, pady=2*default_padding)

        ui_msr.geometry('')
        # ui_msr.wm_attributes("-topmost", 1)
        ui_msr.mainloop()


MundaneSequenceRenamer()
