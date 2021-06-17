import subprocess
import sys
import time
from threading import Thread

import pyautogui

import IDE
import screenCapture
import os
import get_point
from PyQt5.QtCore import QThread, QFile, QIODevice, QTextStream, QDateTime, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import QTcpSocket, QTcpServer
from PyQt5.QtXml import QDomDocument, QDomProcessingInstruction, QDomAttr, QDomElement

if sys.platform.startswith('win32'):
    father_dir = os.path.dirname(os.path.abspath(__file__))
    grandfather_dir = os.path.dirname(father_dir)
    while not father_dir == grandfather_dir:
        father_dir = grandfather_dir
        grandfather_dir = os.path.dirname(grandfather_dir)
    temporary_screenshot_dir = grandfather_dir[0] + ":/screenshotFolder"
    if not os.path.exists(temporary_screenshot_dir):
        os.makedirs(temporary_screenshot_dir)
    screenshot_dir = temporary_screenshot_dir + '/'
elif sys.platform.startswith('linux'):
    pass


class MyThread(QThread):
    def __init__(self, ide, path=None):
        super().__init__()
        self.ide = ide
        self.command = "pytest " + path + " --alluredir=./result"

    def run(self):
        self.ide.stop_action.setEnabled(True)
        self.sbp = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        for line in iter(self.sbp.stdout.readline, 'b'):
            self.ide.console_text.insertPlainText(line.decode('gbk'))
            self.ide.console_text.moveCursor(QTextCursor.End)
            if not subprocess.Popen.poll(self.sbp) is None:
                break
        self.sbp.stdout.close()
        self.ide.stop_action.setEnabled(False)
        self.ide.stop_run_directory_button.setEnabled(False)


device_message = {}


class Functions(IDE.MenuTools):

    def screenshot_function(self, method=None):
        self.setVisible(False)
        time.sleep(1)
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if sys.platform.startswith('win32'):
            self.cs = screenCapture.CaptureScreen(self, screenshot_dir, i, method)
        elif sys.platform.startswith('linux'):
            clib = QApplication.clipboard()
            clib.clear()
            pyautogui.hotkey('shift', 'ctrl', 'prtsc')
            start_time = time.time()
            while True:
                end_time = time.time()
                if clib.mimeData().hasImage():
                    clib.image().save(screenshot_dir + i + ".jpg", "jpg")
                    if method:
                        if method == 'assert_equal':
                            self.edit_tab.currentWidget().edit.insertPlainText(
                                "assert_equal(Template(r\"" + screenshot_dir + i + ".jpg\"), \"预测值\", \"请填写测试点\")")
                        elif method == 'assert_exists':
                            self.edit_tab.currentWidget().edit.insertPlainText(
                                "assert_exists(Template(r\"" + screenshot_dir + i + ".jpg\"), \"请填写测试点\")\n")
                        self.setVisible(True)
                    else:
                        self.edit_tab.currentWidget().edit.insertPlainText(
                            "(Template(r\"" + screenshot_dir + i + ".jpg\")")
                        self.setVisible(True)
                    break
                if end_time - start_time > 10:
                    break

    def screenshot(self):
        Functions.screenshot_function(self)

    def insert_picture(self):
        picture_path_information = QFileDialog.getOpenFileName(self, '请选择图片', '.', '*.jpg *.png *.jpeg')
        picture_path = picture_path_information[0]
        if picture_path:
            self.edit_tab.currentWidget().edit.insertPlainText("Template(r\"" + picture_path + "\")")

    def run(self):
        try:
            self.showMinimized()
            self.console_text.clear()
            self.edit_tab.currentWidget().edit.moveCursor(QTextCursor.Start)
            f = open('./script_template.py', 'r', encoding='utf-8')
            script_head = f.read()
            if not self.edit_tab.currentWidget().edit.find('# script'):
                self.edit_tab.currentWidget().edit.insertPlainText(script_head)
            f.close()

            if self.edit_tab.tabText(self.edit_tab.currentIndex())[0] == '*':
                self.edit_tab.setTabText(self.edit_tab.currentIndex(),
                                         self.edit_tab.tabText(self.edit_tab.currentIndex())[1:])
            f = open(self.edit_tab.currentWidget().path, 'w', encoding='utf-8')
            f.write(self.edit_tab.currentWidget().edit.toPlainText())
            f.close()
            self.thread = MyThread(self, path=self.edit_tab.currentWidget().path)
            self.thread.start()

        except Exception as e:
            print(e)
        '''with open(self.edit_tab.currentWidget().path, 'r', encoding='utf-8') as f:
            exec(f.read())'''

    def part_run(self):
        def part():
            f = open('./script_template.py', 'r', encoding='utf-8')
            script_head = f.read()
            cursor = self.edit_tab.currentWidget().edit.textCursor()
            exec(script_head + "\n" + cursor.selectedText() + "\nrun_end()")

        part_run_thread = Thread(target=part)
        part_run_thread.start()

    def stop_run(self):
        os.system("taskkill /t /f /pid "+str(self.thread.sbp.pid))
        self.stop_action.setEnabled(False)
        #  曾经的尝试
        # os.killpg(os.getpgid(self.thread.sbp.pid),signal.SIGTERM)
        # os.kill(self.thread.sbp.pid, signal.CTRL_C_EVENT)
        # win32api.TerminateProcess(int(self.thread.sbp._handle),-1)
        # self.thread.sbp.send_signal(signal.CTRL_C_EVENT)

    def wait(self):
        Functions.screenshot_function(self, "wait")

    def waitVanish(self):
        Functions.screenshot_function(self, "waitVanish")

    def exists(self):
        Functions.screenshot_function(self, "exists")

    def ocr(self):
        Functions.screenshot_function(self, "ocr")

    def click(self):
        Functions.screenshot_function(self, "click")

    def double_click(self):
        Functions.screenshot_function(self, "double_click")

    def right_click(self):
        Functions.screenshot_function(self, "right_click")

    def swipe(self):
        self.setVisible(False)
        time.sleep(1)
        self.point = get_point.Point(self)

    def hover(self):
        # 鼠标悬浮在该图片位置上
        Functions.screenshot_function(self, "hover")

    def keyevent(self):
        # 模拟按下键盘上某个键
        """keyevent_dialog = QInputDialog(self)
            keyevent_dialog.open()  # exec 模态,应用程序级,其他窗口不可见;open 窗口级,除了关联的之外都可交互;show 所有都可正常交互
            keyevent_dialog.resize(400, 100)
            keyevent_dialog.setWindowTitle('输入要按下的键的键码')"""
        keyevent_value = QInputDialog.getText(self, '按键输入', '例如:(TAB/ENTER/F1)')
        if keyevent_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"keyevent\"):\n" + "\t\tkeyevent(\"{" + keyevent_value[0] + "}\")\n" + "\t\tallure.attach('{}', '', allure.attachment_type.TEXT)\n".format(keyevent_value[0]))

    def snapshot(self):
        # 截取当前屏幕全图
        self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"snapshot\"):\n" + "\t\tsnapshot(msg=\"请填写测试点\")\n")

    def text(self):
        # 输入文本，文本框需要处于激活状态
        text_value = QInputDialog.getText(self, '文字输入', '内容')
        if text_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"text\"):\n" + "\t\ttext(\"" + text_value[0] + "\")\n" + "\t\tallure.attach('{}', '', allure.attachment_type.TEXT)\n".format(text_value[0]))

    def sleep(self):
        sleep_value = QInputDialog.getDouble(self, '等待n秒', '给出n的值', 1.0, 0)
        if sleep_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"sleep\"):\n" + "\t\tsleep(" + str(sleep_value[0]) + ")\n" + "\t\tallure.attach('{}', '', allure.attachment_type.TEXT)\n".format(sleep_value[0]))

    def assert_exist(self):
        Functions.screenshot_function(self, "assert_exists")

    def assert_file_exist(self):
        exist_path_information = QFileDialog.getSaveFileName(self, '判断是否存在文件', '.')
        if exist_path_information[0]:
            file = exist_path_information[0]
            self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"assert_file_exist\"):\n" + "\t\tassert_file_exist(\"" + file + "\")\n")

    def assert_word_exist(self):
        file_value = QFileDialog.getOpenFileName(self, '选择要对比的文件', '.')
        if file_value[0]:
            row_value = QInputDialog.getInt(self, '对比最后n行', '请给出n的取值', 1, 1)
            if row_value[1] is True:
                compare_value = QInputDialog.getMultiLineText(self, '最后n行的预期内容', '请给出您的预期')
                if compare_value[1] is True:
                    compare_v = ''
                    if row_value[0] > 1:
                        for i in compare_value[0].split('\n'):
                            compare_v += i
                    else:
                        compare_v = compare_value[0]
                    self.edit_tab.currentWidget().edit.insertPlainText(
                        "\twith allure.step(\"assert_word_exist\"):\n" + "\t\tassert_word_exist(\"" + file_value[0] + "\"," + str(row_value[0]) + ",\"" + compare_v + "\")\n" + "\t\tallure.attach('断言:{}的最后{}行的内容是{}', '', allure.attachment_type.TEXT)\n".format(file_value[0], row_value[0], compare_v))

    def assert_ocr_true(self):
        Functions.screenshot_function(self, "assert_ocr_true")
    
    def assert_client_exist(self):
        self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"assert_file_exist\"):\n" + "\t\tassert_client_exist(\"client is exist\")")

    def dialog_connect(self):
        self.connect_dialog = QDialog()
        connect_form = QFormLayout(self.connect_dialog)
        self.connect_dialog.setWindowTitle("连接设置")
        self.combox_ip = QComboBox()
        self.combox_ip.setEditable(True)
        self.combox_ip.addItem("Tcp 客户端")
        self.label_ip_style = QLabel("协议类型")
        self.label_ip = QLabel("ip地址:")
        self.lineedit_ip = QLineEdit("127.0.0.1")
        self.label_port = QLabel("端口号:")
        self.lineedit_port = QLineEdit("9948")
        self.btn_con = QPushButton("确定")

        connect_form.addRow(self.label_ip_style, self.combox_ip)
        connect_form.addRow(self.label_ip, self.lineedit_ip)
        connect_form.addRow(self.label_port, self.lineedit_port)
        connect_form.addRow(self.btn_con)
        self.btn_con.clicked.connect(lambda: Functions.connect_clicked(self))
        self.connect_dialog.exec_()

    def connect_clicked(self):
        self.socket = QTcpSocket(self)
        string = str(self.socket)
        if self.lineedit_ip.text() == '' or self.lineedit_port.text() == '':
            QMessageBox.information(self, "提示", "输入不能为空", QMessageBox.Ok)
        else:
            self.host_ip_addr = self.lineedit_ip.text()  # 获取lineEdit中的内容
            self.port = int(self.lineedit_port.text())

            self.socket.connectToHost(self.host_ip_addr, self.port)
            self.textEdit_send.setText("connect to {} on port {} success!\n".format(self.host_ip_addr, self.port))
            self.textEdit_send.insertPlainText(time.strftime("[%Y-%m-%d %H:%M:%S]\n", time.localtime()))
            self.edit_tab.currentWidget().edit.insertPlainText(
                "connect_server(\"" + self.host_ip_addr + "\"," + self.lineedit_port.text() + ")")

            self.btn_disconnect.setEnabled(True)
            self.btn_send.setEnabled(True)
            self.btn_open.setEnabled(True)
            self.socket.readyRead.connect(lambda: Functions.on_socket_receive(self))
            self.connect_dialog.close()

    def on_btn_clear_clicked(self):
        self.textEdit_send.clear()

    def on_socket_receive(self):
        rx_data = self.socket.readAll()
        self.textEdit_send.insertPlainText("回复:" + rx_data.data())

    def send_file(self):
        file_name = QFileDialog.getOpenFileName(self, '打开文件', './')
        if file_name[0]:
            with open(file_name[0], 'r', encoding='utf-8', errors='ignore') as file:  # 文件写操作
                self.textEdit_send.setText(file.read())
        else:
            QMessageBox.warning(self, "提示", "文件不存在")

    def on_btn_send_clicked(self):
        str = self.textEdit_send.toPlainText()
        self.textEdit_send.append(time.strftime("[%Y-%m-%d %H:%M:%S]\n", time.localtime()))
        self.textEdit_send.append("发送:" + str)
        self.socket.write(str.encode("utf-8"))

    def dialog_new_device(self):
        new_device = QDialog()
        self.formlayout2 = QFormLayout(new_device)
        new_device.setWindowTitle("新建设备")
        new_device.setFixedSize(300, 240)
        self.label_send_model = QLabel("指令类型:")
        self.combox_send_model = QComboBox(new_device)
        self.combox_send_model.addItem("newdevice")
        self.label_name = QLabel("设备名字:")
        self.combox_newDevice_name = QComboBox()
        self.combox_newDevice_name.setEditable(True)

        self.label_type = QLabel("设备类型:")
        self.combox_type = QComboBox(new_device)
        self.combox_type.addItem("TcpServer")

        self.label_ip = QLabel("Ip地址:")
        self.combox_newDevice_ip = QComboBox()
        self.combox_newDevice_ip.setEditable(True)

        self.label_port = QLabel("端口号:")
        self.combox_newDevice_port = QComboBox()
        self.combox_newDevice_port.setEditable(True)

        self.btn_true = QPushButton("确定", new_device)
        self.btn_xml_newDevice = QPushButton("加载文件")

        for k, v in device_message.items():
            self.combox_newDevice_name.addItem(k)
            self.combox_newDevice_ip.addItem(v[0])
            self.combox_newDevice_port.addItem(v[1])

        self.btn_xml_newDevice.clicked.connect(lambda: Functions.new_device_analysis(self))
        self.btn_true.clicked.connect(lambda: Functions.new_device_xml(self))
        self.btn_true.clicked.connect(new_device.close)
        self.formlayout2.addRow(self.label_send_model, self.combox_send_model)
        self.formlayout2.addRow(self.label_name, self.combox_newDevice_name)
        self.formlayout2.addRow(self.label_type, self.combox_type)
        self.formlayout2.addRow(self.label_ip, self.combox_newDevice_ip)
        self.formlayout2.addRow(self.label_port, self.combox_newDevice_port)
        self.formlayout2.addRow(self.btn_true)
        self.formlayout2.addRow(self.btn_xml_newDevice)
        new_device.exec_()

    def new_device_analysis(self):
        file_name = QFileDialog.getOpenFileName(self, '打开文件', './file_xml/newDevice')
        file_new_device = QFile(file_name[0])
        doc = QDomDocument()
        doc.setContent(file_new_device)
        com = doc.firstChildElement("command")
        dev = com.firstChildElement("device")
        device_name = dev.attribute("name")
        self.combox_newDevice_name.addItem(device_name)
        par = dev.firstChildElement("parameters")
        new_device_ip = par.attribute("ip")
        self.combox_newDevice_ip.addItem(new_device_ip)
        new_device_port = par.attribute("port")
        self.combox_newDevice_port.addItem(new_device_port)

    def dialog_response(self):
        self.response = QDialog()
        self.response.setWindowTitle("添加回令")
        self.response.setFixedSize(855, 820)

        self.tableWidget = QTableWidget(19, 4)
        self.tableWidget.setHorizontalHeaderLabels(['序号', '字段名称', '字节数', '数值'])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSpan(11, 0, 10, 1)
        self.tableWidget.setSpan(12, 1, 9, 3)

        self.tabWidget = QTabWidget()
        self.tabWidget.insertTab(0, self.tableWidget, "自定义帧")

        datetime = QDateTime(QDateTime.currentDateTime())
        date = datetime.toString("yyyy/MM/dd")
        date_time = datetime.toString("hh:mm")

        new_item1 = QTableWidgetItem("1")
        self.tableWidget.setItem(0, 0, new_item1)
        new_item1.setTextAlignment(Qt.AlignCenter)
        new_item1_1 = QTableWidgetItem("帧类型")
        self.tableWidget.setItem(0, 1, new_item1_1)
        new_item1_1.setTextAlignment(Qt.AlignCenter)
        new_item1_2 = QTableWidgetItem("2")
        self.tableWidget.setItem(0, 2, new_item1_2)
        new_item1_2.setTextAlignment(Qt.AlignCenter)
        new_item1_3 = QTableWidgetItem("0110")
        self.tableWidget.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)

        new_item2 = QTableWidgetItem("2")
        self.tableWidget.setItem(1, 0, new_item2)
        new_item2.setTextAlignment(Qt.AlignCenter)
        new_item2_1 = QTableWidgetItem("重传次数")
        self.tableWidget.setItem(1, 1, new_item2_1)
        new_item2_1.setTextAlignment(Qt.AlignCenter)
        new_item2_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(1, 2, new_item2_2)
        new_item2_2.setTextAlignment(Qt.AlignCenter)
        new_item2_3 = QTableWidgetItem("11")
        self.tableWidget.setItem(1, 3, new_item2_3)
        new_item2_3.setTextAlignment(Qt.AlignCenter)

        new_item3 = QTableWidgetItem("3")
        self.tableWidget.setItem(2, 0, new_item3)
        new_item3.setTextAlignment(Qt.AlignCenter)
        new_item3_1 = QTableWidgetItem("帧确定标记")
        self.tableWidget.setItem(2, 1, new_item3_1)
        new_item3_1.setTextAlignment(Qt.AlignCenter)
        new_item3_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(2, 2, new_item3_2)
        new_item3_2.setTextAlignment(Qt.AlignCenter)
        new_item3_3 = QTableWidgetItem("00")
        self.tableWidget.setItem(2, 3, new_item3_3)
        new_item3_3.setTextAlignment(Qt.AlignCenter)

        new_item4 = QTableWidgetItem("4")
        self.tableWidget.setItem(3, 0, new_item4)
        new_item4.setTextAlignment(Qt.AlignCenter)
        new_item4_1 = QTableWidgetItem("信源系统标记")
        self.tableWidget.setItem(3, 1, new_item4_1)
        new_item4_1.setTextAlignment(Qt.AlignCenter)
        new_item4_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(3, 2, new_item4_2)
        new_item4_2.setTextAlignment(Qt.AlignCenter)
        new_item4_3 = QTableWidgetItem("11")
        self.tableWidget.setItem(3, 3, new_item4_3)
        new_item4_3.setTextAlignment(Qt.AlignCenter)

        new_item5 = QTableWidgetItem("5")
        self.tableWidget.setItem(4, 0, new_item5)
        new_item5.setTextAlignment(Qt.AlignCenter)
        new_item5_1 = QTableWidgetItem("信源节点编码")
        self.tableWidget.setItem(4, 1, new_item5_1)
        new_item5_1.setTextAlignment(Qt.AlignCenter)
        new_item5_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(4, 2, new_item5_2)
        new_item5_2.setTextAlignment(Qt.AlignCenter)
        new_item5_3 = QTableWidgetItem("01")
        self.tableWidget.setItem(4, 3, new_item5_3)
        new_item5_3.setTextAlignment(Qt.AlignCenter)

        new_item6 = QTableWidgetItem("6")
        self.tableWidget.setItem(5, 0, new_item6)
        new_item6.setTextAlignment(Qt.AlignCenter)
        new_item6_1 = QTableWidgetItem("信道系统编码")
        self.tableWidget.setItem(5, 1, new_item6_1)
        new_item6_1.setTextAlignment(Qt.AlignCenter)
        new_item6_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(5, 2, new_item6_2)
        new_item6_2.setTextAlignment(Qt.AlignCenter)
        new_item6_3 = QTableWidgetItem("10")
        self.tableWidget.setItem(5, 3, new_item6_3)
        new_item6_3.setTextAlignment(Qt.AlignCenter)

        new_item7 = QTableWidgetItem("7")
        self.tableWidget.setItem(6, 0, new_item7)
        new_item7.setTextAlignment(Qt.AlignCenter)
        new_item7_1 = QTableWidgetItem("信道节点编码")
        self.tableWidget.setItem(6, 1, new_item7_1)
        new_item7_1.setTextAlignment(Qt.AlignCenter)
        new_item7_2 = QTableWidgetItem("1")
        self.tableWidget.setItem(6, 2, new_item7_2)
        new_item7_2.setTextAlignment(Qt.AlignCenter)
        new_item7_3 = QTableWidgetItem("11")
        self.tableWidget.setItem(6, 3, new_item7_3)
        new_item7_3.setTextAlignment(Qt.AlignCenter)

        new_item8 = QTableWidgetItem("8")
        self.tableWidget.setItem(7, 0, new_item8)
        new_item8.setTextAlignment(Qt.AlignCenter)
        new_item8_1 = QTableWidgetItem("年月日")
        self.tableWidget.setItem(7, 1, new_item8_1)
        new_item8_1.setTextAlignment(Qt.AlignCenter)
        new_item8_2 = QTableWidgetItem("4")
        self.tableWidget.setItem(7, 2, new_item8_2)
        new_item8_2.setTextAlignment(Qt.AlignCenter)
        new_item8_3 = QTableWidgetItem(date)
        self.tableWidget.setItem(7, 3, new_item8_3)
        new_item8_3.setTextAlignment(Qt.AlignCenter)

        new_item9 = QTableWidgetItem("9")
        self.tableWidget.setItem(8, 0, new_item9)
        new_item9.setTextAlignment(Qt.AlignCenter)
        new_item9_1 = QTableWidgetItem("时间")
        self.tableWidget.setItem(8, 1, new_item9_1)
        new_item9_1.setTextAlignment(Qt.AlignCenter)
        new_item9_2 = QTableWidgetItem("2")
        self.tableWidget.setItem(8, 2, new_item9_2)
        new_item9_2.setTextAlignment(Qt.AlignCenter)
        new_item9_3 = QTableWidgetItem(date_time)
        self.tableWidget.setItem(8, 3, new_item9_3)
        new_item9_3.setTextAlignment(Qt.AlignCenter)

        new_item10 = QTableWidgetItem("10")
        self.tableWidget.setItem(9, 0, new_item10)
        new_item10.setTextAlignment(Qt.AlignCenter)
        new_item10_1 = QTableWidgetItem("帧计数")
        self.tableWidget.setItem(9, 1, new_item10_1)
        new_item10_1.setTextAlignment(Qt.AlignCenter)
        new_item10_2 = QTableWidgetItem("4")
        self.tableWidget.setItem(9, 2, new_item10_2)
        new_item10_2.setTextAlignment(Qt.AlignCenter)
        new_item10_3 = QTableWidgetItem("111")
        self.tableWidget.setItem(9, 3, new_item10_3)
        new_item10_3.setTextAlignment(Qt.AlignCenter)

        new_item11 = QTableWidgetItem("11")
        self.tableWidget.setItem(10, 0, new_item11)
        new_item11.setTextAlignment(Qt.AlignCenter)
        new_item11_1 = QTableWidgetItem("备用字节")
        self.tableWidget.setItem(10, 1, new_item11_1)
        new_item11_1.setTextAlignment(Qt.AlignCenter)
        new_item11_2 = QTableWidgetItem("4")
        self.tableWidget.setItem(10, 2, new_item11_2)
        new_item11_2.setTextAlignment(Qt.AlignCenter)
        new_item11_3 = QTableWidgetItem("1")
        self.tableWidget.setItem(10, 3, new_item11_3)
        new_item11_3.setTextAlignment(Qt.AlignCenter)

        new_item12 = QTableWidgetItem("12")
        self.tableWidget.setItem(11, 0, new_item12)
        new_item12.setTextAlignment(Qt.AlignCenter)
        new_item12_1 = QTableWidgetItem("可变区")
        self.tableWidget.setItem(11, 1, new_item12_1)
        new_item12_1.setTextAlignment(Qt.AlignCenter)
        new_item12_2 = QTableWidgetItem("自动")
        self.tableWidget.setItem(11, 2, new_item12_2)
        new_item12_2.setTextAlignment(Qt.AlignCenter)
        self.textEdit_buf = QTextEdit()
        self.tableWidget.setCellWidget(12, 1, self.textEdit_buf)

        # mosbus界面
        widget_mosbus = QWidget()
        label_head = QLabel('<p style=line-height:150%>包头</p>')
        label_head.setStyleSheet('font:20px;')
        # 设置标签居中
        label_head.setAlignment(Qt.AlignCenter)

        # setGeometry(左右， 上下， 宽， 高)
        label_head.setGeometry(10, 10, 20, 20)
        self.table_widget_head = QTableWidget(5, 4)
        self.table_widget_head.verticalHeader().setVisible(False)
        self.table_widget_head.horizontalHeader().setVisible(False)
        head_item1 = QTableWidgetItem("序号")
        self.table_widget_head.setItem(0, 0, head_item1)
        head_item1.setTextAlignment(Qt.AlignCenter)
        head_item1_1 = QTableWidgetItem("字段名称")
        self.table_widget_head.setItem(0, 1, head_item1_1)
        head_item1_1.setTextAlignment(Qt.AlignCenter)
        head_item1_2 = QTableWidgetItem("字节数")
        self.table_widget_head.setItem(0, 2, head_item1_2)
        head_item1_2.setTextAlignment(Qt.AlignCenter)
        head_item1_3 = QTableWidgetItem("数值")
        self.table_widget_head.setItem(0, 3, head_item1_3)
        head_item1_3.setTextAlignment(Qt.AlignCenter)

        head_item2 = QTableWidgetItem("1")
        self.table_widget_head.setItem(1, 0, head_item2)
        head_item2.setTextAlignment(Qt.AlignCenter)
        head_item2_1 = QTableWidgetItem("传输ID")
        self.table_widget_head.setItem(1, 1, head_item2_1)
        head_item2_1.setTextAlignment(Qt.AlignCenter)
        head_item2_2 = QTableWidgetItem("2")
        self.table_widget_head.setItem(1, 2, head_item2_2)
        head_item2_2.setTextAlignment(Qt.AlignCenter)
        head_item2_3 = QTableWidgetItem("0")
        self.table_widget_head.setItem(1, 3, head_item2_3)
        head_item2_3.setTextAlignment(Qt.AlignCenter)

        head_item3 = QTableWidgetItem("2")
        self.table_widget_head.setItem(2, 0, head_item3)
        head_item3.setTextAlignment(Qt.AlignCenter)
        head_item3_1 = QTableWidgetItem("传输协议标识")
        self.table_widget_head.setItem(2, 1, head_item3_1)
        head_item3_1.setTextAlignment(Qt.AlignCenter)
        head_item3_2 = QTableWidgetItem("2")
        self.table_widget_head.setItem(2, 2, head_item3_2)
        head_item3_2.setTextAlignment(Qt.AlignCenter)
        head_item3_3 = QTableWidgetItem("0")
        self.table_widget_head.setItem(2, 3, head_item3_3)
        head_item3_3.setTextAlignment(Qt.AlignCenter)

        head_item4 = QTableWidgetItem("3")
        self.table_widget_head.setItem(3, 0, head_item4)
        head_item4.setTextAlignment(Qt.AlignCenter)
        head_item4_1 = QTableWidgetItem("命令长度")
        self.table_widget_head.setItem(3, 1, head_item4_1)
        head_item4_1.setTextAlignment(Qt.AlignCenter)
        head_item4_2 = QTableWidgetItem("2")
        self.table_widget_head.setItem(3, 2, head_item4_2)
        head_item4_2.setTextAlignment(Qt.AlignCenter)
        head_item4_3 = QTableWidgetItem("4")
        self.table_widget_head.setItem(3, 3, head_item4_3)
        head_item4_3.setTextAlignment(Qt.AlignCenter)

        head_item5 = QTableWidgetItem("4")
        self.table_widget_head.setItem(4, 0, head_item5)
        head_item5.setTextAlignment(Qt.AlignCenter)
        head_item5_1 = QTableWidgetItem("目标的UnitID")
        self.table_widget_head.setItem(4, 1, head_item5_1)
        head_item5_1.setTextAlignment(Qt.AlignCenter)
        head_item5_2 = QTableWidgetItem("1")
        self.table_widget_head.setItem(4, 2, head_item5_2)
        head_item5_2.setTextAlignment(Qt.AlignCenter)
        head_item5_3 = QTableWidgetItem("0")
        self.table_widget_head.setItem(4, 3, head_item5_3)
        head_item5_3.setTextAlignment(Qt.AlignCenter)

        label_command = QLabel('<p style=line-height:150%>命令码：</p>')
        label_command.setStyleSheet('font:20px;')
        label_command.setFixedSize(120, 50)
        # 设置对齐方式
        label_command.setAlignment(Qt.AlignCenter)

        self.combox_command = QComboBox()
        self.combox_command.setStyleSheet('font:20px;')
        self.combox_command.addItem("读输出位（01）")
        self.combox_command.addItem("读输出位（02）")
        self.combox_command.addItem("读多个寄存器（03）")
        self.combox_command.addItem("写输出位（05）")
        self.combox_command.addItem("写多个输出位（0F）")

        label_space = QLabel()
        label_space1 = QLabel()
        label_space2 = QLabel()
        label_space3 = QLabel()
        label_space4 = QLabel()

        label_message = QLabel('<p style=line-height:150%>命令信息</p>')
        label_message.setStyleSheet('font:20px;')
        label_message.setAlignment(Qt.AlignCenter)
        self.table_widget_message = QTableWidget(4, 4)
        # 隐藏水平和垂直头
        self.table_widget_message.verticalHeader().setVisible(False)
        self.table_widget_message.horizontalHeader().setVisible(False)
        new_item1 = QTableWidgetItem("序号")
        self.table_widget_message.setItem(0, 0, new_item1)
        new_item1.setTextAlignment(Qt.AlignCenter)
        new_item1_1 = QTableWidgetItem("字段名称")
        self.table_widget_message.setItem(0, 1, new_item1_1)
        new_item1_1.setTextAlignment(Qt.AlignCenter)
        new_item1_2 = QTableWidgetItem("字节数")
        self.table_widget_message.setItem(0, 2, new_item1_2)
        new_item1_2.setTextAlignment(Qt.AlignCenter)
        new_item1_3 = QTableWidgetItem("数值")
        self.table_widget_message.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)

        self.combox_command.currentIndexChanged.connect(lambda: Functions.add_key_data(self))
        # combox_command.activated[str].connect(lambda: Functions.add_data(self))

        mosbus_layout = QFormLayout()
        # 设置水平和垂直间隔
        mosbus_layout.setVerticalSpacing(15)
        mosbus_layout.addRow(label_space)
        mosbus_layout.addRow(label_head)
        mosbus_layout.addRow(self.table_widget_head)
        mosbus_layout.addRow(label_space1)
        mosbus_layout.addRow(label_space2)
        mosbus_layout.addRow(label_space3)
        mosbus_layout.addRow(label_command, self.combox_command)
        mosbus_layout.addRow(label_space4)
        mosbus_layout.addRow(label_message)
        mosbus_layout.addRow(self.table_widget_message)
        self.tabWidget.insertTab(1, widget_mosbus, "mosbus")
        widget_mosbus.setLayout(mosbus_layout)

        hbox = QVBoxLayout()
        vbox = QHBoxLayout()
        hbox2 = QVBoxLayout()

        gridlayout1 = QFormLayout()
        gridlayout1.setSpacing(15)
        label1 = QLabel()
        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(30, 30)
        self.btn_add.clicked.connect(lambda: Functions.add_tab(self))
        label2 = QLabel()
        self.btn_delete = QPushButton("-")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.clicked.connect(lambda: Functions.delete_tab(self))
        label3 = QLabel()
        label4 = QLabel()
        label5 = QLabel()
        label6 = QLabel()
        self.btn_translate = QPushButton("<<")
        self.btn_translate.setFixedSize(110, 35)

        self.btn_translate.clicked.connect(lambda: Functions.left_translate(self))
        self.btn_reverse_translate = QPushButton(">>")
        self.btn_reverse_translate.setFixedSize(110, 35)
        self.btn_reverse_translate.clicked.connect(lambda: Functions.rigth_translate(self))

        gridlayout2 = QFormLayout()
        gridlayout2.setSpacing(65)
        gridlayout2.addRow(label1, self.btn_add)
        gridlayout2.addRow(label2, self.btn_delete)
        gridlayout2.addRow(label3)
        gridlayout2.addRow(label4)
        gridlayout2.addRow(label5)
        gridlayout2.addRow(label6)
        gridlayout2.addRow(self.btn_translate)
        gridlayout2.addRow(self.btn_reverse_translate)
        hbox2.addLayout(gridlayout2)

        self.label_send_model = QLabel("指令类型:")

        self.combox_send_model = QComboBox(self.response)
        self.combox_send_model.addItem("response")
        gridlayout1.addRow(self.label_send_model, self.combox_send_model)
        self.label_name = QLabel("设备名字:")
        self.combox_response_name = QComboBox()
        self.combox_response_name.setEditable(True)

        gridlayout1.addRow(self.label_name, self.combox_response_name)
        self.label_type = QLabel("设备类型:")

        self.combox_type = QComboBox(self.response)
        self.combox_type.addItem("TcpServer")
        gridlayout1.addRow(self.label_type, self.combox_type)

        self.label_ip = QLabel(" Ip地址:")
        self.combox_response_ip = QComboBox()
        self.combox_response_ip.setEditable(True)

        gridlayout1.addRow(self.label_ip, self.combox_response_ip)
        self.label_port = QLabel(" 端口号:")

        self.combox_response_port = QComboBox()
        self.combox_response_port.setEditable(True)

        gridlayout1.addRow(self.label_port, self.combox_response_port)
        self.label_key_value = QLabel(" 命令字:")

        self.edit_key_value = QLineEdit(self.response)
        gridlayout1.addRow(self.label_key_value, self.edit_key_value)
        self.label_index = QLabel("起始节点:")

        self.combox_index = QSpinBox(self.response)
        gridlayout1.addRow(self.label_index, self.combox_index)

        self.label_length = QLabel("字节长度:")
        self.spin_length = QSpinBox(self.response)
        gridlayout1.addRow(self.label_length, self.spin_length)
        self.label_keyName = QLabel("命令名称:")
        self.edit_keyName = QLineEdit(self.response)
        self.edit_keyName.setText("命令")
        gridlayout1.addRow(self.label_keyName, self.edit_keyName)
        self.label_model = QLabel("回令模式:")
        self.combox_model = QComboBox(self.response)
        self.combox_model.addItem("正常发送")
        self.combox_model.addItem("循环发送")
        self.combox_model.addItem("延迟发送")
        gridlayout1.addRow(self.label_model, self.combox_model)
        self.label_responName = QLabel("回令名称:")
        self.edit_responName = QLineEdit(self.response)
        self.edit_responName.setText("回令")
        gridlayout1.addRow(self.label_responName, self.edit_responName)
        self.label_respon_value = QLabel("回令数据:")
        # self.edit_plainText = QPlainTextEdit()
        self.edit_respon_value = QPlainTextEdit()

        self.label_loop = QLabel("循环次数:")
        self.spin_loop = QSpinBox(self.response)
        gridlayout1.addRow(self.label_loop, self.spin_loop)
        self.label_delayed = QLabel("延迟时间:")
        self.edit_delayed = QLineEdit(self.response)
        gridlayout1.addRow(self.label_delayed, self.edit_delayed)
        self.btn_true = QPushButton("确定", self.response)

        self.btn_respons_xml = QPushButton("加载文件")

        for k, v in device_message.items():
            self.combox_response_name.addItem(k)
            self.combox_response_ip.addItem(v[0])
            self.combox_response_port.addItem(v[1])

        gridlayout1.addRow(self.label_respon_value)
        gridlayout1.addRow(self.edit_respon_value)
        gridlayout1.addRow(self.btn_true)
        gridlayout1.addRow(self.btn_respons_xml)

        self.btn_respons_xml.clicked.connect(lambda: Functions.respon_analysis(self))
        self.btn_true.clicked.connect(lambda: Functions.judge_command(self))

        hbox.addLayout(gridlayout1)
        hbox2.addSpacing(3)
        vbox.addLayout(hbox, 3)
        vbox.addLayout(hbox2, 1)
        vbox.addWidget(self.tabWidget, 8)
        self.response.setLayout(vbox)
        self.response.exec_()

    def add_key_data(self):
        if self.combox_command.currentIndex() == 0:
            mosbus_list_item1 = ["1", "命令码", "1", "01"]
            mosbus_list_item2 = ["2", "回令中的字节数", "1", "1"]
            mosbus_list_item3 = ["3", "点位置", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_command.currentIndex() == 1:
            mosbus_list_item1 = ["1", "命令码", "1", "02"]
            mosbus_list_item2 = ["2", "回令中的字节数", "1", "1"]
            mosbus_list_item3 = ["3", "点位置", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_command.currentIndex() == 2:
            mosbus_list_item1 = ["1", "命令码", "1", "03"]
            mosbus_list_item2 = ["2", "返回值的字节个数", "1", "1"]
            mosbus_list_item3 = ["3", "寄存器值", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_command.currentIndex() == 3:
            mosbus_list_item1 = ["1", "命令码", "1", "05"]
            mosbus_list_item2 = ["2", "地址", "2", "0"]
            mosbus_list_item3 = ["3", "打开或关闭", "1", "00"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_command.currentIndex() == 4:
            mosbus_list_item1 = ["1", "命令码", "1", "0F"]
            mosbus_list_item2 = ["2", "地址", "2", "0"]
            mosbus_list_item3 = ["3", "位数", "3", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

    def respon_analysis(self):
        fileName = QFileDialog.getOpenFileName(self, '打开文件', './file_xml/response')
        file = QFile(fileName[0])
        doc = QDomDocument()
        doc.setContent(file)
        com = doc.firstChildElement("command")
        dev = com.firstChildElement("device")
        respon_name = dev.attribute("name")
        self.combox_response_name.addItem(respon_name)
        par = dev.firstChildElement("parameters")
        respon_ip = par.attribute("ip")
        self.combox_response_ip.addItem(respon_ip)
        respon_port = par.attribute("port")
        self.combox_response_port.addItem(respon_port)
        rep_key = par.firstChildElement("key")
        respon_value = rep_key.attribute("value")
        self.edit_key_value.setText(respon_value)
        respon = rep_key.firstChildElement("response")
        response_value = respon.attribute("value")
        self.edit_respon_value.appendPlainText(response_value)
        response_delayed = respon.attribute("delayed")
        self.edit_delayed.setText(response_delayed)
        response_loop = respon.attribute("loop")

    def add_tab(self):
        table_widget = QTableWidget(1,4)
        table_widget.verticalHeader().setVisible(False)
        table_widget.horizontalHeader().setVisible(False)
        table_widget.setItem(0, 0, QTableWidgetItem('序号'))
        table_widget.setItem(0, 1, QTableWidgetItem('字段名称'))
        table_widget.setItem(0, 2, QTableWidgetItem('字节数'))
        table_widget.setItem(0, 3, QTableWidgetItem('数值'))
        # 输入框为字符串
        table_name = QInputDialog.getText(self, '帧名字', '帧名字')
        self.tabWidget.insertTab(2, table_widget, table_name[0])

    def left_translate(self):
        str = "A5"
        stri = self.tableWidget.item(0, 3).text()
        if len(stri) == 0:
            stri = "00" + " " + "00"
        if len(stri) == 1:
            stri = "00" + " " + stri + "0"
        if len(stri) == 2:
            stri = "00" + " " + stri
        if len(stri) == 3:
            stri1 = stri[0:2]
            stri2 = stri[2:3]
            stri2 = stri2 + "0"
            stri = stri2 + " " + stri
        if len(stri) == 4:
            stri3 = stri[0:2]
            stri4 = stri[2:4]
            stri = stri4 + " " + stri3
        str = str + " " + stri
        print(str)
        k = 1
        while k < 8:
            string = self.tableWidget.item(k, 3).text()
            if len(string) == 1:
                string = string + "0"

            # string = string[::-1] #字符串反转
            if k == 7:
                str_date = string
                str_date = str_date.split('/')
                print(str_date)
                j = 0
                while j < len(str_date) + 1:
                    if j == 0:
                        str_year1 = str_date[j]
                        str_year1 = hex(int(str_year1))
                        if str_year1.startswith("0x"):
                            str_year1 = str_year1[2:]
                        str_year1_1 = str_year1[0:1]
                        str_year1_1 = str_year1_1.zfill(2)
                        str_year2_1 = str_year1[1:3]
                        str_year2_1 = str_year2_1.zfill(2)
                        str = str + " " + str_year2_1
                        str = str + " " + str_year1_1
                    if j == 1:
                        str_date1 = str_date[j]
                        str_date1 = hex(int(str_date1))
                        if str_date1.startswith("0x"):
                            str_date1 = str_date1[2:]
                            str_date1 = str_date1.zfill(2)

                    if j == 2:
                        str_date2 = str_date[j]

                        str_date2 = hex(int(str_date2))

                        if str_date2.startswith("0x"):
                            str_date2 = str_date2[2:]
                            print(str_date2)
                            str_date2 = str_date2.zfill(2)
                    j = j + 1
                break
            str = str + " " + string
            k = k + 1
        # str = str + " " + str_date1+" "+ str_date2 + "A4"
        x = 8
        while x < 10:
            string_time = self.tableWidget.item(x, 3).text()
            print(string_time)
            if x == 8:
                str_time = string_time
                str_time = str_time.split(":")
                i = 0
                while i < len(str_time):
                    str_time1 = str_time[0]
                    str_time1 = hex(int(str_time1))
                    if str_time1.startswith("0x"):
                        str_time1 = str_time1[2:]
                        str_time1 = str_time1.zfill(2)
                    str_time2 = str_time[1]
                    str_time2 = hex(int(str_time2))
                    if str_time2.startswith("0x"):
                        str_time2 = str_time2[2:]
                        str_time2 = str_time2.zfill(2)
                    i = i + 1
                break
            x = x + 1

        y = 9
        while y < 10:
            string_mesg = self.tableWidget.item(y, 3).text()
            if len(string_mesg) == 0:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + "00"
            if len(string_mesg) == 1:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + string_mesg + "0"
            if len(string_mesg) == 2:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + string_mesg
            if len(string_mesg) == 3:
                string_mesg1 = string_mesg[0:2]
                string_mesg2 = string_mesg[2:3] + "0"
                string_mesg = "00" + " " + "00" + " " + string_mesg2 + " " + string_mesg1
            if len(string_mesg) == 4:
                string_mesg3 = string_mesg[0:2]
                string_mesg4 = string_mesg[2:4]
                string_mesg = "00" + " " + "00" + " " + string_mesg4 + " " + string_mesg3
            if len(string_mesg) == 5:
                string_mesg5 = string_mesg[0:2]
                string_mesg6 = string_mesg[2:4]
                string_mesg7 = string_mesg[4:5] + "0"
                string_mesg = "00" + " " + string_mesg7 + " " + string_mesg6 + " " + string_mesg5
            if len(string_mesg) == 6:
                string_mesg8 = string_mesg[0:2]
                string_mesg9 = string_mesg[2:4]
                string_mesg10 = string_mesg[4:6]
                string_mesg = "00" + " " + string_mesg10 + " " + string_mesg9 + " " + string_mesg8
            if len(string_mesg) == 7:
                string_mesg11 = string_mesg[0:2]
                string_mesg12 = string_mesg[2:4]
                string_mesg13 = string_mesg[4:6]
                string_mesg14 = string_mesg[6:7] + "0"
                string_mesg = string_mesg14 + " " + string_mesg13 + " " + string_mesg12 + " " + string_mesg11
            if len(string_mesg) == 8:
                string_mesg15 = string_mesg[0:2]
                string_mesg16 = string_mesg[2:4]
                string_mesg17 = string_mesg[4:6]
                string_mesg18 = string_mesg[6:8]
                string_mesg = string_mesg18 + " " + string_mesg17 + " " + string_mesg16 + " " + string_mesg15
            y = y + 1
        string_mesg = " " + string_mesg
        z = 10
        while z < 11:
            string_mesgz = self.tableWidget.item(z, 3).text()
            if len(string_mesgz) == 0:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + "00"
            if len(string_mesgz) == 1:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + string_mesgz + "0"
            if len(string_mesgz) == 2:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + string_mesgz
            if len(string_mesgz) == 3:
                string_mesg1 = string_mesgz[0:2]
                string_mesg2 = string_mesgz[2:3] + "0"
                string_mesgz = "00" + " " + "00" + " " + string_mesg2 + " " + string_mesg1
            if len(string_mesgz) == 4:
                string_mesg3 = string_mesgz[0:2]
                string_mesg4 = string_mesgz[2:4]
                string_mesgz = "00" + " " + "00" + " " + string_mesg4 + " " + string_mesg3
            if len(string_mesgz) == 5:
                string_mesg5 = string_mesgz[0:2]
                string_mesg6 = string_mesgz[2:4]
                string_mesg7 = string_mesgz[4:5] + "0"
                string_mesgz = "00" + " " + string_mesg7 + " " + string_mesg6 + " " + string_mesg5
            if len(string_mesgz) == 6:
                string_mesg8 = string_mesgz[0:2]
                string_mesg9 = string_mesgz[2:4]
                string_mesg10 = string_mesgz[4:6]
                string_mesgz = "00" + " " + string_mesg10 + " " + string_mesg9 + " " + string_mesg8
            if len(string_mesgz) == 7:
                string_mesg11 = string_mesgz[0:2]
                string_mesg12 = string_mesgz[2:4]
                string_mesg13 = string_mesgz[4:6]
                string_mesg14 = string_mesgz[6:7] + "0"
                string_mesgz = string_mesg14 + " " + string_mesg13 + " " + string_mesg12 + " " + string_mesg11
            if len(string_mesgz) == 8:
                string_mesg15 = string_mesgz[0:2]
                string_mesg16 = string_mesgz[2:4]
                string_mesg17 = string_mesgz[4:6]
                string_mesg18 = string_mesgz[6:8]
                string_mesgz = string_mesg18 + " " + string_mesg17 + " " + string_mesg16 + " " + string_mesg15
            z = z + 1
        string_mesg = string_mesg + " " + string_mesgz
        length = 0
        buffer = ""
        data_buf = self.textEdit_buf.toPlainText()
        while length < len(data_buf):
            buffer = buffer + " " + data_buf[length:length + 2]
            length = length + 2

        buf = int(len(self.textEdit_buf.toPlainText()) / 2 + 22)
        buf = hex(buf)
        if buf.startswith("0x"):
            buf = buf[2:]
            buf = buf + " " + "00"
        str = str + " " + str_date2 + " " + str_date1 + " " + str_time2 + " " + str_time1 + string_mesg + buffer + " " + "00" + " " + buf + " " + "00" + " " + "A4"
        self.edit_respon_value.clear()
        self.edit_respon_value.appendPlainText(str)

    def rigth_translate(self):
        str_key = self.edit_respon_value.toPlainText()
        str_key = str_key.split(" ")
        str1 = str_key[2] + str_key[1]
        new_item1_3 = QTableWidgetItem(str1)
        self.tableWidget.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)
        s1 = self.tableWidget.item(0, 3).text()

        str_key[10] = str_key[10] + str_key[9]
        str_key[10] = int(str_key[10].upper(), 16)
        str_key[11] = int(str_key[11].upper(), 16)
        str_key[12] = int(str_key[12].upper(), 16)
        str_key[12] = str(str_key[10]) + "/" + str(str_key[12]) + "/" + str(str_key[11])
        str_key[13] = int(str_key[13].upper(), 16)
        str_key[14] = int(str_key[14].upper(), 16)
        str_key[14] = str(str_key[14]) + ":" + str(str_key[13])

        new_item2_3 = QTableWidgetItem(str_key[3])
        self.tableWidget.setItem(1, 3, new_item2_3)
        new_item2_3.setTextAlignment(Qt.AlignCenter)
        new_item3_3 = QTableWidgetItem(str_key[4])
        self.tableWidget.setItem(2, 3, new_item3_3)
        new_item3_3.setTextAlignment(Qt.AlignCenter)
        new_item4_3 = QTableWidgetItem(str_key[5])
        self.tableWidget.setItem(3, 3, new_item4_3)
        new_item4_3.setTextAlignment(Qt.AlignCenter)
        new_item5_3 = QTableWidgetItem(str_key[6])
        self.tableWidget.setItem(4, 3, new_item5_3)
        new_item5_3.setTextAlignment(Qt.AlignCenter)
        new_item6_3 = QTableWidgetItem(str_key[7])
        self.tableWidget.setItem(5, 3, new_item6_3)
        new_item6_3.setTextAlignment(Qt.AlignCenter)
        new_item7_3 = QTableWidgetItem(str_key[8])
        self.tableWidget.setItem(6, 3, new_item7_3)
        new_item7_3.setTextAlignment(Qt.AlignCenter)
        new_item8_3 = QTableWidgetItem(str_key[12])
        self.tableWidget.setItem(7, 3, new_item8_3)
        new_item8_3.setTextAlignment(Qt.AlignCenter)
        new_item9_3 = QTableWidgetItem(str_key[14])
        self.tableWidget.setItem(8, 3, new_item9_3)
        new_item9_3.setTextAlignment(Qt.AlignCenter)

    def judge_command(self):
        if (self.combox_model.currentText() == "正常发送"):
            self.btn_true.clicked.connect(lambda: Functions.response_xml(self))
            self.btn_true.clicked.connect(self.response.close)

        if (self.combox_model.currentText() == "循环发送"):
            if (self.spin_loop.text() == "0"):
                QMessageBox.warning(self, "警告", "循环次数未输入")
            if (self.spin_loop.text() != "0"):
                self.btn_true.clicked.connect(lambda: Functions.response_xml(self))
                self.btn_true.clicked.connect(self.response.close)

        if (self.combox_model.currentText() == "延迟发送"):
            print(454545646)
            print(self.edit_delayed.text())
            if (self.edit_delayed.text().strip() == ""):
                QMessageBox.warning(self, "警告", "延时时间未输入")
            if (self.edit_delayed.text().strip() != ""):
                self.btn_true.clicked.connect(lambda: Functions.response_xml(self))
                self.btn_true.clicked.connect(self.response.close)

    def dialog_data(self):
        data = QDialog()
        data.setWindowTitle("添加数据")
        data.setFixedSize(855, 770)
        self.data_tableWidget = QTableWidget(18, 4)
        # 设置列宽

        self.data_tableWidget.setSpan(11, 0, 10, 1)
        self.data_tableWidget.setSpan(12, 1, 9, 3)
        self.data_tableWidget.setHorizontalHeaderLabels(['序号', '字段名称', '字节数', '数值'])
        self.data_tableWidget.verticalHeader().setVisible(False)

        tabWidget = QTabWidget()
        tabWidget.addTab(self.data_tableWidget, "自定义帧")

        datetime = QDateTime(QDateTime.currentDateTime())
        date = datetime.toString("yyyy/MM/dd")
        date_time = datetime.toString("hh:mm")

        new_item1 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(0, 0, new_item1)
        new_item1.setTextAlignment(Qt.AlignCenter)
        new_item1_1 = QTableWidgetItem("帧类型")
        self.data_tableWidget.setItem(0, 1, new_item1_1)
        new_item1_1.setTextAlignment(Qt.AlignCenter)
        new_item1_2 = QTableWidgetItem("2")
        self.data_tableWidget.setItem(0, 2, new_item1_2)
        new_item1_2.setTextAlignment(Qt.AlignCenter)
        new_item1_3 = QTableWidgetItem("1010")
        self.data_tableWidget.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)

        new_item2 = QTableWidgetItem("2")
        self.data_tableWidget.setItem(1, 0, new_item2)
        new_item2.setTextAlignment(Qt.AlignCenter)
        new_item2_1 = QTableWidgetItem("重传次数")
        self.data_tableWidget.setItem(1, 1, new_item2_1)
        new_item2_1.setTextAlignment(Qt.AlignCenter)
        new_item2_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(1, 2, new_item2_2)
        new_item2_2.setTextAlignment(Qt.AlignCenter)
        new_item2_3 = QTableWidgetItem("11")
        self.data_tableWidget.setItem(1, 3, new_item2_3)
        new_item2_3.setTextAlignment(Qt.AlignCenter)

        new_item3 = QTableWidgetItem("3")
        self.data_tableWidget.setItem(2, 0, new_item3)
        new_item3.setTextAlignment(Qt.AlignCenter)
        new_item3_1 = QTableWidgetItem("帧确定标记")
        self.data_tableWidget.setItem(2, 1, new_item3_1)
        new_item3_1.setTextAlignment(Qt.AlignCenter)
        new_item3_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(2, 2, new_item3_2)
        new_item3_2.setTextAlignment(Qt.AlignCenter)
        new_item3_3 = QTableWidgetItem("10")
        self.data_tableWidget.setItem(2, 3, new_item3_3)
        new_item3_3.setTextAlignment(Qt.AlignCenter)

        new_item4 = QTableWidgetItem("4")
        self.data_tableWidget.setItem(3, 0, new_item4)
        new_item4.setTextAlignment(Qt.AlignCenter)
        new_item4_1 = QTableWidgetItem("信源系统标记")
        self.data_tableWidget.setItem(3, 1, new_item4_1)
        new_item4_1.setTextAlignment(Qt.AlignCenter)
        new_item4_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(3, 2, new_item4_2)
        new_item4_2.setTextAlignment(Qt.AlignCenter)
        new_item4_3 = QTableWidgetItem("01")
        self.data_tableWidget.setItem(3, 3, new_item4_3)
        new_item4_3.setTextAlignment(Qt.AlignCenter)

        new_item5 = QTableWidgetItem("5")
        self.data_tableWidget.setItem(4, 0, new_item5)
        new_item5.setTextAlignment(Qt.AlignCenter)
        new_item5_1 = QTableWidgetItem("信源节点编码")
        self.data_tableWidget.setItem(4, 1, new_item5_1)
        new_item5_1.setTextAlignment(Qt.AlignCenter)
        new_item5_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(4, 2, new_item5_2)
        new_item5_2.setTextAlignment(Qt.AlignCenter)
        new_item5_3 = QTableWidgetItem("10")
        self.data_tableWidget.setItem(4, 3, new_item5_3)
        new_item5_3.setTextAlignment(Qt.AlignCenter)

        new_item6 = QTableWidgetItem("6")
        self.data_tableWidget.setItem(5, 0, new_item6)
        new_item6.setTextAlignment(Qt.AlignCenter)
        new_item6_1 = QTableWidgetItem("信道系统编码")
        self.data_tableWidget.setItem(5, 1, new_item6_1)
        new_item6_1.setTextAlignment(Qt.AlignCenter)
        new_item6_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(5, 2, new_item6_2)
        new_item6_2.setTextAlignment(Qt.AlignCenter)
        new_item6_3 = QTableWidgetItem("11")
        self.data_tableWidget.setItem(5, 3, new_item6_3)
        new_item6_3.setTextAlignment(Qt.AlignCenter)

        new_item7 = QTableWidgetItem("7")
        self.data_tableWidget.setItem(6, 0, new_item7)
        new_item7.setTextAlignment(Qt.AlignCenter)
        new_item7_1 = QTableWidgetItem("信道节点编码")
        self.data_tableWidget.setItem(6, 1, new_item7_1)
        new_item7_1.setTextAlignment(Qt.AlignCenter)
        new_item7_2 = QTableWidgetItem("1")
        self.data_tableWidget.setItem(6, 2, new_item7_2)
        new_item7_2.setTextAlignment(Qt.AlignCenter)
        new_item7_3 = QTableWidgetItem("11")
        self.data_tableWidget.setItem(6, 3, new_item7_3)
        new_item7_3.setTextAlignment(Qt.AlignCenter)

        new_item8 = QTableWidgetItem("8")
        self.data_tableWidget.setItem(7, 0, new_item8)
        new_item8.setTextAlignment(Qt.AlignCenter)
        new_item8_1 = QTableWidgetItem("年月日")
        self.data_tableWidget.setItem(7, 1, new_item8_1)
        new_item8_1.setTextAlignment(Qt.AlignCenter)
        new_item8_2 = QTableWidgetItem("4")
        self.data_tableWidget.setItem(7, 2, new_item8_2)
        new_item8_2.setTextAlignment(Qt.AlignCenter)
        new_item8_3 = QTableWidgetItem(date)
        self.data_tableWidget.setItem(7, 3, new_item8_3)
        new_item8_3.setTextAlignment(Qt.AlignCenter)

        new_item9 = QTableWidgetItem("9")
        self.data_tableWidget.setItem(8, 0, new_item9)
        new_item9.setTextAlignment(Qt.AlignCenter)
        new_item9_1 = QTableWidgetItem("时间")
        self.data_tableWidget.setItem(8, 1, new_item9_1)
        new_item9_1.setTextAlignment(Qt.AlignCenter)
        new_item9_2 = QTableWidgetItem("2")
        self.data_tableWidget.setItem(8, 2, new_item9_2)
        new_item9_2.setTextAlignment(Qt.AlignCenter)
        new_item9_3 = QTableWidgetItem(date_time)
        self.data_tableWidget.setItem(8, 3, new_item9_3)
        new_item9_3.setTextAlignment(Qt.AlignCenter)

        new_item10 = QTableWidgetItem("10")
        self.data_tableWidget.setItem(9, 0, new_item10)
        new_item10.setTextAlignment(Qt.AlignCenter)
        new_item10_1 = QTableWidgetItem("帧计数")
        self.data_tableWidget.setItem(9, 1, new_item10_1)
        new_item10_1.setTextAlignment(Qt.AlignCenter)
        new_item10_2 = QTableWidgetItem("4")
        self.data_tableWidget.setItem(9, 2, new_item10_2)
        new_item10_2.setTextAlignment(Qt.AlignCenter)
        new_item10_3 = QTableWidgetItem("10")
        self.data_tableWidget.setItem(9, 3, new_item10_3)
        new_item10_3.setTextAlignment(Qt.AlignCenter)

        new_item11 = QTableWidgetItem("11")
        self.data_tableWidget.setItem(10, 0, new_item11)
        new_item11.setTextAlignment(Qt.AlignCenter)
        new_item11_1 = QTableWidgetItem("备用字节")
        self.data_tableWidget.setItem(10, 1, new_item11_1)
        new_item11_1.setTextAlignment(Qt.AlignCenter)
        new_item11_2 = QTableWidgetItem("4")
        self.data_tableWidget.setItem(10, 2, new_item11_2)
        new_item11_2.setTextAlignment(Qt.AlignCenter)
        new_item11_3 = QTableWidgetItem("11")
        self.data_tableWidget.setItem(10, 3, new_item11_3)
        new_item11_3.setTextAlignment(Qt.AlignCenter)

        new_item12 = QTableWidgetItem("12")
        self.data_tableWidget.setItem(11, 0, new_item12)
        new_item12.setTextAlignment(Qt.AlignCenter)
        new_item12_1 = QTableWidgetItem("可变区")
        self.data_tableWidget.setItem(11, 1, new_item12_1)
        new_item12_1.setTextAlignment(Qt.AlignCenter)
        new_item12_2 = QTableWidgetItem("自动")
        self.data_tableWidget.setItem(11, 2, new_item12_2)
        new_item12_2.setTextAlignment(Qt.AlignCenter)
        self.textEdit_data_buf = QTextEdit()
        self.data_tableWidget.setCellWidget(12, 1, self.textEdit_data_buf)

        # mosbus界面
        widget_mosbus = QWidget()
        label_head = QLabel('<p style=line-height:150%>包头</p>')
        label_head.setStyleSheet('font:20px;')
        # 设置标签居中
        label_head.setAlignment(Qt.AlignCenter)

        # setGeometry(左右， 上下， 宽， 高)
        label_head.setGeometry(10, 10, 20, 20)
        self.table_widget_head = QTableWidget(5, 4)
        self.table_widget_head.verticalHeader().setVisible(False)
        self.table_widget_head.horizontalHeader().setVisible(False)
        head_list_item1 = ["序号", "字段名称", "字节数", "数值"]
        head_list_item2 = ["1", "传输ID", "2", "0"]
        head_list_item3 = ["2", "传输协议标识", "2", "0"]
        head_list_item4 = ["3", "命令长度", "2", "4"]
        head_list_item5 = ["4", "目标的UnitID", "1", "0"]

        for index in range(len(head_list_item1)):
            self.table_widget_head.setItem(0, index, QTableWidgetItem(head_list_item1[index]))
            self.table_widget_head.setItem(1, index, QTableWidgetItem(head_list_item2[index]))
            self.table_widget_head.setItem(2, index, QTableWidgetItem(head_list_item3[index]))
            self.table_widget_head.setItem(3, index, QTableWidgetItem(head_list_item4[index]))
            self.table_widget_head.setItem(4, index, QTableWidgetItem(head_list_item5[index]))

        # head_item1 = QTableWidgetItem("序号")
        # self.table_widget_head.setItem(0, 0, head_item1)
        # head_item1.setTextAlignment(Qt.AlignCenter)
        # head_item1_1 = QTableWidgetItem("字段名称")
        # self.table_widget_head.setItem(0, 1, head_item1_1)
        # head_item1_1.setTextAlignment(Qt.AlignCenter)
        # head_item1_2 = QTableWidgetItem("字节数")
        # self.table_widget_head.setItem(0, 2, head_item1_2)
        # head_item1_2.setTextAlignment(Qt.AlignCenter)
        # head_item1_3 = QTableWidgetItem("数值")
        # self.table_widget_head.setItem(0, 3, head_item1_3)
        # head_item1_3.setTextAlignment(Qt.AlignCenter)
        #
        # head_item2 = QTableWidgetItem("1")
        # self.table_widget_head.setItem(1, 0, head_item2)
        # head_item2.setTextAlignment(Qt.AlignCenter)
        # head_item2_1 = QTableWidgetItem("传输ID")
        # self.table_widget_head.setItem(1, 1, head_item2_1)
        # head_item2_1.setTextAlignment(Qt.AlignCenter)
        # head_item2_2 = QTableWidgetItem("2")
        # self.table_widget_head.setItem(1, 2, head_item2_2)
        # head_item2_2.setTextAlignment(Qt.AlignCenter)
        # head_item2_3 = QTableWidgetItem("0")
        # self.table_widget_head.setItem(1, 3, head_item2_3)
        # head_item2_3.setTextAlignment(Qt.AlignCenter)
        #
        # head_item3 = QTableWidgetItem("2")
        # self.table_widget_head.setItem(2, 0, head_item3)
        # head_item3.setTextAlignment(Qt.AlignCenter)
        # head_item3_1 = QTableWidgetItem("传输协议标识")
        # self.table_widget_head.setItem(2, 1, head_item3_1)
        # head_item3_1.setTextAlignment(Qt.AlignCenter)
        # head_item3_2 = QTableWidgetItem("2")
        # self.table_widget_head.setItem(2, 2, head_item3_2)
        # head_item3_2.setTextAlignment(Qt.AlignCenter)
        # head_item3_3 = QTableWidgetItem("0")
        # self.table_widget_head.setItem(2, 3, head_item3_3)
        # head_item3_3.setTextAlignment(Qt.AlignCenter)
        #
        # head_item4 = QTableWidgetItem("3")
        # self.table_widget_head.setItem(3, 0, head_item4)
        # head_item4.setTextAlignment(Qt.AlignCenter)
        # head_item4_1 = QTableWidgetItem("命令长度")
        # self.table_widget_head.setItem(3, 1, head_item4_1)
        # head_item4_1.setTextAlignment(Qt.AlignCenter)
        # head_item4_2 = QTableWidgetItem("2")
        # self.table_widget_head.setItem(3, 2, head_item4_2)
        # head_item4_2.setTextAlignment(Qt.AlignCenter)
        # head_item4_3 = QTableWidgetItem("4")
        # self.table_widget_head.setItem(3, 3, head_item4_3)
        # head_item4_3.setTextAlignment(Qt.AlignCenter)
        #
        # head_item5 = QTableWidgetItem("4")
        # self.table_widget_head.setItem(4, 0, head_item5)
        # head_item5.setTextAlignment(Qt.AlignCenter)
        # head_item5_1 = QTableWidgetItem("目标的UnitID")
        # self.table_widget_head.setItem(4, 1, head_item5_1)
        # head_item5_1.setTextAlignment(Qt.AlignCenter)
        # head_item5_2 = QTableWidgetItem("1")
        # self.table_widget_head.setItem(4, 2, head_item5_2)
        # head_item5_2.setTextAlignment(Qt.AlignCenter)
        # head_item5_3 = QTableWidgetItem("0")
        # self.table_widget_head.setItem(4, 3, head_item5_3)
        # head_item5_3.setTextAlignment(Qt.AlignCenter)

        label_command = QLabel('<p style=line-height:150%>命令码：</p>')
        label_command.setStyleSheet('font:20px;')
        label_command.setFixedSize(120, 50)
        # 设置对齐方式
        label_command.setAlignment(Qt.AlignCenter)

        self.combox_data_command = QComboBox()
        self.combox_data_command.setStyleSheet('font:20px;')
        self.combox_data_command.addItem("读输出位（01）")
        self.combox_data_command.addItem("读输出位（02）")
        self.combox_data_command.addItem("读多个寄存器（03）")
        self.combox_data_command.addItem("写输出位（05）")
        self.combox_data_command.addItem("写多个输出位（0F）")

        self.combox_data_command.currentIndexChanged.connect(lambda: Functions.add_data_data(self))

        label_space = QLabel()
        label_space1 = QLabel()
        label_space2 = QLabel()
        label_space3 = QLabel()
        label_space4 = QLabel()

        label_message = QLabel('<p style=line-height:150%>命令信息</p>')
        label_message.setStyleSheet('font:20px;')
        label_message.setAlignment(Qt.AlignCenter)
        self.table_widget_message = QTableWidget(4, 4)
        self.table_widget_message.verticalHeader().setVisible(False)
        self.table_widget_message.horizontalHeader().setVisible(False)
        new_item1 = QTableWidgetItem("序号")
        self.table_widget_message.setItem(0, 0, new_item1)
        new_item1.setTextAlignment(Qt.AlignCenter)
        new_item1_1 = QTableWidgetItem("字段名称")
        self.table_widget_message.setItem(0, 1, new_item1_1)
        new_item1_1.setTextAlignment(Qt.AlignCenter)
        new_item1_2 = QTableWidgetItem("字节数")
        self.table_widget_message.setItem(0, 2, new_item1_2)
        new_item1_2.setTextAlignment(Qt.AlignCenter)
        new_item1_3 = QTableWidgetItem("数值")
        self.table_widget_message.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)

        mosbus_layout = QFormLayout()
        # 设置水平和垂直间隔
        mosbus_layout.setVerticalSpacing(15)
        mosbus_layout.addRow(label_space)
        mosbus_layout.addRow(label_head)
        mosbus_layout.addRow(self.table_widget_head)
        mosbus_layout.addRow(label_space1)
        mosbus_layout.addRow(label_space2)
        mosbus_layout.addRow(label_space3)
        mosbus_layout.addRow(label_command, self.combox_data_command)
        mosbus_layout.addRow(label_space4)
        mosbus_layout.addRow(label_message)
        mosbus_layout.addRow(self.table_widget_message)
        tabWidget.insertTab(1, widget_mosbus, "mosbus")
        widget_mosbus.setLayout(mosbus_layout)

        hbox = QVBoxLayout()
        vbox = QHBoxLayout()
        hbox2 = QVBoxLayout()

        gridlayout1 = QFormLayout()
        self.labal = QLabel()
        self.labal2 = QLabel()
        self.labal3 = QLabel()
        self.labal4 = QLabel()
        self.btn_translate = QPushButton("<<")
        self.btn_translate.clicked.connect(lambda: Functions.left_translate_data(self))
        self.btn_reverse_translate = QPushButton(">>")
        self.btn_reverse_translate.clicked.connect(lambda: Functions.right_translate_data(self))

        gridlayout2 = QFormLayout()
        gridlayout2.addRow(self.labal)
        gridlayout2.addRow(self.labal2)
        gridlayout2.addRow(self.labal3)
        gridlayout2.addRow(self.labal4)
        gridlayout2.addRow(self.btn_translate)
        gridlayout2.addRow(self.btn_reverse_translate)
        gridlayout2.setSpacing(55)

        hbox2.addLayout(gridlayout2)
        self.label_data_model = QLabel(" 指令类型:")
        self.combox_data_model = QComboBox()
        self.combox_data_model.addItem("data")
        gridlayout1.addRow(self.label_data_model, self.combox_data_model)
        self.data_label_name = QLabel(" 设备名字:")
        self.combox_data_name = QComboBox()
        self.combox_data_name.setEditable(True)
        gridlayout1.addRow(self.data_label_name, self.combox_data_name)
        self.data_label_type = QLabel(" 设备类型:")
        self.data_combox_type = QComboBox(data)
        self.data_combox_type.addItem("TcpServer")
        gridlayout1.addRow(self.data_label_type, self.data_combox_type)
        self.data_label_ip = QLabel(" Ip 地址:")
        self.combox_data_ip = QComboBox()
        self.combox_data_ip.setEditable(True)
        gridlayout1.addRow(self.data_label_ip, self.combox_data_ip)
        self.data_label_port = QLabel(" 端口号:")
        self.combox_data_port = QComboBox()
        self.combox_data_port.setEditable(True)

        for k, v in device_message.items():
            self.combox_data_name.addItem(k)
            self.combox_data_ip.addItem(v[0])
            self.combox_data_port.addItem(v[1])

        gridlayout1.addRow(self.data_label_port, self.combox_data_port)
        self.data_label_value = QLabel(" 命令名称:", data)
        self.data_edit_key_value = QLineEdit("命令")
        gridlayout1.addRow(self.data_label_value, self.data_edit_key_value)
        self.data_label_re_value = QLabel(" 回令数据:", data)
        self.data_edit_respon_value = QPlainTextEdit()

        gridlayout1.addRow(self.data_label_re_value)
        gridlayout1.addRow(self.data_edit_respon_value)

        self.data_btn_true = QPushButton("确定", data)
        self.data_btn_data_xml = QPushButton("加载文件")
        self.data_btn_data_xml.clicked.connect(lambda: Functions.data_analysis(self))
        gridlayout1.addRow(self.data_btn_true)
        gridlayout1.addRow(self.data_btn_data_xml)

        hbox.addLayout(gridlayout1)
        gridlayout1.setSpacing(16)
        hbox2.addSpacing(3)
        vbox.addLayout(hbox, 3)
        vbox.addLayout(hbox2, 1)
        vbox.addWidget(tabWidget, 8)
        data.setLayout(vbox)

        self.data_btn_true.clicked.connect(lambda: Functions.data_xml(self))
        self.data_btn_true.clicked.connect(data.close)
        data.exec_()

    def add_data_data(self):
        if self.combox_data_command.currentIndex() == 0:
            mosbus_list_item1 = ["1", "命令码", "1", "01"]
            mosbus_list_item2 = ["2", "回令中的字节数", "1", "1"]
            mosbus_list_item3 = ["3", "点位置", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_data_command.currentIndex() == 1:
            mosbus_list_item1 = ["1", "命令码", "1", "02"]
            mosbus_list_item2 = ["2", "回令中的字节数", "1", "1"]
            mosbus_list_item3 = ["3", "点位置", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_data_command.currentIndex() == 2:
            mosbus_list_item1 = ["1", "命令码", "1", "03"]
            mosbus_list_item2 = ["2", "返回值的字节个数", "1", "1"]
            mosbus_list_item3 = ["3", "寄存器值", "1", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_data_command.currentIndex() == 3:
            mosbus_list_item1 = ["1", "命令码", "1", "05"]
            mosbus_list_item2 = ["2", "地址", "2", "0"]
            mosbus_list_item3 = ["3", "打开或关闭", "1", "00"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

        if self.combox_data_command.currentIndex() == 4:
            mosbus_list_item1 = ["1", "命令码", "1", "0F"]
            mosbus_list_item2 = ["2", "地址", "2", "0"]
            mosbus_list_item3 = ["3", "位数", "3", "0"]
            for index in range(len(mosbus_list_item1)):
                self.table_widget_message.setItem(1, index, QTableWidgetItem(mosbus_list_item1[index]))
                self.table_widget_message.setItem(2, index, QTableWidgetItem(mosbus_list_item2[index]))
                self.table_widget_message.setItem(3, index, QTableWidgetItem(mosbus_list_item3[index]))

    def data_analysis(self):
        fileName = QFileDialog.getOpenFileName(self, "打开文件", "./file_xml/data")
        file = QFile(fileName[0])
        doc = QDomDocument()
        doc.setContent(file)
        com = doc.firstChildElement("command")
        dev = com.firstChildElement("device")
        data_name = dev.attribute("name")
        self.combox_data_name.addItem(data_name)
        par = dev.firstChildElement("parameters")
        data_ip = par.attribute("ip")
        self.combox_data_ip.addItem(data_ip)
        data_port = par.attribute("port")
        self.combox_data_port.addItem(data_port)
        respon = par.firstChildElement("response")
        data_value = respon.attribute("value")
        self.data_edit_respon_value.appendPlainText(data_value)

    def left_translate_data(self):
        str = "A5"
        stri = self.data_tableWidget.item(0, 3).text()
        if len(stri) == 0:
            stri = "00" + " " + "00"
        if len(stri) == 1:
            stri = "00" + " " + stri + "0"
        if len(stri) == 2:
            stri = "00" + " " + stri
        if len(stri) == 3:
            stri1 = stri[0:2]
            stri2 = stri[2:3]
            stri2 = stri2 + "0"
            stri = stri2 + " " + stri
        if len(stri) == 4:
            stri3 = stri[0:2]
            stri4 = stri[2:4]
            stri = stri4 + " " + stri3
        str = str + " " + stri
        k = 1
        while k < 8:
            string = self.data_tableWidget.item(k, 3).text()
            if len(string) == 1:
                string = string + "0"
            # string = string[::-1] #字符串反转
            if k == 7:
                str_date = string
                str_date = str_date.split('/')
                print(str_date)
                j = 0
                while j < len(str_date) + 1:
                    if j == 0:
                        str_year1 = str_date[j]
                        str_year1 = hex(int(str_year1))
                        if str_year1.startswith("0x"):
                            str_year1 = str_year1[2:]
                        str_year1_1 = str_year1[0:1]
                        str_year1_1 = str_year1_1.zfill(2)
                        str_year2_1 = str_year1[1:3]
                        str_year2_1 = str_year2_1.zfill(2)
                        str = str + " " + str_year2_1
                        str = str + " " + str_year1_1
                    if j == 1:
                        str_date1 = str_date[j]
                        str_date1 = hex(int(str_date1))
                        if str_date1.startswith("0x"):
                            str_date1 = str_date1[2:]
                            str_date1 = str_date1.zfill(2)

                    if j == 2:
                        str_date2 = str_date[j]
                        print(str_date2)
                        str_date2 = hex(int(str_date2))
                        print(str_date2)
                        if str_date2.startswith("0x"):
                            str_date2 = str_date2[2:]
                            print(str_date2)
                            str_date2 = str_date2.zfill(2)
                            print(str_date2)
                    j = j + 1
                break
            str = str + " " + string
            k = k + 1
        # str = str + " " + str_date1+" "+ str_date2 + "A4"
        x = 8
        while x < 10:
            string_time = self.data_tableWidget.item(x, 3).text()
            if x == 8:
                str_time = string_time
                str_time = str_time.split(":")
                i = 0
                while i < len(str_time):
                    str_time1 = str_time[0]
                    str_time1 = hex(int(str_time1))
                    if str_time1.startswith("0x"):
                        str_time1 = str_time1[2:]
                        str_time1 = str_time1.zfill(2)
                    str_time2 = str_time[1]
                    str_time2 = hex(int(str_time2))
                    if str_time2.startswith("0x"):
                        str_time2 = str_time2[2:]
                        str_time2 = str_time2.zfill(2)
                    i = i + 1
                break
            x = x + 1
        y = 9
        while y < 10:
            string_mesg = self.data_tableWidget.item(y, 3).text()
            if len(string_mesg) == 0:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + "00"
            if len(string_mesg) == 1:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + string_mesg + "0"
            if len(string_mesg) == 2:
                string_mesg = "00" + " " + "00" + " " + "00" + " " + string_mesg
            if len(string_mesg) == 3:
                string_mesg1 = string_mesg[0:2]
                string_mesg2 = string_mesg[2:3] + "0"
                string_mesg = "00" + " " + "00" + " " + string_mesg2 + " " + string_mesg1
            if len(string_mesg) == 4:
                string_mesg3 = string_mesg[0:2]
                string_mesg4 = string_mesg[2:4]
                string_mesg = "00" + " " + "00" + " " + string_mesg4 + " " + string_mesg3
            if len(string_mesg) == 5:
                string_mesg5 = string_mesg[0:2]
                string_mesg6 = string_mesg[2:4]
                string_mesg7 = string_mesg[4:5] + "0"
                string_mesg = "00" + " " + string_mesg7 + " " + string_mesg6 + " " + string_mesg5
            if len(string_mesg) == 6:
                string_mesg8 = string_mesg[0:2]
                string_mesg9 = string_mesg[2:4]
                string_mesg10 = string_mesg[4:6]
                string_mesg = "00" + " " + string_mesg10 + " " + string_mesg9 + " " + string_mesg8
            if len(string_mesg) == 7:
                string_mesg11 = string_mesg[0:2]
                string_mesg12 = string_mesg[2:4]
                string_mesg13 = string_mesg[4:6]
                string_mesg14 = string_mesg[6:7] + "0"
                string_mesg = string_mesg14 + " " + string_mesg13 + " " + string_mesg12 + " " + string_mesg11
            if len(string_mesg) == 8:
                string_mesg15 = string_mesg[0:2]
                string_mesg16 = string_mesg[2:4]
                string_mesg17 = string_mesg[4:6]
                string_mesg18 = string_mesg[6:8]
                string_mesg = string_mesg18 + " " + string_mesg17 + " " + string_mesg16 + " " + string_mesg15
            y = y + 1
        string_mesg = " " + string_mesg

        z = 10
        while z < 11:
            string_mesgz = self.data_tableWidget.item(z, 3).text()
            if len(string_mesgz) == 0:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + "00"
            if len(string_mesgz) == 1:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + string_mesgz + "0"
            if len(string_mesgz) == 2:
                string_mesgz = "00" + " " + "00" + " " + "00" + " " + string_mesgz
            if len(string_mesgz) == 3:
                string_mesg1 = string_mesgz[0:2]
                string_mesg2 = string_mesgz[2:3] + "0"
                string_mesgz = "00" + " " + "00" + " " + string_mesg2 + " " + string_mesg1
            if len(string_mesgz) == 4:
                string_mesg3 = string_mesgz[0:2]
                string_mesg4 = string_mesgz[2:4]
                string_mesgz = "00" + " " + "00" + " " + string_mesg4 + " " + string_mesg3
            if len(string_mesgz) == 5:
                string_mesg5 = string_mesgz[0:2]
                string_mesg6 = string_mesgz[2:4]
                string_mesg7 = string_mesgz[4:5] + "0"
                string_mesgz = "00" + " " + string_mesg7 + " " + string_mesg6 + " " + string_mesg5
            if len(string_mesgz) == 6:
                string_mesg8 = string_mesgz[0:2]
                string_mesg9 = string_mesgz[2:4]
                string_mesg10 = string_mesgz[4:6]
                string_mesgz = "00" + " " + string_mesg10 + " " + string_mesg9 + " " + string_mesg8
            if len(string_mesgz) == 7:
                string_mesg11 = string_mesgz[0:2]
                string_mesg12 = string_mesgz[2:4]
                string_mesg13 = string_mesgz[4:6]
                string_mesg14 = string_mesgz[6:7] + "0"
                string_mesgz = string_mesg14 + " " + string_mesg13 + " " + string_mesg12 + " " + string_mesg11
            if len(string_mesgz) == 8:
                string_mesg15 = string_mesgz[0:2]
                string_mesg16 = string_mesgz[2:4]
                string_mesg17 = string_mesgz[4:6]
                string_mesg18 = string_mesgz[6:8]
                string_mesgz = string_mesg18 + " " + string_mesg17 + " " + string_mesg16 + " " + string_mesg15
            z = z + 1
        string_mesg = string_mesg + " " + string_mesgz
        length = 0
        buffer = ""
        data_buf = self.textEdit_data_buf.toPlainText()
        # data_buf = int(data_buf)
        while length < len(data_buf):
            buffer = buffer + " " + data_buf[length:length + 2]
            length = length + 2

        buf = int(len(self.textEdit_data_buf.toPlainText()) / 2 + 22)
        buf = hex(buf)
        if buf.startswith("0x"):
            buf = buf[2:]
            buf = buf + " " + "00"

        str = str + " " + str_date2 + " " + str_date1 + " " + str_time2 + " " + str_time1 + string_mesg + buffer + " " + "00" + " " + buf + " " + "00" + " " + "A4"

        self.data_edit_respon_value.clear()
        self.data_edit_respon_value.appendPlainText(str)

    def right_translate_data(self):
        str_data = self.data_edit_respon_value.toPlainText()
        str_data = str_data.split(" ")
        str1 = str_data[2] + str_data[1]
        new_item1_3 = QTableWidgetItem(str1)
        self.data_tableWidget.setItem(0, 3, new_item1_3)
        new_item1_3.setTextAlignment(Qt.AlignCenter)
        s1 = self.data_tableWidget.item(0, 3).text()

        str_data[10] = str_data[10] + str_data[9]
        str_data[10] = int(str_data[10].upper(), 16)
        str_data[11] = int(str_data[11].upper(), 16)
        str_data[12] = int(str_data[12].upper(), 16)
        str_data[12] = str(str_data[10] + "/" + str_data[11] + "/" + str_data[12])
        str_data[13] = int(str_data[13].upper(), 16)
        str_data[14] = int(str_data[14].upper(), 16)
        str_data[14] = str_data[13] + ":" + str_data[14]

        new_item2_3 = QTableWidgetItem(str_data[3])
        self.data_tableWidget.setItem(1, 3, new_item2_3)
        new_item2_3.setTextAlignment(Qt.AlignCenter)
        new_item3_3 = QTableWidgetItem(str_data[4])
        self.data_tableWidget.setItem(2, 3, new_item3_3)
        new_item3_3.setTextAlignment(Qt.AlignCenter)
        new_item4_3 = QTableWidgetItem(str_data[5])
        self.data_tableWidget.setItem(3, 3, new_item4_3)
        new_item4_3.setTextAlignment(Qt.AlignCenter)
        new_item5_3 = QTableWidgetItem(str_data[6])
        self.data_tableWidget.setItem(4, 3, new_item5_3)
        new_item5_3.setTextAlignment(Qt.AlignCenter)
        new_item6_3 = QTableWidgetItem(str_data[7])
        self.data_tableWidget.setItem(5, 3, new_item6_3)
        new_item6_3.setTextAlignment(Qt.AlignCenter)
        new_item7_3 = QTableWidgetItem(str_data[8])
        self.data_tableWidget.setItem(6, 3, new_item7_3)
        new_item7_3.setTextAlignment(Qt.AlignCenter)
        new_item8_3 = QTableWidgetItem(str_data[12])
        self.data_tableWidget.setItem(7, 3, new_item8_3)
        new_item8_3.setTextAlignment(Qt.AlignCenter)
        new_item9_3 = QTableWidgetItem(str_data[14])
        self.data_tableWidget.setItem(8, 3, new_item9_3)
        new_item9_3.setTextAlignment(Qt.AlignCenter)

    def dialog_delete_device(self):
        deleteDevice = QDialog()
        self.formlayout_data = QFormLayout(deleteDevice)
        deleteDevice.setWindowTitle("删除设备")
        deleteDevice.setFixedSize(300, 240)

        self.label_deleteType = QLabel("指令类型")
        self.combox_deleteDeviceType = QComboBox(deleteDevice)
        self.combox_deleteDeviceType.addItem("stopdevice")

        self.data_label_name = QLabel("设备名字:")
        self.combox_delete_name = QComboBox()
        self.combox_delete_name.setEditable(True)

        self.data_label_type = QLabel("设备类型:")
        self.data_combox_type = QComboBox(deleteDevice)
        self.data_combox_type.addItem("TcpServer")

        self.data_label_ip = QLabel("ip地址:")
        self.combox_delete_ip = QComboBox()
        self.combox_delete_ip.setEditable(True)

        self.data_label_port = QLabel("端口号:")
        self.combox_delete_port = QComboBox()
        self.combox_delete_port.setEditable(True)

        for k, v in device_message.items():
            self.combox_delete_name.addItem(k)
            self.combox_delete_ip.addItem(v[0])
            self.combox_delete_port.addItem(v[1])

        self.data_btn_true = QPushButton("确定", deleteDevice)
        self.data_btn_xml_deleteDevice = QPushButton("加载文件")

        self.data_btn_xml_deleteDevice.clicked.connect(lambda: Functions.delete_device_analysis(self))
        self.data_btn_true.clicked.connect(lambda: Functions.delete_device_xml(self))
        self.data_btn_true.clicked.connect(deleteDevice.close)

        self.formlayout_data.addRow(self.label_deleteType, self.combox_deleteDeviceType)
        self.formlayout_data.addRow(self.data_label_name, self.combox_delete_name)
        self.formlayout_data.addRow(self.data_label_type, self.data_combox_type)
        self.formlayout_data.addRow(self.data_label_ip, self.combox_delete_ip)
        self.formlayout_data.addRow(self.data_label_port, self.combox_delete_port)
        self.formlayout_data.addRow(self.data_btn_true)
        self.formlayout_data.addRow(self.data_btn_xml_deleteDevice)

        deleteDevice.exec_()

    def delete_device_analysis(self):
        fileName = QFileDialog.getOpenFileName(self, '打开文件', './file_xml/deleteDevice')
        file_newDevice = QFile(fileName[0])
        doc = QDomDocument()
        doc.setContent(file_newDevice)
        com = doc.firstChildElement("command")
        dev = com.firstChildElement("device")
        device_name = dev.attribute("name")
        self.combox_delete_name.addItem(device_name)
        par = dev.firstChildElement("parameters")
        newDevice_ip = par.attribute("ip")
        self.combox_delete_ip.addItem(newDevice_ip)
        newDevice_port = par.attribute("port")
        self.combox_delete_port.addItem(newDevice_port)

    def dialog_delete_key(self):
        deleteKey = QDialog()
        self.formlayout_data = QFormLayout(deleteKey)
        deleteKey.setWindowTitle("删除回令")
        deleteKey.setFixedSize(270, 230)

        self.label_deleteName = QLabel("设备名字:")
        self.combox_deleteKey_name = QComboBox()
        self.combox_deleteKey_name.setEditable(True)

        self.label_deleteIp = QLabel("ip地址:")
        self.combox_deleteKey_ip = QComboBox()
        self.combox_deleteKey_ip.setEditable(True)

        self.label_deletePort = QLabel("端口号:")
        self.combox_deleteKey_port = QComboBox()
        self.combox_deleteKey_port.setEditable(True)

        self.label_deleteType = QLabel("指令类型:")
        self.combox_deleteType = QComboBox(deleteKey)
        self.combox_deleteType.addItem("deleteCommand")

        self.label_delete_Value = QLabel("命令值:", deleteKey)
        self.edit_delete_Value = QLineEdit(deleteKey)

        self.delete_btn_true = QPushButton("确定", deleteKey)
        self.delete_btn_xml = QPushButton("加载文件")

        self.delete_btn_xml.clicked.connect(lambda: Functions.delete_key_analysis(self))
        self.delete_btn_true.clicked.connect(lambda: Functions.delete_command_xml(self))
        self.delete_btn_true.clicked.connect(deleteKey.close)

        self.formlayout_data.addRow(self.label_deleteType, self.combox_deleteType)
        self.formlayout_data.addRow(self.label_deleteName, self.combox_deleteKey_name)
        self.formlayout_data.addRow(self.label_deleteIp, self.combox_deleteKey_ip)
        self.formlayout_data.addRow(self.label_deletePort, self.combox_deleteKey_port)
        self.formlayout_data.addRow(self.label_delete_Value, self.edit_delete_Value)
        self.formlayout_data.addRow(self.delete_btn_true)
        self.formlayout_data.addRow(self.delete_btn_xml)
        deleteKey.exec_()

    def delete_key_analysis(self):
        file_name = QFileDialog.getOpenFileName(self, '打开文件', './file_xml/deleteCommand')
        file_new_device = QFile(file_name[0])
        doc = QDomDocument()
        doc.setContent(file_new_device)
        com = doc.firstChildElement("command")
        par = com.firstChildElement("device")
        delete_key_name = par.attribute("name")
        self.combox_deleteKey_name.addItem(delete_key_name)
        delete_key_ip = par.attribute("ip")
        self.combox_deleteKey_ip.addItem(delete_key_ip)
        delete_key_port = par.attribute("port")
        self.combox_deleteKey_port.addItem(delete_key_port)
        delete_key = par.firstChildElement("key")
        delete_value_name = delete_key.attribute("keyname")
        self.edit_delete_Value.setText(delete_value_name)

    def new_device_xml(self):
        if not os.path.exists('./file_xml/newDevice'):
            os.makedirs('./file_xml/newDevice')
        file = QFileDialog.getSaveFileName(self, "保存文件", "./file_xml/newDevice")
        file_respon = QFile(file[0])

        if file_respon.open(QIODevice.WriteOnly):
            doc = QDomDocument()
            ins = QDomProcessingInstruction()
            ins = doc.createProcessingInstruction("xml", " version=\"1.0\" encoding=\"UTF-8\"")
            doc.appendChild(ins)

            root = doc.createElement("command")
            type_respon = QDomAttr()
            type_respon = doc.createAttribute("type")
            type_respon.setNodeValue(self.combox_send_model.currentText())
            root.setAttributeNode(type_respon)
            doc.appendChild(root)

            newDevice = doc.createElement("device")
            newDevice_name = QDomAttr()
            newDevice_name = doc.createAttribute("name")
            newDevice_name.setNodeValue(self.combox_newDevice_name.currentText())
            newDevice.setAttributeNode(newDevice_name)

            newDevice_type = QDomAttr()
            newDevice_type = doc.createAttribute("type")
            newDevice_type.setNodeValue(self.combox_type.currentText())
            newDevice.setAttributeNode(newDevice_type)
            root.appendChild(newDevice)

            device_para = doc.createElement("parameters")
            device_paraIP = QDomAttr()
            device_paraIP = doc.createAttribute("ip")
            device_paraIP.setNodeValue(self.combox_newDevice_ip.currentText())
            device_para.setAttributeNode(device_paraIP)

            device_paraPort = QDomAttr()
            device_paraPort = doc.createAttribute("port")
            device_paraPort.setNodeValue(self.combox_newDevice_port.currentText())
            device_para.setAttributeNode(device_paraPort)
            newDevice.appendChild(device_para)

            device_message[self.combox_newDevice_name.currentText()] = [self.combox_newDevice_ip.currentText(),
                                                                        self.combox_newDevice_port.currentText()]

            stream = QTextStream(file_respon)
            doc.save(stream, 4)
            file_respon.close()
            self.edit_tab.currentWidget().edit.insertPlainText("\twith allure.step(\"new_device\"):\n" +
                                                                   "\t\tnew_device(\"" + file[0] + "\")")

    def response_xml(self):
        if not os.path.exists('./file_xml/response'):
            os.makedirs('./file_xml/response')
        file = QFileDialog.getSaveFileName(self, "保存文件", "./file_xml/response")
        file_respon = QFile(file[0])
        if file_respon.open(QIODevice.WriteOnly):
            doc = QDomDocument()
            ins = QDomProcessingInstruction()
            ins = doc.createProcessingInstruction("xml", " version=\"1.0\" encoding=\"UTF-8\"")
            doc.appendChild(ins)

            root = doc.createElement("command")
            type_respon = QDomAttr()
            type_respon = doc.createAttribute("type")
            type_respon.setNodeValue(self.combox_send_model.currentText())
            root.setAttributeNode(type_respon)
            doc.appendChild(root)

            device_respon = doc.createElement("device")
            name_respon = QDomAttr()
            name_respon = doc.createAttribute("name")
            name_respon.setNodeValue(self.combox_response_name.currentText())
            device_respon.setAttributeNode(name_respon)

            respon_type = QDomAttr()
            respon_type = doc.createAttribute("type")
            respon_type.setNodeValue(self.combox_type.currentText())
            device_respon.setAttributeNode(respon_type)
            print("sdfa")
            root.appendChild(device_respon)

            respon_para = doc.createElement("parameters")
            respon_ip = QDomAttr()
            respon_ip = doc.createAttribute("ip")
            respon_ip.setNodeValue(self.combox_response_ip.currentText())
            respon_para.setAttributeNode(respon_ip)

            respon_port = QDomAttr()
            respon_port = doc.createAttribute("port")
            respon_port.setNodeValue(self.combox_response_port.currentText())
            respon_para.setAttributeNode(respon_port)
            device_respon.appendChild(respon_para)

            device_message[self.combox_response_name.currentText()] = [self.combox_response_ip.currentText(),
                                                                       self.combox_response_port.currentText()]

            respon_key = doc.createElement("key")
            respon_value = QDomAttr()
            respon_value = doc.createAttribute("value")
            respon_value.setNodeValue(self.edit_key_value.text())
            respon_key.setAttributeNode(respon_value)

            respon_key_name = QDomAttr()
            respon_key_name = doc.createAttribute("keyname")
            respon_key_name.setNodeValue(self.edit_keyName.text())
            respon_key.setAttributeNode(respon_key_name)

            respon_index = QDomAttr()
            respon_index = doc.createAttribute("index")
            respon_index.setNodeValue(self.combox_index.text())
            respon_key.setAttributeNode(respon_index)

            respon_length = QDomAttr()
            respon_length = doc.createAttribute("length")
            respon_length.setNodeValue(self.spin_length.text())
            respon_key.setAttributeNode(respon_length)
            respon_para.appendChild(respon_key)

            respon = doc.createElement("response")
            respon_mode = QDomAttr()
            respon_mode = doc.createAttribute("mode")
            if (self.combox_model.currentText() == "正常发送"):
                respon_mode.setNodeValue("0")
            if (self.combox_model.currentText() == "循环发送"):
                respon_mode.setNodeValue("1")
            if (self.combox_model.currentText() == "延迟发送"):
                respon_mode.setNodeValue("2")
            respon.setAttributeNode(respon_mode)

            resp_name = QDomAttr()
            resp_name = doc.createAttribute("name")
            resp_name.setNodeValue("回令1")
            respon.setAttributeNode(resp_name)

            resp_value = QDomAttr()
            resp_value = doc.createAttribute("value")
            resp_value.setNodeValue(self.edit_respon_value.toPlainText())
            respon.setAttributeNode(resp_value)

            respon_loop = QDomAttr()
            respon_loop = doc.createAttribute("loop")
            respon_loop.setNodeValue(self.spin_loop.text())
            respon.setAttributeNode(respon_loop)

            respon_delayed = QDomAttr()
            respon_delayed = doc.createAttribute("delayed")
            respon_delayed.setNodeValue(self.edit_delayed.text())
            respon.setAttributeNode(respon_delayed)
            respon_key.appendChild(respon)

            stream = QTextStream(file_respon)
            doc.save(stream, 4)
            file_respon.close()
            self.edit_tab.currentWidget().edit.insertPlainText(
                "\twith allure.step(\"add_key\"):\n" + "\t\tadd_key(\"" + file[0] + "\")")

    def data_xml(self):
        if not os.path.exists('./file_xml/data'):
            os.makedirs('./file_xml/data')
        file = QFileDialog.getSaveFileName(self, "保存文件", "./file_xml/data")
        file_respon = QFile(file[0])
        if file_respon.open(QIODevice.WriteOnly):
            doc = QDomDocument()
            ins = QDomProcessingInstruction()
            ins = doc.createProcessingInstruction("xml", " version=\"1.0\" encoding=\"UTF-8\"")
            doc.appendChild(ins)

            root = doc.createElement("command")
            type_respon = QDomAttr()
            type_respon = doc.createAttribute("type")
            type_respon.setNodeValue(self.combox_data_model.currentText())
            root.setAttributeNode(type_respon)
            doc.appendChild(root)

            data_device = doc.createElement("device")
            data_name = QDomAttr()
            data_name = doc.createAttribute("name")
            data_name.setNodeValue(self.combox_data_name.currentText())
            data_device.setAttributeNode(data_name)

            data_type = QDomAttr()
            data_type = doc.createAttribute("type")
            data_type.setNodeValue(self.data_combox_type.currentText())
            data_device.setAttributeNode(data_type)
            root.appendChild(data_device)

            data_para = doc.createElement("parameters")
            data_parameters = QDomAttr()
            data_parameters = doc.createAttribute("ip")
            data_parameters.setNodeValue(self.combox_data_ip.currentText())
            data_para.setAttributeNode(data_parameters)

            data_parametersPort = QDomAttr()
            data_parametersPort = doc.createAttribute("port")
            data_parametersPort.setNodeValue(self.combox_data_port.currentText())
            data_para.setAttributeNode(data_parametersPort)
            data_device.appendChild(data_para)

            device_message[self.combox_data_name.currentText()] = [self.combox_data_ip.currentText(),
                                                                   self.combox_data_port.currentText()]
            data_respon = doc.createElement("response")
            data_responName = QDomAttr()
            data_responName = doc.createAttribute("name")
            data_responName.setNodeValue("回令")
            data_respon.setAttributeNode(data_responName)

            data_responValue = QDomAttr()
            data_responValue = doc.createAttribute("value")
            data_responValue.setNodeValue(self.data_edit_respon_value.toPlainText())
            data_respon.setAttributeNode(data_responValue)
            data_para.appendChild(data_respon)
            stream = QTextStream(file_respon)
            doc.save(stream, 4)
            file_respon.close()
            self.edit_tab.currentWidget().edit.insertPlainText(
                "\twith allure.step(\"add_data\"):\n" + "\t\tadd_data(\"" + file[0] + "\")")

    def delete_device_xml(self):
        if not os.path.exists('./file_xml/deleteDevice'):
            os.makedirs('./file_xml/deleteDevice')
        file = QFileDialog.getSaveFileName(self, "保存文件", "./file_xml/deleteDevice")
        file_respon = QFile(file[0])
        if file_respon.open(QIODevice.WriteOnly):
            doc = QDomDocument()
            ins = QDomProcessingInstruction()
            ins = doc.createProcessingInstruction("xml", " version=\"1.0\" encoding=\"UTF-8\"")
            doc.appendChild(ins)

            root = doc.createElement("command")
            delete_device = QDomAttr()
            delete_device = doc.createAttribute("type")
            delete_device.setNodeValue(self.combox_deleteDeviceType.currentText())
            root.setAttributeNode(delete_device)
            doc.appendChild(root)

            delete_Device = doc.createElement("device")
            delete_Device_name = QDomAttr()
            delete_Device_name = doc.createAttribute("name")
            delete_Device_name.setNodeValue(self.combox_delete_name.currentText())
            delete_Device.setAttributeNode(delete_Device_name)

            deleteDevice_type = QDomAttr()
            deleteDevice_type = doc.createAttribute("type")
            deleteDevice_type.setNodeValue(self.data_combox_type.currentText())
            delete_Device.setAttributeNode(deleteDevice_type)
            root.appendChild(delete_Device)

            delete_para = doc.createElement("parameters")
            delete_deviceIp = QDomAttr()
            delete_deviceIp = doc.createAttribute("ip")
            delete_deviceIp.setNodeValue(self.combox_delete_ip.currentText())
            delete_para.setAttributeNode(delete_deviceIp)

            delete_devicePort = QDomAttr()
            delete_devicePort = doc.createAttribute("port")
            delete_devicePort.setNodeValue(self.combox_delete_port.currentText())
            delete_para.setAttributeNode(delete_devicePort)
            delete_Device.appendChild(delete_para)

            device_message[self.combox_delete_name.currentText()] = [self.combox_delete_ip.currentText(),
                                                                     self.combox_delete_port.currentText()]
            stream = QTextStream(file_respon)
            doc.save(stream, 4)
            file_respon.close()
            self.edit_tab.currentWidget().edit.insertPlainText(
                "\twith allure.step(\"delete_device\"):\n" + "\t\tdelete_device(\"" + file[0] + "\")")

    def delete_command_xml(self):
        if not os.path.exists('./file_xml/deleteCommand'):
            os.makedirs('./file_xml/deleteCommand')
        file = QFileDialog.getSaveFileName(self, "保存文件", "./file_xml/deleteCommand")
        file_respon = QFile(file[0])
        if file_respon.open(QIODevice.WriteOnly):
            doc = QDomDocument()
            ins = QDomProcessingInstruction()
            ins = doc.createProcessingInstruction("xml", " version=\"1.0\" encoding=\"UTF-8\"")
            doc.appendChild(ins)

            root = doc.createElement("command")
            deleteCommand = QDomAttr()
            deleteCommand = doc.createAttribute("type")
            deleteCommand.setNodeValue(self.combox_deleteType.currentText())
            root.setAttributeNode(deleteCommand)
            doc.appendChild(root)

            response_para = doc.createElement("device")
            response_paraIp = QDomAttr()
            response_paraIp = doc.createAttribute("name")
            response_paraIp.setNodeValue(self.combox_deleteKey_name.currentText())
            response_para.setAttributeNode(response_paraIp)

            response_paraIp = QDomAttr()
            response_paraIp = doc.createAttribute("ip")
            response_paraIp.setNodeValue(self.combox_deleteKey_ip.currentText())
            response_para.setAttributeNode(response_paraIp)

            response_paraPort = QDomAttr()
            response_paraPort = doc.createAttribute("port")
            response_paraPort.setNodeValue(self.combox_deleteKey_port.currentText())
            response_para.setAttributeNode(response_paraPort)
            root.appendChild(response_para)

            respon_key = doc.createElement("key")
            respon_value = QDomAttr()
            respon_value = doc.createAttribute("keyname")
            respon_value.setNodeValue(self.edit_delete_Value.text())
            respon_key.setAttributeNode(respon_value)
            response_para.appendChild(respon_key)

            stream = QTextStream(file_respon)
            doc.save(stream, 4)
            file_respon.close()
            self.edit_tab.currentWidget().edit.insertPlainText(
                "\twith allure.step(\"delete_key\"):\n" + "\t\tdelete_key(\"" + file[0] + "\")")

    def disconnect_clicked(self):
        self.socket.disconnectFromHost()
        self.socket.close()
        QMessageBox.information(self, "提示", "网络断开")
        self.btn_send.setEnabled(False)

    def clear_text(self):
        self.textEdit_send.clear()
