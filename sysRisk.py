# -*- coding:utf-8 -*-
from tradeStrategy import *
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

def sys_risk_anlyse(max_position=0.85,ultimate_coefficient=0.25,shzh_score=None,chy_score=None):
    """ 
    when less then -ultimate_coefficient*sys_risk_range, will be zero position; 
    when greater then ultimate_coefficient*sys_risk_range, will be max position; 
    others, will be linearly increased by sys_score
    """
    """
    :param max_position: float type,
    :param ultimate_coefficient: float type,
    :return: position,sys_score,is_sys_risk
    """
    position=0
    shangzheng_score=0.0
    chuangye_score=0.0
    is_sys_risk=False
    if shzh_score!=None:
        shangzheng_score=shzh_score
    else:
        shz_code_str='999999'
        print(shz_code_str,'----------------------------------')
        shz_stock=Stockhistory(shz_code_str,'D')
        shangzheng_score=shz_stock.get_market_score()
    if chy_score!=None:
        chuangye_score=chy_score
    else:
        chy_code_str='399006'
        print(chy_code_str,'----------------------------------')
        chy_stock=Stockhistory(chy_code_str,'D')
        chuangye_score=chy_stock.get_market_score()
    sys_score=round(0.65*shangzheng_score+0.35*chuangye_score,2)  #-5 ~5
    sys_risk_range=10.0 
    if sys_score<-ultimate_coefficient*sys_risk_range:
        is_sys_risk=True
        position=0.0
    elif sys_score < ultimate_coefficient*sys_risk_range:
        position=round(0.5*max_position/sys_risk_range/ultimate_coefficient*sys_score+0.5*max_position,2)
        if shangzheng_score<=-4 or chuangye_score<=-4:
            position=min(0.10*max_position,position)
        if shangzheng_score*chuangye_score<0:
            position=min(0.40*max_position,position)
        if shangzheng_score<=1 or chuangye_score<=1:
            position=min(0.70*max_position,position)
        is_sys_risk=False
    else:
        position=max_position
        is_sys_risk=False
    print('position=',position,'sys_score=',sys_score,'is_sys_risk=',is_sys_risk)
    return position,sys_score,is_sys_risk

def revised_position(sys_risk_anlyse_position,recent_100d_great_dropdown,recent_100d_great_increase,max_position=0.85):
    """ 
    when recent_100d_great_dropdown less then 2.0*permit_great_dropdown, will be linearly increased by recent_100d_great_dropdown
    """
    """
    :param sys_risk_anlyse_position: float type, position value from sys_risk_anlyse()
    :param recent_100d_great_dropdown: float type,
    :param recent_100d_great_increase: float type,
    :param max_position: float type,
    :return: final_position
    """
    final_position=0.0
    permit_great_dropdown=-0.15
    max_revise_drowdown_coefficient=1.5
    max_revise_increase_coefficient=max(2*permit_great_dropdown,-1)
    great_increase=0.618
    extream_increase=1.5
    print('sys_risk_anlyse_position=',sys_risk_anlyse_position,'recent_100d_great_dropdown=',recent_100d_great_dropdown,'recent_100d_great_increase=',recent_100d_great_increase)
    if sys_risk_anlyse_position>0.8*max_position:
        if recent_100d_great_increase<=great_increase: 
            final_position=sys_risk_anlyse_position
        elif recent_100d_great_increase>great_increase and recent_100d_great_increase<extream_increase:
            revise_coefficient=max_revise_increase_coefficient/(extream_increase-great_increase)*(recent_100d_great_increase-great_increase)
            print('recent_100d_great_increase=',recent_100d_great_increase,'revise_coefficient=',revise_coefficient)
            revise_posistion=round(sys_risk_anlyse_position*(1+revise_coefficient),2)
            print('revise_posistion=',revise_posistion)
            final_position=revise_posistion
        else:
            final_position=round(sys_risk_anlyse_position*(1+max_revise_increase_coefficient),2)
    elif sys_risk_anlyse_position>0.3:
        if recent_100d_great_dropdown>2.0*permit_great_dropdown: # great_dropdown>-0.15
            final_position=sys_risk_anlyse_position
        elif recent_100d_great_dropdown<2.0*permit_great_dropdown and recent_100d_great_dropdown>=5.0*permit_great_dropdown:
            # great_dropdown>-0.3 and great_dropdown<-0.15, 最大1.5倍position
            revise_coefficient=max_revise_drowdown_coefficient/3.0*(recent_100d_great_dropdown/permit_great_dropdown-2.0)
            print('recent_100d_great_dropdown=',recent_100d_great_dropdown,'revise_coefficient=',revise_coefficient)
            revise_posistion=round(sys_risk_anlyse_position*(1+revise_coefficient),2)
            print('revise_posistion=',revise_posistion)
            final_position=min(max(sys_risk_anlyse_position,revise_posistion),max_position)
        else:
            final_position=max_position
    else:
        pass
    print('final_position=',final_position)
    return final_position

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
            position,sys_score,is_sys_risk=sys_risk_anlyse(max_position=0.85,ultimate_coefficient=0.25,shzh_score=hushen_score,chy_score=chye_score)  
#test()

def tes1t():
    position,sys_score,is_sys_risk=sys_risk_anlyse(max_position=0.85,ultimate_coefficient=0.25)
    revised_position(sys_risk_anlyse_position=position,recent_100d_great_dropdown=-0.48,recent_100d_great_increase=0.3,max_position=0.85)
    
tes1t()

def revised_position_test():
    revised_position(sys_risk_anlyse_position=0.35,recent_100d_great_dropdown=-0.16,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.35,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.35,recent_100d_great_dropdown=-0.35,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.35,recent_100d_great_dropdown=-0.48,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.35,recent_100d_great_dropdown=-0.70,recent_100d_great_increase=0.3,max_position=0.85)
    print('------------------------------')
    revised_position(sys_risk_anlyse_position=0.50,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.5,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.7,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.9,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.0,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.2,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.4,max_position=0.85)
    revised_position(sys_risk_anlyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=2.4,max_position=0.85)
#revised_position_test()
   