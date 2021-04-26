import os
import sys
from os import startfile
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtWidgets import *
from system_hotkey import SystemHotkey

import edit2
import funcs


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
        self.delete_file_button = QPushButton()
        self.rename_file_button = QPushButton(QApplication.style().standardIcon(QStyle.StandardPixmap(46)), '')
        self.list_add_button = QPushButton()
        self.run_list_button = QPushButton()
        self.new_file_button.setIcon(QIcon("../icons/add.ico"))
        self.delete_file_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap(47)))
        self.list_add_button.setIcon(QIcon("../icons/listadd.ico"))
        self.run_list_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap(66)))
        self.new_file_button.setToolTip("新增脚本")
        self.delete_file_button.setToolTip("删除脚本")
        self.rename_file_button.setToolTip("修改脚本名")
        self.list_add_button.setToolTip("加入脚本到运行队列")
        self.run_list_button.setToolTip("运行队列中的脚本")
        self.new_file_button.clicked.connect(self.new_script)
        self.delete_file_button.clicked.connect(self.delete_script)
        self.rename_file_button.clicked.connect(self.rename_script)
        self.list_add_button.clicked.connect(self.list_add)
        self.run_list_button.clicked.connect(self.run_list)
        self.file_btn_window = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.new_file_button)
        layout.addWidget(self.delete_file_button)
        layout.addWidget(self.rename_file_button)
        layout.addWidget(self.list_add_button)
        layout.addWidget(self.run_list_button)
        self.file_btn_window.setLayout(layout)
        # #文件目录树
        self.file_tree = QTreeView()
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath("/")
        self.dir_model.setReadOnly(True)
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
        self.wait_button = QPushButton("wait")
        self.waitVanish_button = QPushButton("waitVanish")
        self.exists_button = QPushButton("exists")
        self.ocr_button = QPushButton("ocr")
        self.wait_button.setToolTip("等待该图像出现")
        self.waitVanish_button.setToolTip("等待该图像消失")
        self.exists_button.setToolTip("页面是否存在该图像")
        self.ocr_button.setToolTip("图像转文字")
        self.wait_button.setIcon(QIcon('../icons/wait.ico'))
        self.waitVanish_button.setIcon(QIcon('../icons/waitVanish.ico'))
        self.exists_button.setIcon(QIcon('../icons/exist.ico'))
        self.ocr_button.setIcon(QIcon('../icons/ocr.ico'))
        # self.ocr_button.setStyleSheet()
        self.wait_button.clicked.connect(lambda: funcs.Functions.wait(self))
        self.waitVanish_button.clicked.connect(lambda: funcs.Functions.waitVanish(self))
        self.exists_button.clicked.connect(lambda: funcs.Functions.exists(self))
        self.ocr_button.clicked.connect(lambda: funcs.Functions.ocr(self))
        layout.addWidget(self.wait_button)
        layout.addWidget(self.waitVanish_button)
        layout.addWidget(self.exists_button)
        layout.addWidget(self.ocr_button)
        self.groupbox_1.setLayout(layout)

        self.groupbox_2 = QGroupBox("鼠标动作", self)
        layout = QVBoxLayout()
        self.click_button = QPushButton("click")
        self.doubleClick_button = QPushButton("doubleClick")
        self.rightClick_button = QPushButton("rightClick")
        self.swipe_button = QPushButton("swipe")
        self.hover_button = QPushButton("hover")
        self.click_button.setToolTip("鼠标左键单击该图像")
        self.doubleClick_button.setToolTip("鼠标左键双击该图像")
        self.rightClick_button.setToolTip("鼠标右键单击该图像")
        self.swipe_button.setToolTip("拖拽,截图时左键选择起点，右键选择终点")
        self.hover_button.setToolTip("鼠标悬停在该图像处")
        self.click_button.setIcon(QIcon('../icons/click.ico'))
        self.doubleClick_button.setIcon(QIcon('../icons/double_click.ico'))
        self.rightClick_button.setIcon(QIcon('../icons/right_click.ico'))
        self.swipe_button.setIcon(QIcon('../icons/swipe.ico'))
        self.hover_button.setIcon(QIcon('../icons/hover.ico'))
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
        self.text_button = QPushButton("text")
        self.keyevent_button = QPushButton("keyevent")
        self.snapshot_button = QPushButton("snapshot")
        self.sleep_button = QPushButton("sleep")
        self.text_button.setToolTip("键盘输入该段文字")
        self.keyevent_button.setToolTip("键盘按下该键码所对应的键")
        self.snapshot_button.setToolTip("截取全屏图像")
        self.sleep_button.setToolTip("等待n秒")
        self.text_button.setIcon(QIcon('../icons/text.ico'))
        self.keyevent_button.setIcon(QIcon('../icons/keyevent.ico'))
        self.snapshot_button.setIcon(QIcon('../icons/snapshot.ico'))
        self.sleep_button.setIcon(QIcon('../icons/sleep.ico'))
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
        self.assert_equal_button = QPushButton("assert_picture_equal")
        self.assert_picture_exist_button = QPushButton("assert_picture_exist")
        self.assert_file_exist_button = QPushButton("assert_file_exist")
        self.assert_word_exist_button = QPushButton("assert_word_exist")
        self.assert_equal_button.setToolTip("断言两个图像是否相同")
        self.assert_picture_exist_button.setToolTip("断言该图像是否存在")
        self.assert_file_exist_button.setToolTip("断言该文件是否存在")
        self.assert_word_exist_button.setToolTip("断言该句日志是否在末尾")
        self.assert_equal_button.setIcon(QIcon('../icons/assert_equal.ico'))
        self.assert_picture_exist_button.setIcon(QIcon('../icons/assert_exist.ico'))
        self.assert_file_exist_button.setIcon(QIcon('../icons/assert_file.ico'))
        self.assert_word_exist_button.setIcon(QIcon('../icons/assert_word.ico'))
        self.assert_equal_button.clicked.connect(lambda: funcs.Functions.assert_equal(self))
        self.assert_picture_exist_button.clicked.connect(lambda: funcs.Functions.assert_exist(self))
        self.assert_file_exist_button.clicked.connect(lambda: funcs.Functions.assert_file_exist(self))
        self.assert_word_exist_button.clicked.connect(lambda: funcs.Functions.assert_word_exist(self))
        layout.addWidget(self.assert_equal_button)
        layout.addWidget(self.assert_picture_exist_button)
        layout.addWidget(self.assert_file_exist_button)
        layout.addWidget(self.assert_word_exist_button)
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

        self.btn_connect = QPushButton("建立连接")

        self.btn_disconnect = QPushButton("断开连接")
        self.btn_disconnect.setEnabled(False)
        self.formlayout.addRow(self.btn_connect)
        self.formlayout.addRow(self.btn_disconnect)
        self.groupbox_6.setLayout(self.formlayout)

        self.groupbox_7 = QGroupBox("数据日志", self)
        self.formlayout1 = QFormLayout()

        self.textEdit_send = QTextEdit()

        self.btn_addDevice = QPushButton("NewDevice")

        self.btn_response = QPushButton("AddKey")

        self.btn_data = QPushButton("AddData")

        self.btn_deleteDevice = QPushButton("DeleteDevice")

        self.btn_deleteCommand = QPushButton("DeleteKey")

        self.btn_open = QPushButton("打开文件")

        self.btn_open.setEnabled(False)

        # self.btn_open.setFixedSize(280,25)
        self.btn_send = QPushButton("立即执行")

        self.btn_send.setEnabled(False)
        self.btn_close = QPushButton("清除")
        # self.btn_close.setFixedSize(115,27)
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
        self.btn_addDevice.clicked.connect(lambda: funcs.Functions.dialog_newDevice(self))
        self.btn_response.clicked.connect(lambda: funcs.Functions.dialog_response(self))
        self.btn_data.clicked.connect(lambda: funcs.Functions.dialog_data(self))
        self.btn_deleteDevice.clicked.connect(lambda: funcs.Functions.dialog_deleteDevice(self))
        self.btn_deleteCommand.clicked.connect(lambda: funcs.Functions.dialog_deleteKey(self))
        self.btn_open.clicked.connect(lambda: funcs.Functions.send_file(self))
        self.btn_send.clicked.connect(lambda: funcs.Functions.on_btnSend_clicked(self))
        self.btn_close.clicked.connect(lambda: funcs.Functions.on_btn_clear_clicked(self))

        # 将各控件加入对于的局部布局中
        left_layout.addWidget(self.groupbox_1, 4)
        left_layout.addWidget(self.groupbox_2, 5)
        left_layout.addWidget(self.groupbox_3, 4)
        left_layout.addWidget(self.groupbox_4, 4)

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
        widget.setStretchFactor(0, 2)
        widget.setStretchFactor(1, 1)
        widget.setStretchFactor(2, 7)
        widget.setStretchFactor(3, 2)
        self.setCentralWidget(widget)

    # 创建菜单栏
    def create_menu(self):
        bar = self.menuBar()

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
        screen_shot = QAction(QIcon("../icons/screenCapture.png"), "自由截图", self)
        screen_shot.setToolTip("全局快捷键Ctrl+Q")
        tb.addAction(screen_shot)
        screen_shot.triggered.connect(lambda: funcs.Functions.screenshot(self))

        insert_photo = QAction(QIcon("../icons/insert.png"), "插入图片", self)
        tb.addAction(insert_photo)
        insert_photo.triggered.connect(lambda: funcs.Functions.insert_picture(self))

        ins = QAction(self)
        tb.addAction(ins)

        save_file_action = QAction(QApplication.style().standardIcon(QStyle.StandardPixmap(43)), "保存文件", self)
        save_file_action.setShortcut('Ctrl+S')
        tb.addAction(save_file_action)
        save_file_action.triggered.connect(self.save_file)

        run = QAction(QApplication.style().standardIcon(QStyle.StandardPixmap(61)), "运行", self)
        tb.addAction(run)
        run.triggered.connect(lambda: funcs.Functions.run(self))

        part_run = QAction(QIcon("../icons/fast-forward.png"), "运行选中语句", self)
        tb.addAction(part_run)
        part_run.triggered.connect(lambda: funcs.Functions.part_run(self))
        self.stop_action = QAction(QIcon("../icons/stop.png"), "停止", self)
        tb.addAction(self.stop_action)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(lambda: funcs.Functions.stop_run(self))
        tb.setStyleSheet("QToolBar{spacing:6px;height:10px;}")
        tb.setIconSize(QSize(36, 36))
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

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
        else:
            f = open(path[:path.rindex('/')] + "/新脚本.py", 'w')
            f.close()

    def open_script(self, tree_id):
        path = self.dir_model.filePath(tree_id)
        script_edit = QWidget()
        script_name_index = path.rindex('/')
        """这里想实现已打开的选项卡就不会再打开了，但不知道怎么获得已打开的全部选项卡名字信息
        if path[script_name_index + 1:] not in 所以选项卡信息:
        """
        self.edit_tab.addTab(script_edit, path[script_name_index + 1:])
        script_edit.path = path
        script_edit.cwd = path[0:script_name_index]
        script_edit.edit_name = path[script_name_index + 1:]
        script_edit.edit = edit2.QCodeEditor()
        script_edit.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        script_edit.edit.setTabStopWidth(self.fontMetrics().width(' ') * 4)
        script_edit.edit_layout = QHBoxLayout()
        script_edit.edit_layout.addWidget(script_edit.edit)
        script_edit.setLayout(script_edit.edit_layout)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:  # 文件读操作
            script_edit.edit.setPlainText(f.read())
            f.close()
        self.edit_tab.setCurrentWidget(script_edit)
        script_edit.edit.textChanged.connect(self.text_changed)

    def delete_script(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)

    def rename_script(self):
        path = self.dir_model.filePath(self.file_tree.currentIndex())
        new_name = QInputDialog.getText(self, '脚本改名', '输入想要改为的名字')
        if new_name[1] is True:
            name = os.path.join(os.path.split(path)[0], new_name[0]+'.py')
            os.rename(path, name)
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
                self.edit_tab.currentWidget().cwd = save_path_information[0][0:last_index]
                self.edit_tab.setTabText(self.edit_tab.currentIndex(), save_path_information[0][last_index + 1:])
                self.edit_tab.currentWidget().edit_name = save_path_information[0][last_index + 1:]
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

    def list_add(self):
        pass

    def run_list(self):
        pass

    # 查看报告函数
    def show_report(self):
        startfile(funcs.grandfather_dir[0] + ':/TestLog')

    # 脚本栏的右键点击事件
    # 新增右键
    """script_edit.edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    script_edit.edit.customContextMenuRequested.connect(self.edit_right)
    self.edit_tab.setCurrentWidget(script_edit)
    script_edit.edit.textChanged.connect(self.text_changed)
    # 右键新增结束"""
    '''def edit_right(self):
        pop_menu = QMenu(self)
        # qp = pop_menu.addAction(u'全屏')
        gb = pop_menu.addAction(u'关闭')
        # qp.triggered.connect(self.edit_screen)
        gb.triggered.connect(self.edit_close)
        pop_menu.exec_(QCursor.pos())

    def edit_close(self):
        self.edit_tab.removeTab(self.edit_tab.currentIndex())'''
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MenuTools()
    form.show()
    # form.new_file()
    sys.exit(app.exec_())
