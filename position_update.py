# -*- coding:utf-8 -*-
import easytrader
import pdSql as pds


stock_sql = pds.StockSQL()
broker = 'yh'
need_data = 'yh.json'
user = easytrader.use('yh')
user.prepare('yh.json')
holding_stocks_df = user.position#['证券代码']  #['code']
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



print(holding_stocks_df)
stock_sql.drop_table(table_name='myholding')
stock_sql.insert_table(data_frame=holding_stocks_df,table_name='myholding')