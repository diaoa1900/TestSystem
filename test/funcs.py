import logging
import subprocess
import time
import keyboard
import pyautogui
from PIL import ImageGrab
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from airtest.core.helper import G
from threading import Thread
from test import IDE

screenshot_dir = "D:/screenshotFolder/"


class Functions(IDE.MenuTools):

    def screenshot(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "Template(r\"" + screenshot_dir + i + ".jpg\")")
        self.setVisible(True)

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
                                       stderr=subprocess.PIPE)
                self.console_text.insertPlainText(sbp.stdout.read().decode())
                self.console_text.insertPlainText(sbp.stderr.read().decode())
                self.console_text.moveCursor(QTextCursor.End)
                sbp.stdout.close()
                sbp.stderr.close()

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
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "wait(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def waitVanish(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "waitVanish(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def exists(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "exists(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def click(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "click(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def double_click(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "double_click(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def rightClick(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "rightClick(Template(r\"" + screenshot_dir + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def swipe(self):
        self.setVisible(False)
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
        pyautogui.press('enter')

    def cover(self):
        # 鼠标悬浮在该图片位置上
        pass

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
        pass

    def text(self):
        # 输入文本，文本框需要处于激活状态
        keyevent_value = QInputDialog.getText(self, '文字输入', '内容')
        if keyevent_value[1] is True:
            self.edit_tab.currentWidget().edit.insertPlainText("text(\"" + keyevent_value[0] + "\")")
            self.edit_tab.currentWidget().edit.setFocus()
            pyautogui.press('enter')

    def assert_equal(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "assert_equal(Template(r\"" + screenshot_dir + i + ".jpg\"), \"预测值\", \"请填写测试点\")")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def assert_exist(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save(screenshot_dir + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "assert_exists(Template(r\"" + screenshot_dir + i + ".jpg\"), \"请填写测试点\")")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')
