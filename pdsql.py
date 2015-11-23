# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
import tushare as ts
from pandas.io import sql
from tradeStrategy import *

def form_sql(table_name,oper_type='query',select_field=None,where_condition=None,insert_field=None,update_field=None,update_value=None):
    """
    :param table_name: string type, db_name.table_name
    :param select_field: string type, like 'id,type,value'
    :param where_condition: string type, like 'field_value>50'
    :param insert_field: string type, like '(date_time,measurement_id,value)'
    :param update_field: string type, like 'value' or  '(measurement_id,value)'
    :param update_value: string type, like '1000' or "'normal_type'"
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
    elif oper_type=='update' and where_condition and update_field and update_value:
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
    print('%s_sql=%s'%(oper_type,sql))
    return sql

def get_raw_hist_df(code_str,latest_count=None):
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


def get_raw_hist_df1(code_str,latest_count=None):
    file_type='csv'
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    raw_column_list=['date0','open','high','low','close','volume','rmb']
    print('file_name=',file_name)
    df_0=pd.DataFrame({},columns=raw_column_list)
    try:
        df_0=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
    except OSError as e:
        print('OSError:',e)
        return df_0
    #print df_0
    #delete column 'rmb' and delete the last row
    #del df_0['rmb']
    df=df_0.ix[0:(len(df_0)-2)]  #to delete '通达信‘
    #print df
    
    """"check"""
    df= df.set_index('date0')
    """
    #df.index.name='date'
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    df.index.name=this_time_str
    hist_dir=ROOT_DIR+'/hist/'
    file_type='csv'
    file_name=hist_dir+code_str+'.'+file_type
    #print df
    df.to_csv(file_name)
    hist_dir=ROOT_DIR+'/update/'
    file_name=hist_dir+code_str+'.'+file_type
    """
    df.to_csv(file_name,encoding='utf-8')
    #column_list=['date','open','high','low','close','volume']
    column_list=['date0','open','high','low','close','volume','rmb']
    time_list=['00:00:00']*len(df)
    df['time0']=pd.Series(time_list,index=df.index)
    #p=df.pop('code')
    #df.insert(0,'code',p)
    date_spec = {'date': [0, 7]}
    print(df)
    df=pd.read_csv(file_name,names=column_list, header=0,encoding='utf-8',parse_dates=date_spec)
    print(df)
    return df

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
    
    def get_last_db_date0(self,code_str):
        code_condition="code='%s'" % code_str
        last_df=self.query_data(table='histdata', fields='date', condition=code_condition + ' order by date desc limit 1')
        print(last_df)
        if last_df.empty:
            return ''
        else:
            last_date=last_df.ix[0].date
            print(type(last_date))
            print('last_date=',last_date)
            return last_date
    
    def get_last_db_date(self,code_str,histdata_last_df):
        if histdata_last_df.empty:
            print('histdata_last_df is empty')
            return None
        else:
            try:
                histdata_last_df=histdata_last_df.set_index('code')
                last_date=histdata_last_df.loc[code_str,'last_db_time']
                return last_date
            except KeyError as e:
                print('KeyError:',e)
                return None
            
    def update_last_db_date(self,code_str,last_date,update_date,histdata_last_df):
        if last_date:
            if update_date>last_date:
                self.update_data(table=histdata_last, fields='last_db_time', values=update_date, condition="code='%s'"%code_str)
            else:
                pass
        elif update_date:
            self.insert_data(table='histdata_last', fields='code,last_db_time', data=[[code_str,update_date]])
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

def update_one_hist(code_str,stock_sql_obj,histdata_last_df):
    df=get_raw_hist_df(code_str)
    if df.empty:
        return
    code_list=[code_str]*len(df)
    df['code']=pd.Series(code_list,index=df.index)
    p=df.pop('code')
    df.insert(0,'code',p)
    last_db_date=stock_sql_obj.get_last_db_date(code_str,histdata_last_df)
    print('last_db_date',last_db_date,type(last_db_date))
    last_db_date_str='%s' % last_db_date
    last_db_date_str=last_db_date_str[:10]
    print('last_db_date_str',last_db_date_str)
    if last_db_date:
        df=df[df.date>last_db_date_str]
        if df.empty:
            print('History data up-to-date for %s, no need update' % code_str)
            return 0
    stock_sql_obj.insert_table(df, 'histdata')
    print(df.tail(1))
    print(df.tail(1).iloc[0])
    update_date=df.tail(1).iloc[0].date
    #last_date=histdata_last_df.loc[date[-1],'date']
    #update_date= 2015-11-20 <class 'str'>
    print('update_date=',update_date,type(update_date))
    stock_sql_obj.update_last_db_date(code_str,last_db_date,update_date,histdata_last_df)
    return len(df)

#get the all file source data in certain DIR
def get_all_code(hist_dir):
    all_code=[]
    for filename in os.listdir(hist_dir):#(r'ROOT_DIR+/export'):
        code=filename[:-4]
        if len(code)==6:
            all_code.append(code)
    return all_code
    
def update_hist_data_tosql(codes):
    #all_code=get_all_code(RAW_HIST_DIR)
    #pd.DataFrame.to_sql()
    stock_sql_obj=StockSQL()
    #stock_sql_test()
    #code_str='000987'
    #code_str='002678'
    histdata_last_df=stock_sql_obj.query_data(table='histdata_last')
    for code_str in codes:
        update_one_hist(code_str, stock_sql_obj,histdata_last_df)
    print('update completed')
        
    
if __name__ == '__main__':   
    
    codes=get_all_code(RAW_HIST_DIR)
    codes=['000987','000060','600750','600979','000875','600103','002678']
    update_hist_data_tosql(codes)

    