import os
import subprocess
import sys
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QModelIndex, QVariant
from PyQt5.QtGui import QGuiApplication, QIcon, QColor, QCursor
from PyQt5.QtWidgets import *
from system_hotkey import SystemHotkey
import shutil
import qdarkgraystyle
import edit2
import funcs


class MySystemModel(QFileSystemModel):
    def __init__(self):
        super(MySystemModel, self).__init__()
        self.run_list = {}

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.TextColorRole and not self.hasChildren(index):
            if index in self.run_list:
                if self.run_list[index] == 1:
                    return QVariant(QColor("#00FF00"))
                elif self.run_list[index] == 0:
                    return QVariant(QColor("#FF0000"))
            else:
                return super().data(index, role)
        else:
            return super().data(index, role)


class MenuTools(QMainWindow):
    sig_hotkey = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MenuTools, self).__init__(parent)
        a = QWidget()
        # 横向分辨率
        w = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId()).width()
        # 纵向分辨率
        h = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId()).height()
        a.destroy()
        self.setWindowTitle('半实物仿真自动化测试平台')
        self.setWindowIcon(QIcon("../icons/TestSystem.ico"))
        self.resize(int(0.8 * w), int(0.8 * h))
        self.create_menu()
        self.create_tool()
        self.create_statusbar()
        self.sig_hotkey.connect(self.process)
        SystemHotkey().register(('control', 'q'), callback=lambda x: self.send_event("开始截图"))
        self.tab_list = []

        # 设置各个区域的布局
        # 文件树布局
        file_layout = QVBoxLayout()
        # 按钮区域布局
        left_layout = QVBoxLayout()
        # 脚本区域可拖动
        mid_widget = QSplitter(Qt.Vertical)
        # 通信区域布局
        right_layout = QVBoxLayout()

        # 文件树区域
        # #显示当前目录，不显示即为根目录下
        self.dir_url = QLabel('')
        # #操作脚本文件的按钮们
        self.new_file_button = QPushButton()
        self.new_folder_button = QPushButton()
        self.delete_file_button = QPushButton()
        self.rename_file_button = QPushButton()
        self.run_directory_button = QPushButton()
        self.stop_run_directory_button = QPushButton()
        self.new_file_button.setIcon(QIcon("../icons/新建脚本.ico"))
        # self.new_folder_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap(32)))
        self.new_folder_button.setIcon(QIcon("../icons/新建文件夹.ico"))
        self.delete_file_button.setIcon(QIcon("../icons/删除脚本.ico"))
        self.rename_file_button.setIcon(QIcon("../icons/脚本改名.ico"))
        # self.run_directory_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap(66)))
        self.run_directory_button.setIcon(QIcon("../icons/批量运行.ico"))
        self.stop_run_directory_button.setIcon(QIcon("../icons/批量运行停止.ico"))
        self.new_file_button.setToolTip("新增脚本")
        self.new_folder_button.setToolTip("新建文件夹")
        self.delete_file_button.setToolTip("删除脚本")
        self.rename_file_button.setToolTip("修改脚本名")
        self.run_directory_button.setToolTip("运行目录中的脚本")
        self.stop_run_directory_button.setToolTip("停止运行目录中的脚本")
        self.new_file_button.clicked.connect(self.new_script)
        self.new_folder_button.clicked.connect(self.new_folder)
        self.delete_file_button.clicked.connect(self.delete_script)
        self.rename_file_button.clicked.connect(self.rename_script)
        self.run_directory_button.clicked.connect(self.run_directory)
        self.stop_run_directory_button.clicked.connect(self.stop_run_directory)
        self.stop_run_directory_button.setEnabled(False)
        self.file_btn_window = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.new_file_button)
        layout.addWidget(self.new_folder_button)
        layout.addWidget(self.delete_file_button)
        layout.addWidget(self.rename_file_button)
        layout.addWidget(self.run_directory_button)
        layout.addWidget(self.stop_run_directory_button)
        self.file_btn_window.setLayout(layout)
        # #文件目录树
        self.file_tree = QTreeView()
        self.dir_model = MySystemModel()
        self.dir_model.setRootPath("/")
        self.dir_model.setReadOnly(True)
        self.dir_model.setNameFilterDisables(False)
        self.dir_model.setNameFilters(['*.py', '*.txt', '*.jpg', '*.png'])
        self.file_tree.setModel(self.dir_model)
        self.file_tree.setColumnHidden(1, True)
        self.file_tree.setColumnHidden(2, True)
        self.file_tree.setColumnHidden(3, True)
        self.file_tree.header().setHidden(True)
        self.file_tree.doubleClicked.connect(self.open_script)
        file_layout.addWidget(self.dir_url)
        file_layout.addWidget(self.file_btn_window)
        file_layout.addWidget(self.file_tree)

        # 编写脚本需要用到的按钮区域
        self.groupbox_1 = QGroupBox("查找", self)
        layout = QVBoxLayout()
        self.wait_button = QPushButton("  Wait")
        self.waitVanish_button = QPushButton("  Wait Vanish")
        self.exists_button = QPushButton("  Exists")
        self.ocr_button = QPushButton("  Ocr")
        self.wait_button.setToolTip("等待该图像出现")
        self.waitVanish_button.setToolTip("等待该图像消失")
        self.exists_button.setToolTip("页面是否存在该图像")
        self.ocr_button.setToolTip("图像转文字")
        self.wait_button.setIcon(QIcon("../icons/Wait.ico"))
        self.waitVanish_button.setIcon(QIcon("../icons/Wait Vanish.ico"))
        self.exists_button.setIcon(QIcon("../icons/Exists.ico"))
        self.ocr_button.setIcon(QIcon("../icons/Ocr.ico"))
        # self.ocr_button.setStyleSheet()
        self.wait_button.clicked.connect(lambda: funcs.Functions.wait(self))
        self.waitVanish_button.clicked.connect(lambda: funcs.Functions.waitVanish(self))
        self.exists_button.clicked.connect(lambda: funcs.Functions.exists(self))
        self.ocr_button.clicked.connect(lambda: funcs.Functions.ocr(self))
        self.wait_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.waitVanish_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.exists_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.ocr_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        layout.addWidget(self.wait_button)
        layout.addWidget(self.waitVanish_button)
        layout.addWidget(self.exists_button)
        layout.addWidget(self.ocr_button)
        self.groupbox_1.setLayout(layout)

        self.groupbox_2 = QGroupBox("鼠标动作", self)
        layout = QVBoxLayout()
        self.click_button = QPushButton("  Click")
        self.doubleClick_button = QPushButton("  Double Click")
        self.rightClick_button = QPushButton("  Right Click")
        self.swipe_button = QPushButton("  Swipe")
        self.hover_button = QPushButton("  Hover")
        self.click_button.setToolTip("鼠标左键单击该图像")
        self.doubleClick_button.setToolTip("鼠标左键双击该图像")
        self.rightClick_button.setToolTip("鼠标右键单击该图像")
        self.swipe_button.setToolTip("拖拽,截图时左键选择起点，右键选择终点")
        self.hover_button.setToolTip("鼠标悬停在该图像处")
        self.click_button.setIcon(QIcon("../icons/Click.ico"))
        self.doubleClick_button.setIcon(QIcon("../icons/Double Click.ico"))
        self.rightClick_button.setIcon(QIcon("../icons/Right Click.ico"))
        self.swipe_button.setIcon(QIcon("../icons/Swipe.ico"))
        self.hover_button.setIcon(QIcon("../icons/Hover.ico"))
        self.click_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.doubleClick_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.rightClick_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.swipe_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.hover_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        layout.addWidget(self.click_button)
        layout.addWidget(self.doubleClick_button)
        layout.addWidget(self.rightClick_button)
        layout.addWidget(self.swipe_button)
        layout.addWidget(self.hover_button)
        self.click_button.clicked.connect(lambda: funcs.Functions.click(self))
        self.doubleClick_button.clicked.connect(lambda: funcs.Functions.double_click(self))
        self.rightClick_button.clicked.connect(lambda: funcs.Functions.right_click(self))
        self.swipe_button.clicked.connect(lambda: funcs.Functions.swipe(self))
        self.hover_button.clicked.connect(lambda: funcs.Functions.hover(self))
        self.groupbox_2.setLayout(layout)

        self.groupbox_3 = QGroupBox("键盘动作", self)
        layout = QVBoxLayout()
        self.text_button = QPushButton("  Text")
        self.keyevent_button = QPushButton("  Keyevent")
        self.snapshot_button = QPushButton("  Snapshot")
        self.sleep_button = QPushButton("  Sleep")
        self.text_button.setToolTip("键盘输入该段文字")
        self.keyevent_button.setToolTip("键盘按下该键码所对应的键")
        self.snapshot_button.setToolTip("截取全屏图像")
        self.sleep_button.setToolTip("等待n秒")
        self.text_button.setIcon(QIcon("../icons/Text.ico"))
        self.keyevent_button.setIcon(QIcon("../icons/Keyevent.ico"))
        self.snapshot_button.setIcon(QIcon("../icons/Snapshot.ico"))
        self.sleep_button.setIcon(QIcon("../icons/Sleep.ico"))
        self.text_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.keyevent_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.snapshot_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.sleep_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        layout.addWidget(self.text_button)
        layout.addWidget(self.keyevent_button)
        layout.addWidget(self.snapshot_button)
        layout.addWidget(self.sleep_button)
        self.text_button.clicked.connect(lambda: funcs.Functions.text(self))
        self.keyevent_button.clicked.connect(lambda: funcs.Functions.keyevent(self))
        self.snapshot_button.clicked.connect(lambda: funcs.Functions.snapshot(self))
        self.sleep_button.clicked.connect(lambda: funcs.Functions.sleep(self))
        self.groupbox_3.setLayout(layout)

        self.groupbox_4 = QGroupBox("断言", self)
        layout = QVBoxLayout()
        self.assert_picture_exist_button = QPushButton("  Assert Img")
        self.assert_file_exist_button = QPushButton("  Assert File")
        self.assert_word_exist_button = QPushButton("  Assert Word")
        self.assert_client_exist_button = QPushButton("  Assert Client")
        self.assert_ocr_true_button = QPushButton("  Assert Ocr")
        self.assert_recognize_lcd_button = QPushButton("  Assert Lcd")
        self.assert_picture_exist_button.setToolTip("断言该图像是否存在")
        self.assert_file_exist_button.setToolTip("断言该文件是否存在")
        self.assert_word_exist_button.setToolTip("断言该句日志是否在末尾")
        self.assert_ocr_true_button.setToolTip("断言OCR结果是否正确")
        self.assert_recognize_lcd_button.setToolTip("断言LCD数字的识别是否正确")
        self.assert_picture_exist_button.setIcon(QIcon("../icons/Assert_Img.ico"))
        self.assert_file_exist_button.setIcon(QIcon("../icons/Assert_File.ico"))
        self.assert_word_exist_button.setIcon(QIcon("../icons/Assert_Word.ico"))
        self.assert_client_exist_button.setIcon(QIcon("../icons/Assert_Client.ico"))
        self.assert_ocr_true_button.setIcon(QIcon("../icons/Assert_OCR.ico"))
        self.assert_recognize_lcd_button.setIcon(QIcon("../icons/Assert_LCD.ico"))
        self.assert_picture_exist_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_file_exist_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_word_exist_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_client_exist_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_ocr_true_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_recognize_lcd_button.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.assert_picture_exist_button.clicked.connect(lambda: funcs.Functions.assert_exist(self))
        self.assert_file_exist_button.clicked.connect(lambda: funcs.Functions.assert_file_exist(self))
        self.assert_word_exist_button.clicked.connect(lambda: funcs.Functions.assert_word_exist(self))
        self.assert_client_exist_button.clicked.connect(lambda: funcs.Functions.assert_client_exist(self))
        self.assert_ocr_true_button.clicked.connect(lambda: funcs.Functions.assert_ocr_true(self))
        self.assert_recognize_lcd_button.clicked.connect(lambda: funcs.Functions.assert_lcd_true(self))
        layout.addWidget(self.assert_picture_exist_button)
        layout.addWidget(self.assert_file_exist_button)
        layout.addWidget(self.assert_word_exist_button)
        layout.addWidget(self.assert_client_exist_button)
        layout.addWidget(self.assert_ocr_true_button)
        layout.addWidget(self.assert_recognize_lcd_button)
        self.groupbox_4.setLayout(layout)

        # 脚本区域
        # #脚本编写区
        self.edit_tab = QTabWidget()
        self.edit_tab.setTabsClosable(True)
        self.edit_tab.tabCloseRequested.connect(self.tab_close)

        # #控制台
        self.output_tab = QTabWidget()
        self.console_window = QWidget()
        self.console_text = QTextEdit()
        self.console_text.setLineWrapMode(QTextEdit.NoWrap)
        self.console_text.setReadOnly(True)
        layout = QHBoxLayout()
        layout.addWidget(self.console_text)
        self.console_window.setLayout(layout)
        self.output_tab.addTab(self.console_window, "控制台")

        # 通信区域
        self.groupbox_6 = QGroupBox("通信管理", self)
        self.formlayout = QFormLayout()

        self.btn_connect = QPushButton("  建立连接")
        self.btn_disconnect = QPushButton("  断开连接")
        self.btn_connect.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\建立连接.ico'))
        self.btn_disconnect.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\断开连接.ico'))
        self.btn_connect.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_disconnect.setStyleSheet("QPushButton { text-align: left;font-size:20px}")

        self.formlayout.addRow(self.btn_connect)
        self.formlayout.addRow(self.btn_disconnect)
        self.groupbox_6.setLayout(self.formlayout)

        self.groupbox_7 = QGroupBox("数据日志", self)
        self.formlayout1 = QFormLayout()
        self.textEdit_send = QTextEdit()

        self.btn_addDevice = QPushButton("  New Device")
        self.btn_response = QPushButton("  Add Key")
        self.btn_data = QPushButton("  Add Data")
        self.btn_deleteDevice = QPushButton("  Del Device")
        self.btn_deleteCommand = QPushButton("  Del Key")
        self.btn_open = QPushButton("  打开文件")
        self.btn_send = QPushButton("  立即执行")
        self.btn_close = QPushButton("  清除")

        self.btn_addDevice.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\新建设备.ico'))
        self.btn_response.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\AddKey.ico'))
        self.btn_data.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\添加数据.ico'))
        self.btn_deleteDevice.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\删除设备.ico'))
        self.btn_deleteCommand.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\Delay.ico'))
        self.btn_open.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\打开文件.ico'))
        self.btn_send.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\立即执行.ico'))
        self.btn_close.setIcon(QIcon(r'C:\Users\admin\Downloads\ico\清除.ico'))

        self.btn_addDevice.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_response.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_data.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_deleteDevice.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_deleteCommand.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_open.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_send.setStyleSheet("QPushButton { text-align: left;font-size:20px}")
        self.btn_close.setStyleSheet("QPushButton { text-align: left;font-size:20px}")

        self.formlayout1.addRow(self.textEdit_send)
        self.formlayout1.addRow(self.btn_addDevice)
        self.formlayout1.addRow(self.btn_response)
        self.formlayout1.addRow(self.btn_data)
        self.formlayout1.addRow(self.btn_deleteDevice)
        self.formlayout1.addRow(self.btn_deleteCommand)
        self.formlayout1.addRow(self.btn_open)
        self.formlayout1.addRow(self.btn_send)
        self.formlayout1.addRow(self.btn_close)
        self.groupbox_7.setLayout(self.formlayout1)

        self.btn_connect.clicked.connect(lambda: funcs.Functions.dialog_connect(self))
        self.btn_disconnect.clicked.connect(lambda: funcs.Functions.disconnect_clicked(self))
        self.btn_addDevice.clicked.connect(lambda: funcs.Functions.dialog_new_device(self))
        self.btn_response.clicked.connect(lambda: funcs.Functions.dialog_response(self))
        self.btn_data.clicked.connect(lambda: funcs.Functions.dialog_data(self))
        self.btn_deleteDevice.clicked.connect(lambda: funcs.Functions.dialog_delete_device(self))
        self.btn_deleteCommand.clicked.connect(lambda: funcs.Functions.dialog_delete_key(self))
        self.btn_open.clicked.connect(lambda: funcs.Functions.send_file(self))
        self.btn_send.clicked.connect(lambda: funcs.Functions.on_btn_send_clicked(self))
        self.btn_close.clicked.connect(lambda: funcs.Functions.on_btn_clear_clicked(self))

        # 将各控件加入对于的局部布局中
        left_layout.addWidget(self.groupbox_1, 4)
        left_layout.addWidget(self.groupbox_2, 5)
        left_layout.addWidget(self.groupbox_3, 4)
        left_layout.addWidget(self.groupbox_4, 6)

        mid_widget.addWidget(self.edit_tab)
        mid_widget.addWidget(self.output_tab)
        mid_widget.setStretchFactor(0, 40)
        mid_widget.setStretchFactor(1, 1)

        right_layout.addWidget(self.groupbox_6)
        right_layout.addWidget(self.groupbox_7)

        file_widget = QWidget()
        file_widget.setLayout(file_layout)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # 局部布局加到全局布局中
        widget = QSplitter(Qt.Horizontal)
        widget.addWidget(file_widget)
        widget.addWidget(left_widget)
        widget.addWidget(mid_widget)
        widget.addWidget(right_widget)
        widget.setStretchFactor(0, 1)
        widget.setStretchFactor(1, 1)
        widget.setStretchFactor(2, 6)
        widget.setStretchFactor(3, 1)
        self.setCentralWidget(widget)

    # 创建菜单栏
    def create_menu(self):
        bar = self.menuBar()
        bar.setStyleSheet('''MenuBar{background-color:#ccc;}''')
        dir_menu = bar.addMenu("目录")
        # select_menu = QAction('选择目录')
        dir_menu.addAction('选择目录')
        dir_menu.triggered.connect(self.choose_dir)

        check_menu = bar.addMenu("查看")
        check_menu.addAction("查看报告")
        check_menu.triggered.connect(self.show_report)
        bar.setStyleSheet("QMenuBar{spacing:12px;}")

    # 创建工具栏
    def create_tool(self):
        tb = self.addToolBar("file")
        screen_shot = QAction(QIcon("../icons/自由截图.png"), "自由截图", self)
        screen_shot.setToolTip("全局快捷键Ctrl+Q")
        tb.addAction(screen_shot)
        screen_shot.triggered.connect(lambda: funcs.Functions.screenshot(self))

        insert_photo = QAction(QIcon("../icons/插入图片.png"), "插入图片", self)
        tb.addAction(insert_photo)
        insert_photo.triggered.connect(lambda: funcs.Functions.insert_picture(self))

        # save_file_action = QAction(QApplication.style().standardIcon(QStyle.StandardPixmap(43)), "保存文件", self)
        save_file_action = QAction(QIcon("../icons/保存文件.png"), "保存文件", self)
        save_file_action.setShortcut('Ctrl+S')
        tb.addAction(save_file_action)
        save_file_action.triggered.connect(self.save_file)

        # run = QAction(QApplication.style().standardIcon(QStyle.StandardPixmap(61)), "运行", self)
        run = QAction(QIcon("../icons/运行脚本文件.png"), "运行", self)
        tb.addAction(run)
        run.triggered.connect(lambda: funcs.Functions.run(self))

        part_run = QAction(QIcon(r"../icons/运行选中语句.png"), "运行选中语句", self)
        tb.addAction(part_run)
        part_run.triggered.connect(lambda: funcs.Functions.part_run(self))
        self.stop_action = QAction(QIcon("../icons/停止运行脚本.png"), "停止", self)
        tb.addAction(self.stop_action)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(lambda: funcs.Functions.stop_run(self))
        tb.setStyleSheet("QToolBar{spacing:6px;height:10px;}")
        tb.setIconSize(QSize(36, 36))
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tb.setStyleSheet("background:#404244;color:white")

    # 状态栏
    def create_statusbar(self):
        # 刚启动软件的时候会有，一旦有动作它就消失了
        self.statusBar().showMessage("Ready")

    # 操作脚本的函数们
    def choose_dir(self):
        selected_dir = QFileDialog.getExistingDirectoryUrl(self, '选择目录')
        if selected_dir:
            self.dir_url.setText(str(selected_dir)[27:-2])
            self.file_tree.setRootIndex(self.dir_model.index(str(selected_dir)[27:-2]))

    def new_script(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        if os.path.isdir(path):
            f = open(path + "/新脚本.py", 'w')
            f.close()
            os.makedirs(os.path.join(path, "新脚本"))
        else:
            f = open(path[:path.rindex('/')] + "/新脚本.py", 'w')
            f.close()
            os.makedirs(os.path.join(path[:path.rindex('/')], "新脚本"))

    def new_folder(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        if os.path.isdir(path):
            os.makedirs(os.path.join(path, "新文件夹"))
        else:
            os.makedirs(os.path.join(path[:path.rindex('/')], "新文件夹"))

    def open_script(self, tree_id):
        path = self.dir_model.filePath(tree_id)
        if os.path.isfile(path):
            script_edit = QWidget()
            script_name_index = path.rindex('/')
            self.tab_list.clear()
            for i in range(self.edit_tab.count()):
                self.tab_list.append(self.edit_tab.tabText(i))
            if path[script_name_index + 1:] not in self.tab_list:
                self.edit_tab.addTab(script_edit, path[script_name_index + 1:])
                script_edit.path = path
                script_edit.pic_path = path.replace('.py', '/')
                script_edit.edit = edit2.QCodeEditor()
                script_edit.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
                script_edit.edit.setTabStopWidth(self.fontMetrics().width(' ') * 4)
                script_edit.edit_layout = QHBoxLayout()
                script_edit.edit_layout.addWidget(script_edit.edit)
                script_edit.setLayout(script_edit.edit_layout)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:  # 文件读操作
                    script_edit.edit.setPlainText(f.read())
                    f.close()
                script_edit.edit.setContextMenuPolicy(Qt.CustomContextMenu)
                script_edit.edit.customContextMenuRequested.connect(self.edit_right)
                self.edit_tab.setCurrentWidget(script_edit)
                script_edit.edit.textChanged.connect(self.text_changed)
            else:
                self.edit_tab.setCurrentIndex(self.tab_list.index(path[script_name_index + 1:]))

    def delete_script(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)

    def rename_script(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        new_name = QInputDialog.getText(self, '脚本改名', '输入想要改为的名字')
        if new_name[1] is True:
            if os.path.isfile(path):
                name = os.path.join(os.path.split(path)[0], new_name[0]+'.py')
                os.rename(path, name)
                pic_name = os.path.join(os.path.split(path)[0], new_name[0])
                os.rename(path[:-3], pic_name)
            else:
                new_folder_name = os.path.join(os.path.split(path)[0], new_name[0])
                os.rename(path, new_folder_name)
        """如果该文件已经打开，则tabText也会相应改变
        if os.path.split(path)[1] in 所有tabText:
            self.edit_tab.setTabText()
        """

    def save_file(self):
        if self.edit_tab.tabText(self.edit_tab.currentIndex()) == '*新脚本':
            save_path_information = QFileDialog.getSaveFileName(self, '选择保存脚本的路径', '.', '*.py')
            if save_path_information[0]:
                self.edit_tab.currentWidget().path = save_path_information[0]
                f = open(save_path_information[0], 'w', encoding='utf-8')
                f.write(self.edit_tab.currentWidget().edit.toPlainText())
                f.close()
                last_index = save_path_information[0].rindex('/')
                self.edit_tab.setTabText(self.edit_tab.currentIndex(), save_path_information[0][last_index + 1:])
        else:
            f = open(self.edit_tab.currentWidget().path, 'w', encoding='utf-8')
            f.write(self.edit_tab.currentWidget().edit.toPlainText())
            f.close()
            if self.edit_tab.tabText(self.edit_tab.currentIndex())[0] == '*':
                self.edit_tab.setTabText(self.edit_tab.currentIndex(),
                                         self.edit_tab.tabText(self.edit_tab.currentIndex())[1:])

    def save_another_file(self):
        save_another_path = QFileDialog.getSaveFileName(self, '选择要另存为的路径', '.', '*.py')
        if save_another_path[0]:
            f = open(save_another_path[0], 'w')
            f.write(self.edit_tab.currentWidget().edit.toPlainText())
            f.close()

    def run_directory(self):
        self.showMinimized()
        self.stop_run_directory_button.setEnabled(True)
        self.run_directory_thread = funcs.MyThread(self, path=self.dir_model.filePath(self.file_tree.currentIndex()))
        self.run_directory_thread.start()
        self.run_directory_thread.wait()

    def stop_run_directory(self):
        self.run_directory_thread.setTerminationEnabled(True)
        self.run_directory_thread.terminate()
        self.run_directory_thread.wait()
        self.run_directory_thread.deleteLater()
        self.stop_run_directory_button.setEnabled(False)

    # 查看报告函数
    def show_report(self):
        subprocess.Popen("allure serve ./result", shell=True)

    # 脚本栏的右键点击事件
    # 新增右键
    """script_edit.edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    script_edit.edit.customContextMenuRequested.connect(self.edit_right)
    self.edit_tab.setCurrentWidget(script_edit)
    script_edit.edit.textChanged.connect(self.text_changed)
    # 右键新增结束"""
    def edit_right(self):
        pop_menu = QMenu(self)
        # qp = pop_menu.addAction(u'全屏')
        gb = pop_menu.addAction(u'跳转到该文件所在位置')
        replace = pop_menu.addAction(u'替换')
        # qp.triggered.connect(self.edit_screen)
        gb.triggered.connect(self.edit_jump)
        replace.triggered.connect(self.edit_replace)
        pop_menu.exec_(QCursor.pos())

    def edit_jump(self):
        file_path = self.edit_tab.currentWidget().edit.textCursor().selectedText()
        if os.path.exists(file_path):
            os.startfile(file_path)

    def edit_replace(self):
        replace_value = QInputDialog.getText(self, '要替换为的内容', '')
        if replace_value[1] is True:
            be_replaced = self.edit_tab.currentWidget().edit.textCursor().selectedText()
            after_replace = self.edit_tab.currentWidget().edit.toPlainText().replace(be_replaced, replace_value[0])
            self.edit_tab.currentWidget().edit.setPlainText(after_replace)

    # 一些需要用的函数
    def tab_close(self, index):
        self.edit_tab.removeTab(index)

    def process(self, word):
        print(word)
        funcs.Functions.screenshot_function(self)

    def send_event(self, word):
        self.sig_hotkey.emit(word)

    def text_changed(self):
        if not self.edit_tab.tabText(self.edit_tab.currentIndex())[0] == '*':
            self.edit_tab.setTabText(self.edit_tab.currentIndex(),
                                     '*' + self.edit_tab.tabText(self.edit_tab.currentIndex()))

    def show_normal(self):
        self.showNormal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MenuTools()
    with open('./style.qss') as f:
        style = f.read()
    form.setStyleSheet(style)
    form.show()
    sys.exit(app.exec_())
