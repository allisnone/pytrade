# -*- coding:utf-8 -*-
from pdsql import *
if __name__ == '__main__':
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