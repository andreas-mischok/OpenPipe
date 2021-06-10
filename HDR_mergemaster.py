import os

ocio = r"C:/Users/ARM/PycharmProjects/Rohrleitung/ocio/aces_1.2/config.ocio"
os.putenv('OCIO', ocio)

exe = r'"C:\Program Files (x86)\HDR-Merge-master_rec2020_to_acescg\build\hdr_brackets.exe"'
os.system(r'cd C:\Program Files (x86)\HDR-Merge-master_rec2020_to_acescg\build\&& ' + f'start cmd /K {exe}')
#os.system(f'start cmd /K {exe}')