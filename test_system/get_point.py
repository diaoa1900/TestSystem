import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QColor, QPen, QPainter
from PyQt5.QtWidgets import QWidget, QApplication


class Point(QWidget):

    def __init__(self, cx):
        QWidget.__init__(self)
        self._cx = cx
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowActive | Qt.WindowFullScreen)
        self.back_pic = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        self.screen_width = self.back_pic.width()
        self.screen_height = self.back_pic.height()
        self.painter = QPainter()
        self.point1 = None
        self.point2 = None
        self.show()

    def paintEvent(self, event):
        shadow_color = QColor(0, 0, 0, 100)  # 阴影颜色设置
        self.painter.begin(self)
        self.painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine, Qt.FlatCap))  # 设置画笔
        self.painter.drawPixmap(0, 0, self.back_pic)  # 将背景图片画到窗体上
        self.painter.fillRect(self.back_pic.rect(), shadow_color)  # 画影罩效果
        self.painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.point1 = event.globalPos()
        if event.button() == Qt.RightButton:
            self.point2 = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self._cx.setVisible(True)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.point1 and self.point2:
                self._cx.edit_tab.currentWidget().edit.insertPlainText(
                    "swipe(({},{}),({},{}))\n".format(self.point1.x(), self.point1.y(), self.point2.x(), self.point2.y()))
            self._cx.setVisible(True)
            self.close()


'''if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Point()
    sys.exit(app.exec_())'''
