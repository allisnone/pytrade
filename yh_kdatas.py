# -*- coding:utf-8 -*-
import pandas as pd
import os,time
import file_config as fc
"""
code_str='300314'
dir='C:/work/temp/'
stop_stocks_csv_name = 'stop_stocks.csv'
new_stock_df0 = pd.DataFrame({'code':[code_str]})
new_stock_df0.to_csv(dir+stop_stocks_csv_name,encoding='utf-8')
stop_trade_df = df=pd.read_csv(dir+stop_stocks_csv_name)
stop_codes = stop_trade_df['code'].values.tolist()
print('stop_codes=',stop_codes)
code_str1 = '600132'
stop_codes.append(code_str1)
new_stock_df = pd.DataFrame({'code':stop_codes})
#stop_trade_df.append(new_stock_df)
stop_stocks_csv_name = dir+'a_' + stop_stocks_csv_name
new_stock_df.to_csv(stop_stocks_csv_name,encoding='utf-8')
"""
def append_to_csv(value,column_name='code',file_name='C:/work/temp/stop_stocks.csv',empty_first=False):
    """
    追加单列的CSV文件
    """
    stop_codes = []
    if empty_first:
        pd.DataFrame({column_name:[]}).to_csv(file_name,encoding='utf-8')
    try:
        stop_trade_df = df=pd.read_csv(file_name)
        stop_codes = stop_trade_df[column_name].values.tolist()
    except:
        pd.DataFrame({column_name:[]}).to_csv(file_name,encoding='utf-8')
    stop_codes.append(value)
    new_df = pd.DataFrame({column_name:stop_codes})
    new_df.to_csv(file_name,encoding='utf-8')
    return new_df

def combine_file(tail_num=1,dest_dir='C:/work/temp/',keyword='',prefile_slip_num=0,columns=None):
    """
    合并指定目录的最后几行
    """
    all_files = os.listdir(dest_dir)
    file_names = []
    if not keyword:
        file_names = all_files
    else:#根据keywo过滤文件
        for file in all_files:
            if keyword in file:
                file_names.append(file)
            else:
                continue
    df = pd.DataFrame({})
    #3file_names=['bs_000001.csv', 'bs_000002.csv']
    #file_names=['000001.csv', '000002.csv']
    for file_name in file_names:
        tail_df = pd.read_csv(dest_dir+file_name,usecols=columns).tail(tail_num)
        #columns = tail_df.columns.values.tolist()
        #print('columns',columns)
        prefile_name = file_name.split('.')[0]
        if prefile_slip_num:
            prefile_name = prefile_name[prefile_slip_num:]
        tail_df['name'] = prefile_name
        df=df.append(tail_df)
    return df

def get_latest_yh_k_stocks(write_file_name='',data_dir=fc.YH_SOURCE_DATA_DIR):
    """
    获取所有银河最后一个K线的数据：特定目录下
    """
    columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
    df = combine_file(tail_num=1,dest_dir=data_dir,keyword='',prefile_slip_num=0,columns=columns)
    if df.empty:
        return df
    df['counts']=df.index
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']+['counts','name']]
    df = df.set_index('name')
    if write_file_name:
        df.to_csv(write_file_name,encoding='utf-8')
    return df

def get_latest_yh_k_stocks_from_csv():
    """
    获取股票K线数据，数据来源银河证券
    """
    file_name = 'C:/work/temp1/all_yh_stocks.csv'
    columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']+['counts','name']
    try:
        df = pd.read_csv(file_name,usecols=columns)
        df = df.set_index('name')
        return df
    except:
        return get_latest_yh_k_stocks(write_file_name=file_name)

def get_stop_stock(last_date_str,source='from_yh'):
    """
    获取停牌股票，数据来源银河证券
    """
    df = get_latest_yh_k_stocks_from_csv(write_file_name=file_name)
    if df.empty:
            return pd.DataFrame({})
    stop_df = df[df.date<last_date_str]
    return stop_df
    
def get_latest_backtest_datas(write_file_name='',data_dir='D:/work/temp/'):
    """
    获取所有回测最后一个K线的数据：特定目录下
    """
    columns = ['date', 'close', 'id', 'trade', 'p_change', 'position', 'operation', 's_price', 'b_price', 'profit', 'cum_prf', 'fuli_prf', 'hold_count']
    df = combine_file(tail_num=1,dest_dir=data_dir,keyword='bs_',prefile_slip_num=3,columns=columns)
    if df.empty:
        return df
    df['counts']=df.index
    df = df[columns+['counts','name']]
    df = df.set_index('name')
    if write_file_name:
        df.to_csv('C:/work/temp1/bs_all_stocks.csv',encoding='utf-8')
    return df

def get_latest_backtest_datas_from_csv():
    """
    获取所有回测最后一个K线的数据
    """
    file_name = 'C:/work/temp1/bs_all_stocks.csv'
    columns = ['date', 'close', 'id', 'trade', 'p_change', 'position', 'operation', 's_price', 'b_price', 'profit', 'cum_prf', 'fuli_prf', 'hold_count']
    columns = columns + ['counts','name']
    try:
        df = pd.read_csv(file_name,usecols=columns)
        df = df.set_index('name')
        return df
    except:
        return get_latest_backtest_datas(write_file_name=file_name)
"""    
from pdSql import StockSQL
stock_sql = StockSQL()
r = stock_sql.is_histdata_uptodate()
print(r)

from low_high33_backtest import *
df = get_latest_backtest_datas()
#df = get_latest_backtest_datas_from_csv()  #从CSV文件读取所有回测数据
#汇总temp数据，并写入CSV文件，方便交易调用
temp_df = get_latest_temp_datas()
"""

"""
start = time.time()
last_date_str = '2017/12/27'
df=get_latest_yh_k_stocks_from_csv()
#df = get_stop_stock(last_date_str)

#df = get_latest_backtest_datas()
print(df)
end = time.time()
print('Task update yh hist data runs %0.2f seconds.' % (end - start))
"""
