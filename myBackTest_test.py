# -*- coding:utf-8 -*-
# !/usr/bin/env python
from myBackTest1 import *
import datetime
#import pdSql as pds

if __name__ == "__main__":
    import easyhistory
    """
    
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
    stock_sql = StockSQL()
    """
    stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
    all_hold_stocks = []
    for account in list(stock_sql.hold.keys()):
        pos_df = stock_sql.hold[account]
        hold_stocks = pos_df['证券代码'].values.tolist()
        all_hold_stocks = list(set(all_hold_stocks)|set(hold_stocks))
    print("all_hold_stocks=",all_hold_stocks)
    """
    indexs = ['sh','sz','zxb','cyb','hs300','sh50']
    hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    print(holds,available_sells)
    hold_funds = []
    for hold in holds:
        if hold.startswith('1') or hold.startswith('5'):
            hold_funds.append(hold)
    #indexs = indexs + hold_funds
    hold_stocks = list(set(holds).difference(set(hold_funds)))
    print('hold_stocks=',hold_stocks)
    print(hold_df)
    """从新浪 qq网页更新股票"""
    #easyhistory.init(path="C:/hist",stock_codes=hold_stocks)
    #easyhistory.update(path="C:/hist",stock_codes=hold_stocks)
    
    #easyhistory.init('D', export='csv', path="C:/hist")
    #easyhistory.update(path="C:/hist")
    stock_synbol = '300162'
    stock_synbol = '002177'
    stock_synbol = '000418'
    stock_synbol = '600570'
    stock_synbol = '002504'
    stock_synbol = '000989'
    last_year_date =datetime.datetime.now() + datetime.timedelta(days=-365)
    last_year_date_str = last_year_date.strftime('%Y/%m/%d')
    k_num = last_year_date_str
    #all_codes = pds.get_all_code(pds.RAW_HIST_DIR)
    #all_stop_codes = get_stop_trade_symbol()
    #all_stop_codes,all_stocks = get_stopped_stocks()
    #all_codes = list(set(all_stocks).difference(set(all_stop_codes)))
    #all_stop_codes = []
    date_str ='19970101'
    givens = []
    source_type = 'yh'
    if len(sys.argv)>=2:
        if sys.argv[1] and isinstance(sys.argv[1], str):
            k_num = sys.argv[1]  #start date string   #新浪格式：2016-01-25， 银河导出格式： 2016/01/25
            date_str = k_num.replace('/', '')
            try:
                k_num = int(k_num)
            except:
                pass
            #print('k_num=%s' % k_num)
        if len(sys.argv)>=3:
            if sys.argv[2] and isinstance(sys.argv[2], str) and (int(sys.argv[2])==1): #just test for a few stocks
                is_few_test = int(sys.argv[2])==1
                givens = ['000525','300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519','000418','600103','000029']
                #             '002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']# '300476', '002548', '002799']
        if len(sys.argv)>=4 and isinstance(sys.argv[3], str):
            source_type = sys.argv[3]
    else:
        pass
    hist_dir = 'C:/hist/day/data/'
    if source_type=='yh' or source_type=='YH':
        hist_dir = 'C:/中国银河证券海王星/T0002/export/'
    indexs,funds,b_stock,all_stocks = pds.get_different_symbols(hist_dir)
    for stock in hold_stocks:
        #pds.update_one_stock(symbol=stock,realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=False)
        pass  
    
    pds.update_codes_from_YH(indexs,realtime_update=False,dest_dir="C:/中国银河证券海王星/T0002/export/", force_update_from_YH=True)
    
    #back_test(k_num,given_codes=indexs,except_stocks=[],type='index')#except_stocks)
    except_stocks = ['002548','002220','300467','300459','300238','603588','300379','002528',
                       '603026','002615','603609','603010','300459','300378','002709','300438',
                       '300277','002752','002613','300337','603005','603718','600666','002350',
                       '300451','300003','603022','300030','300240','603789','300433','300295',
                       '002544','300395','002605','300403','002225','002297','600572','000333',
                       '300413','002285','002312','002509','600305','002631','603718','002496',
                       '002600','603198','002444','300238','300467','300028','300033','300126',
                       '300135','300143','300380','300399','300117']
    #givens = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
    #             '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']
    
    hold_result_df = back_test(k_num,given_codes=holds,except_stocks=['002807','603515','160722'],type='hold',source=source_type)#,dapan_stocks=[])#except_stocks)
    addition_name = 'hold'
    hold_result_df.to_csv('C:/work/temp/regression_test_' + addition_name +'%s.csv' % date_str)
    
    #hold_statistics = pds.get_hold_stock_statistics(hold_stocks=hold_stocks+hold_funds)
    #hold_statistics.to_csv('C:/work/temp/statistics_test_' + addition_name +'%s.csv' % date_str)
    #print(hold_statistics)
    """ TA_LIB
    his = easyhistory.History(dtype='D', path='C:/hist',type='csv',codes=hold_stocks+hold_funds)
    his.update_indicator_results()      #TA_lib 跟新指标
    indicator_resuls = his.indicator_result
    res = his.indicator_result['000007']
    print(indicator_resuls)
    """
    #all_codes = list(set(all_codes).difference(set(funds+index+except_codes)))
    """
    for rate in [0,-0.005,-0.01]: #[0.015,0.01,0.007,0.003,0.03,0.02,0.00001]
        try:
            all_result_df = back_test(k_num,given_codes=[],except_stocks=['000029','002807','603515'],type='stock',source=source_type,rate_to_confirm=rate)#except_stocks)
        except:
            continue
    """
    dapan_codes = ['600029', '600018', '000776', '600016', '600606', '601668', '600050', '601688', '600030', 
                    '600104', '601377', '601633', '600585', '601186', '600036', '002450', '000538', '601818', 
                    '601898', '002304', '601628', '600276', '601800', '002027', '600000', '601318', '601088', 
                    '601601', '000001', '601988', '601390', '600015', '002673', '600547', '600340', '601238', 
                    '601006', '000783', '001979', '601857', '000768', '601766', '600518', '600011', '000166', 
                    '002024', '000002', '600519', '600048', '600383', '300498', '600028', '600999', '002142', 
                    '601018', '600887', '601336', '600958', '002252', '601328', '002594', '601398', '600115', 
                    '000063', '601618', '601727', '000895', '601985', '300104', '600900', '601989', '600019',
                    '601899', '600663', '600690', '000333', '600649', '600795', '002415', '000725', '601211', 
                    '000625', '000651', '601169', '601111', '601788', '002736', '601009', '601669', '600837', 
                    '601939', '603993', '601288', '601166', '000858', '601998', '600705']
    all_result_df = back_test(k_num,given_codes=[],except_stocks=[],type='stock',source=source_type,rate_to_confirm=0,dapan_stocks=dapan_codes)#except_stocks)
    #all_codes = all_result_df.index.values.tolist()
    #all_statistics = pds.get_hold_stock_statistics(hold_stocks=all_stocks,stock_dir='C:/hist/day/temp/')
    #all_statistics.to_csv('C:/work/temp/statistics_test_' + 'all' +'%s.csv' % date_str)
    """
    all_hold_stocks =hold_stocks
    if all_hold_stocks:
        hold_result = all_result_df[all_result_df.index.isin(all_hold_stocks)]
        addition_name = 'hold'
        hold_result.to_csv('C:/work/temp/regression_test_' + addition_name +'%s.csv' % date_str)
    """
    #k_num = 120
    #print(s_stock.temp_hist_df.tail(20))
