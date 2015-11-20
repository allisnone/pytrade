# -*- coding:utf-8 -*-
'''
insertDBdata.py Created on Dec.18

@author: Vicky Zhao, Jason Zhang
'''
import logging
import pymysql 
#import MySQLdb        #for py2.7
#import common
import sys,time


sys.setrecursionlimit(1000000)     #maximum recursion depth exceeded

class Sqloperation(object):
    def __init__(self, host, port, user, passwd, db):#, charset='utf8'):
        self.host=host
        self.port=port
        self.user=user
        self.passwd=passwd
        self.db=db
        #self.charset=charset
        print(time.time())
        self.conn = pymysql.connect(
                                    host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    passwd=self.passwd,
                                    db=self.db)
                                    #charset=self.charset)
        print(time.time())
    def reconnect(self):
       
        #print 'reconnect==========',datetime.datetime.now()
        time.sleep(1)
        #print 'reconnect==========',datetime.datetime.now()
        try:
            if self.conn:
                self.close()
            print('Try to restart mysql connection...')
            self.conn = pymysql.connect(
                                        host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        passwd=self.passwd,
                                        db=self.db)
                                        #charset=self.charset)
            print('MySQL normal reconnected successfully!')
            print('restart directly completed')
            
        except:
            print('MySQL reconnected error!')
            self.reconnect() 
     
    def get_cursor(self):
        return self.conn.cursor()
   
    def query(self, sql):  
        try:
            cursor = self.get_cursor()
            cursor.execute(sql, None)
            result = cursor.fetchall() 
            self.conn.commit()

        except Exception as e:
            logging.error("mysql query error: %s", e)
            print('query^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            self.reconnect()
            return None
        finally:
            cursor.close()
        return result
    
    def execute(self, sql, param=None):
        cursor = self.get_cursor()
        try:
            cursor.execute(sql, param)
            self.conn.commit()
            affected_row = cursor.rowcount
        except Exception as e:
            logging.error("mysql execute error: %s", e)
            print('execute^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            self.reconnect()
            return 0
        finally:
            cursor.close()
        return affected_row

    def executemany(self, sql, params=None):
        cursor = self.get_cursor()
        try:
            cursor.executemany(sql, params)
            self.conn.commit()
            affected_rows = cursor.rowcount
        except Exception as e:
            logging.error("mysql executemany error: %s", e)
            print('executemany^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            self.reconnect()
            return 0
        finally:
            cursor.close()
        return affected_rows

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def __del__(self):
        self.close()
        
    
    def insert_data(self,sql,data):
        flag = self.executemany(sql, data) 
        #print('flag=',flag)
        if flag:
            print('Successful inserted data to DB!')
        else:
            print('No data inserted to DB.')
        return flag
    
    def update_data(self,sql,data=None):
        flag=0
        if data==None:
            flag = self.execute(sql)
        else:
            flag = self.executemany(sql,data)
        if flag:
            print('Successful updated data to DB!')
        else:
            print('No data updated to DB.')
        return flag
    """        
    def get_data(self, sql):
        tupledata = self.query(sql)
        return tupledata
    """
    
def form_sql(table_name,oper_type='query',select_field=None,where_condition=None,insert_field=None,update_field=None,set_value_str=None):
    """
    :param table_name: string type, db_name.table_name
    :param select_field: string type, like 'id,type,value'
    :param where_condition: string type, like 'field_value>50'
    :param insert_field: string type, like '(date_time,measurement_id,value)'
    :param set_field: string type, like 'value'
    :param set_value_str: string type, like '1000' or "'normal_type'"
    :return: sql string
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
    elif oper_type=='update' and where_condition and update_field and set_value_str:
        sql='update %s set %s='%(table_name,update_field)+ set_value_str + ' where '+  where_condition + ';'
    elif oper_type=='delete' and where_condition:
        sql='delete from %s'%table_name + ' where ' + where_condition + ';'
    else:
        pass
    return sql