# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se

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

def sys_level_exit(l_change,p_change,delay):
    great_drop_exit_half=-2.0
    great_drop_exit_all=-5.0
    max_position=1.0
    if l_change<=great_drop_exit_half:
        max_position=0.25
    elif l_change <=1.5*great_drop_exit_half:
        max_position=0.50
    elif l_change<great_drop_exit_half:
        max_position=0.75
    else:
        pass
    
    if p_change<great_drop_exit_all:
        max_position=max_position*0.50
    elif p_change<great_drop_exit_half:
        max_position=max_position*0.75
    else:
        pass
    return max_position

def get_real_stock_k(code_str='999999'):
    return []
        
def sys_risk_analyse(is_realtime_update=False):
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
    shzh_weight=0.65
    #is_sys_risk=False
    shz_code_str='999999'
    print(shz_code_str,'----------------------------------')
    shz_stock=tds.Stockhistory(shz_code_str,'D')
    #print(shz_stock.h_df.tail(10))
    if is_realtime_update:
        k_data=get_real_stock_k(shz_code_str='999999')
        k_data=['2016/04/21',2954.38,2990.69,2935.05,3062.58,189000000,2.1115e+11]
        shz_stock.update_realtime_hist_df(k_data)
    #print(shz_stock.h_df.tail(10))
    shangzheng_ma_score,shangzheng_score,k_position=shz_stock.get_market_score()
    print(shangzheng_ma_score,shangzheng_score,k_position)
    scz_code_str='399001'
    zxb_code_str='399005'
    chy_code_str='399006'
    chy_code_str='300044'
    print(chy_code_str,'----------------------------------')
    chy_stock=tds.Stockhistory(chy_code_str,'D')
    if is_realtime_update:
        k_data=get_real_stock_k(shz_code_str='399006')
        #k_data=['2016/04/21',2954.38,2990.69,2935.05,3062.58,189000000,2.1115e+11]
        shz_stock.update_realtime_hist_df(k_data)
    chuangye_ma_score,chuangye_score,k_position=chy_stock.get_market_score()
    print(chuangye_ma_score,chuangye_score,k_position)
    #sys_score=round(0.65*shangzheng_score+0.35*chuangye_score,2)  #-5 ~5
    chy_first_date=chy_stock.temp_hist_df.head(1).iloc[0].date
    shz_temp_df=shz_stock.temp_hist_df.set_index('date')
    chy_temp_df=chy_stock.temp_hist_df.set_index('date')
    #shz_temp_df=shz_stock.temp_hist_df.tail(1000).set_index('date')
    #chy_temp_df=chy_stock.temp_hist_df.tail(1000).set_index('date')
    shz_temp_df=shz_temp_df.fillna(0)
    chy_temp_df=chy_temp_df.fillna(0)
    shz_temp_df['sys_score']=shzh_weight*shz_temp_df['k_score']+(1-shzh_weight)*chy_temp_df['k_score']
    shz_temp_df['position']=shzh_weight*shz_temp_df['position']+(1-shzh_weight)*chy_temp_df['position']
    shz_temp_df['operation']=shz_temp_df['position']-shz_temp_df['position'].shift(1)
    shz_temp_df.to_csv('shz_temp_df.csv')
    sys_df=shz_temp_df[['sys_score','position','operation']].round(3)
    sys_df.to_csv('sys.csv')
    return sys_df

def get_stock_position(stock_synbol='399006',is_realtime_update=False,index_weight=0.65):
    """ 
    when less then -ultimate_coefficient*sys_risk_range, will be zero position; 
    when greater then ultimate_coefficient*sys_risk_range, will be max position; 
    others, will be linearly increased by sys_score
    """
    """
    :param stock_synbol: str type, 个股指数
    :param is_realtime_update: bool type, 是否实时更新仓位
    :param index_weight: float type, 指数仓位占的比重
    :return: position,sys_score,is_sys_risk
    """
    refer_index='999999'    #参考指数
    if stock_synbol<'000999':#深证指数
        refer_index = '399001'
    elif stock_synbol>'002000' and stock_synbol<'002999':#中小板指数
        refer_index ='399005'
    elif stock_synbol>'300000' and stock_synbol<'309999':#创业板指数
        refer_index = '399006'
    elif stock_synbol > '600000' and stock_synbol<'609999':#上证指数
        refer_index = '999999'
    else:#返回系统仓位
        stock_synbol='399006'
        pass
    #index_weight=0.65#指数占的比重
    #is_sys_risk=False
    print('refer_index=%s' % refer_index,'----------------------------------')
    index_stock=tds.Stockhistory(refer_index,'D')
    #print(shz_stock.h_df.tail(10))
    if is_realtime_update:
        k_data=get_real_stock_k(code_str=refer_index)
        k_data=['2016/04/21',2954.38,2990.69,2935.05,3062.58,189000000,2.1115e+11]
        index_stock.update_realtime_hist_df()
    #print(shz_stock.h_df.tail(10))
    shangzheng_ma_score,shangzheng_score,k_position=index_stock.get_market_score()
    max_series,max_value,min_series,min_value=index_stock.get_max(column_name='close',latest_num=10)
    print(max_series,max_value,min_series,min_value)
    max_series,max_value,min_series,min_value=index_stock.get_max(column_name='close',latest_num=20)
    print(max_series,max_value,min_series,min_value)
    max_series,max_value,min_series,min_value=index_stock.get_max(column_name='close',latest_num=30)
    #index_stock.boduan_analyze()
    print(max_series,max_value,min_series,min_value)
    print(shangzheng_ma_score,shangzheng_score,k_position)
    print(stock_synbol,'----------------------------------')
    s_stock=tds.Stockhistory(stock_synbol,'D')
    if is_realtime_update:
        k_data=get_real_stock_k(code_str=stock_synbol)
        #k_data=['2016/04/21',2954.38,2990.69,2935.05,3062.58,189000000,2.1115e+11]
        s_stock.update_realtime_hist_df()
    chuangye_ma_score,chuangye_score,k_position=s_stock.get_market_score()
    s_stock.is_island_reverse_up()
    index_temp_df=index_stock.temp_hist_df.set_index('date')
    if s_stock.temp_hist_df.empty:
        index_temp_df['sys_score']=index_temp_df['k_score']
        index_temp_df['position']=index_temp_df['position']
        index_temp_df['operation']=index_temp_df['position']-index_temp_df['position'].shift(1)
        return index_temp_df[['sys_score','position','operation']].round(3)
    print(chuangye_ma_score,chuangye_score,k_position)
    #sys_score=round(0.65*shangzheng_score+0.35*chuangye_score,2)  #-5 ~5
    #stock_first_date=stock.temp_hist_df.head(1).iloc[0].date
    stock_temp_df=s_stock.temp_hist_df.set_index('date')
    #shz_temp_df=shz_stock.temp_hist_df.tail(1000).set_index('date')
    #chy_temp_df=chy_stock.temp_hist_df.tail(1000).set_index('date')
    i_temp_df=index_temp_df.fillna(0)
    s_temp_df=stock_temp_df.fillna(0)
    i_temp_df['sys_score']=index_weight*i_temp_df['k_score']+(1-index_weight)*s_temp_df['k_score']
    i_temp_df['position']=index_weight*i_temp_df['position']+(1-index_weight)*s_temp_df['position']
    i_temp_df['operation']=i_temp_df['position']-i_temp_df['position'].shift(1)
    i_temp_df.to_csv('shz_temp_df.csv')
    select_columns=['p_change','gap','star','p_change1','k_rate','p_rate','island','atr_in','reverse','cross1','cross2','cross3','sys_score','position','operation']
    stock_df=i_temp_df[select_columns].round(3)
    stock_df.to_csv('stock_%s.csv' % stock_synbol)
    print(stock_df.tail(20))
    return stock_df

def get_sys_risk_info(sys_df):
    if sys_df.empty:
        return 0,0,''
    sys_df.is_copy=False
    sys_df=sys_df.fillna(0)
    sys_score=sys_df.tail(1).iloc[0].sys_score
    position=sys_df.tail(1).iloc[0].position
    operation=sys_df.tail(1).iloc[0].operation
    latest_day=sys_df.tail(1).index.values.tolist()[0]
    return sys_score,position,operation,latest_day

def get_recent_100d_great_dropdown():
    return
def get_recent_100d_great_increase():
    return

def revised_position(sys_risk_analyse_position,recent_100d_great_dropdown,recent_100d_great_increase,max_position=0.85):
    """ 
    when recent_100d_great_dropdown less then 2.0*permit_great_dropdown, will be linearly increased by recent_100d_great_dropdown
    """
    """
    :param sys_risk_analyse_position: float type, position value from sys_risk_analyse()
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
    print('sys_risk_analyse_position=',sys_risk_analyse_position,'recent_100d_great_dropdown=',recent_100d_great_dropdown,'recent_100d_great_increase=',recent_100d_great_increase)
    if sys_risk_analyse_position>0.8*max_position:
        if recent_100d_great_increase<=great_increase: 
            final_position=sys_risk_analyse_position
        elif recent_100d_great_increase>great_increase and recent_100d_great_increase<extream_increase:
            revise_coefficient=max_revise_increase_coefficient/(extream_increase-great_increase)*(recent_100d_great_increase-great_increase)
            print('recent_100d_great_increase=',recent_100d_great_increase,'revise_coefficient=',revise_coefficient)
            revise_posistion=round(sys_risk_analyse_position*(1+revise_coefficient),2)
            print('revise_posistion=',revise_posistion)
            final_position=revise_posistion
        else:
            final_position=round(sys_risk_analyse_position*(1+max_revise_increase_coefficient),2)
    elif sys_risk_analyse_position>0.3:
        if recent_100d_great_dropdown>2.0*permit_great_dropdown: # great_dropdown>-0.15
            final_position=sys_risk_analyse_position
        elif recent_100d_great_dropdown<2.0*permit_great_dropdown and recent_100d_great_dropdown>=5.0*permit_great_dropdown:
            # great_dropdown>-0.3 and great_dropdown<-0.15, 最大1.5倍position
            revise_coefficient=max_revise_drowdown_coefficient/3.0*(recent_100d_great_dropdown/permit_great_dropdown-2.0)
            print('recent_100d_great_dropdown=',recent_100d_great_dropdown,'revise_coefficient=',revise_coefficient)
            revise_posistion=round(sys_risk_analyse_position*(1+revise_coefficient),2)
            print('revise_posistion=',revise_posistion)
            final_position=min(max(sys_risk_analyse_position,revise_posistion),max_position)
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
            position,sys_score,is_sys_risk=sys_risk_analyse(max_position=0.85,ultimate_coefficient=0.25,shzh_score=hushen_score,chy_score=chye_score)  
#test()
def sys_position_test():
    #sys_df=sys_risk_analyse()
    sys_df = get_stock_position(is_realtime_update=True)
    sys_df = get_stock_position(stock_synbol='300162',is_realtime_update=True)
    sys_df = get_stock_position(stock_synbol='002673',is_realtime_update=True)
    sys_df = get_stock_position(stock_synbol='000680',is_realtime_update=True)
    sys_score,position,operation,latest_day=get_sys_risk_info(sys_df)
    #se.send_position_mail(position_df=sys_df,symbol=None)
    revised_position(sys_risk_analyse_position=position,recent_100d_great_dropdown=-0.48,recent_100d_great_increase=0.2,max_position=0.85)
    
sys_position_test()

def revised_position_test():
    revised_position(sys_risk_analyse_position=0.35,recent_100d_great_dropdown=-0.16,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.35,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.35,recent_100d_great_dropdown=-0.35,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.35,recent_100d_great_dropdown=-0.48,recent_100d_great_increase=0.3,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.35,recent_100d_great_dropdown=-0.70,recent_100d_great_increase=0.3,max_position=0.85)
    print('------------------------------')
    revised_position(sys_risk_analyse_position=0.50,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.5,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.7,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=0.9,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.0,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.2,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=1.4,max_position=0.85)
    revised_position(sys_risk_analyse_position=0.80,recent_100d_great_dropdown=-0.25,recent_100d_great_increase=2.4,max_position=0.85)
#revised_position_test()


   