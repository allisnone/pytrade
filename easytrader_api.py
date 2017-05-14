# -*- coding:utf-8 -*-
import easytrader,time,datetime

# coding=utf-8
#import logging
#from .log import log
"""
from .gftrader import GFTrader
from .joinquant_follower import JoinQuantFollower
from .ricequant_follower import RiceQuantFollower


from .xq_follower import XueQiuFollower
from .xqtrader import XueQiuTrader
from .yhtrader import YHTrader
from .xczqtrader import XCZQTrader
"""
from easytrader.yh_clienttrader import YHClientTrader

import win32gui,win32con,win32api,struct
from winguiauto import (dumpWindow, dumpWindows,clickButton)
from easytrader_config0 import (HD,VA,LI)

def get_exist_hwnd(hwnd,wantedtest=''):
    windows = dumpWindows(hwnd)
    print('windows=',windows)
    wanted_hwnd = -1
    for window in windows:
        child_hwnd, window_text, window_class = window
        if window_text==wantedtest:
            wanted_hwnd = child_hwnd
            break
        else:
            pass
    return wanted_hwnd
    
        
class myYHClientTrader(YHClientTrader):
    
    def prepare(self, config_path=None, user=None, password=None, exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        """
        登陆银河客户端
        :param config_path: 银河登陆配置文件，跟参数登陆方式二选一
        :param user: 银河账号
        :param password: 银河明文密码
        :param exe_path: 银河客户端路径
        :return:
        """
        if config_path is not None:
            account = helpers.file2dict(config_path)
            user = account['user']
            password = account['password']
        self.login(user, password, exe_path)
        self.trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        
    def myposition(self):
        print('111')
        #print(self.position)
    
    def close_window(self,hwnd):#, extra):
        if hwnd and win32gui.IsWindowVisible(hwnd):
            #if 'Chrome' in win32gui.GetWindowText(hwnd):
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
        return
        
    def get_add_acc_handles(self):
        #trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 59648)  # 操作窗口框架
        tool_menu_hwnd = win32gui.GetDlgItem(self.trade_main_hwnd, 59392)  # 工具栏窗口框架
        tool_menu_hwnd_sub = dumpWindow(tool_menu_hwnd)
        add_acc_hwnd = win32gui.GetDlgItem(tool_menu_hwnd_sub[0][0], 1691)  # 工具栏添加账户按钮
        
        clickButton(add_acc_hwnd)
        new_add_acc_login_hwnd = win32gui.FindWindow(0, '用户登录')  # 交易窗口
        print('new_add_acc_login_hwnd=',new_add_acc_login_hwnd)
        return add_acc_hwnd
        """
        operate_frame_afx_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59648)  # 操作窗口框架
        hexin_hwnd = win32gui.GetDlgItem(operate_frame_afx_hwnd, 129)
        scroll_hwnd = win32gui.GetDlgItem(hexin_hwnd, 200)  # 左部折叠菜单控件
        tree_view_hwnd = win32gui.GetDlgItem(scroll_hwnd, 129)  # 左部折叠菜单控件

        # 获取委托窗口所有控件句柄
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.5)

        # 买入相关
        entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1032)  # 买入代码输入框
        self.buy_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1033)  # 买入价格输入框
        self.buy_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1034)  # 买入数量输入框
        self.buy_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1006)  # 买入确认按钮
        self.refresh_entrust_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 32790)  # 刷新持仓按钮
        entrust_frame_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1047)  # 持仓显示框架
        entrust_sub_frame_hwnd = win32gui.GetDlgItem(entrust_frame_hwnd, 200)  # 持仓显示框架
        self.position_list_hwnd = win32gui.GetDlgItem(entrust_sub_frame_hwnd, 1047)  # 持仓列表
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F2, 0)
        time.sleep(0.5)

        # 卖出相关
        sell_entrust_frame_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.sell_stock_code_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1032)  # 卖出代码输入框
        self.sell_price_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1033)  # 卖出价格输入框
        self.sell_amount_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1034)  # 卖出数量输入框
        self.sell_btn_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1006)  # 卖出确认按钮

        # 撤单窗口
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        cancel_entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 撤单窗口框架
        self.cancel_stock_code_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3348)  # 卖出代码输入框
        self.cancel_query_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3349)  # 查询代码按钮
        self.cancel_buy_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30002)  # 撤买
        self.cancel_sell_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30003)  # 撤卖

        chexin_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 1047)
        chexin_sub_hwnd = win32gui.GetDlgItem(chexin_hwnd, 200)
        self.entrust_list_hwnd = win32gui.GetDlgItem(chexin_sub_hwnd, 1047)  # 委托列表
        """
        
    def logout(self):
        #trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        self.close_window(self.trade_main_hwnd)
        print('exit trade windows')
        return 
    
    def is_right_acc(self,acc_id):
        wantedtext = VA[LI[0]]['A1']
        if acc_id==LI[0]:
            pass
        elif acc_id==LI[1]:
            wantedtext = VA[LI[1]]['A1']
        else:
            return False
        hnwd = get_exist_hwnd(self.trade_main_hwnd, wantedtext)
        return hnwd>0
    
    def get_acc_id(self):
        valid_acc_ids = LI
        acc_id = 0
        for acc_id in valid_acc_ids:
            if self.is_right_acc(acc_id):
                return acc_id
            else:
                pass
        return acc_id
    
    def change_acc(self):
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #is_acc = self.is_acc_36005()
        acc_id = self.get_acc_id()
        #acc_dict = {'36005':'331600036005','38736':'331600038736'}
        changed = False
        if trade_main_hwnd and acc_id:
            self.logout()
            if acc_id==LI[0]:
                changed = True
                print('Will change to ACC: ',LI[1])
                self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'])  
            elif acc_id==LI[1]:
                changed = True
                print('Will change to ACC: ',LI[0])
                self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'])  
            else:
                pass
        return changed
    
    def get_all_position(self):
        pos_dict = dict()
        pos_dict[self.get_acc_id()] = self.position
        self.change_acc()
        pos_dict[self.get_acc_id()] = self.position
        return pos_dict
    
    def _order_stock(self,stock_code, price, amount,direct='S'):
        if direct=='S':
            return self.sell(stock_code, price, amount)
        elif direct=='B':
            return self.buy(stock_code, price, amount)
        else:
            pass

    def order_acc_stock(self,stock_code, price, amount,acc_id=LI[0],direct='S'):
        if self.is_right_acc(acc_id):
            pass
        else:
            self.change_acc()
        return _order_stock(stock_code, price, amount,direct)
    
    def order_acc_stocks(self,stock_datas,direct='S'):
        """
        stock_datas = {'12345':[[stock_code, price, amount],],'12346':[[stock_code, price, amount],]}
        """
        acc_ids = list(stock_datas.keys())
        valid_acc_ids = list(set(LI).intersection(set(acc_ids)))
        if len(valid_acc_ids)==1:
            if self.is_right_acc(valid_acc_ids[0]):
                pass
            else:
                self.change_acc()
            for stock in stock_datas[valid_acc_ids[0]]:
                self._order_stock(stock[0], stock[1], stock[2],direct)
        elif len(valid_acc_ids)==2:
            this_acc_id = self.get_acc_id()
            for stock in stock_datas[this_acc_id]:
                self._order_stock(stock[0], stock[1], stock[2],direct)
            valid_acc_ids.pop(valid_acc_ids.index(this_acc_id))
            second_acc_id = valid_acc_ids[0]
            self.change_acc()
            for stock1 in stock_datas[second_acc_id]:
                self._order_stock(stock1[0], stock1[1], stock1[2],direct)
        else:
            pass
        return 
    
       
def use(broker, debug=True, **kwargs):
    """用于生成特定的券商对象
    :param broker:券商名支持 ['yh', 'YH', '银河'] ['gf', 'GF', '广发']
    :param debug: 控制 debug 日志的显示, 默认为 True
    :param initial_assets: [雪球参数] 控制雪球初始资金，默认为一百万
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('xq')
        >>> user.prepare('xq.json')
    """
    if not debug:
        log.setLevel(logging.INFO)
    if broker.lower() in ['yh', '银河']:
        return YHTrader(debug=debug)
    elif broker.lower() in ['yh_client', '银河客户端']:
        return myYHClientTrader()
    else:
        pass

