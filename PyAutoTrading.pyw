# -*- encoding: utf8 -*-
# QQ群： 486224275
__author__ = '人在江湖'

try:
    #Python3.0
    import tkinter.messagebox
    from tkinter import *
    from tkinter.ttk import *
except ImportError:
    #Python2.7
    import Tkinter
    import tkMessageBox 
    from Tkinter import *
    from ttk import *

#import tkinter.messagebox
#from tkinter import *
#from tkinter.ttk import *
import datetime
import threading
import pickle
import configparser
import time
import tushare as ts
from winguiauto import *


is_start = False
is_monitor = True
set_stock_info = []
order_msg = []
actual_stock_info = []
GUI_ROWS=10
is_ordered = [1] * GUI_ROWS  # 1：未下单  0：已下单
running_money = 0
position = []


def getConfigData():
    '''
    读取配置文件参数
    :return:双向委托界面下，控件的数量
    '''
    cp = configparser.ConfigParser()
    cp.read('pyautotrading.ini')
    numChildWindows = cp.getint('tradeVersion', 'numChildWindows')
    return numChildWindows


class Trade:
    def __init__(self, hwnd):

        self.hwnd = hwnd
        print hwnd
        windows = dumpWindows(self.hwnd)
        print windows
        temp_hwnd = 0
        for window in windows:
            childHwnd, windowText, windowClass = window
            if windowClass == 'AfxMDIFrame42':
                temp_hwnd = childHwnd
                print temp_hwnd
                break
        temp_hwnds = dumpWindow(temp_hwnd)
        print 'temp_hwnds1=',temp_hwnds
        temp_hwnds = dumpWindow(temp_hwnds[1][0])
        print 'temp_hwnds2=',temp_hwnds
        self.menu_hwnd = dumpWindow(temp_hwnds[0][0])[0]
        print self.menu_hwnd 
        self.buy_hwnds = dumpWindow(temp_hwnds[4][0])
        self.sell_hwnds = dumpWindow(temp_hwnds[5][0])
        self.withdrawal_hwnds = dumpWindow(temp_hwnds[6][0])
        self.deal_hwnds = dumpWindow(temp_hwnds[7][0])
        self.position_hwnds = dumpWindow(temp_hwnds[8][0])
        self.button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}

    def _buy(self, code, stop_price, quantity):
        self._clickMenuButton(self.button['buy'])
        setEditText(self.buy_hwnds[2][0], code)
        setEditText(self.buy_hwnds[3][0], stop_price)
        setEditText(self.buy_hwnds[7][0], quantity)
        time.sleep(0.3)
        click(self.buy_hwnds[10][0])
        time.sleep(0.3)

    def _sell(self, code, stop_price, quantity):
        self._clickMenuButton(self.button['sell'])
        setEditText(self.sell_hwnds[2][0], code)
        setEditText(self.sell_hwnds[3][0], stop_price)
        setEditText(self.sell_hwnds[7][0], quantity)
        time.sleep(0.3)
        click(self.sell_hwnds[9][0])
        time.sleep(0.3)

    def order(self, code, prices, quantity, direction):
        if direction == 'B':
            self._buy(code, prices[0], quantity)
        if direction == 'S':
            self._sell(code, prices[1], quantity)
        closePopupWindows(self.hwnd)

    def _clickMenuButton(self, leftDistance):
        left, top, right, bottom = win32gui.GetWindowRect(self.menu_hwnd[0])
        win32api.SetCursorPos([left + leftDistance, (bottom - top) // 2 + top])
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)

    def refresh(self):
        '''
        点击刷新按钮
        :return:
        '''
        self._clickMenuButton(self.button['refresh'])

    def _getListViewInfo(self, hwnd):
        '''
        获取ListView的信息
        :param hwnd: ListView句柄
        :return:
        '''
        col_info = []
        for col in range(10):
            col_info.append(readListViewItems(hwnd, col))
        row_info = []

        # 按行
        for row in range(len(col_info[0])):
            row_info.append([])
            for col in range(len(col_info)):
                row_info[row].append(col_info[col][row].decode('GB2312'))
        return row_info

    def getMoneyInfo(self):
        '''
        :param sub_hwnds: 持仓句柄列表
        :return:可以资金，参考市值， 资产， 盈亏
        '''
        self._clickMenuButton(self.button['position'])
        text = self.position_hwnds[1][1].strip()
        text = text.replace(':', ' ')
        text = text.split(' ')
        return float(text[4]), float(text[10]), float(text[13]), float(text[16])

    def getPositionInfo(self):
        '''获取持仓股票信息
        '''
        self._clickMenuButton(self.button['position'])
        return self._getListViewInfo(self.position_hwnds[27][0])

    def getWithdrawalInfo(self):
        '''获取撤单信息
        '''
        self._clickMenuButton(self.button['withdrawal'])
        return self._getListViewInfo(self.withdrawal_hwnds[27][0])

    def getDealInfo(self):
        '''获取成交信息
        '''
        self._clickMenuButton(self.button['deal'])
        return self._getListViewInfo(self.deal_hwnds[27][0])


def pickCodeFromItems(items_info):
    '''
    提取股票代码
    :param items_info: UI下各项输入信息
    :return:股票代码列表
    '''
    stock_codes = []
    for item in items_info:
        stock_codes.append(item[0])
    return stock_codes


def getStockData(items_info):
    '''
    获取股票实时数据
    :param items_info:UI下各项输入信息
    :return:股票实时数据
    '''
    code_name_price = []
    stock_codes = pickCodeFromItems(items_info)
    try:
        df = ts.get_realtime_quotes(stock_codes)
        df_len = len(df)
        for stock_code in stock_codes:
            is_found = False
            for i in range(df_len):
                actual_code = df['code'][i]
                if stock_code == actual_code:
                    actual_name = df['name'][i]
                    pre_close = float(df['pre_close'][i])
                    if 'ST' in actual_name:
                        highest = str(round(pre_close * 1.05, 2))
                        lowest = str(round(pre_close * 0.95, 2))
                        code_name_price.append((actual_code, actual_name, df['price'][i], (highest, lowest)))
                    else:
                        highest = str(round(pre_close * 1.1, 2))
                        lowest = str(round(pre_close * 0.9, 2))
                        code_name_price.append((actual_code, actual_name, df['price'][i], (highest, lowest)))
                    is_found = True
                    break
            if is_found is False:
                code_name_price.append(('', '', '', ('', '')))
    except:
        code_name_price = [('', '', '', ('', ''))] * GUI_ROWS  # 网络不行，返回空
    return code_name_price


def monitor():
    '''
    实时监控函数
    :return:
    '''
    global actual_stock_info, order_msg, is_ordered, set_stock_info, position
    count = 0

    top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
    if top_hwnd == 0:
        #tkinter.messagebox.showerror('错误', '请先打开交易软件，再运行本软件')
        tkMessageBox.showerror('错误', '请先打开交易软件，再运行本软件')
    else:
        trade = Trade(top_hwnd)

    while is_monitor and top_hwnd:
        if count % 200 == 0:
            # 点击刷新按钮
            trade.refresh()

        time.sleep(3)
        count += 1
        if is_start:
            actual_stock_info = getStockData(set_stock_info)
            for row, (actual_code, actual_name, actual_price, stop_prices) in enumerate(actual_stock_info):
                if is_start and actual_code and is_ordered[row] == 1 \
                        and set_stock_info[row][1] and set_stock_info[row][2] > 0 \
                        and set_stock_info[row][3] and set_stock_info[row][4] \
                        and datetime.datetime.now().time() > set_stock_info[row][5]:
                    if is_start and set_stock_info[row][1] == '>' and float(actual_price) > set_stock_info[row][2]:
                        dt = datetime.datetime.now()
                        trade.order(actual_code, stop_prices,
                              set_stock_info[row][4], set_stock_info[row][3])
                        closePopupWindows(top_hwnd)
                        order_msg.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stock_info[row][3],
                             actual_price, set_stock_info[row][4], '已下单'))
                        time.sleep(0.3)
                        is_ordered[row] = 0

                    if is_start and set_stock_info[row][1] == '<' and float(actual_price) < set_stock_info[row][2]:
                        dt = datetime.datetime.now()
                        trade.order(actual_code, stop_prices,
                              set_stock_info[row][4], set_stock_info[row][3])
                        closePopupWindows(top_hwnd)
                        order_msg.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stock_info[row][3],
                             actual_price, set_stock_info[row][4], '已下单'))
                        time.sleep(0.3)
                        is_ordered[row] = 0


class StockGui:
    def __init__(self):
        self.window = Tk()
        self.window.title("自动化股票交易")
        self.window.resizable(0, 0)

        frame1 = Frame(self.window)
        frame1.pack(padx=10, pady=10)

        Label(frame1, text="股票代码", width=8, justify=CENTER).grid(
            row=1, column=1, padx=5, pady=5)
        Label(frame1, text="股票名称", width=8, justify=CENTER).grid(
            row=1, column=2, padx=5, pady=5)
        Label(frame1, text="当前价格", width=8, justify=CENTER).grid(
            row=1, column=3, padx=5, pady=5)
        Label(frame1, text="关系", width=4, justify=CENTER).grid(
            row=1, column=4, padx=5, pady=5)
        Label(frame1, text="价格", width=8, justify=CENTER).grid(
            row=1, column=5, padx=5, pady=5)
        Label(frame1, text="方向", width=4, justify=CENTER).grid(
            row=1, column=6, padx=5, pady=5)
        Label(frame1, text="数量", width=8, justify=CENTER).grid(
            row=1, column=7, padx=5, pady=5)
        Label(frame1, text="时间可选", width=8, justify=CENTER).grid(
            row=1, column=8, padx=5, pady=5)
        Label(frame1, text="状态", width=4, justify=CENTER).grid(
            row=1, column=9, padx=5, pady=5)

        self.rows = GUI_ROWS
        self.cols = 9

        self.variable = []
        for row in range(self.rows):
            self.variable.append([])
            for col in range(self.cols):
                temp = StringVar()
                self.variable[row].append(temp)

        for row in range(self.rows):
            Entry(frame1, textvariable=self.variable[row][0],
                  width=8).grid(row=row + 2, column=1, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][1], state=DISABLED,
                  width=8).grid(row=row + 2, column=2, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][2], state=DISABLED,
                  width=8).grid(row=row + 2, column=3, padx=5, pady=5)
            Combobox(frame1, values=('<', '>'), textvariable=self.variable[row][3],
                     width=2).grid(row=row + 2, column=4, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=1000, textvariable=self.variable[row][4],
                    increment=0.01, width=6).grid(row=row + 2, column=5, padx=5, pady=5)
            Combobox(frame1, values=('B', 'S'), textvariable=self.variable[row][5],
                     width=2).grid(row=row + 2, column=6, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=100000, textvariable=self.variable[row][6],
                    increment=100, width=6).grid(row=row + 2, column=7, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][7],
                  width=8).grid(row=row + 2, column=8, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][8], state=DISABLED,
                  width=5).grid(row=row + 2, column=9, padx=5, pady=5)

        frame3 = Frame(self.window)
        frame3.pack(padx=10, pady=10)
        self.start_bt = Button(frame3, text="开始", command=self.start)
        self.start_bt.pack(side=LEFT)
        self.set_bt = Button(frame3, text='重置买卖', command=self.setFlags)
        self.set_bt.pack(side=LEFT)
        Button(frame3, text="历史记录", command=self.displayHisRecords).pack(side=LEFT)
        Button(frame3, text='保存', command=self.save).pack(side=LEFT)
        self.load_bt = Button(frame3, text='载入', command=self.load)
        self.load_bt.pack(side=LEFT)

        self.window.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.window.after(100, self.updateControls)
        self.window.mainloop()

    def displayHisRecords(self):
        '''
        显示历史信息
        :return:
        '''
        global order_msg
        tp = Toplevel()
        tp.title('历史记录')
        tp.resizable(0, 1)
        scrollbar = Scrollbar(tp)
        scrollbar.pack(side=RIGHT, fill=Y)
        col_name = ['日期', '时间', '证券代码', '证券名称', '方向', '价格', '数量', '备注']
        tree = Treeview(
            tp, show='headings', columns=col_name, height=30, yscrollcommand=scrollbar.set)
        tree.pack(expand=1, fill=Y)
        scrollbar.config(command=tree.yview)
        for name in col_name:
            tree.heading(name, text=name)
            tree.column(name, width=70, anchor=CENTER)

        for msg in order_msg:
            tree.insert('', 0, values=msg)

    def save(self):
        '''
        保存设置
        :return:
        '''
        global set_stock_info, order_msg, actual_stock_info
        self.getItems()
        with open('stockInfo.dat', 'wb') as fp:
            pickle.dump(set_stock_info, fp)
            # pickle.dump(actual_stock_info, fp)
            pickle.dump(order_msg, fp)

    def load(self):
        '''
        载入设置
        :return:
        '''
        global set_stock_info, order_msg, actual_stock_info
        with open('stockInfo.dat', 'rb') as fp:
            set_stock_info = pickle.load(fp)
            # actual_stock_info = pickle.load(fp)
            order_msg = pickle.load(fp)
        for row in range(self.rows):
            for col in range(self.cols):
                if col == 0:
                    self.variable[row][col].set(set_stock_info[row][0])
                elif col == 3:
                    self.variable[row][col].set(set_stock_info[row][1])
                elif col == 4:
                    self.variable[row][col].set(set_stock_info[row][2])
                elif col == 5:
                    self.variable[row][col].set(set_stock_info[row][3])
                elif col == 6:
                    self.variable[row][col].set(set_stock_info[row][4])
                elif col == 7:
                    temp = set_stock_info[row][5].strftime('%X')
                    if temp == '01:00:00':
                        self.variable[row][col].set('')
                    else:
                        self.variable[row][col].set(temp)

    def setFlags(self):
        '''
        重置买卖标志
        :return:
        '''
        global is_start, is_ordered
        if is_start is False:
            is_ordered = [1] * GUI_ROWS

    def updateControls(self):
        '''
        实时股票名称、价格、状态信息
        :return:
        '''
        global set_stock_info, actual_stock_info, is_start
        if is_start:
            # print('actual_stock_info', actual_stock_info)
            for row, (actual_code, actual_name, actual_price, _) in enumerate(actual_stock_info):
                self.variable[row][1].set(actual_name)
                self.variable[row][2].set(str(actual_price))
                if actual_code:
                    if is_ordered[row] == 1:
                        self.variable[row][8].set('监控中')
                    elif is_ordered[row] == 0:
                        self.variable[row][8].set('已下单')
                else:
                    self.variable[row][8].set('')

        self.window.after(3000, self.updateControls)

    def start(self):
        '''
        启动停止
        :return:
        '''
        global is_start
        if is_start is False:
            is_start = True
        else:
            is_start = False

        if is_start:
            self.getItems()
            # print(set_stock_info)
            self.start_bt['text'] = '停止'
            self.set_bt['state'] = DISABLED
            self.load_bt['state'] = DISABLED
        else:
            self.start_bt['text'] = '开始'
            self.set_bt['state'] = NORMAL
            self.load_bt['state'] = NORMAL

    def close(self):
        '''
        关闭程序时，停止monitor线程
        :return:
        '''
        global is_monitor
        is_monitor = False
        self.window.quit()

    def getItems(self):
        '''
        获取UI上用户输入的各项数据，
        '''
        global set_stock_info
        set_stock_info = []

        # 获取买卖价格数量输入项等
        for row in range(self.rows):
            set_stock_info.append([])
            for col in range(self.cols):
                temp = self.variable[row][col].get().strip()
                if col == 0:
                    if len(temp) == 6 and temp.isdigit():  # 判断股票代码是否为6位数
                        set_stock_info[row].append(temp)
                    else:
                        set_stock_info[row].append('')
                elif col == 3:
                    if temp in ('>', '<'):
                        set_stock_info[row].append(temp)
                    else:
                        set_stock_info[row].append('')
                elif col == 4:
                    try:
                        price = float(temp)
                        if price > 0:
                            set_stock_info[row].append(price)  # 把价格转为数字
                        else:
                            set_stock_info[row].append(0)
                    except ValueError:
                        set_stock_info[row].append(0)
                elif col == 5:
                    if temp in ('B', 'S'):
                        set_stock_info[row].append(temp)
                    else:
                        set_stock_info[row].append('')
                elif col == 6:
                    if temp.isdigit() and int(temp) >= 100:
                        set_stock_info[row].append(str(int(temp) // 100 * 100))
                    else:
                        set_stock_info[row].append('')
                elif col == 7:
                    try:
                        set_stock_info[row].append(datetime.datetime.strptime(temp, '%H:%M:%S').time())
                    except ValueError:
                        set_stock_info[row].append(datetime.datetime.strptime('1:00:00', '%H:%M:%S').time())


if __name__ == '__main__':
    '''
    open txd, login and them input '221', normal buy in
    '''
    t1 = threading.Thread(target=StockGui)
    t2 = threading.Thread(target=monitor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
