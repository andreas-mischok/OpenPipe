"""import os
import shutil as sh

path = r'M:\Andreas Mischok\3D\2019\LOTR\build\envBagend\images\textures\substance\bagend\current'

files = os.listdir(path)

for fl in files:
    if fl[-5] != '_':
        fl_out_parts = fl.split('.')
        fl_out_parts[-2] = fl_out_parts[-2] + '_'
        fl_out = '.'.join(fl_out_parts)

        path_in = os.path.join(path, fl)
        path_out = os.path.join(path, fl_out)
        if os.path.isfile(path_out) is False:
            print(path_in)
            print(path_out)
            sh.copy2(path_in, path_out)
            print("")


"""
import os
import random
import threading
import queue
import time

print('AAAA', os.cpu_count())
file_queue = queue.Queue()

def worker():
    while True:#file_queue.empty() is False:
        fn = file_queue.get()
        try:
            print(fn, type(fn))
        except:
            pass
            print('b')
        #file_queue.task_done()

l = [[1,2], 2, 3]
for i in range(4):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

for item in l:
    file_queue.put(item)
file_queue.join()
