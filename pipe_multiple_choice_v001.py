from pipe_utils import *


class MultipleChoice:
    def __init__(self, parent, title,  text, choices):
        self.ui_multiple_choice = self.col_wdw_title = self.col_wdw_default = self.ui_proxy = self.parent = \
            self.ui_child = self.x_offset = self.y_offset = self.default_padding = self.col_bt_bg_active = \
            self.col_bt_bg_default = self.col_bt_fg_default = self.default_bt_bd = self.def_bt_relief = self.result = \
            None

        self.parent = parent
        self.title = title
        self.text = text
        self.choices = choices

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.ui_main()

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

    def return_choice(self, choice):
        self.result = choice
        close_sub_ui(self.ui_child)
        close_sub_ui(self.ui_proxy)

    def ui_main(self):
        #self.directory_build = directory

        self.ui_proxy = Toplevel()
        self.ui_multiple_choice = Toplevel()
        self.ui_multiple_choice.lift()
        self.ui_multiple_choice.iconbitmap(r'.\ui\icon_pipe.ico')
        self.ui_multiple_choice.title(self.title)
        self.ui_multiple_choice.attributes("-alpha", 0.0)
        self.ui_multiple_choice.geometry('300x300+420+100')
        ui_title_bar(self, self.ui_proxy, self.ui_multiple_choice, self.title, r'.\ui\icon_pipe_white_PNG_s.png',
                     self.col_wdw_title)

        self.ui_multiple_choice.resizable(width=False, height=True)
        self.ui_multiple_choice.configure(bg=self.col_wdw_default)

        frame = Frame(self.ui_multiple_choice, bg=self.col_wdw_default)
        frame.pack(fill=X, padx=self.default_padding, pady=2*self.default_padding)

        # --------------------------------------------------------------------------------------------------------------
        lbl_text = Label(frame, bd=1, text=self.text, anchor=CENTER, #width=5,
                         bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_text.grid(row=0, column=0, columnspan=len(self.choices), sticky=NSEW, padx=self.default_padding,
                      pady=2 * self.default_padding)

        for i, choice in enumerate(self.choices):
            bt_choice = Button(frame, text=choice, command=lambda x=choice: self.return_choice(x),
                               padx=8, pady=4,
                               bg=self.col_bt_bg_default,
                               fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_active,
                               activeforeground=self.col_bt_fg_default, highlightthickness=0,
                               bd=self.default_bt_bd, relief=self.def_bt_relief, justify=CENTER)
            bt_choice.grid(row=1, column=i, sticky=NSEW, padx=self.default_padding,
                           pady=self.default_padding)

        # --------------------------------------------------------------------------------------------------------------
        self.ui_multiple_choice.geometry('')

        self.ui_multiple_choice.attributes("-alpha", 1.0)
        self.ui_multiple_choice.wm_attributes("-topmost", 1)
        self.ui_multiple_choice.mainloop()
