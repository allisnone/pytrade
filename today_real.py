import tushare as ts
import tradeTime as tt
import time


#remain_time_to_trade=tt.get_remain_time_to_trade()
#print(remain_time_to_trade)
interval=30
while True:
    remain_time_to_trade=tt.get_remain_time_to_trade()
    if remain_time_to_trade>=interval:
        time.sleep(remain_time_to_trade)
    else:
        df=ts.get_today_all()
        print(df)
        df_1=df[(df.trade<df.open*0.99) & (df.changepercent>1.5)]
        print(df_1)
        time.sleep(max(interval))
