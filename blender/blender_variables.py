# Defines global variables used by the blender script
import os
import json

scene_has_been_loaded = False
scene_is_turntable = False

python_root = os.getenv('PIPE_PYTHON_ROOT')
root = os.getenv('PIPE_ROOT')
project = os.getenv('PIPE_PROJECT')
project_abbr = os.getenv('PIPE_PROJECT_ABBR')
department = os.getenv('PIPE_DEPARTMENT')
discipline = os.getenv('PIPE_DISCIPLINE')
asset = os.getenv('PIPE_ASSET')
sequence = os.getenv('PIPE_SEQUENCE')
shot = os.getenv('PIPE_SHOT')
user = os.getenv('PIPE_USER')

cfg_sensors = f'{python_root}/projects/{project}-{project_abbr}/config_sensors.json'
with open(cfg_sensors, 'r') as fl_sensors:
    dict_sensors = json.load(fl_sensors)

cfg_render_settings = f'.\\projects\\{project}-{project_abbr}\\config_render_settings.json'
with open(cfg_render_settings, 'r') as fl_render_settings:
    dict_render_settings = json.load(fl_render_settings)
