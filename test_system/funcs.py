import subprocess
import sys
import time
import pyautogui
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QApplication
from threading import Thread
import IDE
import screenShot
import os

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


class Functions(IDE.MenuTools):

    def screenshot_function(self, method=None):
        global shot_flag
        shot_flag = False
        self.setVisible(False)
        time.sleep(1)
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if sys.platform.startswith('win32'):
            scs = screenShot.ScreenShot(screenshot_dir, i)
            shot_flag = scs.shot_flag
        elif sys.platform.startswith('linux'):
            clib = QApplication.clipboard()
            clib.clear()
            pyautogui.hotkey('shift', 'ctrl', 'prtsc')
            start_time = time.time()
            while True:
                end_time = time.time()
                if clib.mimeData().hasImage():
                    clib.image().save(screenshot_dir + i + ".jpg", "jpg")
                    shot_flag = True
                    break
                if end_time - start_time > 10:
                    break
        if shot_flag:
            if method:
                self.edit_tab.currentWidget().edit.insertPlainText(
                    method + "(Template(r\"" + screenshot_dir + i + ".jpg\"))")
                self.setVisible(True)
                self.edit_tab.currentWidget().edit.setFocus()
                pyautogui.press('enter')
            else:
                self.edit_tab.currentWidget().edit.insertPlainText(
                    "Template(r\"" + screenshot_dir + i + ".jpg\")")
                self.setVisible(True)
            shot_flag = False
        else:
            self.setVisible(True)

    def screenshot(self):
        Functions.screenshot_function(self)

    def insert_picture(self):
        picture_path_information = QFileDialog.getOpenFileName(self, '请选择图片', '.', '*.jpg *.png *.jpeg')
        picture_path = picture_path_information[0]
        if picture_path:
            self.edit_tab.currentWidget().edit.insertPlainText("Template(r\"" + picture_path + "\")")

    def part_run(self):
        pass

    def run(self):
        try:
            self.console_text.clear()

            def pp():
                sbp = subprocess.Popen("python " + self.edit_tab.currentWidget().edit_name,
                                       cwd=self.edit_tab.currentWidget().cwd, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
                for line in iter(sbp.stdout.readline, 'b'):
                    self.console_text.insertPlainText(line.decode())
                    self.console_text.moveCursor(QTextCursor.End)
                    if not subprocess.Popen.poll(sbp) is None:
                        break
                sbp.stdout.close()

            global t
            t = Thread(target=pp)
            t.start()
            '''logger = logging.getLogger(" ")
            logger.setLevel(logging.DEBUG)
            sh = logging.FileHandler()
            logger.addHandler(sh)'''
        except Exception as e:
            print(e)
        '''with open(self.edit_tab.currentWidget().path, 'r', encoding='utf-8') as f:
            exec(f.read())'''

    def stop_run(self):
        global t
        t.stop()

    def wait(self):
        Functions.screenshot_function(self, "wait")

    def waitVanish(self):
        Functions.screenshot_function(self, "waitVanish")

    def exists(self):
        Functions.screenshot_function(self, "exists")

    def click(self):
        Functions.screenshot_function(self, "click")

    def double_click(self):
        Functions.screenshot_function(self, "double_click")

    def right_click(self):
        Functions.screenshot_function(self, "right_click")

    def swipe(self):
        """self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "swipe(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')"""
        pass

    def hover(self):
        # 鼠标悬浮在该图片位置上
        Functions.screenshot_function(self, "hover")

    def keyevent(self):
        # 模拟按下键盘上某个键
        """keyevent_dialog = QInputDialog(self)
            keyevent_dialog.open()  # exec 模态,应用程序级,其他窗口不可见;open 窗口级,除了关联的之外都可交互;show 所有都可正常交互
            keyevent_dialog.resize(400, 100)
            keyevent_dialog.setWindowTitle('输入要按下的键的键码')"""
        keyevent_value = QInputDialog.getText(self, '按键输入', '例如:(tab/enter/f1)')
        if keyevent_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("keyevent(\"" + keyevent_value[0] + "\")")
            self.edit_tab.currentWidget().edit.setFocus()
            pyautogui.press('enter')

    def snapshot(self):
        # 截取当前屏幕全图
        self.edit_tab.currentWidget().edit.insertPlainText("snapshot(msg=\"请填写测试点\")")
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def text(self):
        # 输入文本，文本框需要处于激活状态
        keyevent_value = QInputDialog.getText(self, '文字输入', '内容')
        if keyevent_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("text(\"" + keyevent_value[0] + "\")")
            self.edit_tab.currentWidget().edit.setFocus()
            pyautogui.press('enter')

    def assert_equal(self):
        global shot_flag
        shot_flag = False
        self.setVisible(False)
        time.sleep(1)
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if sys.platform.startswith('win32'):
            scs = screenShot.ScreenShot(screenshot_dir, i)
            shot_flag = scs.shot_flag
        elif sys.platform.startswith('linux'):
            clib = QApplication.clipboard()
            clib.clear()
            pyautogui.hotkey('shift', 'ctrl', 'prtsc')
            while True:
                if clib.mimeData().hasImage():
                    clib.image().save(screenshot_dir + i + ".jpg", "jpg")
                    shot_flag = True
        if shot_flag:
            self.edit_tab.currentWidget().edit.insertPlainText(
                "assert_equal(Template(r\"" + screenshot_dir + i + ".jpg\"), \"预测值\", \"请填写测试点\")")
            self.setVisible(True)
            self.edit_tab.currentWidget().edit.setFocus()
            pyautogui.press('enter')
            shot_flag = False

    def assert_exist(self):
        global shot_flag
        shot_flag = False
        self.setVisible(False)
        time.sleep(1)
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if sys.platform.startswith('win32'):
            scs = screenShot.ScreenShot(screenshot_dir, i)
            shot_flag = scs.shot_flag
        elif sys.platform.startswith('linux'):
            clib = QApplication.clipboard()
            clib.clear()
            pyautogui.hotkey('shift', 'ctrl', 'prtsc')
            while True:
                if clib.mimeData().hasImage():
                    clib.image().save(screenshot_dir + i + ".jpg", "jpg")
                    shot_flag = True
        if shot_flag:
            self.edit_tab.currentWidget().edit.insertPlainText(
                "assert_exists(Template(r\"" + screenshot_dir + i + ".jpg\"), \"请填写测试点\")")
            self.setVisible(True)
            self.edit_tab.currentWidget().edit.setFocus()
            pyautogui.press('enter')
            shot_flag = False

    def assert_file_exist(self):
        exist_path_information = QFileDialog.getSaveFileName(self, '判断是否存在文件', '.')
        if exist_path_information[0]:
            file = exist_path_information[0]
            self.edit_tab.currentWidget().edit.insertPlainText("assert_file_exist(\"" + file + "\")")

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
                        "assert_word_exist(\"" + file_value[0] + "\"," + str(row_value[0]) + ",\"" + compare_v + "\")")
                    self.edit_tab.currentWidget().edit.setFocus()
                    pyautogui.press('enter')
