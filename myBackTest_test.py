# -*- coding:utf-8 -*-
from myBackTest import *

if __name__ == "__main__":
    import easyhistory
    """
    import pdSql as pds
    import sys
    #update_type = ''
    update_type = 'index'
    #update_type = 'position'
    if len(sys.argv)>=2:
        if sys.argv[1] and isinstance(sys.argv[1], str):
            update_type = sys.argv[1]  #start date string   
    #update_type = 'index'
    #update_type = 'position'
    stock_sql = pds.StockSQL()
    """
    #easyhistory.init('D', export='csv', path="C:/hist")
    #easyhistory.update(path="C:/hist")
    stock_synbol = '300162'
    stock_synbol = '002177'
    stock_synbol = '000418'
    stock_synbol = '600570'
    stock_synbol = '002504'
    stock_synbol = '000989'
    k_num = 0
    #all_codes = pds.get_all_code(pds.RAW_HIST_DIR)
    #all_stop_codes = get_stop_trade_symbol()
    #all_stop_codes,all_stocks = get_stopped_stocks()
    #all_codes = list(set(all_stocks).difference(set(all_stop_codes)))
    #all_stop_codes = []
    given_codes = []
    indexs = ['sh','sz','zxb','cyb','hs300','sh50']
    given_codes = indexs
    if len(sys.argv)>=2:
        if sys.argv[1] and isinstance(sys.argv[1], str):
            k_num = sys.argv[1]  #start date string   #新浪格式：2016-01-25， 银河导出格式： 2016/01/25
            try:
                k_num = int(k_num)
            except:
                pass
            #print('k_num=%s' % k_num)
        if len(sys.argv)>=3:
            if sys.argv[2] and isinstance(sys.argv[2], str) and (int(sys.argv[2])==1): #just test for a few stocks
                is_few_test = int(sys.argv[2])==1
                given_codes = ['000525','300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519','000418','600103','000029']
                #             '002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']# '300476', '002548', '002799']
    else:
        pass
    except_stocks = ['002548','002220','300467','300459','300238','603588','300379','002528',
                       '603026','002615','603609','603010','300459','300378','002709','300438',
                       '300277','002752','002613','300337','603005','603718','600666','002350',
                       '300451','300003','603022','300030','300240','603789','300433','300295',
                       '002544','300395','002605','300403','002225','002297','600572','000333',
                       '300413','002285','002312','002509','600305','002631','603718','002496',
                       '002600','603198','002444','300238','300467','300028','300033','300126',
                       '300135','300143','300380','300399','300117']
    #given_codes = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
    #             '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']
    back_test(k_num,given_codes,except_stocks=['000029'])#except_stocks)
    #k_num = 120
    #print(s_stock.temp_hist_df.tail(20))
