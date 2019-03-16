# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
import datetime,time,os
import tushare as ts
from pandas.io import sql
import easytrader,easyhistory
import time,os

from tradeStrategy import Stockhistory
import pdSql_common as pdsqlc
from file_config import YH_SOURCE_DATA_DIR
#ROOT_DIR='E:/work/stockAnalyze'
#ROOT_DIR="C:/中国银河证券海王星/T0002"
#ROOT_DIR="C:\work\stockAnalyze"
#RAW_HIST_DIR=YH_SOURCE_DATA_DIR
#HIST_DIR=ROOT_DIR+'/update/'
#"""
import tradeTime as tt
import sendEmail as sm
import qq_quotation as qq

"""
from . import tradeTime as tt
from . import sendEmail as sm
from . import qq_quotation as qq
"""

def form_sql(table_name,oper_type='query',select_field=None,where_condition=None,insert_field=None,update_field=None,update_value=None):
    """
    :param table_name: string type, db_name.table_name
    :param select_field: string type, like 'id,type,value'
    :param where_condition: string type, like 'field_value>50'
    :param insert_field: string type, like '(date_time,measurement_id,value)'
    :param update_field: string type, like 'value' or  '(measurement_id,value)'
    :param update_value: value or string type, like '1000' or "'normal_type'"
    :return: sql string
    
    :use example:
    :query: sql_q=form_sql(table_name='stock.account',oper_type='query',select_field='acc_name,initial',where_condition="acc_name='36005'")
    :insert: sql_insert=form_sql(table_name='stock.account',oper_type='insert',insert_field='(acc_name,initial,comm)')
    :update: sql_update=form_sql(table_name='stock.account',oper_type='update',update_field='initial',where_condition='initial=2900019000',set_value_str='29000')
    :delete: sql_delete=form_sql(table_name='stock.account',oper_type='delete',where_condition="initial=14200.0")
    """
    sql=''
    if table_name=='' or not table_name:
        return sql
    if oper_type=='query':
        field='*'
        if select_field:
            field=select_field
        condition=''
        if where_condition:
            condition=' where %s' % where_condition
        sql='select %s from %s'%(field,table_name) + condition +';'
    elif oper_type=='insert' and insert_field:
        num=len(insert_field.split(','))
        value_tail='%s,'*num
        value_tail='('+value_tail[:-1]+')'
        sql='insert into %s '% table_name +insert_field +' values'+ value_tail + ';'
    elif oper_type=='update' and where_condition and update_field:
        """
        update_value_str=str(update_value)
        if isinstance(update_value, str):
            update_value_str="'%s'"%update_value
        """
        sql='update %s set %s='%(table_name,update_field)+ update_value + ' where '+  where_condition + ';'
        """
        sql=''
        num=len(update_field.split(','))
        if num==1:
            sql='update %s set %s='%(table_name,update_field)+ update_value + ' where '+  where_condition + ';'
        elif num>1:
            value_tail='%s,'*num
            value_tail='('+value_tail[:-1]+')'
            update_sql="update test set " + update_field +value_tail + ':'
        else:
            pass
        """
    elif oper_type=='delete':
        condition=''
        if where_condition:
            condition=' where %s' % where_condition
        sql='delete from %s'%table_name + condition + ';'
    else:
        pass
    # print('%s_sql=%s'%(oper_type,sql))
    return sql

    
class StockSQL(object):
    def __init__(self,username='emsadmin',password='Ems4you',hostname='118.89.107.40',db='stock',sqlite_file='pytrader.db',sqltype='mysql', is_today_update=False): #emsadmin:Ems4you@112.74.101.126
        self.engine = None
        if sqltype=='mysql':
            self.engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8'%(username,password,hostname,db))#
        elif sqltype=='sqlite':
            self.engine = create_engine('sqlite:///' + sqlite_file + '?check_same_thread=False', echo=False)
        elif sqltype=='postgresql':
            self.engine = create_engine('postgresql://%s:%s@%s/%s' % (username,password,hostname,db))
        else:
            pass
        self.hold = {}
        self.is_today_update = is_today_update
        #self.engine.connect()
        #self.engine.close()
    def set_today_update(self,updated=True):
        self.is_today_update = updated
        
    def close(self):
        return
        
    def get_table_df(self,table,columns=None):
        """
        :param table: string type, db_name.table_name
        :param columns: lit type with string value, like: ['acc_name', 'initial']
        :return: DataFrame type
        """
        if columns:
            return pd.read_sql_table(table, self.engine, columns=columns)
        else:
            return pd.read_sql_table(table, self.engine)
            
    def insert_table(self,data_frame,table_name,is_index=False,exists='append'):
        """
        :param data_frame: DataFrame type
        :param table_name: string type, name of table
        :return: 
        """
        data_frame.to_sql(table_name, self.engine, index=is_index,if_exists=exists)#encoding='utf-8')
        return
    
    def query_data(self,table,fields=None,condition=None):
        """
        :param table: string type, db_name.table_name
        :param fields: string type, like 'id,type,value'
        :param condition: string type, like 'field_value>50'
        :return: DataFrame type
        """
        query_sql=form_sql(table_name=table, oper_type='query', select_field=fields, where_condition=condition)
        #print(query_sql)
        return pd.read_sql_query(query_sql, self.engine)
    
    def insert_data(self,table,fields,data):
        """
        :param table: string type, db_name.table_name
        :param fields: string type, like 'id,type,value'
        :param data: list type of list value, like: data=[['李5'],['黄9']]
        :return: 
        """
        fields='(' + fields +')'
        insert_sql=form_sql(table_name=table,oper_type='insert',insert_field=fields)
        sql.execute(insert_sql, self.engine, params=data)
        
    def update_data(self,table,fields,values,condition=None):
        """
        :param table: string type, db_name.table_name
        :param fields: string type, like 'value'
        :param values: string type, like:  '1000' (for value type) or "'normal'" (for string type)
        :param condition: string type, like 'field_value>50'
        :return: 
        """
        if isinstance(values, str):
            values="'%s'"%values
        update_sql=form_sql(table_name=table,oper_type='update',update_field=fields,update_value=values,where_condition=condition)
        sql.execute(update_sql,self.engine)
    
    
    def update_system_time(self,update_field,now_time_str='',time_format='%Y/%m/%d %X'):
        """
        :param update_field:string type, can be: tdx_update_time,pos_update_time,backtest_time
        :param now_time_str: string type
        :return: 
        """
        if not now_time_str:
            now_time =datetime.datetime.now()
            now_time_str = now_time.strftime(time_format)
        self.update_data(table='systime',fields=update_field,values=now_time_str,condition='id=0')
        return
        
    def write_tdx_histdata_update_time(self,now_time_str='',time_format='%Y/%m/%d %X'):
        """
        :param now_time_str: string type
        :return: 
        """
        if not now_time_str:
            now_time =datetime.datetime.now()
            now_time_str = now_time.strftime(time_format)
        self.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
        return
    
    def write_position_update_time(self,now_time_str='',time_format='%Y/%m/%d %X'):
        """
        :param now_time_str: string type
        :return: 
        """
        if not now_time_str:
            now_time =datetime.datetime.now()
            now_time_str = now_time.strftime(time_format)
        self.update_data(table='systime',fields='pos_update_time',values=now_time_str,condition='id=0')
        return
    
    def get_systime(self):
        """
        :return: dict type
        """
        #{'id': 0, 'start_sell_time': 600, 'pos_update_time': '2017/09/03 22:13:19', 
        #'start_buy_time': 840, 'tdx_update_time': '2017/09/03 22:13:19'}
        systime_df = self.query_data(table='systime')
        return systime_df.iloc[0].to_dict()
    
    def is_histdata_uptodate(self):
        latest_date_str = tt.get_latest_trade_date(date_format='%Y/%m/%d')
        last_date_str = tt.get_last_trade_date(date_format='%Y/%m/%d')
        
        latest_datetime_str = latest_date_str + ' 15:00'
        last_datetime_str = last_date_str +  ' 15:00'
        print('last_date = ',last_datetime_str)
        print('latest_date_str=',latest_datetime_str)
        systime_dict = self.get_systime()
        tdx_update_time_str = systime_dict['tdx_update_time']
        pos_update_time_str = systime_dict['pos_update_time']
        backtest_time_str = systime_dict['backtest_time']
        is_tdx_uptodate,is_pos_uptodate,is_backtest_uptodate=False,False,False
        """
        if tdx_update_time_str:
            is_tdx_uptodate = tdx_update_time_str>=latest_date_str
        if pos_update_time_str:
            is_pos_uptodate = pos_update_time_str>=latest_date_str
        
        if backtest_time_str:
            is_backtest_uptodate = backtest_time_str>=last_datetime_str
        """
        #deltatime=datetime.datetime.now()-starttime
        #print('update duration=',deltatime.days*24*3600+deltatime.seconds)
        this_day = datetime.datetime.now()
        if (this_day.hour>=0 and this_day.hour<9) or (this_day.hour==9 and this_day.minute<15):
            is_tdx_uptodate = tdx_update_time_str>latest_datetime_str
            is_pos_uptodate = pos_update_time_str>latest_datetime_str
            is_backtest_uptodate = backtest_time_str>=latest_datetime_str
        elif this_day.hour>=16:
            is_tdx_uptodate = tdx_update_time_str>=latest_datetime_str
            is_pos_uptodate = pos_update_time_str>=latest_datetime_str
            is_backtest_uptodate = backtest_time_str>=latest_datetime_str
            
        else:
            is_tdx_uptodate = tdx_update_time_str>=last_datetime_str
            is_pos_uptodate = pos_update_time_str>=last_datetime_str
            is_backtest_uptodate = backtest_time_str>=last_datetime_str
            
        return is_tdx_uptodate,is_pos_uptodate,is_backtest_uptodate,systime_dict
        
    def delete_data(self,table_name,condition=None):
        """
        :param table_name: string type, db_name.table_name
        :param condition: string type, like 'field_value>50'
        :return: 
        """
        delete_sql=form_sql(table_name=table_name,oper_type='delete',where_condition=condition)
        print('delete_sql=',delete_sql)
        sql.execute(delete_sql, self.engine)
    
    def drop_table(self,table_name):
        """
        :param table_name: string type, db_name.table_name
        :return: 
        """
        drop_sql='drop table %s' % table_name
        sql.execute(drop_sql, self.engine)
    
    def get_last_db_date(self,code_str,histdata_last_df):
        """
        :param code_str: string type, code_name
        :param histdata_last_df: dataframe type, df from table histdata
        :return:  last_date: pandas datetime, last db date
        """
        if histdata_last_df.empty:
            #print('histdata_last_df is empty')
            return None
        else:
            try:
                histdata_last_df=histdata_last_df.set_index('code')
                last_date=histdata_last_df.loc[code_str,'last_db_time']
                return last_date
            except KeyError as e:
                #print('KeyError:',e)
                return None
            
    def get_table_update_time(self):
        update_time_sql = "select TABLE_NAME,UPDATE_TIME from information_schema.TABLES where TABLE_SCHEMA='stock';"
        update_datas = pd.read_sql_query(update_time_sql, self.engine)
        update_datas = update_datas.set_index('TABLE_NAME')
        table_time = {}
        if update_datas.empty:
            pass
        else:
            for index in update_datas.index.values.tolist():
                update_time = update_datas.loc[index].UPDATE_TIME
                table_time.update({index:update_time})
        return table_time
    
    def update_one_stock(self, symbol,force_update=False):
        index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
        FIX_FACTOR = 1.0
        d_format='%Y/%m/%d'
        last_date_str = tt.get_last_trade_date(date_format=d_format)
        latest_date_str = tt.get_latest_trade_date(date_format=d_format)
        print('last_date_str=',last_date_str)
        print('latest_date_str=',latest_date_str)
        next_date_str = tt.get_next_trade_date(date_format=d_format)
        #print(next_date_str)
        quotation_date = ''
        try:
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_date = quotation_index_df.iloc[0]['date']
            #quotation_index_df = ts.get_index()
        except:
            sleep(3)
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_date = quotation_index_df.iloc[0]['date']
        print('quotation_date=',quotation_date)
        print(quotation_index_df)
        quotation_index_df['factor'] = 1.0
        quotation_index_df = quotation_index_df[['date','open','high','low','close','volume','amount','factor']]
        #quotation_index_df.iloc[0]['volume'] = 0
        #quotation_index_df.iloc[0]['amount'] = 0
        print(quotation_index_df)
        #print(quotation_index_df)
        need_to_send_mail = []
        sub = ''
        index_name = symbol
        #table_update_times = self.get_table_update_time()
        if quotation_date:
            yh_symbol = symbol
            if symbol in index_symbol_maps.keys():
                yh_symbol = index_symbol_maps[index_name]
            yh_file_name = YH_SOURCE_DATA_DIR+symbol+'.'+file_type
            #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
            yh_index_df = pd.read_csv(yh_file_name)
            yh_index_df['factor'] = FIX_FACTOR
            yh_last_date = yh_index_df.tail(1).iloc[0]['date']
            print('yh_last_date=',yh_last_date)
            print( yh_index_df)#.head(len(yh_index_df)-1))
            if True:
                #date_data = self.query_data(table=index_name,fields='date',condition="date>='%s'" % last_date_str)
                #data_len = len(date_data)
                #this_table_update_time = table_update_times[index_name]
                #print('this_table_update_time=', this_table_update_time)
                if yh_last_date<last_date_str: #no update more than two day
                    """需要手动下载银河客户端数据"""
                    print('Need to manual update %s index from YH APP! Please make suere you have sync up YH data' % index_name)
                    need_to_send_mail.append(index_name)
                    sub = '多于两天没有更新指数数据库'
                    content = '%s 数据表更新可能异常' % need_to_send_mail
                    sm.send_mail(sub,content,mail_to_list=None)
                elif yh_last_date==last_date_str: # update by last date
                    """只需要更新当天数据"""
                    yh_index_df = yh_index_df.append(quotation_index_df, ignore_index=True)
                    print(yh_index_df)
                    pass
                else:# yh_last_date>latest_date_str: #update to  latest date
                    """YH已经更新到今天，要更新盘中获取的当天数据"""
                    print(' %s index updated to %s; not need to update' % (index_name,latest_date_str))
                    if force_update:
                        print(' force update %s index' % index_name)
                        yh_index_df0 = yh_index_df.head(len(yh_index_df)-1)
                        print(yh_index_df0)
                        yh_index_df = yh_index_df0.append(quotation_index_df, ignore_index=True)
                        print(yh_index_df)
                    else:
                        pass
                yh_index_df = yh_index_df.set_index('date')
                dir='C:/hist/day/data/'
                file_name = dir+ '%s.csv' % index_name
                try:
                    os.remove(file_name)
                    print('Delete and update the csv file')
                except:
                    pass
                yh_index_df.to_csv(file_name ,encoding='utf-8')
        return yh_index_df
            
    def update_sql_index(self, index_list=['sh','sz','zxb','cyb','hs300','sh50'],force_update=False):
        index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
        FIX_FACTOR = 1.0
        scz_code_str='399001'
        zxb_code_str='399005'
        chy_code_str='399006'
        shz ='999999'
        shz_50 = '000016'
        hs_300 = '000300'
        zx_300 ='399008'
        sz_300 ='399007'
        d_format='%Y/%m/%d'
        last_date_str = tt.get_last_trade_date(date_format=d_format)
        latest_date_str = tt.get_latest_trade_date(date_format=d_format)
        print('last_date_str=',last_date_str)
        print('latest_date_str=',latest_date_str)
        #next_date_str = tt.get_next_trade_date(date_format=d_format)
        #print(next_date_str)
        try:
            quotation_index_df = qq.get_qq_quotations(['sh','sz','zxb','cyb','hs300','sh50'], ['code','date','open','high','low','close','volume','amount'])
            #quotation_index_df = ts.get_index()
        except:
            sleep(3)
            quotation_index_df = qq.get_qq_quotations(['sh','sz','zxb','cyb','hs300','sh50'], ['code','date','open','high','low','close','volume','amount'])
        #quotation_index_df[['open','high','low','close']]=quotation_index_df[['open','high','low','close']].round(2)
        #quotation_index_df['amount'] = quotation_index_df['amount']*(10**8)
        #quotation_index_df['date'] = latest_date_str
        quotation_index_df['factor'] = 1.0
        #print(quotation_index_df)
        need_to_send_mail = []
        sub = ''
        #table_update_times = self.get_table_update_time()
        for index_name in index_list:
            yh_symbol = index_symbol_maps[index_name]
            yh_file_name = YH_SOURCE_DATA_DIR+symbol+'.'+file_type
            #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
            yh_index_df = pd.read_csv(yh_file_name)
            yh_index_df['factor'] = FIX_FACTOR
            try:
                date_data = self.query_data(table=index_name,fields='date',condition="date>='%s'" % last_date_str)
                data_len = len(date_data)
                #this_table_update_time = table_update_times[index_name]
                #print('this_table_update_time=', this_table_update_time)
                if len(date_data)==0: #no update more than two day
                    """需要手动下载银河客户端数据"""
                    print('Need to manual update %s index from YH APP! Please make suere you have sync up YH data' % index_name)
                    need_to_send_mail.append(index_name)
                    sub = '多于两天没有更新指数数据库'
                    self.drop_table(table_name=index_name)
                    self.insert_table(data_frame=yh_index_df,table_name=index_name)
                elif len(date_data) == 1: # update by last date
                    """只需要更新当天数据"""
                    self.update_sql_index_today(index_name,latest_date_str,quotation_index_df,index_symbol_maps)
                    pass
                elif len(date_data) == 2: #update to  latest date
                    """要更新盘中获取的当天数据"""
                    print(' %s index updated to %s.' % (index_name,latest_date_str))
                    if force_update:
                        print(' force update %s index' % index_name)
                        self.delete_data(table_name=index_name,condition="date='%s'" % latest_date_str)
                        self.update_sql_index_today(index_name,latest_date_str,quotation_index_df,index_symbol_maps)
                        pass
                    else:
                        pass
                else:
                    pass
            #print(date_data)
            except:
                sub = '数据表不存在'
                need_to_send_mail.append(index_name)
                print('Table %s not exist.'% index_name)
                try:
                    self.drop_table(table_name=yh_index_df)
                except:
                    pass
                self.insert_table(data_frame=yh_index_df,table_name=index_name,is_index=False)
                print('Created the table %s.' % index_name)
        if need_to_send_mail:
            content = '%s 数据表更新可能异常' % need_to_send_mail
            sm.send_mail(sub,content,mail_to_list=None)
    
    def update_sql_index_today(self,index_name,latest_date_str,quotation_index_df):
        """添加今天的更新"""
        #index_sybol = index_symbol_maps[index_name]
        #if index_name=='sh':
        #   index_sybol = '000001'
        columns = ['date','open','high','low','close','volume','amount','factor']
        single_index_df = quotation_index_df[quotation_index_df['code']==index_name]
        single_index_df = single_index_df[columns]
        if single_index_df.empty:
            return
        self.insert_table(data_frame=single_index_df,table_name=index_name,is_index=False)
        
        
    def update_sql_position0(self, users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}}):
        sub = '持仓更异常'
        fail_check = []
        for account in list(users.keys()):
            #stock_sql.drop_table(table_name='myholding')
            try:
                broker = users[account]['broker']
                user_file = users[account]['json']
                position_df,balance = pdsqlc.get_position(broker, user_file)
                self.hold[account] =  position_df
                self.insert_table(data_frame=position_df,table_name='hold')
            except:
                fail_check.append(account)
            #self.insert_table(data_frame=position_df,table_name='balance')
            time.sleep(2)
        if fail_check:
            content = '%s 持仓表更新可能异常' % fail_check
            sm.send_mail(sub,content,mail_to_list=None)
            """再次尝试获取异常持仓"""
            for account in fail_check:
                #stock_sql.drop_table(table_name='myholding')
                try:
                    broker = users[account]['broker']
                    user_file = users[account]['json']
                    position_df,balance = pdsqlc.get_position(broker, user_file)
                    self.hold[account] =  position_df
                    self.insert_table(data_frame=position_df,table_name='hold')
                except:
                    pass
                #self.insert_table(data_frame=position_df,table_name='balance')
                
    def get_except_codes(self):
        #从数据库获取除外的股票代码，比如高风险或者长期持有，或者新股中签等
        except_df = self.query_data(table='stock.except',fields='code',condition='valid=1')
        return except_df['code'].values.tolist()
    
    def get_exit_monitor_stocks(self,accounts=['36005']):
        hold_df,hold_stocks,available_sells =his_sql.get_hold_stocks(accounts)
        except_codes = his_sql.get_except_codes()
        #monitor_indexs = ['sh000001','399006']
        available_sells = list(set(available_sells).difference(set(except_codes)))
        return available_sells
    
    def update_index_chooce_time(self,yh_index='999999',rate_to_confirm=0.001):
        pre_stock_trade_state = 0
        s_stock=Stockhistory(yh_index,'D',test_num=0,source='YH',rate_to_confirm=rate_to_confirm)
        result_df = s_stock.form_temp_df(yh_index)
        test_result = s_stock.regression_test(rate_to_confirm)
        last_trade_date =test_result.last_trade_date
        last_trade_price=test_result.last_trade_price
        positon=test_result.position
        print('last_trade_price=',last_trade_price)
        print('last_trade_date=',last_trade_date)
        if last_trade_price<0:
            pdsqlc.is_system_risk(indexs=['sh','cyb'],index_exit_data=pdsqlc.get_index_exit_data(['sh','cyb']))
            df = qq.get_qq_quotations_df(codes=['sh','cyb'],set_columns=['datetime','open','high','low','close','volume','amount'])
            print(df)
            pass
        else:
            pass
        
        return
    
    def update_sql_position(self, users={'account':'36005','broker':'yh','json':'yh.json'}):
        try:
        #if True:
            account_id = users['account']
            broker = users['broker']
            user_file = users['json']
            position_df,balance = pdsqlc.get_position(broker, user_file)
            except_codes = self.get_except_codes()
            except_holds = list(set(except_codes) & set(position_df['证券代码'].values.tolist()))
            """
            if except_holds:
                position_df['valid'] = np.where((position_df['证券代码']==except_holds[0]),0,1)
                except_holds.pop(0)
                for code in except_holds:
                    #position_df.loc['证券代码','valid'] = 0
                    position_df['valid'] = np.where((position_df['证券代码']==code),0,position_df['valid'])
            else:
                position_df['valid'] = 1
            """
            position_df['valid'] = 1
            for code in except_holds:
                position_df['valid'][position_df['证券代码']==code] = 0
            #df=df.tail(20)
            #df[['close']].apply(lambda x: (x - x.min()) / (x.max()-x.nin()))   
            self.hold[account_id] =  position_df
            #print(position_df)
            table_name='acc%s'%account_id
            try:
                self.drop_table(table_name)
            except:
                pass
            self.insert_table(data_frame=position_df,table_name='acc%s'%account_id)
            return
        except:
        #else:
            time.sleep(10)
            self.update_sql_position(users)
            
    def update_all_position(self,pos_df,table_name='allpositions',):
        try:
            self.drop_table(table_name)
        except:
             pass
        self.insert_table(pos_df,table_name=table_name)
        return
    
    def get_hold_stocks(self,accounts=['36005', '38736']):
        if len(accounts)<1:
            return False
        table_name='acc%s'%accounts[0]
        hold_df = self.get_table_df(table_name)
        if len(accounts)>=2:
            accounts.pop(0)
            for account in accounts:
                table_name='acc%s'%account
                next_hold_df = self.get_table_df(table_name)
                hold_df = hold_df.append(next_hold_df)
        hold_stock_all = hold_df['证券代码'].values.tolist()
        #hold_stocks = ['000932', '002362', '300431', '601009', '000007', '000932', '002405', '600570', '603398']
        hold_stocks = list(set(hold_stock_all) | set(hold_stock_all))
        #print('hold_stocks=',hold_stocks)
        #print(hold_df)
        available_sells = []
        if not hold_df.empty:
            available_sell_df = hold_df[(hold_df['valid']==1) & (hold_df['股份可用']>=100)]
            if not available_sell_df.empty:
                available_sells = available_sell_df['证券代码'].values.tolist()
        available_sells = list(set(available_sells))
        return hold_df,hold_stocks,available_sells
    
    def get_manual_holds(self,table_name='manual_holds',valid=0):
        """
        mysql -h 112.74.101.126 -u emsadmin -p    #Ems4you
        use stock;
        select * from stock.manual_holds;
        insert into stock.manual_holds (code) values('002290');
        SET SQL_SAFE_UPDATES=0;
        update stock.manual_holds set valid=0 where code='002290';
        update stock.manual_holds set name='禾盛新材'  where code='002290';
        insert into stock.manual_holds (code,name) values('002290','禾盛新材');
        """
        hold_df = self.get_table_df(table_name)
        if valid:
            hold_df = hold_df[(hold_df['valid']==1)]
        hold_stocks = hold_df['code'].values.tolist()
        hold_stocks = list(set(hold_stocks))
        return hold_stocks
    
    def get_demon_value(self,demon_type='common'):
        demon_df = self.query_data(table='demon',fields='value',condition="type='common'")
        return demon_df.tail(1).iloc[0].value
    
    def get_mailto(self):
        table='stock.mailto'
        mail_df = self.get_table_df(table)
        valid_mail_df = mail_df[(mail_df['valid']==1)]
        mailto = valid_mail_df['mail'].values.tolist()
        mailto = list(set(mailto))
        return mailtos
    
    def maillogs(self,data):
        table='stock.maillogs'
        fields = 'type,action,symbol,subject,save_time'
        self.insert_data(table, fields, data)
        return
    
    def get_dapan(self,table):
        return self.get_manual_holds(table)
     
    def get_forvary_stocks(self):
        return    
    
    def download_hist_as_csv(self,indexs = ['sh','sz','zxb','cyb','hs300','sh50'],dir='C:/hist/day/data/'):
        for index in indexs:
            index_df = self.get_table_df(table=index)
            index_df = index_df.set_index('date')
            #print(index_df)
            file_name = dir+ '%s.csv' % index
            try:
                os.remove(file_name)
                print('Delete and update the csv file')
            except:
                pass
            index_df.to_csv(file_name ,encoding='utf-8')
        return
    
    def update_last_db_date(self,code_str,last_date,update_date):
        """
        :param code_str: string type, code_name
        :param last_date: string type, last db date
        :param update_date: string type, this date 
        :return: 
        """
        if last_date:
            if update_date>last_date:
                self.update_data(table='histdata_last', fields='last_db_time', values="%s"%update_date, condition="code='%s'"%code_str)
            else:
                pass
        else:
            if update_date:
                self.insert_data(table='histdata_last', fields='code,last_db_time', data=[[code_str,update_date]])
                #print('firstly update: last_db_time',update_date)
            else:
                pass
            
    def get_exit_setting_data(self):
        """
        return example:
        {'exit_confirm_rate': 0.0025999999999999999, 'start_exit_minute': 600.0, 'key': 1.0, 'is_to_t': 0.0,
         'tolerate_loss': -0.029999999999999999, 'start_buy_minute': 870.0, 'valid': 1.0, 'is_system_risk': 0.0}

        """
        exit_setting_df = self.get_table_df('exit_setting')
        setting_dict = exit_setting_df.iloc[0].to_dict()
        return setting_dict
    
    def get_today_df(self,cols=[],is_trade_time=False):
        """
        :param cols: list type, column list
        :param is_trade_time: bool type
        :param ts: object type, 
        :return: dataframe
        """
        if self.is_today_update:
            return self.get_table_df('today', columns=cols)
        else:
            df = ts.get_today_all()
            self.insert_table(df, 'today', is_index=False,exists='replace')
            if is_trade_time:
                pass
            else:
                self.is_today_update = True
            if cols:
                return df[cols]
            return df
        
    def get_code_to_name(self,column='name'):  
        """
        :param column: string
        :return: dict
        """  
        df = self.get_today_df(cols=['code',column], is_trade_time=False)
        df = df.set_index('code')
        return df.to_dict()[column]
        
    #for chunk_df in pd.read_sql_query("SELECT * FROM today_stock", engine, chunksize=5):
    #    print(chunk_df)
"""   
stock_sql_obj=StockSQL()
setting_dict = stock_sql_obj.get_exit_setting_data() 
print(setting_dict)
"""
#stock_sql_obj.update_index_chooce_time()
def stock_sql_test():
    #mysql
    #stock_sql_obj=StockSQL()
    #sqlite3
    stock_sql_obj=StockSQL(sqlite_file='pytrader.db',sqltype='sqlite',is_today_update=False)
    d = stock_sql_obj.get_code_to_name()
    print(d)
    """
    table='today'
    df=stock_sql_obj.get_table_df(table)#, columns=['name']) 
    print('get_table_df=')
    #print(df)
    df2=stock_sql_obj.get_table_df(table, columns=['code','name']) 
    print(df2)
    df2 = df2.set_index('code')
    d = df2.to_dict()
    print('dict=',d)
    print('query_data:')
    df3=stock_sql_obj.query_data(table)
    print(df3)
    df3=stock_sql_obj.query_data(table, 'code,name', "name='格力电器'")
    print(df3)
    
    
    print('insert_data:')
    data=[['李二'],['黄三']]
    stock_sql_obj.insert_data(table, 'name', data)
    print('update_data:')
    stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    #stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    print('delete_data')
    stock_sql_obj.delete_data(table, "name='陈五'")
    """

#stock_sql_test()


    
