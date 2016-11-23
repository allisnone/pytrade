# -*- encoding: utf8 -*-

import time
import struct
import win32api
import win32gui
import ctypes
import win32clipboard

import win32con
import commctrl

GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
OpenProcess = ctypes.windll.kernel32.OpenProcess
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory


def maxFocusWindow(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.2)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)

def minWindow(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.2)

def getTableData(cols):
    content = _getContentsFromClipboard()
    lst = content.strip().split()[:-1]
    matrix = []
    for i in range(0, len(lst) // cols):
        matrix.append(lst[i * cols:(i + 1) * cols])
    return matrix[1:]


def getListViewInfo(hwnd, cols):
    """
    获取sysListView32的信息
    :param hwnd: sysListView32句柄
    :param cols: 读取的列数
    :return: sysListView32中的内容
    """
    col_info = []
    for col in range(cols):
        col_info.append(_readListViewItems(hwnd, col))
    row_info = []
    if not col_info:
        return row_info
    # 按行
    for row in range(len(col_info[0])):
        row_info.append([])
        for col in range(len(col_info)):
            if col_info[col] and row<=len(col_info[col]) and row<len(row_info):
                row_info[row].append(col_info[col][row].decode('GB2312'))
            else:
                pass
    #print('row_info=',row_info
    """
    each row comtents:
    ['000060', '中金岭南', '400', '400', '400', '0', '0', '-1305.00', '-20.86', '4952.00', '15.643', '12.380']
    [证券代码, 证券名字 ,当前持仓，股票余额，可用余额 ，买入冻结，卖出冻结，参考盈亏，盈亏比例，参考市值，参考成本价，参考市价]
    """
    return row_info

def getDictViewInfo(hwnd, cols):
    
    """
    获取sysListView32的信息
    :param hwnd: sysListView32句柄
    :param cols: 读取的列数
    :return: sysListView32中的内容,以字典形式返回
    """
    row_dict={}
    cols = 14
    row_info = getListViewInfo(hwnd, cols)
    acount_dict = {'0130010635':'36005','A732980330':'36005','A355519785':'38736','0148358729':'38736'}
    COLUMN_NAME = ['证券代码','证券名字' ,'当前持仓','股票余额','可用余额 ','买入冻结','卖出冻结','参考盈亏','盈亏比例','参考市值','参考成本价','参考市价','股东代码','交易市场']
    if row_info:
        for row in row_info:
            if len(row)!=cols:
                continue
            stock_dict = {}
            code_str = row[0]
            for i in range(1,cols):
                field_value = row[i]
                if i>=2 and i <=6:
                    field_value = int(field_value)
                elif i>=7 and i <=11:
                    field_value = float(field_value)
                else:
                    pass
                stock_dict.update({COLUMN_NAME[i]:field_value})
            if stock_dict['股东代码'] in list(acount_dict.keys()):
                stock_dict.update({'account':acount_dict[stock_dict['股东代码']]})    
            #code_str=row.pop(0)
            #print(code_str,type(code_str))
            row_dict[code_str] = stock_dict
    else:
        pass
    #print('row_dict=',row_dict)
    """
    each row comtents:
    {'000060': ['中金岭南', '400', '400', '400', '0', '0', '-1305.00', '-20.86', '4952.00', '15.643', '12.380'],}
    ['证券代码','证券名字' ,'当前持仓','股票余额','可用余额 ','买入冻结','卖出冻结','参考盈亏','盈亏比例','参考市值','参考成本价','参考市价','股东代码','交易市场','account']
    """
    return row_dict

def findTopWindow(wantedText=None, wantedClass=None):
    """
    :param wantedText: 标题名字
    :param wantedClass: 窗口类名
    :return: 返回顶层窗口的句柄
    """
    return win32gui.FindWindow(wantedClass, wantedText)


def findPopupWindow(hwnd):
    """
    :param hwnd: 父窗口句柄
    :return: 返回弹出式窗口的句柄
    """
    return win32gui.GetWindow(hwnd, win32con.GW_ENABLEDPOPUP)

def getParentWindow(child_hwnd):
    
    return win32gui.GetParent(child_hwnd)

def activeWindow(hwnd):
    #win32gui.GetWindowLong(hwnd,0)
    #win32gui.BringWindowToTop(hwnd)
    return win32gui.SetActiveWindow(hwnd)
    #return win32gui.SetForegroundWindow(hwnd)#SetActiveWindow(hwnd)

def getWindowStyle(hwnd):
    return win32gui.GetWindowLong(hwnd,win32con.WS_EX_LEFT)#WS_CHILDWINDOW)#GWL_STYLE)#GWL_HWNDPARENT)#GWL_USERDATA)#GWL_EXSTYLE)#DWL_DLGPROC)

def dumpWindow(hwnd, wantedText=None, wantedClass=None):
    """
    :param hwnd: 窗口句柄
    :param wantedText: 指定子窗口名
    :param wantedClass: 指定子窗口类名
    :return: 返回父窗口下所有子窗体的句柄
    """
    windows = []
    hwndChild = None
    while True:
        hwndChild = win32gui.FindWindowEx(hwnd, hwndChild, wantedClass, wantedText)
        if hwndChild:
            textName = win32gui.GetWindowText(hwndChild)
            className = win32gui.GetClassName(hwndChild)
            windows.append((hwndChild, textName, className))
        else:
            return windows


def findSubWindows(windows, numChildWindows):
    """
    查找窗口列表中的窗口，此窗口的子窗口数量为指定
    :param windows: 句柄列表
    :param numChildWindows: 子窗口数量
    :return:子窗口列表，包括子窗口hwnd, title, className
    """
    for window in windows:
        childHwnd, windowText, windowClass = window
        windowContent = dumpWindow(childHwnd)
        if len(windowContent) == numChildWindows:
            return windowContent


def findSubWindow(windows, wantedText=None, wantedClass=None):
    """
    查找窗口列表中，含有wantedText和wantedClass
    :param windows: 窗口列表
    :param wantedText: 窗口文本
    :param wantedClass: 窗口类名
    :return:窗口句柄
    """
    for window in windows:
        childHwnd, windowText, windowClass = window
        if windowText == wantedText and windowClass == wantedClass:
            return childHwnd


def dumpWindows(hwnd):
    """Dump all controls from a window

    Useful during development, allowing to you discover the structure of the
    contents of a window, showing the text and class of all contained controls.

    Parameters
    ----------
    hwnd
        The window handle of the top level window to dump.

    Returns
    -------
        all windows

    Usage example::

        replaceDialog = findTopWindow(wantedText='Replace')
        pprint.pprint(dumpWindow(replaceDialog))
    """
    windows = []
    win32gui.EnumChildWindows(hwnd, _windowEnumerationHandler, windows)
    return windows


def closePopupWindow(top_hwnd, wantedText=None, wantedClass=None):
    """
    关闭一个弹窗。
    :param top_hwnd: 主窗口句柄
    :param wantedText: 弹出对话框上的按钮文本
    :param wantedClass: 弹出对话框上的按钮类名
    :return: 如果有弹出式对话框，返回True，否则返回False
    """
    hwnd_popup = findPopupWindow(top_hwnd)
    print('hwnd_popup',hwnd_popup)
    if hwnd_popup:
        hwnd_control = findControl(hwnd_popup, wantedText, wantedClass)
        print('hwnd_control=',hwnd_control)
        clickButton(hwnd_control)
        return True
    return False


def closePopupWindows(top_hwnd,wantedText=None, wantedClass=None):
    """
    连续关闭多个弹出式对话框，直到没有弹窗
    :param top_hwnd: 主窗口句柄
    :return:
    """
    while closePopupWindow(top_hwnd,wantedText, wantedClass):
        time.sleep(1)


def findControl(topHwnd,
                wantedText=None,
                wantedClass=None,
                selectionFunction=None):
    """Find a control.

    You can identify a control using caption, class, a custom selection
    function, or any combination of these. (Multiple selection criteria are
    ANDed. If this isn't what's wanted, use a selection function.)

    Parameters
    ----------
    topHwnd
        The window handle of the top level window in which the
        required controls reside.
    wantedText
        Text which the required control's captions must contain.
    wantedClass
        Class to which the required control must belong.
    selectionFunction
        Control selection function. Reference to a function
        should be passed here. The function should take hwnd as
        an argument, and should return True when passed the
        hwnd of the desired control.

    Returns
    -------
    The window handle of the first control matching the
    supplied selection criteria.

    Raises
    ------
    WinGuiAutoError, when no control found.

    Usage example::

        optDialog = findTopWindow(wantedText="Options")
        okButton = findControl(optDialog,
                               wantedClass="Button",
                               wantedText="OK")
    """
    controls = findControls(topHwnd,
                            wantedText=wantedText,
                            wantedClass=wantedClass,
                           selectionFunction=selectionFunction)
    #try:
    if controls:
        print('controls[0]=',controls[0])
        return controls[0]
    else:
        raise WinGuiAutoError("No control found for topHwnd=" +
                                repr(topHwnd) +
                                ", wantedText=" +
                                repr(wantedText) +
                                ", wantedClass=" +
                                repr(wantedClass) +
                                ", selectionFunction=" +
                                repr(selectionFunction))
        return 0
    #except:
        #pass


def findControls(topHwnd,
                 wantedText=None,
                 wantedClass=None,
                 selectionFunction=None):
    """Find controls.

    You can identify controls using captions, classes, a custom selection
    function, or any combination of these. (Multiple selection criteria are
    ANDed. If this isn't what's wanted, use a selection function.)

    Parameters
    ----------
    topHwnd
        The window handle of the top level window in which the
        required controls reside.
    wantedText
        Text which the required controls' captions must contain.
    wantedClass
        Class to which the required controls must belong.
    selectionFunction
        Control selection function. Reference to a function
        should be passed here. The function should take hwnd as
        an argument, and should return True when passed the
        hwnd of a desired control.

    Returns
    -------
    The window handles of the controls matching the
    supplied selection criteria.

    Usage example::

        optDialog = findTopWindow(wantedText="Options")
        def findButtons(hwnd, windowText, windowClass):
            return windowClass == "Button"
        buttons = findControl(optDialog, wantedText="Button")
    """

    def searchChildWindows(currentHwnd):
        results = []
        childWindows = []
        try:
            win32gui.EnumChildWindows(currentHwnd,
                                      _windowEnumerationHandler,
                                      childWindows)
        except win32gui.error:
            # This seems to mean that the control *cannot* have child windows,
            # i.e. not a container.
            return
        for childHwnd, windowText, windowClass in childWindows:
            descendentMatchingHwnds = searchChildWindows(childHwnd)
            if descendentMatchingHwnds:
                results += descendentMatchingHwnds

            if wantedText and \
                    not _normaliseText(wantedText) in _normaliseText(windowText):
                continue
            if wantedClass and \
                    not windowClass == wantedClass:
                continue
            if selectionFunction and \
                    not selectionFunction(childHwnd):
                continue
            results.append(childHwnd)
        return results

    return searchChildWindows(topHwnd)


def clickButton(hwnd):
    """Simulates a single mouse click on a button

    Parameters
    ----------
    hwnd
        Window handle of the required button.

    Usage example::

        okButton = findControl(fontDialog,
                               wantedClass="Button",
                               wantedText="OK")
        clickButton(okButton)
    """
    _sendNotifyMessage(hwnd, win32con.BN_CLICKED)


def click(hwnd):
    """
    模拟鼠标左键单击
    :param hwnd: 要单击的控件、窗体句柄
    :return:
    """
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, None, None)
    time.sleep(0.2)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, None)
    time.sleep(0.2)


def clickWindow(hwnd, offset):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    print(left, top, right, bottom)
    win32api.SetCursorPos([left + offset, (bottom - top) // 2 + top])
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)

def sendKeyMsg(hwnd, key_code):
    """
    模拟按键
    :param hwnd: 窗体句柄
    :param key_code: 按键码，在win32con下，比如win32con.VK_F1
    :return:
    """
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)  # 消息键盘
    time.sleep(0.2)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)
    time.sleep(0.2)


def sendKeyEvent(key, command):
    win32api.keybd_event(key, 0, command, 0)
    time.sleep(0.2)


def clickStatic(hwnd):
    """Simulates a single mouse click on a static

    Parameters
    ----------
    hwnd
        Window handle of the required static.

    Usage example:  TODO
    """
    _sendNotifyMessage(hwnd, win32con.STN_CLICKED)


def doubleClickStatic(hwnd):
    """Simulates a double mouse click on a static

    Parameters
    ----------
    hwnd
        Window handle of the required static.

    Usage example:  TODO
    """
    _sendNotifyMessage(hwnd, win32con.STN_DBLCLK)


def getEditText(hwnd):
    bufLen = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
    print(bufLen)
    buffer = win32gui.PyMakeBuffer(bufLen)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, bufLen, buffer)
    print(buffer)

    text = str(buffer[:bufLen])
    #str = str(buffer[:-1])
    return text

def find_idxSubHandle(pHandle, winClass, index=0):
    """
    已知子窗口的窗体类名
    寻找第index号个同类型的兄弟窗口
    """
    assert type(index) == int and index >= 0
    handle = win32gui.FindWindowEx(pHandle, 0, winClass, None)
    while index > 0:
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, None)
        index -= 1
    return handle

def getWindowText(hwnd):
    """
    获取控件的标题
    """
    return win32gui.GetWindowText(hwnd)


def setEditText(hwnd, text):
    """
    设置Edit控件的文本，这个只能是单行文本
    :param hwnd: Edit控件句柄
    :param text: 要设置的文本
    :return:
    """
    win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, None, text)
    sendKeyMsg(hwnd, win32con.VK_RETURN)
    time.sleep(0.2)

def get_valid_combobo_ids(PCB_handle,CB_handle, max_id=100):
    """
    获取全部 拉菜单 ComboBox 的有效id
    :param PCB_handle: 下拉菜单父句柄
    :param CB_handle: 下来菜单句柄
    :param max_id: 最大下拉菜单序号
    :return: list
    """
    valid_combobox_id = []
    for id in range(0,max_id):
        combobox_id = get_combobox_id(PCB_handle,CB_handle,index_id=id)
        #print(id,combobox_id)
        if combobox_id==-1:
                    break
        else:
            if id==combobox_id:
                valid_combobox_id.append(id)
            else:
                pass
    return valid_combobox_id

def get_combobox_id(PCB_handle,CB_handle,index_id=0):
    return win32api.SendMessage(CB_handle, win32con.CB_SETCURSEL, index_id, 0)

def select_combobox(PCB_handle,CB_handle,index_id=1):
    """
    下拉菜单 ComboBox 选择
    :param PCB_handle: 下拉菜单父句柄
    :param CB_handle: 下来菜单句柄
    :param index_id: 下拉菜单序号
    :return:
    """
    idx = win32api.SendMessage(CB_handle, win32con.CB_SETCURSEL, index_id, 0)
    #print('idx=',idx)
    if idx == index_id:  
        time.sleep(0.1)
        win32api.SendMessage(PCB_handle, win32con.WM_COMMAND, 0x90000, CB_handle)  
        time.sleep(0.2)
        win32api.SendMessage(PCB_handle, win32con.WM_COMMAND, 0x10000, CB_handle)
        #print(CB_handle.GetDlgItemText(0xFFFF))
        time.sleep(0.2)
    else:
        print('无效下拉菜单序号: idx= %s'%index_id)
        pass
    return idx
# def setEditText(hwnd, text, append=False):
#     '''Set an edit control's text.
#
#     Parameters
#     ----------
#     hwnd
#         The edit control's hwnd.
#     text
#         The text to send to the control. This can be a single
#         string, or a sequence of strings. If the latter, each will
#         be become a a seperate line in the control.
#     append
#         Should the new text be appended to the existing text?
#         Defaults to False, meaning that any existing text will be
#         replaced. If True, the new text will be appended to the end
#         of the existing text.
#         Note that the first line of the new text will be directly
#         appended to the end of the last line of the existing text.
#         If appending lines of text, you may wish to pass in an
#         empty string as the 1st element of the 'text' argument.
#
#     Usage example::
#
#         print "Enter various bits of text."
#         setEditText(editArea, "Hello, again!")
#         time.sleep(.5)
#         setEditText(editArea, "You still there?")
#         time.sleep(.5)
#         setEditText(editArea, ["Here come", "two lines!"])
#         time.sleep(.5)
#
#         print "Add some..."
#         setEditText(editArea, ["", "And a 3rd one!"], append=True)
#         time.sleep(.5)
#     '''

# Ensure that text is a list
# try:
#     text + ''
#     text = [text]
# except TypeError:
#     pass
#
# # Set the current selection range, depending on append flag
# if append:
#     win32gui.SendMessage(hwnd,
#                          win32con.EM_SETSEL,
#                          -1,
#                          0)
# else:
#     win32gui.SendMessage(hwnd,
#                          win32con.EM_SETSEL,
#                          0,
#                          -1)
#
# # Send the text
# win32gui.SendMessage(hwnd,
#                      win32con.EM_REPLACESEL,
#                      True,
#                      os.linesep.join(text))

def _readListViewItems(hwnd, column_index=0):
    # Allocate virtual memory inside target process
    pid = ctypes.create_string_buffer(4)
    p_pid = ctypes.addressof(pid)
    GetWindowThreadProcessId(hwnd, p_pid)  # process owning the given hwnd
    hProcHnd = OpenProcess(win32con.PROCESS_ALL_ACCESS, False, struct.unpack("i", pid)[0])
    pLVI = VirtualAllocEx(hProcHnd, 0, 4096, win32con.MEM_RESERVE | win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
    pBuffer = VirtualAllocEx(hProcHnd, 0, 4096, win32con.MEM_RESERVE | win32con.MEM_COMMIT, win32con.PAGE_READWRITE)

    # Prepare an LVITEM record and write it to target process memory
    lvitem_str = struct.pack('iiiiiiiii', *[0, 0, column_index, 0, 0, pBuffer, 4096, 0, 0])
    lvitem_buffer = ctypes.create_string_buffer(lvitem_str)
    copied = ctypes.create_string_buffer(4)
    p_copied = ctypes.addressof(copied)
    WriteProcessMemory(hProcHnd, pLVI, ctypes.addressof(lvitem_buffer), ctypes.sizeof(lvitem_buffer), p_copied)

    # iterate items in the SysListView32 control
    num_items = win32gui.SendMessage(hwnd, commctrl.LVM_GETITEMCOUNT)
    item_texts = []
    for item_index in range(num_items):
        win32gui.SendMessage(hwnd, commctrl.LVM_GETITEMTEXT, item_index, pLVI)
        target_buff = ctypes.create_string_buffer(4096)
        ReadProcessMemory(hProcHnd, pBuffer, ctypes.addressof(target_buff), 4096, p_copied)
        item_texts.append(target_buff.value)

    VirtualFreeEx(hProcHnd, pBuffer, 0, win32con.MEM_RELEASE)
    VirtualFreeEx(hProcHnd, pLVI, 0, win32con.MEM_RELEASE)
    win32api.CloseHandle(hProcHnd)
    return item_texts


def _getContentsFromClipboard():
    win32clipboard.OpenClipboard()
    content = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return content


def _windowEnumerationHandler(hwnd, resultList):
    """Pass to win32gui.EnumWindows() to generate list of window handle,
    window text, window class tuples."""
    resultList.append((hwnd,
                       win32gui.GetWindowText(hwnd),
                       win32gui.GetClassName(hwnd)))


def _buildWinLong(high, low):
    """Build a windows long parameter from high and low words.
    See http://support.microsoft.com/support/kb/articles/q189/1/70.asp
    """
    # return ((high << 16) | low)
    return int(struct.unpack('>L',
                             struct.pack('>2H',
                                         high,
                                         low))[0])


def _sendNotifyMessage(hwnd, nofifyMessage):
    """Send a notify message to a control."""
    win32gui.SendMessage(win32gui.GetParent(hwnd),
                         win32con.WM_COMMAND,
                         _buildWinLong(nofifyMessage,
                                       win32api.GetWindowLong(hwnd,
                                                              win32con.GWL_ID)),
                         hwnd)


def _normaliseText(controlText):
    """Remove '&' characters, and lower case.
    Useful for matching control text."""
    return controlText.lower().replace('&', '')


class Bunch(object):
    """See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308"""

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in list(self.__dict__.items())]
        return '\n'.join(state)


class WinGuiAutoError(Exception):
    pass
