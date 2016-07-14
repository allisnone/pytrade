# -*- coding:utf-8 -*-
#import tradeStrategy as tds
#import sendEmail as se
import tradeTime as tt
import easyhistory
import datetime,time
import pdSql as pds
import myBackTest as mybt

if __name__ == "__main__":
    except_stocks = ['002548','002220','300467','300459','300238','603588','300379','002528',
                       '603026','002615','603609','603010','300459','300378','002709','300438',
                       '300277','002752','002613','300337','603005','603718','600666','002350',
                       '300451','300003','603022','300030','300240','603789','300433','300295',
                       '002544','300395','002605','300403','002225','002297','600572','000333',
                       '300413','002285','002312','002509','600305','002631','603718','002496',
                       '002600','603198','002444','300238','300467','300028','300033','300126',
                       '300135','300143','300380','300399','300117']
    #given_codes = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
    #               '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']
    given_codes = []                
    all_code,latest_time = pds.get_dir_latest_modify_time('c:/hist/day/data/')
    print('latest_time= ', latest_time)
    #easyhistory.init('D', export='csv', path="C:/hist",stock_codes=given_codes)
    easyhistory.update(path="C:/hist",stock_codes=given_codes)
    print('First update completed: ', datetime.datetime.now())
    
    updated_date_count = 1
    while True:
        #this_time=datetime.datetime.now()
        #hour=this_time.hour
        #minute=this_time.minute
        last_year_date =datetime.datetime.now() + datetime.timedelta(days=-365)
        date_str = last_year_date.strftime('%Y-%m-%d')
        sleep_seconds = 60*60
        if tt.is_trade_date():
            if tt.is_trade_time_now():
                pass
            else:
                if datetime.datetime.now().hour==18:
                    #easyhistory.init('D', export='csv', path="C:/hist")
                    easyhistory.update(path="C:/hist",stock_codes=given_codes)
                    updated_date_count = updated_date_count +1
                    print('update count %s at: ' % updated_date_count, datetime.datetime.now() )
                    mybt.back_test(k_num=date_str, given_codes=[],except_stocks=except_stocks)
                    sleep_seconds = tt.get_remain_time_to_trade()
                else:
                    pass
                    #sleep_seconds = tt.get_remain_time_to_trade()
        else:
            sleep_seconds = tt.get_remain_time_to_trade()   
        print('Sleep %s seconds.' % sleep_seconds)
        time.sleep(sleep_seconds)
        print('Sleep %s seconds.' % sleep_seconds)
        
