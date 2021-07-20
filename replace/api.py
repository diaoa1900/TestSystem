# -*- coding: utf-8 -*-
"""
This module contains the Airtest Core APIs.
"""
import os
import time
import socket
import cv2
import pytesseract
from six.moves.urllib.parse import parse_qsl, urlparse
from airtest.core.cv import Template, loop_find, try_log_screen, loop_find_vanish
from airtest.core.error import TargetNotFoundError
from airtest.core.settings import Settings as ST
from airtest.utils.compat import script_log_dir
from airtest.core.helper import (G, delay_after_operation, import_device_cls,
                                 logwrap, set_logdir)
import Levenshtein
from PIL import ImageGrab
import numpy as np
from imutils import contours
import imutils

"""
Device Setup APIs
"""


def init_device(platform="Android", uuid=None, **kwargs):
    """
    Initialize device if not yet, and set as current device.

    :param platform: Android, IOS or Windows
    :param uuid: uuid for target device, e.g. serialno for Android, handle for Windows, uuid for iOS
    :param kwargs: Optional platform specific keyword args, e.g. `cap_method=JAVACAP` for Android
    :return: device instance
    :Example:

        >>> init_device(platform="Android",uuid="SJE5T17B17", cap_method="JAVACAP")
        >>> init_device(platform="Windows",uuid="123456")
    """
    cls = import_device_cls(platform)
    dev = cls(uuid, **kwargs)
    # Add device instance in G and set as current device.
    G.add_device(dev)
    return dev


def connect_device(uri):
    """
    Initialize device with uri, and set as current device.

    :param uri: an URI where to connect to device, e.g. `android://adbhost:adbport/serialno?param=value&param2=value2`
    :return: device instance
    :Example:

        >>> connect_device("Android:///")  # local adb device using default params
        >>> # local device with serial number SJE5T17B17 and custom params
        >>> connect_device("Android:///SJE5T17B17?cap_method=javacap&touch_method=adb")
        >>> # remote device using custom params Android://adbhost:adbport/serialno
        >>> connect_device("Android://127.0.0.1:5037/10.254.60.1:5555")
        >>> connect_device("Windows:///")  # connect to the desktop
        >>> connect_device("Windows:///123456")  # Connect to the window with handle 123456
        >>> connect_device("iOS:///127.0.0.1:8100")  # iOS device

    """
    d = urlparse(uri)
    platform = d.scheme
    host = d.netloc
    uuid = d.path.lstrip("/")
    params = dict(parse_qsl(d.query))
    if host:
        params["host"] = host.split(":")
    dev = init_device(platform, uuid, **params)
    return dev


def device():
    """
    Return the current active device.

    :return: current device instance
    :Example:
        >>> dev = device()
        >>> dev.touch((100, 100))
    """
    return G.DEVICE


def set_current(idx):
    """
    Set current active device.

    :param idx: uuid or index of initialized device instance
    :raise IndexError: raised when device idx is not found
    :return: None
    :platforms: Android, iOS, Windows
    :Example:
        >>> # switch to the first phone currently connected
        >>> set_current(0)
        >>> # switch to the phone with serial number serialno1
        >>> set_current("serialno1")

    """

    dev_dict = {dev.uuid: dev for dev in G.DEVICE_LIST}
    if idx in dev_dict:
        current_dev = dev_dict[idx]
    elif isinstance(idx, int) and idx < len(G.DEVICE_LIST):
        current_dev = G.DEVICE_LIST[idx]
    else:
        raise IndexError("device idx not found in: %s or %s" % (
            list(dev_dict.keys()), list(range(len(G.DEVICE_LIST)))))
    G.DEVICE = current_dev


def auto_setup(basedir=None, devices=None, logdir=None, project_root=None, compress=None):
    """
    Auto setup running env and try connect android device if not device connected.

    :param basedir: basedir of script, __file__ is also acceptable.
    :param devices: connect_device uri in list.
    :param logdir: log dir for script report, default is None for no log, set to ``True`` for ``<basedir>/log``.
    :param project_root: project root dir for `using` api.
    :param compress: The compression rate of the screenshot image, integer in range [1, 99], default is 10
    :Example:
        >>> auto_setup(__file__)
        >>> auto_setup(__file__, devices=["Android://127.0.0.1:5037/SJE5T17B17"],
        ...             logdir=True, project_root=r"D:\\test_system\\logs", compress=90)
    """
    if basedir:
        if os.path.isfile(basedir):
            basedir = os.path.dirname(basedir)
        if basedir not in G.BASEDIR:
            G.BASEDIR.append(basedir)
    if devices:
        for dev in devices:
            connect_device(dev)
    if logdir:
        logdir = script_log_dir(basedir, logdir)
        set_logdir(logdir)
    if project_root:
        ST.PROJECT_ROOT = project_root
    if compress:
        ST.SNAPSHOT_QUALITY = compress


"""
Device Operations
"""


@logwrap
def shell(cmd):
    """
    Start remote shell in the target device and execute the command

    :param cmd: command to be run on device, e.g. "ls /data/local/tmp"
    :return: the output of the shell cmd
    :platforms: Android
    :Example:
        >>> # Execute commands on the current device adb shell ls
        >>> print(shell("ls"))

        >>> # Execute adb instructions for specific devices
        >>> dev = connect_device("Android:///device1")
        >>> dev.shell("ls")

        >>> # Switch to a device and execute the adb command
        >>> set_current(0)
        >>> shell("ls")
    """
    return G.DEVICE.shell(cmd)


@logwrap
def start_app(package, activity=None):
    """
    Start the target application on device

    :param package: name of the package to be started, e.g. "com.netease.my"
    :param activity: the activity to start, default is None which means the main activity
    :return: None
    :platforms: Android, iOS
    :Example:
        >>> start_app("com.netease.cloudmusic")
        >>> start_app("com.apple.mobilesafari")  # on iOS
    """
    G.DEVICE.start_app(package, activity)


@logwrap
def stop_app(package):
    """
    Stop the target application on device

    :param package: name of the package to stop, see also `start_app`
    :return: None
    :platforms: Android, iOS
    :Example:
        >>> stop_app("com.netease.cloudmusic")
    """
    G.DEVICE.stop_app(package)


@logwrap
def clear_app(package):
    """
    Clear data of the target application on device

    :param package: name of the package,  see also `start_app`
    :return: None
    :platforms: Android
    :Example:
        >>> clear_app("com.netease.cloudmusic")
    """
    G.DEVICE.clear_app(package)


@logwrap
def install(filepath, **kwargs):
    """
    Install application on device

    :param filepath: the path to file to be installed on target device
    :param kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: None
    :platforms: Android
    :Example:
        >>> install(r"D:\\demo\\test_system.apk")
        >>> # adb install -r -t D:\\demo\\test_system.apk
        >>> install(r"D:\\demo\\test_system.apk", ["-r", "-t"])
    """
    return G.DEVICE.install_app(filepath, **kwargs)


@logwrap
def uninstall(package):
    """
    Uninstall application on device

    :param package: name of the package, see also `start_app`
    :return: None
    :platforms: Android
    :Example:
        >>> uninstall("com.netease.cloudmusic")
    """
    return G.DEVICE.uninstall_app(package)


@logwrap
def snapshot(filename=None, msg="", quality=None, max_size=None):
    """
    Take the screenshot of the target device and save it to the file.

    :param filename: name of the file where to save the screenshot. If the relative path is provided, the default
                     location is ``ST.LOG_DIR``
    :param msg: short description for screenshot, it will be recorded in the report
    :param quality: The image quality, integer in range [1, 99], default is 10
    :param max_size: the maximum size of the picture, e.g 1200
    :return: absolute path of the screenshot
    :platforms: Android, iOS, Windows
    :Example:
        >>> snapshot(msg="index")
        >>> # save the screenshot to test_system.jpg
        >>> snapshot(filename="test_system.png", msg="test_system")

        The quality and size of the screenshot can be set::

        >>> # Set the screenshot quality to 30
        >>> ST.SNAPSHOT_QUALITY = 30
        >>> # Set the screenshot size not to exceed 600*600
        >>> # if not set, the default size is the original image size
        >>> ST.IMAGE_MAXSIZE = 600
        >>> # The quality of the screenshot is 30, and the size does not exceed 600*600
        >>> touch((100, 100))
        >>> # The quality of the screenshot of this sentence is 90
        >>> snapshot(filename="test_system.png", msg="test_system", quality=90)
        >>> # The quality of the screenshot is 90, and the size does not exceed 1200*1200
        >>> snapshot(filename="test2.png", msg="test_system", quality=90, max_size=1200)

    """
    if not quality:
        quality = ST.SNAPSHOT_QUALITY
    if not max_size and ST.IMAGE_MAXSIZE:
        max_size = ST.IMAGE_MAXSIZE
    if filename:
        if not os.path.isabs(filename):
            logdir = ST.LOG_DIR or "."
            filename = os.path.join(logdir, filename)
        screen = G.DEVICE.snapshot(filename, quality=quality, max_size=max_size)
        return try_log_screen(screen, quality=quality, max_size=max_size)
    else:
        return try_log_screen(quality=quality, max_size=max_size)


@logwrap
def wake():
    """
    Wake up and unlock the target device

    :return: None
    :platforms: Android
    :Example:
        >>> wake()

    .. note:: Might not work on some models
    """
    G.DEVICE.wake()


@logwrap
def home():
    """
    Return to the home screen of the target device.

    :return: None
    :platforms: Android, iOS
    :Example:
        >>> home()
    """
    G.DEVICE.home()


@logwrap
def touch(v, times=1, **kwargs):
    """
    Perform the touch action on the device screen

    :param v: target to touch, either a ``Template`` instance or absolute coordinates (x, y)
    :param times: how many touches to be performed
    :param kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: finial position to be clicked
    :platforms: Android, Windows, iOS
    :Example:
        Click absolute coordinates::

        >>> touch((100, 100))

        Click the center of the picture(Template object)::

        >>> touch(Template(r"tpl1606730579419.png", target_pos=5))

        Click 2 times::

        >>> touch((100, 100), times=2)

        Under Android and Windows platforms, you can set the click duration::

        >>> touch((100, 100), duration=2)

        Right click(Windows)::

        >>> touch((100, 100), right_click=True)

    """
    if isinstance(v, Template):
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT)
    else:
        try_log_screen()
        pos = v
    for _ in range(times):
        G.DEVICE.touch(pos, **kwargs)
        time.sleep(0.05)
    delay_after_operation()
    return pos


click = touch  # click is alias of touch


@logwrap
def double_click(v):
    """
    Perform double click

    :param v: target to touch, either a ``Template`` instance or absolute coordinates (x, y)
    :return: finial position to be clicked
    :Example:

        >>> double_click((100, 100))
        >>> double_click(Template(r"tpl1606730579419.png"))
    """
    if isinstance(v, Template):
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT)
    else:
        try_log_screen()
        pos = v
    G.DEVICE.double_click(pos)
    delay_after_operation()
    return pos


@logwrap
def right_click(v):
    """
    Perform right click
    """
    if isinstance(v, Template):
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT)
    else:
        try_log_screen()
        pos = v
    G.DEVICE.right_click(pos)
    delay_after_operation()
    return pos


@logwrap
def hover(v):
    """
    Perform mouse move and stop
    """
    if isinstance(v, Template):
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT)
    else:
        try_log_screen()
        pos = v
    G.DEVICE.hover(pos)
    delay_after_operation()
    return pos


@logwrap
def swipe(v1, v2=None, vector=None, **kwargs):
    """
    Perform the swipe action on the device screen.

    There are two ways of assigning the parameters
        * ``swipe(v1, v2=Template(...))``   # swipe from v1 to v2
        * ``swipe(v1, vector=(x, y))``      # swipe starts at v1 and moves along the vector.


    :param v1: the start point of swipe,
               either a Template instance or absolute coordinates (x, y)
    :param v2: the end point of swipe,
               either a Template instance or absolute coordinates (x, y)
    :param vector: a vector coordinates of swipe action, either absolute coordinates (x, y) or percentage of
                   screen e.g.(0.5, 0.5)
    :param **kwargs: platform specific `kwargs`, please refer to corresponding docs
    :raise Exception: general exception when not enough parameters to perform swap action have been provided
    :return: Origin position and target position
    :platforms: Android, Windows, iOS
    :Example:

        >>> swipe(Template(r"tpl1606814865574.png"), vector=[-0.0316, -0.3311])
        >>> swipe((100, 100), (200, 200))

        Custom swiping duration and number of steps(Android and iOS)::

        >>> # swiping lasts for 1 second, divided into 6 steps
        >>> swipe((100, 100), (200, 200), duration=1, steps=6)

    """
    if isinstance(v1, Template):
        pos1 = loop_find(v1, timeout=ST.FIND_TIMEOUT)
    else:
        try_log_screen()
        pos1 = v1

    if v2:
        if isinstance(v2, Template):
            pos2 = loop_find(v2, timeout=ST.FIND_TIMEOUT_TMP)
        else:
            pos2 = v2
    elif vector:
        if vector[0] <= 1 and vector[1] <= 1:
            w, h = G.DEVICE.get_current_resolution()
            vector = (int(vector[0] * w), int(vector[1] * h))
        pos2 = (pos1[0] + vector[0], pos1[1] + vector[1])
    else:
        raise Exception("no enough params for swipe")

    G.DEVICE.swipe(pos1, pos2, **kwargs)
    delay_after_operation()
    return pos1, pos2


@logwrap
def pinch(in_or_out='in', center=None, percent=0.5):
    """
    Perform the pinch action on the device screen

    :param in_or_out: pinch in or pinch out, enum in ["in", "out"]
    :param center: center of pinch action, default as None which is the center of the screen
    :param percent: percentage of the screen of pinch action, default is 0.5
    :return: None
    :platforms: Android
    :Example:

        Pinch in the center of the screen with two fingers::

        >>> pinch()

        Take (100,100) as the center and slide out with two fingers::

        >>> pinch('out', center=(100, 100))
    """
    try_log_screen()
    G.DEVICE.pinch(in_or_out=in_or_out, center=center, percent=percent)
    delay_after_operation()


@logwrap
def keyevent(keyname, **kwargs):
    """
    Perform key event on the device

    :param keyname: platform specific key name
    :param **kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: None
    :platforms: Android, Windows, iOS
    :Example:

        * ``Android``: it is equivalent to executing ``adb shell input keyevent KEYNAME`` ::

        >>> keyevent("HOME")
        >>> # The constant corresponding to the home key is 3
        >>> keyevent("3")  # same as keyevent("HOME")
        >>> keyevent("BACK")
        >>> keyevent("KEYCODE_DEL")

        .. seealso::

           Module :py:mod:`airtest.core.android.adb.ADB.keyevent`
              Equivalent to calling the ``android.adb.keyevent()``

           `Android Keyevent <https://developer.android.com/reference/android/view/KeyEvent#constants_1>`_
              Documentation for more ``Android.KeyEvent``

        * ``Windows``: Use ``pywinauto.keyboard`` module for key input::

        >>> keyevent("{DEL}")
        >>> keyevent("%{F4}")  # close an active window with Alt+F4

        .. seealso::

            Module :py:mod:`airtest.core.win.win.Windows.keyevent`

            `pywinauto.keyboard <https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html>`_
                Documentation for ``pywinauto.keyboard``

        * ``iOS``: Only supports home/volumeUp/volumeDown::

        >>> keyevent("HOME")
        >>> keyevent("volumeUp")

    """
    G.DEVICE.keyevent(keyname, **kwargs)
    delay_after_operation()


@logwrap
def text(text, enter=True, **kwargs):
    """
    Input text on the target device. Text input widget must be active first.

    :param text: text to input, unicode is supported
    :param enter: input `Enter` keyevent after text input, default is True
    :return: None
    :platforms: Android, Windows, iOS
    :Example:

        >>> text("test_system")
        >>> text("test_system", enter=False)

        On Android, sometimes you need to click the search button after typing::

        >>> text("test_system", search=True)

        .. seealso::

            Module :py:mod:`airtest.core.android.ime.YosemiteIme.code`

            If you want to enter other keys on the keyboard, you can use the interface::

                >>> text("test_system")
                >>> device().yosemite_ime.code("3")  # 3 = IME_ACTION_SEARCH

            Ref: `Editor Action Code <http://developer.android.com/reference/android/view/inputmethod/EditorInfo.html>`_

    """
    G.DEVICE.text(text, enter=enter, **kwargs)
    delay_after_operation()


@logwrap
def sleep(secs=1.0):
    """
    Set the sleep interval. It will be recorded in the report

    :param secs: seconds to sleep
    :return: None
    :platforms: Android, Windows, iOS
    :Example:

        >>> sleep(1)
    """
    time.sleep(secs)


@logwrap
def wait(v, timeout=None, interval=0.5, intervalfunc=None):
    """
    Wait to match the Template on the device screen

    :param v: target object to wait for, Template instance
    :param timeout: time interval to wait for the match, default is None which is ``ST.FIND_TIMEOUT``
    :param interval: time interval in seconds to attempt to find a match
    :param intervalfunc: called after each unsuccessful attempt to find the corresponding match
    :raise TargetNotFoundError: raised if target is not found after the time limit expired
    :return: coordinates of the matched target
    :platforms: Android, Windows, iOS
    :Example:

        >>> wait(Template(r"tpl1606821804906.png"))  # timeout after ST.FIND_TIMEOUT
        >>> # find Template every 3 seconds, timeout after 120 seconds
        >>> wait(Template(r"tpl1606821804906.png"), timeout=120, interval=3)

        You can specify a callback function every time the search target fails::

        >>> def notfound():
        >>>     print("No target found")
        >>> wait(Template(r"tpl1607510661400.png"), intervalfunc=notfound)

    """
    timeout = timeout or ST.FIND_TIMEOUT
    pos = loop_find(v, timeout=timeout, interval=interval, intervalfunc=intervalfunc)
    return pos


@logwrap
def waitVanish(v, timeout=None, interval=0.5, intervalfunc=None):
    timeout = timeout or ST.FIND_TIMEOUT
    pos = loop_find(v, timeout=timeout, interval=interval, intervalfunc=intervalfunc)
    vanish_pos = loop_find_vanish(v, timeout=timeout, interval=interval, intervalfunc=intervalfunc)
    return pos


@logwrap
def exists(v):
    """
    Check whether given target exists on device screen

    :param v: target to be checked
    :return: False if target is not found, otherwise returns the coordinates of the target
    :platforms: Android, Windows, iOS
    :Example:

        >>> if exists(Template(r"tpl1606822430589.png")):
        >>>     touch(Template(r"tpl1606822430589.png"))

        Since ``exists()`` will return the coordinates, we can directly click on this return value to reduce one image search::

        >>> pos = exists(Template(r"tpl1606822430589.png"))
        >>> if pos:
        >>>     touch(pos)

    """
    try:
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT_TMP)
    except TargetNotFoundError:
        return False
    else:
        return pos


@logwrap
def find_all(v):
    """
    Find all occurrences of the target on the device screen and return their coordinates

    :param v: target to find
    :return: list of results, [{'result': (x, y),
                                'rectangle': ( (left_top, left_bottom, right_bottom, right_top) ),
                                'confidence': 0.9},
                                ...]
    :platforms: Android, Windows, iOS
    :Example:

        >>> find_all(Template(r"tpl1607511235111.png"))
        [{'result': (218, 468), 'rectangle': ((149, 440), (149, 496), (288, 496), (288, 440)),
        'confidence': 0.9999996423721313}]

    """
    screen = G.DEVICE.snapshot(quality=ST.SNAPSHOT_QUALITY)
    return v.match_all_in(screen)


"""
Assertions
"""


@logwrap
def assert_exists(v, msg="", timeout=ST.FIND_TIMEOUT):
    """
    Assert target exists on device screen

    :param v: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: coordinates of the target
    :platforms: Android, Windows, iOS
    :Example:

        >>> assert_exists(Template(r"tpl1607324047907.png"), "assert exists")

    """
    try:
        pos = loop_find(v, timeout=timeout, threshold=ST.THRESHOLD_STRICT or v.threshold)
        return pos
    except TargetNotFoundError:
        raise TargetNotFoundError("%s does not exist in screen, message: %s" % (v, msg))


@logwrap
def assert_not_exists(v, msg=""):
    """
    Assert target does not exist on device screen

    :param v: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None.
    :platforms: Android, Windows, iOS
    :Example:

        >>> assert_not_exists(Template(r"tpl1607324047907.png"), "assert not exists")
    """
    try:
        pos = loop_find(v, timeout=ST.FIND_TIMEOUT_TMP)
        raise AssertionError("%s exists unexpectedly at pos: %s, message: %s" % (v, pos, msg))
    except TargetNotFoundError:
        pass


@logwrap
def assert_equal(first, second, msg=""):
    """
    Assert two values are equal

    :param first: first value
    :param second: second value
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None
    :platforms: Android, Windows, iOS
    :Example:

        >>> assert_equal(1, 1, msg="assert 1==1")
    """
    if first != second:
        raise AssertionError("%s and %s are not equal, message: %s" % (first, second, msg))


@logwrap
def assert_not_equal(first, second, msg=""):
    """
    Assert two values are not equal

    :param first: first value
    :param second: second value
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion
    :return: None
    :platforms: Android, Windows, iOS
    :Example:

        >>> assert_not_equal(1, 2, msg="assert 1!=2")
    """
    if first == second:
        raise AssertionError("%s and %s are equal, message: %s" % (first, second, msg))


@logwrap
def assert_file_exist(file, flag=None):
    if flag is None:
        if not os.path.exists(file):
            raise TargetNotFoundError("%s is not exist" % file)
    else:
        index = file.rindex('/')
        start = file[:index]
        end = file[index+1:]
        for fi in os.listdir(start):
            if end in fi:
                index = -1
        if index != -1:
            raise TargetNotFoundError("%s is not exist" % file)




@logwrap
def assert_word_exist(file, row, words_given):
    f = open(file, 'rb')
    offset = -50
    file_size = os.stat(file).st_size
    assert_word_exist_flag = False
    beginning_of_file_flag = False
    while True:
        if -offset > file_size:
            f.seek(0, 0)
            beginning_of_file_flag = True
        else:
            f.seek(offset, 2)
        lines = f.readlines()
        if len(lines) >= row + 1 or (len(lines) == row and beginning_of_file_flag):
            if row > 1:
                words_in_file = lines[-row:]
                words_in_file_co = ''
                for j in range(len(words_in_file)):
                    words_in_file_co += str(words_in_file[j], encoding='gbk')
                words_in_file_co = words_in_file_co.replace('\r\n', '')
                if words_given in words_in_file_co:
                    assert_word_exist_flag = True
            else:
                words_in_file = lines[-1]
                words_in_file = str(words_in_file, encoding='gbk')
                if words_given in words_in_file:
                    assert_word_exist_flag = True
            break
        else:
            offset *= 2
    if assert_word_exist_flag is False:
        raise TargetNotFoundError("{} is not on the last {} lines of {}".format(words_given, row, file))


def ocr(v, language=None):
    if language is None:
        return pytesseract.image_to_string(cv2.threshold(cv2.imread(str(v)[9:-1], cv2.IMREAD_GRAYSCALE), 140, 255, cv2.THRESH_BINARY_INV)[1]).strip()
    else:
        img = cv2.threshold(cv2.imread(str(v)[9:-1], cv2.IMREAD_GRAYSCALE), 140, 255, cv2.THRESH_BINARY_INV)[1]
        img = cv2.resize(img, None, fx=8, fy=8)
        return pytesseract.image_to_string(img, lang='chi_sim').strip()


def assert_lcd_true(start_x, start_y, end_x, end_y, pre, flag=1, val=1):
    img = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
    # 定义每一个数字对应的字段
    DIGITS_LOOKUP = {
        (1, 1, 1, 0, 1, 1, 1): 0,
        (0, 0, 1, 0, 0, 1, 0): 1,
        (1, 0, 1, 1, 1, 0, 1): 2,
        (1, 0, 1, 1, 0, 1, 1): 3,
        (0, 1, 1, 1, 0, 1, 0): 4,
        (1, 1, 0, 1, 0, 1, 1): 5,
        (1, 1, 0, 1, 1, 1, 1): 6,
        (1, 0, 1, 0, 0, 1, 0): 7,
        (1, 1, 1, 1, 1, 1, 1): 8,
        (1, 1, 1, 1, 0, 1, 1): 9,
        (0, 0, 0, 0, 0, 0, 0): ''
    }
    # 将输入转换为灰度图片
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    # 使用阈值进行二值化
    thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
    kernel = (3, 3)
    if end_x-start_x < 150:
        kernel = (1, 1)
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones(kernel, np.uint8))
    # 在阈值图像中查找轮廓，然后初始化数字轮廓列表
    cnts = cv2.findContours(close.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    digitCnts = []

    w_sum = 0.
    h_sum = 0.
    # 循环遍历所有的候选区域
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        w_sum += w
        h_sum += h
        digitCnts.append(c)
    # 从左到右对这些轮廓进行排序
    w_ave = w_sum / len(digitCnts)
    h_ave = h_sum / len(digitCnts)
    digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
    digits = ""
    dc = cv2.drawContours(np.array(img).copy(), digitCnts, -1, (0, 0, 255), 2)
    # 循环处理每一个数字
    i = 0
    for c in digitCnts:
        # 获取ROI区域
        (x, y, w, h) = cv2.boundingRect(c)
        roi = thresh[y:y + h, x:x + w]
        if h / w > 3:
            digits += '1'
            continue
        elif w - h > 1 and w - h < 40:
            digits += '-'
            continue
        elif abs(w - h) <= 1:
            digits += '.'
            continue
        # 分别计算每一段的宽度和高度
        (roiH, roiW) = roi.shape
        (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
        dHC = int(roiH * 0.05)

        # 定义一个7段数码管的集合
        segments = [
            ((0, 0), (w, dH)),  # 上
            ((0, 0), (dW, h // 2)),  # 左上
            ((w - dW, 0), (w, h // 2)),  # 右上
            ((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # 中间
            ((0, h // 2), (dW, h)),  # 左下
            ((w - dW, h // 2), (w, h)),  # 右下
            ((0, h - dH), (w, h))  # 下
        ]
        on = [0] * len(segments)

        # 循环遍历数码管中的每一段
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):  # 检测分割后的ROI区域，并统计分割图中的阈值像素点
            segROI = roi[yA:yB, xA:xB]
            total = cv2.countNonZero(segROI)
            area = (xB - xA) * (yB - yA)

            # 如果非零区域的个数大于整个区域的一半，则认为该段是亮的
            if  area == 0:
                continue
            if total / float(area) > 0.5:
                on[i] = 1
            if total / float(area) == 1.0:
                on[i] = 0

        # 进行数字查询并显示结果
        digit = DIGITS_LOOKUP[tuple(on)]
        digits += str(digit)
    if digits == pre:
        return
    elif digits in pre and flag == 2:
        return
    elif Levenshtein.distance(pre, digits) < val and flag == 3:
        return
    raise TargetNotFoundError("The result of LCD recognization is{}, not {}".format(digits, pre))


def assert_ocr_true(start_x, start_y, end_x, end_y, pre, flag=1, val=1, language=None):
    img = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
    real = ""
    if language is None:
        real = pytesseract.image_to_string(cv2.threshold(cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY), 140, 255, cv2.THRESH_BINARY_INV)[1]).strip()
    else:
        img = cv2.threshold(cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY), 140, 255, cv2.THRESH_BINARY_INV)[1]
        img = cv2.resize(img, None, fx=8, fy=8)
        real = pytesseract.image_to_string(img, lang='chi_sim').strip()
    if real == pre:
        return
    elif pre in real and flag == 2:
        return
    elif Levenshtein.distance(pre, real) < val and flag == 3:
        return
    raise TargetNotFoundError("The OCR result is{}, not {}".format(real, pre))


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('127.0.0.1', 9948))


@logwrap
def connect_server(host, host_port):
    port = int(host_port)
    sock.connect((host, port))


@logwrap
def new_device(file_name):
    f = open(file_name, 'rb')
    str = f.read()
    sock.send(str)
    f.close()


@logwrap
def add_key(file_name):
    f = open(file_name, 'rb')
    str = f.read()
    # 这块要修改
    sock.send(str)
    f.close()


@logwrap
def add_data(file_name):
    f = open(file_name, 'rb')
    str = f.read()
    sock.send(str)
    f.close()


@logwrap
def delete_device(file_name):
    f = open(file_name, 'rb')
    str = f.read()
    sock.send(str)
    f.close()


@logwrap
def delete_key(file_name):
    f = open(file_name, 'rb')
    str = f.read()
    sock.send(str)
    f.close()


@logwrap
def assert_client_exist(order):
    data = sock.recv(1024)
    message = data.decode()
    client_message = data
    if len(message) == 18:
        client_message = data[12:18]
        sock.send(client_message)
    else:
        client_not_message = data
        sock.send(client_not_message)
    if client_message.decode() == "CCCCCC":
        pass
    else:
        raise TargetNotFoundError(order)


@logwrap
def close_socket():
    sock.close()
