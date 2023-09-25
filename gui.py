import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter
from detect import *
from fun import *


class Ui_Dialog(object):
    global detect_img, result_path, loc
    img_path = ''
    color = ''
    contrast = ''
    brightness = ''

    global la_r, lo_r, map_folder_path, screenshot_file
    lo = 0
    la = 0


    ''' 设置窗口背景 '''
    def setWindowBackground(self, Dialog):
        pixmap = QtGui.QPixmap("E:/Subjects/sw/gui/background.png")

        # 创建透明度效果
        opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.6)  # 调整透明度，范围为 0.0 到 1.0

        # 创建带有模糊和透明度效果的背景标签
        background_label = QtWidgets.QLabel(Dialog)
        background_label.setGeometry(Dialog.rect())
        background_label.setPixmap(pixmap)
        background_label.setScaledContents(True)
        background_label.setGraphicsEffect(opacity_effect)
        
        background_label.lower()


    ''' 小目标检测 '''

    ''' 输入图像 浏览 '''
    def browse_file(self):
        global img_path
        file_dialog = QtWidgets.QFileDialog()
        img_path, _ = file_dialog.getOpenFileName(None, "选择文件", "", "所有文件(*.*)")
        self.lineEdit_1.setText(img_path)

    ''' 目标颜色 '''
    def input_color(self):
        global color
        color = self.lineEdit_4.text()

    ''' 对比度 '''
    def input_contrast(self):
        global contrast
        contrast = self.lineEdit_2.text()

    ''' 亮度 '''
    def input_brightness(self):
        global brightness
        brightness = self.lineEdit_3.text()

    ''' 开始检测 '''
    def start_detect(self):
        global img_path, color, contrast, brightness, detect_img, result_path, loc

        self.textBrowser_1.setStyleSheet("font-size: 16px;")
        self.textBrowser_2.setStyleSheet("font-size: 16px;")
        self.textBrowser_1.append('加载图像...')
        QtWidgets.QApplication.processEvents()
        img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR)
        self.textBrowser_1.append('图像预处理...')
        QtWidgets.QApplication.processEvents()
        img = adjust(img, float(contrast), float(brightness))
        self.textBrowser_1.append('检测小目标...')
        QtWidgets.QApplication.processEvents()
        detect_img, result_path, loc = detect(img, color)
        self.textBrowser_1.append('检测完成！')
        self.textBrowser_1.append(f'检测结果保存为{result_path}')
        QtWidgets.QApplication.processEvents()
        self.textBrowser_2.append(str(loc))

    ''' 查看结果 '''
    def view_result(self):
        if not hasattr(self, 'result_window') or not self.result_window:
            self.result_window = QtWidgets.QMainWindow()
            self.result_window.setWindowTitle("小目标检测结果")
            self.result_window.setGeometry(100, 100, 800, 600)

            label = QtWidgets.QLabel(self.result_window)
            pixmap = QtGui.QPixmap(result_path)
            label.setPixmap(pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)

            scroll_area = QtWidgets.QScrollArea(self.result_window)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(label)

            self.result_window.setCentralWidget(scroll_area)

            label.adjustSize()

        # 显示新窗口
        self.result_window.show()

    ''' 清除数据1 '''
    def clear_data_1(self):
        global img_path, color, contrast, brightness
        img_path = ""
        color = ""
        contrast = '1'
        brightness = '0'
        detect_img = ''
        result_path = ''
        loc = (0, 0)
        self.lineEdit_1.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.textBrowser_1.clear()
        self.textBrowser_2.clear()

    ''' 经纬度定位 '''

    ''' 离线地图 '''
    def browse_folder(self):
        global map_folder_path
        file_dialog = QtWidgets.QFileDialog()
        map_folder_path = file_dialog.getExistingDirectory(None, "选择文件夹")
        self.lineEdit_5.setText(map_folder_path)

    ''' 纬度 '''
    def input_la(self):
        global la
        la = self.lineEdit_6.text()

    ''' 经度 '''
    def input_lo(self):
        global lo
        lo = self.lineEdit_7.text()

    ''' 开始定位 '''
    def start_locate(self):
        global la_r, lo_r, screenshot_file

        self.textBrowser_3.setStyleSheet("font-size: 16px;")
        self.textBrowser_4.setStyleSheet("font-size: 16px;")

        offline_map_path = map_folder_path + '/{z}/{x}/{y}.jpg'
        # 地图路径
        current_dir = os.getcwd()
        map_dir = os.path.join(current_dir, "map")
        if not os.path.exists(map_dir):
            os.mkdir(map_dir)
            self.textBrowser_3.append('在当前目录创建map文件夹')
            QtWidgets.QApplication.processEvents()
        else:
            self.textBrowser_3.append('当前目录map文件夹已创建')
            QtWidgets.QApplication.processEvents()
        map_file = os.path.join(map_dir, "map.html")

        self.textBrowser_3.append('加载检测结果图像...')
        QtWidgets.QApplication.processEvents()
        target = cv2.imread(result_path)
        self.textBrowser_3.append('加载检测坐标...')
        QtWidgets.QApplication.processEvents()
        target_loc = loc

        self.textBrowser_3.append('生成离线地图...')
        QtWidgets.QApplication.processEvents()
        m = createmap(offline_map_path, [float(la), float(lo)], 15, map_file, False)
        height, width, _ = target.shape
        size = 3 * max(height, width)
        map, print_text, _ = getmapimg(size, map_file)
        self.textBrowser_3.append(print_text)
        QtWidgets.QApplication.processEvents()

        # 旋转模板匹配
        # 地图图像，识别图像模板，小目标坐标，是否显示匹配结果
        self.textBrowser_3.append('进行图像配准...')
        QtWidgets.QApplication.processEvents()
        map_match, loc_r = rotatematch(map, target, target_loc, False)

        # 输出经纬度
        # 坐标，地图文件，尺寸，是否截图
        self.textBrowser_3.append('图像配准完成！')
        self.textBrowser_3.append('计算目标经纬度...')
        QtWidgets.QApplication.processEvents()
        la_r, lo_r, screenshot_file = outputlalo(loc_r, map_file, size, True)
        self.textBrowser_3.append('经纬度定位完成！')
        QtWidgets.QApplication.processEvents()
        self.textBrowser_4.append(f'la={la_r}')
        self.textBrowser_4.append(f'lo={lo_r}')

    ''' 查看结果 '''
    def view_result_2(self):
        if not hasattr(self, 'result_window_2') or not self.result_window_2:

            self.result_window_2 = QtWidgets.QMainWindow()
            self.result_window_2.setWindowTitle("经纬度定位结果")
            self.result_window_2.setGeometry(100, 100, 800, 600)

            label = QtWidgets.QLabel(self.result_window_2)
            pixmap = QtGui.QPixmap(screenshot_file)
            label.setPixmap(pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)

            scroll_area = QtWidgets.QScrollArea(self.result_window_2)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(label)

            self.result_window_2.setCentralWidget(scroll_area)

            label.adjustSize()

        # 显示新窗口
        self.result_window_2.show()

    ''' 清除数据2 '''
    def clear_data_2(self):
        global lo, la
        lo = ''
        la = ''
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()
        self.textBrowser_3.clear()
        self.textBrowser_4.clear()


    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(761, 861)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(300, 30, 125, 24))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(90, 90, 102, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(90, 140, 102, 16))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(340, 140, 85, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(540, 140, 68, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(490, 260, 102, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(90, 510, 102, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(90, 560, 120, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(430, 560, 120, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(480, 680, 85, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(300, 450, 125, 24))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.lineEdit_1 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_1.setGeometry(QtCore.QRect(200, 90, 391, 20))
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(430, 140, 51, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_3.setGeometry(QtCore.QRect(620, 140, 51, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_4.setGeometry(QtCore.QRect(200, 140, 81, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_5 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_5.setGeometry(QtCore.QRect(200, 510, 391, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_6 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_6.setGeometry(QtCore.QRect(220, 560, 111, 20))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_7 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_7.setGeometry(QtCore.QRect(560, 560, 111, 20))
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.pushButton_1 = QtWidgets.QPushButton(Dialog)
        self.pushButton_1.setGeometry(QtCore.QRect(600, 90, 71, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_1.setFont(font)
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 190, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(340, 190, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(580, 190, 86, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setGeometry(QtCore.QRect(90, 610, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        self.pushButton_6.setGeometry(QtCore.QRect(340, 610, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(Dialog)
        self.pushButton_7.setGeometry(QtCore.QRect(580, 610, 86, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")
        self.textBrowser_1 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_1.setGeometry(QtCore.QRect(90, 240, 251, 171))
        self.textBrowser_1.setObjectName("textBrowser_1")
        self.textBrowser_2 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_2.setGeometry(QtCore.QRect(450, 290, 151, 71))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.textBrowser_3 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_3.setGeometry(QtCore.QRect(90, 660, 251, 171))
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.textBrowser_4 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_4.setGeometry(QtCore.QRect(450, 710, 151, 71))
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.pushButton_8 = QtWidgets.QPushButton(Dialog)
        self.pushButton_8.setGeometry(QtCore.QRect(600, 510, 71, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setObjectName("pushButton_8")
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(670, 0, 91, 91))
        self.graphicsView.setObjectName("graphicsView")

        scene = QtWidgets.QGraphicsScene()
        pixmap = QtGui.QPixmap("E:/Subjects/sw/gui/xiaohui1.jpg")
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.graphicsView.setScene(scene)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # 背景
        self.setWindowBackground(Dialog)
        
        self.pushButton_1.clicked.connect(self.browse_file)
        self.lineEdit_4.textChanged.connect(self.input_color)
        self.lineEdit_2.textChanged.connect(self.input_contrast)
        self.lineEdit_3.textChanged.connect(self.input_brightness)
        self.pushButton_2.clicked.connect(self.start_detect)
        self.pushButton_4.clicked.connect(self.view_result)
        self.pushButton_3.clicked.connect(self.clear_data_1)

        self.pushButton_8.clicked.connect(self.browse_folder)
        self.lineEdit_6.textChanged.connect(self.input_la)
        self.lineEdit_7.textChanged.connect(self.input_lo)
        self.pushButton_5.clicked.connect(self.start_locate)
        self.pushButton_6.clicked.connect(self.clear_data_2)
        self.pushButton_7.clicked.connect(self.view_result_2)


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "星载对地遥感图像小目标配准定位软件"))
        self.label.setText(_translate("Dialog", "小目标检测"))
        self.label_2.setText(_translate("Dialog", "输入图像路径"))
        self.label_3.setText(_translate("Dialog", "目标特征颜色"))
        self.label_4.setText(_translate("Dialog", "增加对比度"))
        self.label_5.setText(_translate("Dialog", "增加亮度"))
        self.label_6.setText(_translate("Dialog", "像素坐标"))
        self.label_7.setText(_translate("Dialog", "离线地图路径"))
        self.label_8.setText(_translate("Dialog", "目标区域纬度la"))
        self.label_9.setText(_translate("Dialog", "目标区域经度lo"))
        self.label_10.setText(_translate("Dialog", "目标经纬度"))
        self.label_11.setText(_translate("Dialog", "经纬度定位"))
        self.pushButton_1.setText(_translate("Dialog", "浏览"))
        self.pushButton_2.setText(_translate("Dialog", "开始检测"))
        self.pushButton_3.setText(_translate("Dialog", "清除数据"))
        self.pushButton_4.setText(_translate("Dialog", "查看检测结果"))
        self.pushButton_5.setText(_translate("Dialog", "开始定位"))
        self.pushButton_6.setText(_translate("Dialog", "清除数据"))
        self.pushButton_7.setText(_translate("Dialog", "查看定位结果"))
        self.pushButton_8.setText(_translate("Dialog", "浏览"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
