from PyQt5.Qt import *
from PyQt5.QtWidgets import *
import os
import matplotlib.pyplot as plt
def open_dicom_dir(self):
    dir_choose = QFileDialog.getExistingDirectory(self,
                                                  "选取文件夹",
                                                  self.cwd)  # 起始路径

    if dir_choose == "":
        print("\n取消选择")
        return

    print("\n你选择的文件夹为:")
    print(dir_choose)
    getfilePath = dir_choose.replace('/', '\\') #换斜杠
    print(getfilePath)

    return dir_choose




