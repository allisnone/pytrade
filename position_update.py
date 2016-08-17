# -*- coding:utf-8 -*-
#import easytrader
import easyhistory
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
stock_sql.update_one_stock(symbol='cyb',force_update=True)

"""
potential_df = stock_sql.query_data(table='potential',fields='category_id,code,valid,name',condition='valid>=1')
print(potential_df)
lanchou_df = potential_df[potential_df['category_id']==1]
print(lanchou_df['code'].values.tolist())
"""

"""
update_data = stock_sql.get_table_update_time()
if update_type == 'index':
    stock_sql.update_sql_index(index_list=['sh','sz','zxb','cyb','hs300','sh50'],force_update=False)
    stock_sql.download_hist_as_csv(indexs = ['sh','sz','zxb','cyb','hs300','sh50'],dir='C:/hist/day/data/')
elif  update_type == 'position':
    stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
elif update_type == 'stock':
    easyhistory.update(path="C:/hist",stock_codes=[])
else:
    pass
print('last_position_update_time=',update_data['hold'])
print('last_index_update_time=',update_data['sh'])
print(stock_sql.hold)

"""

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