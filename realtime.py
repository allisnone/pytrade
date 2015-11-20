import tushare as ts

def get_realtime_ticket(code):
    return

def holding_monitor(codes):
    return

def realtime_market(market):
    return

def sell_short(price,highest,permit_dropdown,exit_price,sell_times=None):
    sell_rate=0.0
    remain_time=1
    if sell_times:
        remain_time=sell_times
    if price<exit_price:
        sell_rate=1.0
        remain_time=0
    elif price<highest*(1.0-permit_dropdown/100.0):
        sell_rate=round(1.0/round(remain_time,2),2)
        remain_time=remain_time-1
    else:
        pass
    return sell_rate,remain_time
    