# -*- coding:utf-8 -*-
from tradeStrategy import *
def get_market_score(market_type='sh'):
    ma_score=get_market_ma_score()
    trend_score=get_trend_score(initial_score)
    market_score=round(ma_score+trend_score,2)
    if market_score>=0:
        market_score=min(market_score,5.0)
    else:
        market_score=max(market_score,-5.0)
    return market_score

def get_market_ma_score(temp_hist_df,hist_ma_score=None,period_type=None):
    ma_score=0.0
    if hist_ma_score:
        ma_score=hist_ma_score
    else:
        if period_type=='long_turn':
            ma_score=get_long_turn_ma_score()
        elif period_type=='short_turn':
            ma_score=get_short_turn_ma_score()
        else:
            pass
    ma_trend_score=get_ma_trend_score(temp_hist_df)
    current_ma_score=round(ma_score+ma_trend_score,2)
    if current_ma_score>0:
        current_ma_score=min(current_ma_score,5.0)
    else:
        current_ma_score=max(current_ma_score,-5.0)
    return current_ma_score

def is_cross_point(last_short_ma,this_short_ma,last_long_ma,this_long_ma):
    ma_cross_value=0
    if last_long_ma>last_short_ma and this_short_ma>=this_long_ma:
        ma_cross_value=1
    elif last_long_ma<last_short_ma and this_short_ma<=this_long_ma:
        ma_cross_value=-1
    return ma_cross_value

def is_ma_cross_point(temp_hist_df):
    if len(temp_hist_df)<2:
        return 0,0,0
    hist_df=temp_hist_df.tail(2)
    ma5_0=hist_df.iloc[0].ma5
    ma10_0=hist_df.iloc[0].ma10
    ma30_0=hist_df.iloc[0].ma30
    ma60_0=hist_df.iloc[0].ma60
    ma5_1=hist_df.iloc[1].ma5
    ma10_1=hist_df.iloc[1].ma10
    ma30_1=hist_df.iloc[1].ma30
    ma60_1=hist_df.iloc[1].ma60
    ma_5_10_cross=is_cross_point(ma5_0, ma5_1, ma10_0, ma10_1)
    ma_10_30_cross=is_cross_point(ma10_0, ma10_1, ma30_0, ma30_1)
    ma_30_60_cross=is_cross_point(ma30_0, ma30_1, ma60_0, ma60_1)
    return ma_5_10_cross,ma_10_30_cross,ma_30_60_cross

def get_ma_trend_score(temp_hist_df):
    delta_score=0.5
    ma_trend_score=0.0
    ma_5_10_cross,ma_10_30_cross,ma_30_60_cross=is_ma_cross_point(temp_hist_df)
    ma_cross_num=ma_5_10_cross+ma_10_30_cross+ma_30_60_cross
    if ma_cross_num>0:
        ma_trend_score=min(round(ma_cross_num*delta_score,2),1.5)
    else:
        ma_trend_score=max(round(ma_cross_num*delta_score*1.5,2),-2.25)
    return ma_trend_score

def get_ma_score(ma_type='ma5'):
    return

def get_short_turn_ma_score():
    ma5_date_score=get_ma_score('ma5')
    ma10_date_score=get_ma_score('ma10')
    ma30_date_score=get_ma_score('ma30')
    ma60_date_score=get_ma_score('ma60')
    ma_score=0.5*ma5_date_score+0.3*ma10_date_score+0.2*ma30_date_score+0.1*ma60_date_score
    return ma_score

def get_long_turn_ma_score():
    ma5_date_score=get_ma_score('ma5')
    ma10_date_score=get_ma_score('ma10')
    ma30_date_score=get_ma_score('ma30')
    ma60_date_score=get_ma_score('ma60')
    ma_score=0.1*ma5_date_score+0.2*ma10_date_score+0.3*ma30_date_score+0.5*ma60_date_score
    return ma_score

def get_trend_score(initial_score):
    delta_score=0.5
    recent_10_hist_df=0
    open_rate=0
    increase_rate=0
    open_score_coefficient=get_open_score(open_rate)
    increase_score_coefficient=get_increase_score(increase_rate)
    continue_trend_num,great_change_num,volume_coefficient=get_continue_trend_num(recent_10_hist_df)
    continue_trend_score_coefficient,recent_great_change_coefficient=get_recent_trend_score(continue_trend_num,great_change_num)
    score=initial_score+(open_score_coefficient+increase_score_coefficient+continue_trend_score_coefficient+recent_great_change_coefficient+volume_coefficient)*0.5
    if score>0:
        score=min(score,5.0)
    else:
        score=max(score,-5.0)
    return score

def get_open_score(open_rate):
    great_high_open_rate=1.0
    great_low_open_rate=-1.5
    open_score_coefficient=0.0
    if open_rate>great_high_open_rate:
        open_score_coefficient=round(open_rate/great_high_open_rate,2)
    elif open_rate<great_low_open_rate:
        open_score_coefficient=-round(open_rate/great_low_open_rate,2)
    else:
        pass
    return open_score_coefficient

def get_increase_score(increase_rate):
    great_increase_rate=3.0
    great_descrease_rate=-3.0
    increase_score_coefficient=0.0
    if increase_rate>great_increase_rate:
        increase_score_coefficient=round(increase_rate/great_increase_rate,2)
        increase_score_coefficient=max(2.0,open_score_coefficient)
    elif increase_rate<great_low_open_rate:
        increase_score_coefficient=-round(increase_rate/great_low_open_rate,2)
        #increase_score_coefficient=max(-2.0,increase_score_coefficient)
    else:
        pass
    return increase_score_coefficient

def get_last_trade_date(date):
    return

def get_continue_trend_num(recent_10_hist_df):
    great_increase_rate=3.0
    great_descrease_rate=-3.0
    great_change_num=0
    great_increase_num=0
    great_descrease_num=0
    great_continue_increase_rate=2.0
    great_continue_descrease_rate=-2.0
    continue_trend_num=0
    latest_trade_date=recent_10_hist_df.tail(1).iloc[0].date
    great_increase_df=recent_10_hist_df[recent_10_hist_df.p_change>great_continue_increase_rate]
    volume_coefficient=0.0
    if great_increase_df.empty:
        pass
    else:
        latest_great_increase_date=great_increase_df.tail(1).iloc[0].date
        if latest_trade_date==latest_great_increase_date:
            continue_increase_num=1
            tatol_inscrease_num=len(great_increase_df)
            while tatol_inscrease_num-continue_increase_num>0:
                temp_inscrease_df=great_increase_df.head(tatol_inscrease_num-continue_increase_num)
                if temp_inscrease_df.tail(1).iloc[0].date==get_last_trade_date(latest_great_increase_date):
                    continue_increase_num+=1
                    latest_great_increase_date=get_last_trade_date(latest_great_increase_date)
                else:
                    break
            continue_trend_num=continue_increase_num
        else:
            great_change_df=recent_10_hist_df[recent_10_hist_df.p_change>great_increase_rate]
            great_increase_num=len(great_change_df)
            
        if continue_increase_num>=2:
            volume0=great_increase_df.tail(2).iloc[0].volume
            volume1=great_increase_df.tail(2).iloc[1].volume
            if volume1>volume0 and volume0:
                volume_coefficient=min(round(volume1/volume0,2),3.0)
            else:
                pass
        else:
            pass
    great_decrease_df=recent_10_hist_df[recent_10_hist_df.p_change<great_continue_descrease_rate]
    if great_decrease_df.empty:
        pass
    else:
        latest_great_decrease_date=great_decrease_df.tail(1).iloc[0].date
        if latest_trade_date==latest_great_decrease_date:
            continue_decrease_num=1
            tatol_decrease_num=len(great_decrease_df)
            while tatol_decrease_num-continue_decrease_num>0:
                temp_decrease_df=great_decrease_df.head(tatol_decrease_num-continue_decrease_num)
                if temp_decrease_df.tail(1).iloc[0].date==get_last_trade_date(latest_great_decrease_date):
                    continue_decrease_num+=1
                    latest_great_decrease_date=get_last_trade_date(latest_great_decrease_date)
                else:
                    break
            continue_trend_num=-continue_decrease_num
        else:
            great_change_df=recent_10_hist_df[recent_10_hist_df.p_change<great_descrease_rate]
            great_descrease_num=len(great_change_df)
        
        if continue_decrease_num>=2:
            volume0=great_decrease_df.tail(2).iloc[0].volume
            volume1=great_decrease_df.tail(2).iloc[1].volume
            if volume1>volume0 and volume0:
                volume_coefficient=max(-round(volume1/volume0,2),-3.0)
            else:
                pass
        else:
            pass
    if great_increase_num==great_descrease_num:
        pass
    elif great_increase_num>great_descrease_num:
        great_change_num=great_increase_num
    else:
        great_change_num=-great_descrease_num
    return continue_trend_num,great_change_num,volume_coefficient

def get_recent_trend_score(continue_trend_num,great_change_num):
    #continue_trend_num,great_change_num,volume_coefficient=get_continue_trend_num(recent_10_hist_df)
    continue_trend_score_coefficient=0.0
    if continue_trend_num>2:
        continue_trend_score_coefficient=round(continue_trend_num/2.0,2)
        continue_trend_score_coefficient=max(3.0,open_score_coefficient)
    elif continue_trend_num<-2:
        continue_trend_score_coefficient=round(continue_trend_num/2.0,2)
    else:
        pass
    recent_great_change_coefficient=0.0
    if great_change_num>2:
        recent_great_change_coefficient=round(great_change_num/2.0,2)
        recent_great_change_coefficient=min(3.0,recent_great_change_coefficient)
    elif great_change_num<-2:
        recent_great_change_coefficient=round(great_change_num/2.0,2)
    else:
        pass
    return continue_trend_score_coefficient,recent_great_change_coefficient


def quick_drop_down(test_interval_minutes=5,drop_rate=-3.0):
    return

def is_first_down():
    is_increase_trend=True
    is_close_lower_than_last_lowest=True
    is_lowest_lower_than_last_lowest=True
    is_low_open_than_last_lowest=True
    return

def is_great_weak():
    return

def is_first_up():
    return

def risk_score():
    
    shz_code_str='999999'
    print(shz_code_str,'----------------------------------')
    shz_stock=Stockhistory(shz_code_str,'D')
    shangzheng_score=shz_stock.get_market_score()
    
    chy_code_str='399006'
    print(chy_code_str,'----------------------------------')
    chy_stock=Stockhistory(chy_code_str,'D')
    chuangye_score=chy_stock.get_market_score()
    
    is_sys_risk=False
    position=0
    #hushen_risk_score=get_market_score(market_type='sh')
    #chye_risk_score=get_market_score(market_type='chye')
    sys_risk_score=round(0.65*shangzheng_score+0.35*chuangye_score,2)  #-5 ~5
    sys_risk_range=10.0
    MAX_POSITION=0.85
    ultimate_coefficient=0.25
    if sys_risk_score<-ultimate_coefficient*sys_risk_range:
        is_sys_risk=True
        position=0.0
    elif sys_risk_score < ultimate_coefficient*sys_risk_range:
        #position=(0.25*sys_risk_range+is_sys_risk)/0.5*sys_risk_range
        #position=round(0.5 +2.0*sys_risk_score/sys_risk_range,2)
        position=round(0.5*MAX_POSITION/sys_risk_range/ultimate_coefficient*sys_risk_score+0.5*MAX_POSITION,2)
        """
        if  hushen_score<=-5.0 or chye_score<=-5.0:
            position=0.0
        elif hushen_score<=-4.0 or chye_score<=-4.5:
            position=min(0.1,position)
        elif hushen_score<=-2.5 or chye_score<=-3:
            position=min(0.3,position)
        elif hushen_score<=1 or chye_score<=1:
            pass
            position=min(0.75,position)
        else:
            position=min(0.85,position)
        """
        is_sys_risk=False
    else:
        position=MAX_POSITION
        is_sys_risk=False
    print('position=',position,'sys_risk_score=',sys_risk_score,'is_sys_risk=',is_sys_risk)
    return position,sys_risk_score,is_sys_risk

def position_control():
    return

def stock_risk():
    return


def exit_all():
    sys_risk=True
    
    
def test():
    #hushen_score=-5
    #chye_score=-5
    for hushen_score in range(-5,6):
        for chye_score in range(-5,6):
            print('hushen_score=',hushen_score,'chye_score=',chye_score)
            position,sys_risk_score,is_sys_risk=risk_score(hushen_score, chye_score)
            print('sys_risk_score=',sys_risk_score,'position=',position)
            
#test()

def tes1t():
    position,sys_risk_score,is_sys_risk=risk_score()
    
tes1t()