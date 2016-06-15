# -*- coding:utf-8 -*-
#import tradeStrategy as tds
#import sendEmail as se
import tradeTime as tt
import easyhistory
import datetime,time

if __name__ == "__main__":
    easyhistory.update(path="C:/hist")
    print('First update completed: ', datetime.datetime.now())
    updated_date_count = 1
    while True:
        #this_time=datetime.datetime.now()
        #hour=this_time.hour
        #minute=this_time.minute
        sleep_seconds = 60*60
        if tt.is_trade_date():
            if tt.is_trade_time_now():
                pass
            else:
                if datetime.datetime.now().hour==18:
                    #easyhistory.init('D', export='csv', path="C:/hist")
                    easyhistory.update(path="C:/hist")
                    updated_date_count = updated_date_count +1
                    print('update count %s at: ' % updated_date_count, datetime.datetime.now() )
                    sleep_seconds = tt.get_remain_time_to_trade()
                else:
                    pass
                    #sleep_seconds = tt.get_remain_time_to_trade()
        else:
            sleep_seconds = tt.get_remain_time_to_trade()
        time.sleep(sleep_seconds)
        print('Sleep %s seconds.' % sleep_seconds)
        
