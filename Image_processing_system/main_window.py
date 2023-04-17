import os
import cv2
import sys
import shutil
import colorsys
import numpy as np
from tkinter import *
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image, ImageTk
from open_imagedir import open_dicom_dir
res = []
mid = []
img_stack = []#图像栈
count = 1
deletepngdirpath = "1"
const_fileName = "1"
class FramePane(QWidget):

    def __init__(self,parent=None):
        super().__init__()
        # 添加标题 QLabel 到垂直布局中
        self.setWindowTitle("图像编辑器")
        self.resize(2020, 1500)
        self.setup_ui()
        # 定义绘画类型
        self.Draw = ""
        self.Line_list = [0, 0, 100, 100]
        self.Point_list = []
        self.Elipse_list = [0, 0, 0, 0]
        self.Rectangle_list = [0, 0, 0, 0]
        self.Polygon_list = []
        # 其他
        self.cwd = os.getcwd() # 获取当前路径
        self.dir_model = QFileSystemModel() # 文件系统模型
        self.dicom_tag_model = QStandardItemModel(5,1)

    def setup_ui(self):
        """
            主构造
        """
        # 创建控件
        self.menu_bar = QWidget()
        self.tool_bar = QWidget()
        self.left = QWidget()
        self.body = QWidget()
        self.body.setMouseTracking(True)
        self.right = QWidget()
        # 1.创建布局管理器对象
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        # 2.把布局管理器对象设置给需要布局的父控件
        self.setLayout(self.v_layout)
        # 3.添加需要布局的子控件到布局管理器当中
        self.v_layout.addWidget(self.menu_bar)
        self.v_layout.addWidget(self.tool_bar)
        self.h_layout.addWidget(self.left)
        self.h_layout.addWidget(self.body)
        self.h_layout.addWidget(self.right)
        self.v_layout.addLayout(self.h_layout)
        # 4.设置伸缩因子
        self.v_layout.setStretchFactor(self.menu_bar, 1)
        self.v_layout.setStretchFactor(self.tool_bar, 1)
        self.v_layout.setStretchFactor(self.h_layout, 200)
        self.h_layout.setStretchFactor(self.left,2)
        self.h_layout.setStretchFactor(self.body,8)
        self.h_layout.setStretchFactor(self.right,2)
        """
            Menu_Bar
        """
        # 创建水平布局
        self.menu_bar_layout = QHBoxLayout()
        # 使用水平布局
        self.menu_bar.setLayout(self.menu_bar_layout)


        #文件菜单
        self.file_menu = QMenu()
        self.filebtn = QPushButton(QIcon("ico/file.png"), "打开图片文件夹", self)
        self.filebtn.resize(220,50)
        self.filebtn.clicked.connect(self.open_imagedir_fun)
        self.filebtn.show()

        #保存
        self.savebtn = QPushButton(QIcon("ico/save.png"), "保存", self)
        self.savebtn.resize(220,50)
        self.savebtn.move(220,0)
        self.savebtn.clicked.connect(self.save_filefun)

        #色调菜单
        self.manipulationbtn = QPushButton(QIcon("ico/manipulation.png"), "色调",self)
        self.manipulationbtn.move(440, 0)
        self.manipulationbtn.resize(220, 50)
        self.manipulationmenu = QMenu()
        self.light_action = QAction(QIcon("ico/light.png"), "亮度            ", self.manipulationmenu)
        self.light_action.triggered.connect(self.bright_img)
        self.Contrast_action = QAction(QIcon("ico/Contrast.png"), "对比度", self.manipulationmenu)
        self.Contrast_action.triggered.connect(self.contrast_img)
        self.saturation_action = QAction(QIcon("ico/saturation.png"), "饱和度", self.manipulationmenu)
        self.saturation_action.triggered.connect(self.change_saturation)
        self.hue_action = QAction(QIcon("ico/manipulation.png"), "色调", self.manipulationmenu)
        self.hue_action.triggered.connect(self.change_hue)
        self.temperature_action = QAction(QIcon("ico/temperature.png"), "温度", self.manipulationmenu)
        self.temperature_action.triggered.connect(self.change_temperature)
        self.manipulationmenu.addAction(self.light_action)
        self.manipulationmenu.addSeparator()
        self.manipulationmenu.addAction(self.Contrast_action)
        self.manipulationmenu.addSeparator()
        self.manipulationmenu.addAction(self.saturation_action)
        self.manipulationmenu.addSeparator()
        self.manipulationmenu.addAction(self.hue_action)
        self.manipulationmenu.addSeparator()
        self.manipulationmenu.addAction(self.temperature_action)
        self.manipulationbtn.setMenu(self.manipulationmenu)
        self.manipulationbtn.show()

        # 回退菜单
        self.rollbackbtn = QPushButton(QIcon(""), "回退", self)
        self.rollbackbtn.move(660, 0)
        self.rollbackbtn.resize(220, 50)
        self.rollbackmenu = QMenu()
        self.back_action = QAction(QIcon(""), "撤回一步        ", self.rollbackmenu)
        self.back_action.triggered.connect(self.back_fun)
        self.redo_action = QAction(QIcon(""), "重做", self.rollbackmenu)
        self.redo_action.triggered.connect(self.redo_fun)
        self.rollbackmenu.addAction(self.back_action)
        self.rollbackmenu.addSeparator()
        self.rollbackmenu.addAction(self.redo_action)
        self.rollbackbtn.setMenu(self.rollbackmenu)
        self.rollbackbtn.show()

        #裁剪
        self.cut_btn = QPushButton(QIcon("ico/cut.png"), "裁剪", self)
        self.cut_btn.move(880, 0)
        self.cut_btn.resize(220, 50)
        self.cut_btn.clicked.connect(self.cut_filefun)

        #旋转
        self.rotation_btn = QPushButton(QIcon("ico/rotation.png"), "旋转", self)
        self.rotation_btn.move(1540, 0)
        self.rotation_btn.resize(220, 50)
        self.rotation_btn.clicked.connect(self.rotate_img)

        #反转菜单
        self.reversal_btn = QPushButton(QIcon("ico/xuanxiang.png"), "反转", self)
        self.reversal_btn.move(1760, 0)
        self.reversal_btn.resize(220, 50)
        self.reversal_menu = QMenu()
        self.LR_action = QAction(QIcon("ico/LR_action.png"), "左右            ", self.reversal_menu)
        self.LR_action.triggered.connect(self.flip_image_horizontal)
        self.UD_action = QAction(QIcon("ico/UD_action.png"), "上下", self.reversal_menu)
        self.UD_action.triggered.connect(self.flip_image_vertical)
        self.reversal_menu.addAction(self.LR_action)
        self.reversal_menu.addSeparator()
        self.reversal_menu.addAction(self.UD_action)
        self.reversal_btn.setMenu(self.reversal_menu)
        self.reversal_btn.show()

        #滤镜菜单
        self.LMbtn = QPushButton(QIcon("ico/LMbtn.png"), "滤镜", self)
        self.LMbtn.move(1100, 0)
        self.LMbtn.resize(220, 50)
        self.LMmenu = QMenu()
        self.filter_action = QAction(QIcon("ico/dise.png"), "一键美化", self.LMmenu)
        self.filter_action.triggered.connect(self.beautify_image)
        self.filter1_action = QAction(QIcon("ico/Grayscalefilter.png"), "灰度滤镜", self.LMmenu)
        self.filter1_action.triggered.connect(self.Grayscalefilter)
        self.filter2_action = QAction(QIcon("ico/Sketchfilter.png"), "素描滤镜", self.LMmenu)
        self.filter2_action.triggered.connect(self.Sketchfilter)
        self.filter3_action = QAction(QIcon("ico/Cartoonfilter.png"), "卡通滤镜", self.LMmenu)
        self.filter3_action.triggered.connect(self.Cartoonfilter)
        self.LMmenu.addAction(self.filter_action)
        self.submenu = QMenu("滤镜选项", self.LMmenu)
        self.submenu.addAction(self.filter1_action)
        self.submenu.addAction(self.filter2_action)
        self.submenu.addAction(self.filter3_action)
        self.LMmenu.addMenu(self.submenu)
        self.LMbtn.setMenu(self.LMmenu)
        self.LMbtn.show()

        # #装饰菜单
        # self.decoration_btn = QPushButton(QIcon("ico/decoration.png"), "装饰", self)
        # self.decoration_btn.move(1320, 0)
        # self.decoration_btn.resize(220, 50)
        # self.decoration_menu = QMenu()
        # self.map_action = QAction(QIcon("ico/map.png"), "贴图            ", self.decoration_menu)
        # self.map_action.triggered.connect(lambda:print("yes"))
        # self.text_action = QAction(QIcon("ico/text.png"), "文字", self.decoration_menu)
        # self.text_action.triggered.connect(lambda:print("yes"))
        # self.decoration_menu .addAction(self.map_action)
        # self.decoration_menu .addSeparator()
        # self.decoration_menu .addAction(self.text_action)
        # self.decoration_btn.setMenu(self.decoration_menu )
        # self.decoration_btn.show()

        #底色菜单
        self.Background_btn = QPushButton(QIcon("ico/decoration.png"), "底色", self)
        self.Background_btn.move(1320, 0)
        self.Background_btn.resize(220, 50)
        self.Background_menu = QMenu()
        self.bluered_action = QAction(QIcon(""), "蓝底变红            ", self.Background_menu)
        self.bluered_action.triggered.connect(self.change_background_blue_red)
        self.bluewhite_action = QAction(QIcon(""), "蓝底变白", self.Background_menu)
        self.bluewhite_action.triggered.connect(self.change_background_blue_white)
        self.action = QAction(QIcon(""), "更多功能敬请期待", self.Background_menu)
        # self.whiteblue_action = QAction(QIcon(""), "白底变蓝            ", self.Background_menu)
        # self.whiteblue_action.triggered.connect(self.change_background_white_blue)
        # self.whitered_action = QAction(QIcon(""), "白底变红", self.Background_menu)
        #self.whitered_action.triggered.connect(self.change_background_white_red)
        self.Background_menu .addAction(self.bluered_action)
        self.Background_menu .addSeparator()
        self.Background_menu .addAction(self.bluewhite_action)
        self.Background_menu .addSeparator()
        self.Background_menu .addAction(self.action)
        # self.Background_menu .addSeparator()
        # self.Background_menu .addAction(self.whitered_action)
        self.Background_btn.setMenu(self.Background_menu)
        self.Background_btn.show()

        '''
         Left
        '''
        self.left_layout = QVBoxLayout()
        self.left.setLayout(self.left_layout)
        self.file_dir_tree = QTreeView()
        self.left_layout.addWidget(self.file_dir_tree)
        '''
         Body
        '''
        self.body_layout = QVBoxLayout()
        self.body.setLayout(self.body_layout)
        self.img_show_lb = QLabel()
        self.img_show_lb.setMouseTracking(True)
        self.body_layout.addWidget(self.img_show_lb)
        '''
         Rights
        '''
        self.right_layout = QVBoxLayout()
        self.right.setLayout(self.right_layout)
        self.tag_view_tv = QTableView(self.right)
        self.right_layout.addWidget(self.tag_view_tv)

    #鼠标
    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        text = "x:{0},y:{1}".format(x, y)
        print(text)

     #打开资源管理器
    def open_imagedir_fun(self):
        dir_choose = open_dicom_dir(self)
        self.dir_model.setRootPath(dir_choose)
        self.file_dir_tree.setModel(self.dir_model)
        self.file_dir_tree.setRootIndex(self.dir_model.index(dir_choose))
        self.file_dir_tree.clicked.connect(self.show_info)
        self.file_dir_tree.setColumnWidth(0, 300)

    #展示图像
    def show_info(self,signal):
        file_path = self.dir_model.filePath(signal)
        print(file_path)
        img = cv2.imread(file_path)
        global img_stack
        new_size = (512, 512)  # 设置新的像素大小
        img = cv2.resize(img, new_size)
        img_stack.append(img)
        print(len(img_stack))
        cv2.imwrite("rgb_show.jpg", img)
        cv2.imwrite("rgb2_show.jpg", img)
        # shutil.copyfile(file_path, "rgb_show.jpg")
        # shutil.copyfile(file_path, "rgb2_show.jpg")
        self.img_show_lb.setPixmap(QPixmap(file_path))
        self.img_show_lb.setScaledContents(True)

    #保存图像
    def save_filefun(self):
        global res
        cv2.imwrite("rgb2_show.jpg", res)  # 保存为图像文件
        global img_stack
        img_stack.append(res)
        print(len(img_stack))

    def back_fun(self):
        global img_stack
        if len(img_stack) > 1:  # 检查栈是否为空
            img_stack.pop()  # 弹出栈顶元素
            global res
            res = img_stack[-1]
            cv2.imwrite("rgb2_show.jpg", res)
            self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
            self.img_show_lb.setScaledContents(True)
        else:
            print("Stack is empty.")

    def redo_fun(self):
        global img_stack
        while len(img_stack) > 1:  # 检查栈中是否还有多于一个元素
            img_stack.pop()  # 弹出栈顶元素，直到只剩下一个元素
        global res
        res = img_stack[-1]
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)

    #亮度
    def brighting_img(self):
        value = self.bright_sd.value()
        self.bright_value_lb.setText(str(value))  # 更新显示数值
        self.bright_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        global res
        res = img_stack[-1].copy()
        res = np.clip(res * (value / 100.0) , 0 , 255)
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)
    def bright_img(self):
        if hasattr(self, 'bright_sd'):  # 检查是否已经存在滑动条对象
            self.bright_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self,'bright_value_lb'):
            self.bright_value_lb.deleteLater()
        if hasattr(self,'test1'):
            self.test1.deleteLater()
        self.test1 = QLabel(self)
        self.test1.setFont(QFont("", 10, QFont.Bold))
        self.test1.move(1690,200)
        self.test1.setText("亮度:")
        self.test1.show()
        self.bright_sd = QSlider(self)
        self.bright_sd.move(1785, 200)
        self.bright_sd.resize(200,30)
        # 设置最大值和最小值
        self.bright_sd.setMinimum(0)
        self.bright_sd.setMaximum(400)
        self.bright_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.bright_sd.valueChanged.connect(self.brighting_img)
        self.bright_sd.setValue(0)  # 设置初始值
        self.bright_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.bright_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.bright_sd.setOrientation(Qt.Horizontal)
        self.bright_sd.show()
        # 创建用于显示亮度数值的 QLabel
        self.bright_value_lb = QLabel(self)
        self.bright_value_lb.move(1980, 200)  # 设置位置
        self.bright_value_lb.show()

    #对比度
    def contrasting_img(self):
        value = self.contrast_sd.value()
        self.contrast_value_lb.setText(str(value))
        self.contrast_value_lb.adjustSize()
        global img_stack
        # 调节对比度
        global res
        res = img_stack[-1].copy()
        res = cv2.convertScaleAbs(res , alpha=1.0*value/100)
        # 将像素值范围裁剪到[0, 255]
        res = np.clip(res , 0, 255)
        cv2.imwrite("rgb2_show.jpg", res)  # ++++++++++++++
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))  # ++++++++++++++
        self.img_show_lb.setScaledContents(True)
    def contrast_img(self):
        if hasattr(self, 'contrast_sd'):  # 检查是否已经存在滑动条对象
            self.contrast_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self,'contrast_value_lb'):
            self.contrast_value_lb.deleteLater()
        if hasattr(self,'test2'):
            self.test2.deleteLater()
        self.test2 = QLabel(self)
        self.test2.setFont(QFont("", 10, QFont.Bold))
        self.test2.move(1690,300)
        self.test2.setText("对比度:")
        self.test2.show()
        self.contrast_sd = QSlider(self)
        self.contrast_sd.move(1785, 300)
        self.contrast_sd.resize(200,30)
        # 设置最大值和最小值
        self.contrast_sd.setMinimum(0)
        self.contrast_sd.setMaximum(240)
        self.contrast_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.contrast_sd.valueChanged.connect(self.contrasting_img)
        self.contrast_sd.setValue(0)  # 设置初始值
        self.contrast_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.contrast_sd.setTickInterval(40)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.contrast_sd.setOrientation(Qt.Horizontal)
        self.contrast_sd.show()
        # 创建用于显示对比度数值的 QLabel
        self.contrast_value_lb = QLabel(self)
        self.contrast_value_lb.move(1980, 300)  # 设置位置
        self.contrast_value_lb.show()

    #饱和度
    def change_saturation_img(self):
        value = self.saturation_sd.value()
        self.saturation_value_lb.setText(str(value))  # 更新显示数值
        self.saturation_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        global res
        res = img_stack[-1].copy()
        res = res / 255.0  ;res = res * 2 - 1  ;res = (res + 1) / 2    ;res = res * 255.0
        r = res[:, :, 0]    ;g = res[:, :, 1];    b = res[:, :, 2]
        # 计算饱和度的调整值
        saturation_adjustment = 1.0*value/100
        # 计算灰度值
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        # 根据饱和度的调整值调整RGB通道
        r = r * saturation_adjustment + gray * (1 - saturation_adjustment)
        g = g * saturation_adjustment + gray * (1 - saturation_adjustment)
        b = b * saturation_adjustment + gray * (1 - saturation_adjustment)
        res = np.stack([r, g, b], axis=2)
        res = res / 255.0   ;res= res * 2 - 1  ;res = (res + 1) / 2    ;res = res * 255.0
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)
    def change_saturation(self):
        if hasattr(self, 'saturation_sd'):  # 检查是否已经存在滑动条对象
            self.saturation_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'saturation_value_lb'):
            self.saturation_value_lb.deleteLater()
        if hasattr(self,'test3'):
            self.test3.deleteLater()
        self.test3 = QLabel(self)
        self.test3.setFont(QFont("", 10, QFont.Bold))
        self.test3.move(1690,400)
        self.test3.setText("饱和度:")
        self.test3.show()
        self.saturation_sd = QSlider(self)
        self.saturation_sd.move(1785, 400)
        self.saturation_sd.resize(200, 30)
        # 设置最大值和最小值
        self.saturation_sd.setMinimum(0)
        self.saturation_sd.setMaximum(200)
        self.saturation_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.saturation_sd.valueChanged.connect(self.change_saturation_img)
        self.saturation_sd.setValue(0)  # 设置初始值
        self.saturation_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.saturation_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.saturation_sd.setOrientation(Qt.Horizontal)
        self.saturation_sd.show()

        # 创建用于显示饱和度数值的 QLabel
        self.saturation_value_lb = QLabel(self)
        self.saturation_value_lb.move(1980, 400)  # 设置位置
        self.saturation_value_lb.show()


    #色调
    def change_hue_img(self):
        value = self.hue_sd.value() / 100.0
        self.hue_value_lb.setText(str(value))  # 更新显示数值
        self.hue_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        global res
        res = img_stack[-1].copy()
        # 获取图像尺寸和通道数
        height, width, channels = res.shape
        # 依次对每个像素点进行处理
        for i in range(height):
            for j in range(width):
                # 获取当前像素点的 RGB 色值
                pixel_r = res[i, j, 0]
                pixel_g = res[i, j, 1]
                pixel_b = res[i, j, 2]
                # 转为 HSV 色值
                h, s, v = colorsys.rgb_to_hsv(pixel_r / 255., pixel_b / 255., pixel_g / 255.)
                # 修改 hue 值
                h = value
                # 转回 RGB 色系
                rgb = colorsys.hsv_to_rgb(h, s, v)
                pixel_r, pixel_g, pixel_b = [int(x * 255.) for x in rgb]
                # 更新像素点的 RGB 色值
                res[i, j, 0] = pixel_r
                res[i, j, 1] = pixel_g
                res[i, j, 2] = pixel_b
        # 保存处理后的图像
        cv2.imwrite('rgb2_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('rgb2_show.jpg'))
        self.img_show_lb.setScaledContents(True)
    def change_hue(self):
        if hasattr(self, 'hue_sd'):  # 检查是否已经存在滑动条对象
            self.hue_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'hue_value_lb'):
            self.hue_value_lb.deleteLater()
        if hasattr(self,'test4'):
            self.test4.deleteLater()
        self.test4 = QLabel(self)
        self.test4.setFont(QFont("", 10, QFont.Bold))
        self.test4.move(1690,500)
        self.test4.setText("色调:")
        self.test4.show()
        self.hue_sd = QSlider(self)
        self.hue_sd.move(1785, 500)
        self.hue_sd.resize(200, 30)
        # 设置最大值和最小值
        self.hue_sd.setMinimum(0)
        self.hue_sd.setMaximum(100)
        self.hue_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.hue_sd.valueChanged.connect(self.change_hue_img)
        self.hue_sd.setValue(0)  # 设置初始值
        self.hue_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.hue_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.hue_sd.setOrientation(Qt.Horizontal)
        self.hue_sd.show()
        # 创建用于显示色调数值的 QLabel
        self.hue_value_lb = QLabel(self)
        self.hue_value_lb.move(1980, 500)  # 设置位置
        self.hue_value_lb.show()

    #温度
    def change_temperature_img(self):
        value = self.temperature_sd.value()
        self.temperature_value_lb.setText(str(value))  # 更新显示数值
        self.temperature_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        img = img_stack[-1].copy()
        # 预定义颜色矩阵
        color_matrix = np.array([[1.0, 0.0, 0.0],  # 红色通道
                                 [0.0, 1.0, 0.0],  # 绿色通道
                                 [0.0, 0.0, 1.0]])  # 蓝色通道
        # 根据温度调节度计算颜色矩阵
        if value > 0:
            color_matrix[:, 0] *= value / 100.0  # 增加红色通道
        elif value < 0:
            color_matrix[:, 2] *= abs(value) / 100.0  # 增加蓝色通道
        global res
        # 对图像应用颜色矩阵
        res = cv2.transform(img, color_matrix)
        # 对调整后的像素值进行截断，确保像素值在0到255之间
        res = np.clip(res, 0, 255).astype(np.uint8)
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)
    def change_temperature(self):
        if hasattr(self, 'temperature_sd'):  # 检查是否已经存在滑动条对象
            self.temperature_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'temperature_value_lb'):
            self.temperature_value_lb.deleteLater()
        if hasattr(self,'test5'):
            self.test5.deleteLater()
        self.test5 = QLabel(self)
        self.test5.setFont(QFont("", 10, QFont.Bold))
        self.test5.move(1690,600)
        self.test5.setText("温度:")
        self.test5.show()
        self.temperature_sd = QSlider(self)
        self.temperature_sd.move(1785, 600)
        self.temperature_sd.resize(200, 30)
        # 设置最大值和最小值
        self.temperature_sd.setMinimum(-100)
        self.temperature_sd.setMaximum(100)
        self.temperature_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.temperature_sd.valueChanged.connect(self.change_temperature_img)
        self.temperature_sd.setValue(0)  # 设置初始值
        self.temperature_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.temperature_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.temperature_sd.setOrientation(Qt.Horizontal)
        self.temperature_sd.show()
        # 创建用于显示温度数值的 QLabel
        self.temperature_value_lb = QLabel(self)
        self.temperature_value_lb.move(1980, 600)  # 设置位置
        self.temperature_value_lb.show()

    #旋转
    def rotating_img(self):
        self.img_show_lb.setText(str(self.dial.value()))
        value = self.dial.value()
        global img_stack
        img = img_stack[-1].copy()
        # 计算图像中心坐标
        height, width = img.shape[:2]
        cx, cy = width / 2, height / 2
        # 计算旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D((cx, cy), value, 1.0)
        # 应用旋转矩阵到图像上
        global res
        res = cv2.warpAffine(img, rotation_matrix, (width, height))
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))#++++++++++++++
        self.img_show_lb.setScaledContents(True)
    def rotate_img(self):
        if hasattr(self, 'dial'):  # 检查是否已经存在滑动条对象
            self.dial.deleteLater()  # 删除旧的滑动条对象
        self.dial =  QDial(self)
        self.dial.move(1800, 100)
        self.dial.resize(80, 80)
        # 设置最大值和最小值
        self.dial.setMinimum(0)
        self.dial.setMaximum(360)
        # 绑定槽函数
        self.dial.valueChanged.connect(self.rotating_img)
        # 外观倒立
        self.dial.setInvertedAppearance(True)
        self.dial.show()

    #反转
    def flip_image_horizontal(self):
        img = img_stack[-1].copy()
        # 左右反转图像
        global res
        res = cv2.flip(img, 1)
        img_stack.append(res)
        #cv2.imwrite("flipped_image.jpg", res)
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)
    def flip_image_vertical(self):
        img = img_stack[-1].copy()
        # 上下反转图像
        global res
        res = cv2.flip(img, 0)
        img_stack.append(res)
        #cv2.imwrite("flipped_image.jpg", res)
        cv2.imwrite("rgb2_show.jpg", res)
        self.img_show_lb.setPixmap(QPixmap("rgb2_show.jpg"))
        self.img_show_lb.setScaledContents(True)

    #裁切
    def cut_filefun(self):
        self.image_cropper(None)
    def image_cropper(self,master):
        crop_start = None
        def on_crop_start(event):
            nonlocal crop_start
            crop_start = (event.x, event.y)
        def on_crop_drag(event):
            nonlocal crop_start
            if crop_start:
                x, y = event.x, event.y
                canvas.delete("crop_rect")
                canvas.create_rectangle(crop_start[0], crop_start[1], x, y, outline="red", tags="crop_rect")
        def on_crop_end(event):
            nonlocal crop_start
            if crop_start:
                x, y = event.x, event.y
                bbox = (crop_start[0], crop_start[1], x, y)
                cropped = image.crop(bbox)
                cropped.save("cropped_image.jpg")
                #cropped.show()
                global res
                res = np.array(cropped)
                self.img_show_lb.setPixmap(QPixmap("cropped_image.jpg"))
                self.img_show_lb.setScaledContents(True)
                crop_start = None
                canvas.delete("crop_rect")
        root = Tk()
        image = Image.open("rgb2_show.jpg")
        image_tk = ImageTk.PhotoImage(image)
        canvas = Canvas(root, width=512, height=512)
        canvas.create_image(0, 0, anchor=NW, image=image_tk)
        canvas.pack()
        canvas.bind("<Button-1>", on_crop_start)
        canvas.bind("<B1-Motion>", on_crop_drag)
        canvas.bind("<ButtonRelease-1>", on_crop_end)
        root.eval('tk::PlaceWindow . center')
        root.mainloop()

    #灰度滤镜
    def Grayscalefilter_img(self):
        value = self.grayscale_sd.value()
        self.grayscale_value_lb.setText(str(value))  # 更新显示数值
        self.grayscale_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        img = img_stack[-1].copy()
        # 检查图像类型，如果是彩色图像则转换为灰度图像
        if len(img.shape) == 3 and img.shape[2] == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        elif len(img.shape) == 2:
            img_gray = img
        else:
            print("图像类型错误")
            return
        global res
        res = np.uint8(np.clip((1.2 * img_gray + 0), value, 255))
        cv2.imwrite('brrgb_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('brrgb_show.jpg'))
        self.img_show_lb.setScaledContents(True)
    def Grayscalefilter(self):
        if hasattr(self, 'grayscale_sd'):  # 检查是否已经存在滑动条对象
            self.grayscale_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'grayscale_value_lb'):
            self.grayscale_value_lb.deleteLater()
        if hasattr(self,'test6'):
            self.test6.deleteLater()
        self.test6 = QLabel(self)
        self.test6.setFont(QFont("", 10, QFont.Bold))
        self.test6.move(1690,800)
        self.test6.setText("灰度:")
        self.test6.show()

        self.grayscale_sd = QSlider(self)
        self.grayscale_sd.move(1785, 800)
        self.grayscale_sd.resize(200, 30)
        # 设置最大值和最小值
        self.grayscale_sd.setMinimum(0)
        self.grayscale_sd.setMaximum(255)
        self.grayscale_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.grayscale_sd.valueChanged.connect(self.Grayscalefilter_img)
        self.grayscale_sd.setValue(0)  # 设置初始值
        self.grayscale_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.grayscale_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.grayscale_sd.setOrientation(Qt.Horizontal)
        self.grayscale_sd.show()
        # 创建用于显示数值的 QLabel
        self.grayscale_value_lb = QLabel(self)
        self.grayscale_value_lb.move(1980, 800)  # 设置位置
        self.grayscale_value_lb.show()

    #素描滤镜
    def Sketchfilter_img(self):
        value = self.sketch_sd.value()
        self.sketch_value_lb.setText(str(value))  # 更新显示数值
        self.sketch_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        img = img_stack[-1].copy()
        num_down = 2  # 缩减像素采样的数目
        num_bilateral = 9  # 定义双边滤波的数目
        img_color = img
        for _ in range(num_down):
            img_color = cv2.pyrDown(img_color)
        # 重复使用小的双边滤波代替一个大的滤波
        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=4, sigmaColor=8, sigmaSpace=4)
        # 升采样图片到原始大小
        for _ in range(num_down):
            img_color = cv2.pyrUp(img_color)
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度
        img_blur = cv2.medianBlur(img_gray, value * 2 + 1)  # 增加模糊效果。值越大越模糊（取奇数）
        # 检测到边缘并且增强其效果
        global res
        res = cv2.adaptiveThreshold(img_blur, 256,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY,
                                         blockSize=9,
                                         C=2)
        res = cv2.cvtColor(res, cv2.COLOR_GRAY2RGB)  # 彩色图像转为灰度图像
        cv2.imwrite('brrgb_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('brrgb_show.jpg'))
        self.img_show_lb.setScaledContents(True)
    def Sketchfilter(self):
        if hasattr(self, 'sketch_sd'):  # 检查是否已经存在滑动条对象
            self.sketch_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'sketch_value_lb'):
            self.sketch_value_lb.deleteLater()
        if hasattr(self,'test7'):
            self.test7.deleteLater()
        self.test7 = QLabel(self)
        self.test7.setFont(QFont("", 10, QFont.Bold))
        self.test7.move(1690,900)
        self.test7.setText("素描:")
        self.test7.show()

        self.sketch_sd = QSlider(self)
        self.sketch_sd.move(1785, 900)
        self.sketch_sd.resize(200, 30)
        # 设置最大值和最小值
        self.sketch_sd.setMinimum(1)
        self.sketch_sd.setMaximum(10)
        self.sketch_sd.setSingleStep(1)  # 调整步长
        # 绑定槽函数
        self.sketch_sd.valueChanged.connect(self.Sketchfilter_img)
        self.sketch_sd.setValue(1)  # 设置初始值
        self.sketch_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.sketch_sd.setTickInterval(2)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.sketch_sd.setOrientation(Qt.Horizontal)
        self.sketch_sd.show()
        # 创建用于显示数值的 QLabel
        self.sketch_value_lb = QLabel(self)
        self.sketch_value_lb.move(1980, 900)  # 设置位置
        self.sketch_value_lb.show()

    #卡通滤镜
    def Cartoonfilter_img(self):
        value = self.cartoon_sd.value()
        self.cartoon_value_lb.setText(str(value))  # 更新显示数值
        self.cartoon_value_lb.adjustSize()  # 调整 QLabel 大小以适应文本长度
        global img_stack
        img = img_stack[-1].copy()
        # 转换为灰度并且使其产生中等的模糊
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_blur = cv2.medianBlur(img_gray, 5)  # 值越大越模糊（取奇数）
        # 检测到边缘并且增强其效果
        img_edge = cv2.adaptiveThreshold(img_blur, value,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY,
                                         blockSize=9,
                                         C=8)
        img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)  # 彩色图像转为灰度图像
        img_cartoon = cv2.bitwise_and(img, img_edge)  # 灰度图像转为彩色图像
        # 调整亮度和对比度
        global res
        res = np.uint8(np.clip((2.0 * img_cartoon + 16), 0, 255))
        cv2.imwrite('brrgb_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('brrgb_show.jpg'))
        self.img_show_lb.setScaledContents(True)
    def Cartoonfilter(self):
        if hasattr(self, 'cartoon_sd'):  # 检查是否已经存在滑动条对象
            self.cartoon_sd.deleteLater()  # 删除旧的滑动条对象
        if hasattr(self, 'cartoon_value_lb'):
            self.cartoon_value_lb.deleteLater()
        if hasattr(self,'test8'):
            self.test8.deleteLater()
        self.test8 = QLabel(self)
        self.test8.setFont(QFont("", 10, QFont.Bold))
        self.test8.move(1690,1000)
        self.test8.setText("卡通:")
        self.test8.show()
        self.cartoon_sd = QSlider(self)
        self.cartoon_sd.move(1785, 1000)
        self.cartoon_sd.resize(200, 30)
        # 设置最大值和最小值
        self.cartoon_sd.setMinimum(1)
        self.cartoon_sd.setMaximum(255)
        self.cartoon_sd.setSingleStep(2)  # 调整步长
        # 绑定槽函数
        self.cartoon_sd.valueChanged.connect(self.Cartoonfilter_img)
        self.cartoon_sd.setValue(0)  # 设置初始值
        self.cartoon_sd.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置
        self.cartoon_sd.setTickInterval(10)  # 设置刻度间隔
        # 设置滑动条的方向为水平
        self.cartoon_sd.setOrientation(Qt.Horizontal)
        self.cartoon_sd.show()
        # 创建用于显示数值的 QLabel
        self.cartoon_value_lb = QLabel(self)
        self.cartoon_value_lb.move(1980, 1000)
        self.cartoon_value_lb.show()

    def beautify_image(self):
        global img_stack
        img = img_stack[-1].copy()
        # 调整对比度和亮度
        img = cv2.convertScaleAbs(img, alpha=60/100.0, beta=0.1)
        # 增加高斯模糊
        img = cv2.GaussianBlur(img, (3, 3), 0.5)
        # 增加颜色饱和度
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[..., 1] = hsv[..., 1] * (1 + 5/100.0)
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        # 增加锐化
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)*1.8
        img = cv2.filter2D(img, -1, kernel)
        # 将像素值限制在0-255之间
        img = np.clip(img, 0, 255).astype(np.uint8)
        global res
        res = img
        cv2.imwrite('rgb2_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('rgb2_show.jpg'))
        self.img_show_lb.setScaledContents(True)

    def change_background_blue_red(self):
        global img_stack
        img = img_stack[-1].copy()
        # 图像缩放并显示
        rows, cols, channels = img.shape
        # 图片转换为灰度图
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #蓝底变红底
        lower_red = np.array([90, 70, 70])
        upper_red = np.array([110, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=1)
        dilate = cv2.dilate(erode, None, iterations=1)
        # 遍历每个像素点，进行颜色的替换
        for i in range(rows):
            for j in range(cols):
                if dilate[i, j] == 255:
                    img[i, j] = (0, 0, 255)
        global res
        res = img
        cv2.imwrite('rgb2_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('rgb2_show.jpg'))
        self.img_show_lb.setScaledContents(True)

    def change_background_blue_white(self):
        global img_stack
        img = img_stack[-1].copy()
        # 图像缩放并显示
        rows, cols, channels = img.shape
        # 图片转换为灰度图
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #蓝底变红底
        lower_red = np.array([90, 70, 70])
        upper_red = np.array([110, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=1)
        dilate = cv2.dilate(erode, None, iterations=1)
        # 遍历每个像素点，进行颜色的替换
        for i in range(rows):
            for j in range(cols):
                if dilate[i, j] == 255:
                    img[i, j] = (255, 255,255)
        global res
        res = img
        cv2.imwrite('rgb2_show.jpg', res)
        self.img_show_lb.setPixmap(QPixmap('rgb2_show.jpg'))
        self.img_show_lb.setScaledContents(True)

    # def change_background_white_blue(self):
    #     global img_stack
    #     img = img_stack[-1].copy()
    #     # 图像缩放并显示
    #     rows, cols, channels = img.shape
    #     # 图片转换为灰度图
    #     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #     # 白底变蓝底
    #     lower_blue = np.array([100, 50, 50])  # 修改这里的颜色阈值为适合白底的蓝色阈值
    #     upper_blue = np.array([130, 255, 255])  # 修改这里的颜色阈值为适合白底的蓝色阈值
    #     mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #     # 腐蚀膨胀
    #     erode = cv2.erode(mask, None, iterations=1)
    #     dilate = cv2.dilate(erode, None, iterations=1)
    #     # 遍历每个像素点，进行颜色的替换
    #     for i in range(rows):
    #         for j in range(cols):
    #             if dilate[i, j] == 255:
    #                 img[i, j] = (255, 0, 0)  # 将白色像素替换为蓝色像素
    #     global res
    #     res = img
    #     cv2.imwrite('rgb2_show.jpg', res)
    #     self.img_show_lb.setPixmap(QPixmap('rgb2_show.jpg'))
    #     self.img_show_lb.setScaledContents(True)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = FramePane()

    window.show()

    sys.exit(app.exec_())