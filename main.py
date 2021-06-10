#from sys import argv
import getpass
import json
from datetime import datetime


def load_variables():
    file_variables = open('variables.dat')
    txt = file_variables.read()
    lines = txt.split('\n')

    l_software_labels = []  # list displayed in the dropdown
    l_software_aces_support = []  # list regarding aces support
    l_software = []  # list containing the launch paths

    is_installed_software = False

    for line in lines:
        if is_installed_software is True:
            software = (line[1:-1].split(', '))
            l_software_labels.append(software[0])
            l_software_aces_support.append(software[1] ==' True')
            l_software.append(software[2])
            print(line)

            if '[' not in line:
                is_installed_software = False

        if line == 'installed_software':
            pass
            is_installed_software = True

        print()
    print(l_software_labels)
    print(l_software_aces_support)
    print(l_software)


def store_json_variables():
    artist = getpass.getuser()
    print(artist)
    time = str(datetime.now()).split('.')[0]
    print(time)
    channels = [['CLR', [artist, time, 'v001']], ["SPR", [artist, time, "v002"]]]

    dict_release_channel = {}
    for variable in ["artist", "time", "channels"]:
        dict_release_channel[variable] = eval(variable)

    json_release = json.dumps(dict_release_channel, indent=2)
    print(json_release)


def load_json_variables(config):
    with open(config, 'r') as config_file:
        config_file_content = json.load(config_file)
    try:
        col_wdw_default = config_file_content["col_wdw_default"]
        col_bt_fg_default = config_file_content["col_bt_fg_default"]
        col_bt_bg_blue = config_file_content["col_bt_bg_blue"]
        col_bt_bg_active = config_file_content["col_bt_bg_active"]
    except KeyError:
        pass

    try:
        filetypes = config_file_content["filetypes"]
    except KeyError:
        pass

    print(col_wdw_default)

    # col defaults
    # config

store_json_variables()
#load_json_variables(r'.\defaults_ui.json')
#load_variables()
