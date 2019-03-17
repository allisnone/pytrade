# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
import datetime,time,os
import tushare as ts
from file_config import YH_SOURCE_DATA_DIR,TDX_LAST_STRING
"""
try:
    from pandas.lib import Timestamp
except:
    pass
"""
from pandas._libs.lib import Timestamp
import easytrader,easyhistory
import time,os

#ROOT_DIR='E:/work/stockAnalyze'
#ROOT_DIR="C:/中国银河证券海王星/T0002"
#ROOT_DIR="C:\work\stockAnalyze"
#RAW_HIST_DIR=YH_SOURCE_DATA_DIR#"C:/中国银河证券海王星/T0002/export/"  
#TDX_LAST_STRING = '数据来源:通达信'
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

def format_code(code):
    """
    股票代码规整
    """
    if not code:
        return ''
    else:
        if isinstance(code,int) or isinstance(code,str):
            code_str = '%s'%code
            if len(code_str)>=6:
                code = code_str
            else:
                code = '0'*(6-len(code_str))+ '%s'%code_str
        else:
             pass
    return  code

def format_name_by_code(code,dict):
    if dict:
        try:
            return dict[code]
        except:
            return '其他指数'
    else:
        return 'None'

def get_data_columns(dest_dir,remove_value='Unnamed: 0'):
    """
    获取某一目录下相同类型文件的列值，返回list
    """
    all_files = os.listdir(dest_dir)
    if not all_files:
        return list()
    file_name = dest_dir + all_files[0]
    columns = pd.read_csv(file_name,usecols=None).tail(1).columns.values.tolist()
    try:
        columns.remove(remove_value)
    except:
        pass
    return  columns
 
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

#append_to_csv('000562')

def get_yh_raw_hist_df(code_str,latest_count=None,target_last_date_str='',is_updated_raw_export_date=False):
    file_type='csv'
    #RAW_HIST_DIR="C:/中国银河证券海王星/T0002/export/"
    file_name=YH_SOURCE_DATA_DIR+code_str+'.'+file_type
    raw_column_list=['date','open','high','low','close','volume','amount']
    #print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    has_tdx_last_string = False
    try:
    #if True:
        #print('code_str=%s'%code_str)
        df=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
        #print('pd.read_csv=',df)
        if df.empty:
            #print('code_str=',code_str)
            df_0.to_csv(file_name,encoding='utf-8')
            return df_0,has_tdx_last_string
        #else:
        #    return
        last_date=df.tail(1).iloc[0].date
        if last_date==TDX_LAST_STRING:
            df=df[:-1]
            #print('数据来源:通达信')
            #print(df.tail(1).iloc[0].date)
            if df.empty:
                df_0.to_csv(file_name,encoding='utf-8')
                return df_0,has_tdx_last_string
            #else:
            #   return
            last_volume=df.tail(1).iloc[0].volume
            last_trade_date_str = df.tail(1).iloc[0].date
            if target_last_date_str and is_updated_raw_export_date:
                if last_trade_date_str>=target_last_date_str:
                    pass
                else:
                    """个股停牌，代码写入txt文件"""
                    pass
                """
                    stop_stocks_csv_name = 'C:/stop_stocks.csv'
                    stop_trade_df = df=pd.read_csv(stop_stocks_csv_name)
                    new_stock_df = pd.DataFrame({'code':[code_str]})
                    stop_trade_df.append(new_stock_df)
                """
            if int(last_volume)==0:
                df=df[:-1]
            df['date'].astype(Timestamp)
            df_to_write = df.set_index('date')
            df_to_write.to_csv(file_name,encoding='utf-8')
            has_tdx_last_string = True
        else:
            pass
        return df,has_tdx_last_string
    except OSError as e:
        #print('OSError:',e)
        df_0.to_csv(file_name,encoding='utf-8')
        return df_0,has_tdx_last_string
    
def get_easyhistory_df(code_str,source='easyhistory'):  #ta_lib
    data_path = 'C:/hist/day/data/'
    if source=='YH' or source=='yh':
        data_path = YH_SOURCE_DATA_DIR
    his = easyhistory.History(dtype='D', path=data_path,type='csv',codes=[code_str])
    #if his.empty:
    #    return his
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

def get_all_quotation(his_dir=YH_SOURCE_DATA_DIR):
    #hist_dir = 'C:/中国银河证券海王星/T0002/export/'
    all_codes = get_all_code(hist_dir)
    quotation_data = qq.get_qq_quotations_df(all_codes)
    print('quotation_data:',quotation_data)
    return quotation_data
#get_all_quotation()


def get_different_symbols(hist_dir='C:/hist/day/data/'):
    indexs= ['cyb', 'zxb', 'sz', 'sh', 'sz300', 'zx300', 'hs300']#, 'sh50']
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

def update_one_stock(symbol,realtime_update=False,dest_dir=YH_SOURCE_DATA_DIR, force_update_from_YH=False):
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
    #RAW_HIST_DIR = YH_SOURCE_DATA_DIR#"C:/中国银河证券海王星/T0002/export/"
    yh_file_name =YH_SOURCE_DATA_DIR+symbol+'.'+file_type
    if symbol in index_symbol_maps.keys():
        symbol = index_symbol_maps[symbol]
        dest_file_name = dest_dir+ '%s.csv' % symbol
    #print('dest_file_name=',dest_file_name)
    if dest_df.empty:
        if symbol in index_symbol_maps.keys():
            symbol = index_symbol_maps[symbol]
        yh_file_name = YH_SOURCE_DATA_DIR+symbol+'.'+file_type
        #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
        #print('yh_file_namev=',yh_file_name)
        yh_index_df = pd.read_csv(yh_file_name)
        #yh_index_df['factor'] = 1.0
        yh_df = yh_index_df.set_index('date')
        yh_df.to_csv(dest_file_name ,encoding='utf-8')
        dest_df = yh_index_df
        #del dest_df['rmb']
        return yh_df
    #print(dest_df)
    dest_df_last_date = dest_df.tail(1).iloc[0]['date']
    #print('dest_df_last_date=',dest_df_last_date)
    quotation_datetime = datetime.datetime.now()
    if dest_df_last_date<latest_date_str:     
        quotation_date = ''
        try:
            quotation_index_df = qq.get_qq_quotations_df([symbol], ['code','date','open','high','low','close','volume','amount'])
            quotation_date = quotation_index_df.iloc[0]['date']
            #quotation_date = quotation_index_df.iloc[0]['date']
            #quotation_datetime = quotation_index_df.iloc[0]['datetime']
            #del quotation_index_df['datetime']
            if dest_df_last_date==quotation_date:
                return dest_df
            #quotation_index_df = ts.get_index()
        except:
            time.sleep(3)
            quotation_index_df = qq.get_qq_quotations_df([symbol], ['code','date','open','high','low','close','volume','amount'])
            print(quotation_index_df)
            quotation_date = quotation_index_df.iloc[0]['date']
            #quotation_datetime = quotation_index_df.iloc[0]['datetime']
            #del quotation_index_df['datetime']
            if dest_df_last_date==quotation_date:
                return dest_df
        #print('quotation_date=',quotation_date)
        #print(quotation_index_df)
        #quotation_index_df['factor'] = 1.0
        quotation_index_df = quotation_index_df[['date','open','high','low','close','volume','amount']]#,'factor']]
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
            yh_file_name = YH_SOURCE_DATA_DIR+yh_symbol+'.'+file_type
            #yh_index_df = get_yh_raw_hist_df(code_str=symbol)
            yh_index_df = pd.read_csv(yh_file_name,encoding='GBK')
            #yh_index_df['factor'] = FIX_FACTOR
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
                    realtime_update = tt.is_trade_time_now()
                    if realtime_update:
                        if yh_last_date<latest_date_str:
                            print(' force update %s index' % symbol)
                            yh_index_df = yh_index_df.append(quotation_index_df, ignore_index=True)
                        
                        #elif yh_last_date==latest_date_str:
                        #    print(' delete last update, then force update %s index' % symbol)
                        #    yh_index_df=yh_index_df[:-1]
                        #    yh_index_df = yh_index_df.append(quotation_index_df, ignore_index=True)
                        
                        else:
                            pass
                        #print(yh_index_df)
                    else:
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
    elif dest_df_last_date==latest_date_str:
        print('No need to update data')
        realtime_update = tt.is_trade_time_now()
        if realtime_update:
            quotation_index_df = qq.get_qq_quotations([symbol], ['code','date','open','high','low','close','volume','amount'])
            #quotation_index_df['factor'] = 1.0
            quotation_index_df = quotation_index_df[['date','open','high','low','close','volume','amount']]#'factor']]
            #print(quotation_index_df)
            print(' force update %s index' % symbol)
            dest_df0 = dest_df
            if dest_df_last_date==latest_date_str:
                dest_df0 = dest_df.head(len(dest_df)-1)
                #dest_df0 = dest_df0[:-1]
            #print(dest_df0)
            dest_df = dest_df0.append(quotation_index_df, ignore_index=True)
            #print(dest_df)
            if quotation_index_df.empty:
                pass
            else:
                yh_index_df = yh_index_df.set_index('date')
                dest_df.to_csv(dest_file_name ,encoding='utf-8')
        else:
            pass
    else:
        pass
    return dest_df

#df = update_one_stock(symbol='399006',dest_dir="C:/中国银河证券海王星/T0002/export/", force_update_from_YH=False)
#print(df)
def update_realtime_k(hist_dir=YH_SOURCE_DATA_DIR):
    update_one_stock(symbol, realtime_update, hist_dir, force_update_from_YH)
    return 

def update_codes_from_YH(codes, realtime_update=False, dest_dir='C:/hist/day/data/', force_update_from_YH=False):
    #index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
    #                 'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
    #print(list(index_symbol_maps.keys()))
    #通常为指数和基金从银河的更新
    for symbol in codes: # #list(index_symbol_maps.keys()):
        print(symbol)
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

def get_exit_comnfirm_rate(sql=None):
    """
    Get from SQL
    """
    confirm_rate=0.0026#卖出交易费
    if sql:
        setting_dict = stock_sql_obj.get_exit_setting_data()
        if setting_dict and 'exit_confirm_rate' in list(setting_dict.keys()):
            confirm_rate = setting_dict['exit_confirm_rate']
    return confirm_rate

def get_exit_setting_rate(exit_setting_dict={}):
    """
    Get from SQL
    """
    confirm_rate=0.0026
    tolerate_dropdown_rate = -0.05
    delay_minutes = 60
    if exit_setting_dict:
        if 'valid' in list(exit_setting_dict.keys()):
            if exit_setting_dict['valid']:
                if 'tolerate_loss' in list(exit_setting_dict.keys()):
                    tolerate_dropdown_rate = exit_setting_dict['tolerate_loss']
                if 'exit_confirm_rate' in list(exit_setting_dict.keys()):
                    confirm_rate = exit_setting_dict['exit_confirm_rate']
                if 'delay_minutes' in list(exit_setting_dict.keys()):
                    delay_minutes = exit_setting_dict['delay_minutes']
            else:
                return 0,0,0
        else:
            pass
        return confirm_rate,tolerate_dropdown_rate,delay_minutes

def get_stock_exit_price(hold_codes=['300162'],exit_setting_dict={},data_path=YH_SOURCE_DATA_DIR):#'C:/中国银河证券海王星/T0002/export/'):#, has_update_history=False):
    """获取包括股票的止损数据"""
    """
    confirm_rate:超过止损价后再次下跌的幅度，以确认止损
    """
    confirm_rate,tolerate_dropdown_rate,delay_minutes = get_exit_setting_rate(exit_setting_dict)
    #exit_dict={'300162': {'exit_half':22.5, 'exit_all': 19.0},'002696': {'exit_half':17.10, 'exit_all': 15.60}}
    has_update_history = True
    """
    if not has_update_history:
        easyhistory.init('D', export='csv', path="C:/hist",stock_codes=hold_codes)
        easyhistory.update(path="C:/hist",stock_codes=hold_codes)
        #has_update_history = True
    """
    #his = easyhistory.History(dtype='D', path='C:/hist',codes=hold_codes)
    #data_path = 'C:/hist/day/data/'
    #data_path = 'C:/中国银河证券海王星/T0002/export/' 
    exit_dict = dict()
    his = easyhistory.History(dtype='D', path=data_path, type='csv',codes=hold_codes)
    d_format='%Y/%m/%d'
    last_date_str = tt.get_last_trade_date(date_format=d_format)
    latest_date_str = tt.get_latest_trade_date(date_format=d_format)
    for code in hold_codes:
        #code_hist_df = hist[code].MA(1).tail(3).describe()
        if code=='sh000001' or code=='sh':
            code = '999999'
        if code=='cyb':
            code = '399006'
        exit_data = dict()
        hist_df  =his[code].ROC(1) 
        hist_last_date = hist_df.tail(1).iloc[0].date
        last_close = hist_df.tail(1).iloc[0].close
        #print('hist_last_date=',hist_last_date)
        great_drop_rate = 0.0
        geat_increase_rate = 0.0
        min_close = 0.0
        min_low =0.0
        if hist_last_date<last_date_str:
            hist_df['l_change'] = ((hist_df['low']-hist_df['close'].shift(1))/hist_df['close'].shift(1)).round(3)
            hist_df['h_change'] = ((hist_df['high']-hist_df['close'].shift(1))/hist_df['close'].shift(1)).round(3)
            hist_low_describe = hist_df.tail(60).describe()
            #print(hist_low_describe)
            great_drop_rate = round(hist_low_describe.loc['25%'].l_change,4)#表征下跌时，异常大的下跌幅度
            geat_increase_rate = round(hist_low_describe.loc['75%'].h_change,4)#表征上涨时，较大的上涨幅度
            if tolerate_dropdown_rate<0: #如果有给定容许回撤
                great_drop_rate = max(great_drop_rate,tolerate_dropdown_rate)
            #print('hist_low_change=',hist_low_change)
            #if hist_low_change< great_drop_rate:
            #great_drop_rate = hist_low_change
            #print('great_drop_rate=',great_drop_rate)
        else:
            hist_df['l_change'] = ((hist_df['low']-hist_df['close'].shift(1))/hist_df['close'].shift(1)).round(3)
            hist_df['h_change'] = ((hist_df['high']-hist_df['close'].shift(1))/hist_df['close'].shift(1)).round(3)
            hist_low_describe = hist_df.tail(60).describe()
            great_drop_rate = round(hist_low_describe.loc['25%'].l_change,4)
            geat_increase_rate = round(hist_low_describe.loc['75%'].h_change,4)
            #great_drop_rate = hist_low_change
            #print('great_drop_rate=',great_drop_rate)
            hist_df = hist_df[hist_df.date<=last_date_str]
            describe_df = his[code].MA(1).tail(3).describe()
            min_low =round(describe_df.loc['min'].low, 2) #撒内最低价的最小值
            min_close = round(round(describe_df.loc['min'].close,2),2)
            max_close = round(describe_df.loc['max'].close,2)
            max_high = round(describe_df.loc['max'].high,2)#三日最高价的最大值
            if tolerate_dropdown_rate<0: #如果有给定容许回撤
                min_low = max(min_low,round(last_close*(1.0+tolerate_dropdown_rate),2))
        exit_half_price = min_close * (1.0 - confirm_rate)
        exit_all_price = min_low * (1.0 - confirm_rate)
        
        """
        if min_low<=5:
            pass
        elif min_low<=10:
            exit_half_price = exit_half_price - 0.01
            exit_all_price = exit_all_price - 0.01
        elif min_low<=30:
            exit_half_price = exit_half_price - 0.02
            exit_all_price = exit_all_price - 0.02
        elif min_low<=50:
            exit_half_price = exit_half_price - 0.05
            exit_all_price = exit_all_price - 0.05
        elif min_low<=100:
            exit_half_price = exit_half_price - 0.1
            exit_all_price = exit_all_price - 0.1
        else:
            exit_half_price = exit_half_price - 0.2
            exit_all_price = exit_all_price - 0.2
        """
        exit_data['exit_half'] = exit_half_price
        exit_data['exit_all'] = exit_all_price
        exit_data['exit_rate'] = great_drop_rate
        exit_data['t_rate'] = geat_increase_rate
        exit_dict[code] = exit_data
    #print('exit_dict=%s' % exit_dict)
    return exit_dict

def send_exit_mail(exit_code='002290',exit_state=1.0,exit_data={},exit_time=datetime.datetime.now(),
                   mail_to_list=None,count=0,clear=0,to_sql=None,period_count=20):
    """发送止损退出email告警"""
    exit_type = ""
    if exit_state==1:
        exit_type = "清仓 "
    elif exit_state==0.5:
        exit_type = "半仓 "
    else:
        pass
    stock_type = "个股风险"
    if exit_code in ['sh','cyb','999999','399006'] :
        stock_type = "系统风险"
    sub = '[%s] %s触发<%s>止损,累计触发count=%s, 时间: %s' % (stock_type,exit_code,exit_type,count, exit_time)
    content = '请确认已经止损！止损数据： \n %s' % exit_data
    if clear:
        sub = '[解除' + sub[1:]
        content = '当日止损后重返止损之上！止损数据： \n %s' % exit_data
    else:
        pass
    if count==1 or count%period_count==0:
        sm.send_mail(sub,content,mail_to_list)
        if to_sql:
            #type,symbol,subject,save_time
            data = [[stock_type,exit_type,exit_code,sub,exit_time]]
            to_sql.maillogs(data)
        else:
            pass
    else:
        pass
    return

def get_exit_price(symbols=['sh','cyb'],exit_setting={},yh_index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008'}):#['sh','sz','zxb','cyb','sz300','sh50']):
    """获取包括指数在内的止损数据"""
    yh_index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008'}#'hs300':'000300'}
    hold_codes = []
    for symbol in symbols:
        actual_code = symbol
        if symbol in list(yh_index_symbol_maps.keys()):
            actual_code = yh_index_symbol_maps[symbol]
        else:#stock
            pass
        hold_codes.append(actual_code)
    exit_data = get_stock_exit_price(hold_codes,exit_setting_dict=exit_setting)
    return exit_data

def is_risk_to_exit(symbols=['sh','cyb'],init_exit_data={},
                   yh_index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008'},mail_count={},
                    demon_sql=None,mail2sql=None,mail_period=20,mailto_list=None,
                    stopped=[], operation_tdx=None,exit_setting_dict={}):
    """风险监测和emai告警"""
    #index_exit_data=get_exit_price(['sh','cyb']
    confirm_rate,tolerate_dropdown_rate,delay_minutes = get_exit_setting_rate(exit_setting_dict)
    exit_data = init_exit_data
    if not exit_data:
        exit_data = get_exit_price(symbols)
    else:
        pass
    if not mail_count:
        for symbol in symbols:
            mail_count[symbol] = 0
    else:
        pass
    symbol_quot = qq.get_qq_quotations(codes=symbols)
    #overlap_symbol = list(set(list(exit_data.keys())) & set(list(symbol_quot.keys())))
    if not exit_data or not symbol_quot:
        return {}
    risk_data = {}
    symbols = list(set(symbols).difference(set(stopped)))
    for symbol in symbols:
        this_risk = {}
        exit_p = 100000.0
        symbol_now_p = symbol_quot[symbol]['now']
        symbol_now_v = symbol_quot[symbol]['volume']
        if symbol_now_v>=0:  #update stop stocks
            pass
        else:
            if symbol not in stopped:
                stopped.append(symbol)
            else:
                pass
        if symbol=='300431' and demon_sql and False: #for test
            symbol_now_p = demon_sql.get_demon_value()
        code = symbol
        if code in list(yh_index_symbol_maps.keys()):
            code = yh_index_symbol_maps[symbol]
        index_exit_half = exit_data[code]['exit_half']
        index_exit_all = exit_data[code]['exit_all']
        #index_exit_all = 52.52
        #index_exit_all = 3098.89
        index_exit_rate = exit_data[code]['exit_rate']
        risk_state = 0
        
        if index_exit_all==0:
            last_close = symbol_quot[symbol]['close']
            index_exit_all = (1+2*index_exit_rate) * last_close
            index_exit_half = (1+index_exit_rate) * last_close
        else:
            pass
        #print('symbol=',symbol)
        #print('symbol_now_p=',symbol_now_p)
        #print('index_exit_all',index_exit_all)
        if symbol_now_p<=index_exit_all*(1+confirm_rate):
            risk_state = 1.0
            exit_p = index_exit_all
        elif symbol_now_p<=index_exit_half*(1+confirm_rate):
            risk_state = 0.5
            exit_p = index_exit_half
        else:
            pass
        if risk_state>0:
            if  mail_count[symbol]>=0: #email to exit
                mail_count[symbol] = mail_count[symbol] + 1
                this_risk['risk_code'] = symbol
                this_risk['risk_now'] = symbol_now_p
                this_risk['risk_state'] = risk_state
                this_risk['risk_time'] = datetime.datetime.now()
                """
                if operation_tdx:
                    pre_position = operation_tdx.get_my_position() 
                    available_to_sell = pre_position[symbol]['可用余额'] * risk_state
                    operation_tdx.order(code=symbol, direction='S', quantity=available_to_sell, actual_price=symbol_now_p)
                    post_position = operation_tdx.get_my_position()
                    print('post_position=',post_position)
                    pos_chg = operation_tdx.getPostionChange(pre_position,post_position)
                """
                send_exit_mail(exit_code=symbol,exit_state=risk_state,exit_data=exit_data[code],
                               exit_time=datetime.datetime.now(),mail_to_list=mailto_list,count=mail_count[symbol],
                               to_sql=mail2sql,period_count=mail_period)
                risk_data[symbol] = this_risk
            else:
                print('Have sent email before')
        elif risk_state==0:# not exit or recover
            if mail_count[symbol]==0:
                pass
            elif mail_count[symbol]>=1:
                if mail_count[symbol]==1:
                    send_exit_mail(exit_code=symbol,exit_state=risk_state,exit_data=exit_data[code],
                                   exit_time=datetime.datetime.now(),mail_to_list=mailto_list,count=mail_count[symbol],
                                   clear=1,to_sql=mail2sql,period_count=mail_period)
                    this_risk['risk_code'] = symbol
                    this_risk['risk_now'] = symbol_now_p
                    this_risk['risk_state'] = risk_state
                    this_risk['risk_time'] = datetime.datetime.now()
                    risk_data[symbol] = this_risk
                else:# still not descrease to 0
                    pass
                mail_count[symbol] = mail_count[symbol] - 1
            else:#不存在的情况
               pass 
        else:
            #不存在的情况
            pass
    if stopped:
        stopped=list(set(stopped))
    
    return risk_data,mail_count,stopped

def sell_risk_stock(risk_data,position,alv_sell_stocks,symbol_quot,operation_tdx,demon_sql=None,half_sell=False):
    #position,alv_sell_stocks = op_tdx.get_all_position()
    risk_stocks = list(risk_data.keys())
    current_acc_id,current_box_id = operation_tdx.get_acc_combobox_id()
    this_acc_position = operation_tdx.get_my_position() 
    acc_list = list(alv_sell_stocks.keys())
    if current_acc_id in acc_list:
        this_acc_avl_sell = alv_sell_stocks[current_acc_id]
        if this_acc_avl_sell:
            this_acc_exit_stocks = list(set(risk_stocks) & set(this_acc_avl_sell))
            for symbol in this_acc_exit_stocks:
                risk_state = risk_data[symbol]['risk_state']
                if (risk_state==0.5 and not half_sell) or risk_state==0:
                    continue
                this_acc_num_to_sell = this_acc_position[symbol]['可用余额'] * risk_state
                """
                set_columns= ['ask1', 'bid1_volume', 'code', 'price_volume_amount', 'ask5_volume', 'ask5', 
                              'PE', 'now', 'bid2_volume', 'bid5', 'recent_trade', 'wave', 'high', 'close', 
                              'circulation', 'bid2', 'bid3', 'ask1_volume', 'increase', 'name', 'low', 
                              'bid3_volume', 'ask3', 'high_2', 'bid_volume', 'bid5_volume', 'ask3_volume', 'quot_time',
                              'datetime', 'open', 'total_market', 'low_2', 'topest', 'ask2_volume', 'turnover', 
                              'ask_volume', 'bid1', 'amount', 'increase_rate', 'PB', 'ask2', 'lowest', 
                              'ask4_volume', 'date', 'bid4_volume', 'ask4', 'volume', 'unknown', 'bid4']
                """
                symbol_bid1_p = symbol_quot[symbol]['bid1']
                symbol_bid5_p = symbol_quot[symbol]['bid5']
                symbol_ask1_p = symbol_quot[symbol]['ask1']
                symbol_ask5_p = symbol_quot[symbol]['ask5']
                symbol_now_p = symbol_quot[symbol]['now']
                symbol_now_v = symbol_quot[symbol]['volume']
                symbol_topest = symbol_quot[symbol]['topest']
                symbol_lowest = symbol_quot[symbol]['lowest']
                if symbol_now_v<=0 or symbol_now_p<=0:#stop trade
                    continue
                limit_p = [symbol_topest,symbol_lowest]
                if symbol=='300432' and demon_sql: #for test
                    symbol_now_p = demon_sql.get_demon_value()
                #operation_tdx.order(code=symbol, direction='S', quantity=this_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None)
                operation_tdx.order(code=symbol, direction='S', quantity=this_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None,post_confirm_interval=0,check_valid_time=True)
        else:
            pass
    if len(acc_list)==2:
        exchange_id = operation_tdx.change_account(current_acc_id, current_box_id)
        second_acc_id,second_box_id = operation_tdx.get_acc_combobox_id()
        second_acc_position = operation_tdx.get_my_position() 
        if second_acc_id in acc_list:
            second_acc_avl_sell = alv_sell_stocks[second_acc_id]
            if second_acc_avl_sell:
                this_acc_exit_stocks = list(set(risk_stocks) & set(second_acc_avl_sell))
                for symbol in this_acc_exit_stocks:
                    risk_state = risk_data[symbol]['risk_state']
                    print('second_acc_position[symbol]=',second_acc_position[symbol])
                    if (risk_state==0.5 and not half_sell) or risk_state==0: #and '可用余额 ' not in list(risk_data[symbol].keys()):
                        continue
                    second_acc_num_to_sell = second_acc_position[symbol]['可用余额 '] * risk_state
                    symbol_bid1_p = symbol_quot[symbol]['bid1']
                    symbol_bid5_p = symbol_quot[symbol]['bid5']
                    symbol_ask1_p = symbol_quot[symbol]['ask1']
                    symbol_ask5_p = symbol_quot[symbol]['ask5']
                    symbol_now_p = symbol_quot[symbol]['now']
                    symbol_now_v = symbol_quot[symbol]['volume']
                    if symbol_now_v<=0 or symbol_now_p<=0:#stop trade
                        continue
                    symbol_topest = symbol_quot[symbol]['topest']
                    symbol_lowest = symbol_quot[symbol]['lowest']
                    limit_p = [symbol_topest,symbol_lowest]
                    if symbol=='300432' and demon_sql: #for test
                        symbol_now_p = demon_sql.get_demon_value()
                    #operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None)
                    operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None,post_confirm_interval=0,check_valid_time=True)
            else:
                pass
    return

def get_potential_stocks(stock_sql,strategy=33):
    potential_stocks = []
    table = 'potential'
    potential_stock_df = stock_sql.get_table_df(table,columns=None)
    if potential_stock_df.empty:
        pass
    else:
        potential_stocks = potential_stock_df['code'].tolist()
    print('potential_stocks=',potential_stocks)
    return potential_stocks

def get_realtime_price(stocks=[]):
    symbol_quot = qq.get_qq_quotations(codes=stocks)
    """
    symbol_bid1_p = symbol_quot[symbol]['bid1']
    symbol_bid5_p = symbol_quot[symbol]['bid5']
    symbol_ask1_p = symbol_quot[symbol]['ask1']
    symbol_ask5_p = symbol_quot[symbol]['ask5']
    symbol_now_p = symbol_quot[symbol]['now']
    """
    return symbol_quot

def get_sort_reference_datas(stock_sql, potential_stocks=[], value_column='refer', sort_reverse=True):
    sort_reference_list = []
    table = 'reference'
    reference_datas_df = stock_sql.get_table_df(table,columns=['code',value_column])
    if reference_datas_df.empty:
        pass
    else:
        del reference_datas_df['id']
        reference_stocks = reference_datas_df['code'].tolist()
        reference_datas_df = reference_datas_df.set_index('code')
        #print(reference_datas_df)
        overlap_stocks = list(set(potential_stocks).intersection(set(reference_stocks)))
        reference_datas_df = reference_datas_df[reference_datas_df.index.isin(overlap_stocks)]
        #print(reference_datas_df)
        print(reference_datas_df[value_column])
        #print(type(reference_datas_df[value_column]))
        sort_reference_datas = reference_datas_df[value_column].to_dict()
        #print('sort_reference_datas=',sort_reference_datas)
        #sort_reference_datas = {'300062':12.0,'000060':10.2}  #to sort and get the sequence
        #sort_reference_list =sorted(sort_reference_datas.items(), lambda x, y: cmp(x[1], y[1]), reverse=sort_reverse)   #code, value  python2.7
        sort_reference_list = sorted(sort_reference_datas.items(), key=lambda d: d[1],reverse=True)
        #sorted(sort_reference_datas.items(), key=lambda d: d[0],reverse=True)
    print('sort_reference_list=',sort_reference_list)
    return sort_reference_list

def determine_buy_stocks(sorted_stock_list,symbol_quot, available_money, 
                         buy_stock_nums=1,suitable_amount=16600,sort_reverse=True,max_buy_stocks=10):
    """
    hist_data = pd.read_csv('C:/hist/day/temp/regression_test.csv')
    hist_data.index.isin(potential_stocks)
    hist_data['sort_value']=hist_data
    """
    #buy_stock_nums = get_acc_buy_nums(acc_value, available_money,max_positon=0.7,suitable_amount=16600):
    potential_len = len(sorted_stock_list)
    buy_stock_datas = []
    #symbol_quot = qq.get_qq_quotations(potential_stocks)
    remained_list = sorted_stock_list
    final_buy_stock_nums = min(potential_len,min(buy_stock_nums,max_buy_stocks))
    print('final_buy_stock_nums=',final_buy_stock_nums)
    i = 0
    if final_buy_stock_nums:
        suitable_amount = max(available_money/final_buy_stock_nums,suitable_amount)
        print('suitable_amount=',suitable_amount)
        while i <final_buy_stock_nums:
            #print('i=',i)
            this_buy = remained_list.pop(0)
            selected_symbol = this_buy[0]
            #print('selected_symbol=',selected_symbol)
            selected_symbol_indicator = this_buy[1]
            symbol_now_p = symbol_quot[selected_symbol]['now']
            buy_stock_share = int(suitable_amount//symbol_now_p/100)*100
            if i==(final_buy_stock_nums-1):
                buy_stock_share = int(available_money//symbol_now_p/100)*100
            #buy_stock_datas[selected_symbol] = buy_nums
            if buy_stock_share>=100:
                buy_stock_data = [selected_symbol,buy_stock_share,symbol_now_p]
                buy_stock_datas.append(buy_stock_data)
                available_money = available_money -buy_stock_share * symbol_now_p * 1.005
            if available_money < suitable_amount * 0.5:
                break
            else:
                pass
            i = i + 1
    else:
        pass
    return buy_stock_datas,remained_list

def get_dapan_position(index=[]):
    position = 0.7
    
    return position

def get_acc_buy_nums(acc_value, available_money,max_positon=0.7,suitable_amount=16600):
    buy_num = 0
    actual_available_money = min(available_money,((acc_value+available_money)*max_positon-acc_value))
    if acc_value/(acc_value+available_money)>max_positon:
        pass
    else:
        if actual_available_money<0.5*suitable_amount:
            pass
        elif actual_available_money<=suitable_amount:
            buy_num = 1
        else:
            buy_num = actual_available_money//suitable_amount
    return buy_num,actual_available_money

def get_buy_stock_datas(buy_stock_num=1,potential_stocks=[]):
    
    return

def get_acc_buy_stocks(op_tdx,stock_sql,acc_list=['36005'],buy_rate=1.0,max_pos=1.0,max_buy_num=3.0,given_stocks=[],strategy_id=1):
    #acc = '36005'
    potential_stocks = get_potential_stocks(stock_sql)
    if given_stocks:
        potential_stocks = given_stocks
    sorted_stock_list = get_sort_reference_datas(stock_sql, potential_stocks, value_column='refer', sort_reverse=True)
    symbol_quot = qq.get_qq_quotations(potential_stocks)
    dapan_pos = get_dapan_position()
    print('dapan_pos=',dapan_pos)
    all_buy_stock_datas = {}
    for acc in acc_list:
        buy_stock_datas = []
        acc_value, available_money = op_tdx.getAccountMoney(acc)
        print('account=',acc)
        print('acc_value=',acc_value)
        print('available_money=',available_money)
        acc_value, available_money = 100000.0,70000.0
        buy_num,actual_available_money = get_acc_buy_nums(acc_value, available_money,max_positon=max_pos,suitable_amount=16600)
        print('buy_num=',buy_num)
        print('actual_available_money=',actual_available_money)
        dapan_po = 0.9
        if dapan_pos<0.3:
            pass
        else:
            buy_num = int(buy_num * buy_rate)
        print('sorted_stock_list=',sorted_stock_list)
        buy_stock_datas,sorted_stock_list = determine_buy_stocks(sorted_stock_list,symbol_quot, actual_available_money, 
                         buy_stock_nums=buy_num,suitable_amount=16600,sort_reverse=True,max_buy_stocks=max_buy_num)
        print('sorted_stock_list1=',sorted_stock_list)
        all_buy_stock_datas[acc] = buy_stock_datas
    return all_buy_stock_datas

def get_dynamic_stop_profit_price(this_highest,stop_profit_price=0.0,stop_rate_from_highest=0.0):
    stop_price = this_highest
    if stop_profit_price>0:
        stop_price = min(stop_profit_price,this_highest)
    elif stop_profit_price==0.0:
        if stop_rate_from_highest<0:
            stop_price = round(this_highest*(1+0.01*stop_rate_from_highest),2)
        else:
            pass
    else:
        pass    
    return stop_price

def get_stop_profit_stocks():
    #from sql query
    return ['300085']

def get_realtime_stop_profit_price(symbol,symbol_quot,stop_profit_stocks,fix_stop_price_data={},fix_drop_rate_data={},stop_type='fixed_drop_rate'):
    #quot_stocks = list(symbol_quot.keys())
    #stop_profit_stocks = list(set(quot_stocks).intersection(set(permit_stop_profit_stocks)))
    symbol_stop_price = 0.0
    if  symbol in stop_profit_stocks:
        symbol_high_price = symbol_quot[symbol]['high']
        symbol_now_price = symbol_quot[symbol]['now']
        
        if stop_type=='fixed_drop_rate':
            stop_rate = -2.5
            if symbol in list(fix_drop_rate_data.keys()):
                stop_rate = fix_drop_rate_data[symbol]   #stop_rate>0, will sell when higher; stop_rate<0, will sell when drop down to lowwer
            else:
                pass
            symbol_stop_price = get_dynamic_stop_profit_price(this_highest=symbol_high_price, stop_rate_from_highest=stop_rate)
        elif stop_type=='fixed_price':
            if symbol in list(fix_stop_price_data.keys()):
                fix_price = fix_stop_price_data[symbol]
                symbol_stop_price = get_dynamic_stop_profit_price(this_highest=symbol_high_price, stop_profit_price=fix_price)
            else:
                pass
        else:
            pass
    return symbol_stop_price

def get_stop_profit_flag():
    stop_type='fixed_drop_rate'
    stop_profit_enable=False
    return stop_type,stop_profit_enable

def get_stop_profit_datas(stop_profit_stocks):
    fix_price_data = {}
    fix_drop_rate_data = {}
    return fix_price_data,fix_drop_rate_data

def to_sell_and_lock_profit(symbol,symbol_quot,stop_profit_stocks,fix_price_data,stop_type='fixed_drop_rate',stop_profit_enable=False):
    """
    To sell stock and lock the profit
    """
    if stop_profit_enable:
            symbol_now_price = symbol_quot[symbol]['now']
            symbol_stop_profit_price = get_realtime_stop_profit_price(symbol,symbol_quot,stop_profit_stocks,fix_price_data,fix_drop_rate_data,stop_type)
            if symbol_now_price<symbol_stop_profit_price and stop_profit_enable:
                 """To sell and stop prifit"""
                 second_acc_num_to_sell =[]
                 #operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_stop_profit_price,limit_price=None)
                 operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_stop_profit_price,limit_price=None,post_confirm_interval=0,check_valid_time=True)
                 """Write to sql, and T action or not"""
                 pass
            
    else:
        pass
    return 

def to_stop_profit(symbol_quot,stop_type='fixed_drop_rate',stop_profit_enable=False):
    """
    To sell stocks and lock the profit
    """
    stop_type,stop_profit_enable = get_stop_profit_flag()
    stop_profit_datas = dict()
    if stop_profit_enable:
        quot_stocks = list(symbol_quot.keys())
        permit_stop_profit_stocks = get_stop_profit_stocks()
        stop_profit_stocks = list(set(quot_stocks).intersection(set(permit_stop_profit_stocks)))
        fix_price_data,fix_drop_rate_data = get_stop_profit_datas(stop_profit_stocks)
        for symbol in stop_profit_stocks:
            symbol_now_price = symbol_quot[symbol]['now']
            symbol_stop_profit_price = get_realtime_stop_profit_price(symbol,symbol_quot,stop_profit_stocks,fix_price_data,fix_drop_rate_data,stop_type)
            if symbol_now_price<symbol_stop_profit_price and stop_profit_enable:
                 """To sell and stop prifit"""
                 second_acc_num_to_sell =[]
                 operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_stop_profit_price,limit_price=None,post_confirm_interval=0,check_valid_time=True)
                 symbol_stop_profit_price
                 """Write to sql, and T action or not"""
                 pass
            
            stop_profit_datas[symbol] = symbol_stop_profit_price
    else:
        pass
    return stop_profit_datas

def sell_stock_to_stop_profit(risk_data,position,alv_sell_stocks,symbol_quot,operation_tdx,demon_sql=None,half_sell=False):
    #position,alv_sell_stocks = op_tdx.get_all_position()
    risk_stocks = list(risk_data.keys())
    current_acc_id,current_box_id = operation_tdx.get_acc_combobox_id()
    this_acc_position = operation_tdx.get_my_position() 
    acc_list = list(alv_sell_stocks.keys())
    if current_acc_id in acc_list:
        this_acc_avl_sell = alv_sell_stocks[current_acc_id]
        if this_acc_avl_sell:
            this_acc_exit_stocks = list(set(risk_stocks) & set(this_acc_avl_sell))
            for symbol in this_acc_exit_stocks:
                risk_state = risk_data[symbol]['risk_state']
                if (risk_state==0.5 and not half_sell) or risk_state==0:
                    continue
                this_acc_num_to_sell = this_acc_position[symbol]['可用余额 '] * risk_state
                """
                set_columns= ['ask1', 'bid1_volume', 'code', 'price_volume_amount', 'ask5_volume', 'ask5', 
                              'PE', 'now', 'bid2_volume', 'bid5', 'recent_trade', 'wave', 'high', 'close', 
                              'circulation', 'bid2', 'bid3', 'ask1_volume', 'increase', 'name', 'low', 
                              'bid3_volume', 'ask3', 'high_2', 'bid_volume', 'bid5_volume', 'ask3_volume', 'quot_time',
                              'datetime', 'open', 'total_market', 'low_2', 'topest', 'ask2_volume', 'turnover', 
                              'ask_volume', 'bid1', 'amount', 'increase_rate', 'PB', 'ask2', 'lowest', 
                              'ask4_volume', 'date', 'bid4_volume', 'ask4', 'volume', 'unknown', 'bid4']
                """
                symbol_bid1_p = symbol_quot[symbol]['bid1']
                symbol_bid5_p = symbol_quot[symbol]['bid5']
                symbol_ask1_p = symbol_quot[symbol]['ask1']
                symbol_ask5_p = symbol_quot[symbol]['ask5']
                symbol_now_p = symbol_quot[symbol]['now']
                symbol_now_v = symbol_quot[symbol]['volume']
                symbol_topest = symbol_quot[symbol]['topest']
                symbol_lowest = symbol_quot[symbol]['lowest']
                if symbol_now_v<=0 or symbol_now_p<=0:#stop trade
                    continue
                limit_p = [symbol_topest,symbol_lowest]
                if symbol=='300432' and demon_sql: #for test
                    symbol_now_p = demon_sql.get_demon_value()
                operation_tdx.order(code=symbol, direction='S', quantity=this_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None,post_confirm_interval=0,check_valid_time=True)
        else:
            pass
    if len(acc_list)==2:
        exchange_id = operation_tdx.change_account(current_acc_id, current_box_id)
        second_acc_id,second_box_id = operation_tdx.get_acc_combobox_id()
        second_acc_position = operation_tdx.get_my_position() 
        if second_acc_id in acc_list:
            second_acc_avl_sell = alv_sell_stocks[second_acc_id]
            if second_acc_avl_sell:
                this_acc_exit_stocks = list(set(risk_stocks) & set(second_acc_avl_sell))
                for symbol in this_acc_exit_stocks:
                    risk_state = risk_data[symbol]['risk_state']
                    if (risk_state==0.5 and not half_sell) or risk_state==0:
                        continue
                    second_acc_num_to_sell = second_acc_position[symbol]['可用余额 '] * risk_state
                    symbol_bid1_p = symbol_quot[symbol]['bid1']
                    symbol_bid5_p = symbol_quot[symbol]['bid5']
                    symbol_ask1_p = symbol_quot[symbol]['ask1']
                    symbol_ask5_p = symbol_quot[symbol]['ask5']
                    symbol_now_p = symbol_quot[symbol]['now']
                    symbol_now_v = symbol_quot[symbol]['volume']
                    if symbol_now_v<=0 or symbol_now_p<=0:#stop trade
                        continue
                    symbol_topest = symbol_quot[symbol]['topest']
                    symbol_lowest = symbol_quot[symbol]['lowest']
                    limit_p = [symbol_topest,symbol_lowest]
                    if symbol=='300432' and demon_sql: #for test
                        symbol_now_p = demon_sql.get_demon_value()
                    operation_tdx.order(code=symbol, direction='S', quantity=second_acc_num_to_sell, actual_price=symbol_now_p,limit_price=None,post_confirm_interval=10,check_valid_time=True)
            else:
                pass
    return


def buy_stocks(op_tdx, acc_list, stock_sql, buy_rate,strategy=1,given_buy_stocks=[]):
    all_buy_stock_datas = get_acc_buy_stocks(op_tdx, acc_list, stock_sql, buy_rate,strategy_id=strategy,given_stocks=given_buy_stocks)
    for acc in list(all_buy_stock_datas.keys()):
        this_acc_buy_data = all_buy_stock_datas[acc]
        for stock_data in this_acc_buy_data:
            symbol = stock_data[0]
            buy_shares = stock_data[1]
            buy_price = stock_data[2]
            operation_tdx.order(code=symbol, direction='b', quantity=buy_shares, actual_price=buy_price,limit_price=None,post_confirm_interval=0,check_valid_time=True)
        #account switchover
    return 

def quotation_monitor(codes,this_date_str,hour,minute):
    over_avrg_datas = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/')
    if (hour==9 and minute>30) or (hour==10) or (hour==11 and minute<=59) or (hour>=13 and hour<15):
        if minute % mail_interval == 0:
            sub = '[%s:%:00]日内均线监测 ' %(hour,minute)
            content = '每%s分钟实时 均线监测数据如下：\n %s ' % (mail_interval,over_avrg_datas)
            sm.send_mail(sub,content,mail_to_list=None)
        else:
            pass
    return

def is_risk_to_exit0(symbols=['sh','cyb'],init_exit_data={},
                   yh_index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                         'sh50':'000016','sz300':'399007','zx300':'399008'},mail_count={},
                    demon_sql=None,mail2sql=None,mail_period=20,mailto_list=None,
                    stopped=[]):
    """风险监测和emai告警"""
    #index_exit_data=get_exit_price(['sh','cyb']
    exit_data = init_exit_data
    if not exit_data:
        exit_data = get_exit_price(symbols)
    else:
        pass
    if not mail_count:
        for symbol in symbols:
            mail_count[symbol] = 0
    else:
        pass
    symbol_quot = qq.get_qq_quotations(codes=symbols)
    #overlap_symbol = list(set(list(exit_data.keys())) & set(list(symbol_quot.keys())))
    if not exit_data or not symbol_quot:
        return {}
    risk_data = {}
    symbols = list(set(symbols).difference(set(stopped)))
    for symbol in symbols:
        this_risk = {}
        exit_p = 100000.0
        symbol_now_p = symbol_quot[symbol]['now']
        symbol_now_v = symbol_quot[symbol]['volume']
        if symbol_now_v>=0:  #update stop stocks
            pass
        else:
            if symbol not in stopped:
                stopped.append(symbol)
            else:
                pass
        if symbol=='002766' and demon_sql: #for test
            symbol_now_p = demon_sql.get_demon_value()
        code = symbol
        if code in list(yh_index_symbol_maps.keys()):
            code = yh_index_symbol_maps[symbol]
        index_exit_half = exit_data[code]['exit_half']
        index_exit_all = exit_data[code]['exit_all']
        #index_exit_all = 52.52
        #index_exit_all = 3098.89
        index_exit_rate = exit_data[code]['exit_rate']
        risk_state = 0
        
        if index_exit_all==0:
            last_close = symbol_quot[symbol]['close']
            index_exit_all = (1+2*index_exit_rate) * last_close
            index_exit_half = (1+index_exit_rate) * last_close
        else:
            pass
        #print('symbol=',symbol)
        #print('symbol_now_p=',symbol_now_p)
        #print('index_exit_all',index_exit_all)
        if symbol_now_p<index_exit_all:
            risk_state = 1.0
            exit_p = index_exit_all
        elif symbol_now_p<index_exit_half:
            risk_state = 0.5
            exit_p = index_exit_half
        else:
            pass
        if risk_state>0:
            if  mail_count[symbol]>=0: #email to exit
                mail_count[symbol] = mail_count[symbol] + 1
                this_risk['risk_code'] = symbol
                this_risk['risk_now'] = symbol_now_p
                this_risk['risk_state'] = risk_state
                this_risk['risk_time'] = datetime.datetime.now()
                send_exit_mail(exit_code=symbol,exit_state=risk_state,exit_data=exit_data[code],
                               exit_time=datetime.datetime.now(),mail_to_list=mailto_list,count=mail_count[symbol],
                               to_sql=mail2sql,period_count=mail_period)
                risk_data[symbol] = this_risk
            else:
                print('Have sent email before')
        elif risk_state==0:# not exit or recover
            if mail_count[symbol]==0:
                pass
            elif mail_count[symbol]>=1:
                if mail_count[symbol]==1:
                    send_exit_mail(exit_code=symbol,exit_state=risk_state,exit_data=exit_data[code],
                                   exit_time=datetime.datetime.now(),mail_to_list=mailto_list,count=mail_count[symbol],
                                   clear=1,to_sql=mail2sql,period_count=mail_period)
                    this_risk['risk_code'] = symbol
                    this_risk['risk_now'] = symbol_now_p
                    this_risk['risk_state'] = risk_state
                    this_risk['risk_time'] = datetime.datetime.now()
                    risk_data[symbol] = this_risk
                else:# still not descrease to 0
                    pass
                mail_count[symbol] = mail_count[symbol] - 1
            else:#不存在的情况
               pass 
        else:
            #不存在的情况
            pass
    if stopped:
        stopped=list(set(stopped))
    
    return risk_data,mail_count,stopped
#is_risk_to_exit(symbols=['002095','sh'])
#is_risk_to_exit(symbols=['sh'])

def get_HO_dapan(dapan_codes=[],ho_rate=0.0026, stock_sql=None,mailto=['104450966@qq.com','1016564866@qq.com']):
    """
    找出高开的大盘股，并触发email
    """
    codes = ['600029', '600018', '000776', '600016', '600606', '601668', '600050', '601688', '600030', 
                    '600104', '601377', '601633', '600585', '601186', '600036', '002450', '000538', '601818', 
                    '601898', '002304', '601628', '600276', '601800', '002027', '600000', '601318', '601088', 
                    '601601', '000001', '601988', '601390', '600015', '002673', '600547', '600340', '601238', 
                    '601006', '000783', '001979', '601857', '000768', '601766', '600518', '600011', '000166', 
                    '002024', '000002', '600519', '600048', '600383', '300498', '600028', '600999', '002142', 
                    '601018', '600887', '601336', '600958', '002252', '601328', '002594', '601398', '600115', 
                    '000063', '601618', '601727', '000895', '601985', '300104', '600900', '601989', '600019',
                    '601899', '600663', '600690', '000333', '600649', '600795', '002415', '000725', '601211', 
                    '000625', '000651', '601169', '601111', '601788', '002736', '601009', '601669', '600837', 
                    '601939', '603993', '601288', '601166', '000858', '601998', '600705']
    if dapan_codes:
        codes = dapan_codes
    ho_codes = []
    if stock_sql:
        codes = stock_sql.get_dapan(table='dapan_gu')
    this_datas = qq.get_qq_quotations_df(codes)
    if this_datas.empty:
        return ho_codes
    ho_datas = this_datas[(this_datas['open']>=(1 + ho_rate) * this_datas['close0'])]
    if ho_datas.empty:
        return ho_codes
    else:
        ho_codes = ho_datas['code'].values.tolist()
        ho_datas['ho_chg'] = (ho_datas['open']/ho_datas['close0'] - 1)*100.0
        mail_columns = ['code','name','ho_chg','PE','increase_rate','open','high','low','close', 'PB', 'total_market','datetime']
        ho_datas = ho_datas.sort_values(axis=0, by='ho_chg', ascending=False)
        ho_datas = ho_datas[mail_columns]
        sub = '[大盘股机会] 大盘股高开比率:%s%%, 今日高开大盘股有: %s' % (round(len(ho_codes),2)/len(codes)*100,ho_codes)
        content = '高开大盘股： \n %s' % ho_datas
        sm.send_mail(sub,content,mail_to_list=mailto)
        return list(set(ho_codes))

#get_HO_dapan()

def get_std(data_df,windows=0,column='close'):
    
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


def position_datafrom_from_dict(position={'36005':{'300241':{}},'36006':{'300241':{}}}):
    new_pos = {}
    for acc in position.keys():
        acc_pos = position[acc]
        for stock in acc_pos.keys():
            acc_pos[stock]['acc'] = acc
        new_pos.update(acc_pos)
    pos_df = pd.DataFrame.from_dict(new_pos, orient='index')
    undefile_column =''
    for col in pos_df.columns.values.tolist():
        if 'Unnamed' in col:
            undefile_column = col
    if undefile_column: del pos_df[undefile_column]
    return pos_df
        