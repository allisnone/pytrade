
import datetime
import sys   
import pdSql_common as pds
from pdSql import StockSQL
now_time =datetime.datetime.now()
now_time_str = now_time.strftime('%Y/%m/%d %X')
print('now_time = ',now_time_str)
d_format='%Y/%m/%d'
last_date_str = pds.tt.get_last_trade_date(date_format=d_format)
latest_date_str = pds.tt.get_latest_trade_date(date_format='%Y/%m/%d')
next_date_str = pds.tt.get_next_trade_date(date_format='%Y/%m/%d')
print('last_date = ',last_date_str)
print('latest_date_str=',latest_date_str)
print('next_date_str=',next_date_str)
code = '000001'
df = pds.get_yh_raw_hist_df(code,latest_count=None)
print(df.empty)
last_code_trade_date = df.tail(1).iloc[0].date
print('last_code_trade_date=',last_code_trade_date)#,type(last_code_trade_date))

def get_last_tradte_date_yh_hist(default_codes=['601398','000002','002001','300059','601857','600028','000333','300251','601766','002027']):
    last_date_str=''
    for test_code in default_codes:
        df = pds.get_yh_raw_hist_df(test_code,latest_count=None)
        last_code_trade_date = df.tail(1).iloc[0].date
        print('last_code_trade_date=',last_code_trade_date)#,type(last_code_trade_date))
        if not df.empty:
            last_date_str = df.tail(1).iloc[0].date
            if last_date_str:
                break
    return last_date_str


if True:
    taget_last_date_str = get_last_tradte_date_yh_hist()
    is_need_update = pds.tt.is_need_update_histdata(taget_last_date_str)
    print('is_need_update=',is_need_update)
    now_time =datetime.datetime.now()
    now_hour = datetime.datetime.now().hour 
    print('now_hour=',now_hour)
    now_time_str = now_time.strftime('%Y/%m/%d %X')
    print('now_time = ',now_time_str)
    print('update_latest update datetime to sql')
    stock_sql = StockSQL()
    stock_sql.write_tdx_histdata_update_time(now_time_str)
    #stock_sql.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
    #stock_sql.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
    stock_sql.write_position_update_time(now_time_str)
    df_dict = stock_sql.get_systime()
    print(df_dict)
    
    is_tdx_uptodate,is_pos_uptodate = stock_sql.is_histdata_uptodate()
    print(is_tdx_uptodate,is_pos_uptodate)