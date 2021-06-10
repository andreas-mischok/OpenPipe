# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pipe_utils import *
from datetime import datetime
import subprocess


class ReleaseAnim:
    def __init__(self):
        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = \
            self.col_bt_bg_blue_highlight = self.def_bt_relief = self.default_padding = self.default_bt_bd = \
            self.col_bt_bg_default = self.col_bt_bg_blue_active = self.ui_proxy = \
            self.ui_child = self.x_offset = self.y_offset = \
            self.col_ui_bt_small = self.col_ui_bt_small_highlight = self.col_ui_dd_default = \
            self.col_wdw_border = self.col_wdw_border_background = self.col_wdw_title = self.col_bt_petrol = \
            self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight = self.col_bt_red = \
            self.col_bt_red_highlight = self.dir_pantry_anm = self.dir_pipeline_anm = self.dir_export_shd = None

        self.current_root = self.current_project_name = self.user = self.current_asset = \
            self.current_discipline = self.current_department = self.parent = self.list_updates_pull = \
            self.frame_main = self.dir_asset = self.bt_publish = self.lbl_update_publish = self.overwrite = \
            self.publish = None

        self.tk_animations = []
        self.tk_animation_bools = []

        self.user = os.getenv('PIPE_USER')
        self.current_root = os.getenv('PIPE_ROOT')
        self.current_project_name = os.getenv('PIPE_PROJECT')
        self.current_department = os.getenv('PIPE_DEPARTMENT')
        self.current_discipline = os.getenv('PIPE_DISCIPLINE')
        self.current_asset = os.getenv('PIPE_ASSET')

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

    def ui_animations(self, frame, animations):
        self.tk_animations = []
        self.tk_animation_bools = []

        animations = ['.'.join(x.split('.')[:-1]) for x in animations]
        row = 1
        for i, animation in enumerate(animations):
            dir_variation = os.path.join(self.parent.dir_export_anm, animation)
            #animations = [x for x in os.listdir(dir_variation) if os.path.join(dir_variation, x)]
            state = NORMAL if len(animations) > 0 else DISABLED

            width_limit = 8
            row = 1
            column = i
            while column > width_limit - 1:
                row += 1
                column -= width_limit
            row = int(i / width_limit)
            column = i % width_limit

            tkvar_anim = BooleanVar()
            tkvar_anim.set(len(animations) > 0)
            cb_variation = Checkbutton(frame, text=animation, var=tkvar_anim, state=state,
                                       bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                       fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                       selectcolor=self.col_bt_bg_active)
            cb_variation.grid(row=row, column=column, sticky=W, padx=self.default_padding, pady=self.default_padding)
            if state == DISABLED:
                CreateToolTip(cb_variation,
                              "no new textures have been detected")

            if len(animations) > 0:
                self.tk_animations.append(animation)
                self.tk_animation_bools.append(tkvar_anim)

        if len(self.tk_animations) > 0:
            return row

    def release_animations(self):
        skip_copy = True
        self.publish = self.var_publish.get()
        self.overwrite = self.var_overwrite.get()

        animations_for_export = [x for i, x in enumerate(self.tk_animations) if self.tk_animation_bools[i].get()]

        if len(animations_for_export) > 0:
            for animation in animations_for_export:
                dir_animation_pantry = os.path.join(self.parent.dir_pantry_anm, animation)

                if os.path.isdir(dir_animation_pantry) is False:
                    os.makedirs(dir_animation_pantry)

                dir_pipe_animation = str(os.path.join(self.parent.dir_pipeline_anm, animation))
                dir_pipe_animation_versions = os.path.join(dir_pipe_animation, 'versions')
                if os.path.isdir(dir_pipe_animation_versions) is False:
                    os.makedirs(dir_pipe_animation_versions)
                existing_pipe_versions = os.listdir(dir_pipe_animation_versions)

                dir_pantry_animation = os.path.join(self.parent.dir_pantry_anm, animation)
                if os.path.isdir(dir_pantry_animation) is False:
                    os.makedirs(dir_pantry_animation)
                existing_pantry_versions = [x for x in os.listdir(dir_pantry_animation) if
                                            os.path.isdir(os.path.join(dir_pantry_animation, x))]

                # Generate latest version numbers
                pantry_version_cur = 'v001'
                pipe_version_cur = 'v001'
                if len(existing_pantry_versions) != 0:
                    existing_pantry_versions.sort()
                    latest_existing_pantry_version = existing_pantry_versions[-1]

                    pantry_version_cur_int = int(latest_existing_pantry_version[1:])
                    pipe_version_cur_int = len(existing_pipe_versions)

                    if self.overwrite is False:
                        pantry_version_cur_int = pantry_version_cur_int + 1
                        pipe_version_cur_int = pipe_version_cur_int + 1

                    pantry_version_cur = 'v' + format(pantry_version_cur_int, '03d')
                    pipe_version_cur = 'v' + format(pipe_version_cur_int, '03d')

                # .pipeline
                # version
                dict_version = {
                    "artist": self.user,
                    "time": str(datetime.now()).split('.')[0],
                    "channel_version": pantry_version_cur,
                    "published": self.publish
                }

                file_name = f'{animation}.{pipe_version_cur}.json'
                file = os.path.join(dir_pipe_animation_versions, file_name)
                print(file)
                with open(file, 'w') as json_output_channel:
                    json.dump(dict_version, json_output_channel, indent=2)

                # package
                file_package = os.path.join(dir_pipe_animation, f'{animation}.json')

                if os.path.isfile(file_package):
                    with open(file_package, 'r') as json_content:
                        dict_package = json.load(json_content)
                        dict_package["anm"] = pipe_version_cur
                else:
                    dict_package = {
                        "mdl": '',
                        "txt": '',
                        "shd": '',
                        "anm": pipe_version_cur,
                        "anm_publish": ''
                    }
                if self.publish:
                    dict_package["anm_publish"] = pipe_version_cur

                with open(file_package, 'w') as json_output_channel:
                    json.dump(dict_package, json_output_channel, indent=2)

                # .pantry
                dir_pantry_version_current = os.path.join(self.parent.dir_pantry_anm, animation, pantry_version_cur)
                if os.path.isdir(dir_pantry_version_current) is False:
                    os.makedirs(dir_pantry_version_current)

                file_animation_src = os.path.join(self.parent.dir_export_anm, f'{animation}.abc')
                file_animation_trgt = os.path.join(dir_pantry_version_current, f'{animation}.abc')

                if skip_copy is False:
                    shutil.move(file_animation_src, file_animation_trgt)
                else:
                    shutil.copy2(file_animation_src, file_animation_trgt)

                # Open Blender (tested with 2.91
                blenders = [x for x in list(self.parent.dict_software.keys()) if 'Blender' in x]
                blender_291 = [x for x in blenders if '2.91' in x]

                if len(blender_291) != 0 :
                    blender = blender_291[0]
                else:
                    blender = blenders[0]

                os.putenv('PIPE_PYTHON_ROOT', os.path.abspath('./'))
                os.putenv('PIPE_DEPARTMENT', self.parent.current_department)
                os.putenv('PIPE_DISCIPLINE', self.parent.current_discipline)
                os.putenv('PIPE_ASSET', self.parent.current_asset)
                os.putenv('PIPE_ROOT', self.parent.current_root)
                os.putenv('PIPE_PROJECT', self.parent.current_project_name)
                os.putenv('PIPE_PROJECT_ABBR', [x.split('-')[1] for x in self.parent.projects
                                                if self.parent.current_project_name == x.split('-')[0]][0])

                os.putenv('PIPE_ALEMBIC', file_animation_src)
                os.putenv('PIPE_OUTPUT', dir_pantry_version_current)
                os.putenv('PIPE_ANIMATION', animation)

                exe = self.parent.dict_software[blender]["exe"]
                cmd = f'{exe} --background --factory-startup --python ./pipe_blender_convert_alembic_v001.py'
                #cmd = f'{exe} --python ./pipe_blender_convert_alembic_v001.py'
                subprocess.call(cmd)

                message = 'Successfully released animation.'
                messagebox.showinfo(title='', message=message)

                close_sub_ui(self.ui_child)
                close_sub_ui(self.ui_proxy)

    def create_ui_release_animation(self, parent):
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
        ui_release_anim = Toplevel()
        ui_release_anim.lift()
        ui_release_anim.attributes("-alpha", 0.0)
        ui_release_anim.iconbitmap(r'.\ui\icon_pipe.ico')
        ui_release_anim.title('Release ANM')
        ui_release_anim.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, ui_release_anim, 'Release ANM',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)
        ui_release_anim.configure(bg=self.col_wdw_default)

        self.frame_main = Frame(ui_release_anim, bg=self.col_wdw_default)
        self.frame_main.pack(side=TOP, anchor=N, fill=X, padx=self.default_padding, pady=self.default_padding)

        # ---------------------------------------------------------------------------------------------
        text = f'{self.parent.current_asset}  //  {self.parent.current_discipline.upper()} Stream'
        lbl_source_directory = Label(self.frame_main, bd=1, text=text, anchor=W,
                                     bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_source_directory.grid(row=0, column=0, columnspan=3, sticky=W, padx=2.5 * self.default_padding,
                                  pady=2.5 * self.default_padding)
        CreateToolTip(lbl_source_directory,
                      f'Source directory:    \n{self.parent.current_project_name}  /  build  /  '
                      f'{self.parent.current_asset}  /  anm  /  _export')
        # ---------------------------------------------------------------------------------------------

        # --- Variations ------------------------------------------------------------------------------
        variations = [x for x in os.listdir(self.parent.dir_export_anm) if os.path.isfile(os.path.join(self.parent.dir_export_anm, x))]

        frame_variations = Frame(self.frame_main, bg=self.col_wdw_default)
        frame_variations.grid(row=1, column=0, columnspan=3, sticky=W, padx=2.5 * self.default_padding,
                              pady=2.5 * self.default_padding)
        last_row = self.ui_animations(frame_variations, variations)

        # ---------------------------------------------------------------------------------------------
        self.var_overwrite = BooleanVar()
        self.var_overwrite.set(False)
        cb_overwrite = Checkbutton(self.frame_main, text='overwrite existing', var=self.var_overwrite,
                                   bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                   fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                   selectcolor=self.col_bt_bg_active)
        cb_overwrite.grid(row=2, column=0, sticky=N, padx=self.default_padding, pady=self.default_padding)
        CreateToolTip(cb_overwrite,
                      "Also skips update of .json files used by the pipeline.\n\n"
                      "You should not use this feature if the current version has already been published.")

        self.var_publish = BooleanVar()
        self.var_publish.set(True)
        cb_publish = Checkbutton(self.frame_main, text='publish result', var=self.var_publish,
                                 bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                 fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                 selectcolor=self.col_bt_bg_active)
        cb_publish.grid(row=2, column=1, sticky=N, padx=7 * self.default_padding, pady=self.default_padding)

        self.bt_release = Button(self.frame_main, text='Release textures into the wild', width=24,
                                 border=self.default_bt_bd,
                                 bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                 activebackground=self.col_bt_bg_active, activeforeground=self.col_bt_fg_default,
                                 command=lambda: self.release_animations())
        # self.bt_release.config(state=DISABLED)
        self.bt_release.grid(row=2, column=2, sticky=N, padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        ui_release_anim.geometry('')

        ui_release_anim.attributes("-alpha", 1.0)
        ui_release_anim.wm_attributes("-topmost", 1)
        ui_release_anim.mainloop()
# TODO is overwriting actually working?