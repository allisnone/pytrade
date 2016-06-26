# -*- coding:utf-8 -*-
import datetime,time
#to get the latest trade day
except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06',\
                           '2015-10-07','2015-10-08', '2016-04-04','2016-05-02','2016-06-09','2016-06-10',\
                           '2016-09-15','2016-09-16','2016-10-03','2016-10-04','2016-10-05','2016-10-06',\
                           '2016-10-07','2017-01-02','2017-01-30','2017-01-31','2017-02-01','2017-02-02',\
                           '2017-04-03','2017-05-29','2017-10-02','2017-10-03','2017-10-04','2017-10-05','2017-10-06']

def is_trade_date(given_date_str=None):
    """
    :param given_date_str: str type, like '2017-10-01'
    :return: bool type 
    """
    this_day=datetime.datetime.now()
    this_str=this_day.strftime('%Y-%m-%d')
    open_str=' 09:15:00'
    if given_date_str!=None:
        if given_date_str in except_trade_day_list:
            return False
        else:
            this_day=datetime.datetime.strptime(given_date_str+open_str,'%Y-%m-%d %X')
    else:
        if this_str in except_trade_day_list:
            return False
        else:
            pass
    return this_day.isoweekday()<6

def get_latest_trade_date(this_date=None):
    """
    :param this_date: datetime.datetim type, like datetime.datetime.now()
    :return: latest_day_str, str type 
    """
    this_day=datetime.datetime.now()
    if this_date!=None:
            this_day=this_date
    open_str=' 09:25:00'
    this_str=this_day.strftime('%Y-%m-%d %X')
    if (this_day.hour>=0 and this_day.hour<9) or (this_day.hour==9 and this_day.minute<15):
        this_day=datetime.datetime.strptime(this_str,'%Y-%m-%d %X')+datetime.timedelta(days=-1)
        this_str=this_day.strftime('%Y-%m-%d')  
    latest_day_str=''
    this_str=this_str[:10]
    while this_str>='1990-01-01':
        if is_trade_date(this_str):
            return this_str
            #break
        else:
            this_day=this_day+datetime.timedelta(days=-1)
            this_str=this_day.strftime('%Y-%m-%d')  

def get_next_trade_date(given_datetime=None):
    """
    :param given_datetime: datetime.datetim type, like datetime.datetime.now()
    :return: next_date_str, str type 
    """
    this_day=datetime.datetime.now()
    if given_datetime!=None:
        latest_datetime=given_latest_datetime
        if isinstance(latest_datetime, str):
            latest_datetime_str=latest_datetime+' 10:00:00'
            try:
                this_day=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
            except:
                this_day=datetime.datetime.strptime(latest_datetime_str,'%Y/%m/%d %X')
        elif isinstance(latest_datetime, datetime.datetime):
            pass
        else:
            pass
    this_day=this_day+datetime.timedelta(days=1)
    next_date_str=this_day.strftime('%Y-%m-%d')
    while next_date_str>='1990-01-01':
        if is_trade_date(next_date_str):
            return next_date_str
        else:
            this_day=this_day+datetime.timedelta(days=1)
            next_date_str=this_day.strftime('%Y-%m-%d') 

#to get the latest trade day
def get_last_trade_date(given_latest_datetime=None):
    """
    :param given_latest_datetime: datetime type
    :return: last_date_str, str type 
    """
    latest_datetime=datetime.datetime.now()
    if given_latest_datetime!=None:
        latest_datetime=given_latest_datetime
        if isinstance(latest_datetime, str):
            latest_datetime_str=latest_datetime+' 10:00:00'
            try:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
            except:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y/%m/%d %X')
    else:
        latest_day_str=get_latest_trade_date()
        latest_datetime_str=latest_day_str+' 10:00:00'
        try:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
        except:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y/%m/%d %X')
    last_datetime=latest_datetime+datetime.timedelta(days=-1)
    last_date_str=get_latest_trade_date(last_datetime)
    return last_date_str

def is_trade_time_now():
    """
    :param 
    :return: bool type 
    """
    if not is_trade_date():
        return False
    this_time=datetime.datetime.now()
    hour=this_time.hour
    minute=this_time.minute
    is_trade_time=((hour==9 and minute>=15) or hour==10 or (hour==11 and minute<=30) or (hour>=13 and hour<15))
    return is_trade_time

def get_pass_trade_time():
    """
    提取已开市时间比例
    :param this_time: ，string
    :return: float, rate of pass trade time, 4 hours per day 
    """
    pass_second=0.0
    if not is_trade_date():
        return pass_second
    this_time=datetime.datetime.now()
    hour=this_time.hour
    minute=this_time.minute
    second=this_time.second
    total_second=4*60*60
    if hour<9 or (hour==9 and minute<=30):
        pass
    elif hour<11 or (hour==11 and minute<=30):
        pass_second=(hour*3600+minute*60+second)-(9*3600+30*60)
    elif hour<13:
        pass_second=2*60*60
    elif hour<15:
        pass_second=2*60*60+(hour*3600+minute*60+second)-13*3600
    else:
        pass_second=total_second
    return round(round(pass_second/total_second,2),2)

def get_remain_time_to_trade():
    """
    :param:
    :return: float, the remain second to trade next 
    """
    this_time=datetime.datetime.now()
    next_trade_str=''
    remain_time=0.0
    if is_trade_date():
        if is_trade_time_now():
            #print('00')
            return 0.0
        else:
            this_time_str=this_time.strftime('%Y-%m-%d')
            hour=this_time.hour
            minute=this_time.minute
            second=this_time.second
            if hour<9 or (hour==9 and minute<15):
                next_trade_str=this_time_str + ' 9:15:00'
                #print('01')
            elif (hour==11 and minute>30) or hour==12:
                next_trade_str=this_time_str + ' 13:00:00'
                #print('02')
            elif hour>=15:
                #print('03')
                next_date_str=get_next_trade_date()
                next_trade_str=next_date_str + ' 9:15:00'
            else:#trade time
                #print('04')
                return 0.0
    else:
        #print('10')
        next_date_str=get_latest_trade_date()
        next_trade_str=next_date_str + ' 9:15:00'
    print('next_trade_str=',next_trade_str)
    next_trade_time=datetime.datetime.strptime(next_trade_str,'%Y-%m-%d %X')
    delta_time=datetime.datetime.strptime(next_trade_str,'%Y-%m-%d %X')-this_time
    delta_seconds=delta_time.days*24*3600+delta_time.seconds+0.000001*delta_time.microseconds
    return delta_seconds

def get_timestamp(date_time_str=None):#获取时间戳
    #date_time_str='2015-07-20 13:20:01'
    if date_time_str==None:
        return time.time()
    else:
        return time.mktime(time.strptime(date_time_str, '%Y-%m-%d %X'))
"""
print(is_trade_date('2017-08-04'))
print(get_pass_trade_time())
print(get_latest_trade_date())
print(get_last_trade_date())
print(get_next_trade_date())
print(get_remain_time_to_trade())
"""