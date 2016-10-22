# -*- encoding: utf8 -*-

import tkinter.messagebox
from tkinter import *
from tkinter.ttk import *
import datetime
import threading
import pickle
import time

import win32con
import tushare as ts
import pdSql

from winguiauto import (dumpWindow, dumpWindows, getWindowText,getParentWindow,activeWindow,
                        getWindowStyle,getListViewInfo, setEditText, clickWindow,getDictViewInfo,
                        click, closePopupWindows, findTopWindow,
                        maxFocusWindow, minWindow, getTableData, sendKeyEvent)

NUM_OF_STOCKS = 10  # 自定义股票数量
POSITION_COlS=12 #define columns of position view
is_start = False
is_monitor = True
set_stocks_info = []
actual_stocks_info = []
consignation_info = []
is_ordered = [1] * NUM_OF_STOCKS  # 1：未下单  0：已下单
is_dealt = [0] * NUM_OF_STOCKS  # 0: 未成交   负整数：卖出数量， 正整数：买入数量
stock_codes = [''] * NUM_OF_STOCKS
max_drop_down=[5.0]*NUM_OF_STOCKS

class OperationThs:
    def __init__(self):

        self.__top_hwnd = findTopWindow(wantedText='网上股票交易系统5.0')
        temp_hwnds = dumpWindows(self.__top_hwnd)[0][0]
        temp_hwnds = dumpWindow(temp_hwnds)[4][0]
        self.__buy_sell_hwnds = dumpWindow(temp_hwnds)
        print(len(self.__buy_sell_hwnds) )
        if len(self.__buy_sell_hwnds) != 73:
            tkinter.messagebox.showerror('错误', '无法获得同花顺双向委托界面的窗口句柄')

    def __buy(self, code, quantity):
        """买函数
        :param code: 代码， 字符串
        :param quantity: 数量， 字符串
        """
        click(self.__buy_sell_hwnds[2][0])
        time.sleep(0.2)
        setEditText(self.__buy_sell_hwnds[2][0], code)
        time.sleep(0.2)
        if quantity != '0':
            setEditText(self.__buy_sell_hwnds[7][0], quantity)
            time.sleep(0.2)
        click(self.__buy_sell_hwnds[8][0])
        time.sleep(1)

    def __sell(self, code, quantity):
        """
        卖函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        click(self.__buy_sell_hwnds[11][0])
        time.sleep(0.2)
        setEditText(self.__buy_sell_hwnds[11][0], code)
        time.sleep(0.2)
        if quantity != '0':
            setEditText(self.__buy_sell_hwnds[16][0], quantity)
            time.sleep(0.2)
        click(self.__buy_sell_hwnds[17][0])
        time.sleep(1)

    def order(self, code, direction, quantity):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向， 字符串
        :param quantity: 买卖数量， 字符串
        """
        # restoreFocusWindow(self.__top_hwnd)
        if direction == 'B':
            self.__buy(code, quantity)
        if direction == 'S':
            self.__sell(code, quantity)
        closePopupWindows(self.__top_hwnd)

    def maximizeFocusWindow(self):
        """
        最大化窗口，获取焦点
        """
        maxFocusWindow(self.__top_hwnd)

    def minimizeWindow(self):
        """
        最小化窗体
        """
        minWindow(self.__top_hwnd)

    def clickRefreshButton(self, t=0.5):
        """
        点击刷新按钮
        """
        click(self.__buy_sell_hwnds[46][0])
        time.sleep(t)

    def getMoney(self):
        """
        获取可用资金
        """
        return float(self.__buy_sell_hwnds[51][1])

    def getPosition(self):
        """
        获取股票持仓
        """
        clickWindow(self.__buy_sell_hwnds[-2][0], 20)
        sendKeyEvent(win32con.VK_CONTROL, 0)
        sendKeyEvent(ord('C'), 0)
        sendKeyEvent(ord('C'), win32con.KEYEVENTF_KEYUP)
        sendKeyEvent(win32con.VK_CONTROL, win32con.KEYEVENTF_KEYUP)
        return getTableData(11)

    def getDeal(self, code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 需检查的股票代码， 字符串
        :param pre_position: 下单前的持仓
        :param cur_position: 下单后的持仓
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        if pre_position == cur_position:
            return 0
        pre_len = len(pre_position)
        cur_len = len(cur_position)
        if pre_len == cur_len:
            for row in range(cur_len):
                if cur_position[row][0] == code:
                    return int(cur_position[row][1]) - int(pre_position[row][1])
        if cur_len > pre_len:
            return int(cur_position[-1][1])


class OperationTdx:
    """
    def __init__(self):

        self.__top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
        self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
        windows = dumpWindows(self.__top_hwnd)
        temp_hwnd = 0
        for window in windows:
            child_hwnd, window_text, window_class = window
            if window_class == 'AfxMDIFrame42':
                temp_hwnd = child_hwnd
                break
        temp_hwnds = dumpWindow(temp_hwnd)
        temp_hwnds = dumpWindow(temp_hwnds[1][0])
        self.__menu_hwnds = dumpWindow(temp_hwnds[0][0])
        self.__buy_sell_hwnds = dumpWindow(temp_hwnds[4][0])
        if len(self.__buy_sell_hwnds) not in (68,):
            msg_box.showerror('错误', '无法获得通达信对买对卖界面的窗口句柄')
    """
    def __init__(self):
        self.__top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
        self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
        windows = dumpWindows(self.__top_hwnd)
        print('windows=',windows)
        temp_hwnd = 0
        temp_hwnd1=0
        p_hwnd=0
        for window in windows:
            child_hwnd, window_text, window_class = window
            if window_text=='买卖关联同一支股票':
                temp_hwnd1 = child_hwnd
                print("find the hwnd: 买卖关联同一支股票",temp_hwnd1)
        p_hwnd=getParentWindow(temp_hwnd1)
        print('p_hwnd=',p_hwnd)
        p_hwnd_children = dumpWindow(p_hwnd)
        print('p_hwnd_children=',p_hwnd_children)
        p_p_hwnd=getParentWindow(p_hwnd)
        p_p_hwnd_children = dumpWindow(p_p_hwnd)   #右侧操作区
        self.__menu_hwnds = dumpWindow(p_p_hwnd_children[0][0])
        print(self.__menu_hwnds)
        self.__buy_sell_hwnds = p_hwnd_children
        print(len(p_hwnd_children))
        if len(self.__buy_sell_hwnds) != 68:
            tkinter.messagebox.showerror('错误', '无法获得通达信对买对卖界面的窗口句柄')
    def __buy0(self, code, quantity,actual_price):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        setEditText(self.__buy_sell_hwnds[0][0], code)
        time.sleep(0.2)
        print(type(quantity))
        if quantity != '0':
            setEditText(self.__buy_sell_hwnds[3][0], quantity)
            time.sleep(0.2)
        click(self.__buy_sell_hwnds[5][0])
        time.sleep(0.2)
        
    def __buy(self, code, quantity,actual_price,limit=None):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        
        available_fund=self.getMoney()
        #if highest:
        #    actual_price=highest
        final_quantity=self._get_valid_buy_quantity(available_fund, actual_price, quantity)
        print('final_quantity=',final_quantity)
        if final_quantity:
            setEditText(self.__buy_sell_hwnds[0][0], code)
            time.sleep(0.2)
            setEditText(self.__buy_sell_hwnds[3][0], str(final_quantity))
            time.sleep(0.2)
            if limit:
                highest=limit[0]
                setEditText(self.__buy_sell_hwnds[1][0], str(highest))
                time.sleep(0.2)
            click(self.__buy_sell_hwnds[5][0])
            print('final_quantity=',final_quantity)
            print(datetime.datetime.now())
            time.sleep(0.2)
            
    def _get_valid_buy_quantity(self,available_fund,actual_price,expect_quantity=None,patial=None):
        """
        买入数量函数
        :param available_fund: 可用资金
        :param actual_price: 买入标的价格
        :param expect_quantity: 期望买入数量
        :param patial: 使用资金比例，如0.75,，0.5,0.33，0.25,0.10
        """
        actual_price=float(actual_price)
        available_fund=float(available_fund)
        if patial!=None and patial>0 and patial<=1.0:
            available_fund=available_fund*patial
        mini_quantity=100
        max_valid_quantity=int(available_fund//actual_price//mini_quantity)*mini_quantity
        acceptable_quantity=max_valid_quantity
        if expect_quantity:
            expect_quantity=int(expect_quantity)
            acceptable_quantity=int(expect_quantity//mini_quantity)*mini_quantity
        final_quantity=min(max_valid_quantity,acceptable_quantity)
        return final_quantity
    
    def __sell(self, code, quantity,limit=None):
        """
        卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        quantity=self._get_valid_sell_quantity(code, quantity)
        if quantity:
            setEditText(self.__buy_sell_hwnds[24][0], code)
            time.sleep(0.2)
            setEditText(self.__buy_sell_hwnds[27][0], str(quantity))
            time.sleep(0.2)
            if limit:
                lowest=limit[1]
                setEditText(self.__buy_sell_hwnds[25][0], str(lowest))
                time.sleep(0.2)
            click(self.__buy_sell_hwnds[29][0])
            print('final_quantity=',quantity)
            print(datetime.datetime.now())
            time.sleep(0.2)
            time.sleep(0.2)
    
    def _get_valid_sell_quantity(self,code,expect_quantity=None,patial=None):
        """
        卖出数量函数
        :param code: 买入股票代码 
        :param expect_quantity: 期望卖出数量
        :param patial: 使用资金比例，如0.75,，0.5,0.33，0.25,0.10
        """
        """
        available_position=0
        all_position=self.getPosition()
        if not all_position:
            return available_position
        this_position=[]
        for position in all_position:
            position_code=position[0]
            if position_code==code:
                this_position=position
                break
        if this_position:
            available_position=int(this_position[4])
            print('available_position=',available_position)
        """
        all_holding,available_position=self.getCodePosition(code)
        if patial!=None and patial>0 and patial<=1.0:
            available_position=available_position*patial
        mini_quantity=100
        max_valid_quantity=int(available_position//mini_quantity)*mini_quantity
        acceptable_quantity=max_valid_quantity
        if expect_quantity:
            expect_quantity=int(expect_quantity)
            acceptable_quantity=int(expect_quantity//mini_quantity)*mini_quantity
        final_quantity=min(max_valid_quantity,acceptable_quantity)
        print('final_quantity=',final_quantity,type(final_quantity))
        return final_quantity

    def order(self, code, direction, quantity,actual_price,limit_price=None):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向
        :param quantity: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        """
        #highest=None
        #lowest=None
        #if limit_price and len(limit_price)>=2:
        #    highest=limit_price[0]
        #    lowest=limit_price[1]
        # restoreFocusWindow(self.__top_hwnd)
        if direction == 'B':
            self.__buy(code, quantity,actual_price,limit_price)
        if direction == 'S':
            self.__sell(code, quantity,limit_price)
        print('self.__top_hwnd=',self.__top_hwnd)
        closePopupWindows(self.__top_hwnd)

    def maximizeFocusWindow(self):
        """
        最大化窗口，获取焦点
        """
        maxFocusWindow(self.__top_hwnd)

    def minimizeWindow(self):
        """
        最小化窗体
        """
        minWindow(self.__top_hwnd)

    def clickRefreshButton(self, t=0.3):
        """点击刷新按钮
        """
        #clickWindow(self.__menu_hwnds[0][0], self.__button['refresh'])
        #self.getMoney()
        """点击'关联同一只股票'按钮
        """
        click(self.__buy_sell_hwnds[49][0])
        time.sleep(t)
        #click(self.__buy_sell_hwnds[49][0])
        #time.sleep(t)
        print('refresh_hwnd=',self.__buy_sell_hwnds[49][0])
        print(datetime.datetime.now())

    def getMoney(self):
        """获取可用资金
        """
        setEditText(self.__buy_sell_hwnds[24][0], '999999')  # 测试时获得资金情况
        time.sleep(0.2)
        #print(self.__buy_sell_hwnds[12][0])
        money = getWindowText(self.__buy_sell_hwnds[12][0]).strip()
        #setEditText(self.__buy_sell_hwnds[24][0], '')  # 测试时获得资金情况
        time.sleep(0.2)
        #print('money_str=',len(money))
        try:
            money=float(money)
        except:
            money=0.0
        print('money=',money)
        return money

    def getPosition(self):
        """获取持仓股票信息
        """
        return getListViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
    
    def getCodePosition(self,code):
        """获取持仓股票信息
        """
        position_dict=getDictViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
        all_holding=0
        all_available_holding=0
        if code in list(position_dict.keys()):
            all_holding=int(position_dict[code][1])
            all_available_holding=int(position_dict[code][3])
        return all_holding,all_available_holding

    def getDeal(self, code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 股票代码
        :param pre_position: 下单前的持仓
        :param cur_position: 下单后的持仓
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        if pre_position == cur_position:
            return 0
        pre_len = len(pre_position)
        cur_len = len(cur_position)
        if pre_len == cur_len:
            for row in range(cur_len):
                if cur_position[row][0] == code:
                    return int(cur_position[row][2]) - int(pre_position[row][2])
        if cur_len > pre_len:
            return int(cur_position[-1][1])
        
    def _to_sell(self,strategy_dict):
        stop_profit_price=strategy_dict['stop_p']
        exit_price=strategy_dict['exit']
        realtime_dict,position_dict=self.get_realtime_holding()
        if not realtime_dict or (code_str not in list(realtime_dict.keys()) and realtime_dict):
            return ''
        realtime_series=realtime_dict[code_str]
        name=realtime_series.name
        open=realtime_series.open
        pre_close=realtime_series.pre_close
        highest_price,lowest_price=get_limit_price(name, pre_close)
        
        all_holding=int(position_dict[code_str][1])
        all_available_holding=int(position_dict[code_str][3])
        profit=float(position_dict[code_str][6])  
        price=realtime_series.price
        high=realtime_series.high
        low=realtime_series.low
        realtime_atr=max(high-pre_close,pre_close-low,high-low)
        
        bid=realtime_series.bid
        ask=realtime_series.ask
        volume=realtime_series.volume
        amount=realtime_series.amount
        b1_v=realtime_series.b1_v
        b1_p=realtime_series.b1_p
        b2_v=realtime_series.b2_v
        b2_p=realtime_series.b2_p
        b3_v=realtime_series.b3_v
        b3_p=realtime_series.b3_p
        b4_v=realtime_series.b4_v
        b4_p=realtime_series.b4_p
        b5_v=realtime_series.b5_v
        b5_p=realtime_series.b5_p
        a1_v=realtime_series.a1_v
        a1_p=realtime_series.a1_p
        a2_v=realtime_series.a2_v
        a2_p=realtime_series.a2_p
        a3_v=realtime_series.a3_v
        a3_p=realtime_series.a3_p
        a4_v=realtime_series.a4_v
        a4_p=realtime_series.a4_p
        a5_v=realtime_series.a5_v
        a5_p=realtime_series.a5_p
        time=realtime_series.time
        date=realtime_series.date
        sell_5_min_price=b5_p
        sell_5_v_total=b1_v+b2_v+b3_v+b4_v+b5_v
        buy_5_max_price=a5_p
        buy_5_v_total=a1_v+a2_v+a3_v+a4_v+a5_v
        return
    
    def get_realtime_holding(self):
        total_money=self.getMoney()
        position_dict=self.getPosition()
        realtime_dict={}
        holding_codes=list(position_dict.keys())
        if not position_dict or (code_str not in list(position_dict.keys()) and position_dict):
            return realtime_dict
        holding_realtime_df=ts.get_realtime_quotes(holding_codes)
        for i in range(len(holding_codes)):
            code_str=holding_codes[i]
            realtime_dict[code_str]=holding_realtime_df.iloc[i]
            
            realtime_series=realtime_dict[code_str]
            name=realtime_series.name
            open=realtime_series.open
            pre_close=realtime_series.pre_close
            highest_price,lowest_price=get_limit_price(name, pre_close)
            
            all_holding=int(position_dict[code_str][1])
            all_available_holding=int(position_dict[code_str][3])
            profit=float(position_dict[code_str][6])  
            price=realtime_series.price
            high=realtime_series.high
            low=realtime_series.low
            realtime_atr=max(high-pre_close,pre_close-low,high-low)
            
            bid=realtime_series.bid
            ask=realtime_series.ask
            volume=realtime_series.volume
            amount=realtime_series.amount
            b1_v=realtime_series.b1_v
            b1_p=realtime_series.b1_p
            b2_v=realtime_series.b2_v
            b2_p=realtime_series.b2_p
            b3_v=realtime_series.b3_v
            b3_p=realtime_series.b3_p
            b4_v=realtime_series.b4_v
            b4_p=realtime_series.b4_p
            b5_v=realtime_series.b5_v
            b5_p=realtime_series.b5_p
            a1_v=realtime_series.a1_v
            a1_p=realtime_series.a1_p
            a2_v=realtime_series.a2_v
            a2_p=realtime_series.a2_p
            a3_v=realtime_series.a3_v
            a3_p=realtime_series.a3_p
            a4_v=realtime_series.a4_v
            a4_p=realtime_series.a4_p
            a5_v=realtime_series.a5_v
            a5_p=realtime_series.a5_p
            time=realtime_series.time
            date=realtime_series.date
            sell_5_min_price=b5_p
            sell_5_v_total=b1_v+b2_v+b3_v+b4_v+b5_v
            buy_5_max_price=a5_p
            buy_5_v_total=a1_v+a2_v+a3_v+a4_v+a5_v
            
        return realtime_dict,position_dict

def pickCodeFromItems(items_info):
    """
    提取股票代码
    :param items_info: UI下各项输入信息
    :return:股票代码列表
    """
    stock_codes = []
    for item in items_info:
        stock_codes.append(item[0])
    return stock_codes

def get_limit_price(actual_name,pre_close):
    """
    提取股票涨停、跌停价
    :param actual_name: 股票中文名字，string
    :param pre_close: 股票上一交易日收盘价格, float
    :return:股票涨停、跌停价,string 
    """
    highest=0.0
    lowest=0.0
    if 'ST' in actual_name:
        highest = str(round(pre_close * 1.05, 2))
        lowest = str(round(pre_close * 0.95, 2))
    else:
        highest = str(round(pre_close * 1.1, 2))
        lowest = str(round(pre_close * 0.9, 2))
    return highest,lowest

def get_pass_time():
    """
    提取已开市时间比例
    :param this_time: ，string
    :return:,float 
    """
    pass_second=0.0
    if not is_trade_time_now():
        return pass_second
    this_time=datetime.datetime.now()
    hour=this_time.hour
    minute=this_time.minute
    second=this_time.second
    total_second=4*60*60
    if hour<9 or (hour==9 and minute<=30):
        pass
    elif hour<11 or (hour==11 and minute<=30):
        pass_second=(hour*3600+minute*60+second)-(9*3600+30*60)
    elif hour<13:
        pass_second=2*60*60
    elif hour<15:
        pass_second=2*60*60+(hour*3600+minute*60+second)-13*3600
    else:
        pass_second=total_second
    pass_rate=round(round(pass_second/total_second,2),2)
    return pass_rate

def set_terminate_profit():
    """
    提取已开市时间比例
    :param this_time: ，string
    :return:,float 
    """
    pass_second=0.0
    if not is_trade_time_now():
        return pass_second
    this_time=datetime.datetime.now()
    hour=this_time.hour
    minute=this_time.minute
    second=this_time.second
    total_second=4*60*60
    limit=10.0
    terminate_rate=limit
    if hour<10 or (hour==10 and minute<=30):
        terminate_rate=limit*0.618
    elif hour<11 or (hour==11 and minute<=30):
        terminate_rate=limit*0.382
    elif hour<14:
        terminate_rate=2.0
    elif hour<15:
        terminate_rate=2.0
    else:
        terminate_rate=10.0
    
    return terminate_rate

def getStockData():
    """
    获取股票实时数据
    :return:股票实时数据
    actual_stocks_info [('000001', '平安银行', 12.39,False), ('', '', 0,False), ('', '', 0,False), ('', '', 0,False), ('', '', 0,False)]
    """
    global stock_codes,max_drop_down
    code_name_price = []
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
                    limit_price=get_limit_price(actual_name, pre_close)
                    #print('limit_price=',limit_price)
                    high_price=float(df['high'][i])
                    current_price=float(df['price'][i])
                    is_great_drop_down=current_price<high_price*(1-max_drop_down[i]/100.0)
                    code_name_price.append((actual_code, df['name'][i], current_price,limit_price))
                    is_found = True
                    break
            if is_found is False:
                code_name_price.append(('', '', 0,(0,0)))
    except:
        code_name_price = [('', '', 0,(0,0))] * NUM_OF_STOCKS  # 网络不行，返回空
    return code_name_price

def monitor():
    """
    实时监控函数
    """
    global actual_stocks_info, consignation_info, is_ordered, is_dealt, set_stocks_info,operation
    count = 1
    try:
        try:
            operation = OperationTdx()
            print('OperationTdx completed')
        except:
            operation = OperationThs()
    except:
        tkinter.messagebox.showerror('错误', '无法获得交易软件句柄')

    while is_monitor:
        if is_start and pdsql.is_trade_time_now():
            actual_stocks_info = getStockData()
            #print('actual_stocks_info',actual_stocks_info)
            for row, (actual_code, actual_name, actual_price,limit_price) in enumerate(actual_stocks_info):
                if actual_code and is_start and is_ordered[row] == 1 and actual_price > 0 \
                        and set_stocks_info[row][1] and set_stocks_info[row][2] > 0 \
                        and set_stocks_info[row][3] and set_stocks_info[row][4] \
                        and datetime.datetime.now().time() > set_stocks_info[row][5]:
                    if set_stocks_info[row][1] == '>' and actual_price > set_stocks_info[row][2]:
                        #operation.maximizeFocusWindow()
                        operation.clickRefreshButton()
                        #pre_position = operation.getPosition()
                        pre_all_holding,_pre_available_position=operation.getCodePosition(actual_code)
                        operation.order(actual_code, set_stocks_info[row][3], set_stocks_info[row][4],actual_price,limit_price)
                        dt = datetime.datetime.now()
                        is_ordered[row] = 0
                        operation.clickRefreshButton()
                        #cur_position = operation.getPosition()
                        cur_all_holding,_cur_available_position=operation.getCodePosition(actual_code)
                        #is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                        is_dealt[row]=cur_all_holding-pre_all_holding
                        consignation_info.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stocks_info[row][3],
                             actual_price, set_stocks_info[row][4], '已委托', is_dealt[row]))

                    if set_stocks_info[row][1] == '<' and float(actual_price) < set_stocks_info[row][2]:
                        #operation.maximizeFocusWindow()
                        operation.clickRefreshButton()
                        #pre_position = operation.getPosition()
                        pre_all_holding,_pre_available_position=operation.getCodePosition(actual_code)
                        operation.order(actual_code, set_stocks_info[row][3], set_stocks_info[row][4],actual_price,limit_price)
                        dt = datetime.datetime.now()
                        is_ordered[row] = 0
                        operation.clickRefreshButton()
                        #cur_position = operation.getPosition()
                        cur_all_holding,_cur_available_position=operation.getCodePosition(actual_code)
                        #is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                        is_dealt[row]=cur_all_holding-pre_all_holding
                        #is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                        consignation_info.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stocks_info[row][3],
                             actual_price, set_stocks_info[row][4], '已委托', is_dealt[row]))

        if count % 60 == 0:
            operation.clickRefreshButton()
        time.sleep(3)
        count += 1

def monitor1():
    """
    实时监控函数
    """
    global actual_stocks_info, consignation_info, is_ordered, is_dealt, set_stocks_info
    count = 1
    try:
        try:
            operation = OperationSzx()
        except:
            operation = OperationThs()
    except:
        tkinter.messagebox.showerror('错误', '无法获得交易软件句柄')

    while is_monitor:

        if is_start:
            actual_stocks_info = getStockData()
            #print('actual_stocks_info',actual_stocks_info)
            for row, (actual_code, actual_name, actual_price) in enumerate(actual_stocks_info):
                if actual_code and is_start and is_ordered[row] == 1 and actual_price > 0 \
                        and set_stocks_info[row][1] and set_stocks_info[row][2] > 0 \
                        and set_stocks_info[row][3] and set_stocks_info[row][4] \
                        and datetime.datetime.now().time() > set_stocks_info[row][5]:
                    if set_stocks_info[row][1] == '>' and actual_price > set_stocks_info[row][2]:
                        operation.maximizeFocusWindow()
                        pre_position = operation.getPosition()
                        print('pre_position=',pre_position)
                        operation.order(actual_code, set_stocks_info[row][3], set_stocks_info[row][4])
                        dt = datetime.datetime.now()
                        is_ordered[row] = 0
                        operation.clickRefreshButton()
                        cur_position = operation.getPosition()
                        is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                        consignation_info.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stocks_info[row][3],
                             actual_price, set_stocks_info[row][4], '已委托', is_dealt[row]))

                    if set_stocks_info[row][1] == '<' and float(actual_price) < set_stocks_info[row][2]:
                        operation.maximizeFocusWindow()
                        pre_position = operation.getPosition()
                        print('pre_position=',pre_position)
                        operation.order(actual_code, set_stocks_info[row][3], set_stocks_info[row][4])
                        dt = datetime.datetime.now()
                        is_ordered[row] = 0
                        operation.clickRefreshButton()
                        cur_position = operation.getPosition()
                        is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                        consignation_info.append(
                            (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                             actual_name, set_stocks_info[row][3],
                             actual_price, set_stocks_info[row][4], '已委托', is_dealt[row]))

        if count % 200 == 0:
            operation.clickRefreshButton()
        time.sleep(3)
        count += 1

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
        Label(frame1, text="实时价格", width=8, justify=CENTER).grid(
            row=1, column=3, padx=5, pady=5)
        Label(frame1, text="关系", width=4, justify=CENTER).grid(
            row=1, column=4, padx=5, pady=5)
        Label(frame1, text="设定价格", width=8, justify=CENTER).grid(
            row=1, column=5, padx=5, pady=5)
        Label(frame1, text="方向", width=4, justify=CENTER).grid(
            row=1, column=6, padx=5, pady=5)
        Label(frame1, text="数量", width=8, justify=CENTER).grid(
            row=1, column=7, padx=5, pady=5)
        Label(frame1, text="时间可选", width=8, justify=CENTER).grid(
            row=1, column=8, padx=5, pady=5)
        Label(frame1, text="委托", width=6, justify=CENTER).grid(
            row=1, column=9, padx=5, pady=5)
        Label(frame1, text="成交", width=6, justify=CENTER).grid(
            row=1, column=10, padx=5, pady=5)
        
        Label(frame1, text="涨幅", width=6, justify=CENTER).grid(
            row=1, column=11, padx=5, pady=5)

        self.rows = NUM_OF_STOCKS
        self.cols = 11

        self.variable = []
        for row in range(self.rows):
            self.variable.append([])
            for col in range(self.cols):
                self.variable[row].append(StringVar())

        for row in range(self.rows):
            Entry(frame1, textvariable=self.variable[row][0],
                  width=8).grid(row=row + 2, column=1, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][1], state=DISABLED,
                  width=8).grid(row=row + 2, column=2, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][2], state=DISABLED, justify=RIGHT,
                  width=8).grid(row=row + 2, column=3, padx=5, pady=5)
            Combobox(frame1, values=('<', '>'), textvariable=self.variable[row][3],
                     width=2).grid(row=row + 2, column=4, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=10, textvariable=self.variable[row][4], justify=RIGHT,
                    increment=0.01, width=6).grid(row=row + 2, column=5, padx=5, pady=5)
            Combobox(frame1, values=('B', 'S'), textvariable=self.variable[row][5],
                     width=2).grid(row=row + 2, column=6, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=100, textvariable=self.variable[row][6], justify=RIGHT,
                    increment=100, width=6).grid(row=row + 2, column=7, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][7],
                  width=8).grid(row=row + 2, column=8, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][8], state=DISABLED, justify=CENTER,
                  width=6).grid(row=row + 2, column=9, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][9], state=DISABLED, justify=RIGHT,
                  width=6).grid(row=row + 2, column=10, padx=5, pady=5)
            Spinbox(frame1, from_=0.9, to=1.1, textvariable=self.variable[row][10], justify=RIGHT,
                    increment=0.01, width=6).grid(row=row + 2, column=11, padx=5, pady=5)

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
        
        self.sellall_bt = Button(frame3, text='清仓', command=self.sellAll())
        self.sellall_bt.pack(side=LEFT)

        self.window.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.window.after(100, self.updateControls)
        self.window.mainloop()

    def displayHisRecords(self):
        """
        显示历史信息
        """
        global consignation_info
        tp = Toplevel()
        tp.title('历史记录')
        tp.resizable(0, 1)
        scrollbar = Scrollbar(tp)
        scrollbar.pack(side=RIGHT, fill=Y)
        col_name = ['日期', '时间', '证券代码', '证券名称', '方向', '价格', '数量', '委托', '成交']
        tree = Treeview(
            tp, show='headings', columns=col_name, height=30, yscrollcommand=scrollbar.set)
        tree.pack(expand=1, fill=Y)
        scrollbar.config(command=tree.yview)
        for name in col_name:
            tree.heading(name, text=name)
            tree.column(name, width=70, anchor=CENTER)

        for msg in consignation_info:
            tree.insert('', 0, values=msg)

    def save(self):
        """
        保存设置
        """
        global set_stocks_info, consignation_info
        self.getItems()
        with open('stockInfo.dat', 'wb') as fp:
            pickle.dump(set_stocks_info, fp)
            pickle.dump(consignation_info, fp)

    def load(self):
        """
        载入设置
        """
        global set_stocks_info, consignation_info
        try:
            with open('stockInfo.dat', 'rb') as fp:
                set_stocks_info = pickle.load(fp)
                consignation_info = pickle.load(fp)
        except FileNotFoundError as error:
            tkinter.messagebox.showerror('错误', error)

        for row in range(self.rows):
            for col in range(self.cols):
                if col == 0:
                    self.variable[row][col].set(set_stocks_info[row][0])
                elif col == 3:
                    self.variable[row][col].set(set_stocks_info[row][1])
                elif col == 4:
                    self.variable[row][col].set(set_stocks_info[row][2])
                elif col == 5:
                    self.variable[row][col].set(set_stocks_info[row][3])
                elif col == 6:
                    self.variable[row][col].set(set_stocks_info[row][4])
                elif col == 7:
                    temp = set_stocks_info[row][5].strftime('%X')
                    if temp == '01:00:00':
                        self.variable[row][col].set('')
                    else:
                        self.variable[row][col].set(temp)

    def setFlags(self):
        """
        重置买卖标志
        """
        global is_start, is_ordered
        if is_start is False:
            is_ordered = [1] * NUM_OF_STOCKS
    
    def sellAll(self):
        return

    def updateControls(self):
        """
        实时股票名称、价格、状态信息
        """
        global actual_stocks_info, is_start
        if is_start:
            for row, (actual_code, actual_name, actual_price,is_great_drop) in enumerate(actual_stocks_info):
                if actual_code:
                    self.variable[row][1].set(actual_name)
                    self.variable[row][2].set(str(actual_price))
                    if is_ordered[row] == 1:
                        self.variable[row][8].set('监控中')
                    elif is_ordered[row] == 0:
                        self.variable[row][8].set('已委托')
                    self.variable[row][9].set(str(is_dealt[row]))
                else:
                    self.variable[row][1].set('')
                    self.variable[row][2].set('')
                    self.variable[row][8].set('')
                    self.variable[row][9].set('')

        self.window.after(3000, self.updateControls)

    def start(self):
        """
        启动停止
        """
        global is_start, stock_codes, set_stocks_info
        if is_start is False:
            is_start = True
        else:
            is_start = False

        if is_start:
            self.getItems()
            stock_codes = pickCodeFromItems(set_stocks_info)
            self.start_bt['text'] = '停止'
            self.set_bt['state'] = DISABLED
            self.load_bt['state'] = DISABLED
        else:
            self.start_bt['text'] = '开始'
            self.set_bt['state'] = NORMAL
            self.load_bt['state'] = NORMAL

    def close(self):
        """
        关闭程序时，停止monitor线程
        """
        global is_monitor
        is_monitor = False
        self.window.quit()

    def getItems(self):
        """
        获取UI上用户输入的各项数据，
        """
        global set_stocks_info
        set_stocks_info = []

        # 获取买卖价格数量输入项等
        for row in range(self.rows):
            set_stocks_info.append([])
            for col in range(self.cols):
                temp = self.variable[row][col].get().strip()
                if col == 0:
                    if len(temp) == 6 and temp.isdigit():  # 判断股票代码是否为6位数
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 3:
                    if temp in ('>', '<'):
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 4:
                    try:
                        price = float(temp)
                        if price > 0:
                            set_stocks_info[row].append(price)  # 把价格转为数字
                        else:
                            set_stocks_info[row].append(0)
                    except ValueError:
                        set_stocks_info[row].append(0)
                elif col == 5:
                    if temp in ('B', 'S'):
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 6:
                    if temp.isdigit() and int(temp) >= 0:
                        set_stocks_info[row].append(str(int(temp) // 100 * 100))
                    else:
                        set_stocks_info[row].append('')
                elif col == 7:
                    try:
                        set_stocks_info[row].append(datetime.datetime.strptime(temp, '%H:%M:%S').time())
                    except ValueError:
                        set_stocks_info[row].append(datetime.datetime.strptime('1:00:00', '%H:%M:%S').time())


if __name__ == '__main__':
    t1 = threading.Thread(target=StockGui)
    t1.start()
    t1.join(2)
    t2 = threading.Thread(target=monitor)
    t2.start()
#test
