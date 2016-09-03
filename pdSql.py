# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
from pandas.io import sql
from pandas.lib import to_datetime
from pandas.lib import Timestamp
import datetime,time,os
import tushare as ts

import easytrader,easyhistory
import time,os
#ROOT_DIR='E:/work/stockAnalyze'
#ROOT_DIR="C:/中国银河证券海王星/T0002"
#ROOT_DIR="C:\work\stockAnalyze"
RAW_HIST_DIR="C:/中国银河证券海王星/T0002/export/"  
#HIST_DIR=ROOT_DIR+'/update/'
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


def get_raw_hist_df(code_str,latest_count=None):
    file_type='csv'
    file_name='C:/hist/day/data/'+code_str+'.'+file_type
    #print('file_name=',file_name)
    raw_column_list=['date','open','high','low','close','volume','rmb','factor']
    #print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    try:
        #print('code_str=%s'%code_str)
        #df=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312' #='gb18030')#'utf-8')   #for python3 
        hist_df = pd.read_csv(file_name)
        hist_df['rmb'] = hist_df['amount']
        #del hist_df['amount']
        #del hist_df['MA1']
        #print(hist_df)
        #print('pd.read_csv=',df)
        if hist_df.empty:
            #print('code_str=',code_str)
            return df_0
        
        return hist_df
    except OSError as e:
        #print('OSError:',e)
        return df_0

def get_yh_raw_hist_df(code_str,latest_count=None):
    file_type='csv'
    RAW_HIST_DIR="C:/中国银河证券海王星/T0002/export/"
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    raw_column_list=['date','open','high','low','close','volume','amount']
    #print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    try:
        #print('code_str=%s'%code_str)
        df=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
        #print('pd.read_csv=',df)
        if df.empty:
            #print('code_str=',code_str)
            df_0.to_csv(file_name,encoding='utf-8')
            return df_0
        #else:
        #    return
        last_date=df.tail(1).iloc[0].date
        if last_date=='数据来源:通达信':
            df=df[:-1]
            #print('数据来源:通达信')
            #print(df.tail(1).iloc[0].date)
            if df.empty:
                df_0.to_csv(file_name,encoding='utf-8')
                return df_0
            #else:
            #   return
            last_volume=df.tail(1).iloc[0].volume
            if int(last_volume)==0:
                df=df[:-1]
            df['date'].astype(Timestamp)
            df_to_write = df.set_index('date')
            df_to_write.to_csv(file_name,encoding='utf-8')
        else:
            pass
        return df
    except OSError as e:
        #print('OSError:',e)
        df_0.to_csv(file_name,encoding='utf-8')
        return df_0
    
def get_easyhistory_df(code_str,source='easyhistory'):  #ta_lib
    data_path = 'C:/hist/day/data/'
    if source=='YH' or source=='yh':
        data_path = 'C:/中国银河证券海王星/T0002/export/'
    his = easyhistory.History(dtype='D', path=data_path,type='csv',codes=[code_str])
    res = his.get_hist_indicator(code_str)
    return res


def update_one_hist(code_str,stock_sql_obj,histdata_last_df,update_db=True):
    """
    :param code_str: string type, code string_name
    :param stock_sql_obj: StockSQL type, 
    :param histdata_last_df: dataframe type, df from table histdata
    :return: 
    """
    df=get_raw_hist_df(code_str)
    if df.empty:
        return 0
    code_list=[code_str]*len(df)
    df['code']=pd.Series(code_list,index=df.index)
    p=df.pop('code')
    df.insert(0,'code',p)
    #print("update_one_hist1")
    last_db_date=stock_sql_obj.get_last_db_date(code_str,histdata_last_df)
    #print("update_one_hist2")
    last_db_date_str=''
    #print('last_db_date',last_db_date,type(last_db_date))
    #print('last_db_date_str',last_db_date_str)
    #criteria0=df.volume>0
    #df=df[df.volume>0]
    if last_db_date:
        last_db_date_str='%s' % last_db_date
        last_db_date_str=last_db_date_str[:10]
        #criteria1=df.date>last_db_date_str
        df=df[df.date>last_db_date_str]
        #print('sub df', df)
    if df.empty:
        #print('History data up-to-date for %s, no need update' % code_str)
        return 0
    if update_db:
        stock_sql_obj.insert_table(df, 'histdata')
    #print(df.tail(1))
    #print(df.tail(1).iloc[0])
    update_date=df.tail(1).iloc[0].date
    #last_date=histdata_last_df.loc[date[-1],'date']
    #update_date= 2015-11-20 <class 'str'>
    #print('update_date=',update_date,type(update_date))
    stock_sql_obj.update_last_db_date(code_str,last_db_date_str,update_date)
    return len(df)

def get_file_timestamp(file_name):
    #get last modify time of given file
    file_mt_str=''
    try:
        file_mt= time.localtime(os.stat(file_name).st_mtime)
        file_mt_str=time.strftime("%Y-%m-%d %X",file_mt)
    except:
        #file do not exist
        pass
    return file_mt_str

#get the all file source data in certain DIR
def get_dir_latest_modify_time(hist_dir,codes={}):
    """
    :param hist_dir: string type, DIR of export data
    :return: list type, code string list 
    """
    all_code=[]
    latest_time = '1970-01-01 00:00:00'
    if codes:
        for code in codes:
            full_file_name = hist_dir + '%s.csv' % code
            file_mt_str = get_file_timestamp(full_file_name)
            if file_mt_str > latest_time:
                latest_time = file_mt_str
            all_code = codes  
    else:
        for filename in os.listdir(hist_dir):#(r'ROOT_DIR+/export'):
            code=filename[:-4]
            if len(code)==6:
                all_code.append(code)
            full_file_name = hist_dir + filename
            file_mt_str = get_file_timestamp(full_file_name)
            if file_mt_str > latest_time:
                latest_time = file_mt_str
    return all_code,latest_time

#get the all file source data in certain DIR
def get_all_code(hist_dir):
    """
    :param hist_dir: string type, DIR of export data
    :return: list type, code string list 
    """
    all_code=[]
    for filename in os.listdir(hist_dir):#(r'ROOT_DIR+/export'):
        code=filename[:-4]
        if len(code)==6:
            all_code.append(code)
    return all_code

def get_different_symbols(hist_dir='C:/hist/day/data/'):
    indexs= ['cyb', 'zxb', 'sz', 'sh', 'sz300', 'zx300', 'hs300', 'sh50']
    all_codes = get_all_code(hist_dir)
    funds =[]
    b_stock = []
    for code in all_codes:
        if code.startswith('1') or code.startswith('5'):
            funds.append(code)
        elif code.startswith('9'):
            b_stock.append(code)
    except_codes = ['000029']
    all_stocks = list(set(all_codes).difference(set(funds+indexs+except_codes)))
    return indexs,funds,b_stock,all_stocks
    
def update_all_hist_data(codes,update_db=True):
    """
    :param codes: list type, code string list 
    :return: 
    """
    starttime=datetime.datetime.now()
    stock_sql_obj=StockSQL()
    print('histdata_last_df1',datetime.datetime.now())
    histdata_last_df=stock_sql_obj.query_data(table='histdata_last')
    print('histdata_last_df2',datetime.datetime.now())
    for code_str in codes:
        update_one_hist(code_str, stock_sql_obj,histdata_last_df,update_db)
    deltatime=datetime.datetime.now()-starttime
    print('update duration=',deltatime.days*24*3600+deltatime.seconds)
    print('update completed')

def get_position(broker='yh',user_file='yh.json'):
    user = easytrader.use(broker)
    user.prepare(user_file)
    holding_stocks_df = user.position#['证券代码']  #['code']
    user_balance = user.balance#['证券代码']  #['code']
    account = '36005'
    if user_file== 'yh1.json':
        account = '38736'
    holding_stocks_df['account'] = account
    this_day=datetime.datetime.now()
    date_format='%Y/%m/%d'
    time_format = date_format + ' %X'
    time_str=this_day.strftime(time_format)
    holding_stocks_df['update'] = time_str
    #holding_stocks_df['valid'] = 1
    """
            当前持仓  股份可用     参考市值   参考市价  股份余额    参考盈亏 交易市场   参考成本价 盈亏比例(%)        股东代码  \
            0  6300  6300  24885.0   3.95  6300  343.00   深A   3.896   1.39%  0130010635   
            1   400   400   9900.0  24.75   400  163.00   深A  24.343   1.67%  0130010635   
            2   600   600  15060.0  25.10   600  115.00   深A  24.908   0.77%  0130010635   
            3  1260     0  13041.0  10.35  1260  906.06   沪A   9.631   7.47%  A732980330   
            
                 证券代码  证券名称  买入冻结 卖出冻结  
            0  000932  华菱钢铁     0    0  
            1  000977  浪潮信息     0    0  
            2  300326   凯利泰     0    0  
            3  601009  南京银行     0    0  
    """
    #print(holding_stocks_df)
    return holding_stocks_df,user_balance       

def update_one_stock(symbol,realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=False):
    """
    运行之前先下载及导出YH历史数据
    """
    """
    :param symbol: string type, stock code
    :param realtime_update: bool type, True for K data force update during trade time 
    :param dest_dir: string type, like csv dir
    :param force_update_from_YH: bool type, force update K data from YH
    :return: Dataframe, history K data for stock
    """
    index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                     'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
    qq_index_symbol_maps = {'sh':'000001','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
    FIX_FACTOR = 1.0
    d_format='%Y/%m/%d'
    last_date_str = tt.get_last_trade_date(date_format=d_format)
    latest_date_str = tt.get_latest_trade_date(date_format=d_format)
    #print('last_date_str=',last_date_str)
    #print('latest_date_str=',latest_date_str)
    next_date_str = tt.get_next_trade_date(date_format=d_format)
    #print(next_date_str)
    dest_file_name = dest_dir+ '%s.csv' % symbol
    dest_df = get_raw_hist_df(code_str=symbol)
    file_type='csv'
    RAW_HIST_DIR = "C:/中国银河证券海王星/T0002/export/"
    yh_file_name = RAW_HIST_DIR+symbol+'.'+file_type
    if dest_df.empty:
        if symbol in index_symbol_maps.keys():
            symbol = index_symbol_maps[symbol]
        yh_file_name = RAW_HIST_DIR+symbol+'.'+file_type
        #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
        yh_index_df = pd.read_csv(yh_file_name)
        yh_index_df['factor'] = 1.0
        yh_df = yh_index_df.set_index('date')
        yh_df.to_csv(dest_file_name ,encoding='utf-8')
        dest_df = yh_index_df
        #del dest_df['rmb']
        return yh_df
    #print(dest_df)
    dest_df_last_date = dest_df.tail(1).iloc[0]['date']
    #print('dest_df_last_date=',dest_df_last_date)
    if dest_df_last_date<latest_date_str:     
        quotation_date = ''
        try:
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_date = quotation_index_df.iloc[0]['date']
            if dest_df_last_date==quotation_date:
                return dest_df
            #quotation_index_df = ts.get_index()
        except:
            time.sleep(3)
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_date = quotation_index_df.iloc[0]['date']
            if dest_df_last_date==quotation_date:
                return dest_df
        #print('quotation_date=',quotation_date)
        #print(quotation_index_df)
        quotation_index_df['factor'] = 1.0
        quotation_index_df = quotation_index_df[['date','open','high','low','close','volume','amount','factor']]
        #quotation_index_df.iloc[0]['volume'] = 0
        #quotation_index_df.iloc[0]['amount'] = 0
        #print(quotation_index_df)
        #print(quotation_index_df)
        need_to_send_mail = []
        sub = ''
        index_name = symbol
        #table_update_times = self.get_table_update_time()
        
        if quotation_date:
            yh_symbol = symbol
            if symbol in index_symbol_maps.keys():
                yh_symbol = index_symbol_maps[index_name]
            yh_file_name = RAW_HIST_DIR+yh_symbol+'.'+file_type
            #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
            yh_index_df = pd.read_csv(yh_file_name,encoding='GBK')
            yh_index_df['factor'] = FIX_FACTOR
            yh_last_date = yh_index_df.tail(1).iloc[0]['date']
            #print('yh_last_date=',yh_last_date)
            #print( yh_index_df)#.head(len(yh_index_df)-1))
            
            if yh_last_date>dest_df_last_date:  #dest_df_last_date<latest_date_str
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
                    if realtime_update and yh_last_date<latest_date_str:
                        print(' force update %s index' % symbol)
                        yh_index_df = yh_index_df.append(quotation_index_df, ignore_index=True)
                        #print(yh_index_df)
                    pass
                else:# yh_last_date>latest_date_str: #update to  latest date
                    """YH已经更新到今天，要更新盘中获取的当天数据"""
                    print(' %s index updated to %s; not need to update' % (index_name,latest_date_str))
                    """
                    if force_update:
                        print(' force update %s index' % index_name)
                        yh_index_df0 = yh_index_df.head(len(yh_index_df)-1)
                        print(yh_index_df0)
                        yh_index_df = yh_index_df0.append(quotation_index_df, ignore_index=True)
                        print(yh_index_df)
                    else:
                        pass
                    """
                yh_index_df = yh_index_df.set_index('date')
                """
                try:
                    os.remove(file_name)
                    print('Delete and update the csv file')
                except:
                    pass
                """
                yh_index_df.to_csv(dest_file_name ,encoding='utf-8')
            else:
                if force_update_from_YH and yh_last_date==dest_df_last_date:
                    yh_index_df = yh_index_df.set_index('date')
                    yh_index_df.to_csv(dest_file_name ,encoding='utf-8')
                pass
    else:
        print('No need to update data')
        if realtime_update:
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_index_df['factor'] = 1.0
            quotation_index_df = quotation_index_df[['date','open','high','low','close','volume','amount','factor']]
            #print(quotation_index_df)
            print(' force update %s index' % symbol)
            dest_df0 = dest_df
            if dest_df_last_date==latest_date_str:
                dest_df0 = dest_df.head(len(dest_df)-1)
            #print(dest_df0)
            dest_df = dest_df0.append(quotation_index_df, ignore_index=True)
            #print(dest_df)
            if quotation_index_df.empty:
                pass
            else:
                dest_df.to_csv(dest_file_name ,encoding='utf-8')
        else:
            pass
    return dest_df

def update_codes_from_YH(codes, realtime_update=False, dest_dir='C:/hist/day/data/', force_update_from_YH=False):
    #index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
    #                 'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
    #print(list(index_symbol_maps.keys()))
    #通常为指数和基金从银河的更新
    for symbol in codes: # #list(index_symbol_maps.keys()):
        update_one_stock(symbol, realtime_update, dest_dir, force_update_from_YH)
    return

def get_exit_data(symbol,dest_df,last_date_str):
    df=pd.read_csv('C:/hist/day/temp/%s.csv' % symbol)
    dest_df = get_raw_hist_df(code_str=symbol)
    if dest_df.empty:
        pass
    else:
        dest_df_last_date = dest_df.tail(1).iloc[0]['date']
        if dest_df_last_date==last_date_str:
            exit_price = dest_df.tail(3)
    return

def get_hold_stock_statistics(hold_stocks= ['000007', '000932', '601009', '150288', '300431', '002362', '002405', '600570', '603398'],
                              stock_dir='C:/hist/day/temp/'):
    if len(hold_stocks)<1:
            return False
    first_stock = hold_stocks[0]
    statistics_df = pd.read_csv(stock_dir + '%s.csv' % first_stock).tail(1)
    statistics_df['code'] = first_stock
    if len(hold_stocks)>=2:
        hold_stocks.pop(0)
        for stock in hold_stocks:
                temp_hold_df = pd.read_csv(stock_dir + '%s.csv' % stock).tail(1)
                temp_hold_df['code'] = stock
                statistics_df = statistics_df.append(temp_hold_df)
    statistics_df = statistics_df.set_index('code')
    return statistics_df
        
class StockSQL(object):
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://emsadmin:Ems4you@112.74.101.126/stock?charset=utf8')#,encoding='utf-8',echo=True,convert_unicode=True)
        self.hold = {}
        #self.engine = create_engine('mysql+pymysql://emsadmin:Ems4you@112.74.101.126/stock?charset=gbk')
    def get_table_df(self,table,columns=None):
        """
        :param table: string type, db_name.table_name
        :param columns: lit type with string value, like: ['acc_name', 'initial']
        :return: DataFrame type
        """
        if columns:
            return pd.read_sql_table(table, self.engine)
        else:
            return pd.read_sql_table(table, self.engine, columns)
        
    def insert_table(self,data_frame,table_name,is_index=False):
        """
        :param data_frame: DataFrame type
        :param table_name: string type, name of table
        :return: 
        """
        data_frame.to_sql(table_name, self.engine, index=is_index,if_exists='append')#encoding='utf-8')
        return
    
    def query_data(self,table,fields=None,condition=None):
        """
        :param table: string type, db_name.table_name
        :param fields: string type, like 'id,type,value'
        :param condition: string type, like 'field_value>50'
        :return: DataFrame type
        """
        query_sql=form_sql(table_name=table, oper_type='query', select_field=fields, where_condition=condition)
        print(query_sql)
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
            yh_file_name = RAW_HIST_DIR+symbol+'.'+file_type
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
            yh_file_name = RAW_HIST_DIR+symbol+'.'+file_type
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
                position_df,balance = get_position(broker, user_file)
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
                    position_df,balance = get_position(broker, user_file)
                    self.hold[account] =  position_df
                    self.insert_table(data_frame=position_df,table_name='hold')
                except:
                    pass
                #self.insert_table(data_frame=position_df,table_name='balance')
                
    def get_except_codes(self):
        #从数据库获取除外的股票代码，比如高风险或者长期持有，或者新股中签等
        except_df = self.query_data(table='stock.except',fields='code',condition='valid=1')
        return except_df['code'].values.tolist()
    
    def update_sql_position(self, users={'account':'36005','broker':'yh','json':'yh.json'}):
        try:
            account_id = users['account']
            broker = users['broker']
            user_file = users['json']
            position_df,balance = get_position(broker, user_file)
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
            time.sleep(10)
            self.update_sql_position(users)
    
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
            available_sell_df = hold_df[(hold_df['valid'])==1 & (hold_df['股份可用']>=100)]
            if available_sell_df.empty:
                available_sells = available_sell_df['证券代码'].values.tolist()
        return hold_df,hold_stocks,available_sells
        
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
    #for chunk_df in pd.read_sql_query("SELECT * FROM today_stock", engine, chunksize=5):
    #    print(chunk_df)

def stock_sql_test():
    stock_sql_obj=StockSQL()
    table='test'
    df=stock_sql_obj.get_table_df(table)#, columns=['name']) 
    print('get_table_df=')
    print(df)
    df2=stock_sql_obj.get_table_df(table, columns=['name']) 
    print(df2)
    print('query_data:')
    df3=stock_sql_obj.query_data(table)
    print(df3)
    df3=stock_sql_obj.query_data(table, 'name', "name='王五'")
    print(df3)
    print('insert_data:')
    data=[['李二'],['黄三']]
    stock_sql_obj.insert_data(table, 'name', data)
    print('update_data:')
    stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    #stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    print('delete_data')
    stock_sql_obj.delete_data(table, "name='陈五'")


    
