import logging
import subprocess
import time
import keyboard
import pyautogui
from PIL import ImageGrab
from PyQt5.QtWidgets import QFileDialog
import IDE


class Functions(IDE.MenuTools):

    def show_result(self):
        pass

    def screenshot(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\")")
        self.setVisible(True)

    def insert_picture(self):
        picture_path_information = QFileDialog.getOpenFileName(self, '请选择图片', '.', '*.jpg *.png *.jpeg')
        picture_path = picture_path_information[0]
        if picture_path:
            self.edit_tab.currentWidget().edit.insertPlainText("Template(r\""+picture_path+"\")")

    def part_run(self):
        pass

    def run(self):
        try:
            self.console_text.clear()
            sbp = subprocess.Popen("python " + self.edit_tab.currentWidget().edit_name,
                                   cwd="D:/work/workspaceTest/TestSystem/test", stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            self.console_text.insertPlainText(sbp.stdout.read().decode())
            sbp.stdout.close()
            self.console_text.insertPlainText(sbp.stderr.read().decode())
            sbp.stderr.close()
            '''logger = logging.getLogger("airtest")
            logger.setLevel(logging.DEBUG)
            sh = logging.FileHandler()
            logger.addHandler(sh)'''
        except Exception as e:
            print(e)
        '''with open(self.edit_tab.currentWidget().path, 'r', encoding='utf-8') as f:
            exec(f.read())'''

    def stop(self):
        subprocess.exit()

    def wait(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "wait(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "waitVanish(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def exist(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "exist(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "click(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        '''pyautogui.hotkey('alt', 'tab')'''
        # 不能insert后自动换行
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "double_click(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "rightClick(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "swipe(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def cover(self):
        pass

    def keyevent(self):
        # 模拟按下键盘上某个键
        pass

    def snapshot(self):
        # 截取当前屏幕全图
        pass

    def text(self):
        # 输入文本，文本框需要处于激活状态
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "text(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    '''def paste(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "paste(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def p_text(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "p_text(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')

    def p_paste(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "p_paste(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')'''

    def assert_same(self):
        self.setVisible(False)
        time.sleep(1)
        pyautogui.press('f1')
        keyboard.wait('enter')
        time.sleep(1)
        img = ImageGrab.grabclipboard()
        i = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "assert_same(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
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
        img.save("D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg")
        self.edit_tab.currentWidget().edit.insertPlainText(
            "assert_exist(Template(r\"D:/work/workspaceTest/TestSystem/脚本的截图/" + i + ".jpg\"))")
        self.setVisible(True)
        self.edit_tab.currentWidget().edit.setFocus()
        pyautogui.press('enter')
