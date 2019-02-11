# -*- coding:utf-8 -*-
import datetime,time
#to get the latest trade day
except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06',\
                           '2015-10-07','2015-10-08', '2016-04-04','2016-05-02','2016-06-09','2016-06-10',\
                           '2016-09-15','2016-09-16','2016-10-03','2016-10-04','2016-10-05','2016-10-06',\
                           '2016-10-07','2017-01-02','2017-01-27','2017-01-30','2017-01-31','2017-02-01','2017-02-02',\
                           '2017-04-03','2017-04-04','2017-05-01','2017-05-29','2017-05-30','2017-10-02','2017-10-03',\
                           '2017-10-04','2017-10-05','2017-10-06','2018-01-01','2018-02-15','2018-02-16','2018-02-19',\
                           '2018-02-20','2018-02-21','2018-04-05','2018-02-06','2018-05-01','2018-06-18','2018-09-24',\
                           '2018-10-01','2018-10-02','2018-10-03','2018-10-04','2018-10-05','2019-01-01','2019-02-04','2019-02-05',\
                           '2019-02-06','2019-02-07','2019-02-08','2019-05-05','2019-05-01','2019-06-07',]

except_trade_day_list1 = []
for date_str in except_trade_day_list:
    except_trade_day_list1.append(date_str.replace('-', '/'))

def is_trade_date(given_date_str=None):
    """
    :param given_date_str: str type, like '2017-10-01'
    :return: bool type 
    """
    this_day=datetime.datetime.now()
    date_format='%Y-%m-%d'
    this_str=this_day.strftime(date_format)
    open_str=' 09:15:00'
    if given_date_str!=None:
        if given_date_str in except_trade_day_list or given_date_str in except_trade_day_list1:
            return False
        else:
            if '-' in given_date_str:
                pass
            else:
                date_format='%Y/%m/%d'
            this_day=datetime.datetime.strptime(given_date_str+open_str,date_format + ' %X')
    else:
        if this_str in except_trade_day_list or given_date_str in except_trade_day_list1:
            return False
        else:
            pass
    return this_day.isoweekday()<6

def get_latest_trade_date(this_date=None,date_format='%Y-%m-%d'):
    """
    :param this_date: datetime.datetim type, like datetime.datetime.now()
    :return: latest_day_str, str type 
    """
    this_day=datetime.datetime.now()
    if this_date!=None:
            this_day=this_date
    open_str=' 09:25:00'
    time_format = date_format + ' %X'
    this_str=this_day.strftime(time_format)
    if (this_day.hour>=0 and this_day.hour<9) or (this_day.hour==9 and this_day.minute<15):
        this_day=datetime.datetime.strptime(this_str,time_format)+datetime.timedelta(days=-1)
        this_str=this_day.strftime(date_format)  
    latest_day_str=''
    this_str=this_str[:10]
    while this_str>='1990-01-01':
        if is_trade_date(this_str):
            return this_str
            #break
        else:
            this_day=this_day+datetime.timedelta(days=-1)
            this_str=this_day.strftime(date_format)  

def get_next_trade_date(given_datetime=None,date_format='%Y-%m-%d'):
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
                this_day=datetime.datetime.strptime(latest_datetime_str,time_format)
            except:
                this_day=datetime.datetime.strptime(latest_datetime_str,date_format + ' %X')
        elif isinstance(latest_datetime, datetime.datetime):
            pass
        else:
            pass
    this_day=this_day+datetime.timedelta(days=1)
    next_date_str=this_day.strftime(date_format)
    init_date = '1990-01-01'
    if '-' not in date_format:
        init_date = '1990/01/01'
    while next_date_str>=init_date:
        if is_trade_date(next_date_str):
            return next_date_str
        else:
            this_day=this_day+datetime.timedelta(days=1)
            next_date_str=this_day.strftime(date_format) 

#to get the latest trade day
def get_last_trade_date(given_latest_datetime=None,date_format='%Y-%m-%d'):
    """
    :param given_latest_datetime: datetime type
    :return: last_date_str, str type 
    """
    time_format = date_format + ' %X'
    latest_datetime=datetime.datetime.now()
    if given_latest_datetime!=None:
        latest_datetime=given_latest_datetime
        if isinstance(latest_datetime, str):
            latest_datetime_str=latest_datetime+' 10:00:00'
            try:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,time_format)
            except:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,time_format)
    else:
        latest_day_str=get_latest_trade_date(date_format=date_format)
        latest_datetime_str=latest_day_str+' 10:00:00'
        try:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,time_format)
        except:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,time_format)
    last_datetime=latest_datetime+datetime.timedelta(days=-1)
    last_date_str=get_latest_trade_date(last_datetime,date_format=date_format)
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
    #MORNING_START = ' 9:15:00'
    MORNING_START = ' 9:20:00'
    MORNING_START_MINUTE = 20
    NOON_START = ' 13:00:00'
    if is_trade_date():
        if is_trade_time_now():
            #print('00')
            return 0.0
        else:
            this_time_str=this_time.strftime('%Y-%m-%d')
            hour=this_time.hour
            minute=this_time.minute
            second=this_time.second
            if hour<9 or (hour==9 and minute<MORNING_START_MINUTE):
                next_trade_str=this_time_str + MORNING_START
                #print('01')
            elif (hour==11 and minute>30) or hour==12:
                next_trade_str=this_time_str + NOON_START
                #print('02')
            elif hour>=15:
                #print('03')
                next_date_str=get_next_trade_date()
                next_trade_str=next_date_str + MORNING_START
            else:#trade time
                #print('04')
                return 0.0
    else:
        #print('10')
        next_date_str=get_next_trade_date()
        next_trade_str=next_date_str +  MORNING_START
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
    
def is_need_update_histdata(taget_last_date_str):
    """
    历史数据更新到交易的前一天，当天是交易日，16点后更新数据
    """
    if '-' in taget_last_date_str:
        taget_last_date_str = taget_last_date_str.replace('-', '/') 
    last_date_str = get_last_trade_date(date_format='%Y/%m/%d')
    if is_trade_date():
        if datetime.datetime.now().hour>=16:
            last_date_str = get_latest_trade_date(date_format='%Y/%m/%d')
    else:
        last_date_str = get_latest_trade_date(date_format='%Y/%m/%d')
    
    return taget_last_date_str<last_date_str
"""
print(is_trade_date('2017-08-04'))
print(get_pass_trade_time())
print(get_latest_trade_date())
print(get_last_trade_date())
print(get_next_trade_date())
print(get_remain_time_to_trade())
"""
