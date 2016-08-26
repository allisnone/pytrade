import easyhistory
import pdSql as pds

#my_stock_sql = pds.StockSQL()

#easyhistory.init('D', export='csv', path="C:/hist",stock_codes=[])
#easyhistory.update(path="C:/hist",stock_codes=['000042','000060'])
#easyhistory.update_single_code(dtype='D', stock_code='002789', path="C:/hist")
#his = easyhistory.History(dtype='D', path='C:/hist',type='mysql',codes=['sh','cyb'],stock_sql=my_stock_sql)
#his = easyhistory.History(dtype='D', path='C:/hist',type='csv',codes=['cyb','sh'])
his = easyhistory.History(dtype='D', path='C:/hist',type='csv',codes=['000007','002362'])
#test_code = 'sh'
test_code = '000007'
# MA 计算, 直接调用的 talib 的对应函数
def get_hist_indicator(easyhistory_obj,code_str):
    res = easyhistory_obj[code_str].MAX(20)
    res = easyhistory_obj[code_str].MIN(20)
    res = easyhistory_obj[code_str].MA(5)
    res = easyhistory_obj[code_str].MA(10)
    res = easyhistory_obj[code_str].MA(20)
    res = easyhistory_obj[code_str].MA(30)
    res = easyhistory_obj[code_str].MA(60)
    res = easyhistory_obj[code_str].MA(120)
    res = easyhistory_obj[code_str].MA(250)
    res = easyhistory_obj[code_str].CCI(timeperiod=14)
    res = easyhistory_obj[code_str].MACD(fastperiod=12, slowperiod=26, signalperiod=9)
    res = easyhistory_obj[code_str].BBANDS(timeperiod=10,nbdevup=2, nbdevdn=2)#(20,2,2)  #boll
    res = easyhistory_obj[code_str].STOCH(fastk_period=9, slowk_period=3, slowd_period=3)  #KDJ
    res = easyhistory_obj[code_str].MFI(timeperiod=14)  #MFI
    res = easyhistory_obj[code_str].ATR(timeperiod=14)  #Average True Range 
    res = easyhistory_obj[code_str].NATR(timeperiod=14)  #Normalized Average True Range 
    res = easyhistory_obj[code_str].MOM(12)#(timeperiod=12)  #Momentum Indicators
    res['MTM'] = 100*res['MOM']/(res['close'].shift(12))
    return res
#res = get_hist_indicator(easyhistory_obj=his,code_str=test_code)
#res = his.get_hist_indicator(code_str=test_code)
his.update_indicator_results()
print(his.indicator_result)
#res = his.get_hist_indicator(code_str='test_code')
res = his.indicator_result['000007']
print( res)
res.to_csv('%s.csv' % test_code)
describe_df = his[test_code].MA(1).tail(3).describe()
min_low = describe_df.loc['min'].low
min_close = describe_df.loc['min'].close
max_close = describe_df.loc['max'].close
max_high = describe_df.loc['max'].high

print(describe_df)
print(min_low,min_close,max_close)



def update_hist(codes=[]):
    this_day = easyhistory.Day(path="C:/hist")
    stock_codes_need_to_init = this_day.store.init_stock_codes
    actual_init_codes = list(set(stock_codes_need_to_init).intersection(set(codes)))
    if actual_init_codes:
        easyhistory.init('D', export='csv', path="C:/hist",stock_codes=actual_init_codes)
    else:
        pass
    if len(codes)>=1:
        for code in codes:
            easyhistory.update_single_code(dtype='D', stock_code=code, path="C:/hist")
    else:
        pass


push_stocks=['000932', '002191', '002521', '002766', '601009', '000002', '300162']
#update_hist(push_stocks)