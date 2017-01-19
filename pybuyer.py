# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime
from pytrade_tdx import OperationTdx
import sys


stock_sql = StockSQL()
print(datetime.datetime.now())
accounts = ['36005', '38736']
op_tdx = OperationTdx(debug=debug_enable)
get_acc_buy_stocks(op_tdx,stock_sql,acc_list=accounts, buy_rate=1.0)