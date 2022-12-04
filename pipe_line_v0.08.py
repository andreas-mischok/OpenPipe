# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Created by Andreas Mischok
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# import built-in
import time
import getpass

# import local modules
from pipe_utils import *
from pipe_utils_file_management import list_assets
from pipe_utils_file_management import get_build_dir
from pipe_dd import Dropdown
from pipe_pull_v001 import Pull
from pipe_publish_v001 import Publish
from pipe_package_manager_txt_v007 import PackageManager
from pipe_multiple_choice_v001 import MultipleChoice
from pipe_project_creator_v004 import ProjectCreator
from pipe_release_tool_anm_v002 import ReleaseAnim
from pipe_release_tool_txt_v004 import ReleaseTextures
from pipe_shot_creator import ShotCreator


class PipelineUI:
    def __init__(self):
        self.version = os.path.basename(__file__).split('_')[-1][:-3]
        self.user = getpass.getuser()
        os.putenv('PIPE_USER', self.user)  # store environment variable only for children
        self.python_path = "py"

        self.col_wdw_default = self.col_bt_fg_default = self.col_bt_bg_blue = self.col_bt_bg_active = \
            self.col_bt_bg_blue_highlight = self.def_bt_relief = self.default_padding = self.default_bt_bd = \
            self.col_bt_bg_default = self.current_root = self.dd_projects = self.current_project_name = self.main_ui =\
            self.col_bt_bg_blue_active = self.bt_projects_duplicate = self.bt_projects_edit = self.dd_department = \
            self.current_department = self.current_discipline = self.dd_discipline = self.ui_elements_asset = \
            self.dd_asset_test = self.current_asset = self.frame_asset = self.bt_asset_edit = self.assets = \
            self.icon_create = self.ui_proxy = self.ui_child = self.x_offset = self.y_offset = \
            self.col_ui_bt_small = self.col_ui_bt_small_highlight = self.col_ui_dd_default = \
            self.col_wdw_border = self.col_wdw_border_background = self.col_wdw_title = self.col_bt_petrol = \
            self.col_ui_dd_default_highlight = self.dd_software = self.current_software = self.frame_launcher = \
            self.col_bt_petrol_highlight = self.tkvar_ocio = self.cb_ocio = self.dict_software = \
            self.ocio_default = self.tkvar_top = self.bt_directory = self.initialise = self.col_bt_red = \
            self.col_bt_red_highlight = self.bt_pull = self.dir_pipeline_txt = self.bt_connections = \
            self.bt_rtt = self.bt_publish = self.frame_directories = self.dir_pipeline_mdl = self.bt_package = \
            self.bt_check = self.dir_pantry_mdl = self.dir_pantry_txt = self.dir_pipeline_shd = self.dir_pantry_shd = \
            self.dd_sequence = self.current_sequence = self.sequences = self.dd_shot = self.current_shot = \
            self.column_width = self.ui_elements_discipline = self.dir_pipeline_anm = self.icon_edit = \
            self.dir_export_txt = self.col_bt_bg_default_highlight = self.dd_software_redo = None

        if os.path.isdir(r'.\projects\\'):
            self.projects = [x for x in os.listdir(r'.\projects\\') if os.path.isdir(f'.\\projects\\{x}')]  # TODO replace with os.walk [0][1]
            self.projects_parts = [x.split('-') for x in self.projects]
            self.project_names = [x[0] for x in self.projects_parts]
            self.project_abbreviations = [x[1] for x in self.projects_parts]
        else:
            os.makedirs(r'.\projects\\')
            self.projects = []
        json_load_ui_variables(self, r'.\ui\defaults_ui.json')
        self.create_main_ui()

    def launch_software(self):
        """ Will set local OCIO environment variable according to project settings and launch
        the software currently selected in the software-dropdown.
        """
        self.store_last_job()
        state = self.cb_ocio.cget('state')

        try:
            dict_software_sub = self.dict_software[self.current_software]
            if 'Blender' in self.current_software or 'blender' in self.current_software:
                exe = dict_software_sub["exe"] + ' --python ./pipe_blender_v007.py'
                os.putenv("blender_exe", dict_software_sub["exe"])
            else:
                exe = dict_software_sub["exe"]

            if state == 'normal' and self.tkvar_ocio.get() is True:
                ocio_custom = dict_software_sub["alternative_ocio"]
                ocio = ocio_custom if len(ocio_custom) > 0 else self.ocio_default
            else:
                ocio = ''

            os.putenv('OCIO', ocio)
            os.system(f'start cmd /C {exe}')
        except KeyError:
            print("Software is no longer in the project list.")

    def start_release_texture(self):
        """ Launches new UI, which is used by texturing (and possibly modelling for displacement).
        - Creates folder structures.
        - Moves textures to versioned channel folder inside '<asset>/txt/.pantry'
        - Adds missing UDIMs from previous version.
        - creates json files in '<asset>/.pipeline' which determine the
        channels and versions available to each asset in each stream.
        """
        latest_rtt = sorted([x for x in os.listdir('.\\') if os.path.isfile('.\\' + x)
                             and '.py' in x and 'pipe_release_tool_txt' in x])[-1]
        self.store_last_job()

        c = f"{self.python_path} {latest_rtt} "
        self.check_for_outdated_packages()
        ReleaseTextures().create_ui_texture_release(self)
        #os.popen(c)
        #os.system(f'start cmd /K {c}')
    # TODO make class instead of independent script

    def start_release_animation(self):
        """ Launches new UI, which is used by animation
        - Creates folder structures.
        - Moves animation to versioned folder inside '<asset>/anm/.pantry'
        - creates json files in '<asset>/.pipeline'.
        """
        self.store_last_job()
        ReleaseAnim().create_ui_release_animation(self)

    def start_package_manager_texture(self):
        """ Launches new UI, which is used by texturing (and possibly shading).
        Manages json files in the '<asset>/.pipeline' directory generated by the texture releasing tool.

        - Allows roll back of texture channel versions without generating additional
        image files (Only 1kb json files.)
        - Allows connecting channels from other assets or variations to a specific asset
        variation without generating additional image files (Only 1kb json files.)
        """
        generate_paths(self)
        self.store_last_job()
        PackageManager().create_ui_package_manager(self)

    def start_connection_manager_texture(self):
        """ Launches new UI, which is used by texturing and shading.
        UI manages 'txt_connections.json file in the '<asset>/.pipeline' directory.

        This file is being used by the shading tools in blender to automatically
        connect specific channels to generated shaders. File won't be used once shading is published.

        UI mostly won't be needed as connections are made automatically according to the naming conventions
        handled in: './config/config_release_tool_txt.json'
        """
        latest_rtt = sorted([x for x in os.listdir('.\\') if os.path.isfile('.\\' + x)
                             and '.py' in x and 'pipe_connection_manager_txt' in x])[-1]
        self.store_last_job()
        c = f"{self.python_path} {latest_rtt} "
        os.popen(c)
        # os.system(f'start cmd /K {c}')

    def start_msr(self):
        """ Launches new UI, which can be used to rename multiple files.
        - Replace <UDIM> (Mari) and <u1_v1> (Mudbox) texture tile conventions.
        (Not present in most other renaming software, e.g. 'ReNamer')
        - Replace phrase.
        - Offset frame numbers.

        History: The name 'MundaneSequenceRenamer' is a reference to MPCs renaming tool which is called
        'SuperSequenceRenamer'. SSR uses a gigantic superhero image as 'apply' button and
        will play a superhero sound at maximum volume whenever you use it to rename a file.
        """
        latest_msr = sorted([x for x in os.listdir('.\\') if os.path.isfile('.\\' + x)
                             and '.py' in x and 'pipe_msr' in x])[-1]
        self.store_last_job()
        os.popen(f"{self.python_path} {latest_msr} ")

    def start_pull(self):
        self.store_last_job()
        self.check_for_outdated_packages()
        Pull().create_ui_pull(self)

    def start_publish(self):
        self.store_last_job()
        self.check_for_outdated_packages()
        try:
            Publish().create_ui_publish(self)
        except FileNotFoundError:
            messagebox.showinfo(title='', message="Asset does not contain any active versions.")

    def open_asset_dir(self):
        """Opens the directory of the asset currently selected in the dropdown."""
        self.store_last_job()
        root = self.current_root
        project = self.current_project_name
        department = self.current_department

        if department == 'build':
            asset = self.current_asset
            directory = os.path.join(root, project, 'build', asset)

        else:
            sequence = self.current_sequence
            shot = self.current_shot
            directory = os.path.join(root, project, 'sequences', sequence, shot)

        os.startfile(directory)

    def open_pantry_dir_mdl(self):
        """Opens the active mdl directory of the asset currently selected in the dropdown."""
        self.store_last_job()
        department = self.current_department

        failed = True
        if department == 'build':
            generate_paths(self)
            file_mdl_package = os.path.join(self.dir_pipeline_mdl, 'mdl_package.json')
            if os.path.isfile(file_mdl_package):
                with open(file_mdl_package, 'r') as json_file:
                    dict_mdl_package = json.load(json_file)

                active_mdl_version = dict_mdl_package[self.current_discipline]
                if active_mdl_version != '':
                    file_mdl_version = os.path.join(self.dir_pipeline_mdl, 'versions',
                                                    f'{self.current_asset}.{active_mdl_version}.json')
                    with open(file_mdl_version, 'r') as json_file:
                        dict_mdl_version = json.load(json_file)
                    version_cur = dict_mdl_version["version"]
                    failed = False
                    dir_pantry_version = os.path.join(self.dir_pantry_mdl, version_cur)
                    os.startfile(dir_pantry_version)

        if failed:
            messagebox.showinfo(title='', message="No active MDL version has been found for this stream.")

    def open_pantry_dir_txt(self):
        """Opens the active txt directory of the asset currently selected in the dropdown."""
        self.store_last_job()
        department = self.current_department

        failed = True
        if department == 'build':
            generate_paths(self)
            variations = os.listdir(self.dir_pipeline_txt)

            if len(variations) != 0:
                if len(variations) > 1:
                    question = MultipleChoice(self, 'TXT', 'Which TXT VARIATION would you like to open?', variations)
                    if question.result is not None:
                        variation = question.result
                    else:
                        variation = None
                else:
                    variation = 'A'
                if variation is not None:
                    # variation = question.result
                    dir_txt_package = os.path.join(self.dir_pipeline_txt, variation, 'txt_package')
                    channels = [x.split('.')[0] for x in os.listdir(dir_txt_package)
                                if os.path.isfile(os.path.join(dir_txt_package, x))]

                    question = MultipleChoice(self, 'Channel', 'Which CHANNEL would you like to open?', channels)

                    if question.result is not None:
                        channel = question.result
                        file_channel = os.path.join(dir_txt_package, f'{channel}.json')
                        with open(file_channel, 'r') as json_file:
                            json_content = json.load(json_file)
                        if 'asset' in json_content:
                            asset = json_content['asset']
                            variation = json_content['variation']
                            channel = json_content["channel"]
                            dir_txt_package = os.path.join(self.dir_build, asset, '.pipeline', 'txt',
                                                    variation, 'txt_package')
                            tmp_json = os.path.join(dir_txt_package, f'{channel}.json')
                            with open(tmp_json, 'r') as json_file:
                                json_content = json.load(json_file)
                                messagebox.showinfo('', 'Note that this texture is linked from another package.')
                        else:
                            asset = self.current_asset
                        json_version = json_content[self.current_discipline]

                        file_json_version = os.path.join(dir_txt_package, channel, f'{channel}.{json_version}.json')
                        with open(file_json_version, 'r') as json_file:
                            json_content = json.load(json_file)
                            dir_version = json_content['channel_version']

                        # dir_open = os.path.join(self.dir_pantry_txt, variation, channel, dir_version)
                        dir_open = os.path.join(self.dir_build, asset, 'txt', '.pantry',
                                                variation, channel, dir_version)

                        # file_txt_package = os.path.join(self.dir_pipeline_txt, question.result, 'shd_package.json')
                        failed = False
                        os.startfile(dir_open)

        if failed:
            try:
                if self.ui_child.winfo_exists():
                    messagebox.showinfo(title='', message="No active TXT version has been found "
                                                          "for this TXT variation in your stream.")
            except TclError:
                pass

    def open_pantry_dir_shd(self):
        """Opens the active shd directory of the asset currently selected in the dropdown."""
        self.store_last_job()
        department = self.current_department

        failed = True
        if department == 'build':
            generate_paths(self)

            variations = os.listdir(self.dir_pipeline_shd)

            if variations:

                if len(variations) > 1:
                    question = MultipleChoice(self, 'SHD', 'Which SHD variation would you like to open?', variations)
                    if question.result is not None:
                        variation = question.result
                    else:
                        variation = None
                else:
                    variation = 'A'
                if variation is not None:
                    file_shd_package = os.path.join(self.dir_pipeline_shd, variation, 'shd_package.json')
                    if os.path.isfile(file_shd_package):
                        with open(file_shd_package, 'r') as json_file:
                            dict_shd_package = json.load(json_file)

                        active_shd_version = dict_shd_package[self.current_discipline]
                        if active_shd_version != '':
                            file_version = os.path.join(self.dir_pipeline_shd, variation, 'versions',
                                                        f'{self.current_asset}.{active_shd_version}.json')
                            with open(file_version, 'r') as json_file:
                                dict_shd_version = json.load(json_file)

                            version_cur = dict_shd_version["version"]
                            failed = False
                            dir_pantry_version = os.path.join(self.dir_pantry_shd, variation, version_cur)
                            os.startfile(dir_pantry_version)

        if failed:
            try:
                if self.ui_child.winfo_exists():
                    messagebox.showinfo(title='', message="No active SHD version has been found "
                                                          "for this SHD variation in your stream.")
            except TclError:
                pass

    def store_last_job(self):
        """ Will store all settings (dropdowns and checkboxes) and store them in store them in a .json file.
        A separate file is generated for each user which can be accessed here:
        './userdata/<user>/last_job.json'
        The file is used to launch the UI with the same settings as when you left off.

        All settings are also set as temporary environment variables. This function is executed whenever
        a script/software is launched using the UI, allowing them to access all these
        settings without relying on the .json file.
        """
        asset = ''
        sequence = ''
        shot = ''
        if self.current_department == 'build':
            asset = self.current_asset
        else:  # self.current_department == 'sequence':
            sequence = self.current_sequence
            shot = self.current_shot

        dir_userdata = r'.\userdata'
        if os.path.isdir(dir_userdata) is False:
            os.makedirs(dir_userdata)

        dir_user = os.path.join(dir_userdata, self.user)
        if os.path.isdir(dir_user) is False:
            os.makedirs(dir_user)

        dict_last_job = {
            "project": self.current_project_name,
            "department": self.current_department,
            "discipline": self.current_discipline,
            "asset": asset,
            "sequence": sequence,
            "shot": shot,
            "software": self.current_software,
            "ocio": self.tkvar_ocio.get(),
            "top": self.tkvar_top.get()
        }
        file_last_job = os.path.join(dir_user, 'last_job.json')

        with open(file_last_job, 'w') as json_output:
            json.dump(dict_last_job, json_output, indent=2)

        os.putenv('PIPE_PYTHON_ROOT', os.path.abspath('./'))
        os.putenv('PIPE_PROJECT', self.current_project_name)
        os.putenv('PIPE_PROJECT_ABBR', [x.split('-')[1] for x in self.projects
                                        if self.current_project_name == x.split('-')[0]][0])
        os.putenv('PIPE_DEPARTMENT', self.current_department)
        os.putenv('PIPE_DISCIPLINE', self.current_discipline)
        os.putenv('PIPE_ASSET', asset)
        os.putenv('PIPE_SEQUENCE', sequence)
        os.putenv('PIPE_SHOT', shot)
        os.putenv('PIPE_ROOT', self.current_root)

    def load_last_job(self):
        """ Executed when the pipeline is launched. Will set all dropdowns and checkboxes
        according to the json file saved by the 'store_last_job' function.
        Uses './userdata/<user>/last_job.json' file.
        """

        all_projects = [x for x in os.listdir(r'.\projects\\') if os.path.isdir(f'.\\projects\\{x}')]

        if len(all_projects) > 0:
            self.current_project_name = all_projects[0]
            self.current_department = 'build'  # gets overriden later on
            self.current_discipline = 'mdl'

            with open(f'.\\projects\\{self.current_project_name}\\{self.current_project_name}.json', 'r') as cfg_file:
                config_file_content = json.load(cfg_file)
            self.current_root = config_file_content["root"]
            dir_build = get_build_dir(self.current_root, self.current_project_name)

        else:
            self.current_department = 'build'
            self.current_discipline = 'mdl'
            self.current_project_name = ''
            self.current_asset = ''
            self.current_software = ''

        dir_userdata = r'.\userdata'
        if os.path.isdir(dir_userdata):
            dir_user = os.path.join(dir_userdata, self.user)
            if os.path.isdir(dir_user):
                config = os.path.join(dir_user, 'last_job.json')
                if os.path.isfile(config):
                    with open(config, 'r') as config_file:
                        config_file_content = json.load(config_file)
                        self.switch_project(config_file_content["project"])
                        self.switch_department(config_file_content["department"])
                        self.switch_discipline(config_file_content["discipline"])
                        asset = config_file_content["asset"]
                        sequence = config_file_content["sequence"]
                        shot = config_file_content["shot"]
                        self.switch_software(config_file_content["software"])
                        self.tkvar_ocio.set(config_file_content["ocio"])
                        self.tkvar_top.set(config_file_content["top"])
                        self.ui_toggle_on_top()

                        if len(asset):
                            self.switch_asset(asset)
                        if len(sequence) & len(shot):
                            self.switch_sequence(sequence)
                            self.switch_shot(shot)

    def switch_project(self, project):
        """ Executed when project is selected from the project dropdown.
        - updates text of dropdown
        - updates multiple variables used by other functions according to the config file
        of the project and updates the text of the dropdown.
        - updates list of software available in the software dropdown.

        :param project: name of the project (without abbreviation)
        """
        for index, project_name in enumerate(self.project_names):
            if project == project_name:
                target = f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json'
                with open(target, 'r') as config_file:
                    config_file_content = json.load(config_file)
                break

        root = config_file_content["root"]
        dict_software = config_file_content["software"]
        ocio_default = config_file_content["ocio"]

        self.get_project_root()
        # self.dir_build = '/'.join([root, project, 'build'])

        project_switch_success = True

        bg = self.col_bt_petrol
        abg = self.col_bt_petrol_highlight

        if os.path.isdir(self.dir_build) is False:
            if self.initialise is None:
                bg = self.col_bt_red
                abg = self.col_bt_red_highlight
            else:
                msg = messagebox.askquestion(
                    f'Create Project directory >>{ project }<< not found.\nDo you want to create it?'
                )
                if msg == 'yes':
                    create_folder_structure(project, root)
                else:
                    project_switch_success = False

                    msg = messagebox.askquestion('Create',
                                                 'To you want to edit the project config instead?')
                    if msg == 'yes':
                        for project_name in self.project_names:
                            if project == project_name:
                                index = self.project_names.index(project_name)
                                ProjectCreator().create_ui(f'.\\projects\\{self.projects[index]}'
                                                           f'\\{self.projects[index]}.json')
                                break

        # TODO NEEDS TO LAUNCH PROJECT EDITOR SO THAT CONFIG CAN BE ADJUSTED TO FIND THE PROJECT

        if project_switch_success:
            self.dd_projects.configure(text=project, bg=bg, activebackground=abg)
            self.current_project_name = project
            self.ui_create_elements_asset_row()

            self.current_root = root
            self.dict_software = dict_software
            self.ocio_default = ocio_default
            self.ui_create_elements_software()

            self.initialise = True

    def switch_department(self, department):
        """ Executed when a department is selected from the department dropdown.
        - updates text of dropdown
        - updates variable used by other functions
        - triggers 'ui_create_elements_asset' function which reiterates the 'asset'/'shot' selection row

        :param department: The name of the department selected from the dropdown. Either 'build' or 'shot'.
        """
        self.dd_department.configure(text=department)
        self.current_department = department
        self.ui_create_elements_discipline()
        self.ui_create_elements_asset_row()

        if self.current_department == 'build':
            self.switch_asset(self.current_asset)

        self.disable_unqualified_tools()

    def switch_discipline(self, discipline):
        """ Executed when a discipline is selected from the discipline dropdown.
        - updates text of dropdown
        - updates variable used by other functions

        :param discipline: The name of the discipline selected from the dropdown. Either 'build' or 'shot'.
        """
        self.dd_discipline.configure(text=discipline)
        self.current_discipline = discipline

        self.check_for_outdated_packages()
        self.disable_unqualified_tools()

    def switch_asset(self, asset):
        """ Executed when an asset is selected from the asset dropdown.
        - updates text of the dropdown
        - updates variable used by other functions

        :param asset: Name of the asset selected from the dropdown.
        """
        #self.dd_asset.configure(text=asset)
        self.dd_asset_test.configure(text=asset)
        self.current_asset = asset
        if self.current_asset in self.assets:
            self.check_for_outdated_packages()
            self.disable_unqualified_tools()
        else:
            #self.dd_asset.configure(text='')
            self.dd_asset_test.configure(text='')
            self.disable_unqualified_tools()

    def switch_sequence(self, sequence):
        """Executed when an asset is selected from the asset dropdown.
        - updates text of the dropdown
        - updates variable used by other functions

        :param sequence: Name of the sequence selected from the dropdown.
        """
        self.dd_sequence.configure(text=sequence)
        self.current_sequence = sequence
        self.ui_dd_shot(self.current_root, 3)
        self.check_for_outdated_packages()
        self.disable_unqualified_tools()

    def switch_shot(self, shot):
        """Executed when an asset is selected from the asset dropdown.
        - updates text of the dropdown
        - updates variable used by other functions

        :param shot: Name of the shot selected from the dropdown.
        """
        self.dd_shot.configure(text=shot)
        self.current_shot = shot
        self.check_for_outdated_packages()
        self.disable_unqualified_tools()

    def switch_software(self, software):
        """Executed when an software is selected from the software dropdown.
        - updates text of the dropdown
        - updates variable used by other functions

        :param software: Name of the software selected from the dropdown
        """
        self.current_software = software
        #self.dd_software.configure(text=software)
        self.dd_software_redo.configure(text=software)

        try:
            state = NORMAL if self.dict_software[software]["support"] else DISABLED
            self.cb_ocio.configure(state=state)
        except:
            pass

    def disable_unqualified_tools(self):
        """Disables certain buttons if the required directories and json file don't exist."""
        if self.current_asset not in self.assets:  # Asset not found / no asset
            self.bt_package.configure(state=DISABLED)
            self.dd_discipline.configure(state=DISABLED)
            self.bt_pull.configure(state=DISABLED)
            self.bt_publish.configure(state=DISABLED)
            self.bt_check.configure(state=DISABLED)
            self.bt_connections.configure(state=DISABLED)
            self.bt_rtt.configure(state=DISABLED)
            self.bt_launch.configure(state=DISABLED)
            self.bt_pantry_mdl.configure(state=DISABLED)
            self.bt_pantry_txt.configure(state=DISABLED)
            self.bt_pantry_shd.configure(state=DISABLED)
            self.bt_directory.configure(state=DISABLED)
            self.bt_asset_edit.configure(state=DISABLED)
        else:
            self.bt_package.configure(state=NORMAL)
            self.dd_discipline.configure(state=NORMAL)
            self.bt_connections.configure(state=NORMAL)
            self.bt_rtt.configure(state=NORMAL)
            self.bt_launch.configure(state=NORMAL)
            if self.current_department == "build":
                self.bt_check.configure(state=NORMAL)
                self.bt_pull.configure(state=NORMAL)
                self.bt_publish.configure(state=NORMAL)
                self.bt_pantry_mdl.configure(state=NORMAL)
                self.bt_pantry_txt.configure(state=NORMAL)
                self.bt_pantry_shd.configure(state=NORMAL)
                # self.bt_asset_edit.configure(state=NORMAL)
                # self.bt_directory.configure(state=NORMAL)
            else:
                self.bt_check.configure(state=DISABLED)
                self.bt_pull.configure(state=DISABLED)
                self.bt_publish.configure(state=DISABLED)
                self.bt_pantry_mdl.configure(state=DISABLED)
                self.bt_pantry_txt.configure(state=DISABLED)
                self.bt_pantry_shd.configure(state=DISABLED)

        if self.dir_pipeline_txt is None:
            self.bt_connections.configure(state=DISABLED)
            self.bt_publish.configure(state=DISABLED)
            self.bt_rtt.configure(state=DISABLED)
            self.bt_pull.configure(state=DISABLED)
            self.bt_package.configure(state=DISABLED)
            self.bt_check.configure(state=DISABLED)
            if self.current_department == 'build':
                # self.dd_asset.configure(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)
                self.dd_asset_test.configure(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)

        else:
            self.bt_package.configure(state=NORMAL)
            if self.current_department == 'build':
                self.bt_check.configure(state=NORMAL)
                self.bt_publish.configure(state=NORMAL)
                self.bt_pull.configure(state=NORMAL)
                #self.dd_asset.configure(bg=self.col_bt_petrol, activebackground=self.col_bt_petrol_highlight)
                self.dd_asset_test.configure(bg=self.col_bt_petrol, activebackground=self.col_bt_petrol_highlight)

            if self.current_discipline == 'txt':
                self.bt_connections.config(state=NORMAL)
                self.bt_rtt.config(state=NORMAL, command=lambda: self.start_release_texture())

            elif self.current_discipline == 'anm':
                self.bt_rtt.config(state=NORMAL, command=lambda: self.start_release_animation())

            elif self.current_discipline == 'shd':
                self.bt_connections.config(state=NORMAL)
                self.bt_rtt.config(state=DISABLED)

            else:
                self.bt_connections.config(state=DISABLED)
                self.bt_rtt.config(state=DISABLED)

    # TODO change colour of asset dd if it doesn't exist

    def project_config_edit(self):
        """Launches a variation of the ProjectCreator UI that has preloaded the config of the
        currently selected project.

        :return:
        """
        for project_name in self.project_names:
            if self.current_project_name == project_name:
                index = self.project_names.index(project_name)
                ProjectCreator().create_ui(f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json')
                break

    def project_config_duplicate(self):
        """Launches ProjectDuplicator UI (part of './pipe_utils.py').
        This UI allows you to duplicate the configuration of the currently selected project.
        The content of the project itself will not be duplicated.

        :return:
        """
        for project_name in self.project_names:
            if self.current_project_name == project_name:
                index = self.project_names.index(project_name)
                ProjectDuplicator().create_ui(f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json', self)
                break

    def asset_edit(self):
        """Launches AssetCreator UI in edit mode. (part of './pipe_utils.py')
        This UI allows you to edit the name and type of the selected asset.
        """

        for project_name in self.project_names:
            if self.current_project_name == project_name:
                """index = self.project_names.index(project_name)
                target = f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json'

                with open(target, 'r') as config_file:
                    config_file_content = json.load(config_file)
                    name = config_file_content["name"]
                    root = config_file_content["root"]

                dir_build = os.path.join(root, name, 'build')"""
                AssetCreator(True).create_ui(self.dir_build, self)
                break

    def asset_create(self):
        """Launches AssetCreator UI (part of './pipe_utils.py').
        This UI allows you to create a new asset directory, including its subdirectories.
        """
        for project_name in self.project_names:
            if self.current_project_name == project_name:
                """index = self.project_names.index(project_name)
                target = f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json'

                with open(target, 'r') as config_file:
                    config_file_content = json.load(config_file)
                    name = config_file_content["name"]
                    root = config_file_content["root"]

                dir_build = os.path.join(root, name, 'build')"""
                AssetCreator(False).create_ui(self.dir_build, self)
                break

    def move_window_offset(self, event):
        """Saves the current offset of the cursor in relation to the window.

        :param event: clicking on the title-bar
        :return:
        """
        window_x = self.ui_child.winfo_x()
        window_y = self.ui_child.winfo_y()
        cursor_x = event.x_root
        cursor_y = event.y_root
        self.x_offset = cursor_x - window_x
        self.y_offset = cursor_y - window_y

    def move_window(self, event):
        """ Moves the window when the title-bar is clicked

        :param event: clicking and holding the title-bar
        :return:
        """
        x_new = event.x_root-self.x_offset
        y_new = event.y_root-self.y_offset
        self.ui_child.geometry(f'+{x_new}+{y_new}')

    def on_root_deiconify(self, _):
        """ Hides the proxy window again immediately after it is deiconified.

        :param _: Throwaway event variable.
        :return:
        """
        self.ui_child.withdraw()
        self.ui_child.deiconify()
        self.ui_proxy.iconify()

    def dd_ui(self, bt, options):
        Dropdown(self, bt, options).create_ui_dropdown()
        #Pull().create_ui_pull(self)

    def on_dd_enter(self, e):
        e.widget['background'] = self.col_ui_dd_default_highlight

    def on_dd_leave(self, e):
        e.widget['background'] = self.col_ui_dd_default

    def on_bt_enter(self, e):
        e.widget['background'] = self.col_bt_bg_blue_highlight

    def on_bt_leave(self, e):
        e.widget['background'] = self.col_bt_bg_blue

    def on_bt_enter_red(self, e):
        e.widget['background'] = self.col_bt_red_highlight

    def on_bt_leave_red(self, e):
        e.widget['background'] = self.col_bt_red

    def ui_create_elements_discipline(self):
        if self.ui_elements_discipline is not None:
            for element in self.ui_elements_discipline:
                element.destroy()

        if self.current_department == 'build':
            self.current_discipline = 'mdl'
            self.dd_discipline = Menubutton(self.frame_asset, text=self.current_discipline,
                                            width=4, bg=self.col_ui_dd_default, fg=self.col_bt_fg_default,
                                            highlightthickness=0, activebackground=self.col_ui_dd_default_highlight,
                                            anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                            relief=self.def_bt_relief, justify=RIGHT)
            self.dd_discipline.menu = Menu(self.dd_discipline, tearoff=0, bd=0, activeborderwidth=3,
                                           relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                           activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                           activebackground=self.col_bt_bg_blue_highlight)
            self.dd_discipline['menu'] = self.dd_discipline.menu

            self.dd_discipline.menu.add_command(label='mdl', command=lambda: self.switch_discipline('mdl'))
            self.dd_discipline.menu.add_command(label='txt', command=lambda: self.switch_discipline('txt'))
            self.dd_discipline.menu.add_command(label='shd', command=lambda: self.switch_discipline('shd'))
            self.dd_discipline.menu.add_command(label='anm', command=lambda: self.switch_discipline('anm'))

            self.dd_discipline.grid(row=0, column=4, columnspan=1, sticky=EW, padx=self.default_padding,
                                    pady=self.default_padding)
            CreateToolTip(
                self.dd_discipline,
                "Your discipline has an effect on the availability and functionality of "
                "other pipeline tools.\n\n"
                "mdl = modeling\n"
                "txt = texturing\n"
                "shd = shading",
                self.col_ui_dd_default_highlight,
                self.col_ui_dd_default
            )
            self.ui_elements_discipline = [self.dd_discipline]

        elif self.current_department == 'sequence':
            self.current_discipline = 'sht'
            self.dd_discipline = Menubutton(
                self.frame_asset, text=self.current_discipline, width=4, bg=self.col_ui_dd_default,
                fg=self.col_bt_fg_default, highlightthickness=0, activebackground=self.col_ui_dd_default_highlight,
                anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                relief=self.def_bt_relief, justify=RIGHT
            )
            self.dd_discipline.menu = Menu(
                self.dd_discipline, tearoff=0, bd=0, activeborderwidth=3,
                relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                activebackground=self.col_bt_bg_blue_highlight
            )
            self.dd_discipline['menu'] = self.dd_discipline.menu

            self.dd_discipline.menu.add_command(label='sht', command=lambda: self.switch_discipline('sht'))

            self.dd_discipline.grid(
                row=0, column=4, columnspan=1, sticky=EW, padx=self.default_padding, pady=self.default_padding
            )
            CreateToolTip(
                self.dd_discipline,
                "Your discipline has an effect on the availability and functionality of other pipeline tools.\n\n"
                + "sht = shot",
                self.col_ui_dd_default_highlight,
                self.col_ui_dd_default
            )
            self.ui_elements_discipline = [self.dd_discipline]

    def update_dropdowns(self):
        try:  # dropdown might no longer exist if in sequence department
            self.switch_asset(self.dd_asset_test.cget('text'))
        except TclError:
            pass
        self.switch_software(self.dd_software_redo.cget('text'))

    def get_project_root(self):
        """Checks for root directory of the project stored in self.current_project_name."""
        self.current_root = None  # load project config # self.root =
        for project_name in self.project_names:
            if self.current_project_name == project_name:
                index = self.project_names.index(project_name)
                config = os.path.join('.', 'projects', self.projects[index], f'{self.projects[index]}.json')
                # config = f'.\\projects\\{self.projects[index]}\\{self.projects[index]}.json'

                with open(config, 'r') as config_file:
                    config_file_content = json.load(config_file)
                    self.current_root = config_file_content["root"]  # self.root =

                self.dir_build = get_build_dir(self.current_root, self.current_project_name)  # self.root
                self.dir_sequences = os.path.join(self.current_root, self.current_project_name, 'sequences')  # self.root

                break

    def ui_create_elements_asset_row(self):
        """ Called from init. Launches the main UI of this script.

        :return:
        """
        row_asset = 3
        if self.ui_elements_asset is not None:
            for element in self.ui_elements_asset:
                element.destroy()
            self.ui_elements_asset = None

        if self.current_project_name != '':
            self.get_project_root()
            if self.current_department == 'build':
                # ---------------------------------------------------------------------------------------------
                lbl_asset = Label(self.frame_asset, bd=1, text='Asset',
                                  bg=self.col_wdw_default, fg=self.col_bt_fg_default)
                lbl_asset.grid(row=row_asset, column=0, padx=self.default_padding, pady=self.default_padding)
                # ---------------------------------------------------------------------------------------------
                self.assets = list_assets(self.current_root, self.dir_build)  # self.root

                if len(self.assets) == 0:
                    self.current_asset = ''
                else:
                    self.current_asset = self.assets[0]

                """self.dd_asset = Menubutton(self.frame_asset, text=self.current_asset,
                                           bg=self.col_ui_dd_default, fg=self.col_bt_fg_default,
                                           highlightthickness=0,
                                           activebackground=self.col_ui_dd_default_highlight,
                                           anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                           relief=self.def_bt_relief, justify=RIGHT)
                self.dd_asset.menu = Menu(self.dd_asset, tearoff=0, bd=0, activeborderwidth=3,
                                          relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                          activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                          activebackground=self.col_bt_bg_blue_highlight)
                self.dd_asset['menu'] = self.dd_asset.menu
                self.assets.sort()
                for asset in self.assets:
                    self.dd_asset.menu.add_command(label=asset, command=lambda x=asset: self.switch_asset(x))
                
                self.dd_asset.grid(row=row_asset, column=1, columnspan=1, sticky=EW, padx=self.default_padding,
                                   pady=self.default_padding)"""

                self.assets.sort()
                self.dd_asset_test = Button(
                    self.frame_asset, text="", bg=self.col_ui_dd_default, anchor=W, fg=self.col_bt_fg_default,
                    relief=self.def_bt_relief, bd=1
                )
                self.dd_asset_test.configure(
                    command=lambda bt=self.dd_asset_test, options=self.assets: self.dd_ui(bt, options)
                )
                self.dd_asset_test.grid(row=row_asset, column=1, columnspan=1, sticky=EW, padx=self.default_padding,
                                        pady=self.default_padding)

                self.dd_asset_test.bind('<Enter>', self.on_dd_enter)
                self.dd_asset_test.bind('<Leave>', self.on_dd_leave)
                #self.dd_asset_test.bind('<Configure>', self.update_dropdowns)

                # ---------------------------------------------------------------------------------------------
                self.bt_directory = Button(self.frame_asset, text='dir', border=self.default_bt_bd,
                                           bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                           activebackground=self.col_bt_bg_active,
                                           activeforeground=self.col_bt_fg_default,
                                           command=lambda: self.open_asset_dir())

                self.bt_directory.grid(
                    row=row_asset, column=2, columnspan=1, sticky=NSEW,
                    padx=self.default_padding, pady=self.default_padding
                )

                CreateToolTip(
                    self.bt_directory, "Opens the selected asset's directory", self.col_bt_bg_default_highlight,
                    self.col_bt_bg_default
                )
                # ---------------------------------------------------------------------------------------------
                self.bt_asset_edit = Button(self.frame_asset, image=self.icon_edit, height=1, bg=self.col_ui_bt_small,
                                            fg=self.col_bt_fg_default,
                                            activebackground=self.col_ui_bt_small_highlight,
                                            activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                            bd=self.default_bt_bd, relief=self.def_bt_relief,
                                            command=lambda: self.asset_edit())
                self.bt_asset_edit.grid(row=row_asset, column=3, sticky=NSEW, padx=self.default_padding,
                                        pady=self.default_padding)
                CreateToolTip(
                    self.bt_asset_edit,
                    "UI which allows you to edit the name and category of the asset currently selected.",
                    self.col_bt_bg_default_highlight,
                    self.col_bt_bg_default
                )
                # ---------------------------------------------------------------------------------------------

                bt_asset_create = Button(self.frame_asset, text='+', width=3, image=self.icon_create,
                                         bg=self.col_ui_bt_small,
                                         fg=self.col_bt_fg_default, activebackground=self.col_ui_bt_small_highlight,
                                         activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                         bd=self.default_bt_bd, relief=self.def_bt_relief, justify=CENTER,
                                         command=lambda: self.asset_create())
                bt_asset_create.grid(row=row_asset, column=4, sticky=NSEW, padx=self.default_padding,
                                     pady=self.default_padding)
                CreateToolTip(
                    bt_asset_create,
                    "UI which allows you to create a new asset directory, "
                    "including its subdirectories.",
                    self.col_bt_bg_default_highlight, self.col_bt_bg_default
                )

                self.ui_elements_asset = [
                    lbl_asset,
                    self.dd_asset_test,
                    bt_asset_create,
                    self.bt_directory,
                    self.bt_asset_edit
                ]
                # , bt_asset_edit]

            elif self.current_department == 'sequence':
                # ---------------------------------------------------------------------------------------------
                lbl_seq = Label(self.frame_asset, bd=1, text='Sq/Sh',
                                bg=self.col_wdw_default, fg=self.col_bt_fg_default)
                lbl_seq.grid(row=row_asset, column=0, padx=self.default_padding, pady=self.default_padding)
                CreateToolTip(lbl_seq, "Sequence & Shot", None, None, False)
                # ---------------------------------------------------------------------------------------------
                # ---------------------------------------------------------------------------------------------
                self.bt_directory = Button(self.frame_asset, text='dir', border=self.default_bt_bd,
                                           bg=self.col_bt_bg_default, fg=self.col_bt_fg_default,
                                           relief=self.def_bt_relief,
                                           activebackground=self.col_bt_bg_active,
                                           activeforeground=self.col_bt_fg_default,
                                           command=lambda: self.open_asset_dir())

                self.bt_directory.grid(
                    row=row_asset, column=2, columnspan=2, sticky=NSEW,
                    padx=self.default_padding, pady=self.default_padding
                )
                # ---------------------------------------------------------------------------------------------
                if self.current_root is not None:  # self.root
                    # seq_path = '/'.join([self.root, self.current_project_name, 'sequences'])
                    if os.path.isdir(self.dir_sequences) is False:
                        self.sequences = []
                    else:
                        self.sequences = os.listdir(self.dir_sequences)
                else:
                    self.sequences = []

                if len(self.sequences) == 0:
                    self.current_sequence = ''
                else:
                    self.current_sequence = self.sequences[0]

                self.frame_sequence = Frame(self.frame_asset, bg=self.col_wdw_default)
                self.frame_sequence.grid(row=row_asset, column=1, columnspan=1, sticky=NSEW)
                self.frame_sequence.columnconfigure(0, weight=1)

                self.dd_sequence = Menubutton(self.frame_sequence, text=self.current_sequence,
                                              bg=self.col_ui_dd_default, fg=self.col_bt_fg_default,
                                              highlightthickness=0,
                                              activebackground=self.col_ui_dd_default_highlight,
                                              anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                              relief=self.def_bt_relief, justify=RIGHT)
                self.dd_sequence.menu = Menu(self.dd_sequence, tearoff=0, bd=0, activeborderwidth=3,
                                             relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                             activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                             activebackground=self.col_bt_bg_blue_highlight)
                self.dd_sequence['menu'] = self.dd_sequence.menu
                CreateToolTip(self.dd_sequence, "Sequence", self.col_ui_dd_default_highlight, self.col_ui_dd_default)
                self.sequences.sort()

                for sequence in self.sequences:
                    self.dd_sequence.menu.add_command(label=sequence,
                                                      command=lambda x=sequence: self.switch_sequence(x))
                self.dd_sequence.grid(row=row_asset, column=0, columnspan=1, padx=self.default_padding, sticky=NSEW,
                                      pady=self.default_padding)

                # --- Shots --------------------------------------------------------------------------------------
                dd_shot = self.ui_dd_shot(self.current_root, row_asset)  # self.root

                # --- Buttons ------------------------------------------------------------------------------------
                bt_create_shot = Button(
                    self.frame_asset, image=self.icon_create, bg=self.col_ui_bt_small, fg=self.col_bt_fg_default,
                    activebackground=self.col_ui_bt_small_highlight, activeforeground=self.col_bt_fg_default,
                    highlightthickness=0, bd=self.default_bt_bd, relief=self.def_bt_relief, justify=CENTER,
                    command=lambda: ShotCreator(False).create_ui(self)
                )
                bt_create_shot.grid(
                    row=row_asset, column=4, sticky=NSEW, padx=self.default_padding, pady=self.default_padding
                )
                self.ui_elements_asset = [
                    lbl_seq, self.dd_sequence, dd_shot, self.frame_sequence, bt_create_shot, self.bt_directory
                ]

    # TODO Discipline Layout/Shot
    # TODO layout needs to delete shot dropdown and only keep sequence dropdown
    # TODO last shot needs to be stored
    # TODO shot creation tool

    def ui_dd_shot(self, root, row_asset):
        if self.dd_shot is not None:
            self.dd_shot.destroy()

        if root is not None and self.current_sequence != '':
            # sequence_path = '/'.join([root, self.current_project_name, 'sequences', self.current_sequence])
            dir_sequence = os.path.join(self.dir_sequences, self.current_sequence)
            shots = [x for x in os.listdir(dir_sequence) if x != '.pipeline']

            shots.sort()
            if 'layout' in shots:
                shots.insert(0, shots.pop(shots.index('layout')))
            self.current_shot = shots[0]
        else:
            shots = []
            self.current_shot = ''

        self.dd_shot = Menubutton(self.frame_sequence, text=self.current_shot, width=6,
                                  bg=self.col_ui_dd_default, fg=self.col_bt_fg_default,
                                  highlightthickness=0,
                                  activebackground=self.col_ui_dd_default_highlight,
                                  anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                  relief=self.def_bt_relief, justify=RIGHT)
        self.dd_shot.menu = Menu(self.dd_shot, tearoff=0, bd=0, activeborderwidth=3,
                                 relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                 activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                 activebackground=self.col_bt_bg_blue_highlight)
        self.dd_shot['menu'] = self.dd_shot.menu
        CreateToolTip(
            self.dd_shot,
            "Shot",
            self.col_ui_dd_default_highlight,
            self.col_ui_dd_default
        )
        for shot in shots:
            self.dd_shot.menu.add_command(label=shot,
                                          command=lambda x=shot: self.switch_shot(x))
        self.dd_shot.grid(row=row_asset, column=1, columnspan=1, sticky=NSEW, padx=self.default_padding,
                          pady=self.default_padding)

        return self.dd_shot

    def ui_create_elements_software(self):
        #if self.dd_software is not None:
        #    self.dd_software.destroy()
        if self.dd_software_redo is not None:
            self.dd_software_redo.destroy()

        list_software = list(self.dict_software.keys())
        self.current_software = list_software[0]
        state = NORMAL if self.dict_software[self.current_software]["support"] else DISABLED
        """self.dd_software = Menubutton(
            self.frame_launcher, text=self.current_software, bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
            highlightthickness=0, activebackground=self.col_bt_bg_blue_highlight, anchor=W,
            activeforeground=self.col_bt_fg_default, bd=1, relief=self.def_bt_relief
        )
        self.dd_software.menu = Menu(
            self.dd_software, tearoff=0, bd=0, activeborderwidth=3, relief=self.def_bt_relief,
            bg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
            activebackground=self.col_bt_bg_blue_highlight, fg=self.col_bt_bg_default
        )
        self.dd_software['menu'] = self.dd_software.menu

        self.dd_software.config(bg=self.col_bt_petrol, activebackground=self.col_bt_petrol_highlight)
        for key in list_software:
            self.dd_software.menu.add_command(label=key, command=lambda x=key: self.switch_software(x))

        self.dd_software.grid(row=0, column=0, columnspan=2, sticky=EW, padx=self.default_padding,
                              pady=self.default_padding)"""
        self.dd_software_redo = Button(
            self.frame_launcher, text=self.current_software, bg=self.col_ui_dd_default,
            anchor=W, fg=self.col_bt_fg_default, relief=self.def_bt_relief, bd=1#, state=state
        )
        self.dd_software_redo.configure(
            command=lambda bt=self.dd_software_redo, options=sorted(list_software):
            self.dd_ui(bt, options)
        )
        self.dd_software_redo.grid(
            row=0, column=0, columnspan=2, sticky=EW, padx=self.default_padding,
            pady=self.default_padding)

        self.dd_software_redo.bind('<Enter>', self.on_dd_enter)
        self.dd_software_redo.bind('<Leave>', self.on_dd_leave)
        # … 0133
        # τ 231 2023
        # ‣
        # ·250

        self.frame_launcher.grid_columnconfigure(0, weight=1)
        # --- OCIO Boolean ----------------------------------------------------------------------------
        self.tkvar_ocio = BooleanVar()
        self.tkvar_ocio.set(True)
        self.cb_ocio = Checkbutton(self.frame_launcher, text='OCIO', var=self.tkvar_ocio, state=state,
                                   bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                   fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                   selectcolor=self.col_bt_bg_active)
        self.cb_ocio.grid(row=1, column=0, sticky=W, padx=self.default_padding-1, pady=self.default_padding)
        CreateToolTip(
            self.cb_ocio,
            "enabled = uses OCIO defined in the project config\n\n"
            "disabled = manual override - no OCIO",
            None, None, False
        )
        # --- Launch button ---------------------------------------------------------------------------
        self.bt_launch = Button(self.frame_launcher, text='Launch Software', width=14, bg=self.col_bt_bg_blue, pady=3,
                                fg=self.col_bt_fg_default,
                                activebackground=self.col_bt_bg_blue_highlight, activeforeground=self.col_bt_fg_default,
                                highlightthickness=0, bd=self.default_bt_bd, relief=self.def_bt_relief,
                                command=lambda: self.launch_software())
        self.bt_launch.grid(row=1, column=1, rowspan=1, sticky=NSEW, padx=self.default_padding,
                            pady=self.default_padding)

        self.bt_launch.bind('<Enter>', self.on_bt_enter)
        self.bt_launch.bind('<Leave>', self.on_bt_leave)
        # ---------------------------------------------------------------------------------------------

    def ui_toggle_on_top(self):
        """ Belongs to the 'always on top' checkbox. Allows to enable and disable whether the software
        should always be on top of other applications.

        :return:
        """
        if self.tkvar_top.get():
            self.main_ui.wm_attributes("-topmost", 1)
        else:
            self.main_ui.wm_attributes("-topmost", 0)

    def check_for_outdated_packages(self):
        """ Checks if pulling or publishing is required.

        :return:
        """

        generate_paths(self)

        # pull
        list_updates = pull_required(self)
        updates = 0

        if list_updates['mdl'] is not None:
            updates += 1
        if len(list_updates['anm']) > 0:
            for _ in list_updates['anm']:
                updates += 1
        if len(list_updates['txt']) > 0:
            for _ in list_updates['txt']:
                updates += 1
        if len(list_updates['shd']) > 0:
            for _ in list_updates['shd']:
                updates += 1

        if updates > 0:
            self.bt_pull.config(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)
            self.bt_pull.bind('<Enter>', self.on_bt_enter_red)
            self.bt_pull.bind('<Leave>', self.on_bt_leave_red)
        else:
            self.bt_pull.config(bg=self.col_bt_bg_blue, activebackground=self.col_bt_bg_blue_highlight)
            self.bt_pull.bind('<Enter>', self.on_bt_enter)
            self.bt_pull.bind('<Leave>', self.on_bt_leave)

        # mdl publish
        if self.current_discipline == 'mdl':
            if publish_required_mdl(self):
                self.bt_publish.config(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter_red)
                self.bt_publish.bind('<Leave>', self.on_bt_leave_red)
            else:
                self.bt_publish.config(bg=self.col_bt_bg_blue, activebackground=self.col_bt_bg_blue_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter)
                self.bt_publish.bind('<Leave>', self.on_bt_leave)

        # txt publish
        if self.current_discipline == 'txt':
            list_txt_publish = publish_required_txt(self)
            if len(list_txt_publish) != 0:
                self.bt_publish.config(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter_red)
                self.bt_publish.bind('<Leave>', self.on_bt_leave_red)
            else:
                self.bt_publish.config(bg=self.col_bt_bg_blue, activebackground=self.col_bt_bg_blue_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter)
                self.bt_publish.bind('<Leave>', self.on_bt_leave)

        # shd publish
        if self.current_discipline == 'shd':
            if len(publish_required_shd(self)) != 0:
                self.bt_publish.config(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter_red)
                self.bt_publish.bind('<Leave>', self.on_bt_leave_red)
            else:
                self.bt_publish.config(bg=self.col_bt_bg_blue, activebackground=self.col_bt_bg_blue_highlight)
                self.bt_publish.bind('<Enter>', self.on_bt_enter)
                self.bt_publish.bind('<Leave>', self.on_bt_leave)

        # Texture release colour
        has_files = False
        if self.current_discipline == 'txt':
            variations = os.listdir(self.dir_export_txt)
            for var in variations:
                dir_var = os.path.join(self.dir_export_txt, var)
                files_of_var = [x for x in os.listdir(dir_var) if os.path.isfile(os.path.join(dir_var, x))]
                if len(files_of_var) != 0:
                    has_files = True
                    break
        if has_files:
            self.bt_rtt.config(bg=self.col_bt_red, activebackground=self.col_bt_red_highlight)

            CreateToolTip(
                self.bt_rtt,
                "Tool that automatically moves textures into the correct channel and "
                "version directory.\n<asset>/txt/.pantry/<XvX>/<channel>/<version>\n\n"
                "Also creates json files referencing these textures, which allows "
                "other pipeline functionalities like texture rollback,automatic "
                "shader connections and separate active texture version for each "
                "stream/discipline\n\n"
                "(json files are located in '<asset>/.pipeline')\n\n"
                "(directories starting with a dot are hidden and shouldn't be touched "
                "by the artists)",
                self.col_bt_red_highlight,
                self.col_bt_red
            )
        else:
            self.bt_rtt.config(bg=self.col_bt_bg_blue, activebackground=self.col_bt_bg_blue_highlight)

            CreateToolTip(
                self.bt_rtt,
                "Tool that automatically moves textures into the correct channel and "
                "version directory.\n<asset>/txt/.pantry/<XvX>/<channel>/<version>\n\n"
                "Also creates json files referencing these textures, which allows "
                "other pipeline functionalities like texture rollback,automatic "
                "shader connections and separate active texture version for each "
                "stream/discipline\n\n"
                "(json files are located in '<asset>/.pipeline')\n\n"
                "(directories starting with a dot are hidden and shouldn't be touched "
                "by the artists)",
                self.col_bt_bg_blue_highlight,
                self.col_bt_bg_blue
            )

    def event_tick(self):
        """ Currently unused. Ticks once a minute. Could be used to continuously check for package updates.

        :return:
        """
        self.check_for_outdated_packages()
        self.ui_child.after(60000, self.event_tick)

    def create_main_ui(self):
        """ Main function which sets up the UI and triggers all other required functions.

        :return:
        """

        # --- Spacing defaults
        dimensions = '282x385+120+100'  # '390x190'  # '310x215'

        '''self.col_ui_bt_small = self.col_bt_bg_blue
        self.col_ui_bt_small_highlight = self.col_bt_bg_blue_highlight'''
        self.col_ui_bt_small = self.col_bt_bg_default
        self.col_ui_bt_small_highlight = self.col_bt_bg_active
        self.col_ui_dd_default = self.col_bt_petrol
        self.col_ui_dd_default_highlight = self.col_bt_petrol_highlight

        # UI
        self.ui_proxy = Tk()
        self.main_ui = Toplevel()
        self.main_ui.wm_attributes("-topmost", 1)
        self.main_ui.lift()
        self.main_ui.iconbitmap(r'.\ui\icon_pipe.ico')
        self.main_ui.title('%s' % self.version)
        self.main_ui.attributes("-alpha", 0.0)
        self.main_ui.geometry(dimensions)
        ui_title_bar(self, self.ui_proxy, self.main_ui, f'Open Pipe {self.version}',
                     r'.\ui\icon_pipe_white_PNG_s.png', self.col_wdw_title)

        self.main_ui.resizable(width=True, height=True)
        self.main_ui.configure(bg=self.col_wdw_default)

        # icons
        icon_duplicate = PhotoImage(file=r'.\ui\bt_duplicate.png')
        self.icon_edit = PhotoImage(file=r'.\ui\bt_edit.png')
        self.icon_create = PhotoImage(file=r'.\ui\bt_create.png')
        icon_refresh = PhotoImage(file=r'.\ui\bt_refresh.png')

        self.frame_asset = Frame(self.main_ui, bg=self.col_wdw_default)
        self.frame_asset.pack(fill=X, padx=self.default_padding, pady=2*self.default_padding)

        # Row management
        # root_row = 1
        project_row = 2
        department_row = 0
        self.column_width = 5

        pad_sep = self.default_padding
        frame_separator = Frame(self.frame_asset, bg="gray60", height=1)
        frame_separator2 = Frame(self.frame_asset, bg="gray60", height=1)  # height=2?
        frame_separator3 = Frame(self.frame_asset, bg="gray60", height=1)
        frame_separator4 = Frame(self.frame_asset, bg="gray60", height=1)
        frame_separator5 = Frame(self.frame_asset, bg="gray60", height=1)
        frame_separator.grid(row=1, column=0, columnspan=self.column_width, sticky=NSEW, padx=pad_sep, pady=3)
        frame_separator2.grid(row=5, column=0, columnspan=self.column_width, sticky=NSEW, padx=pad_sep, pady=3)
        frame_separator3.grid(row=8, column=0, columnspan=self.column_width, sticky=NSEW, padx=pad_sep, pady=3)
        frame_separator4.grid(row=13, column=0, columnspan=self.column_width, sticky=NSEW, padx=pad_sep, pady=3)
        frame_separator5.grid(row=15, column=0, columnspan=self.column_width, sticky=NSEW, padx=pad_sep, pady=3)

        # ---------------------------------------------------------------------------------------------
        # -- Project
        lbl_projects = Label(self.frame_asset, bd=1, text='Project ', anchor=W, width=5,
                             bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_projects.grid(row=project_row, column=0, sticky=N, padx=self.default_padding, pady=2*self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.bt_projects_duplicate = Button(self.frame_asset, image=icon_duplicate,
                                            bg=self.col_ui_bt_small,
                                            fg=self.col_bt_fg_default, activebackground=self.col_ui_bt_small_highlight,
                                            activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                            bd=self.default_bt_bd, relief=self.def_bt_relief,
                                            command=lambda: self.project_config_duplicate())
        self.bt_projects_duplicate.grid(row=project_row, column=2, sticky=NSEW, padx=self.default_padding,
                                        pady=self.default_padding)
        CreateToolTip(
            self.bt_projects_duplicate,
            "UI which allows you to duplicate the configuration of the currently selected project. "
            "(located in './projects') \nThe content (e.g. assets/shots) of the project "
            "will not be duplicated.",
            self.col_bt_bg_default_highlight,
            self.col_bt_bg_default
        )
        # ---------------------------------------------------------------------------------------------
        self.bt_projects_edit = Button(self.frame_asset, image=self.icon_edit, height=1, bg=self.col_ui_bt_small,
                                       fg=self.col_bt_fg_default, activebackground=self.col_ui_bt_small_highlight,
                                       activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                       bd=self.default_bt_bd, relief=self.def_bt_relief,
                                       command=lambda: self.project_config_edit())
        self.bt_projects_edit.grid(row=project_row, column=3, sticky=NSEW, padx=self.default_padding,
                                   pady=self.default_padding)
        CreateToolTip(
            self.bt_projects_edit,
            "UI which allows you to edit the configuration file of the currently selected project. "
            "(except for project name and abbreviation)",
            self.col_bt_bg_default_highlight, self.col_bt_bg_default
        )
        # ---------------------------------------------------------------------------------------------
        bt_projects_create = Button(self.frame_asset, image=self.icon_create, bg=self.col_ui_bt_small,
                                    fg=self.col_bt_fg_default, activebackground=self.col_ui_bt_small_highlight,
                                    activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                    bd=self.default_bt_bd, relief=self.def_bt_relief, justify=CENTER,
                                    command=lambda: ProjectCreator().create_ui(None))
        bt_projects_create.grid(row=project_row, column=4, sticky=NSEW, padx=self.default_padding,
                                pady=self.default_padding)
        CreateToolTip(
            bt_projects_create,
            "UI which allows you to create a project configuration file and directory. "
            "Configs include information about:\n"
            "- location of the project\n"
            "- OCIO files used by the project (e.g. ACES)\n"
            "- software versions available to the artists",
            self.col_bt_bg_default_highlight, self.col_bt_bg_default
        )
        # ---------------------------------------------------------------------------------------------
        if len(self.projects) == 0:
            self.current_project_name = ''
            self.projects = []
            self.bt_projects_duplicate.configure(state=DISABLED)
            self.bt_projects_edit.configure(state=DISABLED)
        else:
            self.current_project_name = self.project_names[0]

        self.dd_projects = Menubutton(self.frame_asset, text=self.current_project_name, width=18,
                                      bg=self.col_ui_dd_default, fg=self.col_bt_fg_default, highlightthickness=0,
                                      activebackground=self.col_ui_dd_default_highlight, anchor=W,
                                      activeforeground=self.col_bt_fg_default, bd=1, relief=self.def_bt_relief)
        self.dd_projects.menu = Menu(self.dd_projects, tearoff=0, bd=0, activeborderwidth=3, relief=self.def_bt_relief,
                                     bg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                     activebackground=self.col_bt_bg_blue_highlight, fg=self.col_bt_bg_default)
        self.dd_projects['menu'] = self.dd_projects.menu

        try:
            for project in self.project_names:
                self.dd_projects.menu.add_command(label=project, command=lambda x=project: self.switch_project(x))
        except AttributeError:
            pass
        self.dd_projects.grid(row=project_row, column=1, columnspan=1, sticky=EW, padx=self.default_padding,
                              pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------

        # ---------------------------------------------------------------------------------------------
        # --- Department --- Discipline
        lbl_department = Label(self.frame_asset, bd=1, text='Dep.',
                               bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_department.grid(row=department_row, column=0, sticky=W, padx=self.default_padding,
                            pady=self.default_padding)
        CreateToolTip(lbl_department, "Department", None, None, False)
        # ---------------------------------------------------------------------------------------------
        lbl_discipline = Label(self.frame_asset, bd=1, text='Discipline', width=9,
                               bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_discipline.grid(row=department_row, column=2, columnspan=2,
                            padx=self.default_padding, pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.current_department = 'build'
        self.dd_department = Menubutton(self.frame_asset, text=self.current_department,
                                        width=8, bg=self.col_ui_dd_default, fg=self.col_bt_fg_default,
                                        highlightthickness=0, activebackground=self.col_ui_dd_default_highlight,
                                        anchor=W, activeforeground=self.col_bt_fg_default, bd=1,
                                        relief=self.def_bt_relief, justify=RIGHT)
        self.dd_department.menu = Menu(self.dd_department, tearoff=0, bd=0, activeborderwidth=3,
                                       relief=self.def_bt_relief, bg=self.col_bt_fg_default,
                                       activeforeground=self.col_bt_fg_default, fg=self.col_bt_bg_default,
                                       activebackground=self.col_bt_bg_blue_highlight)
        self.dd_department['menu'] = self.dd_department.menu

        self.dd_department.menu.add_command(label='build', command=lambda: self.switch_department('build'))
        self.dd_department.menu.add_command(label='sequence', command=lambda: self.switch_department('sequence'))
        # self.dd_department.menu.add_command(label='shot', command=lambda: self.switch_department('shot'))

        self.dd_department.grid(row=department_row, column=1, columnspan=1, sticky=EW, padx=self.default_padding,
                                pady=self.default_padding)
        # ---------------------------------------------------------------------------------------------
        self.ui_create_elements_discipline()
        # ---------------------------------------------------------------------------------------------
        self.ui_create_elements_asset_row()
        # ---------------------------------------------------------------------------------------------
        # LAUNCH SCRIPTS SECTION
        # --- Button - Software launcher
        self.frame_launcher = Frame(self.frame_asset, bg=self.col_wdw_default)
        self.frame_launcher.grid(row=7, column=0, columnspan=2, sticky=NSEW, padx=0,
                                 pady=self.default_padding)
        # --- Open MDL/TXT/SHD ------------------------------------------------------------------------
        self.frame_directories = Frame(self.frame_asset, bg=self.col_wdw_default)
        self.frame_directories.grid(row=7, column=2, columnspan=self.column_width-2, sticky=NSEW, padx=0,
                                    pady=self.default_padding)

        lbl_pantries = Label(self.frame_directories, bd=1, text='Stream Pantries', pady=4,
                             bg=self.col_wdw_default, fg=self.col_bt_fg_default)
        lbl_pantries.grid(row=0, column=0, columnspan=3, sticky=NSEW, padx=self.default_padding,
                          pady=self.default_padding)

        self.bt_pantry_mdl = Button(self.frame_directories, text='MDL', border=self.default_bt_bd, padx=2, pady=2,
                                    bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                    activebackground=self.col_bt_bg_active,
                                    activeforeground=self.col_bt_fg_default,
                                    command=lambda: self.open_pantry_dir_mdl())
        self.bt_pantry_mdl.grid(row=1, column=0, columnspan=1, sticky=NSEW, padx=self.default_padding,
                                pady=self.default_padding)
        CreateToolTip(
            self.bt_pantry_mdl,
            'Opens the directory of the model currently used by the selected discipline.',
            self.col_bt_bg_default_highlight,
            self.col_bt_bg_default
        )

        self.bt_pantry_txt = Button(self.frame_directories, text='TXT', border=self.default_bt_bd, padx=2, pady=2,
                                    bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                    activebackground=self.col_bt_bg_active,
                                    activeforeground=self.col_bt_fg_default,
                                    command=lambda: self.open_pantry_dir_txt())
        self.bt_pantry_txt.grid(row=1, column=1, columnspan=1, sticky=NSEW, padx=self.default_padding,
                                pady=self.default_padding)
        CreateToolTip(
            self.bt_pantry_txt,
            'Opens the directory of the texture currently used by the selected discipline.',
            self.col_bt_bg_default_highlight,
            self.col_bt_bg_default
        )

        self.bt_pantry_shd = Button(self.frame_directories, text='SHD', border=self.default_bt_bd, padx=2, pady=2,
                                    bg=self.col_bt_bg_default, fg=self.col_bt_fg_default, relief=self.def_bt_relief,
                                    activebackground=self.col_bt_bg_active,
                                    activeforeground=self.col_bt_fg_default,
                                    command=lambda: self.open_pantry_dir_shd())
        self.bt_pantry_shd.grid(row=1, column=2, columnspan=1, sticky=NSEW, padx=self.default_padding,
                                pady=self.default_padding)
        CreateToolTip(
            self.bt_pantry_shd,
            'Opens the directory of the shading currently used by the selected discipline.',
            self.col_bt_bg_default_highlight,
            self.col_bt_bg_default
        )

        # --- Button - Release Tool - Texture ----------------------------------------------------------
        self.bt_rtt = Button(self.frame_asset, text='Release Tool', height=2, bg=self.col_bt_bg_blue,
                             fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                             activeforeground=self.col_bt_fg_default, highlightthickness=0,
                             bd=self.default_bt_bd, relief=self.def_bt_relief,
                             command=lambda: self.start_release_texture())
        self.bt_rtt.grid(row=9, column=0, columnspan=self.column_width, sticky=NSEW, padx=self.default_padding,
                         pady=self.default_padding)

        CreateToolTip(
            self.bt_rtt,
            "Tool that automatically moves textures into the correct channel and "
            "version directory.\n<asset>/txt/.pantry/<XvX>/<channel>/<version>\n\n"
            "Also creates json files referencing these textures, which allows "
            "other pipeline functionalities like texture rollback,automatic "
            "shader connections and separate active texture version for each "
            "stream/discipline\n\n"
            "(json files are located in '<asset>/.pipeline')\n\n"
            "(directories starting with a dot are hidden and shouldn't be touched "
            "by the artists)",
            self.col_bt_bg_blue_highlight,
            self.col_bt_bg_blue
        )

        # --- Pull & Publish -------------------------------------------------------------------------------
        frame_pull_publish = Frame(self.frame_asset, bg=self.col_wdw_default)
        frame_pull_publish.grid(row=10, column=0, columnspan=self.column_width, sticky=NSEW, padx=0,
                                pady=0)
        frame_pull_publish.grid_columnconfigure(0, weight=1)
        frame_pull_publish.grid_columnconfigure(2, weight=1)

        self.bt_pull = Button(frame_pull_publish, text='Pull', height=2, bg=self.col_bt_bg_blue, width=6,
                              fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                              activeforeground=self.col_bt_fg_default, highlightthickness=0,
                              bd=self.default_bt_bd, relief=self.def_bt_relief,
                              command=lambda: self.start_pull())
        # self.bt_pull.grid(row=10, column=0, columnspan=self.column_width - 1, sticky=NSEW, padx=self.default_padding,
        #                  pady=self.default_padding)
        self.bt_pull.grid(row=0, column=0, columnspan=1, sticky=NSEW, padx=self.default_padding,
                          pady=self.default_padding)
        self.bt_pull.bind('<Enter>', self.on_bt_enter)
        self.bt_pull.bind('<Leave>', self.on_bt_leave)

        self.bt_publish = Button(frame_pull_publish, text='Push', height=2, bg=self.col_bt_bg_blue,
                                 fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                                 activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                 bd=self.default_bt_bd, relief=self.def_bt_relief,
                                 command=lambda: self.start_publish())
        self.bt_publish.grid(row=0, column=2, columnspan=1, sticky=NSEW, padx=self.default_padding,
                             pady=self.default_padding)
        self.bt_publish.bind('<Enter>', self.on_bt_enter)
        self.bt_publish.bind('<Leave>', self.on_bt_leave)

        self.bt_check = Button(frame_pull_publish, image=icon_refresh, height=2, bg=self.col_bt_bg_blue, width=38,
                               fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                               activeforeground=self.col_bt_fg_default, highlightthickness=0,
                               bd=self.default_bt_bd, relief=self.def_bt_relief,
                               command=lambda: self.check_for_outdated_packages())
        # bt_check.grid(row=10, column=self.column_width-1, columnspan=1, sticky=NSEW, padx=self.default_padding,
        #              pady=self.default_padding)
        self.bt_check.grid(row=0, column=1, columnspan=1, sticky=NSEW, padx=self.default_padding,
                           pady=self.default_padding)
        self.bt_check.bind('<Enter>', self.on_bt_enter)
        self.bt_check.bind('<Leave>', self.on_bt_leave)

        # --- Button - Connection Manager - Texture --------------------------------------------------------
        self.bt_connections = Button(self.frame_asset, text='Connection Manager', height=2, bg=self.col_bt_bg_blue,
                                     fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                                     activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                     bd=self.default_bt_bd, relief=self.def_bt_relief,
                                     command=lambda: self.start_connection_manager_texture())
        self.bt_connections.grid(row=11, column=0, columnspan=self.column_width,
                                 sticky=NSEW, padx=self.default_padding, pady=self.default_padding)
        CreateToolTip(
            self.bt_connections,
            "UI that allows you to edit the file that defines which textures are automatically plugged "
            "into a shader.\n"
            "- the file is only used until shading starts to publish\n"
            "- separate file for each asset\n"
            "- manual modification rarely necessary, as file gets created automatically\n"
            "- only available once channels are included in the texture package",
            self.col_bt_bg_blue_highlight,
            self.col_bt_bg_blue
        )

        # --- Button - Package Manager - Texture --------------------------------------------------------
        self.bt_package = Button(self.frame_asset, text='Package Manager', height=2, bg=self.col_bt_bg_blue,
                                 fg=self.col_bt_fg_default, activebackground=self.col_bt_bg_blue_active,
                                 activeforeground=self.col_bt_fg_default, highlightthickness=0,
                                 bd=self.default_bt_bd, relief=self.def_bt_relief,
                                 command=lambda: self.start_package_manager_texture())
        self.bt_package.grid(row=12, column=0, columnspan=self.column_width, sticky=NSEW, padx=self.default_padding,
                             pady=self.default_padding)
        CreateToolTip(
            self.bt_package,
            "Tool that:\n"
            "- enables texture rollback without generating new "
            "texture files. Only json files will be modified.\n"
            "(TXT and SHD are handled separately. SHD can only access published versions.)\n\n"
            "- allows linking of texture channels from other assets or variations",
            self.col_bt_bg_blue_highlight,
            self.col_bt_bg_blue
        )

        # --- Button - Mundane Sequence Renamer ----------------------------------------------------------
        bt_renaming_tool = Button(self.frame_asset, text='Mundane Sequence Renamer', height=2,
                                  bg=self.col_bt_bg_blue, fg=self.col_bt_fg_default,
                                  activebackground=self.col_bt_bg_blue_active, activeforeground=self.col_bt_fg_default,
                                  highlightthickness=0, bd=self.default_bt_bd,
                                  relief=self.def_bt_relief, command=lambda: self.start_msr())
        bt_renaming_tool.grid(row=14, column=0, columnspan=self.column_width, sticky=NSEW, padx=self.default_padding,
                              pady=self.default_padding)
        CreateToolTip(
            bt_renaming_tool,
            "Tool to rename multiple files at once. "
            "\n- Replace <UDIM> (Mari) and <u1_v1> (Mudbox) texture "
            "tile conventions. \n(Not present in most other renaming "
            "software, "
            "e.g. 'ReNamer') \n- Replace phrase. \n- Offset frame numbers."
            "\n\nOrigin: The name is a reference to a renaming tool called 'Super Sequence Renamer' (SSR). "
            "Rory Woodford created this tool for MPC and it's unavailable to the public. "
            "SSR uses a gigantic superhero image as 'apply' "
            "button and will play a superhero sound at maximum "
            "volume whenever it is used, notifying everyone in the office that you "
            "needed to rename something.",
            self.col_bt_bg_blue_highlight,
            self.col_bt_bg_blue
        )
        # --- Bottom Section --------------------------------------------------------------------------
        """frame_bottom = Frame(self.frame_asset, bg=self.col_wdw_default)
        frame_bottom.grid(row=15, column=0, columnspan=self.column_width, sticky=NSEW, padx=self.default_padding,
                          pady=self.default_padding)
        frame_bottom.grid_columnconfigure(0, weight=1)"""

        # --- Always on Top ---------------------------------------------------------------------------
        self.tkvar_top = BooleanVar()
        self.tkvar_top.set(True)
        cb_on_top = Checkbutton(self.frame_asset, text='always on top', var=self.tkvar_top,
                                bg=self.col_wdw_default, activebackground=self.col_wdw_default,
                                fg=self.col_bt_fg_default, activeforeground=self.col_bt_fg_default,
                                selectcolor=self.col_bt_bg_active, command=lambda: self.ui_toggle_on_top())
        cb_on_top.grid(row=16, column=0, columnspan=self.column_width, sticky=N, padx=self.default_padding,
                       pady=self.default_padding)
        CreateToolTip(
            cb_on_top,
            "Forces the main UI to always be on top of all other windows.",
            None,
            None,
            False
        )
        # ---------------------------------------------------------------------------------------------
        self.main_ui.geometry('')  # enable automatic scaling of the UI to fit widgets

        self.load_last_job()
        self.main_ui.attributes("-alpha", 1.0)

        # Continuously checks for updates in push and publish
        # (Deactivated in case constant checking of files affects hard drive life span.)
        # self.event_tick()

        self.main_ui.mainloop()


PipelineUI()

# TODO SWITCH ANIM TO FBX, BECAUSE OF MISSING SG, RESET SCALE TO 1 AFTER IMPORT
# TODO model pipeline doesn't need export directory?
# TODO bind loading image with colourspace detection script
# TODO blender script for IOR controlling group

# TODO needs to copy default configs for projects if copying or creating

# TODO TURNTABLE SCRIPT FOR ALL VARIATIONS
# TODO AUTOMATIC RENDER SETTINGS FOR ALL STREAMS
# TODO alternative shading system that allows to have separate txt/shd variations which allows you to use the same
#  shader for all texture variations (redundant if you can link materials from other asset)

# TODO full-screen meme quiz as easter-egg when clicking on logo
# TODO msr needs sound
# TODO proxy windows need to have the same size as child ui
# TODO update connections unified for both release and package manager
# TODO layout and shot, deactivate discipline
# TODO add release tool for other software (maya model release)
# TODO tooltips for package manager

# TODO layout as additional department

# TODO comment ability for releases

# TODO turn into sub-classees:
# - RTT
# - connection manager

# TODO RTT copy missing tile not from last version folder, but from last json file version not folder

# TODO FINAL - ask rory for permission to mention the origin
# TODO FINAL - add conifg.ocio file, without ACES if ACES can't be packaged (license?)

# TODO blender: issue, deleted objects stay linked to the collection. causes errors as they are not linked to the scene




# TODO If pipeline is opened, and no show exists, run project_editor/creator,
#  ask if you want to source existing projects from somewhere else

# TODO blender turntable doesn't necessarily update all textures?

# Maybe if I feel like it:
# TODO blender rename default view_layer to MASTER
# TODO MSR save/load replacement preset (lists)
# TODO MSR swap replace inputs


# TODO print error if OCIO is not found

# TODO LONGTERM
# TODO auto generate chromeball references for given HDRIs to comp in (and comp in automatically?)
# TODO off tune superhero sound for MSR
# TODO project archiver (delete unused versions, moves project config to a different directory,
#  create what happens if last job config doesn't exist)
# TODO clear access materials when updating models
# TODO MSR allow to create & use custom rename config (furTags lists)
# TODO assets within assets? (split building into parts? frames, wallsegments)

# TODO IMPORTANT
# TODO MSR too large if too many files (scrollable lists?)
# TODO exposure offset for HDRIs in panel
# TODO distribute custom dropdowns
# TODO remove hard link option
# TODO overwrite existing in texture publisher is somehow red...

# TODO what controls the dsp level? shading or modelling?
# TODO who controls the displacement & bump setting? does it get updated?
# TODO open texture version pantry too long (e.g Gollum)
# TODO displacement bug, archive and recreate the modelling settings (auto smooth off)


# TODO FOR SEQUENCE/LAYOUT
# TODO switching shots triggers asset refresh algorithm for old asset
#  (reprode: open UI in Asset mode (on an out of date asset
#  , switch to a different asset (up to date), switch to sequence work, switch the shot...)
# TODO camera packages?
# TODO add push and pull functionality for sequences (pull_required function from pipe_utils)

# TODO store rename history (can't load appleA mdl v003 in shading setup because of broken collection name)

# TODO add resolutions 6x9, 645
# TODO preset& dropdown for focal length and aperture
# TODO creating new shading turntable has two cameras (one gets gathered from the shading file)

# TODO framing tool that changes fov but also distance in order to keep main framing the same.
#  (based on the selected object)

# TODO cleanup
#  - relocate variables from pipe_blender to b_vars
#  - cleanup main blend py-file by moving parts to other files (backup before)

# TODO not sure?
#  - add new package stream (sht) to shd files + ability to set them?
#  - Publish?

# TODO make sequence creator more like Texture variation creator in the package manager

# TODO save backup of project config when overwriting
# TODO wtf is going on with the red highlighting
