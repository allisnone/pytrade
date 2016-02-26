# -*- coding:utf-8 -*-
import datetime
#to get the latest trade day
def get_latest_trade_date(this_date=None):
    """
    :param this_date: datetime.date type, like datetime.date.today()
    :return: latest_day_str, str type 
    """
    except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06','2015-10-07','2015-10-08']
    this_day=datetime.datetime.now()
    if this_date!=None:
            this_day=this_date
    open_str=' 09:25:00'
    this_str=this_day.strftime('%Y-%m-%d %X')
    if (this_day.hour>=0 and this_day.hour<9) or (this_day.hour==9 and this_date.minute<15):
        this_day=datetime.datetime.strptime(this_str,'%Y-%m-%d %X')+datetime.timedelta(days=-1)
        this_str=this_day.strftime('%Y-%m-%d')  
    latest_day_str=''
    this_str=this_str[:10]
    while this_str>='2000-01-01':
        if this_day.isoweekday()<6 and (this_str not in except_trade_day_list):
            latest_day_str = this_str
            break
        else:
            this_day=this_day+datetime.timedelta(days=-1)
            this_str=this_day.strftime('%Y-%m-%d')  
    return latest_day_str

#to get the latest trade day
def get_last_trade_date(given_latest_datetime=None):
    """
    :param given_latest_datetime: datetime type
    :return: last_date_str, str type 
    """
    latest_datetime=datetime.datetime.now()
    if given_latest_datetime:
        latest_datetime=given_latest_datetime
        if isinstance(latest_datetime, str):
            latest_datetime_str=latest_datetime+' 10:00:00'
            try:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
            except:
                latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y/%m/%d %X')
    else:
        latest_day_str=get_latest_trade_date()
        print('latest_day_str=',latest_day_str)
        latest_datetime_str=latest_day_str+' 10:00:00'
        try:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
        except:
            latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y/%m/%d %X')
    print(type(latest_datetime))
    last_datetime=latest_datetime+datetime.timedelta(days=-1)
    last_date_str=get_latest_trade_date(last_datetime)
    print('last_date_str=',last_date_str)
    return last_date_str

def is_trade_time_now():
    except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06',\
                           '2015-10-07','2015-10-08', '2016-04-04','2016-05-02','2016-06-09','2016-06-10',\
                           '2016-09-15','2016-09-16','2016-10-03','2016-10-04','2016-10-05','2016-10-06',\
                           '2016-10-07','2017-01-02','2017-01-30','2017-01-31','2017-02-01','2017-02-02',\
                           '2017-04-03','2017-05-29','2017-10-02','2017-10-03','2017-10-04','2017-10-05','2017-10-06']
    now_timestamp=time.time()
    this_time=datetime.datetime.now()
    this_date=this_time.strftime('%Y-%m-%d')
    hour=this_time.hour
    minute=this_time.minute
    is_trade_time=((hour>=9 and minute>=15) and (hour<=11 and minute<=30)) or (hour>=13 and hour<=15)
    is_working_date=this_time.isoweekday()<6 and (this_date not in except_trade_day_list)
    return is_trade_time and is_working_date

def is_trade_time_now0(latest_trade_date):
    """
    :param latest_trade_date: str type
    :return: bool type 
    """
    this_time=datetime.datetime.now()
    this_str=this_time.strftime('%Y-%m-%d %X')
    #latest_trade_date=get_latest_trade_date()
    return this_str>=(latest_trade_date+ ' 09:31:00') and this_str <= (latest_trade_date + ' 15:00:00')

def get_pass_time():
    """
    提取已开市时间比例
    :param this_time: ，string
    :return:,float 
    """
    pass_second=0.0
    if not is_trade_time_now():
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