

def dapan_zeshi():
    return

def filter_stock():
    ma30_1k<0
    ma30_k1>0
    
    return

def get_days_of_strong_zone():
    days_of_strong_zone = 0
    days_of_last_up_across_middle = 0
    days_of_last_down_across_middle = 0
    if days_of_last_up_across_middle<days_of_last_down_across_middle:
        days_of_strong_zone = days_of_last_up_across_middle
    else:
         days_of_strong_zone = -1 * days_of_last_down_across_middle
    return days_of_strong_zone

def boll_trade():
    days_of_strong_zone = 3  #表征运行的区间，强势区间为正
    days_up_across_upper = 0  #表征运行的区间，强势区间为正
    up_across_middle = True
    down_across_middle = True
    up_across_upper = True
    down_cross_upper = True
    #if close>las_close:
    if days_of_strong_zone<-3:
        if up_across_middle:
            buy = 1
        else:
            just_monitor = 1
    elif days_of_strong_zone>3:
        if down_across_middle:
            sell_now = 0.5   
        else:
            pass
        
        if days_up_across_upper==1:
            hold = 1
        elif days_up_across_upper>1:
            if is_last_chang_shangyin:
                sell_last_high = 1
            elif down_cross_upper:
                sell_now =1 
            else:
                pass
    else:
        if up_across_middle:
            buy = 0.5
        else:
            pass
        
        if down_across_middle:
            sell_now = 1
        else:
            pass
        
    
    
    return