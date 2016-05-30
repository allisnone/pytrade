
# -*- coding:utf-8 -*-

import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt

import sys
#import argparse
 
 
if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(
        description='sum the integers at the command line')
    parser.add_argument(
        'integers', metavar='int', nargs='+', type=int,
        help='an integer to be summed')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the sum should be written')
    args = parser.parse_args()
    args.log.write('%s\n' % sum(args.integers))
    args.log.close()
    
    """
    stock_synbol = '300162'
    stock_synbol = '002177'
    stock_synbol = '000418'
    stock_synbol = '600570'
    stock_synbol = '300162'
    stock_synbol = '300458'
    stock_synbol = '300407'
    stock_synbol = '300269'
    stock_synbol = '600260'
    num = 0
    if len(sys.argv)>=3:
        if sys.argv[2] and isinstance(sys.argv[2], str):
            num = int(sys.argv[2])
    elif len(sys.argv)==2:
        if sys.argv[1] and isinstance(sys.argv[1], str) and len(sys.argv[1])==6:
            stock_synbol = sys.argv[1]
    else:
        pass
    num = 900
    s_stock=tds.Stockhistory(stock_synbol,'D',test_num=num)
    result_df = s_stock.form_temp_df(stock_synbol)
    test_result = s_stock.regression_test()
    s_stock.get_recent_max_min()
    print(test_result)
    #print(result_df.tail(20))
    s_stock.temp_hist_df.to_csv('./temp/%s.csv' % stock_synbol)
    #print(s_stock.temp_hist_df.tail(20))
   
    
    