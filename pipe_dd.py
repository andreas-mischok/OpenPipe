from pipe_utils import *


class Dropdown:
    def __init__(self, parent, bt, options):
        self.parent = parent
        self.bt = bt
        self.options = options
        self.parent.open_dd = self

        self.ui_child = self.col_bt_fg_default = self.col_bt_petrol = self.def_bt_relief = self.default_padding = \
            self.col_wdw_default = self.col_bt_petrol_highlight = None

        self.current_page = 0
        self.page_limit = 24
        self.last_page = int((len(self.options)-1)/self.page_limit)
        self.page_elements = []

        json_load_ui_variables(self, r'.\ui\defaults_ui.json')

    def ui_draw(self):
        # Reset
        self.frame_main.configure(bg=self.col_bt_petrol)
        for element in self.page_elements:
            element.destroy()

        # self.prv_elements = [x for x in self.page_elements]
        self.page_elements = []

        # Draw elements
        frame_separator1 = Frame(self.frame_main, bg="gray60", height=2)
        frame_separator1.pack(fill=X)
        frame_separator2 = Frame(self.frame_main, bg="black", height=1)
        frame_separator2.pack(fill=X)
        self.page_elements.append(frame_separator1)
        self.page_elements.append(frame_separator2)
        for i in range(self.page_limit):
            item_index = i + self.current_page * self.page_limit
            if item_index < len(self.options):
                item = self.options[item_index]
                if i != 0:
                    frame_separator = Frame(self.frame_main, bg="gray60", height=1)
                    frame_separator.pack(fill=X)
                    self.page_elements.append(frame_separator)

                bt_item = Button(self.frame_main, text=item, bg=self.col_bt_petrol,
                                 fg=self.col_bt_fg_default, relief=self.def_bt_relief, bd=0,
                                 command=lambda x=item_index: self.select_ui(x), anchor=W)
                bt_item.pack(fill=X)
                bt_item.bind('<Enter>', self.on_dd_enter)
                bt_item.bind('<Leave>', self.on_dd_leave)

                self.page_elements.append(bt_item)

            else:
                break

        if self.page_limit < len(self.options):
            frame_separator = Frame(self.frame_main, bg="gray60", height=1)
            frame_separator.pack(fill=X)
            self.page_elements.append(frame_separator)
            l_hint = Label(self.frame_main, bd=1, text='scroll for nxt/prv page',
                           bg='gray40', fg=self.col_bt_fg_default)
            l_hint.configure(text=f'page {self.current_page+1}/{self.last_page+1}')
            l_hint.pack(fill=X)
            self.page_elements.append(l_hint)
            #CreateToolTip(self.frame_main,
            #              "Scroll to go to next page.")

        self.frame_main.configure(bg='gray60')

    def on_dd_enter(self, e):
        e.widget['background'] = self.col_bt_petrol_highlight

    def on_dd_leave(self, e):
        e.widget['background'] = self.col_bt_petrol

    def select_ui(self, button_index):
        self.bt.configure(text=f'{self.options[button_index]}')
        self.parent.update_dropdowns()
        close_sub_ui(self.ui_child)

    def close(self, event=None):
        #self.parent.focus_set()
        close_sub_ui(self.ui_child)

    def scroll(self, e):
        change = False
        if e.delta > 0:
            if self.current_page > 0:
                self.current_page -= 1
                change = True
        else:
            if self.current_page < self.last_page:
                self.current_page += 1
                change = True
        if change:
            self.ui_draw()

    def key_press(self, e):
        """Jumps to the page with the first prop starting with that letter."""
        prop_names = [[x[3:], self.parent.assets.index(x)] for x in self.parent.assets if x[:3] == 'prp']
        for prp, i in prop_names:
            if prp[0].upper() == str(e.char).upper():
                self.current_page = int(i / self.page_limit)
                self.ui_draw()
                break

    def create_ui_dropdown(self):
        bt_pos_x = self.bt.winfo_rootx()
        bt_pos_y = self.bt.winfo_rooty()
        bt_dim_x = self.bt.winfo_width()
        bt_dim_y = self.bt.winfo_height()
        dimensions = f'1x1+{bt_pos_x}+{bt_pos_y+bt_dim_y-1}'

        # self.ui_proxy = Tk()
        ui_dropdown = Toplevel()
        self.ui_child = ui_dropdown
        ui_dropdown.focus_force()
        ui_dropdown.lift()
        ui_dropdown.bind("<FocusOut>", self.close)
        ui_dropdown.bind("<MouseWheel>", self.scroll)
        ui_dropdown.bind("<Key>", self.key_press)
        ui_dropdown.attributes("-alpha", 0.0)
        # ui_dropdown.iconbitmap(r'.\ui\icon_pipe.ico')
        # ui_dropdown.title('Pull')
        ui_dropdown.geometry(dimensions)
        ui_dropdown.configure(bg='gray60')#self.col_wdw_default)

        ui_dropdown.overrideredirect(True)
        ui_dropdown.configure(highlightcolor=self.parent.col_wdw_border, highlightthickness=1,
                              highlightbackground='gray60')#self.parent.col_wdw_border_background)

        self.frame_main = Frame(ui_dropdown, bg='gray60', width=50, bd=1)#self.col_wdw_default
        #self.frame_main.configure(bg='#900000')
        self.frame_main.pack(side=TOP, anchor=N, fill=BOTH, padx=0, pady=0)
        # ---------------------------------------------------------------------------------------------
        try:
            self.current_page = int(self.options.index(self.bt.cget('text')) / self.page_limit)
        except ValueError:
            self.current_page = 0
        self.ui_draw()
        # ---------------------------------------------------------------------------------------------
        ui_dropdown.geometry('')
        ui_dropdown.minsize(width=bt_dim_x, height=1)

        ui_dropdown.attributes("-alpha", 1.0)
        ui_dropdown.wm_attributes("-topmost", 1)
        ui_dropdown.mainloop()


# TODO button: 850
# TODO textfield search function?
