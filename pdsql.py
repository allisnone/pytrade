# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
from pandas.io import sql
from pandas.lib import to_datetime
from pandas.lib import Timestamp
import datetime,time,os
ROOT_DIR='E:/work/stockAnalyze'
RAW_HIST_DIR=ROOT_DIR+'/export/'  
HIST_DIR=ROOT_DIR+'/update/'

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
    if table_name=='':
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
    #print('%s_sql=%s'%(oper_type,sql))
    return sql

def get_raw_hist_df0(code_str,latest_count=None):
    file_type='csv'
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    raw_column_list=['date','open','high','low','close','volume','rmb']
    #print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    try:
        df_0=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
    except (OSError,PermissionError) as e:
        print(e)
        return df_0
    #print df_0
    #delete column 'rmb' and delete the last row
    #del df_0['rmb']
    df=df_0.ix[0:(len(df_0)-2)]  #to delete '通达信‘
    #print df
    df= df.set_index('date')
    df.to_csv(file_name,encoding='utf-8')
    #column_list=['date','open','high','low','close','volume']
    column_list=['date','open','high','low','close','volume','rmb']
    df=pd.read_csv(file_name,names=column_list, header=0,encoding='utf-8')
    return df


def get_raw_hist_df(code_str,latest_count=None):
    file_type='csv'
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    raw_column_list=['date','open','high','low','close','volume','rmb']
    #print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    try:
        df=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
        #print('pd.read_csv=',df)
        if df.empty:
            #print('code_str=',code_str)
            return df
        last_date=df.tail(1).iloc[0].date
        if last_date=='数据来源:通达信':
            df=df[:-1]
            #print('数据来源:通达信')
            #print(df.tail(1).iloc[0].date)
            last_volume=df.tail(1).iloc[0].volume
            if int(last_volume)==0:
                df=df[:-1]
            df['date'].astype(Timestamp)
            df.to_csv(file_name,encoding='utf-8')
        else:
            pass
        return df
    except OSError as e:
        #print('OSError:',e)
        return df_0

def update_one_hist(code_str,stock_sql_obj,histdata_last_df):
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
    last_db_date=stock_sql_obj.get_last_db_date(code_str,histdata_last_df)
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
    stock_sql_obj.insert_table(df, 'histdata')
    #print(df.tail(1))
    #print(df.tail(1).iloc[0])
    update_date=df.tail(1).iloc[0].date
    #last_date=histdata_last_df.loc[date[-1],'date']
    #update_date= 2015-11-20 <class 'str'>
    #print('update_date=',update_date,type(update_date))
    stock_sql_obj.update_last_db_date(code_str,last_db_date_str,update_date,histdata_last_df)
    return len(df)

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
    
def update_hist_data_tosql(codes):
    """
    :param codes: list type, code string list 
    :return: 
    """
    starttime=datetime.datetime.now()
    #all_code=get_all_code(RAW_HIST_DIR)
    #pd.DataFrame.to_sql()
    stock_sql_obj=StockSQL()
    #stock_sql_test()
    #code_str='000987'
    #code_str='002678'
    histdata_last_df=stock_sql_obj.query_data(table='histdata_last')
    for code_str in codes:
        update_one_hist(code_str, stock_sql_obj,histdata_last_df)
    deltatime=datetime.datetime.now()-starttime
    print('update duration=',deltatime.days*24*3600+deltatime.seconds)
    print('update completed')
        
def is_trade_time_now():
    except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06','2015-10-07','2015-10-08']
    now_timestamp=time.time()
    this_time=datetime.datetime.now()
    this_date=this_time.strftime('%Y-%m-%d')
    hour=this_time.hour
    minute=this_time.minute
    is_trade_time=((hour>=9 and minute>=30) and (hour<=11 and minute<=30)) or (hour>=13 and hour<=15)
    is_working_date=this_time.isoweekday()<6 and (this_date not in except_trade_day_list)
    return is_trade_time and is_working_date


class StockSQL(object):
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://emsadmin:Ems4you@112.74.101.126/stock?charset=utf8')#,encoding='utf-8',echo=True,convert_unicode=True)
    
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
        
    def insert_table(self,data_frame,table_name):
        """
        :param data_frame: DataFrame type
        :param table_name: string type, name of table
        :return: 
        """
        data_frame.to_sql(table_name, self.engine, index=False,if_exists='append')#encoding='utf-8')
        return
    
    def query_data(self,table,fields=None,condition=None):
        """
        :param table: string type, db_name.table_name
        :param fields: string type, like 'id,type,value'
        :param condition: string type, like 'field_value>50'
        :return: DataFrame type
        """
        query_sql=form_sql(table_name=table, oper_type='query', select_field=fields, where_condition=condition)
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
        
    def delete_data(self,table,condition=None):
        """
        :param table_name: string type, db_name.table_name
        :param condition: string type, like 'field_value>50'
        :return: 
        """
        delete_sql=form_sql(table_name=table,oper_type='delete',where_condition=condition)
        sql.execute(delete_sql, self.engine)
    
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
            
    def update_last_db_date(self,code_str,last_date,update_date,histdata_last_df):
        """
        :param code_str: string type, code_name
        :param last_date: string type, last db date
        :param update_date: string type, this date 
        :param histdata_last_df: dataframe type, df from table histdata
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




    