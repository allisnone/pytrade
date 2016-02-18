# -*- coding:utf-8 -*-
def hushen_risk0():
    is_over_ma5=False
    is_over_ma30=False
    is_great_drop_in_5m=True
    is_great_incrs_in_5m=True
    is_great_high_open=True
    is_great_low_open=True
    is_great_volume_incrs=True
    is_little_volume=True
    is_continue_low_open=True
    is_continue_high_open=True
    far_from_highest_20=True
    far_from_lowest_20=True
    return

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

def hushen_risk(score):
    return score

def chye_risk(score):
    return score

def risk_score(hushen_score,chye_score):
    is_sys_risk=False
    position=0
    hushen_risk_score=hushen_risk(hushen_score)
    chye_risk_score=chye_risk(chye_score)
    sys_risk_score=round(0.65*hushen_risk_score+0.35*chye_risk_score,2)  #-5 ~5
    sys_risk_range=10.0
    if sys_risk_score<-0.25*sys_risk_range:
        is_sys_risk=True
        position=0.0
    elif sys_risk_score < 0.25*sys_risk_range:
        #position=(0.25*sys_risk_range+is_sys_risk)/0.5*sys_risk_range
        position=round(0.5 +2.0*sys_risk_score/sys_risk_range,2)
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
        is_sys_risk=False
    else:
        position=0.85
        is_sys_risk=False
    return sys_risk_score,position

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
            sys_risk_score,position=risk_score(hushen_score, chye_score)
            print('sys_risk_score=',sys_risk_score,'position=',position)
            
test()
    