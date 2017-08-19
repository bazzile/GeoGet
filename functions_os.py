import os
import shutil


def extract2folder(file_list, dst_folder):
    for file in file_list:
        src = file
        dst = os.path.join(dst_folder, os.path.basename(file))
        # shutil.copyfile(src, dst)
        open(dst, 'a').close()
