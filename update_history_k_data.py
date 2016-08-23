# -*- coding:utf-8 -*-
#import tradeStrategy as tds
#import sendEmail as se
import tradeTime as tt
import easyhistory
import datetime,time
import pdSql as pds
import myBackTest as mybt

if __name__ == "__main__":
    except_stock = ['002548','002220','300467','300459','300238','603588','300379','002528',
                       '603026','002615','603609','603010','300459','300378','002709','300438',
                       '300277','002752','002613','300337','603005','603718','600666','002350',
                       '300451','300003','603022','300030','300240','603789','300433','300295',
                       '002544','300395','002605','300403','002225','002297','600572','000333',
                       '300413','002285','002312','002509','600305','002631','603718','002496',
                       '002600','603198','002444','300238','300467','300028','300033','300126',
                       '300135','300143','300380','300399','300117','000029','300372']
    #'300372' 创业板第一退市
    #except_stocks = ['000029','300372']
    #'000029'  数据错误：11.4.0
    #given_codes = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
    #               '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']
    given_codes = []                
    all_code,latest_time = pds.get_dir_latest_modify_time('c:/hist/day/data/')
    print('latest_time= ', latest_time)
    #easyhistory.init('D', export='csv', path="C:/hist",stock_codes=given_codes)
    easyhistory.update(path="C:/hist",stock_codes=given_codes)
    print('First update completed: ', datetime.datetime.now())
    last_year_date =datetime.datetime.now() + datetime.timedelta(days=-365)
    date_str = last_year_date.strftime('%Y-%m-%d')
    mybt.back_test(k_num=date_str, given_codes=[],except_stocks=except_stock,type='stock')
    print('First back_test completed: ', datetime.datetime.now())
    updated_date_count = 1
    while True:
        #this_time=datetime.datetime.now()
        #hour=this_time.hour
        #minute=this_time.minute
        stock_sql = pds.StockSQL()
        last_year_date =datetime.datetime.now() + datetime.timedelta(days=-365)
        date_str = last_year_date.strftime('%Y-%m-%d')
        sleep_seconds = 60
        if tt.is_trade_date():
            if tt.is_trade_time_now():
                if datetime.datetime.now().minute%2==0:
                    """更新持仓信息到数据库"""
                    stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
                    """更新指数历史数据到数据库"""
                    stock_sql.update_sql_index(index_list=['sh','sz','zxb','cyb','hs300','sh50'],force_update=True)
                    sleep_seconds=30
            else:
                if datetime.datetime.now().hour==18:
                    #easyhistory.init('D', export='csv', path="C:/hist")
                    updated_date_count = updated_date_count +1
                    """更新股票数据"""
                    easyhistory.update(path="C:/hist",stock_codes=given_codes)
                    
                    print('update count %s at: ' % updated_date_count, datetime.datetime.now() )
                    mybt.back_test(k_num=date_str, given_codes=[],except_stocks=except_stock,type='stock')
                    mybt.back_test(k_num=date_str, given_codes=['sh','sz','zxb','cyb','hs300','sh50'],except_stocks=['000029'], type='index')
                    """更新持仓信息到数据库"""
                    stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
                    """更新指数历史数据到数据库"""
                    stock_sql.update_sql_index(index_list=['sh','sz','zxb','cyb','hs300','sh50'],force_update=False)
                    sleep_seconds = tt.get_remain_time_to_trade()
                else:
                    pass
                    #sleep_seconds = tt.get_remain_time_to_trade()
        else:
            sleep_seconds = tt.get_remain_time_to_trade()   
        print('Going to sleep %s seconds.' % sleep_seconds)
        time.sleep(sleep_seconds)
        print('Slept %s seconds.' % sleep_seconds)
        
