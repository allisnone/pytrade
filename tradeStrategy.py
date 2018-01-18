# -*- coding:utf-8 -*-
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os,sys,time,platform

import tushare as ts
import json
import string

#import urllib.request, urllib.error, urllib.parse
import datetime
import threading
import smtplib

from pdSql_common import get_easyhistory_df
import tradeTime as tt
import easyquotation

ISOTIMEFORMAT='%Y-%m-%d %X'
#ISODATEFORMAT='%Y%m%d'
ISODATEFORMAT='%Y-%m-%d'

#ROOT_DIR='C:/work/stockAnalyze'
ROOT_DIR="C:/中国银河证券海王星/T0002"

RAW_HIST_DIR=ROOT_DIR+'/export/'
HIST_DIR=ROOT_DIR+'/hist/'
HIST_FILE_TYPE='.csv'


#get the all file source data in certain DIR
def get_all_code(hist_dir='C:/hist/day/data/'):
    all_code=[]
    for filename in os.listdir(hist_dir):#(r'ROOT_DIR+/export'):
        """
        code=filename[:-4]
        if len(code)==6:
            all_code.append(code)
        """
        code = filename.split('.')
        if len(code)>=1:
            all_code.append(code[0])
    return all_code

#get the history raw data for certain code: ['date','open','high','low','close','volume','amount']
"""data from 'export' is update from trade software everyday """
def get_raw_hist_df(code_str,latest_count=None):
    file_type='csv'
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    column_list=['date','open','high','low','close','volume','amount']
    #print('file_name=',file_name)
    df_0=pd.read_csv(file_name,names=column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
    #print df_0
    #delete column 'amount' and delete the last row
    del df_0['amount']
    df=df_0.ix[0:(len(df_0)-2)]
    #print df
    
    """"check"""
    df= df.set_index('date')
    #df.index.name='date'
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    df.index.name=this_time_str
    """check"""
    hist_dir=ROOT_DIR+'/hist/'
    file_type='csv'
    file_name=hist_dir+code_str+'.'+file_type
    #print df
    df.to_csv(file_name)
    hist_dir=ROOT_DIR+'/update/'
    file_name=hist_dir+code_str+'.'+file_type
    df.to_csv(file_name)
    #column_list=['date','open','high','low','close','volume']
    if latest_count!=None and latest_count<len(df):
        df=df.tail(latest_count)
    return df

def write_hist_index():
    """
    hist_sh_df=ts.get_hist_data('sh')
    hist_sz_df=ts.get_hist_data('sz')
    hist_hs300_df=ts.get_hist_data('hs300')
    hist_sz50_df=ts.get_hist_data('sz50')
    hist_zxb_df=ts.get_hist_data('zxb')
    hist_cyb_df=ts.get_hist_data('cyb')
    """
    #print datetime.datetime.now()
    index_list=['sh','sz','zxb','cyb','hs300','sz50']
    index_dir=ROOT_DIR+'/index/'
    file_type='csv'
    for index_str in index_list:
        print('Getting hist data for %s index ...' % index_str)
        file_name=index_dir+index_str+'.'+file_type
        index_df=ts.get_hist_data(index_str)
        index_df.to_csv(file_name)
        print('Getting hist data for %s index is completed' % index_str)
    
    #print datetime.datetime.now()
def get_hist_index(index_str):
    index_dir=ROOT_DIR+'/index/'
    file_type='csv'
    index_list=['sh','sz','zxb','cyb','hs300','sz50']
    file_name=index_dir+index_str+'.'+file_type
    column_list=['date','open','high','close','low','volume','price_change','p_change','ma5','ma10','ma20','v_ma5','v_ma10','v_ma20']
    index_df=pd.read_csv(file_name)#,names=column_list)
    index_df= index_df.set_index('date')
    return index_df

def get_file_timestamp(file_name):
    file_mt_str=''
    try:
        file_mt= time.localtime(os.stat(file_name).st_mtime)
        file_mt_str=time.strftime("%Y-%m-%d %X",file_mt)
    except:
        #file do not exist
        pass
    return file_mt_str

#get the history data for certain code: ['date','open','high','low','close','volume']
def get_hist_df(code_str,analyze_type,latest_count=None):
    target_dir=''
    if analyze_type=='history':
        target_dir=ROOT_DIR+'/hist/'
    else:
        if analyze_type=='realtime':
            target_dir=ROOT_DIR+'/update/'
        else:
            pass
    file_type='csv'
    code_str=str(code_str)
    file_name=target_dir+code_str+'.'+ file_type
    #print 'file_name:',file_name
    data={}
    column_list=['date','open','high','low','close','volume']#,'amount']
    df=pd.DataFrame(data=data,columns=column_list)
    now_time=datetime.datetime.now()
    file_mt_str=now_time.strftime("%Y-%m-%d %X")
    try:
        hist_df=pd.read_csv(file_name,names=column_list, header=0)
        #column_list=['date','open','high','low','close','volume']
        """"check"""
        #df= df_0.set_index('date')
        #df=df_0.ix[:'2015-05-22']
        #df.index.name='date'
        """check"""
        default_count=10000
        if latest_count!=None and latest_count<len(hist_df):
            default_count=latest_count
        df=hist_df.tail(min(default_count,len(hist_df)))
            #df=df.set_index('date')
        file_mt_str= get_file_timestamp(file_name)
    except:
        pass
    return df,file_mt_str
  

def f_code_2sybol(code_f):
    #print 'code_f:',code_f
    s1=str(code_f)
    #print 's1=',s1
    zero_str={6:'',5:'0',4:'00',3:'000',2:'0000',1:'00000'} #,2:'00000',1:'00000'}
    le_n=len(s1)
    code_str=zero_str[le_n]+s1 #[:-2]
    #print 'code_str=',code_str
    return code_str

    #is_trade_time=now_timestamp>start_timestamp and 
def get_ma_list(close_list,ma_num):
    ma_list=[]
    i=0
    while (i<len(close_list)):
        k=0
        if i<ma_num:
            temp_list=close_list[0:(i+1)]
            ma=round(round(sum(temp_list),2)/len(temp_list),2)
            ma_list.append(ma)
        else:
            temp_list=close_list[(i-(ma_num-1)):(i+1)]
            ma=round(round(sum(temp_list),2)/ma_num,2)
            ma_list.append(ma)
        i=i+1
    #print ma_list,len(ma_list)
    return ma_list

def find_boduan(data_list,min_range_rate=0.10):
    
    count=len(data_list)
    max=data_list[0]
    min=data_list[0]
    split_list=[]
    indx=1
    max_index=0
    min_index=0
    action=''
    found_min=False
    found_max=False
    print(data_list)
    while indx<(count-1) and indx>=1:
        value=data_list[indx]
        print(max,min,value)
        up_bord=min*(1+min_range_rate)
        if min<0:
            up_bord=min*(1-min_range_rate)
        down_bord=max*(1-min_range_rate)
        if max<0:
            down_bord=max*(1+min_range_rate)
        print(up_bord,down_bord)
        if value>up_bord:
            action='find_max'
            print(found_min)
            if not found_min:
                split_list.append(min)
                min=value
                found_min=True
                found_max=False
            else:
                if value>max:
                    max=value
                    max_index=indx
                    found_max=False
                if value<min:
                    min=value
                    min_index=indx
                    found_min=False
        elif value<down_bord:
            action='find_min'
            if not found_max:
                split_list.append(max)
                max=value
                found_max=True
                found_min=False
            else:
                if value>max:
                    max=value
                    max_index=indx
                    found_max=False
                if value<min:
                    min=value
                    min_index=indx
                    found_min=False
        else:
            if value>max:
                max=value
                max_index=indx
                found_max=False
            if value<min:
                min=value
                min_index=indx
            #found_min=False
            #found_max=False
        indx=indx+1
    #split_list.append(lst_value)
    return split_list

def find_boduan0(data_list):
    indx=0
    count=len(data_list)
    max=data_list[0]
    min=data_list[0]
    split_list=[]
    split_list.append(max)
    indx=1
    action=''
    if data_list[0]>data_list[1]:
        action='find_min'
    else:
        action='find_max'
    lst_value=data_list[(count-1)]
    while indx<(count-1) and indx>=1:
        value=data_list[indx]
        #print value,action,indx
        if action=='find_max':
            #print min,max
            if value>=max:
                max=value
                action='find_max'
            else:
                last_value=data_list[indx-1]
                min=value
                max=last_value
                split_list.append(last_value)
                action='find_min'
                pass
        else:
            if action=='find_min':
                #print min,max
                if value<=min:
                    min=value
                    action='find_min'
                else:
                    last_value=data_list[indx-1]
                    max=value
                    min=last_value
                    split_list.append(last_value)
                    action='find_max'
                    pass
            else:
                pass
        indx=indx+1
    split_list.append(lst_value)
    return split_list

def specify_rate_range(init_rate=-1.5,rate_interval=0.5,range_num=10):
    """
    return the range to seperate the rate in class 
    """
    rate_list=[]
    for i in range(0,range_num):
        rate=round(init_rate+i*rate_interval,1)
        rate_list.append(rate)
        if rate>10.95 or rate <-9.0:
            break
    return rate_list

def get_today_df():
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    """
    latest_trade_day=tradeTime.get_latest_trade_date()
    latest_trade_end=latest_trade_day + ' 15:00:00'
    latest_trade_before_start=latest_trade_day + ' 09:15:00'
    """
    latest_trade_day_str=tradeTime.get_latest_trade_date()
    latest_trade_time_str=latest_trade_day_str + ' 15:00:00'
    pre_name='all'
    #if profix_name != None:
    #    pre_name=profix_name
    file_name=ROOT_DIR+'/data/%s.csv'%(pre_name+latest_trade_day_str)
    file_time_str=get_file_timestamp(file_name)
    
    data={}
    column_list=['code','changepercent','trade','open','high','low','settlement','volume','turnoverratio']
    today_df=pd.DataFrame(data,columns=column_list)#,index=['
    if not tradeTime.is_trade_time_now():
        if file_time_str:
            #if file_time_str>=latest_trade_day_str+' 13:00:00':
            #print '---------------1'
            today_df=read_today_df(file_name)
            today_df.index.name=latest_trade_time_str
            #return today_df,file_time_str
        else:
            #print '---------------2'
            today_df=ts.get_today_all()
            del today_df['name']
            today_df=write_today_df(file_name,today_df)
            today_df= today_df.set_index('code')
            file_time_str=get_file_timestamp(file_name)
            today_df.index.name=latest_trade_time_str
            #return today_df,this_time_str
    else:
        # read the real time update data on today
        #print '---------------3'
        today_df=ts.get_today_all()
        del today_df['name']
        today_df= today_df.set_index('code')
        today_df.index.name=this_time_str
        #return today_df,this_time_str
    
    today_df=today_df.astype(float)
    today_df.insert(6, 'h_change', (100*(today_df.high-today_df.settlement)/today_df.settlement).round(2))
    today_df.insert(7, 'l_change', (100*(today_df.low-today_df.settlement)/today_df.settlement).round(2))
    today_df['atr']=np.where(today_df['high']-today_df['low']<today_df['high']-today_df['settlement'],(today_df['high']-today_df['settlement'])/today_df['settlement']*100.0,(today_df['high']-today_df['low'])/today_df['settlement']*100.0) #temp_df['close'].shift(1)-temp_df['low'])
    today_df['atr']=np.where(today_df['atr']<today_df['settlement']-today_df['low'],(today_df['settlement']-today_df['low'])/today_df['settlement']*100.0,today_df['atr'])
    return today_df,this_time_str

def write_today_df(file_name,today_df):
    #latest_trade_day_str=tradeTime.get_latest_trade_date()
    #today_df=ts.get_today_all()
    #del today_df['name']
    #today_df1=today_df.set_index('code')
    #pre_name='all'
    #file_name=ROOT_DIR+'/data/%s.csv'%(pre_name+latest_trade_day_str)
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    today_df.index.name=this_time_str
    today_df.to_csv(file_name) #,encoding='GB18030')
    return today_df
        
def read_today_df(file_name):
    column_list=['code','changepercent','trade','open','high','low','settlement','volume','turnoverratio']
    
    today_df=pd.read_csv(file_name,names=column_list)# header=1)
    #all_codes_f=today_df['code'].values.tolist()
    #print all_codes_f
    """
    all_codes=[]
    if all_codes_f:
        for code_f in all_codes_f:
            code=f_code_2sybol(code_f)
            all_codes.append(code)
    all_codes=all_codes[1:]
    today_df['code']=pd.Series(all_codes)
    """
    df= today_df.set_index('code')
    #this_time=datetime.datetime.now()
    #this_time_str=this_time.strftime('%Y-%m-%d %X')
    #print 'read_today_df,index.name',df.index.name
   # df.index.name=this_time_str
    df=df.ix[1:]
    #print df
    return df

def update_one_hist(code_sybol,today_df,today_df_update_time):
    #latest_trade_day_str=tradeTime.get_latest_trade_date()
    #print latest_trade_day_str
    #today_df_update_time=today_df.index.name
    #print 'today_df_update_time=',today_df_update_time
    #print today_df
    today_str=today_df_update_time[:10]
    #print 'today_str=',today_str
    hist_df,file_mt=get_hist_df(code_sybol,'history')
    #print 'hist_df0=',hist_df
    #print 'file_mt=',file_mt
    date_list=hist_df['date'].values.tolist()
    #print date_list
    last_hist_date=date_list[-1]
    #print 'last_hist_date=',last_hist_date
    if file_mt>today_df_update_time:
        #print 'update_one_hist1, if1'
        pass
    else:
        #print 'update_one_hist, else1'
        if last_hist_date==today_str:
            hist_df=hist_df.head(len(hist_df)-1)
            #print 'update_one_hist1,hist_df1=',hist_df
            print(last_hist_date)
        else:
            #print 'update_one_hist1, else2'
            pass
        today_df=today_df.astype(float)
        code_value=today_df.ix[code_sybol].values.tolist()
        open_price=today_df.ix[code_sybol].open
        high_price=today_df.ix[code_sybol].high
        low_price=today_df.ix[code_sybol].low
        current_price=today_df.ix[code_sybol].trade
        last_price=today_df.ix[code_sybol].settlement
        volume=today_df.ix[code_sybol].volume
        """
        open_price=round(today_df.ix[code_sybol]['open'].mean(),2)
        high_price=round(today_df.ix[code_sybol]['high'].mean(),2)
        low_price=round(today_df.ix[code_sybol]['low'].mean(),2)
        current_price=round(today_df.ix[code_sybol]['trade'].mean(),2)
        last_price=round(today_df.ix[code_sybol]['settlement'].mean(),2)
        volume=round(today_df.ix[code_sybol]['volume'].mean(),2)
        """
        #hist_value=[code_value[3],code_value[4],code_value[5],code_value[2],code_value[7]]
        data={'date':[today_str],'open':open_price,'high':high_price,'low':low_price,'close':current_price,'volume':volume}
        column_list=['date','open','high','low','close','volume']
        hist_today_df=pd.DataFrame(data,columns=column_list)#,index=['2015-05-15'])
        hist_df=hist_df.append(hist_today_df,ignore_index=True)
        #print hist_today_df
        #print hist_df
        #print hist_df_updated
        hist_df= hist_df.set_index('date')
        #hist_df_updated.index.name='date'
        hist_df.index.name=today_df_update_time
        #print hist_df.index.name
        #print hist_df
        #print 'update_one_hist:',hist_df_updated
        update_file_name=ROOT_DIR+'/update/%s.csv'% code_sybol
        hist_df.to_csv(update_file_name)
        hist_file_name=ROOT_DIR+'/hist/%s.csv'% code_sybol
        if tradeTime.is_trade_time_now0(tradeTime.get_latest_trade_date()):
            pass
        else:
            hist_df.to_csv(hist_file_name)
    return hist_df
    
def update_all_hist(today_df,today_df_update_time):
    print('Star update history stock data...')
    hist_all_code=get_all_code(ROOT_DIR+'/hist')
    #print 'update_all_hist:',hist_all_code
    all_codes=today_df.index.values.tolist()
    #for code_sybol in hist_all_code:
    latest_trade_date=tradeTime.get_latest_trade_date()
    #all_codes=['000001']
    #hist_all_code=['000001']
    print('update_all_hist,all_codes=', all_codes)
    print('update_all_hist,hist_all_code=', hist_all_code)
    for code_sybol in all_codes:
        
        if code_sybol in hist_all_code:
            updated_df=update_one_hist(code_sybol, today_df,today_df_update_time)
            """
            file_name=ROOT_DIR+'/update/%s.csv'% code_sybol
            hist_file_name=ROOT_DIR+'/hist/%s.csv'% code_sybol
            #updated_df.to_csv(file_name) #,encoding='GB18030')
            if tradeTime.is_trade_time_now0(latest_trade_date):
                pass
            else:
                #updated_df.to_csv(hist_file_name)
                pass
            """
        else:
            #to get hist data update
            print('update_all_hist----else')
            pass
    print('Completed history stock data update!')
    return

#update all hist code from export
def init_all_hist_from_export():
    raw_hist_code=get_all_code(RAW_HIST_DIR)
    hist_code=get_all_code(HIST_DIR)
    except_code_list=list(set(raw_hist_code).difference(set(hist_code)))
    print(except_code_list) 
    print(len(hist_code))
    print(len(raw_hist_code))
    """update all hist data from export"""
    if len(hist_code)==0 or (len(hist_code)!=0 and len(hist_code)!=(len(raw_hist_code))):
        print('Begin pre-processing  the hist data')
        for code_sybol in raw_hist_code:
            get_raw_hist_df(code_sybol)
        print('pre-processing completed')
    else:
        pass
    
    """update all hist data based on the new 'today' data"""
    #update_all_hist(get_today_df())
    
def get_top_list():
    update_file_name=ROOT_DIR+'/result/top_2015-07-08.csv'
    df=ts.top_list('2015-07-08')
    df.to_csv(update_file_name,encoding='GB18030')
    return

def get_timestamp(date_time_str):
    #date_time_str='2015-07-20 13:20:01'
    return time.mktime(time.strptime(date_time_str, ISOTIMEFORMAT))

def get_delta_seconds(start_time, end_time):
    #start_time,end_time: datetime.datetime Object
    delta=end_time-start_time
    delta_second=delta.days*24*3600+delta.seconds+delta.microseconds*10**(-6)
    return delta_second

def send_mail(alarm_list):
    # alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
    if alarm_list:
        mailto_list=['104450966@qq.com'] 
        mail_host='smtp.163.com'
        mail_user='zgx20022002@163.com'
        mail_pass='821853Zgx'  
        mail_postfix="qq.com"
        me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
        """
        print 'Setting MIMEText'
        CT=open('content.txt','r')  #read the txt
        content=CT.read().decode('utf-8')
        msg=MIMEText(content.encode('utf8'),_subtype='html')
        CT.close()#close tst
        """
        sub=alarm_list[2]+ ' for '+ alarm_list[0]+' :' +alarm_list[3]
        #date_time='%s'%alarm_list[1]
        content=alarm_list[1] + '\n ' + alarm_list[4]
        msg = MIMEText(content)  
        msg['Subject'] = sub  
        msg['From'] = mail_user 
        msg['To'] = ";".join(mailto_list)
        try:  
            #s = smtplib.SMTP()
            s=smtplib.SMTP_SSL(mail_host,465)
            s.login(mail_user,mail_pass)  
            s.sendmail(mail_user, mailto_list, msg.as_string())  
            s.close()  
        except Exception as e:  
            print(str(e))
    else:
        pass

def get_interval(interval):
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    latest_trade_day=tradeTime.get_latest_trade_date()
    morning_time0=datetime.datetime.strptime(latest_trade_day+' 09:30:00','%Y-%m-%d %X')
    morning_time1=datetime.datetime.strptime(latest_trade_day+' 11:30:00','%Y-%m-%d %X')
    noon_time0=datetime.datetime.strptime(latest_trade_day+' 13:00:00','%Y-%m-%d %X')
    noon_time1=datetime.datetime.strptime(latest_trade_day+' 15:00:00','%Y-%m-%d %X')
    next_morning_time0=morning_time0+datetime.timedelta(days=1)
    #print 'now_time=',this_time
    #this_time=datetime.datetime(2015,7,21,13,25,20,0)
    #print my_df
    if this_time>morning_time1 and this_time<noon_time0 :
        interval_time=noon_time0-this_time
        interval=interval_time.days*24*3600+interval_time.seconds
        print('Have a lest druing the noon, sleep %s seconds...'%interval)
    else:
        if this_time<=morning_time0:
            interval_time=morning_time0-this_time
            interval=interval_time.days*24*3600+interval_time.seconds
            print('Market does not start yet in the morning, sleep %s seconds...'%interval)
        else:
            if this_time>=noon_time1:
                interval_time=next_morning_time0-this_time
                interval=interval_time.days*24*3600+interval_time.seconds
                market_analyze_today()
                #market_analyze_today()
                write_hist_index()
                print('Market will start in next morning, sleep %s seconds...'%interval)
            else:
                if (this_time>=morning_time0 and this_time<=morning_time1)  or (this_time>=noon_time0 and this_time<=noon_time1):
                    interval=interval
"""
def filter_df_by_date(raw_df,from_date_str,to_date_str):  #index of df should be date:
    #from_date_str: '2015-05-16'
    if from_date_str>to_date_str:
        temp_date_str=from_date_str
        from_date_str=to_date_str
        to_date_str=temp_date_str
    else:
        pass
    #self.h_df.set_index('date')
   
    date_index=raw_df.index.values.tolist()
    #print date_index

    df=raw_df[from_date_str:to_date_str]
    return df
"""
def filter_df_by_date(raw_df,from_date_str,to_date_str):  #index of df should not be date:
    #from_date_str: '2015-05-16'
    if from_date_str>to_date_str:
        temp_date_str=from_date_str
        from_date_str=to_date_str
        to_date_str=temp_date_str
    else:
        pass
    #self.h_df.set_index('date')
    """
    date_index=raw_df.index.values.tolist()
    #print date_index
    if date_index[0]>from_date_str:
        from_date_str=date_index[0]
    else:
        pass
    if date_index[-1]<to_date_str:
        to_date_str=date_index[-1]
    else:
        pass
    """
    crit1=raw_df.date>=from_date_str 
    crit2=raw_df.date<=to_date_str
    df=raw_df[crit1 & crit2]
    return df
def market_analyze_today():
    #init_all_hist_from_export()
    latest_trade_day=tradeTime.get_latest_trade_date()
    today_df,df_time_stamp=get_today_df()
    out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    market=Market(today_df)
    #update_all_hist(today_df,df_time_stamp)
    #actual_101_list,success_101_rate=market.get_101()
    market.get_hist_cross_analyze()
    market.get_realtime_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('realtime')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    #print 'df_101=',df_101
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    #print star_df
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('history', star_list)
    #print code_10
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    #print df_10
    filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
    df_10.to_csv(filename)
    #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    #print 'potential_101_list=',potential_101_list
    realtime_101_list,success_101_rate=market.get_101('realtime',code_10)
    sys.stdout=sys.__stdout__
    output.close()
    print('market_analyze completed for today.')
    
class Stockhistory:
    def __init__(self,code_str,ktype, test_num=0,source='easyhistory',rate_to_confirm=0.01):
        self.code=code_str
        self.ktype=ktype
        self.DEBUG_ENABLED=False
        #self.h_df=pds.get_raw_hist_df(code_str)             #the history data frame data set
        """
        self.h_df = None  #ta_lib  indicator
        if source=='yh' or source=='YH':
            self.h_df = pds.get_yh_raw_hist_df(code_str)
            self.h_df['amount'] = self.h_df['rmb']
        else:
            self.h_df=pds.get_easyhistory_df(code_str)  #ta_lib  indicator
        """
        self.h_df= get_easyhistory_df(code_str,source)  #ta_lib
        #print(self.h_df)
        self.alarm_trigger_timestamp=0
        self.max_price=-1
        self.min_price=1000
        self.alarm_category='normal'
        self.realtime_stamp=0
        self.temp_hist_df=self._form_temp_df()
        self.test_num = test_num
        self.rate_to_confirm = rate_to_confirm
        if test_num ==0 and isinstance(test_num, int):
            self.test_num = len(self.h_df)
        #self.average_high=0
        #self.average_low=0
    def set_code(self,code_str):
        self.code = code_str
        
        
    def data_feed(self, k_data, feed_type='hist'):
        if feed_type=='hist':
            self.h_df = k_data
        elif feed_type=='temp':
            self.temp_hist_df = k_data
        else:
            pass
        
        """
        if k_data==None:
            self.h_df = pds.get_raw_hist_df(code_str)
            if feed_type=='temp':
                self.temp_hist_df = self._form_temp_df()
            else:
                pass
        else:
            if feed_type=='hist':
                self.h_df = k_data
            elif feed_type=='temp':
                self.temp_hist_df = k_data
            else:
                pass
        """
            
    def get_all_symbols(self):
        return
    
    def get_all_on_trade_symbols(self):
        return
    
    def filter(self, filter_type, symbols=None):
        target_symbols=[]
        if symbols:
            if isinstance(symbols, str):
                target_symboles = [symbols]
            elif isinstance(symbols, str):
                target_symboles = symbols
            else:
                pass
        else:
            target_symboles = self.get_all_symbols()
        stock_hist_anlyse = tds.Stockhistory(code_str='000001',ktype='D')
        for symbol in target_symboles:
            pass    
        
        return
        
    def is_island_reverse_up(self,gap_rate=0.005):
        """
        temp_df = self.temp_hist_df
        temp_df['jump_max']=np.where(temp_df['close']>temp_df['open'],temp_df['close'],temp_df['open'])
        temp_df['jump_min']=np.where(temp_df['close']<temp_df['open'],temp_df['close'],temp_df['open'])
        temp_df['jump_up']=np.where(temp_df['jump_min']>(1+gap_rate)*temp_df['jump_max'].shift(1),
                                    temp_df['jump_min']/temp_df['jump_max'].shift(1)-1,0)
        temp_df['jump_down']=np.where(temp_df['jump_max']<(1-gap_rate)*temp_df['jump_min'].shift(1),
                                      1-temp_df['jump_min'].shift(1)/temp_df['jump_max'],0)
        temp_df['gap'] = (temp_df['jump_up'] + temp_df['jump_down']).round(3)
        temp_df['island'] = np.where(temp_df['gap']*temp_df['gap'].shift(1)<0,temp_df['gap'],0)
        island_df=temp_df[['date','p_change','gap','star','island','atr_in']]
        print(island_df[island_df.island!=0])
        print(island_df.tail(50))
        del temp_df['jump_max']
        del temp_df['jump_min']
        del temp_df['jump_up']
        del temp_df['jump_down']
        """
        return 
    
    
    def get_realtime_k_data(self):
        #https://github.com/shidenggui/easyquotation
        quotation=easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
        #quotation = easyquotation.use('lf') # ['leverfun', 'lf'] #免费十档行情
        index_code=['999999','399001','399002','399003','399005']
        print(quotation.stocks(self.code))
        k_data=quotation.stocks(self.code)
        is_stop_trade = False
        if k_data:
            k_data=k_data[self.code]
            is_stop_trade = not k_data['volume'] and not k_data['high']
        """
        {'000680': {'bid4_volume': 19000, 'high': 5.76, 'bid2_volume': 119096, 'sell': 5.7, 'bid2': 5.68, 'volume': 202358001.01,
                    'ask4_volume': 143800, 'ask5_volume': 153400, 'ask1': 5.7, 'bid1_volume': 110500, 'bid3_volume': 20817, 
                    'ask3_volume': 337408, 'open': 5.41, 'ask3': 5.72, 'turnover': 36100590, 'ask2': 5.71, 'ask1_volume': 210213,
                    'ask2_volume': 217367, 'bid4': 5.66, 'ask5': 5.74, 'date': '2016-04-22', 'low': 5.37, 'time': '15:05:56', 
                    'bid3': 5.67, 'name': '山推股份', 'now': 5.69, 'ask4': 5.73, 'bid5': 5.65, 'buy': 5.69, 'bid1': 5.69, 
                    'close': 5.44, 'bid5_volume': 31000}
         }
         """
        return k_data   
    
    def update_realtime_hist_df(self,k_data=None):
        """
        实时更新当前K线到历史数据
        """
        #k_data=[date,open,high,low,close,volume,amount]
        k_data = self.get_realtime_k_data()
        #print(k_data)
        if self.h_df.empty:
            return
        latest_day=self.h_df.tail(1)['date'].values.tolist()[0]
        latest_index=self.h_df.tail(1).index.values.tolist()[0]
        #print('latest_day=',latest_day)
        #print(self.h_df.tail(10))
        if k_data and len(k_data)>=7:
            this_trade_time =  k_data['date'] + ' ' +  k_data['time']
            pass_time_rate = tt.get_pass_trade_time()
            predict_volume_rate = 1.0
            if pass_time_rate:
                predict_volume_rate = pass_time_rate
            column_list=['date','open','high','low','close','volume','amount']
            #this_k_data={'date': k_data[0],'open': k_data[1],'high': k_data[2],'low': k_data[3],'close': k_data[4],'volume': k_data[5],'amount': k_data[6]}
            this_k_data={'date': k_data['date'],'open': k_data['open'],'high': k_data['high'],'low': k_data['low'],'close': k_data['now'],'volume': k_data['turnover']*predict_volume_rate,'amount': k_data['volume']*predict_volume_rate}
            this_k_df=pd.DataFrame(data=this_k_data,columns=column_list,index=[latest_index+1])
            #print(this_k_df)
            #print(k_data['date'])
            if k_data['date']>latest_day:
                pass
            elif k_data['date']==latest_day:
                this_k_df=pd.DataFrame(data=this_k_data,columns=column_list,index=[latest_index])
                self.h_df=self.h_df.head(len(self.h_df)-1)
            else:
                return
            self.h_df=self.h_df.append(this_k_data,ignore_index=True)
            #print(self.h_df.tail(10))
        return
    
    def get_last_k_data(self,last_num=None):
        if self.temp_hist_df.empty:
            return
        last_n=1
        if last_num!=None:
            last_n=last_num
        temp_hist_df_len=len(self.temp_hist_df)
        last_df=self.temp_hist_df.head(temp_hist_df_len-last_n+1).tail(1)
        ma5=last_df.iloc[0].ma5
        ma10=last_df.iloc[0].ma10
        ma20=last_df.iloc[0].ma20
        ma30=last_df.iloc[0].ma30
        ma60=last_df.iloc[0].ma60
        ma120=last_df.iloc[0].ma120
        change=last_df.iloc[0].p_change
        open=last_df.iloc[0].open
        close=last_df.iloc[0].close
        high=last_df.iloc[0].high
        low=last_df.iloc[0].low
        volume=last_df.iloc[0].volume
        atr=last_df.iloc[0].atr
        score=last_df.iloc[0].score
        v_ma5=last_df.iloc[0].v_ma5
        v_ma10=last_df.iloc[0].v_ma10
        v_ma30=last_df.iloc[0].v_ma30
        v_ma60=last_df.iloc[0].v_ma60
        return open,high,low,close,volume,change,ma5,ma10,ma30,ma60,ma120,v_ma5,v_ma10,v_ma30,v_ma60
    
    def is_great_drop_then_high_open(self):
        great_drop_rate=-3.0
        if self.temp_hist_df.empty:
            return 0.0
        temp_df=self.temp_hist_df.tail(2)
        ma5_0=temp_df.tail(1).iloc[0].ma5
        ma10_0=temp_df.tail(1).iloc[0].ma10
        ma20_0=temp_df.tail(1).iloc[0].ma20
        last_change=temp_df.tail(1).iloc[0].p_change
        ma5_1=temp_df.tail(1).iloc[1].ma5
        ma10_1=temp_df.tail(1).iloc[1].ma10
        ma20_1=temp_df.tail(1).iloc[1].ma20
        change=temp_df.tail(1).iloc[1].p_change
        close=temp_df.tail(1).iloc[1].close
        open=temp_df.tail(1).iloc[1].open
        return 0.0
    
    def get_price_score(self):
        if self.temp_hist_df.empty:
            return 0.0
        temp_df=self.temp_hist_df.tail(2)
        ma5_0=temp_df.tail(1).iloc[0].ma5
        ma10_0=temp_df.tail(1).iloc[0].ma10
        ma20_0=temp_df.tail(1).iloc[0].ma20
        ma5_1=temp_df.tail(1).iloc[1].ma5
        ma10_1=temp_df.tail(1).iloc[1].ma10
        ma20_1=temp_df.tail(1).iloc[1].ma20
        close=temp_df.tail(1).iloc[1].close
        open=temp_df.tail(1).iloc[1].open
        return 0.0
    
    
    def get_market_score0(self,short_turn_weight=None,k_data=None):
        ma_type='ma5'
        temp_df=self.temp_hist_df
        if temp_df.empty:
            return 0,0,0
        if k_data!=None:
            update_one_hist(code_sybol, today_df, today_df_update_time)
            temp_df=self._form_temp_df()
        if len(temp_df)<5:
            return 0.0,0.0
        ma_offset=0.002
        WINDOW=3
        ma_type_list=['ma5','ma10','ma20','ma30','ma60','ma120']
        ma_weight=[0.3,0.2,0.2,0.1,0.1,0.1]
        short_weight=0.7
        ma_seq_score={'ma5_o_ma10':0.5,'ma10_o_ma30':0.3,'ma30_o_ma60':0.2}
        ma_cross_score={'ma5_c_ma10':0.75,'ma10_c_ma30':0.5,'ma30_c_ma60':0.3}
        if short_turn_weight!=None:
            short_weight=short_turn_weight
        """Get MA score next"""
        for ma_type in ma_type_list:
            ma_sum_name='sum_o_'
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])<-ma_offset*temp_df['close'].shift(1),-1,temp_df['c_o_ma']) #-1 for bellow ma
            ma_sum_name=ma_sum_name+ma_type
            #temp_df[ma_sum_name] = pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW).round(2)
            if '3.5' in platform.python_version():
                temp_df[ma_sum_name] = temp_df['c_o_ma'].rolling(window=5,center=False).mean().round(2)
            else:
                temp_df[ma_sum_name] = np.round(pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW), 2)
            del temp_df['c_o_ma']
            temp_df[ma_sum_name]=temp_df[ma_sum_name]+(temp_df[ma_sum_name]-temp_df[ma_sum_name].shift(1))
            
        temp_df['ma_score0']=(short_weight*ma_weight[0]+(1-short_weight)*ma_weight[5])*temp_df['sum_o_ma5']\
        +(short_weight*ma_weight[1]+(1-short_weight)*ma_weight[4])*temp_df['sum_o_ma10']\
        +(short_weight*ma_weight[2]+(1-short_weight)*ma_weight[3])*temp_df['sum_o_ma20']\
        +(short_weight*ma_weight[3]+(1-short_weight)*ma_weight[2])*temp_df['sum_o_ma30']\
        +(short_weight*ma_weight[4]+(1-short_weight)*ma_weight[1])*temp_df['sum_o_ma60']\
        +(short_weight*ma_weight[5]+(1-short_weight)*ma_weight[1])*temp_df['sum_o_ma120']
        #temp_df['ma_s_score']=0.1*temp_df['sum_o_ma5']+0.1*temp_df['sum_o_ma10']+0.1*temp_df['sum_o_ma20']+0.2*temp_df['sum_o_ma30']+0.2*temp_df['sum_o_ma60']+0.3*temp_df['sum_o_ma120']
        del temp_df['sum_o_ma5']
        del temp_df['sum_o_ma10']
        del temp_df['sum_o_ma20']
        del temp_df['sum_o_ma30']
        del temp_df['sum_o_ma60']
        del temp_df['sum_o_ma120']
        """Get MA trend score next"""
        ma_trend_score=0.0
        for ma_o_name in ma_seq_score.keys():
            ma_name_list=ma_o_name.split('_')
            s_ma_name=ma_name_list[0]
            l_ma_name=ma_name_list[2]
            ma_cross_name=ma_o_name.replace('o','c')
            temp_df[ma_o_name]=np.where(temp_df[s_ma_name]>temp_df[l_ma_name],ma_seq_score[ma_o_name],-ma_seq_score[ma_o_name])
            temp_df[ma_cross_name+'_d']=np.where((temp_df[s_ma_name]<=temp_df[l_ma_name]) & 
                                                 (temp_df[s_ma_name].shift(1)>temp_df[l_ma_name].shift(1)),-ma_cross_score[ma_cross_name],0)
            temp_df[ma_cross_name+'_u']=np.where((temp_df[s_ma_name]>=temp_df[l_ma_name]) &
                                                  (temp_df[s_ma_name].shift(1)<temp_df[l_ma_name].shift(1)),ma_cross_score[ma_cross_name],0)
            temp_df[ma_cross_name]=temp_df[ma_cross_name+'_d']+temp_df[ma_cross_name+'_u']
            del temp_df[ma_cross_name+'_d']
            del temp_df[ma_cross_name+'_u']
        ma_o_name_list=ma_seq_score.keys()
        ma_c_name_list=ma_cross_score.keys()
        temp_df['ma_trend_score']=temp_df['ma5_o_ma10']+temp_df['ma10_o_ma30']+temp_df['ma30_o_ma60']\
        +temp_df['ma5_c_ma10']+temp_df['ma10_c_ma30']+temp_df['ma30_c_ma60']
        temp_df['ma_score']=temp_df['ma_score0']+temp_df['ma_trend_score']
        del temp_df['ma5_o_ma10']
        del temp_df['ma10_o_ma30']
        del temp_df['ma30_o_ma60']
        """
        del temp_df['ma5_c_ma10']
        del temp_df['ma10_c_ma30']
        del temp_df['ma30_c_ma60']
        """
        """Get K data trend score next"""
        great_high_open_rate = 1.0
        great_low_open_rate = -1.5
        recent_k_num = 120
        temp_df1=temp_df.fillna(0).tail(recent_k_num)
        extreme_rate = 0.8
        temp_df1['o_change']=(temp_df1['o_change']).round(1)
        o_change_list=temp_df1['o_change'].values.tolist()
        great_high_open_rate,great_low_open_rate=self.get_extreme_change(o_change_list,rate=extreme_rate)
        print('great_high_open_rate=%s,great_low_open_rate=%s' %(great_high_open_rate,great_low_open_rate))
        
        temp_df['gt_o_h']=np.where(temp_df['o_change']>great_high_open_rate,(temp_df['o_change']/great_high_open_rate-1),0)
        temp_df['gt_o_l']=np.where(temp_df['o_change']<great_low_open_rate,-(temp_df['o_change']/great_low_open_rate-1),0)
        temp_df['gt_open']=temp_df['gt_o_h']+temp_df['gt_o_l']
        del temp_df['gt_o_h']
        del temp_df['gt_o_l']
        
        great_increase_rate=3.0
        great_descrease_rate=-3.0
        temp_df1['p_change']=(temp_df1['p_change']).round(1)
        p_change_list=temp_df1['p_change'].values.tolist()
        great_increase_rate,great_descrease_rate=self.get_extreme_change(p_change_list,rate=extreme_rate)
        print('great_increase_rate=%s,great_descrease_rate=%s' %(great_increase_rate,great_descrease_rate))
        
        temp_df['gt_c_h']=np.where(temp_df['p_change']>great_increase_rate,(temp_df['p_change']/great_increase_rate-1),0)
        temp_df['gt_c_l']=np.where(temp_df['p_change']<great_descrease_rate,-(temp_df['p_change']/great_descrease_rate-1),0)
        temp_df['gt_close']=temp_df['gt_c_h']+temp_df['gt_c_l']
        del temp_df['gt_c_h']
        del temp_df['gt_c_l']
        
        great_v_rate=1.2
        little_v_rate=0.8
        temp_df1['amount_rate']=(temp_df1['amount_rate']).round(2)
        amount_rate_list=temp_df1['amount_rate'].values.tolist()
        great_v_rate,little_v_rate=self.get_extreme_change(amount_rate_list,rate=extreme_rate)
        print('great_v_rate=%s,little_v_rate=%s' %(great_v_rate,little_v_rate))
        
        temp_df['gt_v_r']=np.where(temp_df['amount_rate']>great_v_rate,(temp_df['amount_rate']/great_v_rate-1),0)
        temp_df['lt_v_r']=np.where(temp_df['amount_rate']<little_v_rate,-(little_v_rate/temp_df['amount_rate']-1),0)
        temp_df['great_v_rate']=temp_df['gt_v_r']+temp_df['lt_v_r']
        del temp_df['gt_v_r']
        del temp_df['lt_v_r']
        
        great_continue_increase_rate=great_increase_rate*0.75
        great_continue_descrease_rate=great_descrease_rate*0.75
        temp_df['gt_cc_h']=np.where((temp_df['p_change']>great_continue_increase_rate)\
                                     & (temp_df['p_change'].shift(1)>great_continue_increase_rate),\
                                     0.5*(0.5*(temp_df['p_change']+temp_df['p_change'].shift(1))/great_increase_rate-1),0)
        temp_df['gt_cc_l']=np.where((temp_df['p_change']<great_continue_descrease_rate)\
                                     & (temp_df['p_change'].shift(1)<great_continue_descrease_rate),\
                                     -0.5*(0.5*(temp_df['p_change']+temp_df['p_change'].shift(1))/great_continue_descrease_rate-1),0)
        temp_df['gt_cont_close']=temp_df['gt_cc_h']+temp_df['gt_cc_l']
        del temp_df['gt_cc_h']
        del temp_df['gt_cc_l']
        
        temp_df['k_trend']=temp_df['gt_open']*0.5 + temp_df['gt_close'] + temp_df['gt_cont_close'] \
        + 2.0*temp_df['p_change']/abs(temp_df['p_change'])*temp_df['great_v_rate']
        temp_df['k_score0']=temp_df['ma_score'] + temp_df['k_trend']
        temp_df['k_score_g']=np.where(temp_df['k_score0']>5.0,5.0,0.0)
        temp_df['k_score_m']=np.where((temp_df['k_score0']<=5.0) & (temp_df['k_score0']>=-5.0),temp_df['k_score0'],0.0)
        temp_df['k_score_l']=np.where(temp_df['k_score0']<-5.0,-5.0,0.0)
        temp_df['k_score'] =temp_df['k_score_g'] + temp_df['k_score_l'] + temp_df['k_score_m']
        del temp_df['k_score_g']
        del temp_df['k_score_l']
        
        sys_risk_range = 10.0
        ultimate_coefficient = 0.25
        max_position=1.0
        temp_df['position_nor'] = np.where((temp_df['k_score']>=-ultimate_coefficient*sys_risk_range) & \
                                         (temp_df['k_score']<=ultimate_coefficient*sys_risk_range),\
                                         0.5*max_position/sys_risk_range/ultimate_coefficient*temp_df['k_score']+0.5*max_position,0)
        temp_df['position_full'] = np.where(temp_df['k_score']>ultimate_coefficient*sys_risk_range,max_position,0)
        temp_df['position']=  temp_df['position_nor'] + temp_df['position_full']
        del temp_df['position_nor']
        del temp_df['position_full']
        self.data_feed(k_data=temp_df, feed_type='temp')
        temp_df.to_csv('temp_df_%s.csv' % self.code)
        #print(temp_df.tail(10))
        p_change = temp_df.tail(1).iloc[0].p_change
        close = temp_df.tail(1).iloc[0].close
        ma5 = temp_df.tail(1).iloc[0].ma5
        ma10 = temp_df.tail(1).iloc[0].ma10
        amount_rate = temp_df.tail(1).iloc[0].amount_rate
        atr = temp_df.tail(1).iloc[0].atr
        atr_ma5 = temp_df.tail(1).iloc[0].atr
        atr_in = temp_df.tail(1).iloc[0].atr_in
        ma_score = temp_df.tail(1).iloc[0].ma_score
        stock_score = temp_df.tail(1).iloc[0].k_score
        position = temp_df.tail(1).iloc[0].position
        
        """
        if stock_score>0:
            stock_score = min(stock_score,5.0)
        else:
            stock_score = max(stock_score,-5.0)
        """
        latest_k_data = temp_df.tail(1)
        #recent_k_num=10
        #describe_df = temp_df.tail(recent_k_num).describe()
        #print(describe_df)
        
        return ma_score,stock_score,position
    
    def get_exit_loss(self, tolerate_loss=-0.06, new_buy=False, cost=None):
        highest_day5 = 10
        lowest_day5 = 5
        ma5 = 1.0
        ma10 = 2.0
        atr5 = 2.0
        exit_0 = 0.0   #第一道防线
        cost = 1.2
        exit1 = cost*(1+tolerate_loss*1.01)    #第二道防线
        if new_buy:
            exit_0 = max(ma5-atr5,cost*(1+tolerate_loss))
        else:
            if is_most_over_ma5:
                exit_0 = max(ma10,min(ma5,highest_day5-2*atr5))
            else:
                exit_0 = max(lowest_day5,ma5-0.5*atr5)
        exit_0 = max(exit_0,exit1)
        return exit_0, exit1
    
    
    def get_extreme_change(self,value_list,rate=None,unique_v=False):
        normal_rate = 0.8
        if rate != None:
            normal_rate = rate
        strong_v = 0.0
        weak_v = 0.0
        if value_list:
            value_length = len(value_list)
            #print('value_length=%s' % value_length)
            if value_length==1:
                return value_list[0],value_list[0]
            elif value_length==2:
                #print('value_length1=%s' % value_length)
                return max(value_list[0],value_list[1]),min(value_list[0],value_list[1])
            else:
                pass
            if unique_v:   
                filter_li = []
                for ele in value_list:
                    if ele not in filter_li and ele!=np.nan:
                        filter_li.append(ele)
                    else:
                        pass
                value_list = filter_li
            #sorted_li = sorted(filter_li,reverse=True)
            value_list.pop(0)
            value_list.pop(len(value_list)-2)
            sorted_li = sorted(value_list,reverse=True)
            strong_index = int(len(sorted_li)*(1-normal_rate))
            weak_index = round(len(sorted_li)*normal_rate)
            weak_index = int(len(sorted_li)*normal_rate)
            #print('sorted_li=',sorted_li,type(sorted_li[1]))
            strong_v = sorted_li[strong_index]
            weak_v = sorted_li[weak_index]
        return strong_v,weak_v
    
    def get_trend_score(self,open_change=None,p_change=None):
        delta_score = 0.5
        open_rate = 0.0
        increase_rate = 0.0
        if open_change:
            open_rate = open_change
        else:
            if self.temp_hist_df.empty:
                return 0.0
            else:
                open_rate = self.temp_hist_df.iloc[1].o_change
        if p_change:
            increase_rate = p_change
        else:
            if self.temp_hist_df.empty:
                return 0.0
            else:
                increase_rate = self.temp_hist_df.iloc[1].p_change
        open_score_coefficient = self.get_open_score(open_rate)
        increase_score_coefficient = self.get_increase_score(increase_rate)
        continue_trend_num,great_change_num,volume_coefficient = self.get_continue_trend_num()
        continue_trend_score_coefficient,recent_great_change_coefficient = self.get_recent_trend_score(continue_trend_num,great_change_num)
        score = (open_score_coefficient+increase_score_coefficient+continue_trend_score_coefficient+recent_great_change_coefficient+volume_coefficient)*0.5
        if score>0:
            score = min(score,5.0)
        else:
            score = max(score,-5.0)
        return score
    
    def get_continue_trend_num(self):
        if len(self.temp_hist_df)<2:
            return 0,0,0.0
        recent_10_hist_df = self.temp_hist_df.tail(min(10,len(self.temp_hist_df)))
        great_increase_rate = 3.0
        great_descrease_rate = -3.0
        great_change_num = 0
        great_increase_num = 0
        great_descrease_num = 0
        great_continue_increase_rate = 2.0
        great_continue_descrease_rate = -2.0
        continue_trend_num = 0
        continue_increase_num = 0
        continue_decrease_num = 0
        latest_trade_date = recent_10_hist_df.tail(1).iloc[0].date
        great_increase_df = recent_10_hist_df[recent_10_hist_df.p_change>great_continue_increase_rate]
        volume_coefficient = 0.0
        if great_increase_df.empty:
            pass
        else:
            latest_great_increase_date = great_increase_df.tail(1).iloc[0].date
            if latest_trade_date==latest_great_increase_date:
                continue_increase_num = 1
                tatol_inscrease_num=len(great_increase_df)
                while tatol_inscrease_num-continue_increase_num>0:
                    temp_inscrease_df = great_increase_df.head(tatol_inscrease_num-continue_increase_num)
                    if temp_inscrease_df.tail(1).iloc[0].date==tradeTime.get_last_trade_date(latest_great_increase_date):
                        continue_increase_num += 1
                        latest_great_increase_date = tradeTime.get_last_trade_date(latest_great_increase_date)
                    else:
                        break
                continue_trend_num=continue_increase_num
            else:
                great_change_df = recent_10_hist_df[recent_10_hist_df.p_change>great_increase_rate]
                great_increase_num = len(great_change_df)
                
            if continue_increase_num>=2:
                volume0 = great_increase_df.tail(2).iloc[0].volume
                volume1 = great_increase_df.tail(2).iloc[1].volume
                if volume1>volume0 and volume0:
                    volume_coefficient = min(round(volume1/volume0,2),3.0)
                else:
                    pass
            else:
                pass
        great_decrease_df = recent_10_hist_df[recent_10_hist_df.p_change<great_continue_descrease_rate]
        if great_decrease_df.empty:
            pass
        else:
            latest_great_decrease_date = great_decrease_df.tail(1).iloc[0].date
            if latest_trade_date==latest_great_decrease_date:
                continue_decrease_num = 1
                tatol_decrease_num = len(great_decrease_df)
                while tatol_decrease_num-continue_decrease_num>0:
                    temp_decrease_df = great_decrease_df.head(tatol_decrease_num-continue_decrease_num)
                    if temp_decrease_df.tail(1).iloc[0].date==tradeTime.get_last_trade_date(latest_great_decrease_date):
                        continue_decrease_num += 1
                        latest_great_decrease_date = tradeTime.get_last_trade_date(latest_great_decrease_date)
                    else:
                        break
                continue_trend_num = -continue_decrease_num
            else:
                great_change_df = recent_10_hist_df[recent_10_hist_df.p_change<great_descrease_rate]
                great_descrease_num = len(great_change_df)
            
            if continue_decrease_num>=2:
                volume0 = great_decrease_df.tail(2).iloc[0].volume
                volume1 = great_decrease_df.tail(2).iloc[1].volume
                if volume1>volume0 and volume0:
                    volume_coefficient = max(-round(volume1/volume0,2),-3.0)
                else:
                    pass
            else:
                pass
        if great_increase_num==great_descrease_num:
            pass
        elif great_increase_num>great_descrease_num:
            great_change_num = great_increase_num
        else:
            great_change_num = -great_descrease_num
        return continue_trend_num,great_change_num,volume_coefficient
    
    'VSA-------spread=high-low---------------------------------'
    
    def is_up_bar(self):
        return this_close>=last_close*1.01
    
    def is_down_bar(self):
        return this_close<=last_close*0.99
    
    def get_recent_extreme_factor(self):
        recent_high=2.0
        recent_low=1.0
        this_high=3.0
        trust_factor=0.0
        if this_high>recent_high:
            trust_factor=this_high/recent_high-1
        elif this_low <recent_low:
            trust_factor=this_low/recent_low-1
        return trust_factor
    
    def get_wide_range_factor(self):
        high=2.0
        low=1.0
        close=1.1
        ma5_spread_range=1.0
        max_range=1.8
        min_range=0.8
        trust_factor=0.0
        spread_rate=(high-low)/ma5_spread_range
        if spread_rate>max_range:   #is_wide_range_bar
            trust_factor=spread_rate-max_range
        elif spread_rate<min_range: #is_narrow_range_bar
            trust_factor=spread_rate-min_range
        else:
            pass
        return trust_factor
    
    def get_up_colse_factor(self):
        high=2.0
        low=1.0
        close=1.1
        high_rate=0.66
        low_rate=0.33
        trust_factor=0.0
        close_coefficient=round((close-low)/(high-low),2)
        if close_coefficient>high_rate: # is_up_colse
            trust_factor=close_coefficient-high_rate
        elif close_coefficient<low_rate:   #is_down_close
            trust_factor=close_coefficient-low_rate
        else:
            pass
        return trust_factor
    
    def get_high_volume_factor(self):
        this_volume=100
        ma5_volume=105
        high_rate=1.5
        low_rate=0.8
        trust_factor=0.0
        volume_coefficient=round(this_volume/ma5_volume,2)
        if volume_coefficient>high_rate:
            trust_factor=volume_coefficient-high_rate
        elif volume_coefficient<low_rate:
            trust_factor=volume_coefficient-high_rate
        else:
            pass
        return trust_factor
    
    def is_up_down_trust(self): # 冲高回落，强弱势
        trust_factor=0.0
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        is_up_down=range_factor>0 and close_factor<0 and volume_factor>0 and extreme_factor>0
        if is_up_down:
            trust_factor=1.0+range_factor+abs(close_factor)+volume_factor+extreme_factor
        return is_up_down,trust_factor
    
    def is_up_down_confirm(self):# 冲高回落 确认
        is_last_up_down_trust=True
        to_exit=False
        if is_last_up_down_trust:
            if  self.is_down_bar() and self.get_high_volume_factor()>=0: #第二天下降k线且放量
                to_exit=True
            else:
                pass
        return to_exit
    
    def is_no_demand(self):#买盘不足,弱势
        trust_factor=0.0
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        no_demand=range_factor<0 and close_factor==0 and volume_factor<0 and self.is_up_bar()
        if no_demand:
            trust_factor=1.0+abs(range_factor)+abs(volume_factor)
        return no_demand,trust_factor
    
    def is_no_demand_confirm(self):# 冲高回落 确认
        is_no_demand_trust=True
        to_exit=False
        if is_no_demand_trust:
            if  self.is_down_bar():#and self.get_high_volume_factor()>=0: #第二天下降k线且放量
                to_exit=True
            else:
                pass
        return to_exit    
        
    def is_sell_pressure_test(self): #卖压测试，将拉升
        has_the_first_increase=True
        this_low_is_reach_last_high_volume_area=True
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        sell_pressure_test=has_the_first_increase and this_low_is_reach_last_high_volume_area and close_factor>=0 and volume_factor==0
        return sell_pressure_test
    
    def is_stop_volume(self): #止跌成交量，下跌将结束
        is_down_trend=True
        trust_factor=0.0
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        stop_volume=is_down_trend and close_factor >0 and self.is_down_bar() and volume_factor>0
        if stop_volume:
            trust_factor=1.0+close_factor+volume_factor
        return stop_volume,trust_factor
    
    def is_reverse_up_trust(self):
        is_down_trend=True
        trust_factor=0.0
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        reverse_up_trust=is_down_trend and range_factor>0 and close_factor >0 and self.is_down_bar() and volume_factor>0 and extreme_factor<0
        if reverse_up_trust:
            trust_factor=1.0+close_factor+volume_factor+range_factor+abs(extreme_factor)
        return reverse_up_trust,trust_factor
    
    def is_sell_no_supply(self): #卖盘不足，强势
        is_down_trend=True
        trust_factor=0.0
        range_factor=self.get_wide_range_factor()
        close_factor=self.get_up_colse_factor()
        volume_factor=self.get_high_volume_factor()
        extreme_factor=self.get_recent_extreme_factor()
        sell_no_supply=range_factor<0 and close_factor<0 and volume_factor<0 and self.is_down_bar()
        if sell_no_supply:
            trust_factor=1.0+abs(range_factor)+abs(volume_factor)
            if is_down_trend:
                trust_factor+=0.5
        return sell_no_supply,trust_factor
        
    'VSA-------spread=high-low---------------------------------'
    def data_feed_by_date(self,from_date_str, to_date_str,raw_df=None):  #from_date_str: '2015-05-16'
        h_df=self.h_df#.set_index('date')
        if raw_df!=None:
            h_df=raw_df
        self.h_df=filter_df_by_date(h_df,from_date_str,to_date_str)
        
    def data_feed_by_count(self,count):
        if self.h_df.empty:
            pass
        else:
            valid_count=min(count,len(self.h_df))
            self.h_df=self.h_df.tail(valid_count)
                
    def set_max_price(self,max_price):
        self.max_price=max_price
        
    def set_min_price(self,min_price):
        self.min_price=min_price        
        
    def set_alarm_category(self,alarm_category):
        self.alarm_category=alarm_category
        
    def is_new_stock(self):
        return len(self.h_df)<2
    
    def is_second_new_stock(self):
        return len(self.h_df)>=20 and len(self.h_df)<100
    
    def is_stop_trade(self):
        is_stopping=False
        if self.h_df.empty:
            is_stopping=True
        else:
            last_trade_date=tradeTime.get_latest_trade_date()
            last_df_date=self.h_df.tail(1).iloc[0].date
            #print(last_trade_date,last_df_date)
            is_stopping=last_df_date<last_trade_date
            #print(is_stopping)
        return is_stopping
            
    #to set debug mode
    def set_debug_mode(self,debug):
        self.DEBUG_ENABLED=debug
        
    #get df of the latest <num>
    def set_history_df(self,df):
        self.h_df=df
    
    def get_average_rate(self,days=None,selected_column=None):
        num=60
        if days!=None:
            num=days
        temp_df=self._form_temp_df()
        temp_df=temp_df.tail(num)
        #print temp_df
        column='p_change'
        if selected_column!=None:
            column=selected_column
        average_rate=temp_df[column].mean()
        #average_high=high_df['p_change'].mean()
        return average_rate
    
    def get_average_high(self,days=None):
        num=60
        if days!=None:
            num=days
        high_df,filter_rate=self.filter_hist('gte', 0, num)
        #print high_df
        average_high=high_df['h_change'].mean()
        average_close=high_df['p_change'].mean()
        #print average_high,average_close
        average_high=round((average_high+average_close)*0.5,2)
        return average_high
    
    def get_max_id(self, temp_df, column='close', num=20):
        print(temp_df[column].tail(num).idxmax(axis=0))
        return temp_df[column].tail(num).idxmax(axis=0)
    
    def get_average_low(self,days=None):
        num=60
        if days!=None:
            num=days
        low_df,filter_rate=self.filter_hist('lt', 0, num)
        #print low_df
        average_low=low_df['l_change'].mean()
        average_close=low_df['p_change'].mean()
        #print average_low,average_close
        average_low=round((average_low+average_close)*0.5,2)
        return average_low
    
    #form temp df with 'last_close' for calculating p_change    
    def _form_temp_df(self):
        
        if self.h_df.empty:
            return self.h_df
        df=self.h_df
        #df.to_csv('aa.csv')
        #close_c=df['close']
        idx=df.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        #temp_df['close'] = temp_df['close'].astype(float)
        #print(type(temp_df.close))
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        
        temp_df.is_copy=False
        if '3.5' in platform.python_version():
            temp_df['ma5'] = temp_df['close'].rolling(window=5,center=False).mean().round(2)
            temp_df['ma10'] = temp_df['close'].rolling(window=10,center=False).mean().round(2)
            temp_df['ma20'] = temp_df['close'].rolling(window=20,center=False).mean().round(2)
            temp_df['ma30'] = temp_df['close'].rolling(window=30,center=False).mean().round(2)
            temp_df['ma60'] = temp_df['close'].rolling(window=60,center=False).mean().round(2)
            temp_df['ma120'] = temp_df['close'].rolling(window=120,center=False).mean().round(2)
            temp_df['ma250'] = temp_df['close'].rolling(window=250,center=False).mean().round(2)
            temp_df['v_ma5'] = temp_df['volume'].rolling(window=5,center=False).mean().round(2)
            temp_df['v_ma10'] = temp_df['volume'].rolling(window=10,center=False).mean().round(2)
        else:#elif '3.4' in platform.python_version():
            temp_df['ma5'] = pd.rolling_mean(temp_df['close'], window=5).round(2)
            temp_df['ma10'] = pd.rolling_mean(temp_df['close'], window=10).round(2)
            temp_df['ma20'] = pd.rolling_mean(temp_df['close'], window=20).round(2)
            temp_df['ma30'] = pd.rolling_mean(temp_df['close'], window=30).round(2)
            temp_df['ma60'] = pd.rolling_mean(temp_df['close'], window=60).round(2)
            temp_df['ma120'] = pd.rolling_mean(temp_df['close'], window=120).round(2)
            temp_df['ma250'] = pd.rolling_mean(temp_df['close'], window=250).round(2)
            temp_df['v_ma5'] = pd.rolling_mean(temp_df['volume'], window=5).round(2)
            temp_df['v_ma10'] = pd.rolling_mean(temp_df['volume'], window=10).round(2)
        
        """py2.7 or 3.4
        temp_df['ma5'] = np.round(pd.rolling_mean(temp_df['close'], window=5), 2)
        temp_df['ma10'] = np.round(pd.rolling_mean(temp_df['close'], window=10), 2)
        temp_df['ma20'] = np.round(pd.rolling_mean(temp_df['close'], window=20), 2)
        temp_df['ma30'] = np.round(pd.rolling_mean(temp_df['close'], window=30), 2)
        temp_df['ma60'] = np.round(pd.rolling_mean(temp_df['close'], window=60), 2)
        temp_df['ma120'] = np.round(pd.rolling_mean(temp_df['close'], window=120), 2)
        temp_df['v_ma5'] = np.round(pd.rolling_mean(temp_df['volume'], window=5), 2)
        temp_df['v_ma10'] = np.round(pd.rolling_mean(temp_df['volume'], window=10), 2)
        """
        #temp_df['v_rate'] = np.round(pd.rolling_mean(temp_df['volume'], window=10), 2)
        temp_df.insert(17, 'v_rate', (temp_df['volume']/(temp_df['v_ma5'].shift(1))).round(4))
        if '3.5' in platform.python_version():
            temp_df['amount_ma5'] = temp_df['amount'].rolling(center=False,window=5).mean().round(2)
            temp_df['amount_ma10'] = temp_df['amount'].rolling(center=False,window=10).mean().round(2)
        else:#elif '3.4' in platform.python_version():
            temp_df['amount_ma5'] = pd.rolling_mean(temp_df['amount'], window=5).round(2)
            temp_df['amount_ma10'] = pd.rolling_mean(temp_df['amount'], window=10).round(2)
        #temp_df['amount_ma5'] = np.round(pd.rolling_mean(temp_df['amount'], window=5), 2)
        #temp_df['amount_ma10'] = np.round(pd.rolling_mean(temp_df['amount'], window=10), 2)
        temp_df.insert(18, 'amount_rate', (temp_df['amount']/(temp_df['amount_ma5'].shift(1))).round(4))
        temp_df.insert(19, 'ma_amount_rate', (temp_df['amount_ma5']/temp_df['amount_ma10']).round(4))
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(16, 'o_change', 100.00*((temp_df.open-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df['atr']=np.where((temp_df['high']-temp_df['low'])<(temp_df['high']-temp_df['close'].shift(1)),
                                temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<(temp_df['close'].shift(1)-temp_df['low']),temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        short_num=5
        long_num=10
        long_num20 = 20
        long_num60 = 60
        if '3.5' in platform.python_version():
            temp_df['atr_ma%s'%short_num] = temp_df['atr'].rolling(center=False,window=short_num).mean().round(2)
            temp_df['atr_ma%s'%long_num] = temp_df['atr'].rolling(center=False,window=long_num).mean().round(2)
            temp_df['atr_%s_rate'%short_num]=(temp_df['atr_ma%s'%short_num]/temp_df['atr']).round(2)
            temp_df['atr_%s_max_r'%short_num]=temp_df['atr_%s_rate'%short_num].rolling(window=short_num,center=False).max().round(2)
            temp_df['atr_%s_rate'%long_num]=(temp_df['atr_ma%s'%long_num]/temp_df['atr']).round(2)
            temp_df['atr_%s_max_r'%long_num]=temp_df['atr_%s_rate'%long_num].rolling(window=long_num,center=False).max().round(2)
            temp_df['c_max10'] = temp_df['close'].rolling(window=long_num,center=False).max().round(2)
            temp_df['c_min10'] = temp_df['close'].rolling(window=long_num,center=False).min().round(2)
            temp_df['h_max10'] = temp_df['high'].rolling(window=long_num,center=False).max().round(2)
            temp_df['l_min10'] = temp_df['low'].rolling(window=long_num,center=False).min().round(2)
            temp_df['h_max20'] = temp_df['high'].rolling(window=long_num20,center=False).max().round(2)
            temp_df['l_min20'] = temp_df['low'].rolling(window=long_num20,center=False).min().round(2)
            temp_df['c_max20'] = temp_df['close'].rolling(window=long_num20,center=False).max().round(2)
            temp_df['c_min20'] = temp_df['close'].rolling(window=long_num20,center=False).min().round(2)
            temp_df['c_max60'] = temp_df['close'].rolling(window=long_num60,center=False).max().round(2)
            temp_df['c_min60'] = temp_df['close'].rolling(window=long_num60,center=False).min().round(2)
            temp_df['l_max3'] = temp_df['low'].rolling(window=3,center=False).max().round(2)
            temp_df['h_max3'] = temp_df['high'].rolling(window=3,center=False).max().round(2)
            temp_df['c_max3'] = temp_df['close'].rolling(window=3,center=False).max().round(2)
            temp_df['l_min3'] = temp_df['low'].rolling(window=3,center=False).min().round(2)
            temp_df['c_min2'] = temp_df['close'].rolling(window=2,center=False).min().round(2)
            temp_df['chg_mean2'] = temp_df['p_change'].rolling(window=2,center=False).mean().round(2)
            temp_df['chg_min2'] = temp_df['p_change'].rolling(window=2,center=False).min().round(2)
            temp_df['chg_min3'] = temp_df['p_change'].rolling(window=3,center=False).min().round(2)
            temp_df['chg_min4'] = temp_df['p_change'].rolling(window=4,center=False).min().round(2)
            temp_df['chg_min5'] = temp_df['p_change'].rolling(window=5,center=False).min().round(2)
            temp_df['chg_max2'] = temp_df['p_change'].rolling(window=2,center=False).max().round(2)
            temp_df['chg_max3'] = temp_df['p_change'].rolling(window=3,center=False).max().round(2)
            temp_df['amount_rate_min2'] = temp_df['amount_rate'].rolling(window=2,center=False).min().round(2)
            #temp_df['id_c_max20'] = temp_df['close'].idxmax(axis=0)
            #print(temp_df['close'].rolling(window=20,center=False))
            #print(type(temp_df['close'].rolling(window=20,center=False)))
            #temp_df['id_c_max20'] = temp_df['close'].rolling(window=20,center=False).apply(self.get_max_id(temp_df))
        else:#elif '3.4' in platform.python_version():
            temp_df['atr_ma%s'%short_num] = pd.rolling_mean(temp_df['atr'], window=short_num).round(2)
            temp_df['atr_ma%s'%long_num] = pd.rolling_mean(temp_df['atr'], window=long_num).round(2)
            temp_df['atr_%s_rate'%short_num]=(temp_df['atr_ma%s'%short_num]/temp_df['atr']).round(2)
            temp_df['atr_%s_max_r'%short_num]=pd.rolling_max(temp_df['atr_%s_rate'%short_num], window=short_num).round(2)
            temp_df['atr_%s_rate'%long_num]=(temp_df['atr_ma%s'%long_num]/temp_df['atr']).round(2)
            temp_df['atr_%s_max_r'%long_num]=pd.rolling_max(temp_df['atr_%s_rate'%long_num], window=long_num).round(2)
            temp_df['c_max10']=pd.rolling_max(temp_df['close'], window=long_num).round(2)
            temp_df['c_min10']=pd.rolling_min(temp_df['close'], window=long_num).round(2)
            temp_df['h_max10']=pd.rolling_max(temp_df['high'], window=long_num).round(2)
            temp_df['l_min10']=pd.rolling_min(temp_df['low'], window=long_num).round(2)
            temp_df['h_max20']=pd.rolling_max(temp_df['high'], window=long_num20).round(2)
            temp_df['l_min20']=pd.rolling_min(temp_df['low'], window=long_num20).round(2)
            temp_df['c_max20']=pd.rolling_max(temp_df['close'], window=long_num20).round(2)
            temp_df['c_min20']=pd.rolling_min(temp_df['close'], window=long_num20).round(2)
            temp_df['c_max60']=pd.rolling_max(temp_df['close'], window=long_num60).round(2)
            temp_df['c_min60']=pd.rolling_min(temp_df['close'], window=long_num60).round(2)
            temp_df['l_max3']=pd.rolling_max(temp_df['low'], window=3).round(2)
            temp_df['h_max3']=pd.rolling_max(temp_df['high'], window=3).round(2)
            temp_df['c_max3']=pd.rolling_max(temp_df['close'], window=3).round(2)
            temp_df['l_min3']=pd.rolling_min(temp_df['low'], window=3).round(2)
            temp_df['c_min2']=pd.rolling_min(temp_df['low'], window=2).round(2)
            temp_df['chg_min2']=pd.rolling_min(temp_df['p_change'], window=2).round(2)
            temp_df['chg_min3']=pd.rolling_min(temp_df['p_change'], window=2).round(2)
            temp_df['chg_min4']=pd.rolling_min(temp_df['p_change'], window=2).round(2)
            temp_df['chg_min5']=pd.rolling_min(temp_df['p_change'], window=2).round(2)
            temp_df['chg_max2']=pd.rolling_max(temp_df['p_change'], window=2).round(2)
            temp_df['chg_max3']=pd.rolling_max(temp_df['p_change'], window=3).round(2)
            temp_df['amount_rate_min2'] = pd.rolling_min(temp_df['amount_rate'], window=2).round(2)
        #print(self.temp_df.tail(30)[['date','close','id_c_max20']]) 
        expect_rate=1.8
        temp_df['rate_%s'%expect_rate]=(expect_rate*temp_df['atr']/temp_df['atr']).round(2)
        temp_df['atr_in']=np.where((temp_df['atr_%s_rate'%short_num]==temp_df['atr_%s_max_r'%short_num]
                                    ) & (temp_df['atr_%s_max_r'%short_num]>=temp_df['rate_%s'%expect_rate]
                                         ),(0.5*(temp_df['atr_%s_rate'%short_num]+temp_df['atr_%s_rate'%long_num])).round(2),0)
        temp_df['star'] = ((temp_df['close']-temp_df['open'])/(temp_df['high']-temp_df['low'])).round(2) #k线实体比例
        temp_df['star_h'] = np.where(temp_df['star']>=0, ((temp_df['high']-temp_df['close'])/(temp_df['high']-temp_df['low'])).round(3),
                                  ((temp_df['high']-temp_df['open'])/(temp_df['high']-temp_df['low'])).round(3))
        temp_df['star_l'] = 1 - temp_df['star'].abs() - temp_df['star_h']
        temp_df['star_chg'] =temp_df['p_change']*(temp_df['star'].abs())
        temp_df['k_chg'] =(100.0 * (temp_df['close'] -temp_df['open'])/(temp_df['close'].shift(1))).round(4)
        """一日反转"""
        temp_df['k_rate'] = np.where((temp_df['close'].shift(1)-temp_df['open'].shift(1))!=0,
                                     ((temp_df['close']-temp_df['open'])/(temp_df['close'].shift(1)-temp_df['open'].shift(1))).round(2),0)
        great_rate=1.5
        temp_df['reverse'] = np.where((temp_df['p_change'].shift(1).abs()>great_rate) 
                                      & (temp_df['k_rate']<=-0.51) & (temp_df['star'].abs()>=0.5)
                                      & (temp_df['star'].shift(1).abs()>=0.5),
                                      -temp_df['k_rate']*temp_df['p_change']/(temp_df['p_change'].abs()),0)
        temp_df['p_rate'] = np.where(temp_df['p_change'].shift(1)!=0,(temp_df['p_change']/temp_df['p_change'].shift(1)).round(2),0)
        """相对开盘价,用于大盘股高开"""
        temp_df['oo_chg'] = ((temp_df['open'].shift(-1)-temp_df['open'])/temp_df['open']*100.0).round(2) #次日开盘价相对今天开盘价
        temp_df['oh_chg'] = ((temp_df['high'].shift(-1)-temp_df['open'])/temp_df['open']*100.0).round(2) #次日最高价相对今天开盘价
        temp_df['ol_chg'] = ((temp_df['low'].shift(-1)-temp_df['open'])/temp_df['open']*100.0).round(2) #次日最低价相对今天开盘价
        temp_df['oc_chg'] = ((temp_df['close'].shift(-1)-temp_df['open'])/temp_df['open']*100.0).round(2) #次日收盘价相对今天开盘价
        #temp_df.to_csv(ROOT_DIR+'/result_temp/temp_%s.csv' % self.code)
        """岛型反转"""
        gap_rate=0.005
        temp_df['jump_max']=np.where(temp_df['close']>temp_df['open'],temp_df['close'],temp_df['open'])
        temp_df['jump_min']=np.where(temp_df['close']<temp_df['open'],temp_df['close'],temp_df['open'])
        temp_df['jump_up']=np.where(temp_df['jump_min']>(1+gap_rate)*temp_df['jump_max'].shift(1),
                                    temp_df['jump_min']/temp_df['jump_max'].shift(1)-1,0)
        temp_df['jump_up']=np.where(temp_df['low']>(1+gap_rate)*temp_df['high'].shift(1),
                                    temp_df['jump_min']/temp_df['jump_max'].shift(1)-1,0)
        temp_df['jump_down']=np.where(temp_df['jump_max']<(1-gap_rate)*temp_df['jump_min'].shift(1),
                                      1-temp_df['jump_min'].shift(1)/temp_df['jump_max'],0)
        temp_df['gap'] = (temp_df['jump_up'] + temp_df['jump_down']).round(3)
        temp_df['island'] = np.where(temp_df['gap']*temp_df['gap'].shift(1)<0,temp_df['gap'],0)
        """实体跨越多条k线"""
        cross_ma5_criteria = (temp_df['ma5']>=temp_df['jump_min']) & (temp_df['ma5']<=temp_df['jump_max'])
        cross_ma10_criteria = (temp_df['ma10']>=temp_df['jump_min']) & (temp_df['ma10']<=temp_df['jump_max'])
        cross_ma30_criteria = (temp_df['ma20']>=temp_df['jump_min']) & (temp_df['ma20']<=temp_df['jump_max'])
        cross_ma60_criteria = (temp_df['ma60']>=temp_df['jump_min']) & (temp_df['ma60']<=temp_df['jump_max'])
        temp_df['cross1'] = np.where(cross_ma5_criteria,temp_df['p_change'],0)
        temp_df['cross2'] = np.where(cross_ma5_criteria & cross_ma10_criteria,temp_df['p_change'],0)
        temp_df['cross3'] = np.where(cross_ma5_criteria & cross_ma10_criteria & cross_ma30_criteria,temp_df['p_change'],0)
        temp_df['cross4'] = np.where(cross_ma5_criteria & cross_ma10_criteria & cross_ma30_criteria & cross_ma60_criteria,temp_df['p_change'],0)
        
        #temp_df['std'] =  temp_df['p_change'].rolling(window=10).std()
        temp_df['std'] =  temp_df['close'].rolling(window=5).std()
        island_df=temp_df[['date','p_change','gap','star','k_rate','p_rate','island','atr_in','reverse','cross1','cross2','cross3']]
        
        """收盘价所处的位置"""
        """
        temp_df_20 = temp_df.tail(20)
        temp_df_20['pos20'] = df[['close']].apply(lambda x: (x - x.min()) / (x.max()-x.nin())) 
        temp_df_60 = temp_df.tail(60)
        temp_df_60['pos60'] = df[['close']].apply(lambda x: (x - x.min()) / (x.max()-x.nin())) 
        """
        temp_df['pos20'] = (temp_df['close']-temp_df['c_min20'])/(temp_df['c_max20']-temp_df['c_min20'])
        temp_df['pos60'] = (temp_df['close']-temp_df['c_min60'])/(temp_df['c_max60']-temp_df['c_min60'])
        
        #print(island_df[island_df.island!=0])
        #print(island_df.tail(50))
        del temp_df['jump_max']
        del temp_df['jump_min']
        del temp_df['jump_up']
        del temp_df['jump_down']
        temp_df['cOma5'] = (temp_df['close']/temp_df['ma5']-1).round(4)
        temp_df['cOma10'] = (temp_df['close']/temp_df['ma10']-1).round(4)
        #temp_df['ma5_chg'] = np.where(temp_df['ma5']>0, (temp_df['close']/temp_df['ma5']-1).round(4),-10)
        #temp_df['ma10_chg'] = np.where(temp_df['ma10']>0, (temp_df['close']/temp_df['ma10']-1).round(4),-10)
        """均线拐点"""
        #temp_df['ma5_k'] = temp_df['ma5'].diff(1)
        for ma_name in ['ma5','ma10','ma20']:
            ma_name_k = '%s_k' % ma_name
            temp_df[ma_name_k] = temp_df[ma_name].diff(1)
            temp_df[ma_name_k+'2'] = temp_df[ma_name_k].diff(1)
            ma_name_turn = '%s_turn' % ma_name
            temp_df[ma_name_turn] = np.where((temp_df[ma_name_k] * (temp_df[ma_name_k].shift(1)))<=0, (temp_df[ma_name_k]-temp_df[ma_name_k].shift(1)),0)
        temp_df['trend_chg'] = np.where((temp_df['ma5_turn'] * (temp_df['ma10_turn'].shift(1)))<=0,1,0)
        
        #print(temp_df[['p_change','ma5_k','ma5_k2','ma5_turn','ma10_k','ma10_k2','ma10_turn','ma20_turn','trend_chg']].tail(30))
        #temp_df['sell'] = np.where((temp_df['ma5_chg']<0 ) & ( temp_df['ma10_chg']<0),1,0)
        
        """ma over cross """
        """
        temp_df['cOma5'] = (temp_df['close']-temp_df['ma5']).round(2)
        temp_df['ma5O10'] = (temp_df['ma5']-temp_df['ma10']).round(2)
        temp_df['ma20O30'] = (temp_df['ma20']-temp_df['ma30']).round(2)
        temp_df['ma30O60'] = (temp_df['ma30']-temp_df['ma60']).round(2)
        temp_df['lowOma5'] = (temp_df['low']-temp_df['ma60']).round(2)
        """
        temp_df['ma5Cma20'] = np.where((temp_df['ma5']>=temp_df['ma20']) & (temp_df['ma5'].shift(1)<temp_df['ma20'].shift(1)),1,0)
        temp_df['ma5Cma30'] = np.where((temp_df['ma5']>=temp_df['ma30']) & (temp_df['ma5'].shift(1)<temp_df['ma30'].shift(1)),1,0)
        temp_df['ma10Cma20'] = np.where((temp_df['ma10']>=temp_df['ma20']) & (temp_df['ma10'].shift(1)<temp_df['ma20'].shift(1)),1,0)
        temp_df['ma10Cma30'] = np.where((temp_df['ma10']>=temp_df['ma30']) & (temp_df['ma10'].shift(1)<temp_df['ma30'].shift(1)),1,0)
        criteria_trangle_p = ((temp_df['ma5']>=temp_df['ma20']) & 
                              (temp_df['ma5'].shift(1)<temp_df['ma20'].shift(1)) & 
                              (temp_df['ma5']>=temp_df['ma10']) & 
                              (temp_df['ma20']<temp_df['ma30'])
                              )
        
        criteria_trangle_p1 = ((temp_df['ma5']>=temp_df['ma30']) & 
                              (temp_df['ma5'].shift(1)<temp_df['ma30'].shift(1)) & 
                              (temp_df['ma5']>=temp_df['ma10']) & 
                              (temp_df['ma30']<temp_df['ma60'])
                              )
        temp_df['tangle_p'] = np.where(criteria_trangle_p,(temp_df['ma5']/temp_df['ma10']-1),0)
        temp_df['tangle_p1'] = np.where(criteria_trangle_p1,(temp_df['ma5']/temp_df['ma10']-1),0)
        #self.data_feed(k_data=temp_df, feed_type='temp')
        #print(temp_df.tail(30))
        """动态止损点"""
        #temp_df['e_d_loss'] = (temp_df['low'].shift(1)).rolling(window=3,center=False).min().round(2)
        #temp_df['e_d_loss'] = temp_df['low'].rolling(window=3,center=False).min().round(2)
        """涨停后十字星，MA5之上入手"""
        temp_df['star_in'] = np.where(((
                                        (temp_df['p_change'].shift(1) >= 6.50)
                                       | (temp_df['chg_min2'].shift(1) >= 4.00)
                                       | (temp_df['chg_min3'].shift(1) >= 3.00)
                                       | (temp_df['chg_min4'].shift(1) >= 1.50)
                                       #| (temp_df['chg_min5'].shift(1) >= -0.50)
                                       | (temp_df['chg_min2'].shift(2) >= 4.00)
                                       | (temp_df['chg_min3'].shift(2) >= 3.00)
                                       | (temp_df['chg_min4'].shift(2) >= 1.50)
                                       )
                                      & (temp_df['star']<0.20)
                                      & (temp_df['cOma10']>0.015)
                                      #& ((temp_df['ma5']-temp_df['ma10'])>0)
                                      ),temp_df['amount_rate'],0)
        """
        temp_df['star_in'] = np.where(((
                                      (temp_df['close'] == (temp_df['close'].shift(1)*1.1).round(2))
                                       | (temp_df['close'].shift(1) == (temp_df['close'].shift(2)*1.1).round(2))
                                       | (temp_df['close'].shift(2) == (temp_df['close'].shift(3)*1.1).round(2))
                                       )
                                      & (temp_df['star'].abs()<0.20)
                                      & (temp_df['cOma5'].abs()<0.02)
                                      & ((temp_df['ma5']-temp_df['ma10'])>0)
                                      ),temp_df['p_change'],0)
        """
        """连涨若干天后，第一次回调入手"""""
        
        """前日低收，大幅次日高开反转"""
        weak_change = -1.5
        high_open_rate = 0.6
        temp_df['low_high_open'] = np.where((
                                        (temp_df['p_change'].shift(1) <=weak_change)
                                        & (temp_df['o_change']>= (temp_df['p_change'].shift(1).abs())*high_open_rate)
                                        #& (temp_df['close'] !=temp_df['open'])
                                        & (temp_df['close'].shift(1) <temp_df['open'].shift(1))
                                        #& (temp_df['pos20'].shift(1)<0.6)
                                      
                                      ),(temp_df['p_change'].shift(1).abs()*temp_df['o_change'])/(1.0+temp_df['pos20'].shift(1)),0)
        """盘整20天后突破"""""
        wave_rate = 10.0
        strong_posistion = 0.5
        temp_df['break_in'] = np.where((
                                        (temp_df['h_max20'].shift(1) <=((1+wave_rate*0.01)*temp_df['l_min20'].shift(1)))
                                        & (temp_df['close']>= temp_df['c_max20'].shift(1))
                                      
                                      ),temp_df['amount_rate'],0)
        
        temp_df['break_in_p'] = np.where((
                                        (temp_df['h_max20'] <=((1+wave_rate*0.01)*temp_df['l_min20']))
                                        #& (temp_df['close']>= ((temp_df['h_max20']-temp_df['l_max20'])* strong_posistion + temp_df['l_max20']))
                                      
                                      ),((temp_df['close']-temp_df['l_min20'])/(temp_df['h_max20']-temp_df['l_min20'])),0)
        
        self.temp_hist_df = temp_df
        
        return temp_df
    
    def diff_ma(self,ma=[10,30,60,120,250],target_column='close',win_num=5):
        """
        收盘价到MA的距离
        """
        for ma_num in ma:
            ma_column = 'MA%s' % ma_num
            self.temp_hist_df['diff_v_' + ma_column] = (self.temp_hist_df[target_column]-self.temp_hist_df[ma_column])*100.0/self.temp_hist_df[ma_column]
            self.temp_hist_df['diff_' + ma_column] = self.temp_hist_df['diff_v_' + ma_column].rolling(window=win_num,center=False).mean().round(2)
            self.temp_hist_df['diff_std_' + ma_column] = self.temp_hist_df['diff_' + ma_column].rolling(window=win_num,center=False).std().round(2)
        
        return
    
    def diff_ma_score(self,ma=[10,30,60,120,250],target_column='close',win_num=5):
        """
        收盘价到MA的距离
        """
        ma_count = len(ma)
        self.diff_ma(ma, target_column, win_num)
        ma_num = ma.pop(0)
        ma_column = 'MA%s' % ma_num
        self.temp_hist_df['diff_score'] = self.temp_hist_df['diff_' + ma_column]
        for ma_num in ma:
            ma_column = 'MA%s' % ma_num
            self.temp_hist_df['diff_score'] = self.temp_hist_df['diff_score'] + self.temp_hist_df['diff_' + ma_column]
        self.temp_hist_df['diff_score'] = (self.temp_hist_df['diff_score']/ma_count).round(2)
        #self.temp_hist_df['diff_score'].round(2)
        return
    
    def regress_high_open(self,regress_column = 'close',base_column='open'):
        high_open_df =  self.temp_hist_df
        crit_low_high_open = high_open_df['low_high_open']!= 0
        days = [0,-1,-2,-3,-5,-10,-20,-30,-50]
        columns = ['date','close','p_change','o_change','position','low_high_open']
        for day in days:
            column_name = 'high_o_day%s' % abs(day)
            columns.append(column_name)
            high_open_df[column_name] = np.where(crit_low_high_open,
                                                   (high_open_df[regress_column].shift(day)-high_open_df[base_column])/high_open_df[base_column],0)
        high_open_df = high_open_df[high_open_df['low_high_open']!= 0]
        high_open_df = high_open_df[columns]
        #high_open_df.to_csv('C:/work/temp/low_high_open_%s_%s.csv' % (self.code,column_type))
        return high_open_df,columns
    
    def regress_common(self,criteria,post_days=[0,-1,-2,-3,-4,-5],regress_column = 'close',
                       base_column='open',fix_columns=['date','close','p_change','o_change','position']):
        #criteria = self.temp_hist_df['low_high_open']!= 0
        #post_days = [0,-1,-2,-3,-5,-10,-20,-30,-50]
        #fix_columns = ['date','close','p_change','o_change','position','low_high_open']
        for day in post_days:
            column_name = 'high_o_day%s' % abs(day)
            fix_columns.append(column_name)
            self.temp_hist_df[column_name] = np.where(criteria,
                                                   (self.temp_hist_df[regress_column].shift(day)-self.temp_hist_df[base_column])/self.temp_hist_df[base_column],0)
        regress_df = self.temp_hist_df[criteria]
        regress_df = regress_df[fix_columns]
        regress_df.to_csv('C:/work/temp/low_high_open_%s_%s.csv' % (self.code,regress_column))
        return regress_df,fix_columns
    
    def get_market_score(self,short_turn_weight=None,k_data=None):
        ma_type='ma5'
        temp_df=self.temp_hist_df
        if temp_df.empty:
            return temp_df
        if k_data!=None:
            update_one_hist(code_sybol, today_df, today_df_update_time)
            temp_df=self._form_temp_df()
        #if len(temp_df)<5:
        #    return temp_df
        #temp_df.to_csv('aa.csv')
        ma_offset=0.002
        WINDOW=3
        ma_type_list=['ma5','ma10','ma20','ma30','ma60','ma120']
        ma_weight=[0.3,0.2,0.2,0.1,0.1,0.1]
        short_weight=0.7
        ma_seq_score={'ma5_o_ma10':0.5,'ma10_o_ma30':0.3,'ma30_o_ma60':0.2}
        ma_cross_score={'ma5_c_ma10':0.75,'ma10_c_ma30':0.5,'ma30_c_ma60':0.3}
        if short_turn_weight!=None:
            short_weight=short_turn_weight
        """Get MA score next"""
        for ma_type in ma_type_list:
            ma_sum_name='sum_o_'
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])<-ma_offset*temp_df['close'].shift(1),-1,temp_df['c_o_ma']) #-1 for bellow ma
            ma_sum_name=ma_sum_name+ma_type
            #temp_df[ma_sum_name] = pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW).round(2)
            if '3.5' in platform.python_version():
                temp_df[ma_sum_name] = temp_df['c_o_ma'].rolling(window=5,center=False).mean().round(2)
            else:
                temp_df[ma_sum_name] = np.round(pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW), 2)
            del temp_df['c_o_ma']
            temp_df[ma_sum_name]=temp_df[ma_sum_name]+(temp_df[ma_sum_name]-temp_df[ma_sum_name].shift(1))
        temp_df['ma_score0']=(short_weight*ma_weight[0]+(1-short_weight)*ma_weight[5])*temp_df['sum_o_ma5']\
        +(short_weight*ma_weight[1]+(1-short_weight)*ma_weight[4])*temp_df['sum_o_ma10']\
        +(short_weight*ma_weight[2]+(1-short_weight)*ma_weight[3])*temp_df['sum_o_ma20']\
        +(short_weight*ma_weight[3]+(1-short_weight)*ma_weight[2])*temp_df['sum_o_ma30']\
        +(short_weight*ma_weight[4]+(1-short_weight)*ma_weight[1])*temp_df['sum_o_ma60']\
        +(short_weight*ma_weight[5]+(1-short_weight)*ma_weight[1])*temp_df['sum_o_ma120']
        #temp_df['ma_s_score']=0.1*temp_df['sum_o_ma5']+0.1*temp_df['sum_o_ma10']+0.1*temp_df['sum_o_ma20']+0.2*temp_df['sum_o_ma30']+0.2*temp_df['sum_o_ma60']+0.3*temp_df['sum_o_ma120']
        del temp_df['sum_o_ma5']
        del temp_df['sum_o_ma10']
        del temp_df['sum_o_ma20']
        del temp_df['sum_o_ma30']
        del temp_df['sum_o_ma60']
        del temp_df['sum_o_ma120']
        """Get MA trend score next"""
        ma_trend_score=0.0
        for ma_o_name in ma_seq_score.keys():
            ma_name_list=ma_o_name.split('_')
            s_ma_name=ma_name_list[0]
            l_ma_name=ma_name_list[2]
            ma_cross_name=ma_o_name.replace('o','c')
            temp_df[ma_o_name]=np.where(temp_df[s_ma_name]>temp_df[l_ma_name],ma_seq_score[ma_o_name],-ma_seq_score[ma_o_name])
            temp_df[ma_cross_name+'_d']=np.where((temp_df[s_ma_name]<=temp_df[l_ma_name]) & 
                                                 (temp_df[s_ma_name].shift(1)>temp_df[l_ma_name].shift(1)),-ma_cross_score[ma_cross_name],0)
            temp_df[ma_cross_name+'_u']=np.where((temp_df[s_ma_name]>=temp_df[l_ma_name]) &
                                                  (temp_df[s_ma_name].shift(1)<temp_df[l_ma_name].shift(1)),ma_cross_score[ma_cross_name],0)
            temp_df[ma_cross_name]=temp_df[ma_cross_name+'_d']+temp_df[ma_cross_name+'_u']
            del temp_df[ma_cross_name+'_d']
            del temp_df[ma_cross_name+'_u']
        ma_o_name_list=ma_seq_score.keys()
        ma_c_name_list=ma_cross_score.keys()
        temp_df['ma_trend_score']=temp_df['ma5_o_ma10']+temp_df['ma10_o_ma30']+temp_df['ma30_o_ma60']\
        +temp_df['ma5_c_ma10']+temp_df['ma10_c_ma30']+temp_df['ma30_c_ma60']
        temp_df['ma_score']=temp_df['ma_score0']+temp_df['ma_trend_score']
        del temp_df['ma5_o_ma10']
        del temp_df['ma10_o_ma30']
        del temp_df['ma30_o_ma60']
        """
        del temp_df['ma5_c_ma10']
        del temp_df['ma10_c_ma30']
        del temp_df['ma30_c_ma60']
        """
        """Get K data trend score next"""
        great_high_open_rate = 1.0
        great_low_open_rate = -1.5
        recent_k_num = 60
        temp_df1=temp_df.fillna(0).tail(recent_k_num)
        extreme_rate = 0.85
        temp_df1['o_change']=(temp_df1['o_change']).round(1)
        o_change_list=temp_df1['o_change'].values.tolist()
        great_high_open_rate,great_low_open_rate=self.get_extreme_change(o_change_list,rate=extreme_rate)
        #print('great_high_open_rate=%s,great_low_open_rate=%s' %(great_high_open_rate,great_low_open_rate))
        
        temp_df['gt_o_h']=np.where(temp_df['o_change']>great_high_open_rate,(temp_df['o_change']/great_high_open_rate-1),0)
        temp_df['gt_o_l']=np.where(temp_df['o_change']<great_low_open_rate,-(temp_df['o_change']/great_low_open_rate-1),0)
        temp_df['gt_open']=temp_df['gt_o_h']+temp_df['gt_o_l']
        del temp_df['gt_o_h']
        del temp_df['gt_o_l']
        
        great_increase_rate=3.0
        great_descrease_rate=-3.0
        temp_df1['p_change']=(temp_df1['p_change']).round(1)
        p_change_list=temp_df1['p_change'].values.tolist()
        great_increase_rate,great_descrease_rate=self.get_extreme_change(p_change_list,rate=extreme_rate)
        #print('great_increase_rate=%s,great_descrease_rate=%s' %(great_increase_rate,great_descrease_rate))
        
        temp_df['gt_c_h']=np.where(temp_df['p_change']>great_increase_rate,(temp_df['p_change']/great_increase_rate-1),0)
        temp_df['gt_c_l']=np.where(temp_df['p_change']<great_descrease_rate,-(temp_df['p_change']/great_descrease_rate-1),0)
        temp_df['gt_close']=temp_df['gt_c_h']+temp_df['gt_c_l']
        del temp_df['gt_c_h']
        del temp_df['gt_c_l']
        
        great_v_rate=1.2
        little_v_rate=0.8
        temp_df1['amount_rate']=(temp_df1['amount_rate']).round(2)
        amount_rate_list=temp_df1['amount_rate'].values.tolist()
        great_v_rate,little_v_rate=self.get_extreme_change(amount_rate_list,rate=extreme_rate)
        #print('great_v_rate=%s,little_v_rate=%s' %(great_v_rate,little_v_rate))
        
        temp_df['gt_v_r']=np.where(temp_df['amount_rate']>great_v_rate,(temp_df['amount_rate']/great_v_rate-1),0)
        temp_df['lt_v_r']=np.where(temp_df['amount_rate']<little_v_rate,-(little_v_rate/temp_df['amount_rate']-1),0)
        temp_df['great_v_rate']=temp_df['gt_v_r']+temp_df['lt_v_r']
        del temp_df['gt_v_r']
        del temp_df['lt_v_r']
        
        temp_df['gt2_amount'] = np.where(((temp_df['amount_rate']>(great_v_rate*1.2)) 
                                       & (temp_df['amount_rate'].shift(1)>(great_v_rate*1.2)) 
                                       ),(temp_df['amount_rate']>great_v_rate),0)
        
        temp_df['gt3_amount'] = np.where(((temp_df['amount_rate']>great_v_rate) 
                                       & (temp_df['amount_rate'].shift(1)>great_v_rate) 
                                       & (temp_df['amount_rate'].shift(2)>great_v_rate)),(temp_df['amount_rate']>great_v_rate),0)
        
        great_continue_increase_rate=great_increase_rate*0.75
        great_continue_descrease_rate=great_descrease_rate*0.75
        temp_df['gt_cc_h']=np.where((temp_df['p_change']>great_continue_increase_rate)\
                                     & (temp_df['p_change'].shift(1)>great_continue_increase_rate),\
                                     0.5*(0.5*(temp_df['p_change']+temp_df['p_change'].shift(1))/great_increase_rate-1),0)
        temp_df['gt_cc_l']=np.where((temp_df['p_change']<great_continue_descrease_rate)\
                                     & (temp_df['p_change'].shift(1)<great_continue_descrease_rate),\
                                     -0.5*(0.5*(temp_df['p_change']+temp_df['p_change'].shift(1))/great_continue_descrease_rate-1),0)
        temp_df['gt_cont_close']=temp_df['gt_cc_h']+temp_df['gt_cc_l']
        del temp_df['gt_cc_h']
        del temp_df['gt_cc_l']
        
        temp_df['k_trend']=temp_df['gt_open']*0.5 + temp_df['gt_close'] + temp_df['gt_cont_close'] \
        + 2.0*temp_df['p_change']/abs(temp_df['p_change'])*temp_df['great_v_rate']
        temp_df['k_score0']=temp_df['ma_score'] + temp_df['k_trend']
        temp_df['k_score_g']=np.where(temp_df['k_score0']>5.0,5.0,0.0)
        temp_df['k_score_m']=np.where((temp_df['k_score0']<=5.0) & (temp_df['k_score0']>=-5.0),temp_df['k_score0'],0.0)
        temp_df['k_score_l']=np.where(temp_df['k_score0']<-5.0,-5.0,0.0)
        temp_df['k_score'] =temp_df['k_score_g'] + temp_df['k_score_l'] + temp_df['k_score_m']
        del temp_df['k_score_g']
        del temp_df['k_score_l']
        
        sys_risk_range = 10.0
        ultimate_coefficient = 0.25
        max_position=1.0
        temp_df['position_nor'] = np.where((temp_df['k_score']>=-ultimate_coefficient*sys_risk_range) & \
                                         (temp_df['k_score']<=ultimate_coefficient*sys_risk_range),\
                                         0.5*max_position/sys_risk_range/ultimate_coefficient*temp_df['k_score']+0.5*max_position,0)
        temp_df['position_full'] = np.where(temp_df['k_score']>ultimate_coefficient*sys_risk_range,max_position,0)
        temp_df['position']=  temp_df['position_nor'] + temp_df['position_full']
        temp_df['operation']= temp_df['position'] - temp_df['position'].shift(1)
        del temp_df['position_nor']
        del temp_df['position_full']
        #print(temp_df)
        #self.data_feed(k_data=temp_df, feed_type='temp')
        self.temp_hist_df = temp_df
        #self.temp_hist_df.to_csv('aa.csv')
        #print(temp_df)
        return temp_df
    
    def get_extrem_data(self):
        return
    
    def get_recent_state(self, temp_df,num=20,column='close'):#,id_max_id_min,id_latest,id_close_max20,id_close_min20,max_close,min_close):
        """
        state>=3, strong
        state<=-3, weak
        """
        if temp_df.empty:
            return -1,-1,-1, 0, 0,0,pd.DataFrame({})
        latest_date = temp_df.tail(1).iloc[0].date
        id_latest = len(temp_df)
        latest_close = temp_df.tail(1).iloc[0].close
        #print('latest_close= %s' %latest_close)
        #print('------------',self.code,temp_df)
        id_close_max20 = temp_df.tail(num)[column].idxmax(axis=0)
        #print(id_close_max20)
        max_close = temp_df.loc[id_close_max20].close
        max_high = temp_df.loc[temp_df.tail(num)['high'].idxmax(axis=0)].close
        id_close_min20 = temp_df.tail(num)[column].idxmin(axis=0)
        min_close = temp_df.loc[id_close_min20].close
        id_max_id_min = id_close_max20 -id_close_min20
        close_position = (latest_close-min_close)/(max_close-min_close)
        recent_trend_df = temp_df[temp_df.index>id_close_min20]
        if column == 'amount_rate':
            latest_close = temp_df.tail(1).iloc[0].amount_rate
            max_close = temp_df.loc[id_close_max20].amount_rate
            min_close = temp_df.loc[id_close_min20].amount_rate
        elif column == 'close':
            latest_close = temp_df.tail(1).iloc[0].close
            max_close = temp_df.loc[id_close_max20].close
            min_close = temp_df.loc[id_close_min20].close
        close_state = 0
        if id_max_id_min>0:
            if id_close_max20==id_latest:
                close_state = 5
            else:
                recent_trend_df = temp_df[temp_df.index>id_close_max20]
                if latest_close>(2.0*max_close + min_close)/3.0:
                    close_state = 4
                elif latest_close<(max_close + 2.0* min_close)/3.0:
                    close_state = -3
                else:
                    close_state = 1
        else:
            if id_close_min20==id_latest:
                close_state = -5
                recent_trend_df = temp_df[temp_df.index>id_close_max20]
            else:
                recent_trend_df = temp_df[temp_df.index>id_close_min20]
                if latest_close>(2.0*max_close + min_close)/3.0:
                    #print((2.0*max_close + min_close)/3.0)
                    close_state = 3
                elif latest_close<(max_close + 2.0* min_close)/3.0:
                    close_state = -4
                else:
                    close_state = -1
        return id_close_max20,id_close_min20,max_close, min_close, close_state,max_high,recent_trend_df
    
    def get_continue_incrs(self,index_list):
        #index_list = [244, 245, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256]
        count = len(index_list)
        if count == 0:
            return 0,0
        loop_count = count -1
        while loop_count>0:
            if (index_list[loop_count] -index_list[loop_count-1])==1:
                loop_count = loop_count - 1
            else:
                break
        min_incrs_index = index_list[loop_count]
        continue_incrs_count = count - loop_count
        return continue_incrs_count,min_incrs_index
    
    def get_recent_trend(self,num=20,column='close'):
        
        if self.temp_hist_df.empty:
            return pd.Series({})
        id_close_max20,id_close_min20, max_close, min_close, close_state,max_high, recent_trend_df =self.get_recent_state(temp_df=self.temp_hist_df,num=20,column='close')
        #print(id_close_max20,id_close_min20, max_close, min_close, close_state,max_high, recent_trend_df )
        #id_rbm_rate_max20,id_rbm_rate_min20, max_rbm_rate, min_rbm_rate, rbm_rate_state,max_high, rbm_rate_recent_trend_df =self.get_recent_state(temp_df=self.temp_hist_df,num=20,column='amount_rate')
        #print(id_rbm_rate_max20,id_rbm_rate_min20, max_rbm_rate, min_rbm_rate, rbm_rate_state,max_high, rbm_rate_recent_trend_df)
        #print('rbm_rate_state=%s' % close_state)
        if recent_trend_df.empty:
            return pd.Series({})
        #close_state = get_recent_state(temp_df, id_max_id_min, id_latest, id_close_max20, id_close_min20, max_close, min_close)
        latest_close = recent_trend_df.tail(1).iloc[0].close
        fantan_rate = (latest_close/min_close-1)
        continue_incrs_df = recent_trend_df[recent_trend_df['p_change']>0]
        index_value = continue_incrs_df.index.values.tolist()
        #index_list = [247, 248, 249, 250, 251, 252, 253, 254, 255, 256]
        continue_incrs_count,min_incrs_index = self.get_continue_incrs(index_value)
        #print(continue_incrs_count,min_incrs_index)
        #continue_incrs_df['diff_id'] = continue_incrs_df[continue_incrs_df.index - continue_incrs_df.index.shift(1)]
        #print(continue_incrs_df[['p_change','diff_id']])
        if close_state in [-5,-3,1,4]:
            fantan_rate = -(1-latest_close/max_close) #drop down
        
        last_temp_df = self.temp_hist_df[self.temp_hist_df.index<min(id_close_min20,id_close_max20)]
        id_close_max20_last,id_close_min20_last,  max_close_last, min_close_last, close_state_last,max_high_last,recent_trend_df_last =self.get_recent_state(temp_df=last_temp_df,num=20,column='close')
        recent_trend_describe = recent_trend_df[['close','p_change','star_chg','position']].describe()
        #print(recent_trend_describe)
        recent_trend = recent_trend_describe['star_chg']
        recent_trend['chg_fuli'] = ((latest_close/min_close)**(1/len(recent_trend))-1)*100.0
        if len(recent_trend) ==0 or min_close==0:
            recent_trend['chg_fuli'] =0
        #if id_close_max20>id_close_min20:
        #    recent_trend['chg_fuli'] = ((latest_close/min_close)**(1/len(recent_trend))-1)*100.0
        amount_rate = recent_trend_df.tail(1).iloc[0].amount_rate
        ma_amount_rate = recent_trend_df.tail(1).iloc[0].ma_amount_rate
        recent_trend['c_state'] = close_state
        recent_trend['c_state0'] = close_state_last
        recent_trend['c_mean'] = recent_trend_describe.loc['mean'].close
        recent_trend['p_mean'] = recent_trend_describe.loc['mean'].p_change
        recent_trend['p_std'] = recent_trend_describe.loc['std'].p_change
        recent_trend['pos_mean'] = recent_trend_describe.loc['mean'].position
        recent_trend['ft_rate'] = fantan_rate
        #recent_trend['presure'] = max_close
        recent_trend['presure'] = max_high
        recent_trend['holding'] = min_close
        recent_trend['close'] = latest_close
        recent_trend['cont_num'] = continue_incrs_count
        recent_trend['amount_rate'] = amount_rate
        recent_trend['ma_amount_rate'] = ma_amount_rate
        
        
        #print(recent_trend)
        return recent_trend
    
    def regression_test0(self,rate_to_confirm = 0.0001):
        """
        卖出： 当天最低价小于之前三天的最低价，以最近三天的最低价卖出；如果跳空低开且开盘价小于近三天的最低价，以开盘价卖出
        买入： 当天价格高于前三天的收盘价的最大值，且当前建议仓位不小于25%，并无明显的减仓建议， 则以前三天收盘价的最大值买入；如果跳空高开且开盘价大于前三天的收盘价的最大值，以开盘价买入；
        """
        if self.temp_hist_df.empty:
            return pd.Series({})
        self.temp_hist_df['exit_3p'] = np.where((self.temp_hist_df['l_min3'].shift(1)>self.temp_hist_df['ma10']),
                                                self.temp_hist_df['l_min3'].shift(1),self.temp_hist_df['ma10'])
        """
        self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['high']!=self.temp_hist_df['low']) 
                                                 & (self.temp_hist_df['p_change']<0)
                                                 & (self.temp_hist_df['low']<self.temp_hist_df['l_min3'].shift(1)),self.temp_hist_df['l_min3'].shift(1),0)
        self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price0']>0) & (self.temp_hist_df['high']<self.temp_hist_df['s_price0']),
                                                self.temp_hist_df['open'],self.temp_hist_df['s_price0'])
        """
        #"""
        if rate_to_confirm:
            self.rate_to_confirm = rate_to_confirm
        self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['low']<(self.temp_hist_df['l_min3'].shift(1)*(1-self.rate_to_confirm))) 
                                                 #& (self.temp_hist_df['p_change']<0)  #预测了收盘价 不合理
                                                 #& (self.temp_hist_df['position'].shift(1)<0.7)
                                                 ,self.temp_hist_df['l_min3'].shift(1),0)
        #self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['low']<self.temp_hist_df['l_min3'].shift(1)*(1-self.rate_to_confirm))& #(self.temp_hist_df['p_change']>0) &
                                                 #(self.temp_hist_df['s_price0']==0) & (self.temp_hist_df['position'].shift(1)>0.6),  #预测了收盘价 不合理
                                                 #0,self.temp_hist_df['s_price0'])
        self.temp_hist_df['s_price1'] = np.where((self.temp_hist_df['s_price0']>0) & (self.temp_hist_df['high']==self.temp_hist_df['low']) ,
                                                0,self.temp_hist_df['s_price0']) #低开一字板跌停，卖不出去，第二天卖
        self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price1']>0) & (self.temp_hist_df['high']<self.temp_hist_df['s_price1']),
                                                self.temp_hist_df['open'],self.temp_hist_df['s_price1']) #低开，按开盘价卖
        #self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price1']>0) & (self.temp_hist_df['high']==self.temp_hist_df['low']) ,
        #                                        0,self.temp_hist_df['s_price1']) #低开一字板跌停，卖不出去，第二天卖
        #"""
        #self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price1']==0) & (self.temp_hist_df['star_chg']<-3.5),
        #                                        self.temp_hist_df['close'],self.temp_hist_df['s_price1'])
        """
        self.temp_hist_df['b_price0'] = np.where((self.temp_hist_df['high']!=self.temp_hist_df['low'])
                                                 & (self.temp_hist_df['p_change']>0)
                                                 & (self.temp_hist_df['high']>self.temp_hist_df['c_max3'].shift(1)) &
                                                 (self.temp_hist_df['position']>0.3) & (self.temp_hist_df['operation']>-0.15),self.temp_hist_df['c_max3'].shift(1),0)
        self.temp_hist_df['b_price'] = np.where((self.temp_hist_df['b_price0']>0) & (self.temp_hist_df['low']>self.temp_hist_df['b_price0']),
                                                -self.temp_hist_df['open'], -self.temp_hist_df['b_price0'])
        #print(self.temp_hist_df[['s_price', 'b_price']].tail(30))
        self.temp_hist_df['b_price'] = np.where(((self.temp_hist_df['b_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']==0)
                                                & (self.temp_hist_df['b_price']<0)), self.temp_hist_df['b_price'], 0)
        self.temp_hist_df['s_price'] = np.where(((self.temp_hist_df['s_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']>0)
                                                & (self.temp_hist_df['b_price']==0)),self.temp_hist_df['s_price'],0)
        """
        #"""
        self.temp_hist_df['b_price0'] = np.where(((self.temp_hist_df['high']>((self.temp_hist_df['c_max3'].shift(1))*(1.0+self.rate_to_confirm))) 
                                                 & (self.temp_hist_df['position']>0.3)),# & (self.temp_hist_df['operation']>-0.15),
                                                 self.temp_hist_df['c_max3'].shift(1),0)
        #self.temp_hist_df['b_price0'] = np.where((self.temp_hist_df['high']>self.temp_hist_df['h_max3'].shift(1)) #&
        #                                         #(self.temp_hist_df['position']>0.3) & (self.temp_hist_df['operation']>-0.15),
        #                                         ,self.temp_hist_df['h_max3'].shift(1),0)
        self.temp_hist_df['b_price1'] = np.where((self.temp_hist_df['b_price0']>0) & (self.temp_hist_df['low']>self.temp_hist_df['b_price0']),
                                                -self.temp_hist_df['open'], -self.temp_hist_df['b_price0']) #高开
        self.temp_hist_df['b_price'] = np.where((self.temp_hist_df['high']==self.temp_hist_df['low'])
                                                 & (self.temp_hist_df['p_change']>0) & (self.temp_hist_df['b_price1']<0),
                                                    0,self.temp_hist_df['b_price1']) #一字涨停,剔除
        #self.temp_hist_df['b_price'] = np.where((self.temp_hist_df['s_price'].shift(1)>0)
        #                                         & (self.temp_hist_df['p_change'].shift(1)>0.5) & (self.temp_hist_df['b_price2']==0),
        #                                            -self.temp_hist_df['open'],self.temp_hist_df['b_price2']) #昨日卖出后上涨，次日开盘买回
        #"""
        #print(self.temp_hist_df[['s_price', 'b_price']].tail(30))
        self.temp_hist_df['b_price'] = np.where(((self.temp_hist_df['b_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']==0)
                                                & (self.temp_hist_df['b_price']<0)), self.temp_hist_df['b_price'], 0)
        self.temp_hist_df['s_price'] = np.where(((self.temp_hist_df['s_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']>0)
                                                & (self.temp_hist_df['b_price']==0)),self.temp_hist_df['s_price'],0)
        
        #self.temp_hist_df['trade'] = self.temp_hist_df['b_price'] * self.temp_hist_df['s_price'] + self.temp_hist_df['b_price']  + self.temp_hist_df['s_price'] 
        self.temp_hist_df['trade'] = self.temp_hist_df['b_price']  + self.temp_hist_df['s_price'] 
        self.temp_hist_df['trade_na'] = np.where((self.temp_hist_df['trade']!=0),self.temp_hist_df['trade'],self.temp_hist_df['trade']/0.0)
        self.temp_hist_df['trade_na'] =  self.temp_hist_df['trade_na'].fillna(method='pad')
        #self.temp_hist_df['trade_na0'] = np.where((self.temp_hist_df['trade_na']*(self.temp_hist_df['trade_na'].shift(1))>0),self.temp_hist_df['trade_na'].shift(1),self.temp_hist_df['trade_na'])
        
        temp_hist_df =self.temp_hist_df.tail(100)
        break_in_df = temp_hist_df[(temp_hist_df['break_in']!=0) & (temp_hist_df['break_in'].shift(1)==0)]
        #print(break_in_df)
        break_in_v_rate = 0
        tupo_count_100 = len(break_in_df)
        break_in_id = len(temp_hist_df)
        break_in_date = '1977-01-01'
        if break_in_df.empty:
            pass
        else:
            break_in_df['id'] = break_in_df.index
            break_in_v_rate = break_in_df.tail(1).iloc[0].break_in
            break_in_id = break_in_df.tail(1).iloc[0].id
            break_in_date = break_in_df.tail(1).iloc[0].date    
        if  isinstance(self.test_num, int):
            temp_hist_df =self.temp_hist_df.tail(self.test_num)
        elif isinstance(self.test_num, str):
            """
            print(self.test_num)
            print(type(self.test_num))
            print(type(self.temp_hist_df['date']))
            print(self.temp_hist_df['date'])
            """
            temp_hist_df =self.temp_hist_df[self.temp_hist_df['date']>self.test_num]
        else:
            pass
        #print(temp_hist_df)
        #self.temp_hist_df.to_csv('aa.csv')
        temp_df = temp_hist_df[(temp_hist_df['s_price']>0) | (temp_hist_df['b_price']<0)]
        temp_df = temp_df[['date','close','p_change', 'position','operation','s_price','b_price']]
        temp_df['b_price'] = np.where(((temp_df['b_price'].shift(1)==0) 
                                                & (temp_df['s_price']==0)
                                                & (temp_df['b_price']<0)), temp_df['b_price'], 0)
        temp_df['s_price'] = np.where(((temp_df['s_price'].shift(1)==0) 
                                                & (temp_df['s_price']>0)
                                                & (temp_df['b_price']==0)),temp_df['s_price'],0)
        temp_df = temp_df[(temp_df['s_price']>0) | (temp_df['b_price']<0)]
        if temp_hist_df.empty or temp_df.empty:
            return pd.Series({})
        TRADE_FEE = 0.00162
        temp_df['profit'] = np.where(((temp_df['s_price']>0)
                                      & (temp_df['s_price'].shift(1)==0)
                                      & (temp_df['b_price'].shift(1)<0)),-(temp_df['s_price']+temp_df['b_price'].shift(1))/(temp_df['b_price'].shift(1)),0)
        temp_df['fuli_prf0'] = np.where((temp_df['profit']!=0) ,(temp_df['profit'] + 1.0 - TRADE_FEE),(temp_df['profit'] + 1.0))
        temp_df['fuli_prf'] = temp_df['fuli_prf0'].cumprod()
        
        del temp_df['fuli_prf0']
        temp_df['profit'] = np.where((temp_df['profit']!=0) ,(temp_df['profit'] - TRADE_FEE),temp_df['profit'])
        
        #temp_df = self.temp_hist_df[['date','close','p_change', 'position','operation','s_price','b_price']]
        #print(temp_df[temp_df['profit']!=0])
        #print(temp_df[temp_df['profit']!=0].describe())
        #print(temp_df[['close','p_change', 'position','operation','s_price','b_price']].describe())
        #print(temp_df.sum())
        temp_df['id'] = temp_df.index
        temp_df['hold_count'] = np.where((temp_df['profit']!=0) ,(temp_df['id'] - temp_df['id'].shift(1)),0)
        temp_df['trade'] = temp_df['s_price'] + temp_df['b_price']
        temp_df['cum_prf'] = temp_df['profit'].cumsum()
        cum_prf = temp_df.tail(1).iloc[0].cum_prf
        fuli_prf = temp_df.tail(1).iloc[0].fuli_prf  #倍数
        #print('fuli_prf=',fuli_prf)
        last_trade_date = temp_df.tail(1).iloc[0].date
        first_date = temp_hist_df.head(1).iloc[0].date
        #print('first_date=',first_date)
        last_date = temp_hist_df.tail(1).iloc[0].date
        date_format = '%Y-%m-%d'
        if '/' in last_trade_date:
            date_format = date_format.replace('-', '/')
        natual_days = (datetime.datetime.strptime(last_date,date_format)-datetime.datetime.strptime(first_date,date_format)).days
        #print('natual_days=',natual_days)
        yearly_prf = 0.0
        if natual_days!=0:
            yearly_prf = round(fuli_prf**(365.0/abs(natual_days))-1.0,4)
        #print('yearly_prf=',yearly_prf)
        last_360_df = self.temp_hist_df.tail(250)
        last_360_df['cum_amount'] = last_360_df['amount'].cumsum()
        cum_amount = last_360_df.tail(1).iloc[0].cum_amount
        n_last_360_df = len(last_360_df)
        average_amount = cum_amount / n_last_360_df
        n_topest = len(last_360_df[last_360_df['p_change']>9.2])/n_last_360_df
        n_topest_one = len(last_360_df[(last_360_df['p_change']>9.2) & (last_360_df['high']==last_360_df['low'])])/n_last_360_df
        great_incrs = 2.5
        great_drop = -2.0
        n_great_increase = len(last_360_df[last_360_df['p_change']>great_incrs])/n_last_360_df
        n_great_drop = len(last_360_df[last_360_df['p_change']<great_drop])/n_last_360_df
        """
        print('average_amount=',average_amount)
        print('n_topest=',n_topest)
        print('n_topest_one=',n_topest_one)
        print('n_great_increase=',n_great_increase)
        print('n_great_drop=',n_great_drop)
        """
        last_trade_price = temp_df.tail(1).iloc[0].trade
        last_trade_id = temp_df.tail(1).iloc[0].id
        last_id = temp_hist_df.tail(1).index.values.tolist()[0]
        last_price = temp_hist_df.tail(1).iloc[0].close
        #print(temp_hist_df.tail(3))
        dynamic_exit_price  = temp_hist_df.tail(1).iloc[0].l_min3
        dynamic_buy_price  = temp_hist_df.tail(1).iloc[0].c_max3
        this_position  = temp_hist_df.tail(1).iloc[0].position
        if last_trade_price<0:
            fuli_prf = fuli_prf * (1.0 + (last_price+last_trade_price)/abs(last_trade_price))
            cum_prf = cum_prf + (last_price+last_trade_price)/abs(last_trade_price)
        #rmd_rate_sumary = temp_hist_df.describe()['amount_rate']
        #max_amount_rate = temp_hist_df.tail(1).iloc[0].amount_rate
        #last_amount_rate = temp_hist_df.tail(1).iloc[0].amount_rate
        #print(last_id,last_trade_id)
        #print( temp_df)
        #print('cum_prf=%s' % cum_prf)
        del temp_df['id']
        #print(temp_df[temp_df['profit']!=0])
        
        temp_df = temp_df[['date','close','p_change',  'position','operation','s_price','b_price','profit','cum_prf','fuli_prf','hold_count']]
        trade_count = len(temp_df[temp_df['profit']!=0])
        trade_success_count = len(temp_df[temp_df['profit']>0])
        trade_success_rate = 0.0
        if trade_count!=0:
            trade_success_rate = round((round(trade_success_count,2)/trade_count),2 )
        summary_profit = temp_df[temp_df['profit']!=0].describe()['profit']
        avrg_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['mean'].hold_count)
        min_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['min'].hold_count)
        max_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['max'].hold_count)
        #recent_trend['p_mean'] = recent_trend_describe.loc['mean'].p_change
        #print(summary_hold_count)
        #trade_times = len(temp_df)/2
        #total_profit = temp_df.sum().profit - trade_times * TRADE_FEE
        #summary_profit['sum'] = total_profit
        summary_profit['cum_prf'] = cum_prf
        summary_profit['fuli_prf'] = (fuli_prf - 1.0)
        summary_profit['last_trade_date'] = last_trade_date
        summary_profit['last_trade_price'] = last_trade_price
        summary_profit['min_hold_count'] = min_hold_count
        summary_profit['max_hold_count'] = max_hold_count
        summary_profit['avrg_hold_count'] = avrg_hold_count
        this_trade_count = last_id - last_trade_id + 1
        if last_trade_price >0:#last trade to be sell
            this_trade_count = -1*this_trade_count
        summary_profit['this_hold_count'] = this_trade_count
        summary_profit['exit'] = dynamic_exit_price 
        summary_profit['enter'] = dynamic_buy_price
        summary_profit['position'] = this_position 
        summary_profit['break_in'] = break_in_v_rate 
        summary_profit['break_in_distance'] = last_id - break_in_id
        summary_profit['break_in_date'] = break_in_date
        summary_profit['break_in_count'] = tupo_count_100
        summary_profit['success_rate'] = trade_success_rate
        #summary_profit['max_amount_rate'] = max_amount_rate
        #summary_profit['max_amount_rate'] = max_amount_rate
        
        id_amount_rate_min2_max20 = self.temp_hist_df.tail(20)['amount_rate_min2'].idxmax(axis=0)
        #print(id_close_max20)
        max_amount_rate_min2 = self.temp_hist_df.loc[id_amount_rate_min2_max20].amount_rate_min2
        summary_profit['max_amount_rate'] = max_amount_rate_min2 
        summary_profit['max_amount_distance'] = last_id - id_amount_rate_min2_max20 + 1
        summary_profit['yearly_prf'] = yearly_prf
        #print(temp_df)
        #self.temp_hist_df.to_csv('C:/work/temp/hist_temp_%s.csv' % self.code)
        temp_df.to_csv('C:/work/temp/bs_%s.csv' % self.code)
        return summary_profit
    
    def form_regression_temp_df(self,rate_to_confirm = 0.0001,buyin_type='c_max3'):
        """
        buyin_type='c_max3', 以超过三天收盘价的最大值为买入点
        buyin_type='h_max3'， 以超过三天最高价的最大值为买入点
        卖出： 当天最低价小于之前三天的最低价，以最近三天的最低价卖出；如果跳空低开且开盘价小于近三天的最低价，以开盘价卖出
        买入： 当天价格高于前三天的收盘价的最大值，且当前建议仓位不小于25%，并无明显的减仓建议， 则以前三天收盘价的最大值买入；如果跳空高开且开盘价大于前三天的收盘价的最大值，以开盘价买入；
        """
        if self.temp_hist_df.empty:
            return pd.Series({})
        self.temp_hist_df['exit_3p'] = np.where((self.temp_hist_df['l_min3'].shift(1)>self.temp_hist_df['ma10']),
                                                self.temp_hist_df['l_min3'].shift(1),self.temp_hist_df['ma10'])
        """
        self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['high']!=self.temp_hist_df['low']) 
                                                 & (self.temp_hist_df['p_change']<0)
                                                 & (self.temp_hist_df['low']<self.temp_hist_df['l_min3'].shift(1)),self.temp_hist_df['l_min3'].shift(1),0)
        self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price0']>0) & (self.temp_hist_df['high']<self.temp_hist_df['s_price0']),
                                                self.temp_hist_df['open'],self.temp_hist_df['s_price0'])
        """
        #"""
        if rate_to_confirm:
            self.rate_to_confirm = rate_to_confirm
        self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['low']<(self.temp_hist_df['l_min3'].shift(1)*(1-self.rate_to_confirm))) 
                                                 #& (self.temp_hist_df['p_change']<0)  #预测了收盘价 不合理
                                                 #& (self.temp_hist_df['position'].shift(1)<0.7)
                                                 ,self.temp_hist_df['l_min3'].shift(1),0)
        #self.temp_hist_df['s_price0'] = np.where((self.temp_hist_df['low']<self.temp_hist_df['l_min3'].shift(1)*(1-self.rate_to_confirm))& #(self.temp_hist_df['p_change']>0) &
                                                 #(self.temp_hist_df['s_price0']==0) & (self.temp_hist_df['position'].shift(1)>0.6),  #预测了收盘价 不合理
                                                 #0,self.temp_hist_df['s_price0'])
        self.temp_hist_df['s_price1'] = np.where((self.temp_hist_df['s_price0']>0) & (self.temp_hist_df['high']==self.temp_hist_df['low']) ,
                                                0,self.temp_hist_df['s_price0']) #低开一字板跌停，卖不出去，第二天卖
        self.temp_hist_df['s_price2'] = np.where((self.temp_hist_df['s_price1']>0) & (self.temp_hist_df['high']<self.temp_hist_df['s_price1']),
                                                self.temp_hist_df['open'],self.temp_hist_df['s_price1']) #低开，按开盘价卖
        #self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price1']>0) & (self.temp_hist_df['high']==self.temp_hist_df['low']) ,
        #                                        0,self.temp_hist_df['s_price1']) #低开一字板跌停，卖不出去，第二天卖
        #"""
        #self.temp_hist_df['s_price'] = np.where((self.temp_hist_df['s_price1']==0) & (self.temp_hist_df['star_chg']<-3.5),
        #                                        self.temp_hist_df['close'],self.temp_hist_df['s_price1'])
        """
        self.temp_hist_df['b_price0'] = np.where((self.temp_hist_df['high']!=self.temp_hist_df['low'])
                                                 & (self.temp_hist_df['p_change']>0)
                                                 & (self.temp_hist_df['high']>self.temp_hist_df['c_max3'].shift(1)) &
                                                 (self.temp_hist_df['position']>0.3) & (self.temp_hist_df['operation']>-0.15),self.temp_hist_df['c_max3'].shift(1),0)
        self.temp_hist_df['b_price'] = np.where((self.temp_hist_df['b_price0']>0) & (self.temp_hist_df['low']>self.temp_hist_df['b_price0']),
                                                -self.temp_hist_df['open'], -self.temp_hist_df['b_price0'])
        #print(self.temp_hist_df[['s_price', 'b_price']].tail(30))
        self.temp_hist_df['b_price'] = np.where(((self.temp_hist_df['b_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']==0)
                                                & (self.temp_hist_df['b_price']<0)), self.temp_hist_df['b_price'], 0)
        self.temp_hist_df['s_price'] = np.where(((self.temp_hist_df['s_price'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price']>0)
                                                & (self.temp_hist_df['b_price']==0)),self.temp_hist_df['s_price'],0)
        """
        #"""
        self.temp_hist_df['b_price0'] = np.where(((self.temp_hist_df['high']>((self.temp_hist_df[buyin_type].shift(1))*(1.0+self.rate_to_confirm))) 
                                                 & (self.temp_hist_df['position']>0.3)),# & (self.temp_hist_df['operation']>-0.15),
                                                 self.temp_hist_df[buyin_type].shift(1),0)
        #self.temp_hist_df['b_price0'] = np.where((self.temp_hist_df['high']>self.temp_hist_df['h_max3'].shift(1)) #&
        #                                         #(self.temp_hist_df['position']>0.3) & (self.temp_hist_df['operation']>-0.15),
        #                                         ,self.temp_hist_df['h_max3'].shift(1),0)
        self.temp_hist_df['b_price1'] = np.where((self.temp_hist_df['b_price0']>0) & (self.temp_hist_df['low']>self.temp_hist_df['b_price0']),
                                                -self.temp_hist_df['open'], -self.temp_hist_df['b_price0']) #高开
        self.temp_hist_df['b_price2'] = np.where((self.temp_hist_df['high']==self.temp_hist_df['low'])
                                                 & (self.temp_hist_df['p_change']>0) & (self.temp_hist_df['b_price1']<0),
                                                    0,self.temp_hist_df['b_price1']) #一字涨停
        #self.temp_hist_df['b_price'] = np.where((self.temp_hist_df['s_price'].shift(1)>0)
        #                                         & (self.temp_hist_df['p_change'].shift(1)>0.5) & (self.temp_hist_df['b_price2']==0),
        #                                            -self.temp_hist_df['open'],self.temp_hist_df['b_price2']) #昨日卖出后上涨，次日开盘买回
        #"""
        self.temp_hist_df['b_price2'] = np.where((self.temp_hist_df['s_price2']>0) & (self.temp_hist_df['b_price2']<0),
                                                    0,self.temp_hist_df['b_price2']) #当天同时出现买点和卖点时，以卖出为准；卖出风险，不确定时
        
        #print(self.temp_hist_df[['s_price', 'b_price']].tail(30))
        self.temp_hist_df['b_price'] = np.where(((self.temp_hist_df['b_price2'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price2']==0)
                                                & (self.temp_hist_df['b_price2']<0)), self.temp_hist_df['b_price2'], 0)
        self.temp_hist_df['s_price'] = np.where(((self.temp_hist_df['s_price2'].shift(1)==0) 
                                                & (self.temp_hist_df['s_price2']>0)
                                                & (self.temp_hist_df['b_price2']==0)),self.temp_hist_df['s_price2'],0)
        
        #self.temp_hist_df['trade'] = self.temp_hist_df['b_price'] * self.temp_hist_df['s_price'] + self.temp_hist_df['b_price']  + self.temp_hist_df['s_price'] 
        self.temp_hist_df['trade'] = self.temp_hist_df['b_price']  + self.temp_hist_df['s_price'] 
        self.temp_hist_df['trade_na'] = np.where((self.temp_hist_df['trade']!=0),self.temp_hist_df['trade'],self.temp_hist_df['trade']/0.0)
        self.temp_hist_df['trade_na'] =  self.temp_hist_df['trade_na'].fillna(method='pad')
        #self.temp_hist_df['trade_na0'] = np.where((self.temp_hist_df['trade_na']*(self.temp_hist_df['trade_na'].shift(1))>0),self.temp_hist_df['trade_na'].shift(1),self.temp_hist_df['trade_na'])
        return
    
    def form_regression_result(self,save_dir='C:/work/temp/',rate_to_confirm = 0.0001,
                               save_column=['date','close','id','trade','p_change',  'position','operation','s_price','b_price','profit','cum_prf','fuli_prf','hold_count']):
        if 'trade' not in self.temp_hist_df.columns.values.tolist():
            self.form_regression_temp_df(rate_to_confirm)
        if self.temp_hist_df.empty:
            return self.temp_hist_df 
        if  isinstance(self.test_num, int):
            temp_hist_df =self.temp_hist_df.tail(self.test_num)
        elif isinstance(self.test_num, str):
            """
            print(self.test_num)
            print(type(self.test_num))
            print(type(self.temp_hist_df['date']))
            print(self.temp_hist_df['date'])
            """
            temp_hist_df =self.temp_hist_df[self.temp_hist_df['date']>self.test_num]
        else:
            pass
        #print(temp_hist_df)
        #self.temp_hist_df.to_csv('aa.csv')
        temp_df = temp_hist_df[(temp_hist_df['s_price']>0) | (temp_hist_df['b_price']<0)]
        temp_df = temp_df[['date','close','p_change', 'position','operation','s_price','b_price']]
        temp_df['b_price'] = np.where(((temp_df['b_price'].shift(1)==0) 
                                                & (temp_df['s_price']==0)
                                                & (temp_df['b_price']<0)), temp_df['b_price'], 0)
        temp_df['s_price'] = np.where(((temp_df['s_price'].shift(1)==0) 
                                                & (temp_df['s_price']>0)
                                                & (temp_df['b_price']==0)),temp_df['s_price'],0)
        temp_df = temp_df[(temp_df['s_price']>0) | (temp_df['b_price']<0)]
        if temp_hist_df.empty or temp_df.empty:
            return pd.Series({})
        TRADE_FEE = 0.00162
        temp_df['profit'] = np.where(((temp_df['s_price']>0)
                                      & (temp_df['s_price'].shift(1)==0)
                                      & (temp_df['b_price'].shift(1)<0)),-(temp_df['s_price']+temp_df['b_price'].shift(1))/(temp_df['b_price'].shift(1)),0)
        temp_df['fuli_prf0'] = np.where((temp_df['profit']!=0) ,(temp_df['profit'] + 1.0 - TRADE_FEE),(temp_df['profit'] + 1.0))
        temp_df['fuli_prf'] = temp_df['fuli_prf0'].cumprod()
        
        del temp_df['fuli_prf0']
        temp_df['profit'] = np.where((temp_df['profit']!=0) ,(temp_df['profit'] - TRADE_FEE),temp_df['profit'])
        
        #temp_df = self.temp_hist_df[['date','close','p_change', 'position','operation','s_price','b_price']]
        #print(temp_df[temp_df['profit']!=0])
        #print(temp_df[temp_df['profit']!=0].describe())
        #print(temp_df[['close','p_change', 'position','operation','s_price','b_price']].describe())
        #print(temp_df.sum())
        temp_df['id'] = temp_df.index
        temp_df['hold_count'] = np.where((temp_df['profit']!=0) ,(temp_df['id'] - temp_df['id'].shift(1)),0)
        temp_df['trade'] = temp_df['s_price'] + temp_df['b_price']
        temp_df['cum_prf'] = temp_df['profit'].cumsum()
        if save_dir:
            temp_df_save = temp_df[save_column]
            try:
                temp_df_save.to_csv(save_dir + '%s.csv' % self.code)
            except:
                pass
        return temp_df
    
    def get_regression_result(self,rate_to_confirm=0.0001,refresh_regression=True,from_csv=False,bs_csv_dir='',temp_csv_dir='',from_date='2017/01/01'):
        """获取分析结果,默认不保存回测文件bs-xx"""
        if refresh_regression:
            self.form_regression_temp_df(rate_to_confirm=rate_to_confirm)
            temp_df = self.form_regression_result(save_dir=csv_dir)
            temp_hist_df =self.temp_hist_df
        else:
            """直接从制定csv文件读取，必须指定csv_dir"""
            if from_csv:
                bs_csv_file = bs_csv_dir + '%s.csv' % self.code
                temp_csv_file = temp_csv_dir + '%s.csv' % self.code
                try:
                    temp_df =  pd.read_csv(bs_csv_file,index_col=0)
                    #temp_df['id'] = temp_df.index
                    #print(temp_df)
                    temp_hist_df = pd.read_csv(temp_csv_file)
                except:
                    return pd.Series({})
            else:
                return pd.Series({})
            
        if self.temp_hist_df.empty:
            return pd.Series({})
        #temp_hist_df =self.temp_hist_df.tail(100)
        break_in_df = temp_hist_df[(temp_hist_df['break_in']!=0) & (temp_hist_df['break_in'].shift(1)==0)]
        #print(break_in_df)
        break_in_v_rate = 0
        tupo_count_100 = len(break_in_df)
        break_in_id = len(temp_hist_df)
        break_in_date = '1977-01-01'
        if break_in_df.empty:
            pass
        else:
            break_in_df['id'] = break_in_df.index
            #break_in_df.loc[,'id'] = break_in_df.index
            break_in_v_rate = break_in_df.tail(1).iloc[0].break_in
            break_in_id = break_in_df.tail(1).iloc[0].id
            break_in_date = break_in_df.tail(1).iloc[0].date   
            
        cum_prf = temp_df.tail(1).iloc[0].cum_prf
        fuli_prf = temp_df.tail(1).iloc[0].fuli_prf  #倍数
        #print('fuli_prf=',fuli_prf)
        last_trade_date = temp_df.tail(1).iloc[0].date
        first_date = temp_hist_df.head(1).iloc[0].date
        #print('first_date=',first_date)
        last_date = temp_hist_df.tail(1).iloc[0].date
        date_format = '%Y-%m-%d'
        if '/' in last_trade_date:
            date_format = date_format.replace('-', '/')
        natual_days = (datetime.datetime.strptime(last_date,date_format)-datetime.datetime.strptime(first_date,date_format)).days
        #print('natual_days=',natual_days)
        yearly_prf = 0.0
        if natual_days!=0:
            yearly_prf = round(fuli_prf**(365.0/abs(natual_days))-1.0,4)
        #print('yearly_prf=',yearly_prf)
        last_360_df = self.temp_hist_df.tail(250)
        last_360_df['cum_amount'] = last_360_df['amount'].cumsum()
        cum_amount = last_360_df.tail(1).iloc[0].cum_amount
        n_last_360_df = len(last_360_df)
        average_amount = cum_amount / n_last_360_df
        n_topest = len(last_360_df[last_360_df['p_change']>9.2])/n_last_360_df
        n_topest_one = len(last_360_df[(last_360_df['p_change']>9.2) & (last_360_df['high']==last_360_df['low'])])/n_last_360_df
        great_incrs = 2.5
        great_drop = -2.0
        n_great_increase = len(last_360_df[last_360_df['p_change']>great_incrs])/n_last_360_df
        n_great_drop = len(last_360_df[last_360_df['p_change']<great_drop])/n_last_360_df
        """
        print('average_amount=',average_amount)
        print('n_topest=',n_topest)
        print('n_topest_one=',n_topest_one)
        print('n_great_increase=',n_great_increase)
        print('n_great_drop=',n_great_drop)
        """
        last_trade_price = temp_df.tail(1).iloc[0].trade
        last_trade_id = temp_df.tail(1).iloc[0].id
        last_id = temp_hist_df.tail(1).index.values.tolist()[0]
        last_price = temp_hist_df.tail(1).iloc[0].close
        #print(temp_hist_df.tail(3))
        dynamic_exit_price  = temp_hist_df.tail(1).iloc[0].l_min3
        dynamic_buy_price  = temp_hist_df.tail(1).iloc[0].c_max3
        this_position  = temp_hist_df.tail(1).iloc[0].position
        if last_trade_price<0:
            fuli_prf = fuli_prf * (1.0 + (last_price+last_trade_price)/abs(last_trade_price))
            cum_prf = cum_prf + (last_price+last_trade_price)/abs(last_trade_price)
        #rmd_rate_sumary = temp_hist_df.describe()['amount_rate']
        #max_amount_rate = temp_hist_df.tail(1).iloc[0].amount_rate
        #last_amount_rate = temp_hist_df.tail(1).iloc[0].amount_rate
        #print(last_id,last_trade_id)
        #print( temp_df)
        #print('cum_prf=%s' % cum_prf)
        del temp_df['id']
        #print(temp_df[temp_df['profit']!=0])
        trade_count = len(temp_df[temp_df['profit']!=0])
        trade_success_count = len(temp_df[temp_df['profit']>0])
        trade_success_rate = 0.0
        if trade_count!=0:
            trade_success_rate = round((round(trade_success_count,2)/trade_count),2 )
        summary_profit = temp_df[temp_df['profit']!=0].describe()['profit']
        avrg_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['mean'].hold_count)
        min_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['min'].hold_count)
        max_hold_count = round(temp_df[temp_df['profit']!=0].describe().loc['max'].hold_count)
        #recent_trend['p_mean'] = recent_trend_describe.loc['mean'].p_change
        #print(summary_hold_count)
        #trade_times = len(temp_df)/2
        #total_profit = temp_df.sum().profit - trade_times * TRADE_FEE
        #summary_profit['sum'] = total_profit
        summary_profit['cum_prf'] = cum_prf
        summary_profit['fuli_prf'] = (fuli_prf - 1.0)
        summary_profit['last_trade_date'] = last_trade_date
        summary_profit['last_trade_price'] = last_trade_price
        summary_profit['min_hold_count'] = min_hold_count
        summary_profit['max_hold_count'] = max_hold_count
        summary_profit['avrg_hold_count'] = avrg_hold_count
        this_trade_count = last_id - last_trade_id + 1
        if last_trade_price >0:#last trade to be sell
            this_trade_count = -1*this_trade_count
        summary_profit['this_hold_count'] = this_trade_count
        summary_profit['exit'] = dynamic_exit_price 
        summary_profit['enter'] = dynamic_buy_price
        summary_profit['position'] = this_position 
        summary_profit['break_in'] = break_in_v_rate 
        summary_profit['break_in_distance'] = last_id - break_in_id
        summary_profit['break_in_date'] = break_in_date
        summary_profit['break_in_count'] = tupo_count_100
        summary_profit['success_rate'] = trade_success_rate
        #summary_profit['max_amount_rate'] = max_amount_rate
        #summary_profit['max_amount_rate'] = max_amount_rate
        
        id_amount_rate_min2_max20 = self.temp_hist_df.tail(20)['amount_rate_min2'].idxmax(axis=0)
        #print(id_close_max20)
        max_amount_rate_min2 = self.temp_hist_df.loc[id_amount_rate_min2_max20].amount_rate_min2
        summary_profit['max_amount_rate'] = max_amount_rate_min2 
        summary_profit['max_amount_distance'] = last_id - id_amount_rate_min2_max20 + 1
        summary_profit['yearly_prf'] = yearly_prf
        
        latest_360d_num = 250
        from_date = (datetime.datetime.now() + datetime.timedelta(days=-365)).strftime('%Y/%m/%d')
        #latest_360d_temp_hist_df = temp_df.tail(latest_360d_num)
        latest_360d_temp_hist_df = temp_df[temp_df.date>from_date]
        latest_360d_sum_profit = latest_360d_temp_hist_df['profit'].sum()
        if last_trade_price<0:
            latest_360d_sum_profit = latest_360d_sum_profit + (last_price+last_trade_price)/abs(last_trade_price)
        init_fuli_profit = latest_360d_temp_hist_df.head(1).iloc[0].fuli_prf
        last_360d_fuli_profit = latest_360d_temp_hist_df.tail(1).iloc[0].fuli_prf
        latest_360d_fuli_profit = fuli_prf/init_fuli_profit-1
        summary_profit['last_year_prf'] = latest_360d_sum_profit
        summary_profit['last_year_fuli_prf'] = latest_360d_fuli_profit
        #print(temp_df)
        #self.temp_hist_df.to_csv('C:/work/temp/hist_temp_%s.csv' % self.code)
        #temp_df.to_csv('C:/work/temp/bs_%s.csv' % self.code)
        return summary_profit
    
    def get_regression_result_from_csv(self,rate_to_confirm=0.0001,csv_dir='C:/work/temp/'):
        """直接从指定csv文件读取并分析结果，前提是已经保存了CSV文件"""
        return self.get_regression_result(refresh_regression=False,rate_to_confirm=rate_to_confirm,from_csv=True,csv_dir=csv_dir)
    
    def get_and_save_regression_result(self,rate_to_confirm=0.0001,csv_dir='C:/work/temp/'):
        """获取分析结果并保存回测文件bs-xx,csv_dir为保存目录"""
        return self.get_regression_result(refresh_regression=True,rate_to_confirm=rate_to_confirm,from_csv=False,csv_dir=csv_dir)
    
    def form_temp_df(self,code_str):
        #self.set_code(code_str)
        #self.h_df = pds.get_raw_hist_df(code_str)
        #print(self.h_df)
        #self.temp_hist_df = self._form_temp_df()
        self.get_market_score()
        select_columns=['close','p_change','amount_rate','ma_amount_rate','gap','star','star_h','star_chg','cOma5',
                        'cOma10','k_rate','p_rate','island','atr_in','reverse',
                        'cross1','cross2','cross3','k_score','position','operation',
                        'std','tangle_p','tangle_p1','gt2_amount','gt3_amount']#,'e_d_loss']
        if self.temp_hist_df.empty:
            return self.temp_hist_df
        else:
            select_df=self.temp_hist_df[select_columns].round(3)
            return select_df
    
    def _form_temp_df1(self):
        #print(self.h_df)
        if len(self.h_df) <30:
            return 0,'',0,'' 
        df=self.h_df
        if len(self.h_df)>1000:
            df=df.tail(1000)
        close_c=df['close']
        idx=close_c.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        
        temp_df.is_copy=False
        temp_df['ma5'] = np.round(pd.rolling_mean(temp_df['close'], window=5), 2)
        temp_df['ma10'] = np.round(pd.rolling_mean(temp_df['close'], window=10), 2)
        temp_df['ma20'] = np.round(pd.rolling_mean(temp_df['close'], window=20), 2)
        temp_df['ma30'] = np.round(pd.rolling_mean(temp_df['close'], window=30), 2)
        temp_df['ma60'] = np.round(pd.rolling_mean(temp_df['close'], window=60), 2)
        temp_df['ma120'] = np.round(pd.rolling_mean(temp_df['close'], window=120), 2)
        temp_df['ma250'] = np.round(pd.rolling_mean(temp_df['close'], window=250), 2)
        temp_df['v_ma5'] = np.round(pd.rolling_mean(temp_df['volume'], window=5), 2)
        temp_df['v_ma10'] = np.round(pd.rolling_mean(temp_df['volume'], window=10), 2)
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df['atr']=np.where(temp_df['high']-temp_df['low']<temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<temp_df['close'].shift(1)-temp_df['low'],temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        short_num=5
        long_num=10
        temp_df['atr_ma%s'%short_num] = np.round(pd.rolling_mean(temp_df['atr'], window=short_num), 2)
        temp_df['atr_%s_rate'%short_num]=(temp_df['atr_ma%s'%short_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%short_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%short_num], window=short_num), 2)
        temp_df['atr_ma%s'%long_num] = np.round(pd.rolling_mean(temp_df['atr'], window=long_num), 2)
        temp_df['atr_%s_rate'%long_num]=(temp_df['atr_ma%s'%long_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%long_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%long_num], window=long_num), 2)
        expect_rate=1.8
        temp_df['rate_%s'%expect_rate]=(expect_rate*temp_df['atr']/temp_df['atr']).round(2)
        temp_df['atr_in']=np.where((temp_df['atr_%s_rate'%short_num]==temp_df['atr_%s_max_r'%short_num]) & (temp_df['atr_%s_max_r'%short_num]>=temp_df['rate_%s'%expect_rate]),(0.5*(temp_df['atr_%s_rate'%short_num]+temp_df['atr_%s_rate'%long_num])).round(2),0)
        temp_df.to_csv(ROOT_DIR+'/result_temp1/temp_%s.csv' % self.code,encoding='utf-8')
        atr_in_rate=round(temp_df.tail(1)['atr_in'].mean(),2)
        last_date=temp_df.tail(1).iloc[0].date
        #print type(last_date)
        last2_df=temp_df.tail(2)
        atr_in_rate_last=round(last2_df.head(1)['atr_in'].mean(),2)
        last2_date=last2_df.head(1).iloc[0].date
        #print 'atr_in_rate=',atr_in_rate
        return atr_in_rate,last_date,atr_in_rate_last,last2_date
    
    def _form_temp_df0(self):
        df=self.h_df
        close_c=df['close']
        idx=close_c.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        #temp_df.insert(7, '_change', 100.00*(temp_df.high-temp_df.last_close)/temp_df.last_close)
        """Insert MA data here """
        close_list=temp_df['close'].values.tolist()
        ma5_list=get_ma_list(close_list, 5)
        ma10_list=get_ma_list(close_list, 10)
        ma20_list=get_ma_list(close_list, 20)
        ma30_list=get_ma_list(close_list, 30)
        ma60_list=get_ma_list(close_list, 60)
        ma120_list=get_ma_list(close_list, 120)
        s_ma5=pd.Series(ma5_list,index=temp_df.index)
        s_ma10=pd.Series(ma10_list,index=temp_df.index)
        s_ma20=pd.Series(ma20_list,index=temp_df.index)
        s_ma30=pd.Series(ma30_list,index=temp_df.index)
        s_ma60=pd.Series(ma60_list,index=temp_df.index)
        s_ma120=pd.Series(ma120_list,index=temp_df.index)
        temp_df.insert(8,'ma5',s_ma5)
        temp_df.insert(9,'ma10',s_ma10)
        temp_df.insert(10,'ma20',s_ma20)
        temp_df.insert(11,'ma30',s_ma30)
        temp_df.insert(12,'ma60',s_ma60)
        temp_df.insert(13,'ma120',s_ma120)
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        return temp_df
    
    def change_static(self,rate_list,column):
        temp_df=self._form_temp_df()
        N=len(temp_df)
        if N<50:
            return pd.DataFrame({})
        else:
            #Do not consider special first 30 days for each stock 
            temp_df=temp_df[30:]
        gt_column=['code']
        #gt_column=['code']
        gt_data={}
        gt_data['code']=self.code
        for rate in rate_list:
            df=temp_df[temp_df[column]>rate]
            gt_rate_num=len(df)
            gt_rate=round(float(gt_rate_num)/N,2)
            column_name='gt_%s' % rate
            gt_data[column_name]=gt_rate
            gt_column.append(column_name)
        gt_static_df=pd.DataFrame(gt_data,columns=gt_column,index=['0'])
        #print 'static for %s:' % column
        #print gt_static_df 
        return gt_static_df
    
    def get_open_static(self,high_open_rate):
        trade_rate=0.2
        criteria_high_open=self.h_df['open']>self.h_df['close'].shift(1)*(1+high_open_rate*0.01)
        high_open_df=self.h_df[criteria_high_open]
        if len(high_open_df)>0:
            hopen_hclose_df=high_open_df[high_open_df['close']>high_open_df['open']*(1+(trade_rate)*0.01)]
            hopen_hclose_rate=round(round(len(hopen_hclose_df),2)/len(high_open_df),2)
            print('hopen_hclose_rate_%s=%s' % (high_open_rate,hopen_hclose_rate))
            
            criteria_high_next=self.h_df['high'].shift(-1)>self.h_df['open'].shift(1)*(1+(trade_rate+high_open_rate)*0.01)
            hopen_next_high_df=self.h_df[criteria_high_open & criteria_high_next]
            print(len(hopen_next_high_df))
            hopen_hnext_rate=round(round(len(hopen_next_high_df),2)/len(high_open_df),2)
            print('hopen_hnext_rate_%s=%s' % (high_open_rate,hopen_hnext_rate))
        
        low_open_df=self.h_df[self.h_df['open']<self.h_df['close'].shift(1)*(1-high_open_rate*0.01)]
        if len(low_open_df):
            lopen_lclose_df=low_open_df[low_open_df['close']<low_open_df['open']*(1+trade_rate*0.01)]
            lopen_lclose_rate=round(round(len(lopen_lclose_df),2)/len(low_open_df),2)
            print('lopen_lclose_rate_n%s=%s' %(high_open_rate,lopen_lclose_rate))
        return
    
    def is_drop_then_up(self,great_dropdown=-4.0,turnover_rate=0.75,turnover_num=None):
        #turnover_num=2, mean 2 days inscrease over turnover_rate
        temp_df=self._form_temp_df()
        is_drop_up=False
        actual_turnover_rate=0
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            pass
        else:
            if turnover_num and turnover_num<len(temp_df)-1:
                temp_df=temp_df.tail(turnover_num+1)
                drop_rate=temp_df.iloc[0].p_change
                temp_df_1=temp_df.tail(turnover_num)
                total_incrs_after_drop=temp_df_1['p_change'].sum()
                is_drop_up=total_incrs_after_drop>=turnover_rate*abs(drop_rate) and drop_rate<great_dropdown
                if is_drop_up:
                    actual_turnover_rate=round(total_incrs_after_drop/abs(drop_rate),4)
            elif not turnover_num and len(temp_df)>=2: #turnover_num=1
                temp_df=temp_df.tail(2)
                drop_rate=temp_df.iloc[0].p_change
                incrs_after_drop=temp_df.iloc[1].p_change
                is_drop_up=incrs_after_drop>=turnover_rate*abs(drop_rate) and drop_rate<great_dropdown
                if is_drop_up:
                    actual_turnover_rate=round(incrs_after_drop/abs(drop_rate),4)
            else:
                pass
        return is_drop_up,actual_turnover_rate
    
    def is_extreme_recent(self,recent_count=None,continue_extreme_count=None):
        temp_df=self._form_temp_df()
        continue_extreme_num=0
        is_continue_extreme=False
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            return is_continue_extreme,continue_extreme_num
        extreme_num=1
        extreme_rate=0.1
        recent_num=20
        if recent_count:
            recent_num=recent_count
        recent_df=temp_df.tail(min(len(temp_df),100))
        last_index=recent_df.index.values.tolist()[-1]
        if continue_extreme_count:
            extreme_num=continue_extreme_count
        extreme_df=recent_df[recent_df.volume<recent_df.v_ma10*extreme_rate]
        if extreme_df.empty:
            return is_continue_extreme,continue_extreme_num
        else:
            last_extreme_index=extreme_df.index.values.tolist()[-1]
            last_extreme_rate=extreme_df.tail(1).iloc[0].p_change
            is_extreme=(last_index-last_extreme_index)<recent_num
            if (last_index-last_extreme_index)<recent_num:
                continue_extreme_num=self.get_continue_index_num(extreme_df)
                if continue_extreme_num==0:
                    continue_extreme_num=1
                else:
                    pass
            continue_extreme_num=continue_extreme_num*int(last_extreme_rate/abs(last_extreme_rate))
            is_continue_extreme=continue_extreme_num>=extreme_num
            #print(self.code,continue_extreme_num)
        return is_continue_extreme,continue_extreme_num
    
    def get_recent_over_ma(self,ma_type='ma5',ma_offset=0.002,recent_count=None):
        temp_df=self._form_temp_df()
        count=len(temp_df)
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            return 0.0,0,'1979-01-01'
        else:
            if recent_count:
                count=min(len(temp_df),recent_count)
            else:
                pass
        temp_df=temp_df.tail(count)
        date_last=temp_df.tail(1).iloc[0].date
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        df_over_ma=temp_df[(temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1)]
        over_ma_rate=round(round(len(df_over_ma),4)/len(temp_df),4)
        #print('over_ma_rate=',over_ma_rate)
        continue_over_ma_num=0
        index_i=len(df_over_ma)-1
        index_list=df_over_ma.index.values.tolist()
        if df_over_ma.empty:
            return over_ma_rate,continue_over_ma_num,'1979-01-01'
        date_last_over_ma=df_over_ma.tail(1).iloc[0].date
        #print(date_last,date_last_over_ma)
        if date_last_over_ma==date_last:
            continue_over_ma_num=self.get_continue_index_num(df_over_ma)
        #print('continue_over_ma=',continue_over_ma_num)
        return over_ma_rate,continue_over_ma_num,date_last
    
    def get_continue_index_num(self,df):
        continue_num=0
        if df.empty:
            return continue_num
        index_i=len(df)-1
        index_list=df.index.values.tolist()
        while index_i>0:
            if index_list[index_i]-index_list[index_i-1]==1:
                continue_num+=1
            else:
                break
            index_i=index_i-1
        if continue_num>0:
            continue_num+=1
        return continue_num
    
    def get_trade_df(self,ma_type='ma5',ma_offset=0.002,great_score=4,great_change=5.0):
        #based on MA5
        #scoring based on recent three day's close: -5 to 5
        temp_df=self._form_temp_df()
        if len(temp_df)==0:
            return {}
        ma_offset=0.002
        temp_df['pv_rate']=(temp_df['p_change']/100.0/(temp_df['volume']-temp_df['volume'].shift(1))*temp_df['volume'].shift(1)).round(2)
        temp_df['v_rate']=(temp_df['volume']/temp_df['v_ma5'].shift(1)).round(2)
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])<-ma_offset*temp_df['close'].shift(1),-1,temp_df['c_o_ma']) #-1 for bellow ma
        #print temp_df
        WINDOW=3
        temp_df['sum_o_ma'] = np.round(pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW), 2)
        temp_df['trend_o_ma']=temp_df['sum_o_ma']-temp_df['sum_o_ma'].shift(1)
     
        temp_df['g-chg']=np.where(temp_df['p_change']>great_change,1,0)
        temp_df['g-chg']=np.where(temp_df['p_change']<-great_change,-1,temp_df['g-chg'])
        
        temp_df['score']=temp_df['sum_o_ma']+temp_df['trend_o_ma'] #+temp_df['g-chg']
        
        temp_df['max'] = np.round(pd.rolling_max(temp_df['score'], window=WINDOW), 2)
        temp_df['min'] = np.round(pd.rolling_min(temp_df['score'], window=WINDOW), 2)
        
        temp_df['operate']=np.where(temp_df['score']>=temp_df['min']+great_score,1,0)              #1 to buy, 0 to keep unchanged
        temp_df['operate']=np.where(temp_df['max']>=temp_df['score']+great_score,-1,temp_df['operate'])       #-1 to sell

        #count_sell= temp_df['operate'].value_counts()
        #print count_sell
        
        recent_sum=temp_df.tail(WINDOW)['operate'].sum()
        #print 'recent_sum=', recent_sum
        
        #"""
        non_zero_df=temp_df[temp_df['operate']!=0]
        if non_zero_df.empty:
            return {}
        this_stratege_state= non_zero_df.tail(1).iloc[0].operate
        this_stratege_date= non_zero_df.tail(1).iloc[0].date
        #print this_stratege_date,this_stratege_state
        this_state= temp_df.tail(1).iloc[0].operate
        this_date= temp_df.tail(1).iloc[0].date
        this_score=temp_df.tail(1).iloc[0].score
        #print this_date,this_state
        
        last_stratege_df=non_zero_df[non_zero_df['operate']!=this_stratege_state]#.tail(1)
        last_stratege_date=last_stratege_df.tail(1).iloc[0].date
        #print last_stratege_date
        #temp_df['market']=np.log(temp_df['close']/temp_df['close'].shift(1))
        #temp_df['strategy']=temp_df['regime'].shift(1)*temp_df['market']
        result_data={'code':self.code,
                     'l_s_date':last_stratege_date,
                     'l_s_state':this_stratege_state*(-1),
                     't_s_date':this_stratege_date,
                     't_s_state':this_stratege_state,
                     't_date':this_date,
                     't_state':this_state,
                     'score':this_score,
                     'oper3':recent_sum
                     }
        #result_list=[self.code,last_stratege_date,this_stratege_state*(-1),this_stratege_date,this_stratege_state,this_date,this_state,this_score,recent_sum]
        #print result_list
        #"""
        temp_df.to_csv(ROOT_DIR+'/trade_temp/%s.csv'%self.code)
        #print 'temp_df=',temp_df
        return result_data
    
    def get_trade_df0(self,ma_type='ma5',ma_offset=0.01,great_score=4,great_change=5.0):
        #based on MA5
        #scoring based on recent three day's close: -5 to 5
        temp_df=self._form_temp_df()
        temp_df['c_o_ma']=temp_df['close']-temp_df[ma_type]
        ma_offset=0.01
        temp_df['regime']=np.where(temp_df['c_o_ma']>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        temp_df['regime']=np.where(temp_df['c_o_ma']<-ma_offset*temp_df['close'].shift(1),-1,temp_df['regime']) #-1 for bellow ma
        #print temp_df
        WINDOW=3
        temp_df['gt_ma'] = np.round(pd.rolling_sum(temp_df['regime'], window=WINDOW), 2)
        temp_df['gt-ma5-incrs']=temp_df['gt_ma']-temp_df['gt_ma'].shift(1)
     
        
        temp_df['g-chg']=np.where(temp_df['p_change']>great_change,1,0)
        temp_df['g-chg']=np.where(temp_df['p_change']<-great_change,-1,temp_df['g-chg'])
        
        temp_df['score']=temp_df['gt_ma']+temp_df['gt-ma5-incrs'] #+temp_df['g-chg']
        
        temp_df['max'] = np.round(pd.rolling_max(temp_df['score'], window=WINDOW), 2)
        temp_df['min'] = np.round(pd.rolling_min(temp_df['score'], window=WINDOW), 2)
        
        temp_df['sell']=np.where(temp_df['score']>=temp_df['min']+great_score,1,0)              #1 to buy, 0 to keep unchanged
        temp_df['sell']=np.where(temp_df['max']>=temp_df['score']+great_score,-1,temp_df['sell'])       #-1 to sell

        #count_sell= temp_df['sell'].value_counts()
        #print count_sell
        
        recent_sum=temp_df.tail(WINDOW)['sell'].sum()
        #print 'recent_sum=', recent_sum
        
        #"""
        non_zero_df=temp_df[temp_df['sell']!=0]
        this_stratege_state= non_zero_df.tail(1).iloc[0].sell
        this_stratege_date= non_zero_df.tail(1).iloc[0].date
        #print this_stratege_date,this_stratege_state
        this_state= temp_df.tail(1).iloc[0].sell
        this_date= temp_df.tail(1).iloc[0].date
        #print this_date,this_state
        
        last_stratege_df=non_zero_df[non_zero_df['sell']!=this_stratege_state]#.tail(1)
        last_stratege_date=last_stratege_df.tail(1).iloc[0].date
        #print last_stratege_date
        #temp_df['market']=np.log(temp_df['close']/temp_df['close'].shift(1))
        #temp_df['strategy']=temp_df['regime'].shift(1)*temp_df['market']
        result_list=[self.code,last_stratege_date,this_stratege_state*(-1),this_stratege_date,this_stratege_state,this_date,this_state,recent_sum]
        #print result_list
        #"""
        temp_df.to_csv(ROOT_DIR+'/trade_temp/%s.csv'%self.code)
        return recent_sum
    
    def boduan_analyze(self):
        df=self.temp_hist_df
        #print df
        boduan_list=[]
        analyze_types=['close','ma5','ma10','ma20','ma30','ma60','ma120','ma250']
        if df.empty:
            return
        df_num=len(df)
        split_index=1
        if df_num<5:
            split_index=1
        elif df_num<10:
            split_index=2
        elif df_num<20:
            split_index=3
        elif df_num<30:
            split_index=4
        elif df_num<60:
            split_index=5
        elif df_num<120:
            split_index=6
        elif df_num<250:
            split_index=7
        else:
            split_index=8 
        analyze_types=analyze_types[:split_index]
        df.fillna(0)
        for analyze_type in analyze_types:
            analyze_list=df[analyze_type].values.tolist()
            boduan_list=find_boduan(analyze_list)
            print('%s_boduan_list=%s' % (analyze_type,boduan_list[-20:]))
            if len(boduan_list)>=3:
                last_value0=boduan_list[-1]
                last_value1=boduan_list[-2]
                last_value2=boduan_list[-3]
                if last_value0>last_value1:
                    print('The trade of %s is INREASING from %s to %s' % (analyze_type,last_value1,last_value0))
                    print('The upholding is %s , and the press is %s' % (last_value1,last_value2))
                else:
                    print('The trade of %s is DECREASING from %s to %s' % (analyze_type,last_value1,last_value0))
                    print('The upholding is %s , and the press is %s' % (last_value2,last_value1))
            else:
                pass
        return
    
    def hist_analyze(self,num):
        df=self._form_temp_df()
        rate=0.8
        df = df.tail(num)
        mean_c=(df['p_change'].mean()).round(2)
        mean_h=(df['h_change'].mean()).round(2)
        mean_l=(df['l_change'].mean()).round(2)
        mean_h_df=df[df.h_change>mean_h]
        mean_h_2=(mean_h_df['h_change'].mean()).round(2)
        #print 'mean_h_2=',mean_h_2
        current_price=self.get_mean('close', 1)
        #print 'current_price=',current_price
        ma5=self.get_predict_ma('close', 5,mean_c)
        ma10=self.get_predict_ma('close', 10,mean_c)
        
        h_sell_1=round(current_price*(1+mean_h/100),2)
        h_sell_2=round(current_price*(1+mean_h_2/100),2)
        #print 'h_sell_1=',mean_h
        #print 'h_sell_2=',mean_h_2
        buy_in=round(current_price*(1+mean_l/100),2)
        l_sell_1=min(ma5,ma10,buy_in)
        mean_l_df=df[df.l_change<mean_l]
        mean_l_2=(mean_l_df['l_change'].mean()).round(2)
        l_sell_2=round(current_price*(1+mean_l_2/100),2)
        l_sell_2=min(ma5,ma10,l_sell_2)
        
        print('buy_in gt ma5: ', buy_in>=ma5)
        print('buy_in gt ma10: ', buy_in>=ma10)
        worth_buy_in=buy_in>=ma5 and buy_in>=ma10
        
        price_data={'cur_prc':[current_price],'p_ma5':ma5,'p_ma10':ma10,'h_sell1':h_sell_1,'h_sell2':h_sell_2,'l_sell1':l_sell_1,'l_sell2':l_sell_2,'buy_in':buy_in,'worth_in':worth_buy_in}
        price_column=['cur_prc','p_ma5','p_ma10','h_sell1','h_sell2','l_sell1','l_sell2','buy_in','worth_in']
        
        price_df=pd.DataFrame(price_data,columns=price_column)
        #print price_df
    
        #print 'mean_c=',mean_c
        mean_c_df=df[df.h_change>=mean_c]
        h_gt_meanc_rate=round(round(len(mean_c_df),2)/num,2)
        #print 'h_change_gt_mc_%s_n=%s'%(mean_c,h_gt_meanc_rate)
    
        h_gt_meanh_rate=round(round(len(mean_h_df),2)/num,2)
        c_lt_meanh_rate=round(round(len(df[df.p_change<mean_h]),2)/num,2)
        #print 'h_change_gt_mh_%s_n=%s' % (mean_h,h_gt_meanh_rate)
        #print 'p_change_lt_mh_%s_n=%s' % (mean_h,c_lt_meanh_rate)
  
        
        l_lt_meanl_rate=round(round(len(mean_l_df),2)/num,2)
        c_gt_meanl_rate=round(round(len(df[df.p_change>=mean_l]),2)/num,2)
   
        #print 'l_change_lt_ml_%s_n=%s' % (mean_l,l_lt_meanl_rate)
        #print 'p_change_gt_ml_%s_n=%s' % (mean_l,c_gt_meanl_rate)
    
        data={'mc':[mean_c],'mh1':mean_h,'mh2':mean_h_2,'ml1':mean_l,'ml2':mean_l_2,'h_gt_mc':h_gt_meanc_rate,'h_gt_mh':h_gt_meanh_rate,'c_lt_mh':c_lt_meanh_rate,'l_lt_ml':l_lt_meanl_rate,'c_gt_ml':c_gt_meanl_rate}
        column_list=['mc','mh1','mh2','ml1','ml2','h_gt_mc','h_gt_mh','c_lt_mh','l_lt_ml','c_gt_ml']
        """<price>_gt_mean<high>:highprice_gt_meanhigh as  h_gt_mh"""
        hist_df=pd.DataFrame(data,columns=column_list) #,index=['2015-05-15'])
        #print hist_df
    
        
    #get topest df for history data
    def get_hist_topest(self,recent_days=None):
        if recent_days!=None and recent_days<len(self.h_df):
            df=self.h_df.tail(recent_days)
            self.set_history_df(df)
        temp_df=self._form_temp_df()
        #print temp_df
        topest_df=temp_df[temp_df.close==(temp_df.last_close*1.1).round(2)]   #filter the topest items
        topest_rate=round(round(len(topest_df),3)/len(temp_df),3)
        return topest_df,topest_rate
    
    def filter_hist(self,operator,threshhold_rate,recent_days=None):
        temp_df=self._form_temp_df()
        if recent_days!=None and recent_days<len(temp_df):
            temp_df=temp_df.tail(recent_days)
        #print temp_df
        criteria=True
        if operator=='gte':
            #criteria=temp_df.close>=temp_df.last_close*threshhold_rate/100
            criteria=temp_df.p_change>=threshhold_rate
        else:
            if operator=='lt':
                #criteria=temp_df.close<temp_df.last_close*threshhold_rate/100
                criteria=temp_df.p_change<threshhold_rate
            else:
                pass
        filter_df=temp_df[criteria]
        filter_rate=round(round(len(filter_df),3)/len(temp_df),3)
        return filter_df,filter_rate
    #get max data of <latest_num> days
    def get_max(self,column_name='close',latest_num=None):
        df=self.h_df
        if latest_num !=None and len(df)>=latest_num:
            #df = df.head(latest_num)
            df = df.tail(latest_num)
            #print 'The latest df:',df
        max_idx=df[column_name].idxmax()
        max_value=df[column_name].max()
        max_value=round(max_value,2)
        max_series=df.ix[max_idx]
        min_idx=df[column_name].idxmin()
        min_value=df[column_name].min()
        min_value=round(min_value,2)
        min_series=df.ix[min_idx]
        return max_series,max_value,min_series,min_value
    
    #get min data of <latest_num> days
    def get_min(self,column_name='close',latest_num=None):
        df=self.h_df
        if latest_num !=None and len(df)>=latest_num:
            #df = df.head(latest_num)
            df = df.tail(latest_num)
        min_idx=df[column_name].idxmin()
        min_value=df[column_name].min()
        min_value=round(min_value,2)
        min_series=df.ix[min_idx]
        return min_series,min_value
    
    #get min data of <latest_num> days
    def get_mean(self,column_name,latest_num):
        df=self.h_df
        #print 'mean df:',df
        #print latest_num
        #if latest_num !=None  and len(df)>=latest_num:
        df = df.tail(latest_num)
        mean_value=df[column_name].mean()
        mean_value=round(mean_value,2)
        return mean_value
    
    def get_ma(self,column,ma_num):
        mean_value=self.get_mean(column, ma_num)
        return mean_value
    
    def get_predict_ma(self,column,ma_num,mean_inrcs):
        df=self.h_df
        ma_num=min(len(df),ma_num)  #to prevent 'index exceed
        df = df.tail(ma_num)
        mean_value=df[column].mean()
        value_list=df[column].values.tolist()
        value_0=value_list[0]#df.ix[0].column
        value_n=value_list[ma_num-1] #df.ix[(ma_num-1)].column
        predict_ma=mean_value+(value_n*(1+mean_inrcs/100)-value_0)/ma_num
        predict_ma=round(predict_ma,2)
        if self.DEBUG_ENABLED: print('predict_ma%s=%s'%(ma_num,predict_ma))
        return predict_ma
    
    def get_realtime_ma(self,column,ma_num,current_price):
        df=self.h_df
        ma_num=min(len(df),ma_num)  #to prevent 'index exceed
        df = df.tail(ma_num)
        mean_value=df[column].mean()
        value_list=df[column].values.tolist()
        value_0=value_list[0]#df.ix[0].column
        value_n=value_list[ma_num-1] #df.ix[(ma_num-1)].column
        predict_ma=mean_value+(current_price-value_0)/ma_num
        predict_ma=round(predict_ma,2)
        if self.DEBUG_ENABLED: print('predict_ma%s=%s'%(ma_num,predict_ma))
        return predict_ma
    
    def get_atr_df(self,short_num, long_num):
        temp_df=self.h_df
        if len(temp_df)==0:
            return temp_df,'','',0.0
        temp_df.is_copy=False  
        #temp_df.fillna(0)
        #temp_df.fillna(method='pad')
        #temp_df=temp_df.fillna(method='bfill')
        
        #temp_df['atr']=max(temp_df['high']-temp_df['low'],temp_df['high']-temp_df['close'].shift(1), temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['high']-temp_df['low']<temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<temp_df['close'].shift(1)-temp_df['low'],temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        #temp_df['atr_rate']=(2.00*temp_df['atr']*100/(temp_df['high']+temp_df['low'])).round(0)
        temp_df['atr_rate']=(temp_df['atr']*100/temp_df['close'].shift(1)).round(0)
        temp_df['atr_%s'%short_num] = np.round(pd.rolling_mean(temp_df['atr'], window=short_num), 2)
        temp_df['atr_%s'%long_num] = np.round(pd.rolling_mean(temp_df['atr'], window=long_num), 2)
        
        temp_df['atr_std%s'%short_num] = np.round(pd.rolling_std(temp_df['atr_rate'], window=short_num), 2)
        temp_df['atr_var%s'%short_num] = np.round(pd.rolling_var(temp_df['atr_rate'], window=short_num), 2)
        temp_df['max_%s'%short_num] = np.round(pd.rolling_max(temp_df['high'], window=short_num), 2)
        temp_df['break_up_%s'%short_num]=np.where(temp_df['high']>temp_df['max_%s'%short_num].shift(1),1,0)
        temp_df['min_%s'%short_num] = np.round(pd.rolling_min(temp_df['low'], window=short_num), 2)
        temp_df['subtr_%s'%short_num]=temp_df['max_%s'%short_num]-temp_df['min_%s'%short_num]
        temp_df['break_up_%s'%short_num]=np.where(temp_df['low']<temp_df['min_%s'%short_num].shift(1),-1,temp_df['break_up_%s'%short_num])
        temp_df['max_%s'%long_num] = np.round(pd.rolling_max(temp_df['high'], window=long_num), 2)
        temp_df['break_up_%s'%long_num]=np.where(temp_df['high']>temp_df['max_%s'%long_num].shift(1),1,0)
        temp_df['min_%s'%long_num] = np.round(pd.rolling_min(temp_df['low'], window=long_num), 2)
        temp_df['subtr_%s'%long_num]=temp_df['max_%s'%long_num]-temp_df['min_%s'%long_num]
        temp_df['break_up_%s'%long_num]=np.where(temp_df['low']<temp_df['min_%s'%long_num].shift(1),-1,temp_df['break_up_%s'%long_num])
        temp_df['break_sum_%s'%short_num]=np.round(pd.rolling_sum(temp_df['break_up_%s'%short_num], window=2), 2)
        temp_df['break_sum_%s'%long_num]=np.round(pd.rolling_sum(temp_df['break_up_%s'%long_num], window=2), 2)
        #print temp_df
        crit1=temp_df['break_up_%s'%short_num]==1 
        crit2=temp_df['break_sum_%s'%short_num]==1
        #temp_df=temp_df.fillna(0)
        temp_df=temp_df.fillna(method='bfill')
        #print temp_df
        #temp_df['1st_break'%short_num]=np.where(temp_df['break_sum_%s'%short_num]>temp_df['break_up_%s'%short_num],1,0)
        #temp_df['1st_break'%short_num]=np.where(temp_df['break_sum_%s'%short_num]>1,1,0)
        #crit1=temp_df.break_sum_20==1
        #crit2=temp_df.break_up_20==1
        df_20=temp_df[crit1&crit2]#[temp_df['break_sum_%s'%short_num]==1 and temp_df['break_up_%s'%short_num]==1]
        #print 'df='
        #print len(df)
        #print df_20['date'].values.tolist()
        
        crit1=temp_df['break_up_%s'%long_num]==1 
        crit2=temp_df['break_sum_%s'%long_num]==1
        df_55=temp_df[crit1&crit2]
        latest_break_20=''
        latest_break_55=''
        if df_20['date'].values.tolist(): latest_break_20=df_20['date'].values.tolist()[-1]
        if df_55['date'].values.tolist():latest_break_55=df_55['date'].values.tolist()[-1]
        temp_df.to_csv(ROOT_DIR+'/result_temp/atr_%s.csv' % self.code)
        #print temp_df
        print(temp_df['atr_rate'].value_counts())
        atr_s= (temp_df['atr_rate'].value_counts()/temp_df['atr_rate'].count()).round(2)
        #print 'atr_static:'
        #print atr_s
        value_list=atr_s.values.tolist()
        wave_rate_list=atr_s.index.tolist()
        sum_point=0.00
        value_list_sum=0.00
        for i in range(5):#(len(value_list)):
            sum_point+=value_list[i]*wave_rate_list[i]
            value_list_sum+=value_list[i]
        weight_average_atr=round(sum_point/value_list_sum,2)
        #print 'weight_average_atr=%s%%' % weight_average_atr
        top5_average=sum(atr_s.index.tolist()[:5])/5.00
        #print 'top5_average=%s%%' % top5_average
      
        return temp_df,latest_break_20,latest_break_55,top5_average
    
    def get_macd_df(self,short_num, long_num,dif_num,current_price):
        temp_df=self.h_df
        temp_df.is_copy=False
        short_num=12
        long_num=26
        dif_num=9
        print(temp_df)
        temp_df.index.name=['idx']
        idx_list=temp_df.index.values.tolist()
        idx_df=pd.DataFrame({'idx':idx_list})
        idx_df=idx_df.astype(int)
        print('idx_df')
        #print idx_df
        #print (temp_df['idx'])
        temp_df['idx']=idx_df['idx']
        temp_df['idx'].astype(int)
        print(temp_df.dtypes)
        temp_df['s_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=short_num), 2)
        #temp_df['s_ma_csum']=temp_df['close'].cumsum()
        temp_df['s_ma']=np.where(temp_df['idx']<short_num, np.round(temp_df['close'].cumsum()/(temp_df['idx']+1), 2), temp_df['s_ma']) 
        #temp_df['s_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=short_num), 2)
        
        temp_df['l_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=long_num), 2)
        temp_df['l_ma']=np.where(temp_df['idx']<long_num, np.round(temp_df['close'].cumsum()/(temp_df['idx']+1), 2), temp_df['l_ma']) 
        
        #temp_df['dif'] =temp_df['s_ma']-temp_df['l_ma']
        temp_df['dif'] =idx_df['idx']-idx_df['idx']
        temp_df['maca']=idx_df['idx']-idx_df['idx']
        print(temp_df)
        temp_df['dif'] = np.where(temp_df['idx']<1,temp_df['dif'],temp_df['s_ma'].shift(1)*(short_num-1)/(short_num+1)+temp_df['close']*2/(short_num+1)-temp_df['l_ma'].shift(1)*(long_num-1)/(long_num+1)-temp_df['close']*2/(long_num+1))
        temp_df['maca'] = np.round(pd.rolling_mean(temp_df['dif'], window=dif_num), 2)
        temp_df['maca'] = np.where(temp_df['idx']<dif_num, np.round(temp_df['dif'].cumsum()/(temp_df['idx']+1), 2), temp_df['maca'])
        
        temp_df['dea'] = idx_df['idx']-idx_df['idx']
        temp_df['dea'] =np.where(temp_df['idx']<1,temp_df['dif'],temp_df['dea'].shift(1)*(dif_num-1)/(dif_num+1)+temp_df['dif']*2/(dif_num+1))
        #temp_df['dea'] = np.round(pd.rolling_mean(temp_df['dif'], window=dif_num), 2)
        temp_df['bar']=idx_df['idx']-idx_df['idx']
        temp_df['bar']=np.where(temp_df['idx']<1,temp_df['bar'],(temp_df['dif']-temp_df['dea'])*2)
        print(temp_df)
        temp_df.to_csv(ROOT_DIR+'/result/macd%s.csv'%self.code)
        return temp_df
    
    def get_reatime_macd(self,short_num, long_num,dif_num,current_price):
        macd_df=self.get_macd_df(short_num, long_num, dif_num, current_price).tail(1).iloc[0]
        ema1_last=macd_df.s_ma
        ema2_last=macd_df.l_ma
        dif_last=macd_df.dif
        dea_last=macd_df.dea
        macd_last=macd_df.bar
        ema1=ema1_last*(short_num-1)/(short_num+1)+current_price*2/(short_num+1)
        ema2=ema2_last*(long_num-1)/(long_num+1)+current_price*2/(long_num+1)
        dif_realtime=ema1-ema2
        dea_realtime=dea_last*(dif_num-1)/(dif_num+1)+dif_realtime*2/(dif_num+1)
        macd_realtime=2*(dif_realtime-dea_realtime)
        print('For last: dif=%s, dea=%s, bar=%s' % (dif_last,dea_last,macd_last)) 
        print('Realtime: dif=%s, dea=%s, bar=%s' % (dif_realtime,dea_realtime,macd_realtime)) 
        return dif_realtime,dea_realtime,macd_realtime
    
    def is_potential_cross_N(self,cross_num):
        """
        ma5=self.get_ma('close', 5)
        #print 'ma5=', ma5
        ma10=self.get_ma('close', 10)
        #print 'ma10=',ma10
        ma20=self.get_ma('close', 20)
        #print 'ma20=',ma20
        ma30=self.get_ma('close', 30)
        ma60=self.get_ma('close', 60)
        """
        rate=0.5
        ma5=self.get_predict_ma('close', 5,rate)
        print('ma5=', ma5)
        ma10=self.get_predict_ma('close', 10,rate)
        print('ma10=',ma10)
        ma20=self.get_predict_ma('close', 20,rate)
        print('ma20=',ma20)
        ma30=self.get_predict_ma('close', 30,rate)
        ma60=self.get_predict_ma('close', 60,rate)
        current_price=ma5=self.get_ma('close', 1)#potential_df.iloc[0]['close']
        print('current_price=',current_price)
        min_ma=0.0
        max_ma=0.0
        
        if cross_num==1:
            min_ma=ma5
            max_ma=ma5
        else:
            if cross_num==2:
                min_ma=min(ma5,ma10)#round(min(ma5,ma10)*(1-rate/100),2)
                max_ma=max(ma5,ma10)
            else:
                if cross_num==3:
                    min_ma=min(ma5,ma10,ma20)#round(min(ma5,ma10,ma20)*(1-rate/100),2)
                    max_ma=max(ma5,ma10,ma20)
                else:
                    if cross_num==4:
                        min_ma=min(ma5,ma10,ma20,ma30)#round(min(ma5,ma10,ma20,ma30)*(1-rate/100),2)
                        max_ma=max(ma5,ma10,ma20,ma30)
                    else:
                        pass
        print('min_ma=',min_ma)
        is_potential=current_price<=min_ma and current_price*1.10>max_ma
        return is_potential

    def is_cross_N(self,cross_num,cross_type):
        potential_df=self.h_df.tail(1) #[self.today_df.trade>self.today_df.open]
        high_price=potential_df.iloc[0]['high']
        low_price=potential_df.iloc[0]['low']
        #print 'potential_df:',potential_df
        current_price=potential_df.iloc[0]['close']
        if cross_type=='potential':
            current_price=high_price
        else:
            if cross_type=='actual':
                pass
            else:
                pass
        today_open_price=potential_df.iloc[0]['open']
        #print current_price
        ma5=self.get_ma('close', 5)
        #print 'ma5=', ma5
        ma10=self.get_ma('close', 10)
        #print 'ma10=',ma10
        ma20=self.get_ma('close', 20)
        #print 'ma20=',ma20
        ma30=self.get_ma('close', 30)
        ma60=self.get_ma('close', 60)
        current_price_over_ma=False
        open_price_bellow_ma=False
        if cross_num==1:
            current_price_over_ma=current_price>=ma5 and 0.5*(high_price+low_price)>=ma10
            open_price_bellow_ma=today_open_price<=ma5
        else:
            if  cross_num==2:
                current_price_over_ma=current_price>=ma5 and current_price>=ma10 and 0.5*(high_price+low_price)>=ma20
                open_price_bellow_ma=today_open_price<=min(ma5,ma10)
            else:
                if cross_num==3:
                    current_price_over_ma=current_price>=ma5 and current_price>=ma10 and current_price>=ma20
                    open_price_bellow_ma=today_open_price<=min(ma5, ma10,ma20)
                else:
                    if cross_num==4:
                        current_price_over_ma=current_price>=ma5 and current_price>=ma10 and current_price>=ma20 and current_price>=ma60
                        open_price_bellow_ma=today_open_price<=min(ma5, ma10,ma20,ma60)
                    else:
                        pass
        is_cross_N=current_price_over_ma and open_price_bellow_ma
        return is_cross_N

    def is_101(self,potential):
        if len(self.h_df)<3:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(3)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                #close_1=high_1
                #close_2=high_2
                close_3=high_3
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #day2 is star
            day2_is_justsoso=close_2<=0.5*(close_1+close_2) and abs(close_2-open_2)<(high_2-low_2)*0.33
            #day2_is_justsoso=True
            day3_is_strong=round((close_3-open_3),2)/open_3*100>1 and abs(close_1-open_1)<(close_3-open_3)*1.01 and close_1<=close_3*1.02 and 1.02*close_3>=max(close_1,high_2)
            #day3_is_strong=True
            volume_is_line=vlm_1>vlm_2 and vlm_2<=vlm_3
            volume_is_line=True
            is_101=day1_is_strong and day2_is_justsoso and day3_is_strong and volume_is_line
            #"""
            return is_101
        except:
            return False
        
    def is_10_fanzhuang(self):
        if len(self.temp_hist_df)<2:
            print('No enough history data for 101 verify!')
            return False
        df=self.temp_hist_df.tail(3)
        
        return  
     
    def is_10(self,potential):
        if len(self.h_df)<2:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(2)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            #vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            #open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            #high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            #close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            #low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                #close_1=high_1
                #close_2=high_2
                close_2=high_2
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #day2 is star
            day2_is_justsoso=close_2<=0.5*(close_1+close_2) and abs(close_2-open_2)<(high_2-low_2)*0.25 
            #day2_is_justsoso=True
            #day3_is_strong=round((close_3-open_3),2)/open_3*100>1 and abs(close_1-open_1)<(close_3-open_3)*1.01 and close_1<=close_3*1.02 and 1.02*close_3>=max(close_1,high_2)
            #day3_is_strong=True
            volume_is_line=vlm_1*0.9>vlm_2
            #volume_is_line=True
            is_10=day1_is_strong and day2_is_justsoso and volume_is_line
            #"""
            return is_10
        except:
            return False
        
    def is_constant_1(self):
        potential_df=self.h_df.tail(2) #[self.today_df.trade>self.today_df.open]
        high_price1=potential_df.iloc[0]['high']
        low_price1=potential_df.iloc[0]['low']
        close_price1=potential_df.iloc[0]['close']
        
        high_price2=potential_df.iloc[1]['high']
        low_price2=potential_df.iloc[1]['low']
        close_price2=potential_df.iloc[1]['close']
        is_const_1=(low_price2==high_price2) and (close_price2==round(close_price1*1.1,2)) and (close_price2==low_price2)
        return is_const_1
    
    def is_star(self,rate):
        potential_df=self.h_df.tail(2) #[self.today_df.trade>self.today_df.open]
        high_price1=potential_df.iloc[0]['high']
        low_price1=potential_df.iloc[0]['low']
        close_price1=potential_df.iloc[0]['close']
        
        high_price2=potential_df.iloc[1]['high']
        low_price2=potential_df.iloc[1]['low']
        close_price2=potential_df.iloc[1]['close']
        open_price2=potential_df.iloc[1]['open']
        is_star=abs(close_price2-open_price2)<=rate*(high_price2-low_price2)
        return is_star
    
    def get_star_df(self,rate,raw_df):
        df=raw_df
        crit1=abs(df.close-df.open)/(df.high-df.low)<rate
        df=df[crit1]
        return df
    
    def get_next_df(self,raw_df,filter_df,next_num):
        filter_df_indexs=filter_df.index.values.tolist()
        print(filter_df_indexs)
        next_df_indexs_new=[]
        for filter_df_index in filter_df_indexs:
            next_df_indexs_new.append(filter_df_index+next_num)
        
        print(next_df_indexs_new)
        
        next_df=raw_df[raw_df.index.isin(next_df_indexs_new)]
        next_df_p_change_mean=next_df['p_change'].mean()
        print('next_df_p_change_mean=',next_df_p_change_mean)
        next_df_gt_0=next_df[next_df.p_change>0.2]
        print(len(filter_df))
        print(len(next_df_gt_0))
        filter_then_gt0_rate=round(round(len(next_df_gt_0),2)/len(filter_df),2)
        print('filter_then_next%s_gt0_rate=%s' % (next_num,filter_then_gt0_rate))

    def is_110(self,potential):
        if len(self.h_df)<3:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(3)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                close_1=high_1
                close_2=high_2
                close_3=high_3
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #print round((close_1-open_1),2)/open_1*100
            day2_is_strong=round((close_2-open_2),2)/open_2*100>1.5
  
            day3_is_justsoso=(high_3-low_3)<0.8*min((high_1-low_1),(high_2-low_2))
            #day3_is_justsoso=True
            volume_is_line=vlm_3<1.01*min(vlm_1,vlm_2)
            volume_is_line=True
            is_110=day1_is_strong and day2_is_strong and day3_is_justsoso and volume_is_line
            #"""
            return is_110
        except:
            return False
        
    def get_realtime_data(self):
        realtime_df = ts.get_realtime_quotes(self.code) #Single stock symbol
        realtime_df=realtime_df[['code','open','pre_close','price','high','low','bid','ask','volume','amount','time']]
        #realtime_df=realtime_df['pre_close'].astype(float)
        #realtime_df=realtime_df['price'].astype(float)
        """
        open_price= df['open'].mean()
        pre_close_price= df['pre_close'].mean()
        current_price= df['price'].mean()
        high_price= df['high'].mean()
        low_price= df['low'].mean()
        bid_price= df['bid'].mean()
        ask_price= df['ask'].mean()
        volume_price= df['volume'].mean()
        amount_price= df['amount'].mean()
        this_time= df['time'].mean()
        """
        return realtime_df
    
    #def get_realtime_value(self,realtime_df,column_name):
        #return realtime_df[column_name].mean()
    
    def get_realtime_mean_price(self,realtime_df):
        #volume=self.get_realtime_value(realtime_df, 'volume')
        #amount=self.get_realtime_value(realtime_df, 'amount')
        volume=float(realtime_df.ix[0].volume)
        amount=float(realtime_df.ix[0].amount)
        realtime_mean_price=0
        if amount!=0:
            realtime_mean_price=round(round(amount,2)/volume,2)
            print('realtime_mean_price=',realtime_mean_price)
        return realtime_mean_price
        
    def is_realtime_price_gte_mean(self,realtime_df):
        #return self.get_realtime_value(realtime_df, 'price')>=self.get_realtime_mean_price(realtime_df)
        return realtime_df.ix[0].price>=self.get_realtime_mean_price(realtime_df)
    
    def get_weak_lt_interval(self,realtime_df,realtime_mean_price):    #get the interval little than mean price
        realtime_lt_mean_interval=0
        this_time=realtime_df.ix[0].time
        #print type(this_time)
        this_date_time=tradeTime.get_latest_trade_date()+ ' '+this_time
        if realtime_df.ix[0].price>=realtime_mean_price:  #is_realtime_price_gte_mean
            self.realtime_stamp=get_timestamp(this_date_time)
        else:
            this_realtime_lt_mean_stamp=get_timestamp(this_date_time)
            realtime_lt_mean_interval=this_realtime_lt_mean_stamp-self.realtime_stamp
            print('this_date_time=',this_date_time)
            print('realtime_lt_mean_interval=',realtime_lt_mean_interval)
        return realtime_lt_mean_interval
    
    def get_weak_sell_price(self,realtime_df,realtime_mean_price,permit_interval):
        
        #realtime_mean_price=self.get_realtime_mean_price(realtime_df)
        realtime_weak_interval=self.get_weak_lt_interval(realtime_df,realtime_mean_price)
        sell_pirce=0
        if realtime_weak_interval>=permit_interval:  #permit_interval>=60 seconds
            realtime_price=self.get_realtime_value(realtime_df, 'price')
            sell_pirce=realtime_price+0.382*(realtime_mean_price-realtime_price)
            print('realtime_lt_mean_interval=%s, which is great than permit_interval=%s'%(realtime_weak_interval,permit_interval))
            print('set sell_pirce=%s , and realtime_mean_price=%s'%(sell_pirce,realtime_mean_price))
        return sell_pirce
    
    def email_trigger(self,alarm_list):
        if alarm_list:
            alarm_category=alarm_list[3]
            print(self.alarm_category,alarm_category)
            if self.alarm_category==alarm_category:     # alarm_category does not change
                alarm_list=[]
            else:
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                if self.DEBUG_ENABLED: print('alarm_list=',alarm_list)
        else:
            alarm_list=[]
        return alarm_list
    
    def ma_alarm(self,ma_num,current_price,this_date_time):
        ma=self.get_realtime_ma('close', ma_num, current_price)
        if current_price<ma*0.99:
            alarm_content='Down through ma_%s: %s, sell 1/3.' % (ma_num,ma)
            alarm_content=alarm_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alert'
            alarm_category='lt_ma'
            alarm_list=[self.code,this_date_time,alarm_type,alarm_category,alarm_content]
            alarm_list=self.email_trigger( alarm_list)
        else:
            pass
    
    def alarm_logging(self,realtime_df):
        
        #print realtime_df.dtype()
        #open_price=realtime_df.ix[0].open
        #print 'open_price=',open_price
        #print type(open_price)
        """
        open_price= self.get_realtime_value(realtime_df,'open')
        #print type(open_price)
        pre_close_price= self.get_realtime_value(realtime_df,'pre_close')
        current_price= self.get_realtime_value(realtime_df,'price')
        high_price= self.get_realtime_value(realtime_df,'high')
        low_price= self.get_realtime_value(realtime_df,'low')
        bid_price= self.get_realtime_value(realtime_df,'bid')
        ask_price= self.get_realtime_value(realtime_df,'ask')
        volume_price=self.get_realtime_value(realtime_df,'volume') 
        amount_price= self.get_realtime_value(realtime_df,'amount')
        """
        open_price=float(realtime_df.ix[0].open)
        pre_close_price=float(realtime_df.ix[0].pre_close)
        current_price= float(realtime_df.ix[0].price)
        high_price=float(realtime_df.ix[0].high)
        low_price=float(realtime_df.ix[0].low)
        bid_price=float(realtime_df.ix[0].bid)
        ask_price=float(realtime_df.ix[0].ask)
        volume=float(realtime_df.ix[0].volume)
        amount=float(realtime_df.ix[0].amount)
        
        per_change=round((current_price-pre_close_price)*100/pre_close_price,2)
        high_change=round((high_price-pre_close_price)*100/pre_close_price,2)
        #this_time='13:35:47'
        this_time= realtime_df.ix[0].time
        this_date_time=tradeTime.get_latest_trade_date()+' '+this_time
        this_timestamp=get_timestamp(this_date_time)
        print('%s  %s---------------------------------------------------------'% (self.code,this_date_time))
        #print this_timestamp
        hist_high_rate=self.get_average_high(60)
        hist_low_rate=self.get_average_low(60)
        expect_profile_rate=hist_high_rate
        terminate_loss_rate=hist_low_rate
        print('expect_profile_rate=',expect_profile_rate)
        print('terminate_loss_rate=',terminate_loss_rate)
        drop_down_rate=min(-1.5,0.33*terminate_loss_rate)
        print('drop_down_rate=',drop_down_rate)
        hold_time=60*5
        #state_confirm=False
        average_inrcs=1.0
        average_decrs=-1.0
        #print realtime_df
        #print current_price
        alarm_list=[]
        alarm_type=''   #notice,alarm,alarm
        #alarm_category=''
        alarm_content=''
        stock_code=self.code
        #alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
        current_content='Current price = %s, and per_change=%s%%'%(current_price,per_change)
        permit_interval=5*60
        realtime_mean_price=self.get_realtime_mean_price(realtime_df)
        weak_sell_price=self.get_weak_sell_price(realtime_df, realtime_mean_price, permit_interval)
        if weak_sell_price>0:
            alarm_content='weak_sell_price= %s. '% weak_sell_price
            alarm_content=alarm_content+current_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alarm'
            alarm_category='lt_day_mean'
            alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
            self.alarm_category=alarm_category
            send_mail(alarm_list)
            
        
        if high_price>self.max_price:
            if self.max_price!=-1: 
                alarm_content='New topest price: %s. '% high_price
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='new_highest'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                #alarm_list=self.email_trigger( alarm_list)
            self.max_price=high_price
        else:
            pass
        
        if low_price<self.min_price:
            if self.min_price!=1000:
                alarm_content='New lowest price: %s. '%low_price
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='new_lowest'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                #alarm_list=self.email_trigger( alarm_list)
            self.min_price=low_price
            
        if current_price<self.max_price*(1+drop_down_rate/100):
            alarm_content='Descreasing more than %s%% from highest rate %s%% , sell 1/3.' % (drop_down_rate,high_change)
            alarm_content=alarm_content+current_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alarm'
            alarm_category='high_then_down'
            alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
            alarm_list=self.email_trigger( alarm_list)
        else:
            pass
        
        if current_price>=(1+expect_profile_rate)*pre_close_price:
            if self.alarm_trigger_timestamp==0:
                print('Firstly meet expectation, prepare to sell')
                self.alarm_trigger_timestamp=this_time
                alarm_content='Firstly meet expectation rate: %s%%, prepare to sell. ' % expect_profile_rate
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='meet_expect'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                alarm_list=self.email_trigger( alarm_list)
            else:
                print('Meet expectation and waiting confirmation...')
                interval=this_timestamp-self.alarm_trigger_timestamp
                if interval>60*5:
                    print('Meet expectation and confirmed, sell now')
                    self.alarm_trigger_timestamp=0
                    alarm_content='Meet expectation rate %s%% and confirmed, sell 1/3. ' % expect_profile_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='alarm'
                    alarm_category='confirm_expect'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
            exceed_high_rate=min(8.0,expect_profile_rate*1.5)            
            if current_price>(1+exceed_high_rate)*pre_close_price:
                alarm_content='Exactly exceed 1.5x expectation rate %s%% and confirmed, sell 1/2.' % exceed_high_rate 
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='alert'
                alarm_category='exceed_high'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                alarm_list=self.email_trigger( alarm_list)
            
        else:
            if current_price<(1+terminate_loss_rate)*pre_close_price:
                if self.alarm_trigger_timestamp==0:
                    print('Firstly reach loss termination, prepare to sell. ')
                    
                    self.alarm_trigger_timestamp=this_time
                    alarm_content='Firstly reach lost termination rate: %s%%, prepare to sell' % terminate_loss_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='notice'
                    alarm_category='reach_lost'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
                        
                else:
                    interval=this_timestamp-self.alarm_trigger_timestamp
                    if interval>60*3:
                        print('Reach lost termination and confirmed, sell now.')
                        self.alarm_trigger_timestamp=0
                        alarm_content='Reach lost termination rate %s%% and confirmed, sell 1/2. ' % terminate_loss_rate
                        alarm_content=alarm_content+current_content
                        if self.DEBUG_ENABLED: print(alarm_content)
                        alarm_type='alarm'
                        alarm_category='confirm_lost'
                        alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                        alarm_list=self.email_trigger( alarm_list)
                exceed_low_rate=max(-8.0,terminate_loss_rate*1.5)           
                if current_price<(1+exceed_low_rate)*pre_close_price:
                    alarm_content='Exactly exceed 1.5x loss termination rate %s%% and confirmed, sell all. ' % exceed_low_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='alert'
                    alarm_category='exceed_lost'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
            else:
                print('Wave in normal, the current price is %s , perchange is %s%%.' % (current_price,per_change))
                pass
        
        return alarm_list #alarm_trigger_timestamp
    
    def realtime_monitor(self):
        state_confirm=False
        if tradeTime.is_trade_time_now0(tradeTime.get_latest_trade_date()):
            #while is_valid_trade_time(now) :
            while True:
                realtime_df=self.get_realtime_data()
                trigger_timestamp=self.alarm_logging(realtime_df)
                time.sleep(30)
        return

class Market:
    def __init__(self,today_df):
        self.DEBUG_ENABLED=False
        self.today_df=today_df
        #self.all_codes=[]
        self.all_codes=today_df.index.values.tolist()
        
    def set_today_df(self,today_df):
        self.today_df=today_df
        
    def set_debug_mode(self,debug=True):
        self.DEBUG_ENABLED=debug
     #get topest df for history data
     
    def get_today_upper_limit(self):
        today_df=self.today_df
        #print temp_df
        #today_df.to_csv('today_df-0810.csv')
        upper_limit_df=today_df[today_df.trade==(today_df.settlement*1.1).round(2)]   #filter the topest items
        upperr_limit_rate=round(round(len(upper_limit_df),3)/len(today_df),3)
        return upper_limit_df,upperr_limit_rate
    
    def get_today_lower_limit(self):
        today_df=self.today_df
        #print temp_df
        lower_limit_df=today_df[today_df.trade==(today_df.settlement*0.9).round(2)]   #filter the topest items
        lower_limit_rate=round(round(len(lower_limit_df),3)/len(today_df),3)
        return lower_limit_df,lower_limit_rate
    
    def get_high_open(self,high_open_rate):
        high_open_df,high_open_rate = self.filter_today_df(self,operator='gte', threshhold_rate=high_open_rate, column='o_change')
        return
        
    def filter_today_df(self,operator,threshhold_rate, column):
        #print temp_df
        today_df=self.today_df
        criteria=True
        if operator=='gte':
            #criteria=temp_df.close>=temp_df.last_close*threshhold_rate/100
            if column=='changepercent':
                criteria=today_df.changepercent>=threshhold_rate
            elif column=='h_change':
                criteria=today_df.h_change>=threshhold_rate
            elif column=='l_change':
                criteria=today_df.l_change>=threshhold_rate
            elif column=='o_change':
                criteria=today_df.o_change>=threshhold_rate
            else:
                pass
                
        else:
            if operator=='lt':
                #criteria=temp_df.close<temp_df.last_close*threshhold_rate/100
                criteria=today_df.changepercent<threshhold_rate
                if column=='changepercent':
                    criteria=today_df.changepercent<threshhold_rate
                elif column=='h_change':
                    criteria=today_df.h_change<threshhold_rate
                elif column=='l_change':
                    criteria=today_df.l_change<threshhold_rate
                elif column=='o_change':
                    criteria=today_df.o_change<threshhold_rate
                else:
                    pass
            else:
                pass
        filter_df=today_df[criteria]
        filter_rate=0
        if len(today_df)!=0:
            filter_rate=round(round(len(filter_df),3)/len(today_df),3)
        return filter_df,filter_rate
    
    def get_up_then_down(self,up_rate,week_percent):
        up_rate=5.0
        week_percent=0.25
        today_df=self.today_df
        criteria2=today_df.changepercent<today_df.h_change*week_percent
        criteria1=today_df.h_change>up_rate
        criteria=criteria1 & criteria2
        #up_and_down_df=today_df[today_df.changepercent<today_df.h_change*0.5]
        up_and_down_df=today_df[criteria]
        #print up_and_down_df
        print(len(up_and_down_df))
    
    def get_h_open_then_down(self,h_open_rate):
        h_open_rate=3.0
        today_df=self.today_df
        criteria2=today_df.changepercent<-h_open_rate
        criteria1=today_df.open>today_df.settlement*(1+h_open_rate/100)
        criteria=criteria1 & criteria2
        #up_and_down_df=today_df[today_df.changepercent<today_df.h_change*0.5]
        up_and_down_df=today_df[criteria]
        #print up_and_down_df
        print(len(up_and_down_df))
    
    def get_split_num(self,split_rate):
        num_list=[]   #[close>=split_late, close<-split_late,high>=split_rate,high<split_rate]
        rate_list=[]
        filter_c_gte,c_gte_rate=self.filter_today_df(operator='gte', threshhold_rate=split_rate, column='changepercent')
        filter_c_lt,c_lt=self.filter_today_df(operator='lt', threshhold_rate=-split_rate,column='changepercent')
        filter_h_gte,h_gte_rate=self.filter_today_df(operator='gte', threshhold_rate=split_rate,column='h_change')
        filter_l_lt,l_lt_rate=self.filter_today_df(operator='lt', threshhold_rate=-split_rate,column='l_change')
        num_list=[len(filter_c_gte),len(filter_c_lt),len(filter_h_gte),len(filter_l_lt)]
        keep_strong_rate=0          #>60, higher then better, 100 will be the best
        #rate(%) of stock_num keepping strong after reached up the expeact increase_rate(6.2%)
        if num_list[2]!=0:
            keep_strong_rate=round(round(num_list[0],3)/num_list[2],3)
        #print 'rate=%s%%,keep_strong_rate=%s'%(split_rate,keep_strong_rate)
        keep_weak_rate=0         #smaller then better, 0 will be pefect
        #rate(%) of stock_num keepping weak after drop downthe expeact increase_rate(-6.2%)
        if num_list[3]!=0:
            keep_weak_rate=round(round(num_list[1],3)/num_list[3],3)
        #print 'rate=-%s%%,keep_weak_rate=%s'%(split_rate,keep_weak_rate)
        rate_list=[c_gte_rate,c_lt,h_gte_rate,l_lt_rate,keep_strong_rate,keep_weak_rate]
        return num_list,rate_list
    
    def today_static(self):
        #today_df,this_time_str=get_today_df()
        #today_df=today_df.astype(float)
        #this_time=datetime.datetime.now()
        #this_time_str=this_time.strftime('%Y-%m-%d %X')
        this_time_str=self.today_df.index.name
        print(this_time_str)
        len_today_df=len(self.today_df)
        #self.get_h_open_then_down(h_open_rate=3.0)
        upper_limit_df,upper_limit_rate=self.get_today_upper_limit()
        lower_limit_df,lower_limit_rate=self.get_today_lower_limit()
        flat_rate=0.2
        # gold split: 3.82:6.18
        middle_increase_rate=4
        middle_c_str='c_gt_%s'%middle_increase_rate
        middle_c_str_n='c_lt_n%s'%middle_increase_rate
        middle_str_h='h_gt_%s'%middle_increase_rate
        middle_str_l_n='l_lt_n%s'%middle_increase_rate
        great_increase_rate=6
        great_c_str='c_gt_%s'%great_increase_rate
        great_c_str_n='c_lt_n%s'%great_increase_rate
        great_h_str='h_gt_%s'%great_increase_rate
        great_l_str_n='l_lt_n%s'%great_increase_rate
        static_data={}
        #static_column_list=['time','h_limit','l_limit','red','green','flat','c>=5','c<=-5','h>=5','l<=-5']   
        static_column_list=['time','h_lmt','l_lmt','R','G','F',middle_c_str,middle_c_str_n,middle_str_h,middle_str_l_n,great_c_str,great_c_str_n,great_h_str,great_l_str_n] 
        #high_limit: h_lmt, low_limit:l_lmt, close_red: R,close_green: G, close_flat:F
        static_data['time']=this_time_str
        num_h_lmt=[len(upper_limit_df)]
        num_l_lmt=len(lower_limit_df)
        static_data['h_lmt']=num_h_lmt
        static_data['l_lmt']=num_l_lmt
        
        print('Now time: %s' % datetime.datetime.now())
        print('-----------------------------------------------------------------')
        #print 'num_upper_limit:num_lower_limit=%s:%s' %(len(upper_limit_df),len(lower_limit_df))
        #print 'upper_limit_rate=%s%%,lower_limit_rate=%s%%' %(upper_limit_rate,lower_limit_rate)
        #print '-----------------------------------------------------------------'
        filter_df_gt_0,positive_rate=self.filter_today_df(operator='gte', threshhold_rate=flat_rate, column='changepercent')
        filter_df_lt_0,nagative_rate=self.filter_today_df(operator='lt', threshhold_rate=-flat_rate,column='changepercent')
        #print 'num_positive:num_nagative=%s:%s' % (len(filter_df_gt_0),len(filter_df_lt_0))
        #print 'positive_rate=%s%%,nagative_rate=%s%%,flat_rate=%s%%' %(positive_rate,nagative_rate,(100-positive_rate-nagative_rate))
        num_R=len(filter_df_gt_0)
        num_G=len(filter_df_lt_0)
        num_F=len_today_df-num_G-num_R
        static_data['R']=num_R
        static_data['G']=num_G
        static_data['F']=num_F
        min_x=min(num_R,num_G,num_F)
        R_F_G=''
        if min_x!=0:
            R_F_G='%s:%s:%s'%(num_R/min_x,num_G/min_x,num_F/min_x)
        print('R:G:F=%s' % R_F_G)
        num_list1,rate_list1=self.get_split_num(middle_increase_rate)
        num_list2,rate_list2=self.get_split_num(great_increase_rate)
        """
        static_data[middle_c_str]=num_list1[0]
        static_data[middle_c_str_n]=num_list1[1]
        static_data[middle_str_h]=num_list1[2]
        static_data[middle_str_l_n]=num_list1[3]
        static_data[great_c_str]=num_list2[0]
        static_data[great_c_str_n]=num_list2[1]
        static_data[great_h_str]=num_list2[2]
        static_data[great_l_str_n]=num_list2[3]
        """
        static_data[middle_c_str]=rate_list1[0]
        static_data[middle_c_str_n]=rate_list1[1]
        static_data[middle_str_h]=rate_list1[2]
        static_data[middle_str_l_n]=rate_list1[3]
        static_data[great_c_str]=rate_list2[0]
        static_data[great_c_str_n]=rate_list2[1]
        static_data[great_h_str]=rate_list2[2]
        static_data[great_l_str_n]=rate_list2[3]
        ps_str=''
        keep_strong_rate=0
        keep_weak_rate=0
        if num_R>=len_today_df*0.5:
            keep_strong_rate=rate_list2[4]
            keep_weak_rate=rate_list2[5]
            ps_str='%s'%middle_increase_rate
        else:
            keep_strong_rate=rate_list1[4]
            keep_weak_rate=rate_list1[5]
            ps_str='%s'%great_increase_rate
        ks_str='ks_'+ps_str                 #'ks' for 'keep strong' rate
        kw_str='kw_n'+ps_str                #'kw' for 'keep weak' rate
        static_column_list=['time','h_lmt','l_lmt','R','G','F',middle_c_str,middle_c_str_n,middle_str_h,middle_str_l_n,great_c_str,great_c_str_n,great_h_str,great_l_str_n,ks_str,kw_str] 
        #high_limit: h_lmt, low_limit:l_lmt, close_red: R,close_green: G, close_flat:F, rate_keep_strong:ks_str, rate_keep_week:kw_str
        static_data[ks_str]=keep_strong_rate
        static_data[kw_str]=keep_weak_rate
        static_result_df=pd.DataFrame(static_data,columns=static_column_list)#,index='aa')
        static_result_df=static_result_df.set_index('time')
        print(static_result_df) #.columns.values.tolist()
        return static_result_df
    
    def get_allcode_list(self):
        #self.get_all_today()
        self.all_codes= self.today_df['code'].values.tolist()
        #print self.all_codes
    def get_p_cross_N(self,cross_num,analyze_type):
        potential_cross_n_list=[]
        hist_all_code=get_all_code(ROOT_DIR+'/hist')
        if self.all_codes:
            #print self.all_codes
            for code in self.all_codes:
                if code in hist_all_code:
                    stockhist=Stockhistory(code_str=code,ktype='D')
                    #stockhist.set_history_df(analyze_type)
                    if stockhist.is_new_stock():
                        pass
                    else:
                        if stockhist.is_potential_cross_N(cross_num):
                            potential_cross_n_list.append(code)
                else:
                    #new stock
                    pass
            print('potential_cross_%s_list= %s' % (cross_num,potential_cross_n_list))
        
        else:
            pass
        return potential_cross_n_list
    
    def get_cross_N(self,cross_num,analyze_type):
        potential_cross_n_list=[]
        actual_cross_n_list=[]
        success_rate=0
        hist_all_code=get_all_code(ROOT_DIR+'/hist')
        if self.all_codes:
            #print self.all_codes
            for code in self.all_codes:
                if code in hist_all_code:
                    stockhist=Stockhistory(code_str=code,ktype='D')
                    #stockhist.set_history_df(analyze_type)
                    if stockhist.is_new_stock():
                        pass
                    else:
                        if stockhist.is_cross_N(cross_num,'potential'):
                            potential_cross_n_list.append(code)
                        if stockhist.is_cross_N(cross_num,'actual'):
                            actual_cross_n_list.append(code)
                else:
                    #new stock
                    pass
            print('potential_cross_%s_list= %s' % (cross_num,potential_cross_n_list))
            print('actual_cross_%s_list= %s' % (cross_num,actual_cross_n_list))
            if len(potential_cross_n_list):
                success_rate=round(round(len(actual_cross_n_list),2)/len(potential_cross_n_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_cross_n_list,success_rate
    
    def get_star_df(self, star_rate,raw_df=None):
        df=self.today_df
        #del df['name']
        if raw_df != None:
            df=raw_df
        
        #print df
        #print df.dtypes
        df=df.astype(float)
        Crit=abs(df.trade-df.open)<star_rate*(df.high-df.low)
        star_df=df[Crit]
        """
        pre_name='star'
        #today=datetime.date.today()
        today=datetime.datetime.now()
        #if today.isoweekday()<6:
        today_str=today.strftime(ISODATEFORMAT)
        star_df.index.name=today_str
        #df.to_csv(ROOT_DIR+'/data/%s%s.csv'%(filename,today_str),encoding='GB18030')  #'utf-8')
        star_df.to_excel(ROOT_DIR+'/data/%s.xlsx'%(pre_name+today_str), sheet_name='%s'%today_str)
        print 'The the star code today are saved as ROOT_DIR+/data/%s.xlsx'%(pre_name+today_str)
        """
        return star_df
    
    def get_10(self,analyze_type,code_list=None):
        potential_10_list=[]
        actual_10_list=[]
        success_rate=0
        #hist_all_code=get_all_code('ROOT_DIR+/hist')
        all_codes=get_all_code(ROOT_DIR+'/update')
        if code_list:
            all_codes=list(set(all_codes).intersection(set(code_list)))
        if all_codes:
            for code in all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if analyze_type=='realtime':
                    pass
                    #stockhist.set_history_df('realtime')
                if stockhist.is_new_stock():
                    pass
                else:
                    if stockhist.is_10('potential'):
                        potential_10_list.append(code)
                    if stockhist.is_10('actual'):
                        actual_10_list.append(code)
            print('potentia_10_list= %s' % (potential_10_list))
            print('actual_10_list= %s' % (actual_10_list))
            if len(potential_10_list):
                success_rate=round(round(len(actual_10_list),2)/len(potential_10_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_10_list,success_rate
    
    def get_101(self,analyze_type,code_list=None):
        potential_101_list=[]
        actual_101_list=[]
        success_rate=0
        #hist_all_code=get_all_code('ROOT_DIR+/hist')
        all_codes=get_all_code(ROOT_DIR+'/update')
        if code_list !=None:
            all_codes=list(set(all_codes).intersection(set(code_list)))
        #print 'all_codes=',all_codes
        if all_codes:
            for code in all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if analyze_type=='realtime':
                    pass
                    #stockhist.set_history_df('realtime')
                if stockhist.is_new_stock():
                    pass
                else:
                    if stockhist.is_101('potential'):
                        potential_101_list.append(code)
                    if stockhist.is_101('actual'):
                        actual_101_list.append(code)
            print('potential_101_list= %s' % (potential_101_list))
            print('actual_101_list= %s' % (actual_101_list))
            if len(potential_101_list):
                success_rate=round(round(len(actual_101_list),2)/len(potential_101_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_101_list,success_rate

    def get_110(self):
        potential_110_list=[]
        actual_110_list=[]
        success_rate=0
        if self.all_codes:
            for code in self.all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if stockhist.is_new_stock() or stockhist.is_constant_1() or stockhist.is_star(rate=0.33):
                    pass
                else:
                    if stockhist.is_110('potential'):
                        potential_110_list.append(code)
                    if stockhist.is_110('actual'):
                        actual_110_list.append(code)
            print('potential_110_list= %s' % (potential_110_list))
            print('actual_110_list= %s' % (actual_110_list))
            if len(potential_110_list):
                success_rate=round(round(len(actual_110_list),2)/len(potential_110_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_110_list,success_rate
    
    def get_positive_target(self,target_list):
        target_count=len(target_list)
        postive_count=0
        total_avrg=0
        postive_avrg_incrs=0
        postive_rate=0
        for code in target_list:
            try:
                p_change=self.today_df.ix[code]['changepercent']
                p_change=float(p_change)
                total_avrg+=p_change
                if p_change>0.01:
                    postive_count+=1
                    postive_avrg_incrs+=p_change
            except:
                #print 'except'
                pass
        if postive_count!=0:
            postive_avrg_incrs=round(postive_avrg_incrs/postive_count,2)
        if target_count!=0:
            postive_rate=round(round(postive_count,2)/target_count,2)
            total_avrg=round(total_avrg/target_count,2)
        print('postive_rate_2nd_day=',postive_rate)
        print('postive_avrg_incrs=',postive_avrg_incrs)
        print('total_avrg=',total_avrg)
        return total_avrg,postive_rate
    
    def get_hist_cross_analyze(self):
        latest_trade_day=tradeTime.get_latest_trade_date()
        N=4
        for N in range(1,N):
            print('=============================')
            print('History statistics analyze for actual_cross_%s_list  on  %s' %(N,latest_trade_day))
            actual_cross_n_list,success_rate=self.get_cross_N(N,'history')
            total_avrg,postive_rate=self.get_positive_target(actual_cross_n_list)
        return
    
    def get_realtime_cross_analyze(self):
        latest_trade_day=tradeTime.get_latest_trade_date()
        N=4
        for n in range(1,N):
            print('=============================')
            print('Realtime statistics analyze for actual_cross_%s_list  on  %s' %(n,latest_trade_day))
            actual_cross_n_list,success_rate=self.get_cross_N(n,'realtime')
        return
    
    def market_analyze_today(self):
        #init_all_hist_from_export()
        latest_trade_day=tradeTime.get_latest_trade_date()
        today_df,df_time_stamp=get_today_df()
        self.set_today_df(today_df)
        out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
        output=open(out_file_name,'w')
        sys.stdout=output
        #market=Market(today_df)
        #update_all_hist(today_df,df_time_stamp)
        #actual_101_list,success_101_rate=market.get_101()
        self.get_hist_cross_analyze()
        self.get_realtime_cross_analyze()
        actual_101_list,success_101_rate=self.get_101('realtime')
        df_101=today_df[today_df.index.isin(actual_101_list)]
        #print 'df_101=',df_101
        star_rate=0.25
        star_df=self.get_star_df(star_rate)
        #print star_df
        star_list=star_df.index.values.tolist()
        code_10,rate=self.get_10('history', star_list)
        #print code_10
        t_df=today_df
        df_10=t_df[t_df.index.isin(code_10)]
        #print df_10
        filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
        df_10.to_csv(filename)
        #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
        #print 'potential_101_list=',potential_101_list
        realtime_101_list,success_101_rate=self.get_101('realtime',code_10)
        sys.stdout=sys.__stdout__
        output.close()
        print('market_analyze completed for today.')
        
    
class Monitor:
    
    def __init__(self,holding_code_list):
        self.holding_stocks=holding_code_list
        
    def set_holding_code(self,holding_code_list):
        self.holding_stocks=holding_code_list 
         
    def set_debug_mode(self,debug=True):
        self.DEBUG_ENABLED=debug
        
    def get_holding_statics(self):
        latest_trade_day=tradeTime.get_latest_trade_date()
        out_file_name=ROOT_DIR+'/result/static-' + latest_trade_day + '.txt'
        static_output=open(out_file_name,'w')
        sys.stdout=static_output
        #code_list=['600031','603988','603158','601018','002282','002556','600673','002678','000998','601088','600398']
        code_list=self.holding_stocks
        for code in code_list:
            print('---------------------------------------------------')
            stock=Stockhistory(code,'D')
            print('code:', code)
            stock.hist_analyze(10)
            stock.boduan_analyze()
            print('---------------------------------------------------')
        
        sys.stdout=sys.__stdout__
        static_output.close()
        print('Stock static completed')
        
    def realtime_monitor(self,given_interval):
        interval=60     #30 seconds
        data={}
        column_list=['code','open','pre_close','price','high','low','bid','ask','volume','amount','time']
        my_df=pd.DataFrame(data,columns=column_list)#,index=['
        latest_trade_day=tradeTime.get_latest_trade_date()
        morning_time0=datetime.datetime.strptime(latest_trade_day+' 09:30:00','%Y-%m-%d %X')
        morning_time1=datetime.datetime.strptime(latest_trade_day+' 11:30:00','%Y-%m-%d %X')
        noon_time0=datetime.datetime.strptime(latest_trade_day+' 13:00:00','%Y-%m-%d %X')
        noon_time1=datetime.datetime.strptime(latest_trade_day+' 15:00:00','%Y-%m-%d %X')
        next_morning_time0=morning_time0+datetime.timedelta(days=1)
        #while tradeTime.is_trade_time_now0(latest_trade_day):
        alarm_category_dict={}
        max_price_dict={}
        min_price_dict={}
        for code in self.holding_stocks:
            alarm_category_dict[code]='normal'
            max_price_dict[code]=-1
            min_price_dict[code]=1000
        
        while True:
            this_time=datetime.datetime.now()
            this_time_str=this_time.strftime('%Y-%m-%d %X')
            #print 'now_time=',this_time
            #this_time=datetime.datetime(2015,7,21,13,25,20,0)
            #print my_df
            if this_time>morning_time1 and this_time<noon_time0 :
                interval_time=noon_time0-this_time
                interval=interval_time.days*24*3600+interval_time.seconds
                print('Have a lest druing the noon, sleep %s seconds...'%interval)
            else:
                if this_time<=morning_time0:
                    interval_time=morning_time0-this_time
                    interval=interval_time.days*24*3600+interval_time.seconds
                    print('Market does not start yet in the morning, sleep %s seconds...'%interval)
                else:
                    if this_time>=noon_time1:
                        interval_time=next_morning_time0-this_time
                        interval=interval_time.days*24*3600+interval_time.seconds
                        market_analyze_today()
                        #market_analyze_today()
                        write_hist_index()
                        self.get_holding_statics()
                        print('Market will start in next morning, sleep %s seconds...'%interval)
                    else:
                        if (this_time>=morning_time0 and this_time<=morning_time1)  or (this_time>=noon_time0 and this_time<=noon_time1):
                            latest_trade_day=tradeTime.get_latest_trade_date()
                            my_df=pd.DataFrame(data,columns=column_list)        #empty df
                            for code in self.holding_stocks:
                                out_file_name=ROOT_DIR+'/result/realtime_' +code +'_'+latest_trade_day + '.txt'
                                realtime_output=open(out_file_name,'a')
                                sys.stdout=realtime_output
                                mystock=Stockhistory(code,ktype='D')
                                mystock.set_alarm_category(alarm_category_dict[code])
                                mystock.set_max_price(max_price_dict[code])
                                mystock.set_min_price(min_price_dict[code])
                                mystock.set_debug_mode(True)
                                realtime_df=mystock.get_realtime_data()
                                mystock.alarm_logging(realtime_df)
                                alarm_category=mystock.alarm_category
                                alarm_category_dict[code]=alarm_category
                                max_price_dict[code]=mystock.max_price
                                min_price_dict[code]=mystock.min_price
                                my_df=my_df.append(realtime_df,ignore_index=True)
                                #market_test()
                                realtime_output.close()
                            del my_df['time']
                            my_df=my_df.set_index('code')
                            my_df=my_df.astype(float)
                            my_df.insert(1, 'p_change', 100.00*((my_df.price-my_df.pre_close)/my_df.pre_close).round(4))
                            if this_time.minute%30==0:
                                stock_code='holding_stock'
                                alarm_type='notice'
                                alarm_category='realtime_report'
                                alarm_content='%s'%my_df
                                alarm_list=[stock_code,this_time_str,alarm_type,alarm_category,alarm_content]
                                send_mail(alarm_list)
                                #market_test()
                            interval=given_interval
                        else:
                            pass
            time.sleep(interval)
            
class Monitorthread(threading.Thread):
    def __init__(self,thread_num,thread_type,interval,code_str=None):
        threading.Thread.__init__(self)  
        self.thread_num = thread_num 
        self.thread_type=thread_type 
        self.interval = interval  
        self.thread_stop = False
        
    def set_interval(self,interval):
        self.interval=interval
        
    def run(self): #Overwrite run() method, put what you want the thread do here  
        while not self.thread_stop:
            if self.thread_type=='panmian':
                today_df,this_time_str=get_today_df()
                market=Market(today_df)
                #market.get_p_cross_N(3, 'realtime')
                static_result_df=market.today_static()
                pass
            else:
                if self.thread_type=='holding' and self.code_str!=None:
                    """
                    mystock=Stockhistory(self.code_str,ktype='D')
                    mystock.set_alarm_category(alarm_category_dict[code])
                    mystock.set_max_price(max_price_dict[code])
                    mystock.set_min_price(min_price_dict[code])
                    mystock.set_debug_mode(True)
                    realtime_df=mystock.get_realtime_data()
                    mystock.alarm_logging(realtime_df)
                    alarm_category=mystock.alarm_category
                    alarm_category_dict[code]=alarm_category
                    max_price_dict[code]=mystock.max_price
                    min_price_dict[code]=mystock.min_price
                    my_df=my_df.append(realtime_df,ignore_index=True)
                    """
                    pass
                else:
                    if self.thread_type=='report':
                        pass
                    else:
                        if self.thread_type=='hist_update':
                            pass
                        else:
                            print('Thread_type incorrect! Make sure your input is corret!')
                    
            print('Thread Object(%d), Time:%s\n' %(self.thread_num, time.ctime()))  
            time.sleep(self.interval)  
            
    def stop(self):  
        self.thread_stop = True  

def thread_test():  
    thread1 = Monitorthread(1, 1)  
    thread2 = Monitorthread(2, 2)  
    thread1.start()  
    thread2.start()  
    time.sleep(10)  
    thread1.stop()  
    thread2.stop()  
          
def test():
    hist_dir=ROOT_DIR+'/hist'
    hist_code=get_all_code(hist_dir)
    print('hist_code:',hist_code)
    if len(hist_code)==0:
        print('Begin pre-processing  the hist data')
        init_all_hist_from_export()
        print('pre-processing completed')
        hist_code=get_all_code(hist_dir)
    code_str=hist_code[5]
    stock=Stockhistory(code_str='000157',ktype='D')
    #print 'Stockhistory:',stock.h_df
    topest_df,topest_rate= stock.get_hist_topest(recent_days=60)
    print(topest_df)
    print('topest_rate=',topest_rate)
    filter_df,filter_rate=stock.filter_hist('gte', 2, 100)
    print(filter_df)
    print('filter_rate=',filter_rate)
    ma5=stock.get_ma('close', 5)
    print(ma5)
    ma5_high=stock.get_ma('high', 5)
    print(ma5_high)
    ma5_volume=stock.get_ma('volume', 5)
    print(ma5_volume)
    
    print(stock.is_cross_N(1,'actual'))
    
    #market=Market()    
    #print market.today_df
    #hist_df=market.update_one_hist(code_str,market.today_df)
    #print hist_df


def test1(): 
    market=Market()
    #market.write_today_df()
    #df=market.read_today_df()
    #print 'market.today_df:',market.today_df
    #actual_cross_n_list,success_rate=market.get_cross_N(1)
    """
    actual_cross_1_list= ['600317', '600724', '600971', '601101', '601518', '601139', '000570', '000620', '601699', '600403', '601018', '600736', '600821', '002574', '600573', '600272', '600997', '601929', '000525', '002118', '000597', '600448', '601088', '000595', '300138', '600360', '601369', '300047', '600456', '600721', '000504', '000685', '002514', '002541', '002637', '300131', '000967', '002005', '002017', '002386', '601666', '000723', '000851', '002528', '000014', '000933', '002395', '002430', '002653', '300314', '600195', '600202', '600400', '600518', '603167', '600157', '600666', '000722', '000983', '600529', '600774', '002678', '300120', '300336', '600093', '600239', '600463', '600687', '000973', '000988', '600712', '002161', '002190', '600100', '002143', '600241', '600280', '601677', '603002', '002504', '300339', '600422', '000768', '002458', '002507', '300218', '601222', '000605', '002152', '002413', '002468', '603166', '002396', '002665', '600017', '600267', '600475', '600590', '600684', '600822', '600823', '601058', '601313', '601999', '000503', '000703', '000777', '000780', '000955', '002054', '002266', '002287', '002332', '002339', '002409', '002446', '002482', '002513', '002563', '002585', '002684', '300024', '300067', '300115', '300128', '300222', '300324', '300325', '300331', '002317', '300182', '300195', '000020', '000910', '002352', '600079', '600270', '000090', '002579', '600460', '601001', '000509', '000753', '002375', '600096', '300063', '000532', '002472', '600814', '000032', '300061', '300103', '600480', '000899', '002149', '002641', '600011', '002049', '002193', '002433', '600508', '600004', '000523', '600123', '600778', '600800', '002128', '600095', '601328', '600853', '600395', '300031', '600368', '300265', '600348', '600546', '000937', '000909', '601898', '601991', '601333', '002134', '600603', '002489', '600488', '000809', '600835', '002205', '002708', '002448', '000698', '300299', '002543', '600579', '300100', '000417', '002099', '300169', '002297', '600577', '000514', '600555', '002041', '002687', '002401', '600121', '600523', '600179', '000408', '300238', '600571', '000529', '600650', '002309', '600613', '600653', '601117', '002492', '000903', '600189', '600780', '600027', '002275', '000636', '000889', '000838', '000037', '000739', '000752', '300003', '002715', '300116', '002419', '600331', '000543', '600418', '002510', '000760', '300326', '002420', '002286', '601177', '600761', '300046', '002270', '300284', '002305', '002035', '000822', '002447', '600883', '002394', '600088', '300219', '600399', '600792', '300092', '601126', '000919', '600485', '002265', '300057', '000790', '600328', '000606', '002554', '600623', '600160', '300274', '300037', '002524', '600112', '002692', '002336', '002634', '600353', '300127', '002483', '002592', '002132', '002247', '000419', '600874', '002077', '000806', '300054', '002072', '601208', '600501', '000972', '002658', '300062', '300329', '601113', '600775', '600740', '002150', '600854', '002130', '600308', '300393', '000019', '300132', '600421', '601965', '002480', '002062', '300154', '002474', '600236', '000936', '002398', '002729', '000830', '000908', '600131', '300286', '600051', '000673', '300034', '000663', '000683', '600355', '002481', '600958', '600651', '600982', '002068', '000539', '600075', '002562', '000533', '000670', '601636', '000572', '601225', '600776', '000802', '603123', '300239', '000886', '000430', '600863', '600965', '002404', '002186', '002313', '600183', '000421', '002392', '002088', '002454', '600500', '000678', '600726', '002223', '300292', '300084', '600439', '000667', '300117', '300306', '601588', '002171', '002532', '002083', '600641', '300106', '601008', '600557', '600791', '600321', '300147', '601188', '300221', '300370', '600843', '000153', '600973', '000060', '600056', '002399', '002422', '600350', '600839', '000721', '002557', '002538', '002621', '002369', '002277', '000985', '000639', '600345', '600054', '300157', '002145', '000707', '002527', '600693', '600988', '000725', '002300', '002393', '600861', '002267', '600084', '000004', '002222', '600316', '601727', '300091', '002591', '600551', '000737', '300307', '000720', '002304', '002436', '603128', '000962', '600979', '600816', '600985', '002603', '600162', '600192', '002243', '600449', '000762', '002218', '600636', '000738', '002452', '600295', '600593', '002666', '601798', '000702', '600517', '600231', '600851', '300039', '600784', '002328', '600115', '300215', '002526', '300320', '002382', '601616', '000423', '300129', '601678', '600578', '601216', '002423', '002377', '002225', '000682', '601003', '000672', '000999', '002101', '002025', '000949', '300108', '600077', '000929', '002220', '300256', '000705', '002566', '002058', '002714', '002181', '600356', '600766', '600795', '600746', '002168', '300253', '600261', '600227', '603766', '601168', '600663', '002123', '002046', '002357', '002654', '000413', '000960', '000713', '600569', '002598', '600969', '000761', '601107', '600396', '601339', '002209', '300347', '002111', '600377', '002228', '002675', '000559', '600743', '002521', '600362', '000978', '300009', '601558', '600483', '600187', '300080', '300360', '000561', '002459', '000036', '002618', '603126', '000900', '600980', '002570', '000422', '600565', '000592', '000631', '002428', '600219', '601198', '600619', '300338', '002214', '000030', '600540', '002559', '002231', '002465', '000785', '300086', '600601', '300330', '002184', '600237', '600723', '600796', '600537', '300305', '600664', '603898', '600976', '600007', '601231', '002221', '600218', '002402', '600372', '000756', '600176', '600833', '002324', '002672', '601098', '300247', '300248', '000531', '300099', '300202', '300228', '002338', '000070', '002531', '002499', '600230', '600751', '002202', '600515', '600052', '600509', '600273', '601099', '000966', '600686', '002198', '000795', '600141', '600022', '000404', '002320', '600312', '002457', '600389', '000521', '300045', '600995', '300269', '000778', '600674', '002544', '000519', '600311', '600838', '600238', '002071', '002467', '000301', '002351', '600282', '000882', '600661', '002142', '600600', '600668', '002262', '300355', '002201', '600129', '000923', '000918', '603268', '600966', '600033', '600787', '300275', '000632', '002706', '300181', '600315', '600512', '300273', '002342', '002605', '002208', '300258', '002469', '000511', '600481', '002613', '002303', '002475', '002503', '601258', '600300', '002007', '002311', '000930', '600243', '000729', '000544', '600062', '600352', '300263', '601789', '600393', '600805', '600252', '000858', '600809', '600322', '002695', '002105', '300321', '300021', '002042', '002215', '600386', '600900', '600671', '603555', '600658', '002608', '000096', '000912', '000748', '002600', '002306', '000501', '600660', '600235', '600638', '600120', '600634', '600892', '300310', '600690', '000759', '002172', '002048', '002238', '600279', '002003', '300014', '600074', '002725', '600213', '300102', '600692', '300378', '600735', '002252', '001896', '600381', '002705', '300225', '600392', '600917', '002614', '002495', '300346', '002445', '000848', '300075', '600781', '600438', '002076', '600367', '000839', '002685', '603000', '000488', '000026', '600309', '300277', '600738', '600208', '601069', '300350', '600419', '600090', '002335', '002321', '000585', '000617', '600888', '600067', '000166', '002075', '600616', '600782', '300095', '002279', '000977', '000619', '002014', '002053', '600066', '600284', '002633', '600423', '600860', '600276', '002242', '600118', '002372', '000935', '300174', '000965', '002040', '002479', '300235', '002693', '600228', '300072', '002291', '300344', '601989', '000505', '002713', '002690', '600038', '600742', '300390', '002240', '600130', '002060', '600458', '600498', '600223', '000975', '300245', '600889', '002141', '000589', '600171', '300052', '300365', '600117', '600707', '000953', '300216', '600385', '002484', '600987', '000799', '300313', '002258', '002157', '002651', '600262', '002373', '002411', '603328', '002726', '600299', '000963', '002065', '002518', '600785', '002722', '300094', '600566', '600103', '600598', '603100', '002061', '600567', '601555', '002639', '601599', '300170', '601028', '000810', '000681', '600824', '002371', '600594', '600532', '000826', '002550', '603456', '300406', '600184', '002289', '002322', '002556', '002424', '000666', '002741', '300234', '002023', '002085', '603169', '300375', '300415', '000541', '300211', '600868', '603099', '300408', '002730', '300401', '603077', '300140', '000928', '000028', '002515', '002327', '600548', '000590', '300400', '603636', '002119', '600820', '002747', '002734']
    
    actual_cross_2_list= ['600317', '600724', '000751', '600971', '601139', '000570', '000620', '601699', '600538', '600225', '600573', '600272', '600358', '002540', '600997', '000525', '002118', '600188', '000597', '600448', '000750', '601088', '300138', '002580', '601369', '000797', '600456', '000685', '002514', '000967', '002017', '002386', '000851', '002528', '000014', '000933', '002395', '300314', '600518', '603167', '600157', '000983', '600774', '000988', '600712', '600490', '000812', '002103', '002143', '600241', '601677', '300175', '300339', '300218', '601222', '000582', '000605', '002055', '002152', '002169', '002657', '002197', '002665', '300004', '300187', '600475', '600823', '601058', '601999', '000637', '000777', '000780', '000955', '000971', '002266', '002339', '002446', '002482', '002563', '002585', '002684', '300067', '300222', '300324', '300325', '300331', '300348', '300254', '000020', '000524', '600270', '002579', '300290', '600058', '600397', '002094', '000509', '000753', '002187', '002375', '300063', '000045', '002472', '600814', '600480', '002149', '002641', '600011', '600531', '002193', '002433', '600508', '601886', '600095', '601328', '600395', '600368', '600348', '600546', '000937', '601898', '601991', '002134', '600543', '600488', '000809', '600835', '002358', '000698', '300299', '300100', '600580', '000055', '300169', '600750', '000514', '002041', '600523', '601199', '300238', '600571', '000529', '002309', '600613', '601117', '000555', '000968', '002462', '002492', '002410', '002567', '000903', '600027', '000636', '000838', '000739', '300003', '600418', '002510', '000609', '002286', '601177', '002270', '300284', '002305', '000822', '002011', '300219', '300092', '601126', '000046', '300057', '300212', '000790', '600328', '002131', '300118', '600623', '300274', '300037', '600110', '002592', '002132', '000419', '600874', '002072', '600501', '300349', '300062', '300329', '601113', '002150', '600854', '002002', '002364', '600421', '002195', '002146', '002062', '002474', '600236', '300050', '600125', '002398', '000908', '600131', '600455', '600829', '000683', '600355', '600107', '600958', '002068', '002584', '000533', '000572', '601225', '600776', '600005', '600965', '300207', '002404', '002186', '300150', '002313', '002088', '002223', '300292', '600875', '000667', '300117', '600679', '002028', '002083', '600641', '300106', '600557', '600865', '300147', '601188', '002403', '300221', '600139', '300370', '600973', '002399', '002084', '002344', '601918', '600839', '002557', '600059', '600741', '002621', '002078', '002277', '002478', '000985', '002026', '000639', '600260', '600345', '002145', '002350', '002527', '600988', '002300', '002267', '600084', '000004', '002222', '600316', '601727', '000662', '600551', '002144', '000720', '002304', '600884', '002436', '603128', '603008', '600162', '600192', '600449', '000762', '002218', '000039', '600636', '600978', '600295', '002666', '601798', '000702', '600517', '000852', '600851', '600784', '002328', '300215', '601678', '002560', '600578', '000551', '002225', '601003', '000672', '000999', '002572', '300108', '000929', '002220', '300256', '600737', '002331', '002714', '600081', '002181', '002629', '600356', '600766', '600795', '300029', '300253', '600612', '600261', '601168', '600506', '002635', '002123', '002194', '000713', '300283', '600969', '600251', '600018', '600396', '601339', '300347', '600377', '000970', '002675', '600743', '600320', '000978', '600483', '300080', '000036', '002618', '000900', '600527', '000422', '600565', '002341', '000631', '600219', '600540', '601007', '300086', '600237', '600723', '600537', '600592', '603898', '002490', '600007', '601231', '600218', '000860', '000798', '000756', '600833', '002324', '000528', '601098', '300248', '300139', '000531', '300099', '300202', '600459', '600830', '000070', '601818', '600751', '002202', '600509', '601099', '000966', '600686', '600773', '002198', '002534', '600141', '600022', '002457', '600995', '300269', '000425', '000778', '600020', '600674', '601137', '000519', '600311', '600238', '002071', '300315', '000301', '002079', '000957', '002142', '002262', '002576', '600129', '000918', '600420', '600966', '002509', '600033', '600787', '300275', '000727', '300181', '600127', '600315', '600512', '300163', '300273', '002605', '002469', '002303', '002007', '000548', '600769', '600243', '000729', '000544', '600062', '600000', '300263', '601789', '600252', '000858', '600809', '600322', '300199', '002215', '300073', '600671', '600658', '002608', '000912', '601801', '002508', '600660', '600235', '600859', '600892', '600068', '000759', '002172', '002136', '000418', '002051', '002568', '600279', '600074', '600323', '002252', '001896', '600477', '002705', '002495', '002445', '002599', '600781', '600438', '000596', '002076', '002619', '000338', '603000', '300081', '000488', '600208', '000828', '002335', '000568', '600067', '300146', '600616', '300107', '000400', '300095', '002279', '300303', '600285', '600066', '600992', '002138', '002242', '600731', '600615', '600036', '002040', '300072', '002595', '600742', '002140', '600498', '601166', '600171', '002340', '300365', '600707', '000920', '600385', '000887', '300313', '002373', '002726', '601555', '000681', '600594', '300070', '002289', '000666', '300134']
    print 'Postive Statistics for  actual_cross_1_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_1_list)
    
    print 'Postive Statistics for  actual_cross_2_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_2_list)
    
    actual_cross_3_list= ['000751', '600225', '600188', '000750', '601088', '600490', '000582', '002657', '000637', '600058', '000045', '600011', '600395', '601898', '601991', '002358', '000055', '601199', '601117', '000555', '000968', '600027', '002011', '000046', '300274', '300349', '002146', '600125', '600829', '600446', '600717', '600005', '600741', '002478', '002572', '600795', '300253', '600018', '000970', '300059', '000860', '601818', '600369', '000623', '600020', '600000', '600015', '000912', '601939', '002051', '000869', '000596', '000338', '601169', '000916', '601998', '600992', '600036', '601166', '601288', '601555']
    print 'Postive Statistics for  actual_cross_3_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_3_list)
    """
    #market.get_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('history')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    print('df_101:',df_101)
    """
    actual_cross_n_list,success_rate=market.get_cross_N(1, 'history')
    intersect_list=list(set(actual_cross_n_list).intersection(set(actual_101_list)))
    print 'intersect_list=',intersect_list
    market.get_positive_target(intersect_list)
    """
    #actual_110_list,success_110_rate=market.get_110()
def update_test():
    file_name=ROOT_DIR+'/data/all2015-07-17.csv'
    file_time_str=get_file_timestamp(file_name)
    print(file_time_str)
    today_df,today_df_update_time=get_today_df()
    update_all_hist(today_df,today_df_update_time)
    
def test2():
    #init_all_hist_from_export()
    latest_trade_day=tradeTime.get_latest_trade_date()
    today_df,df_time_stamp=get_today_df()
    out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    market=Market(today_df)
    update_all_hist(today_df,df_time_stamp)
    #actual_101_list,success_101_rate=market.get_101()
    market.get_hist_cross_analyze()
    market.get_realtime_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('realtime')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    #print 'df_101=',df_101
    
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    #print star_df
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('history', star_list)
    #print code_10
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    #print df_10
    filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
    df_10.to_csv(filename)
    #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    #print 'potential_101_list=',potential_101_list
    realtime_101_list,success_101_rate=market.get_101('realtime',code_10)
    sys.stdout=sys.__stdout__
    output.close()
    print('test2 completed')
    
def test3():
    potential_101_list= ['000043', '000404', '000407', '000525', '000585', '000693', '000751', '000757', '000759', '000838', '000923', '002032', '002054', '002056', '002084', '002089', '002105', '002150', '002287', '002432', '002460', '002478', '002606', '002654', '002692', '002749', '300003', '300030', '300063', '300103', '300116', '300152', '300183', '300187', '300199', '300207', '300218', '300411', '600097', '600101', '600128', '600187', '600279', '600368', '600476', '600508', '600612', '600794', '600830', '600960', '600969', '600983', '601001', '601107', '601179', '601801', '601808', '601818', '601958', '603003', '603399']
    actual_101_list= ['000043', '000404', '000525', '000585', '000693', '000751', '000759', '000838', '002056', '002084', '002089', '002287', '002432', '002460', '002478', '002606', '002692', '300103', '300199', '300207', '300411', '600097', '600101', '600128', '600187', '600368', '600476', '600508', '600612', '600794', '600830', '600969', '600983', '601001', '601179', '601808', '601818', '601958', '603003', '603399']
    diffence_list=list(set(potential_101_list).difference(set(actual_101_list)))
    print(diffence_list)
    
    union_list=list(set(potential_101_list).union(actual_101_list))
    
    actual_cross_1_list=['600307', '600586', '002128', '002232', '000662', '600248', '600508', '000933', '000065', '600792', '300028', '600584', '300244', '600546', '600612', '600983', '002003', '002089', '002460', '002709', '300207', '300411', '000983', '000693', '000043', '600097', '600123', '600432', '000759', '000899', '601777', '600348', '000761', '600429', '002466', '600187', '000878', '600121', '300007', '601898', '000514', '600857', '603399', '601666', '000582', '002033', '600818', '603611', '601958', '600509', '600638', '600768', '000552', '601699', '601016', '600172', '600196', '603333', '600202', '002749', '300041', '600809', '600022', '600748', '002418', '002320', '600106', '600740', '300157', '000571', '300378', '601288', '002646', '002298', '002279', '000546', '300069', '002112', '601126']
    potential_cross_1_list=['600307', '600586', '002128', '002232', '000662', '600248', '600508', '000933', '000065', '600792', '300028', '600584', '300244', '600546', '600612', '600983', '002003', '002089', '002460', '002709', '300207', '300411', '000983', '000693', '000043', '600097', '600123', '600432', '000759', '000899', '601777', '600348', '000761', '600429', '002466', '600187', '000878', '600121', '300007', '601898', '000514', '600857', '603399', '601666', '000582', '002033', '600818', '603611', '601958', '600509', '600638', '600768', '000552', '601699', '601016', '600172', '600196', '603333', '600202', '002749', '300041', '600809', '600022', '600748', '002418', '002320', '600106', '600740', '300157', '000571', '300378', '601288', '000005', '002646', '002298', '600072', '002279', '000546', '300069', '300053', '002366', '002112', '600112', '600249', '300032', '000913', '002322', '002659', '300016', '601126', '300166', '300337', '300052', '603123', '002513', '300375', '300217', '600706', '002343', '300328', '300340', '002751', '002611', '300261', '300144', '002361', '300051', '300165']
    
    intersect_list=list(set(actual_cross_1_list).intersection(set(actual_101_list)))
    print('intersect_list=',intersect_list)
    print(len(intersect_list))
    
    potential_intersect_list=list(set(potential_cross_1_list).intersection(set(potential_101_list)))
    print('potential_intersect_list=',potential_intersect_list)
    print(len(potential_intersect_list))

def test4():
    print(tradeTime.get_latest_trade_date())
    market=Market()
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    print(star_df)
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('realtime', star_list)
    print(code_10)
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    print(df_10)
    df_10.to_csv(ROOT_DIR+'/data/is10-2015-06-04.csv')
    potential_101_list=code_10
    potential_101_list= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    print('potential_101_list=',potential_101_list)
    realtime_101_list,success_101_rate=market.get_101('realtime',potential_101_list)


#test()    
#test1()
#test2()
#update_test()
#get_top_list()



def stock_test():
    latest_trade_day=tradeTime.get_latest_trade_date()
    #out_file_name=ROOT_DIR+'/result/static-' + latest_trade_day + '.txt'
    out_file_name='static-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    code_list=['600031','603988','603158','601018','002282','002556','600673','002678','000998','601088','600398']
    for code in code_list:
        print('---------------------------------------------------')
        stock=Stockhistory(code,'D')
        print('code:', code)
        stock.hist_analyze(10)
        stock.boduan_analyze()
        print('---------------------------------------------------')
    
    sys.stdout=sys.__stdout__
    output.close()
    print('Stock static completed')
    
def stock_test1():
        code='002678'
        #code='000987'
        #code='601018'
        #code='002466'
        stock=Stockhistory(code,'D')
        #print stock.h_df
        temp_df=stock._form_temp_df()
        #df=df.set_index('date')
        #df=filter_df_by_date(raw_df=df, from_date_str='2015-05-08', to_date_str='2015-06-18')
        #df=filter_df_by_date(raw_df=df, from_date_str='2015-06-19', to_date_str='2015-07-08')
        df=filter_df_by_date(raw_df=temp_df, from_date_str='2015-07-09', to_date_str='2015-08-18')
        #print df
        print(len(df))
        h_change_mean=df['h_change'].mean()
        print(h_change_mean)
        l_change_mean=df['l_change'].mean()
        print(l_change_mean)
        df=df[df.h_change>0.5*h_change_mean]
        #df=df[df.l_change<-6.2]
        print(len(df))
        #stock.data_feed_by_date(from_date_str='2015-05-08', to_date_str='2015-06-18')
        #stock.data_feed_by_date(from_date_str='2015-06-19', to_date_str='2015-07-08')
        #stock.data_feed_by_date(from_date_str='2015-07-09', to_date_str='2015-08-18')
        #print stock.h_df
        star_df=stock.get_star_df(rate=0.25,raw_df=temp_df)
        stock.get_next_df(temp_df, filter_df=star_df, next_num=1)
        topest_df=temp_df[temp_df.close==(temp_df.last_close*1.1).round(2)]
        stock.get_next_df(raw_df=temp_df, filter_df=topest_df, next_num=1)
        
        """
        print stock.get_average_high(60)
        print stock.get_average_low(60)
        print stock.get_average_rate(60,'l_change')*1.5
        realtime_df=stock.get_realtime_data()
        realtime_mean_price=stock.get_realtime_mean_price(realtime_df)
        #stock.get_weak_lt_interval(realtime_df,realtime_mean_price)
        permit_interval=60*5
        stock.get_weak_sell_price(realtime_df, realtime_mean_price,permit_interval)
        #stock.boduan_analyze()
        """
        """
        df=stock._form_temp_df()
        #print df
        close_list=df['ma5'].values.tolist()
        boduan_list=find_boduan(close_list)
        print 'boduan_list=',boduan_list
        
        close_list=df['close'].values.tolist()
        print close_list,len(close_list)
        ma5_list=get_ma_list(close_list, 5)
        ma10_list=get_ma_list(close_list, 10)
        ma20_list=get_ma_list(close_list, 20)
        ss=pd.Series(ma5_list,index=df.index)
        df.insert(8,'ma5',ss)
        print df
        """
def stock_realtime_monitor():
    """
    code='601018'
    stock=Stockhistory(code,'D')
    stock.realtime_monitor()
    """
    #init_all_hist_from_export()
    code_list=['002678','000987','002269','601018','603158','002556']#'002755','603988','600276','601857']
    my_monitor=Monitor(code_list)
    my_monitor.realtime_monitor(60)
    

"""
write_hist_index()
index_df=get_hist_index('sh')
print index_df
"""
def market_test():
    #print 'start-----------'
    today_df,this_time_str=get_today_df()
    """
    today_df=today_df.astype(float)
    today_df.insert(6, 'h_change', ((today_df.changepercent*today_df.high)/today_df.trade).round(2))
    today_df.insert(7, 'l_change', ((today_df.changepercent*today_df.low)/today_df.trade).round(2))
    """
    #print today_df
    market=Market(today_df)
    #market.get_p_cross_N(3, 'realtime')
    static_result_df=market.today_static()

def score_market():
    today_df,this_time_str=get_today_df()
    gt5_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    ma_type='ma5'
    ma_offset=0.01
    great_score=4
    great_change=5.0
    all_codes=gt5_df.index.values.tolist()
    data={}
    stronge_ma_3_list=[]
    result_column=['code','l_s_date','l_s_state','t_s_date','t_s_state','t_date','t_state','score','oper3']
    result_df=pd.DataFrame(data,columns=result_column)
    if all_codes:
        for code_str in all_codes:
            stock=Stockhistory(code_str,'D')
            code_data=stock.get_trade_df(ma_type,ma_offset,great_score,great_change)
            #print 'code_data=',code_data
            if code_data:
                code_df=pd.DataFrame(code_data,index=['code'],columns=result_column)
                result_df=result_df.append(code_df,ignore_index=True)
                if code_data['oper3'] ==3:
                    stronge_ma_3_list.append(code_str)
    
    result_df.to_csv(ROOT_DIR+'/result/score_%s.csv' % this_time_str[:10])
    if stronge_ma_3_list:
        print('stronge_ma5_list=',stronge_ma_3_list)
        stronge_ma5_df=today_df[today_df.index.isin(stronge_ma_3_list)]
        print(stronge_ma5_df)
    print('result_df:')
    result_df=result_df.sort_index(axis=0, by='oper3', ascending=False)
    print(result_df)
    
    result_df_score_gt0=result_df[result_df['score']>=0]
    print(result_df_score_gt0)
    result_df_oper3_gt1=result_df[result_df['oper3']>=1]
    print(result_df_oper3_gt1)
    
def atr_market():
    today_df,this_time_str=get_today_df()
    #file_name=ROOT_DIR+'/data/all2015-10-26.csv'
    #today_df=read_today_df(file_name)
    #print today_df
    gt2_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    short_num=20
    long_num=55
    all_codes=gt2_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=tradeTime.get_latest_trade_date()
    print('latest_day_str=',latest_day_str)
    if all_codes and latest_day_str:
        for code_str in all_codes:
            stock=Stockhistory(code_str,'D')
            #print 'code_str=',code_str
            temp_df,latest_break_20,latest_break_55,top5_average=stock.get_atr_df(short_num, long_num)
            if latest_day_str==latest_break_20:
                latest_break_20_list.append(code_str)
            
            if latest_day_str==latest_break_55:
                latest_break_55_list.append(code_str)
            
            top5_average_sum+=top5_average
        top5_average_all_market=round(top5_average_sum/len(all_codes))
    print('latest_break_20_list=',latest_break_20_list)
    print('latest_break_55_list=',latest_break_55_list)
    print('top5_average_all_market=',top5_average_all_market)
    latest_break_20_df=today_df[today_df.index.isin(latest_break_20_list)]
    latest_break_20_df.index.name='code'
    column_list=latest_break_20_df.columns.values.tolist()
    #print 'column_list=',column_list
    latest_break_55_df=today_df[today_df.index.isin(latest_break_55_list)]
    latest_break_55_df.index.name='code'
    latest_break_20_df.to_csv(ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % latest_day_str)
    latest_break_55_df.to_csv(ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % latest_day_str)
    #print 'latest_break_20_df:'
    #print latest_break_20_df
    #print 'latest_break_55_df:'
    #print latest_break_55_df
    return latest_break_20_list,latest_break_55_list,top5_average_all_market

def change_static_market():
    code='002678'
    #code='000987'
    #code='601018'
    code='002466'
    #code='600650'
    #code='300244'
    #code='000001'
    #code='300033'
    #code='000821'
    short_num=20
    long_num=55
    dif_num=9
    current_price=12.10
    
    init_rate=-2.5
    rate_interval=0.5
    range_num=18
    rate_list=specify_rate_range(init_rate, rate_interval, range_num)
    df_data={}
    column_list=['code']
    #gt_data['code']=code
    for rate in rate_list:
        column_name='gt_%s' % rate
        column_list.append(column_name)
    empty_df=pd.DataFrame(df_data,columns=column_list)#,index=[''])
    #print 'static_df=',static_df
    static_df_h=static_df_l=static_df_p=empty_df
    today_df,this_time_str=get_today_df()
    #file_name=ROOT_DIR+'/data/all2015-10-26.csv'
    #today_df=read_today_df(file_name)
    #print today_df
    gt2_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    short_num=20
    long_num=55
    all_codes=today_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=tradeTime.get_latest_trade_date()
    #print 'latest_day_str=',latest_day_str
    for code in all_codes:
        stock=Stockhistory(code,'D')
        gt_static_df_h=stock.change_static(rate_list,column='h_change')
        gt_static_df_p=stock.change_static(rate_list,column='p_change')
        gt_static_df_l=stock.change_static(rate_list,column='l_change')
        if gt_static_df_h.empty:
            pass
        else:
            static_df_h=static_df_h.append(gt_static_df_h, ignore_index=True)
        if gt_static_df_p.empty:
            pass
        else:
            static_df_p=static_df_p.append(gt_static_df_p, ignore_index=True)
        if gt_static_df_l.empty:
            pass
        else:
            static_df_l=static_df_l.append(gt_static_df_l, ignore_index=True)
            #print 'static_df=',static_df
    """
        for rate_t_h in rate_list:
            max_profit_loss_ratio=0.0
            max_rate_t_l=0.0
            max_rate_t_h=0.0
            for rate_t_l in rate_list:
                if rate_t_h>rate_t_l and rate_t_h>=0.5 and rate_t_l<=0.5:
                    column_name_h='gt_%s' % rate_t_h
                    column_name_l='gt_%s' % rate_t_l
                    h_rate=gt_static_df_h[column_name_h].mean()
                    l_rate=gt_static_df_l[column_name_l].mean()
                    profit_loss_ratio=round(h_rate/(1-l_rate),2)
                    if profit_loss_ratio>=max_profit_loss_ratio:
                        max_profit_loss_ratio=profit_loss_ratio
                        max_rate_t_l=rate_t_l
                        max_rate_t_h=rate_t_h
                    #print 'hight_terminate_rate=',rate_t_h
                    #print 'low_terminate_rate=',rate_t_l
                    #print 'then profit_loss_ratio=',profit_loss_ratio
                else:
                    pass
            if max_profit_loss_ratio>0:
                print 'max_rate_t_h=',max_rate_t_h
                print 'max_rate_t_l=',max_rate_t_l
                print 'max_profit_loss_ratio=',max_profit_loss_ratio
    """
    static_df_h.to_csv(ROOT_DIR+'/result_temp/h_change_static_%s.csv' % latest_day_str)
    static_df_p.to_csv(ROOT_DIR+'/result_temp/p_change_static_%s.csv' % latest_day_str)
    static_df_l.to_csv(ROOT_DIR+'/result_temp/l_change_static_%s.csv' % latest_day_str)
    
    close_change_df=static_df_p.describe()
    high_change_df=static_df_h.describe()
    low_change_df=static_df_l.describe()
    close_change_df.to_csv(ROOT_DIR+'/result_temp/p_change_static_describe_%s.csv' % latest_day_str)
    high_change_df.to_csv(ROOT_DIR+'/result_temp/h_change_static_describe_%s.csv' % latest_day_str)
    low_change_df.to_csv(ROOT_DIR+'/result_temp/l_change_static_describe_%s.csv' % latest_day_str)
    
    return  static_df_p,static_df_h,static_df_l


def mini_atr_market():
    code='002678'
    #code='000987'
    #code='601018'
    code='002466'
    #code='600650'
    #code='300244'
    #code='000001'
    #code='300033'
    #code='000821'
    short_num=20
    long_num=55
    dif_num=9
    current_price=12.10
    
    init_rate=-2.5
    rate_interval=0.5
    range_num=18
    rate_list=specify_rate_range(init_rate, rate_interval, range_num)
    df_data={}
    column_list=['code']
    #gt_data['code']=code
    for rate in rate_list:
        column_name='gt_%s' % rate
        column_list.append(column_name)
    empty_df=pd.DataFrame(df_data,columns=column_list)#,index=[''])
    #print 'static_df=',static_df
    static_df_h=static_df_l=static_df_p=empty_df
    today_df,this_time_str=get_today_df()
    short_num=20
    long_num=55
    all_codes=today_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=tradeTime.get_latest_trade_date()
    #print 'latest_day_str=',latest_day_str
    atr_in_codes=[]
    atr_in_codes_last=[]
    df_data={}
    column_list= ['code','atr_in_rate']
    atr_min_df=pd.DataFrame(df_data,columns=column_list)
    #print('all_codes=',all_codes)
    for code in all_codes:
        stock=Stockhistory(code,'D')
        atr_in_rate,last_date,atr_in_rate_last,last2_date=stock._form_temp_df1()
        #print(atr_in_rate,last_date,atr_in_rate_last,last2_date)
        if atr_in_rate:
            df_data={}
            df_data['code']=[str(code)]
            df_data['atr_in_rate']=[atr_in_rate]
            #code_df=pd.DataFrame(code_data,index=['code'],columns=result_column)
            #result_df=result_df.append(code_df,ignore_index=True)
            atr_df=pd.DataFrame(df_data,columns=column_list)
            atr_min_df=atr_min_df.append(atr_df,ignore_index=True)
            atr_in_codes.append([code,atr_in_rate])
        if atr_in_rate_last:
            atr_in_codes_last.append([code,atr_in_rate_last])
    atr_min_df=atr_min_df.sort_index(axis=0, by='atr_in_rate', ascending=False)
    atr_min_df.to_csv(ROOT_DIR+'/result_temp1/mini_atr_market_%s.csv' % latest_day_str)
    stocksql_obj=pds.StockSQL()
    stocksql_obj.insert_table(data_frame=atr_min_df,table_name='mini_atr')
    print(atr_min_df)
    print('atr_in_codes=',atr_in_codes)
    print('atr_in_codes_last=',atr_in_codes_last)
    return  atr_in_codes

def back_test_atr():
    last_day_str=tradeTime.get_last_trade_date()
    today_df,this_time_str=get_today_df()
    #print 'today_df=',today_df
    today_column_list= ['code','changepercent', 'trade', 'open', 'high', 'low', 'settlement', 'h_change', 'l_change', 'volume', 'turnoverratio']
    today_df_code_list=today_df.index.values.tolist()
    last_20_file_name=ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % last_day_str
    last_break_20_df=pd.read_csv(last_20_file_name,index_col=0,names=today_column_list)
    last_55_file_name=ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % last_day_str
    last_break_55_df=pd.read_csv(last_55_file_name,index_col=0,names=today_column_list)
    #print 'last_break_20_df=',last_break_20_df
    last_break_20_code_list=last_break_20_df.index.values.tolist()
    #print 'last_break_20_code_list=',last_break_20_code_list
    last_break_20_code_list=list(set(last_break_20_code_list).intersection(set(today_df_code_list)))
    last_break_55_code_list=last_break_55_df.index.values.tolist()
    last_break_55_code_list=list(set(last_break_55_code_list).intersection(set(today_df_code_list)))
    latest_break_20_df=today_df[today_df.index.isin(last_break_20_code_list)]
    #print 'latest_break_20_df=',latest_break_20_df
    latest_break_20_df_mean=latest_break_20_df['changepercent'].mean()
    latest_break_20_df_high_mean=latest_break_20_df['h_change'].mean()
    latest_break_55_df=today_df[today_df.index.isin(last_break_55_code_list)]
    #print 'latest_break_55_df=',latest_break_55_df
    latest_break_55_df_mean=latest_break_55_df['changepercent'].mean()
    latest_break_55_df_high_mean=latest_break_55_df['h_change'].mean()
    
    print('latest_break_20_df_mean=',latest_break_20_df_mean)
    print('latest_break_20_df_high_mean=',latest_break_20_df_high_mean)
    print('latest_break_55_df_mean',latest_break_55_df_mean)
    print('latest_break_55_df_high_mean',latest_break_55_df_high_mean)
    
    latest_day_str=tradeTime.get_latest_trade_date()
    latest_20_file_name=ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % latest_day_str
    latest_break_20_df=pd.read_csv(latest_20_file_name)
    #print latest_break_20_df
    #print latest_break_20_df.index.name=[code]
    latest_break_20_df=latest_break_20_df.set_index('code')
    
    latest_55_file_name=ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % latest_day_str
    latest_break_55_df=pd.read_csv(latest_55_file_name)
    latest_break_55_df=latest_break_55_df.set_index('code')
    latest_break_20_code_list=latest_break_20_df.index.values.tolist()
    
    latest_break_20_code_list= json.loads(json.dumps(latest_break_20_code_list))
    last_break_20_code_list_int=[]
    for code_str in last_break_20_code_list:
        last_break_20_code_list_int.append(string.atoi(code_str))
    print('last_break_20_code_list_int=',last_break_20_code_list_int)
    print('latest_break_20_code_list=',latest_break_20_code_list)
    continue_break_20_list=list(set(latest_break_20_code_list).intersection(set(last_break_20_code_list_int)))
    latest_break_55_code_list=latest_break_55_df.index.values.tolist()
    latest_break_55_code_list= json.loads(json.dumps(latest_break_55_code_list))
    last_break_55_code_list_int=[]
    for code_str in last_break_55_code_list:
        last_break_55_code_list_int.append(string.atoi(code_str))
    print('last_break_55_code_list_int=',last_break_55_code_list_int)
    continue_break_55_list=list(set(latest_break_55_code_list).intersection(set(last_break_55_code_list_int)))

    print('latest_break_55_code_list=', latest_break_55_code_list)
    
    print('continue_break_20_list=',continue_break_20_list)
    print('continue_break_55_list=',continue_break_55_list)
    
    
#test2()     
#stock_test()
#stock_realtime_monitor()
#thread_test()
#market_test()



import _thread

def test_thread1():
    _thread.start_new_thread(market_test,())
    print('doing thread1')
    _thread.start_new_thread(stock_realtime_monitor,())
    print('doing thread')
    
    
    return

#test_thread1()
