# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pymysql 
import pandas as pd
import numpy as np
import tushare as ts
from pandas.io import sql

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
        data_frame.to_sql(table_name, self.engine, index=True)#encoding='utf-8')
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
    stock_sql_obj.insert_data(table, '(name)', data)
    print('update_data:')
    stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    #stock_sql_obj.update_data(table, 'name', "'陈五'", condition="name='王五'")
    print('delete_data')
    stock_sql_obj.delete_data(table, "name='陈五'")

#if __name__ == '__main__':
#    stock_sql_test()
    
    