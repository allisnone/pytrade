# -*- encoding: utf8 -*-
import functools
import io
import os
import re
import tempfile
import time
"""
import tkinter.messagebox
from tkinter import *
from tkinter.ttk import *
"""
import datetime
import threading
import pickle
import time
import win32con
#import tushare as ts
#import pdSql
import sendEmail as sm
from pytrade_tdx import OperationThs
from easytrader.yh_clienttrader import YHClientTrader
from easytrader.config import client
from tradeTime import *
from easytrader_config0 import (HD,VA,LI)

import pywinauto
import pywinauto.clipboard

from easytrader import exceptions
#from . import helpers
#from .clienttrader import ClientTrader
from easytrader.log import log
import pandas as pd

from winguiauto import dumpWindow,clickButton#,click,activeWindow


def close_yingyebu_gonggao(key_text='营业部公告',click_text='确定',interval=0.2):
    """
      关闭弹出的对话窗口
    :param key_text: 关键字句柄标题，字符串
    :param click_text: 同级句柄标题，需要点击的按钮确定或者取消按钮， 字符串
    """
    all_dialog_hwnd = dumpWindow(hwnd=0, wantedText=None, wantedClass='#32770')
    print('all_dialog_hwnd=',all_dialog_hwnd)
    for subwin in all_dialog_hwnd:
        sub_win_hwnd = subwin[0]
        sub_gonggao=dumpWindow(sub_win_hwnd, wantedText=key_text)#, wantedClass='Static')
        if sub_gonggao:
            sub_confgirm=dumpWindow(sub_win_hwnd, wantedText=click_text)#0038736, wantedClass='Button')
            print('sub_confgirm=',sub_confgirm)
            confirm_hwnd = sub_confgirm[0][0]
            print('confirm_hwnd=',confirm_hwnd)
            clickButton(confirm_hwnd)
            #click(sub_confgirm[0][0])
            time.sleep(interval)
            return confirm_hwnd
    return -1
    

def trader(trade_api='shuangzixing',bebug=True):
    if trade_api=='haiwangxing':
        return  OperationTdx()
    elif trade_api=='shuangzixing':
        return OperationSZX()
    else:
        print('No %s API. Please input right trade API' % trade_api)


class OperationSZX(YHClientTrader):
    """
    """
    """
    def __init__(self,debug=False):
       
        self.debug = debug
        self.init_hwnd()
    """
    debug=False

    def enable_debug(self,debug=True):
        self.debug=debug
    """        
    def init_hwnd(self,user='331600036005', password='821853',exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        self.prepare(user=user, password=password,exe_path=exe_path)

        return
    """
    
    #def exit(self):
    """
        退出交易api
    """
        #return
    def auto_ipo(self):
        #self._switch_left_menus(['新股申购', '一键打新'])
        self._switch_left_menus(['新股申购', '批量新股申购'])
        #self._click(self._config.AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID)
        self._click(1007)#点击重填
        #self._click(1098)#点击全部选中
        time.sleep(0.5)
        self._click(self._config.AUTO_IPO_BUTTON_CONTROL_ID)#点击全一键打新
        time.sleep(0.5)

        return self._handle_auto_ipo_pop_dialog()
    
    def _handle_auto_ipo_pop_dialog(self):
        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            try:
                title = self._get_pop_dialog_title()
            except:
                log.warning('今日可能没有新股申购,请复核')
                return {'message': 'unkown message: {}'}
            print('title=',title)
            if '提示信息' in title:
                self._app.top_window().type_keys('%Y')
            elif '提示' in title:
                data = self._app.top_window().Static.window_text()
                self._app.top_window()['确定'].click()
                print('data',data)
                if self._main.wrapper_object() != self._app.top_window().wrapper_object():
                    continue
                return {'message': data}
            elif '委托确认' in title:
                data = self._app.top_window().Static.window_text()
                self._app.top_window()['是(&Y)'].click()
                print('data2',data)
                print(self._main.wrapper_object())
                print(self._app.top_window().wrapper_object())
                """
                title = self._get_pop_dialog_title()
                print('title1=',title)
                if '提示' in title:
                    data = self._app.top_window().Static.window_text()
                    self._app.top_window()['确定'].click()
                    print('data',data)
                if self._main.wrapper_object() != self._app.top_window().wrapper_object():
                    continue
                print('data21',data)
                """
                log.warning('完成今日新股申购,请复核')
                return {'message': data}
            
            else:
                data = self._app.top_window().Static.window_text()
                self._app.top_window().close()
                print('data1',data)
                return {'message': 'unkown message: {}'.find(data)}
            self._wait(0.1)
    
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
    
    def prepare(self, config_path=None, user=None, password=None, exe_path=None, comm_password=None,
                **kwargs):
        """
        登陆客户端
        :param config_path: 登陆配置文件，跟参数登陆方式二选一
        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 r'C:\\htzqzyb2\\xiadan.exe', 默认 r'C:\\htzqzyb2\\xiadan.exe'
        :param comm_password: 通讯密码
        :return:
        """
        if config_path is not None:
            account = helpers.file2dict(config_path)
            user = account['user']
            password = account['password']
        try:
            self.login(user, password, exe_path or self._config.DEFAULT_EXE_PATH, comm_password, **kwargs)
        except:#尝试两次login
            self.login(user, password, exe_path or self._config.DEFAULT_EXE_PATH, comm_password, **kwargs)
            
    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        登陆客户端
        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 r'C:\中国银河证券双子星3.2\Binarystar.exe', 默认 r'C:\中国银河证券双子星3.2\Binarystar.exe'
        :param comm_password: 通讯密码, 华泰需要，可不设
        :return:
        """
        #print('self._config=',self._config)
        try:
            self._app = pywinauto.Application().connect(path=self._run_exe_path(exe_path), timeout=1)
        except Exception:
            self._app = pywinauto.Application().start(exe_path)

            # wait login window ready
            while True:
                try:
                    self._app.top_window().Edit1.wait('ready')
                    break
                except RuntimeError:
                    pass
            #print('self._app.top_window()=',self._app.top_window(),type(self._app.top_window()))
            self._app.top_window().Edit1.type_keys(user)
            self._app.top_window().Edit2.type_keys(password)

            while True:
                #print('self._handle_verify_code=',self._handle_verify_code())
                self._app.top_window().Edit3.type_keys(self._handle_verify_code())

                self._app.top_window()['登录'].click()
                
                # detect login is success or not
                try:
                    self._app.top_window().wait_not('exists', 2)
                    log.info('登录成功')
                    self._wait(0.2)
                    break
                except:
                    log.info('重新输入验证码，登录中...')
                    pass
                self._wait(0.5)
            close_yingyebu_gonggao(key_text='营业部公告',click_text='确定')#关闭营业部公告弹出窗口，如果有
            self._app = pywinauto.Application().connect(path=self._run_exe_path(exe_path), timeout=10)
        #self._wait(2)
        
        self._close_prompt_windows()
        self._main = self._app.top_window()
    
    

        
                        
    def __buy(self, code, quantity,actual_price,limit=None):
        """
        直接买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        if limit:
            actual_price=limit[0]  #涨停价
        #actual_price=str(actual_price)
        return self.buy(security=code, price=actual_price, amount=quantity)
        
            
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
    
    def _buy(self, code, quantity,actual_price,limit=None):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        
        available_fund=self.get_available_money()
        #if highest:
        #    actual_price=highest
        final_quantity=self._get_valid_buy_quantity(available_fund, actual_price, quantity)
        #if self.debug: print('final_buy_quantity=',final_quantity)
        if final_quantity>=100:
            return self.__buy(code, quantity,actual_price,limit)
        else:
            if self.debug: print('可用资金不足买入100股%s，取消买入下单'%code)
            return {}
    
    
        
    def __sell(self, code, quantity,actual_price,limit=None):
        """
        直接卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        if limit:
            actual_price=limit[1]  #跌停价
        #actual_price=str(actual_price)
        return self.sell(security=code, price=actual_price, amount=quantity)

    

    def _get_valid_sell_quantity(self,code,expect_quantity=None,patial=None):
        """
        卖出数量函数
        :param code: 买入股票代码 
        :param expect_quantity: 期望卖出数量
        :param patial: 使用资金比例，如0.75,，0.5,0.33，0.25,0.10
        """
        all_holding,available_position=self.get_stock_position(code)
        if patial!=None and patial>0 and patial<=1.0:
            available_position=available_position*patial
        mini_quantity=100
        max_valid_quantity=int(available_position//mini_quantity)*mini_quantity
        acceptable_quantity=max_valid_quantity
        if expect_quantity:
            expect_quantity=int(expect_quantity)
            acceptable_quantity=int(expect_quantity//mini_quantity)*mini_quantity
        final_quantity=min(max_valid_quantity,acceptable_quantity)
        #if self.debug: print('final_sell_quantity=',final_quantity,type(final_quantity))
        return final_quantity
    
    def _sell(self, code, quantity,actual_price,limit=None):
        """
        卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        quantity=self._get_valid_sell_quantity(code, quantity)
        if quantity>=100:
            return self.__sell(code, quantity,actual_price,limit=limit)  #{'entrust_no': entrust_no}{'entrust_no': entrust_no}
        else:
            if self.debug: print('不满100股%s，取消卖出下单'%code)
            return {}

    def order(self, code, direction, quantity,actual_price,limit_price=None,post_confirm_interval=0,check_valid_time=True):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向
        :param quantity: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        :param actual_price: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        :param limit_price: [涨停价,跌停价]
        :param post_confirm_interval: 延时确认交易结果的时间，秒，int，0秒表示不确认交易结果
        :param check_valid_time, 是否检查当前是有效的交易时间
        reurn: 如果成功下单，返回下单委托号字典，否认返回空字典
        """
        #highest=None
        #lowest=None
        #if limit_price and len(limit_price)>=2:
        #    highest=limit_price[0]
        #    lowest=limit_price[1]
        # restoreFocusWindow(self.__top_hwnd)
        entrust_no_dict = {}  
        if not is_trade_time_now() and check_valid_time:
            print('非交易时间，不允许下单')
            return entrust_no_dict
        pre_position = {}
        if post_confirm_interval:
            pre_position = self.get_my_position()
        if quantity<=0:#invalid quantity
            if self.debug: print('Please input valid quantity!')
            return
        trade_num = quantity
        
        if direction.lower()=='b':
            entrust_no_dict = self._buy(code, quantity,actual_price,limit_price)
        if direction.lower()=='s':
            trade_num = -1*quantity
            entrust_no_dict =self._sell(code, quantity,actual_price,limit_price)
        #if self.debug: print('self.__top_hwnd=',self.__top_hwnd)
        close_yingyebu_gonggao(key_text='提示',click_text='确定',interval=0.2)
        if post_confirm_interval:
            self.post_trade_confirm(code,plan_trade_num=trade_num,pre_position=pre_position,interval=post_confirm_interval)
        return entrust_no_dict
    
    def post_trade_confirm(self,code,plan_trade_num,pre_position,interval=60):
        time.sleep(interval)
        post_position = self.get_my_position()
        pos_chg = self.get_postion_change(pre_position,post_position)
        #if self.debug: print('pos_chg=',pos_chg)
        self.trade_confirm(code, plan_trade_num, pos_chg)

    def maximizeFocusWindow(self):
        """
        最大化窗口，获取焦点
        """
       
    def minimizeWindow(self):
        """
        最小化窗体
        """
       

    def clickRefreshButton(self, t=0.3):
        """点击刷新按钮
        """
        #clickWindow(self.__menu_hwnds[0][0], self.__button['refresh'])
        #self.get_available_money()
        """点击'关联同一只股票'按钮
        """
        #click(self.__buy_sell_hwnds[49][0])
        #time.sleep(t)
        #click(self.__buy_sell_hwnds[49][0])
        #time.sleep(t)
        #print('refresh_hwnd=',self.__buy_sell_hwnds[49][0])
        #print(datetime.datetime.now())

    def get_available_money(self):
        """获取可用资金
        """
        money=0.0
        try:
            money = self.balance[0]['可用金额']
            money=float(money)
        except:
            money=0.0
            sm.send_mail(sub='获取可用资金失败',content='检查验证是否软件异常' )
        if self.debug: print('可用资金=',money)
        return money
    
    """
    def getPosition(self):
        
        return self.position
    """
    
        
    def is_right_acc(self,acc='36005',position=list()):
        """确认是否正确账号
        return bool
        """
        acount_dict = {'0130010635':'36005','A732980330':'36005','A355519785':'38736','0148358729':'38736'}
        pos_list =[]
        if position:
            pos_list =position
        else:
            pos_list = self.position
        #print('pos_list=',pos_list)
        right_acc = False
        if pos_list:
            stock_owner = pos_list[0][12]
            if stock_owner in list(acount_dict.keys()):
                right_acc = acc==acount_dict[stock_owner]
        return right_acc
    
    def get_account_money(self,acc='36005'):
        """获取账户持仓
        return 市值，可用资金
        """
        pos_list = self.position
        market_value = 0.0
        available_money = 0.0
        if self.is_right_acc(acc, pos_list):
            available_money = self.get_available_money()
        else:
            current_acc_id,current_box_id = self.get_acc_combobox_id()
            position_dict = self.get_my_position() 
            exchange_id = self.change_account(current_acc_id, current_box_id, position_dict)
            pos_list = self.position
            if self.is_right_acc(acc, pos_list):
                available_money = self.get_available_money()
            else:
                return market_value,available_money
        if pos_list:
            for stock_data in pos_list:
                market_value = market_value + float(stock_data[9])  #9 for '参考市值'
        return market_value,available_money
    
    
    """
    def get_position_dict(self):
        #单账户
        #print('111')
        pos_dict = {}
        my_pos = {}
        pos = self.position
        if not pos:
            return {}
        for stock in pos:
            stock_code = int_code_to_stock_symbol(stock['证券代码'])
            stock['证券代码'] = stock_code
            pos_dict[stock_code] = stock
        #my_pos[self.get_acc_id()] = pos_dict 
        return pos_dict
    """
    
    def get_stock_position(self,code):
        """获取持仓股票信息
        return 持仓数量，可卖数量
        """
        #POSITION_COlS = 14 
        #position_dict = getDictViewInfo(self.__buy_sell_hwnds[-4][0], POSITION_COlS)
        position_dict = self.get_my_position()
        #print('position_dict=',position_dict)
        hold_num = 0
        available_to_sell =0
        if not position_dict:
            log.info('当前空仓或者提取仓位数据错误,请手动确认！！')
            return 0,0
        if code in list(position_dict.keys()):
            hold_num = position_dict[code]['当前持仓']
            #print('hold_num=',hold_num)
            available_to_sell = position_dict[code]['可用余额']
            #print('available_to_sell=',available_to_sell)
        else:
            log.info('当前账号无股票%s的持仓'%code)
        return hold_num,available_to_sell
    
    def get_postion_change(self,pre_position,post_position):
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
        #if self.debug: print('pos_chg= ', pos_chg)
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
            if self.debug: print('请手动确认股票  %s交易是否成功 !'% code)
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
        
    def is_right_acc(self,acc_id):
        #this_acc_id,combobox_id = self.get_acc_combobox_id()
        """
        wantedtext = VA[LI[0]]['A1']
        if acc_id==LI[0]:
            pass
        elif acc_id==LI[1]:
            wantedtext = VA[LI[1]]['A1']
        else:
            return False
        hnwd = get_exist_hwnd(self.trade_main_hwnd, wantedtext)
        """
        return self.acc_id==acc_id
    
    def get_acc_id(self):
        """
        valid_acc_ids = LI
        acc_id = 0
        for acc_id in valid_acc_ids:
            if self.is_right_acc(acc_id):
                return acc_id
            else:
                pass
        this_acc_id,combobox_id = self.get_acc_combobox_id()
        """
        return self.acc_id
    
    def update_acc_id(self):
        this_acc_id,combobox_id = self.get_acc_combobox_id()
        self.acc_id = this_acc_id
        
    def get_acc_combobox_id(self,position_dict={},acc_combobox_map = {'36005':0,'38736':1}):
        """
        双帐号切换: 获取当前账号的id，和combobox_id
        """
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
    
    def change_acc(self,acc_id='',exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        #trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #is_acc = self.is_acc_36005()
        #acc_id = self.update_acc_id()
        #acc_dict = {'36005':'331600036005','38736':'331600038736'}
        #changed = False
        pre_acc_id = self.acc_id
        changed_acc = False
        if acc_id:#指定切换的acc_id
            #self.logout()
            if self.is_right_acc(acc_id):
                print('正确的acc_id=%s，无需切换'%acc_id)
                pass
            else:
                if acc_id==LI[0]:
                    #changed = True
                    self.exit()
                    log.info('切换到 ACC=: %s' % acc_id)
                    #self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'],exe_path=exe_path)  
                    self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'], exe_path=exe_path)
                    #self.acc_id = LI[1]
                    changed_acc = True
                elif acc_id==LI[1]:
                    #changed = True
                    self.exit()
                    log.info('切换到 ACC=: %s' % acc_id)
                    #self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'],exe_path=exe_path)
                    self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'], exe_path=exe_path)
                    #self.acc_id = LI[0]  
                    changed_acc = True
                else:
                    log.warning('给定无效acc_id=%s' % acc_id)
        else:
            if pre_acc_id==LI[0]:
                #changed = True
                self.exit()
                log.info('切换到 ACC=: %s' % LI[1])
                #print('Will change to ACC: ',LI[1])
                #self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'],exe_path=exe_path)  
                self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'], exe_path=exe_path)
                #self.acc_id = LI[1]
                changed_acc = True
            elif pre_acc_id==LI[1]:
                #changed = True
                self.exit()
                log.info('切换到 ACC=: %s' % LI[0])
                #print('Will change to ACC: ',LI[0])
                #self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'],exe_path=exe_path)
                self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'], exe_path=exe_path)
                #self.acc_id = LI[0]  
                changed_acc = True
            else:
                log.warning('未在配置文件预定acc_id')  
        if changed_acc:
            self.update_acc_id()
        return changed_acc
    
    def get_all_position(self):
        pos_dict = dict()
        pos_dict[self.get_acc_id()] = self.get_my_position()
        self.change_acc()
        pos_dict[self.get_acc_id()] = self.get_my_position()
        return pos_dict
    
    
    def get_my_position(self):
        #单账户
        #print('111')
        pos_dict = {}
        pos = self.position
        if not pos:
            return {}
        for stock in pos:
            stock_code = int_code_to_stock_symbol(stock['证券代码'])
            stock['证券代码'] = stock_code
            pos_dict[stock_code] = stock
        return pos_dict
    
    def order_acc_stock(self,acc_id,stock_code, price, amount,direct='S',
                        is_absolute_order=False,limit_price=None,confirm=True):
        """
        For single account
        
        limit_price: list type,  跌停价卖，涨停价买,[涨停价,跌停价]
        """
        #if is_absolute_order and limit_price: #跌停价卖，涨停价买
        #        price = limit_price
                
        if acc_id and acc_id==self.acc_id:
            pass
        else:
            self.change_acc()
            if acc_id and acc_id==self.acc_id:
                pass
            else:
                print('无效acc id')
                return {}
        return self.order(code, direction, quantity,actual_price,limit_price=limit_price,post_confirm=confirm)
    
    def change_to_valid_acc(self,acc_id):
        if self.is_right_acc(acc_id):
            pass
        else:
            self.change_acc()
            if self.is_right_acc(acc_id):
                pass
            else:
                print('无效acc_id')
                return False
        return True
    
    def is_holding_stock(self,acc_id,stock):
        #is_valid_acc = self.change_to_valid_acc(acc_id)
        if not self.change_to_valid_acc(acc_id):
            return False
        this_acc_positon = self.position
        print('this_acc_positon=',this_acc_positon)
        for pos in this_acc_positon:
            code = pos['证券代码']
            symbol = int_code_to_stock_symbol(code)
            if stock==symbol:
                return True
        return False
    
    def exchange_stocks(self,acc_id,position, replaced_stock,replaced_stock_price, target_stock,
                         target_stock_price,sell_then_buy=True,exchange_rate=1.0,absolute_order=False):
        
        if self.is_holding_stock(acc_id, replaced_stock):
            pass
        else:
            log.warning('There is not stock %s in this account %s ' % (replaced_stock,acc_id))
            return False
        available_money = self.get_available_money()
        sleep_seconds = 1
        print(position[acc_id][replaced_stock]['可用余额'])
        replaced_stock_amount = int((position[acc_id][replaced_stock]['可用余额'] * exchange_rate//100) * 100)
        target_stock_amount = int((replaced_stock_amount*replaced_stock_price/target_stock_price//100)*100)
        if sell_then_buy and replaced_stock_amount>100 and target_stock_amount>100:#先卖后买
            print('Plan to sell %s %s, and then buy %s %s' % (replaced_stock_amount,replaced_stock,target_stock_amount,target_stock))
            sell_replace_stock = self.order_acc_stock(acc_id,replaced_stock, replaced_stock_price, 
                    replaced_stock_amount, direct='S', is_absolute_order=absolute_order, limit_price=None)
            time.sleep(sleep_seconds)
            if sell_replace_stock:
                buy_target_stock = self.order_acc_stock(target_stock, target_stock_price, 
                    target_stock_amount, acc_id, direct='B', is_absolute_order=absolute_order, limit_price=None)
                print('Completed exchange order: sell then buy')
                return buy_target_stock
            else:
                return False
        elif not sell_then_buy and replaced_stock_amount>100 and target_stock_amount>100: #先买后卖
            print('Plan to buy %s %s, and then sell %s %s' % (target_stock_amount,target_stock,replaced_stock_amount,replaced_stock))
            if available_money>target_stock_amount*target_stock_price:
                buy_target_stock = self.order_acc_stock(target_stock, target_stock_price, 
                    target_stock_amount, acc_id, direct='B', is_absolute_order=absolute_order, limit_price=None)
                time.sleep(sleep_seconds)
                if buy_target_stock:
                    sell_replace_stock = self.order_acc_stock(replaced_stock, replaced_stock_price, 
                    replaced_stock_amount, acc_id, direct='S', is_absolute_order=absolute_order, limit_price=None)
                    print('Completed exchange order: sell then buy')
                    return replaced_stock
            else:
                return False
        else:
            log.warning('试图调股换仓, 但是失败！！ ')
            return False
    
    def get_stock_exit_datas(self,position):
        return
    
    def get_stock_buy_datas(self,position,avaiable_money):
        return
    
    def order_acc_stocks(self,stock_order_datas,direct='S'):
        """
        For multi-account
        
        stock_order_datas = {'12345':[
        [stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],],
        '12346':[[stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],]}
        """
        def get_stock_order_price(stock):
            #stock=[stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price]
            direction =stock[3]
            is_absolute_order = stock[4]
            price = stock[1]
            if is_absolute_order and direction=='B':
                price = stock[5]
            elif is_absolute_order and direction=='S':
                price = stock[6]
            else:
                pass
            return price,direction
        order_num = 0
        if self.enable_trade:
            pass
        else:
            return order_num
        acc_ids = list(stock_order_datas.keys())
        valid_acc_ids = list(set(LI).intersection(set(acc_ids)))
        if len(valid_acc_ids)==1:
            if self.is_right_acc(valid_acc_ids[0]):
                pass
            else:
                self.change_acc()
            for stock in stock_order_datas[valid_acc_ids[0]]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock[0], price, stock[2],direct)
                order_num = order_num + 1
        elif len(valid_acc_ids)==2:
            this_acc_id = self.get_acc_id()
            for stock in stock_order_datas[this_acc_id]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock[0], price, stock[2],direct)
                order_num = order_num + 1
            valid_acc_ids.pop(valid_acc_ids.index(this_acc_id))
            second_acc_id = valid_acc_ids[0]
            self.change_acc()
            for stock1 in stock_order_datas[second_acc_id]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock1[0], price, stock1[2],direct)
                order_num = order_num + 1
        else:
            order_num = -1
        return order_num    
    
    
    
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
    
    
    def _handle_cancel_gonggao_dialog(self):
        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            title = self._get_pop_dialog_title()
            if '营业部公告' in title:
                self._app.top_window().type_keys('%Y')
            elif '提示' in title:
                data = self._app.top_window().Static.window_text()
                self._app.top_window()['确定'].click()
                return {'message': data}
            else:
                data = self._app.top_window().Static.window_text()
                self._app.top_window().close()
                return {'message': 'unkown message: {}'.find(data)}
            self._wait(0.2)
    
    
    #@functools.lru_cache()
    def _get_left_menus_handle(self):
        while True:
            try:
                handle = self._app.top_window().window(
                    control_id=129,
                    class_name='SysTreeView32'
                )
                # sometime can't find handle ready, must retry
                handle.wait('ready', 2)
                return handle
            except:
                pass
            
    def _get_grid_data(self, control_id):
        grid = self._app.top_window().window(
            control_id=control_id,
            class_name='CVirtualGridCtrl'
        )
        grid.type_keys('^A^C')
        return self._get_clipboard_data()
            
    def _get_clipboard_data(self):
        n=0
        while n<1000000:
            try:
                
                #print(type(pywinauto.clipboard.GetData()))
                #print(pywinauto.clipboard.GetData())#[:-30])
                #print(str(pywinauto.clipboard.GetData()).split('\n'))
                #try:
                    #return pywinauto.clipboard.GetData()
                #except:
                data = pywinauto.clipboard.GetData()
                #print(io.StringIO(data[:n*(-1)]))
                df = pd.read_csv(io.StringIO(data[:n*(-1)]),delimiter='\t',dtype=self._config.GRID_DTYPE,na_filter=False,encoding='utf-8')
                                 #error_bad_lines=True,
                                 #encoding='utf-8',
                return df.to_dict('records')
                #return pywinauto.clipboard.GetData()[:-30]
            
            except Exception as e:
                if n<100:
                    log.warning('{}, retry ......'.format(e))
                else:
                    pass
                n=n+10
        return {}
                
    def _format_grid_data(self, data):
        print(io.StringIO(data))
        df = pd.read_csv(io.StringIO(data),delimiter='\t',dtype=self._config.GRID_DTYPE,na_filter=False,encoding='utf-8')
                         #error_bad_lines=True,
                         #encoding='utf-8',
        return df.to_dict('records')
                
    def get_realtime_holding(self):
        total_money=self.get_available_money()
        position_dict=self.position  #may error
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
    
    

def int_code_to_stock_symbol(code):
    """
    code, int type
    """
    return '0'*(6-len(str(code)))+str(code)

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

def set_terminate_profit(limit=9.8):
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
    terminate_rate=limit
    if hour<10:
        return limit
    elif (hour==10 and minute<=30):
        terminate_rate=limit*0.618
    elif hour<11 or (hour==11 and minute<=30):
        
        terminate_rate=limit*0.382
    elif hour<14:
        terminate_rate=limit*0.618
    elif hour<15:
        terminate_rate=2.0
    else:
        terminate_rate=10.0
    
    return terminate_rate


    
