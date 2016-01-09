
def hushen_risk():
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

def chye_risk():
    return

def risk_score():
    is_sys_risk=False
    position=0
    hushen_risk_score=hushen_risk()
    chye_risk_score=chye_risk()
    sys_risk_score=0.65*hushen_risk_score+0.35*chye_risk_score  #-5 ~5
    sys_risk_range=10.0
    if sys_risk_score<-0.25*sys_risk_range:
        is_sys_risk=True
        position=0.0
    elif sys_risk_score < 0.25*sys_risk_range:
        #position=(0.25*sys_risk_range+is_sys_risk)/0.5*sys_risk_range
        position=0.5 +2.0*is_sys_risk/sys_risk_range
    else:
        position=1.0
        
    return is_sys_risk,position

def position_control():
    return

def stock_risk():
    return


def exit_all():
    sys_risk=True
    