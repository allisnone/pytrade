# -*- encoding: utf8 -*-

import tkinter.messagebox
from tkinter import *
from tkinter.ttk import *
import datetime
import threading
import pickle
import time
import win32con
#import tushare as ts
#import pdSql
import sendEmail as sm

from winguiauto import (dumpWindow, dumpWindows, getWindowText,getParentWindow,activeWindow,
                        getWindowStyle,getListViewInfo, setEditText, clickWindow,getDictViewInfo,
                        click, closePopupWindows, findTopWindow,findSubWindow,
                        select_combobox,getEditText,get_combobox_id,get_valid_combobo_ids,
                        maxFocusWindow, minWindow, getTableData, sendKeyEvent)
"""
NUM_OF_STOCKS = 10  # 自定义股票数量
POSITION_COlS=14 #define columns of position view
is_start = False
is_monitor = True
set_stocks_info = []
actual_stocks_info = []
consignation_info = []
is_ordered = [1] * NUM_OF_STOCKS  # 1：未下单  0：已下单
is_dealt = [0] * NUM_OF_STOCKS  # 0: 未成交   负整数：卖出数量， 正整数：买入数量
stock_codes = [''] * NUM_OF_STOCKS
max_drop_down=[5.0]*NUM_OF_STOCKS
"""
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
    def __init__(self,debug=False):
        self.debug = debug
        self.init_hwnd()
        """
        self.__top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
        self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
        windows = dumpWindows(self.__top_hwnd)
        if self.debug: print('windows=',windows)
        temp_hwnd = 0
        temp_hwnd_guanlian=0
        p_hwnd=0
        self.p_acc_hwnd = 0
        self.acc_hwnd = 0
        for window in windows:
            child_hwnd, window_text, window_class = window
            if window_text=='买卖关联同一支股票':
                temp_hwnd_guanlian = child_hwnd
                print("find the hwnd: 买卖关联同一支股票, ",temp_hwnd_guanlian)
            if window_class == 'MHPToolBar' and window_text=='MainViewBar':
                self.p_acc_hwnd = child_hwnd
                print('parent_acc_combobox_hwnd=',self.p_acc_hwnd)
                p_p_acc_hwnd=getParentWindow(self.p_acc_hwnd)
                acc_windows = dumpWindows(self.p_acc_hwnd)   
                for window in acc_windows:
                    child_hwnd, window_text, window_class = window
                    if window_class == 'ComboBox':
                        self.acc_hwnd = child_hwnd
                        print('acc_combobox_hwnd=',self.acc_hwnd)
        else:
            pass  
            #raise Exception("Change saving type failed") 
                    
        if temp_hwnd_guanlian:
            p_hwnd=getParentWindow(temp_hwnd_guanlian) #买卖关联同一支股票的上一级句柄
            if self.debug: print('p_hwnd=',p_hwnd)
            p_hwnd_children = dumpWindow(p_hwnd)
            if self.debug: print('p_hwnd_children=',p_hwnd_children)
            p_p_hwnd=getParentWindow(p_hwnd) #股票交易第一级句柄
            p_p_hwnd_children = dumpWindow(p_p_hwnd)   #右侧操作区
            self.__menu_hwnds = dumpWindow(p_p_hwnd_children[0][0])
            if self.debug: print(self.__menu_hwnds)
            self.__buy_sell_hwnds = p_hwnd_children
            EXPECT_LEN = 68
            if len(self.__buy_sell_hwnds) != EXPECT_LEN:
                sm.send_mail(sub='无法获得通达信对买对卖界面的窗口句柄',content='子句柄数量为 %s，不等于期望数量：%s.也许软件亿升级。' %(len(self.__buy_sell_hwnds),EXPECT_LEN))
                tkinter.messagebox.showerror('错误', '无法获得通达信对买对卖界面的窗口句柄')
            else:
                pass
        else:
            sm.send_mail(sub='无法获得  买卖关联同一支股票 的窗口句柄',content='请点击  双向委托 按钮' )
            tkinter.messagebox.showerror('错误', '无法获得 "买卖关联同一支股票"的窗口句柄')
        """
    def enable_debug(self,debug=True):
        self.debug=debug
                
    def init_hwnd(self):
        self.__top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
        self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
        windows = dumpWindows(self.__top_hwnd)
        if self.debug: print('windows=',windows)
        temp_hwnd = 0
        temp_hwnd_guanlian=0
        p_hwnd=0
        self.p_acc_hwnd = 0
        self.acc_hwnd = 0
        self.new_stock_order_hwnd = 0
        find_guan_lian = False
        find_new_stock = False
        find_combobox = False
        for window in windows:
            child_hwnd, window_text, window_class = window
            if window_text=='买卖关联同一支股票':
                temp_hwnd_guanlian = child_hwnd
                print("find the hwnd: 买卖关联同一支股票, ",temp_hwnd_guanlian)
            if window_class == 'MHPToolBar' and window_text=='MainViewBar':
                self.p_acc_hwnd = child_hwnd
                print('parent_acc_combobox_hwnd=',self.p_acc_hwnd)
                p_p_acc_hwnd=getParentWindow(self.p_acc_hwnd)
                acc_windows = dumpWindows(self.p_acc_hwnd)   
                for window in acc_windows:
                    child_hwnd, window_text, window_class = window
                    if window_class == 'ComboBox':
                        self.acc_hwnd = child_hwnd
                        find_combobox = True
                        print('acc_combobox_hwnd=',self.acc_hwnd)
            if window_text=='一键申购':
                self.new_stock_order_hwnd = child_hwnd
                find_new_stock = True
            if find_guan_lian and find_new_stock and find_combobox:
                break
        else:
            pass  
            #raise Exception("Change saving type failed") 
                    
        if temp_hwnd_guanlian:
            p_hwnd=getParentWindow(temp_hwnd_guanlian) #买卖关联同一支股票的上一级句柄
            if self.debug: print('p_hwnd=',p_hwnd)
            p_hwnd_children = dumpWindow(p_hwnd)
            if self.debug: print('p_hwnd_children=',p_hwnd_children)
            p_p_hwnd=getParentWindow(p_hwnd) #股票交易第一级句柄
            p_p_hwnd_children = dumpWindow(p_p_hwnd)   #右侧操作区
            self.__menu_hwnds = dumpWindow(p_p_hwnd_children[0][0])
            if self.debug: print(self.__menu_hwnds)
            self.__buy_sell_hwnds = p_hwnd_children
            EXPECT_LEN = 83#68
            print(len(self.__buy_sell_hwnds))
            if len(self.__buy_sell_hwnds) != EXPECT_LEN:
                sm.send_mail(sub='无法获得通达信对买对卖界面的窗口句柄',content='子句柄数量为 %s，不等于期望数量：%s.也许软件亿升级。' %(len(self.__buy_sell_hwnds),EXPECT_LEN))
                tkinter.messagebox.showerror('错误', '无法获得通达信对买对卖界面的窗口句柄')
            else:
                pass
        else:
            sm.send_mail(sub='无法获得  买卖关联同一支股票 的窗口句柄',content='请点击  双向委托 按钮' )
            tkinter.messagebox.showerror('错误', '无法获得 "买卖关联同一支股票"的窗口句柄')
        return
    
    def _new_stock_order(self):
        """
        新股申购
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        if self.new_stock_order_hwnd:
            click(self.new_stock_order_hwnd)
            time.sleep(0.1)
            closePopupWindows(self.new_stock_order_hwnd,wantedText='确认')
        else:
            pass
        return
    
    def __buy0(self, code, quantity,new_stock_order_hwnd):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        setEditText(self.__buy_sell_hwnds[0][0], code)
        time.sleep(0.2)
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
        if self.debug: print('final_buy_quantity=',final_quantity)
        if final_quantity:
            setEditText(self.__buy_sell_hwnds[0][0], code)
            time.sleep(0.2)
            setEditText(self.__buy_sell_hwnds[3][0], str(final_quantity))
            time.sleep(0.2)
            if limit:
                highest=limit[0]
                setEditText(self.__buy_sell_hwnds[1][0], str(highest))
                time.sleep(0.2)
            else:
                setEditText(self.__buy_sell_hwnds[1][0], str(actual_price))
            click(self.__buy_sell_hwnds[5][0])
            if self.debug: print('buy_quantity=',final_quantity)
            if self.debug: print(datetime.datetime.now())
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
    
    def __sell(self, code, quantity,actual_price,limit=None):
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
            else:
                setEditText(self.__buy_sell_hwnds[25][0], str(actual_price))
                time.sleep(0.2)
            click(self.__buy_sell_hwnds[29][0])
            if self.debug: print('sell_quantity=',quantity)
            if self.debug: print(datetime.datetime.now())
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
        if self.debug: print('final_sell_quantity=',final_quantity,type(final_quantity))
        return final_quantity

    #def order(self, code, direction, quantity,actual_price,limit_price=None):
    def order(self, code, direction, quantity,actual_price,limit_price=None,post_confirm_interval=0,check_valid_time=True):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向
        :param quantity: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        :param actual_price: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        :param limit_price: [涨停价,跌停价]
        """
        #highest=None
        #lowest=None
        #if limit_price and len(limit_price)>=2:
        #    highest=limit_price[0]
        #    lowest=limit_price[1]
        # restoreFocusWindow(self.__top_hwnd)
        pre_position = self.get_my_position()
        if quantity<=0:#invalid quantity
            if self.debug: print('Please input valid quantity!')
            return
        trade_num = quantity
        if direction == 'B':
            self.__buy(code, quantity,actual_price,limit_price)
        if direction == 'S':
            trade_num = -1*quantity
            self.__sell(code, quantity,actual_price,limit_price)
        #if self.debug: print('self.__top_hwnd=',self.__top_hwnd)
        closePopupWindows(self.__top_hwnd)
        post_position = self.get_my_position()
        pos_chg = self.getPostionChange(pre_position,post_position)
        if self.debug: print('pos_chg=',pos_chg)
        self.trade_confirm(code, trade_num, pos_chg)

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
        #print('refresh_hwnd=',self.__buy_sell_hwnds[49][0])
        #print(datetime.datetime.now())

    def getMoney(self):
        """获取可用资金
        """
        code = '999999'
        setEditText(self.__buy_sell_hwnds[24][0], code)  # 测试时获得资金情况
        time.sleep(0.2)
        if self.debug: print('money_hwnd=',self.__buy_sell_hwnds[12][0])
        money = getWindowText(self.__buy_sell_hwnds[12][0]).strip()
        #setEditText(self.__buy_sell_hwnds[24][0], '')  # 测试时获得资金情况
        time.sleep(0.2)
        #print('money_str=',money)
        try:
            money=float(money)
        except:
            money=0.0
            sm.send_mail(sub='获取可用资金失败',content='检查验证是否软件异常' )
        if self.debug: print('可用资金=',money)
        return money
    
    def getRealtimeQuotation(self,code='300431'):
        """获取可用资金
        """
        #code = '999999'
        setEditText(self.__buy_sell_hwnds[24][0], code)  # 测试时获得资金情况
        time.sleep(0.2)
        if self.debug: print('money_hwnd=',self.__buy_sell_hwnds[12][0])
        #money = getWindowText(self.__buy_sell_hwnds[12][0]).strip()
        #setEditText(self.__buy_sell_hwnds[24][0], '')  # 测试时获得资金情况
        buy1 = getWindowText(self.__buy_sell_hwnds[25][0]).strip()
        sell1 = getWindowText(self.__buy_sell_hwnds[1][0]).strip()
        print('buy1=',buy1)
        print('sell1=',sell1)
        time.sleep(0.2)
        #print('money_str=',money)
        try:
            money=float(money)
        except:
            money=0.0
            sm.send_mail(sub='获取可用资金失败',content='检查验证是否软件异常' )
        if self.debug: print('可用资金=',money)
        return money

    def getPosition(self):
        """获取持仓股票信息
        """
        POSITION_COlS = 14 
        return getListViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
    
    def get_my_position(self):
        POSITION_COlS = 14 
        return getDictViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
        
    def isRightAcc(self,acc='36005',pos_list=list()):
        acount_dict = {'0130010635':'36005','A732980330':'36005','A355519785':'38736','0148358729':'38736'}
        pos_list = self.getPosition()
        print('pos_list=',pos_list)
        is_right_acc = False
        if pos_list:
            stock_ower = pos_list[0][12]
            if stock_ower in list(acount_dict.keys()):
                is_right_acc = acc== acount_dict[stock_ower]
        return is_right_acc
    
    def getAccountMoney(self,acc='36005'):
        pos_list = self.getPosition()
        market_value = 0.0
        available_money = 0.0
        if self.isRightAcc(acc, pos_list):
            available_money = self.getMoney()
        else:
            current_acc_id,current_box_id = self.get_acc_combobox_id()
            position_dict = self.get_my_position() 
            exchange_id = self.change_account(current_acc_id, current_box_id, position_dict)
            pos_list = self.getPosition()
            if self.isRightAcc(acc, pos_list):
                available_money = self.getMoney()
            else:
                return market_value,available_money
        if pos_list:
            for stock_data in pos_list:
                market_value = market_value + float(stock_data[9])  #9 for '参考市值'
        return market_value,available_money
    
    def getCodePosition(self,code):
        """获取持仓股票信息
        """
        POSITION_COlS = 14 
        position_dict = getDictViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
        #print('position_dict=',position_dict)
        hold_num = 0
        available_to_sell =0
        if code in list(position_dict.keys()):
            hold_num = position_dict[code]['当前持仓']
            available_to_sell = position_dict[code]['可用余额 ']
        return hold_num,available_to_sell
    
    def getPostionChange(self,pre_position,post_position):
        """
        获取成交数量
        :param pre_position: 下单前的持仓, dict type  (getPosition)
        :param post_position: 下单后的持仓, dict type (getPosition)
        :return pos_chg, 持仓变化，dict type
        """
        pre_codes = list(pre_position.keys())
        post_codes = list(post_position.keys())
        new_buy_codes = list(set(post_codes).difference(set(pre_codes)))
        old_sell_codes = list(set(pre_codes).difference(set(post_codes)))
        all_codes = list(set(pre_codes+post_codes))
        pos_chg = {}
        for code in all_codes:
            if code in old_sell_codes:
                pos_chg.update({code:-1*pre_position[code]['当前持仓']})
            elif code in new_buy_codes:
                pos_chg.update({code:post_position[code]['当前持仓']})
            else:
                chg_num = post_position[code]['当前持仓'] - pre_position[code]['当前持仓']
                pos_chg.update({code: chg_num})
        if self.debug: print('pos_chg= ', pos_chg)
        return pos_chg
    
    def trade_confirm(self,code, trade_num, pos_chg={}):
        """
    确认成交并email通知
        :param code: 股票代码, char type  (getPosition)
        :param trade_num: 计划成交数量, int type (getPosition)
        :return pos_chg, 持仓变化，dict type
        """
        if trade_num==0:# no trade
            return
        if not pos_chg or code not in list(pos_chg.keys()):
            if self.debug: print('请手动确认股票  %s交易是否成功 !', code)
            pass
        else:
            actual_trade_num = pos_chg[code]
            if actual_trade_num==0:
                sm.send_mail(sub='计划成交%s, 股票%s无任何成交' %(trade_num,code),content='请人工检查验证！' )
            else:
                if (trade_num>0 and actual_trade_num>0) or (trade_num<0 and actual_trade_num<0):
                    remain_num = actual_trade_num - actual_trade_num
                    if  remain_num==0:
                        sm.send_mail(sub='[股票%s全部成交]计划成交%s, 还有%s未成交' %(code, trade_num, remain_num),content='请人工检查验证！' )
                    else:
                        sm.send_mail(sub='[股票%s部分成交]计划成交%s, 还有%s未成交' %(code, trade_num, remain_num),content='请人工检查验证！' )
                elif (trade_num>0 and actual_trade_num<0):
                    sm.send_mail(sub='[股票%s交易逻辑混乱]原计划买入%s股, 结果<卖出>%s股' %(code, trade_num, actual_trade_num),content='请人工检查验证！' )
                elif (trade_num<0 and actual_trade_num>0):
                    sm.send_mail(sub='[股票%s交易逻辑混乱]原计划<卖出>%s股, 结果买入%s股' %(code, trade_num, actual_trade_num),content='请人工检查验证！' )
                else:
                    pass
        return
                    

    def getDeal(self, code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 股票代码
        :param pre_position: 下单前的持仓,list
        :param cur_position: 下单后的持仓, list
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
        
    def get_acc_combobox_id(self,position_dict={},acc_combobox_map = {'36005':0,'38736':1}):
        acount_dict = {'0130010635':'36005','A732980330':'36005','A355519785':'38736','0148358729':'38736'}
        acc_id = ''
        combobox_id = 0
        if not position_dict:
            position_dict = self.get_my_position()
        else:
            pass
        if position_dict:
            code_gudong = position_dict[list(position_dict.keys())[0]]['股东代码']
            acc_id = acount_dict[code_gudong]
            combobox_id = acc_combobox_map[acc_id]
        else:
            pass
        return acc_id,combobox_id
    
    def change_account(self,current_acc_id,current_box_id,position_dict={}):
        """
        双帐号切换: 默认先登录36005,再登录38736
        :param code: 股票代码
        :param current_acc_id: 当前账户id,int
        :param current_box_id: 当前账户切换的下拉菜单id, int
        :param position_dict: 持仓, dict
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        #index_map = {'36005':0,'38736':1}
        exchange_id = -1
        if self.p_acc_hwnd and self.acc_hwnd:
            valid_combobox_id = get_valid_combobo_ids(self.p_acc_hwnd, self.acc_hwnd)
            if self.debug: print('valid_combobox_id=',valid_combobox_id)
            len_id = len(valid_combobox_id)
            if len_id>2:
                pass
                if self.debug: print('超过三个账户切换，未实现')
            elif len_id==2:
                if current_box_id==0 and current_acc_id=='36005':
                    exchange_id = select_combobox(self.p_acc_hwnd ,self.acc_hwnd,index_id=1)
                    #target_acc_id,target_box_id = self.get_acc_combobox_id(position_dict)
                    if self.debug: print('从%s账户切换成功到：%s ' % (current_acc_id,'38736'))
                    time.sleep(1)
                elif current_box_id==1 and current_acc_id=='38736':
                    exchange_id = select_combobox(self.p_acc_hwnd ,self.acc_hwnd,index_id=0)
                    #target_acc_id,target_box_id = self.get_acc_combobox_id(position_dict)
                    if self.debug: print('从%s账户切换成功到：%s ' % (current_acc_id,'36005'))
                    time.sleep(1)
                else:
                    if self.debug: print('账户切换异常，请检查')
            elif len_id==1:
                pass
                if self.debug: print('仅有一个登录账户，无需切换')
            else:
                pass
                if self.debug: print('无任何登录账户，无需切换')
        else:
            sm.send_mail(sub='无法获得通达信帐户切换下来菜单的窗口句柄',content='下来菜单的父窗口句柄 =%s，下来菜单的窗口句柄= %s.也许软件亿升级。' %(self.p_acc_hwnd,self.acc_hwnd))
        return exchange_id
    
    def get_all_position(self):
        avl_sell_datas = {}
        position = self.get_my_position()
        current_acc_id,current_box_id = self.get_acc_combobox_id(position_dict=position)
        print('first_acc=%s' % current_acc_id)
        current_avl_sell = []
        for code in list(position.keys()):
            #print(position[code].keys())
            avl_to_sell = position[code]['可用余额 ']
            if avl_to_sell>=100:
                current_avl_sell.append(code)
        avl_sell_datas[current_acc_id] = current_avl_sell
        exchange_id = self.change_account(current_acc_id, current_box_id, position)
        second_acc_position = self.get_my_position()
        second_acc_id,second_box_id = self.get_acc_combobox_id(position_dict=second_acc_position)
        print('second_acc=%s' % second_acc_id)
        second_avl_sell = []
        for code in list(second_acc_position.keys()):
            avl_to_sell = second_acc_position[code]['可用余额 ']
            if avl_to_sell>=100:
                second_avl_sell.append(code)
        avl_sell_datas[second_acc_id] = second_avl_sell
        monitor_stocks = list(set(second_avl_sell + current_avl_sell))
        position.update(second_acc_position)
        return position,avl_sell_datas,monitor_stocks
    
    
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


    
