# -*- coding:utf-8 -*-
'''
insertDBdata.py Created on Dec.18

@author: Vicky Zhao, Jason Zhang
'''
import logging
import pymysql as MySQLdb
#import MySQLdb        #for py2.7
#import common
import sys,time,datetime
from _mysql import result
from datetime import date
RECONNECT_COUNT=10
Operation_COUNT=10
TIMEOUT_COUNT=10

sys.setrecursionlimit(1000000)     #maximum recursion depth exceeded

class _MySQL(object):
    def __init__(self, host, port, user, passwd, db, charset='utf8'):
        self.host=host
        self.port=port
        self.user=user
        self.passwd=passwd
        self.db=db
        self.charset=charset
        self.conn = MySQLdb.connect(
                                    host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    passwd=self.passwd,
                                    db=self.db,
                                    charset=self.charset)
    
    def reconnect(self):
       
        #print 'reconnect==========',datetime.datetime.now()
        time.sleep(1)
        #print 'reconnect==========',datetime.datetime.now()
        try:
            if self.conn:
                self.close()
            print('Try to restart mysql connection...')
            self.conn = MySQLdb.connect(
                                        host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        passwd=self.passwd,
                                        db=self.db,
                                        charset=self.charset)
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

def insert_data(mysql,sql,data):
    flag = mysql.executemany(sql, data) 
    if flag == 1:
        print('Successful stored data to DB!')
    else:
        print('No data stored to DB.')
        
def update_data(mysql,sql,data=None):
    flag=0
    if data==None:
        flag = mysql.execute(sql)
    else:
        flag = mysql.executemany(sql,data)
    if flag == 1:
        print('Successful stored new data to DB!')
    else:
        print('No new data stored to DB.')
        
def get_data(mysql, sql):
    tupledata = mysql.query(sql)
    return tupledata
