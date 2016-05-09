# coding: utf-8
from easytrader import *
import easyquotation
import time
import pandas as pd
log = helpers.get_logger(__file__)


class MyTrader(YHTrader):
    
    def set_account_config(self,account_dict):
        self.account_config = account_dict
        
    def prepare(self, need_data):
        """登录的统一接口
        :param need_data 登录所需数据, str type or dict type"""
        if isinstance(need_data, dict):
            self.set_account_config(need_data)
        else:
            self.read_config(need_data)
        self.autologin()
        
    def list2dict(self,list_nesting_dict):
        """嵌套着字典的 list 转化为字典 """
        this_dict={}
        for ls in list_nesting_dict:
            this_dict.update(ls)
        return this_dict
  
    def get_balance(self):
        """获取账户资金状况"""
        #return self.do(self.config['balance'])
        balance_list=self.do(self.config['balance'])
        #print(balance_list)
        if balance_list:
            return balance_list[0]
        else:
            return {}

    def get_position(self):
        """获取持仓"""
        #return self.do(self.config['position'])
        column_list=['盈亏比例(%)', '参考市值', '证券名称', '买入冻结', '当前持仓', '卖出冻结', '股东代码', '交易市场', '参考市价', '证券代码', '股份可用', '参考成本价', '股份余额', '参考盈亏']
        pos_data={}
        pos_df=pd.DataFrame(pos_data,columns=column_list)
        position_list=self.do(self.config['position'])
        if position_list:
            if isinstance(position_list[0], dict):
                column_list=list(position_list[0].keys())
            pos_df=pd.DataFrame(data=position_list,columns=column_list)
        """
        pd_data={}
        atr_df=pd.DataFrame(df_data,columns=column_list)
        atr_min_df=atr_min_df.append(atr_df,ignore_index=True)
        print(column_list)
        print(position_list)
        position_dict={}
        for pos in position_list:
            absolute_loss=pos[7]['参考盈亏']
            absolute_loss_v=absolute_loss[(absolute_loss.find('>')+1):-7]
            pos[7]['参考盈亏']=absolute_loss_v
            absolute_loss_rate=pos[8]['盈亏比例(%)']
            absolute_loss_rate_v=absolute_loss_rate[(absolute_loss_rate.find('>')+1):-7]
            #print('absolute_loss_rate_v=',absolute_loss_rate_v)
            pos[8]['盈亏比例(%)']=absolute_loss_rate_v
            symbole_dict=pos.pop(1)
            position_dict[symbole_dict['证券代码']]=self.list2dict(pos)
        return position_dict
        """
        #print(pos_df)
        return pos_df 
        
    def sell_to_exit(self, stock_code, exit_price, last_close,realtime_price,exit_type=0,exit_rate=0,delay=0):
        """止损止盈 卖出股票
        :param stock_code: 股票代码
        :param exit_price: 止损卖出价格
        :param exit_type: 0, 止损退出；1,止盈退出
        :param exit_rate: 止损比例 ,若不指定，全部退出
        :param delay: 延时止损,秒 
        """
        if stock_code not in self.position.keys():
            return
        exit_amount=int(self.position[stock_code]['股份可用'])
        if exit_rate and exit_rate<1 and exit_rate>0 and exit_amount!=100:
            exit_amount=int(exit_amount*exit_rate/100)*100
        if exit_amount==0:
            return
        lowest_price=round(last_close*0.9,2)
        highest_price=round(last_close*1.1,2)
        if exit_price<lowest_price or exit_price>highest_price:
            return
        this_timestamp=time.time()
        if exit_type==0:#止损
            if realtime_price<exit_price:
                if delay==0:#即时止损
                    log.debug('股票  %s 达到止损价格 : %s,立即止损退出  %s股' % (stock_code,exit_price,amount))
                    self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                else:
                    if self.time_stamp['exit_l'] ==0:#第一次达到止损价格
                        self.time_stamp['exit_l']=this_timestamp
                        log.debug('股票  %s 达到止损价格 : %s,延时  %秒' % (stock_code,exit_price,delay))
                    else:
                        if (this_timestamp-self.time_stamp['exit_l'])>delay:#延时确认止损
                            log.debug('股票  %s 达到止损价格 : %s,延时%s秒，止损退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                            self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                            self.time_stamp['exit_l'] =0
                        elif (this_timestamp-self.time_stamp['exit_l'])<=delay*0.5:
                            if realtime_price<=(exit_price-0.6*(exit_price-lowest_price)):#快速下跌
                                log.debug('股票  %s 达到止损价格 : %s,延时%s秒,但快速下跌，故止损退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                                self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                                self.time_stamp['exit_l'] =0
                            else:
                                pass
                        else:
                            pass
            elif realtime_price>exit_price*1.013:
                if delay and self.time_stamp['exit_l']!=0:
                    if (this_timestamp-self.time_stamp['exit_l'])<=delay*0.5:#下探止损价格后，快速回升在止损价格之上
                        self.time_stamp['exit_l'] =0
                    else:
                        pass
            else:
                pass
        elif exit_type==1:#止盈
            if delay==0:#即时止盈
                if realtime_price>=exit_price:
                    log.debug('股票  %s 达到止盈价格 : %s,立即止盈退出  %s股' % (stock_code,exit_price,amount))
                    self.sell(stock_code, price=exit_price, amount=exit_amount, volume=0, entrust_prop=0)
                else:
                    pass
            else:
                if self.time_stamp['exit_h'] ==0:
                    if realtime_price>=exit_price:
                        self.time_stamp['exit_h']=this_timestamp
                        log.debug('股票  %s 第一次 达到止盈价格 : %s,延时  %秒' % (stock_code,exit_price,delay))
                    else:
                        pass
                else:
                    if realtime_price>=(exit_price+0.6*(highest_price-exit_price)):#突破止盈价格后，快速强势，重新延时止盈
                        if (this_timestamp-self.time_stamp['exit_h'])<delay*0.5:
                            #log.debug('股票  %s 达到止损价格 : %s,延时%s秒,但快速下跌，故止损退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                            self.time_stamp['exit_h'] =this_timestamp
                            exit_price=exit_price+0.6*(highest_price-exit_price)
                        else:
                            pass
                    elif realtime_price>=exit_price:
                        if (this_timestamp-self.time_stamp['exit_h'])>delay:#突破止盈价格后，长时间强势，重新延时止盈
                            self.time_stamp['exit_h']=this_timestamp
                        else:
                            pass
                    else:
                        if (this_timestamp-self.time_stamp['exit_h'])<0.5*delay:
                            if realtime_price<=exit_price*0.97:#突破止盈价格后，快速强势，重新延时止盈
                                log.debug('股票  %s 达到止盈价格 : %s,尝试延时%s秒,但短时快速下跌，故止盈退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                                self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                                self.time_stamp['exit_h'] =0
                            else:
                                pass
                        elif (this_timestamp-self.time_stamp['exit_h'])<delay:
                            if realtime_price<=exit_price*0.95:#突破止盈价格后，快速强势，重新延时止盈
                                log.debug('股票  %s 达到止盈价格 : %s后在%s秒内出现大幅下跌，故止盈退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                                self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                                self.time_stamp['exit_h'] =0
                            else:
                                pass
                        else:
                            log.debug('股票  %s 达到止盈价格 : %s,延时%s秒后回落，故止盈退出  %s股' % (stock_code,exit_price,delay,exit_amount))
                            self.sell(stock_code, price=lowest_price, amount=exit_amount, volume=0, entrust_prop=0)
                            self.time_stamp['exit_h'] =0
        else:
            pass
    
    
    def sell_all_to_exit_now(self,sell_rate=0,set_time=None):
        """一键即时清仓
        :param sell_rate: 卖出比例
        :param set_time: 卖出时间
        """
        if self.position:
            if set_time==None: 
                log.debug('一键即时卖出股票 ： %s, 比例:%s' % (self.position.keys(),'清仓' if sell_rate==0 else sell_rate))
            else:
                log.debug('一键定时卖出股票：  %s, 比例:%s' % (self.position.keys(),'清仓' if sell_rate==0 else sell_rate))
            for stock_code in self.position.keys():
                self.sell_stock_by_time(stock_code, sell_rate, set_time)
                time.sleep(5)
        else:
            pass
        return
    
    
    def sell_stock_by_low(self,stock_code,exit_price,realtime_price,sell_rate=0,delay=True,set_time=None,time_type='later'):
        """定价止损推出
        :param stock_code: 股票代码
        :param exit_price: 推出价格
        :param realtime_price: 实时价格
        :param sell_rate: 卖出比例
        :param set_time: 卖出时间
        :param delay: 是否认已经延时
        """
        if realtime_price<exit_price and delay:
            self.sell_stock_by_time(stock_code, sell_rate,set_time,time_type)
        else:
            pass
        return
    
        
    def buy_stock_by_high(self,stock_code,high_price,realtime_price,buy_rate=0,delay=True,set_time=None,time_type='later'):
        """定价追高买入某只股票
        :param stock_code: 股票代码
        :param high_price: 追高买入价格,通常是压力位
        :param realtime_price: 实时价格
        :param buy_rate: 买入比例 
        :param set_time: 卖出时间
        :param delay: 是否认已经延时
        """
        if realtime_price>high_price and delay:
            self.buy_stock_by_time(stock_code, buy_rate,set_time,time_type)
        else:
            pass
        return
    
    def get_sell_amount(self,stock_code,sell_rate=0):
        """获取可以卖出的股份数
        :param stock_code: 股票代码
        :param sell_rate: 卖出比例，默认全卖
        :return: 返回可以卖出的数量
        """
        sell_amount = 0
        #print(self.position)
        if self.position.empty:
            log.debug('帐户空仓，无任何持仓股票')
            sell_amount = -2
        else:
            pos_df = self.position.set_index(keys='证券代码')
            avl_pos = pos_df[pos_df['股份可用']>=100]
            if  stock_code not in pos_df.index.values.tolist():#不是持仓股票
                log.debug('1无该股 %s的持仓' % stock_code)
                sell_amount = -1
            elif stock_code not in avl_pos.index.values.tolist():#不是持仓股票
                log.debug('有该股 %s的持仓，但无可卖数量' % stock_code)
                #sell_amount = -1
            else:
                avl_amount=avl_pos.loc[stock_code,'股份可用']
                if sell_rate and sell_rate<1 and sell_rate>0:
                    sell_amount=int(avl_amount*sell_rate/100)*100
                else:
                    sell_amount=avl_amount
        return sell_amount
        #return sell_amount,is_stop_trade
            
    def sell_stock_by_time(self,stock_code,sell_rate=0,set_time=None,time_type='later'):
        """定时清仓某只股票
        :param stock_code: 股票代码
        :param sell_rate: 卖出比例
        :param set_time: 卖出时间
        """
        k_data,is_stop_trade = self.get_realtime_k_data(symbol=stock_code)
        if is_stop_trade:
            log.debug('股票   %s 停牌, 无法卖出' % stock_code)
            return -2
        sell_amount=self.get_sell_amount(stock_code, sell_rate)
        if sell_amount<=0:
            return -1
        else:
            if set_time==None or (set_time!=none and time_type=='later' and datetime.datetime.now()>set_time
                                  ) or (set_time!=none and time_type=='early' and datetime.datetime.now()<set_time):
                last_close = k_data['close']
                realtime_price = k_data['now']
                bid5 = k_data['bid5']
                bid2 = k_data['bid2']
                lowest_price=round(last_close*0.9,2)
                highest_price=round(last_close*1.1,2)
                pre_holding_amount = self.get_position_info(stock_code, info_column='股份余额')
                self.sell(stock_code, lowest_price, sell_amount, volume=0, entrust_prop=0)
                #self.sell(stock_code, bid2, sell_amount, volume=0, entrust_prop=0)
                if set_time==None: 
                    log.debug('即时卖出股票   %s, 数量%s股' % (stock_code,sell_amount))
                else:
                    log.debug('定时于  %s 卖出股票  %s, 数量%s股' % (set_time,stock_code,sell_amount))
                time.sleep(10)
                trade_status = self.config_trade(stock_code, pre_holding_amount, trade_amount=sell_amount, trade_direct='S')
                return 1
            else:
                return 0
    
    def get_buy_amount(self,stock_code,buy_price=0,buy_rate=0):
        """获取可以买入的股份数
        :param stock_code: 股票代码
        :param buy_price: 买入价格
        :param buy_rate: 买入比例，对全部可用资金而言，默认全买
        """
        if '可用资金' not in self.balance.keys():
            log.debug('无法获取帐户 %s可用资金信息' % self.account_config['inputaccount'])
            return -1,{}
        a_fund=self.balance['可用资金']
        if buy_rate and buy_rate<1 and buy_rate>0:
            a_fund=a_fund*buy_rate 
        #last_close,realtime_price,volume,highest,lowest=self.get_realtime_stock(stock_code)
        k_data,is_stop_trade = self.get_realtime_k_data(symbol=stock_code)
        if is_stop_trade or not k_data:
            log.debug('股票   %s 停牌, 无法买入' % stock_code)
            return -2,k_data
        if not k_data:
            log.debug('未获得股票   %s 报价信息, 咱不买入' % stock_code)
            return -1,k_data
        last_close = k_data['close']
        ask2 = k_data['ask2']#卖贰
        ask5 = k_data['ask5']#卖五
        #bid5 = k_data['bid5']#买五
        realtime_price = k_data['now']
        lowest_price = round(last_close*0.9,2)
        highest_price = round(last_close*1.1,2)
        a_amount=0
        if a_fund<lowest_price*100:
            log.debug('可用资金不足买100股  %s，无法购买;至少尚需资金： %s' % (stock_code,(highest*100-a_fund)))
        else:
            #f_buy_price = realtime_price
            f_buy_price = ask5
            if buy_price<=lowest_price:
                f_buy_price = lowest_price
            elif buy_price>=highest_price:
                f_buy_price = highest_price
            else:
                #f_buy_price=realtime_price+0.5*(highest_price-realtime_price)
                pass
            if f_buy_price:
                a_amount=int((a_fund/f_buy_price)*0.01)*100
        return a_amount,k_data
    
    def buy_stock_by_time(self,stock_code,buy_rate=0,set_time=None,time_type='later'):
        """定时买入某只股票
        :param stock_code: 股票代码
        :param buy_rate: 买出比例，默认全买
        :param set_time: datetime type, 买入时间
        """
        a_amount,k_data=self.get_buy_amount(stock_code,buy_rate)
        if a_amount<=0:
            return -1
        if set_time==None or (set_time!=none and time_type=='later' and datetime.datetime.now()>set_time
                                  ) or (set_time!=none and time_type=='early' and datetime.datetime.now()<set_time):
            
            highest_price = round(k_data['close']*1.1,2)
            ask5 = k_data['ask5']
            ask2 = k_data['ask2']
            pre_holding_amount = self.get_position_info(stock_code, info_column='股份余额')
            self.buy(stock_code, highest_price, a_amount, volume=0, entrust_prop=0)
            #self.buy(stock_code, ask2, a_amount, volume=0, entrust_prop=0)
            if set_time==None: 
                log.debug('即时买入股票  %s, 数量%s股' % (stock_code,a_amount))
            else:
                log.debug('定时于 %s 买入股票  %s, 数量%s股' % (set_time,stock_code,a_amount))
            time.sleep(10)
            trade_status = self.config_trade(stock_code, pre_holding_amount, trade_amount=a_amount, trade_direct='B')
            return 1
        else:
            return 0
        
        
    def exchange_stock(self,stock_to_sell,stock_to_buy,sell_rate=0,buy_rate=0,sell_time=None,buy_time=None):
        """换股
        :param stock_to_sell: 已持有的股票代码
        :param stock_to_buy: 带买入的标的股票代码
        :param sell_rate: 卖出比例，默认全卖
        :param buy_rate: 买入比例，默认全买
        :param set_time: datetime type, 卖出时间
        :param buy_time: datetime type, 买入时间
        """
        sell_success = self.sell_stock_by_time(stock_to_sell, sell_rate, sell_time)
        buy_success = self.buy_stock_by_time(stock_to_buy, buy_rate, buy_time)
        if sell_success==1 and buy_success==1:
            log.debug('换股尝试下单完成，卖出股票 %s 买入股票  %s!!' % (stock_to_sell,stock_to_buy))
        else: 
            log.debug('换股尝试下单失败，试图 卖出股票 %s 买入股票  %s!!' % (stock_to_sell,stock_to_buy))
        return 
    
    def get_position_info(self, stock_code,info_column):
        """获取股份余额：剩余股份数
        :param stock_code: 股票代码
        :param info_column: 持仓列信息
        """
        column_list=['盈亏比例(%)', '参考市值', '证券名称', '买入冻结', '当前持仓', '卖出冻结', '股东代码', '交易市场', '参考市价', '证券代码', '股份可用', '参考成本价', '股份余额', '参考盈亏']
        info_column_result = 0
        if info_column not in column_list:
            log.debug('请输入正确的持仓列关键字')
            return -1
        else:
            if info_column in ['证券名称',  '股东代码', '交易市场',  '证券代码']:
                info_column_result = ''
            else:
                pass
            #print(self.position)
            if self.position.empty:
                log.debug('帐户空仓，无任何持仓股票')
                return info_column_result
            pos_df = self.position.set_index(keys='证券代码')
            if  stock_code not in pos_df.index.values.tolist():#不是持仓股票
                log.debug('2无该股 %s的持仓' % stock_code)
                return  info_column_result
            else:
                return pos_df.loc[stock_code,info_column]
        
    def config_trade(self,stock_code,pre_holding_amount,trade_amount,trade_direct='B'):
        """定时买入某只股票
        :param stock_code: 股票代码
        :param buy_rate: 买出比例，默认全买
        :param set_time: datetime type, 买入时间
        :return trade_state: float type, -2 系统异常，-1 反向操作，0实质无成交，0.5部分成交，1按计划成交，2超额成交
        """
        trade_state = 0
        #print(self.position)
        pos_holding_amount = self.get_position_info(stock_code, info_column='股份余额')
        if pos_holding_amount<0:
            log.debug('帐户空仓，无任何持仓股票')
            trade_state = -2
        else:
            if trade_direct=='B':
                if pos_holding_amount<pre_holding_amount:
                    log.debug('原计划买入 %s %s股，实质卖出%s股' % (stock_code,trade_amount,(pre_holding_amount-pos_holding_amount)))
                    trade_state = -1
                elif pos_holding_amount==pre_holding_amount:
                    log.debug('原计划买入 %s %s股，实质无任何买入' % (stock_code,trade_amount))
                    trade_state = 0
                elif pos_holding_amount<(pre_holding_amount+trade_amount):
                    log.debug('原计划买入 %s %s股，实质部分买入%s股' % (stock_code,trade_amount,(pos_holding_amount-pre_holding_amount)))
                    trade_state = 0.5
                elif pos_holding_amount==(pre_holding_amount+trade_amount):
                    log.debug('按原计划买入 %s %s股' % (stock_code,trade_amount))
                    trade_state = 1
                else:
                    log.debug('原计划买入 %s %s股，实质超额买入，共买入%s股' % (stock_code,trade_amount,(pos_holding_amount-pre_holding_amount)))
                    trade_state = 2
            elif trade_direct=='S':
                if pos_holding_amount>pre_holding_amount:
                    log.debug('原计划卖出 %s %s股，实质买入%s股' % (stock_code,trade_amount,(pos_holding_amount-pre_holding_amount)))
                    trade_state = -1
                elif pos_holding_amount==pre_holding_amount:
                    log.debug('原计划卖出 %s %s股，实质无任何卖出' % (stock_code,trade_amount))
                    trade_state = 0
                elif pos_holding_amount>(pre_holding_amount-trade_amount):
                    log.debug('原计划卖出 %s %s股，实质部分卖出%s股' % (stock_code,trade_amount,(pre_holding_amount-pos_holding_amount)))
                    trade_state = 0.5
                elif pos_holding_amount==(pre_holding_amount-trade_amount):
                    log.debug('按原计划卖出%s %s股' % (stock_code,trade_amount))
                    trade_state = 1
                else:
                    log.debug('原计划卖出 %s %s股，实质超额卖出，共卖出%s股' % (stock_code,trade_amount,(pre_holding_amount-pos_holding_amount)))
                    trade_state = 2
            else:
                trade_state = -2
        return trade_state
    
    def get_realtime_k_data(self,symbol):
        #https://github.com/shidenggui/easyquotation
        quotation=easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
        #quotation = easyquotation.use('lf') # ['leverfun', 'lf'] #免费十档行情
        index_code=['999999','399001','399002','399003','399005']
        #print(quotation.stocks(symbol))
        k_data=quotation.stocks(symbol)
        is_stop_trade = False
        if k_data:
            k_data=k_data[symbol]
            is_stop_trade = not k_data['volume'] and not k_data['high']
        """
        {'000680': {'bid4_volume': 19000, 'high': 5.76, 'bid2_volume': 119096, 'sell': 5.7, 'bid2': 5.68, 'volume': 202358001.01,
                    'ask4_volume': 143800, 'ask5_volume': 153400, 'ask1': 5.7, 'bid1_volume': 110500, 'bid3_volume': 20817, 
                    'ask3_volume': 337408, 'open': 5.41, 'ask3': 5.72, 'turnover': 36100590, 'ask2': 5.71, 'ask1_volume': 210213,
                    'ask2_volume': 217367, 'bid4': 5.66, 'ask5': 5.74, 'date': '2016-04-22', 'low': 5.37, 'time': '15:05:56', 
                    'bid3': 5.67, 'name': '山推股份', 'now': 5.69, 'ask4': 5.73, 'bid5': 5.65, 'buy': 5.69, 'bid1': 5.69, 
                    'close': 5.44, 'bid5_volume': 31000}
         }
         """
        #print('k_data=',k_data)
        return k_data,is_stop_trade
    
    
def my_trade_test():
    import datetime
    user=MyTrader()
    #user = easytrader.use('yh')
    account_dict={
        "inputaccount": "331600036005",
        "trdpwd": "F71281A2D62C4b3a8268C6453E9C42212CCC5BA9AB89CAFF4E97CC31AE0E4C48"
    }
    user.prepare(account_dict) 
    print('time0: ', datetime.datetime.now())
    #json_file='yh.json'
    #user.prepare(json_file)
    print('time1: ', datetime.datetime.now())
    account_id=user.account_config['inputaccount']
    print('account_id=',account_id)
    print('time2: ', datetime.datetime.now())
    print(user.balance)
    print('time3: ', datetime.datetime.now())
    print(user.position)
    print('time4: ', datetime.datetime.now())
    print(user.entrust)
    print('end: ', datetime.datetime.now())
    user.exchange_stock(stock_to_sell='300162', stock_to_buy='000418')
    
    
my_trade_test()