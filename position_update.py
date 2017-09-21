# -*- coding:utf-8 -*-
#import easytrader
import easyhistory
import pdSql_common as pds
from pdSql import StockSQL
import sys
import datetime


def update_k_data(update_type='yh'):
    stock_sql = StockSQL()
    hold_df,hold_stocks,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    print('hold_stocks=',hold_stocks)
    print('available_sells=',available_sells)
    
    #pds.get_exit_price(hold_codes=['002521'],data_path='C:/中国银河证券海王星/T0002/export/' )
    
    #print(hold_df)
    """从新浪 qq网页更新股票"""
    #easyhistory.init(path="C:/hist",stock_codes=hold_stocks)
    #easyhistory.update(path="C:/hist",stock_codes=hold_stocks)
    """从银河更新股票"""
    #for stock in hold_stocks:
        #pds.update_one_stock(symbol=stock,realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=False)
    #   pass
    
    #stock_sql.update_sql_position(users={'account':'36005','broker':'yh','json':'yh.json'})
    #stock_sql.update_sql_position(users={'account':'38736','broker':'yh','json':'yh1.json'})
    #hold_df,hold_stocks,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    #print('hold_stocks=',hold_stocks)
    #print(hold_df)
    #pds.update_one_stock(symbol='sh',force_update=False)
    #pds.update_codes_from_YH(realtime_update=False)
    """从银河更新指数"""
    #pds.update_codes_from_YH(realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=True)
    
    #pds.update_codes_from_YH(realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=True)
    #indexs = ['zxb', 'sh50', 'hs300', 'sz300', 'cyb', 'sz', 'zx300', 'sh']
    
    """
    potential_df = stock_sql.query_data(table='potential',fields='category_id,code,valid,name',condition='valid>=1')
    print(potential_df)
    lanchou_df = potential_df[potential_df['category_id']==1]
    print(lanchou_df['code'].values.tolist())
    """
    #"""
    last_date_str = pds.tt.get_last_trade_date(date_format='%Y/%m/%d')
    latest_date_str = pds.tt.get_latest_trade_date(date_format='%Y/%m/%d')
    next_date_str = pds.tt.get_next_trade_date(date_format='%Y/%m/%d')
    print('last_date = ',last_date_str)
    print('latest_date_str=',latest_date_str)
    print('next_date_str=',next_date_str)
    indexs,funds,b_stock,all_stocks = pds.get_different_symbols()
    if update_type == 'index':
        #从银河更新指数
        #stock_sql.update_sql_index(index_list=['sh','sz','zxb','cyb','hs300','sh50'],force_update=False)
        #stock_sql.download_hist_as_csv(indexs = ['sh','sz','zxb','cyb','hs300','sh50'],dir='C:/hist/day/data/')
        pds.update_codes_from_YH(indexs,realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=True)
    elif update_type == 'fund':
        #从银河更新基金
        all_codes = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
        funds =[]
        for code in all_codes:
            if code.startswith('1') or code.startswith('5'):
                funds.append(code)
        pds.update_codes_from_YH(funds,realtime_update=False,dest_dir='C:/hist/day/data/', force_update_from_YH=True)
    elif update_type == 'position':
        #更新仓位
        #stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
        stock_sql.update_sql_position(users={'account':'36005','broker':'yh','json':'yh.json'})
        stock_sql.update_sql_position(users={'account':'38736','broker':'yh','json':'yh1.json'})
        hold_df,hold_stocks,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
        print('hold_stocks=',hold_stocks)
        print(hold_df)
    elif update_type == 'stock':
        #从新浪 qq网页更新股票
        #easyhistory.init(path="C:/hist",stock_codes=hold_stocks)
        #easyhistory.update(path="C:/hist",stock_codes=hold_stocks)
        #easyhistory.init(path="C:/hist")#,stock_codes=all_codes)
        easyhistory.update(path="C:/hist",stock_codes=all_stocks)#+b_stock)
    elif update_type == 'YH' or update_type == 'yh':
        all_codes = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
        #all_codes = ['999999', '000016', '399007', '399008', '399006', '000300', '399005', '399001',
        #             '399004','399106','000009','000010','000903','000905']
        #all_codes=['300162']
        all_count = len(all_codes)
        latest_count = 0
        count = 0
        pc0=0
        for code in all_codes:
            df = pds.get_yh_raw_hist_df(code,latest_count=None)
            count = count + 1
            pc = round(round(count,2)/all_count,2)* 100
            if pc>pc0:
                print('count=',count)
                print('完成数据更新百分之%s' % pc)
                pc0 = pc
            if len(df)>=1:
                last_code_trade_date = df.tail(1).iloc[0].date
                if last_code_trade_date==latest_date_str:
                    latest_count = latest_count + 1
        latest_update_rate =round(round(latest_count,2)/all_count,2)
        print('latest_update_rate=',latest_update_rate)
            
    else:
        pass

#update_type = ''
update_type = 'index'
#update_type = 'position'
#update_type = 'stock'
update_type = 'yh'
#update_type = 'aa'
now_time =datetime.datetime.now()
now_time_str = now_time.strftime('%Y/%m/%d %X')
d_format='%Y/%m/%d'
last_date_str = pds.tt.get_last_trade_date(date_format=d_format)
print('now_time = ',now_time_str)
print('last_date = ',last_date_str)

if len(sys.argv)>=2:
    if sys.argv[1] and isinstance(sys.argv[1], str):
        update_type = sys.argv[1]  #start date string   
#update_type = 'index'
#update_type = 'position'
#update_type = 'aa'
update_k_data(update_type)

"""
update_data = stock_sql.get_table_update_time()
print('last_position_update_time=',update_data['hold'])
print('last_index_update_time=',update_data['sh'])
print(stock_sql.hold)
"""
#"""

"""
print(update_data)
broker = 'yh'
need_data = 'yh.json'
user = easytrader.use('yh')
user.prepare('yh.json')
holding_stocks_df = user.position#['证券代码']  #['code']
print(holding_stocks_df)
"""
"""
当前持仓  股份可用     参考市值   参考市价  股份余额    参考盈亏 交易市场   参考成本价 盈亏比例(%)        股东代码  \
0  6300  6300  24885.0   3.95  6300  343.00   深A   3.896   1.39%  0130010635   
1   400   400   9900.0  24.75   400  163.00   深A  24.343   1.67%  0130010635   
2   600   600  15060.0  25.10   600  115.00   深A  24.908   0.77%  0130010635   
3  1260     0  13041.0  10.35  1260  906.06   沪A   9.631   7.47%  A732980330   

     证券代码  证券名称  买入冻结 卖出冻结  
0  000932  华菱钢铁     0    0  
1  000977  浪潮信息     0    0  
2  300326   凯利泰     0    0  
3  601009  南京银行     0    0  
"""



#stock_sql.drop_table(table_name='myholding')
#stock_sql.insert_table(data_frame=holding_stocks_df,table_name='myholding')