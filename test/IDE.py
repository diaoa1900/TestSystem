import sys

import win32con
import win32gui
import win32print
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from test import funcs
from test import edit2


class MenuTools(QMainWindow):
    def __init__(self, parent=None):
        super(MenuTools, self).__init__(parent)
        hdc = win32gui.GetDC(0)
        # 横向分辨率
        w = win32print.GetDeviceCaps(hdc, win32con.DESKTOPHORZRES)
        # 纵向分辨率
        h = win32print.GetDeviceCaps(hdc, win32con.DESKTOPVERTRES)
        self.setWindowTitle('testSystem')
        # self.resize(1700, 900)
        self.resize(0.8 * w, 0.8 * h)
        self.create_menu()
        self.create_tool()
        self.create_statusbar()
        # os.startfile("D:\Learn\Snipaste-2.5.1-Beta-x64\Snipaste.exe")

        # 全局水平布局
        all_layout = QHBoxLayout()
        # 设置局部布局
        # 左侧垂直布局
        left_layout = QVBoxLayout()
        # 中间垂直布局
        mid_widget = QSplitter(Qt.Vertical)
        # 右边垂直布局
        right_layout = QVBoxLayout()

        # 左侧栏
        self.groupbox_1 = QGroupBox("查找", self)
        layout = QVBoxLayout()
        self.wait_button = QPushButton("wait")
        self.wait_button.setToolTip("等待该图像出现")
        self.waitVanish_button = QPushButton("waitVanish")
        self.waitVanish_button.setToolTip("等待该图像消失")
        self.exists_button = QPushButton("exists")
        self.exists_button.setToolTip("页面是否存在该图像")
        layout.addWidget(self.wait_button)
        layout.addWidget(self.waitVanish_button)
        layout.addWidget(self.exists_button)
        self.groupbox_1.setLayout(layout)

        self.groupbox_2 = QGroupBox("鼠标动作", self)
        layout = QVBoxLayout()
        self.click_button = QPushButton("click")
        self.click_button.setToolTip("鼠标左键单击该图像")
        self.doubleClick_button = QPushButton("doubleClick")
        self.doubleClick_button.setToolTip("鼠标左键双击该图像")
        self.rightClick_button = QPushButton("rightClick")
        self.rightClick_button.setToolTip("鼠标右键单击该图像")
        self.swipe_button = QPushButton("swipe")
        self.swipe_button.setToolTip("鼠标左键按住拖拽至指定位置")
        self.hover_button = QPushButton("hover")
        self.hover_button.setToolTip("鼠标悬停在该图像处")
        layout.addWidget(self.click_button)
        layout.addWidget(self.doubleClick_button)
        layout.addWidget(self.rightClick_button)
        layout.addWidget(self.swipe_button)
        layout.addWidget(self.hover_button)
        self.groupbox_2.setLayout(layout)

        self.groupbox_3 = QGroupBox("键盘动作", self)
        layout = QVBoxLayout()
        self.text_button = QPushButton("text")
        self.text_button.setToolTip("键盘输入该段文字")
        self.keyevent_button = QPushButton("keyevent")
        self.keyevent_button.setToolTip("键盘按下该键码所对应的键")
        self.snapshot_button = QPushButton("snapshot")
        self.snapshot_button.setToolTip("截取全屏图像")
        layout.addWidget(self.text_button)
        layout.addWidget(self.keyevent_button)
        layout.addWidget(self.snapshot_button)
        self.groupbox_3.setLayout(layout)

        self.groupbox_4 = QGroupBox("断言", self)
        layout = QVBoxLayout()
        self.assert_equal_button = QPushButton("assert_equal")
        self.assert_equal_button.setToolTip("断言两个图像是否相同")
        self.assert_exist_button = QPushButton("assert_exist")
        self.assert_exist_button.setToolTip("断言该图像是否存在")
        layout.addWidget(self.assert_equal_button)
        layout.addWidget(self.assert_exist_button)
        self.groupbox_4.setLayout(layout)

        # 脚本编辑栏

        '''self.dockerable_edit = QDockWidget('脚本编辑区', self)
        self.dockerable_edit.setWidget(self.edit1)
        self.addDockWidget(Qt.NoDockWidgetArea, self.dockerable_edit)'''

        self.edit_tab = QTabWidget()

        # 控制台栏
        self.output_tab = QTabWidget()
        self.console_window = QWidget()
        self.console_text = QTextEdit()
        self.console_text.setLineWrapMode(QTextEdit.NoWrap)  # 怎么换行呢？是个问题
        self.console_text.setReadOnly(True)
        layout = QHBoxLayout()
        layout.addWidget(self.console_text)
        self.console_window.setLayout(layout)
        self.run_result_window = QWidget()
        self.run_result = QTextEdit()
        self.run_result.setReadOnly(True)
        layout = QHBoxLayout()
        layout.addWidget(self.run_result)
        self.run_result_window.setLayout(layout)
        self.output_tab.addTab(self.run_result_window, "函数运行结果")
        self.output_tab.addTab(self.console_window, "控制台")

        # 右侧栏
        self.groupbox_6 = QGroupBox("通信管理", self)
        layout = QVBoxLayout()
        self.connect_button = QPushButton("建立连接")
        self.disconnect_button = QPushButton("断开连接")
        self.textEdit = QTextEdit()
        self.send_button = QCommandLinkButton("发送")

        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.send_button, 0, Qt.AlignCenter)
        self.groupbox_6.setLayout(layout)

        self.wait_button.clicked.connect(lambda: funcs.Functions.wait(self))
        self.waitVanish_button.clicked.connect(lambda: funcs.Functions.waitVanish(self))
        self.exists_button.clicked.connect(lambda: funcs.Functions.exists(self))
        self.click_button.clicked.connect(lambda: funcs.Functions.click(self))
        self.doubleClick_button.clicked.connect(lambda: funcs.Functions.double_click(self))
        self.rightClick_button.clicked.connect(lambda: funcs.Functions.right_click(self))
        self.swipe_button.clicked.connect(lambda: funcs.Functions.swipe(self))
        self.hover_button.clicked.connect(lambda: funcs.Functions.hover(self))
        self.text_button.clicked.connect(lambda: funcs.Functions.text(self))
        self.keyevent_button.clicked.connect(lambda: funcs.Functions.keyevent(self))
        self.snapshot_button.clicked.connect(lambda: funcs.Functions.snapshot(self))
        self.assert_equal_button.clicked.connect(lambda: funcs.Functions.assert_equal(self))
        self.assert_exist_button.clicked.connect(lambda: funcs.Functions.assert_exist(self))

        # 将控件加入布局
        left_layout.addWidget(self.groupbox_1, 3)
        left_layout.addWidget(self.groupbox_2, 5)
        left_layout.addWidget(self.groupbox_3, 3)
        left_layout.addWidget(self.groupbox_4, 2)

        mid_widget.addWidget(self.edit_tab)
        mid_widget.addWidget(self.output_tab)
        mid_widget.setStretchFactor(0, 40)
        mid_widget.setStretchFactor(1, 1)

        right_layout.addWidget(self.groupbox_6)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        widget = QSplitter(Qt.Horizontal)
        widget.addWidget(left_widget)
        widget.addWidget(mid_widget)
        widget.addWidget(right_widget)
        widget.setStretchFactor(0, 1)
        widget.setStretchFactor(1, 7)
        widget.setStretchFactor(2, 2)
        self.setCentralWidget(widget)

        # 局部布局加到全局布局中

    # 创建菜单栏
    def create_menu(self):
        bar = self.menuBar()
        file_menu = bar.addMenu("文件")
        new_action = QAction(QIcon(), '新建', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('Create a new file')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon(), '打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open an existing file')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(), '保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save the document to disk')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        saves_action = QAction(QIcon(), '另存为', self)
        saves_action.setStatusTip('Save the document under a new name')
        saves_action.triggered.connect(self.save_another_file)
        file_menu.addAction(saves_action)

        check_menu = bar.addMenu("&查看")
        check_menu.addAction("查看报告")
        check_menu.triggered.connect(self.show_report)
        bar.setStyleSheet("QMenuBar{spacing:12px;}")

    # 创建工具栏
    def create_tool(self):
        tb = self.addToolBar("file")
        screen_shot = QAction(QIcon("../image/camera.png"), "自由截图", self)
        tb.addAction(screen_shot)
        screen_shot.triggered.connect(lambda: funcs.Functions.screenshot(self))

        insert_photo = QAction(QIcon("../image/image.png"), "插入图片", self)
        tb.addAction(insert_photo)
        insert_photo.triggered.connect(lambda: funcs.Functions.insert_picture(self))

        ins = QAction(self)
        tb.addAction(ins)
        ins1 = QAction(self)
        tb.addAction(ins1)

        run = QAction(QIcon("../image/play-circle.png"), "运行", self)
        tb.addAction(run)
        run.triggered.connect(lambda: funcs.Functions.run(self))

        run1 = QAction(QIcon("../image/fast-forward.png"), "逐步运行", self)
        tb.addAction(run1)
        stop = QAction(QIcon("../image/slash.png"), "停止", self)
        tb.addAction(stop)
        tb.setStyleSheet("QToolBar{spacing:6px;height:10px;}")
        tb.setIconSize(QSize(36, 36))
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    # 状态栏
    def create_statusbar(self):
        # 刚启动软件的时候会有，一旦有动作它就消失了
        self.statusBar().showMessage("Ready")

    # 新建文件
    def new_file(self):
        script_edit = QWidget()
        self.edit_tab.addTab(script_edit, '新脚本')
        # flag为False时保存文件需要弹出文件对话框
        script_edit.flag = False
        script_edit.edit = edit2.QCodeEditor()
        script_edit.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        f = open('script_template.py', 'r', encoding='utf-8')
        script_edit.edit.setPlainText(f.read())
        try:
            completer = QCompleter(['print', 'click', 'double_click'], script_edit.edit)
            script_edit.edit.setCompleter(completer)
        except Exception as e:
            print(e)
        script_edit.edit_layout = QVBoxLayout()
        script_edit.edit_layout.addWidget(script_edit.edit)
        script_edit.setLayout(script_edit.edit_layout)
        # 新增右键
        script_edit.edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        script_edit.edit.customContextMenuRequested.connect(self.edit_right)
        script_edit.setWindowFlags(Qt.WindowFullscreenButtonHint | Qt.WindowCloseButtonHint)
        # 右键新增结束

    # 打开文件
    def open_file(self):
        open_path_information = QFileDialog.getOpenFileName(self, '打开文件', '.', '*.py')
        if open_path_information[0]:
            last_index = open_path_information[0].rindex('/')
            script_edit = QWidget()
            self.edit_tab.addTab(script_edit, open_path_information[0][last_index + 1:])
            # flag为True时保存文件无需弹出文件对话框
            script_edit.flag = True
            script_edit.path = open_path_information[0]
            script_edit.cwd = open_path_information[0][0:last_index]
            script_edit.edit_name = open_path_information[0][last_index + 1:]
            script_edit.edit = edit2.QCodeEditor()
            script_edit.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
            script_edit.edit_layout = QHBoxLayout()
            script_edit.edit_layout.addWidget(script_edit.edit)
            script_edit.setLayout(script_edit.edit_layout)
            with open(open_path_information[0], 'r', encoding='utf-8', errors='ignore') as f:  # 文件读操作
                script_edit.edit.setPlainText(f.read())
                f.close()
            # 新增右键
            script_edit.edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            script_edit.edit.customContextMenuRequested.connect(self.edit_right)
            # 右键新增结束

    # 保存文件
    def save_file(self):
        if not self.edit_tab.currentWidget().flag:
            save_path_information = QFileDialog.getSaveFileName(self, '选择保存脚本的路径', '.', '*.py')
            try:
                self.edit_tab.currentWidget().path = save_path_information[0]
                f = open(save_path_information[0], 'w', encoding='utf-8')
                f.write(self.edit_tab.currentWidget().edit.toPlainText())
                f.close()
                last_index = save_path_information[0].rindex('/')
                self.edit_tab.currentWidget().cwd = save_path_information[0][0:last_index]
                self.edit_tab.setTabText(self.edit_tab.currentIndex(), save_path_information[0][last_index + 1:])
                self.edit_tab.currentWidget().flag = True
                self.edit_tab.currentWidget().edit_name = save_path_information[0][last_index + 1:]
            except Exception as e:
                print(e)
        else:
            try:
                f = open(self.edit_tab.currentWidget().path, 'w', encoding='utf-8')
                f.write(self.edit_tab.currentWidget().edit.toPlainText())
                f.close()
            except Exception as e:
                print(e)

    '''def maybeSave(self):
        # 检查是否做了修改
        if self.edit1.document().isModified():
            # 进行提示，提供三个选择
            ret = QMessageBox.warning(self, "Application",
                                      "您想要在关闭之前保存对这个文档所做的改变么？\n如果您不保存，您的这些改变将丢失",
                                      QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.save()
            if ret == QMessageBox.Cancel:
                return False
        return True'''

    def save_another_file(self):
        save_another_path = QFileDialog.getSaveFileName(self, '选择要另存为的路径', '.', '*.py')
        if save_another_path[0]:
            f = open(save_another_path[0], 'w')
            f.write(self.edit_tab.currentWidget().edit.toPlainText())
            f.close()

    def show_report(self):
        pass

        # 脚本栏的右键点击事件

    def edit_right(self):
        try:
            pop_menu = QMenu(self)
            # qp = pop_menu.addAction(u'全屏')
            gb = pop_menu.addAction(u'关闭')
            # qp.triggered.connect(self.edit_screen)
            gb.triggered.connect(self.edit_close)
            pop_menu.exec_(QCursor.pos())
        except Exception as e:
            print(e)

    def edit_close(self):
        try:
            self.edit_tab.removeTab(self.edit_tab.currentIndex())
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MenuTools()
    form.show()
    sys.exit(app.exec_())
