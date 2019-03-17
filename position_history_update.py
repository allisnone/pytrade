# -*- coding:utf-8 -*-
# !/usr/bin/env python
#import easytrader
import easyhistory
import pdSql_common as pds
from pdSql import StockSQL
import sys
import datetime

from pytrade_api import *

from multiprocessing import Pool
import os, time
import file_config as fc
import code

stock_sql_obj=StockSQL(sqlite_file='pytrader.db',sqltype='sqlite',is_today_update=True)
CHINESE_DICT = stock_sql_obj.get_code_to_name()

def seprate_list(all_codes,seprate_num=4):
    """
    分割股票池
    """
    #all_codes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    c = len(all_codes)
    sub_c = int(c/seprate_num)
    code_list_dict = {}
    for j in range(seprate_num-1):
        code_list_dict[j] = all_codes[j*sub_c:(j+1)*sub_c]
    code_list_dict[j+1] = all_codes[(j+1)*sub_c:]
    return code_list_dict

def update_yh_hist_data(all_codes,process_id,latest_date_str):
    """
    更新历史数据，单个CPU
    """
    all_count = len(all_codes)
    print('processor %s: all_count=%s '% (process_id,all_count))
    if all_count<=0:
        print('processor %s: empty list'% process_id)
        return
    else:
        print('processor %s start'%process_id)
        latest_count = 0
        count = 0
        pc0=0
        #print('all_codes=',all_codes)
        for code in all_codes:
            #print('code=',code)
            df,has_tdx_last_string = pds.get_yh_raw_hist_df(code,latest_count=None)
            pc = round(round(count,2)/all_count,2)*100
            if pc>pc0:
                #print('count=',count)
                print('processor %s 完成数据更新百分之%s' % (process_id,pc))
                pc0 = pc
            if len(df)>=1:
                last_code_trade_date = df.tail(1).iloc[0].date
                if last_code_trade_date==latest_date_str:
                    latest_count = latest_count + 1
            #time.sleep(0.2)
            count = count + 1
        latest_update_rate =round(round(latest_count,2)/all_count,2)
        print('latest_update_rate_processor_%s=%s'%(process_id,latest_update_rate))
    return

def update_one_stock_k_data(code):
    df,has_tdx_last_string = pds.get_yh_raw_hist_df(code,latest_count=None)
    return

def multiprocess_update_k_data0(code_list_dict,update_type='yh'):
    """
    多进程更新历史数据，apply_async方法
    存在问题：数据分片丢失
    """
    #code_list_dict = seprate_list(all_codes,4)
    #print('code_list_dict=',code_list_dict)
    print('Parent process %s.' % os.getpid())
    processor_num=len(code_list_dict)
    #update_yh_hist_data(codes_list=[],process_id=0)
    p = Pool()
    for i in range(processor_num):
        p.apply_async(update_yh_hist_data, args=(code_list_dict[i],i,last_date_str,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    return

def multiprocess_update_k_data(allcodes,update_type='yh',pool_num=10):
    """
    多进程更新历史数据，map方法
    """
    #code_list_dict = seprate_list(all_codes,4)
    #print('code_list_dict=',code_list_dict)
    print('Parent process %s, multiprocess_num=%s.' % (os.getpid(),pool_num))
    processor_num=len(allcodes)
    #update_yh_hist_data(codes_list=[],process_id=0)
    p = Pool(pool_num)
    p.map(update_one_stock_k_data,allcodes)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    return

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
        """
        code_list_dict = seprate_list(all_codes,4)
        print('code_list_dict=',code_list_dict)
        print('Parent process %s.' % os.getpid())
        #update_yh_hist_data(codes_list=[],process_id=0)
        p = Pool()
        for i in range(4):
            p.apply_async(update_yh_hist_data, args=(code_list_dict[i],i))
        print('Waiting for all subprocesses done...')
        p.close()
        p.join()
        print('All subprocesses done.')
        """
        all_count = len(all_codes)
        latest_count = 0
        count = 0
        pc0=0
        for code in all_codes:
            df,has_tdx_last_string = pds.get_yh_raw_hist_df(code,latest_count=None)
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
        #"""
            
    else:
        pass

def get_stock_last_trade_date_yh():
    last_date_str=''
    is_need_del_tdx_last_string=False
    df,has_tdx_last_string = pds.get_yh_raw_hist_df(test_code,latest_count=None)
    if has_tdx_last_string:
        is_need_del_tdx_last_string =True
    if not df.empty:
        last_date_str_stock = df.tail(1).iloc[0].date
        if last_date_str_stock>=target_last_date_str:
            last_date_str = last_date_str_stock
        else:
            if last_date_str_stock>last_date_str:
                last_date_str = last_date_str_stock
            else:
                pass
    else:
        pass
                
    return last_date_str,is_need_del_tdx_last_string 
   
def get_last_trade_date_yh_hist(target_last_date_str,default_codes=['601398','000002','002001','300059','601857','600028','000333','300251','601766','002027']):
    last_date_str=''
    is_need_del_tdx_last_string = False
    for test_code in default_codes:
        df,has_tdx_last_string = pds.get_yh_raw_hist_df(test_code,latest_count=None)
        if has_tdx_last_string:
            is_need_del_tdx_last_string =True
        if not df.empty:
            last_date_str_stock = df.tail(1).iloc[0].date
            if last_date_str_stock>=target_last_date_str:
                last_date_str = last_date_str_stock
                break
            else:
                if last_date_str_stock>last_date_str:
                    last_date_str = last_date_str_stock
                else:
                    pass
                
    return last_date_str,is_need_del_tdx_last_string

def update_hist_k_datas(update_type='yh'):
    target_last_date_str = pds.tt.get_last_trade_date(date_format='%Y/%m/%d')
    last_date_str,is_need_del_tdx_last_string = get_last_trade_date_yh_hist(target_last_date_str)
    is_need_update = pds.tt.is_need_update_histdata(last_date_str)
    update_state = 0
    if is_need_update or is_need_del_tdx_last_string:
        start = time.time()
        all_codes = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
        #multiprocess_update_k_data(code_list_dict)  #apply,非阻塞，传不同参数，支持回调函数
        multiprocess_update_k_data(all_codes,update_type)  #map，阻塞，一个参数
        end = time.time()
        print('Task update yh hist data runs %0.2f seconds.' % (end - start))
        """Post-check"""
        last_date_str,is_need_del_tdx_last_string = get_last_trade_date_yh_hist(target_last_date_str)
        is_need_update = pds.tt.is_need_update_histdata(last_date_str)
        if is_need_update and not is_need_del_tdx_last_string:
            print('尝试更新历史数据，但是更新失败；请全部盘后数据已下载...')
            update_state = -1
        else:
            update_state = 1
    else:
        print('No need to update history data')
    return update_state

def append_to_csv(value,column_name='code',file_name='C:/work/temp/stop_stocks.csv',empty_first=False):
    """
    追加单列的CSV文件
    """
    stop_codes = []
    if empty_first:
        pd.DataFrame({column_name:[]}).to_csv(file_name,encoding='utf-8')
    try:
        stop_trade_df = df=pd.read_csv(file_name)
        stop_codes = stop_trade_df[column_name].values.tolist()
    except:
        pd.DataFrame({column_name:[]}).to_csv(file_name,encoding='utf-8')
    stop_codes.append(value)
    new_df = pd.DataFrame({column_name:stop_codes})
    new_df.to_csv(file_name,encoding='utf-8')
    return new_df

def combine_file(tail_num=1,dest_dir='C:/work/temp/',keyword='',prefile_slip_num=0,columns=None,file_list=[],chinese_dict={}):
    """
    合并指定目录的最后几行
    """
    all_files = os.listdir(dest_dir)
    df = pd.DataFrame({})
    if not all_files:
        return df
    file_names = []
    if not keyword:
        file_names = all_files
    else:#根据keywo过滤文件
        for file in all_files:
            if keyword in file:
                file_names.append(file)
            else:
                continue
    #file_names=['bs_000001.csv', 'bs_000002.csv']
    #file_names=['000001.csv', '000002.csv']
    if file_list:
        file_names = list(set(file_names).intersection(set(file_list)))
    for file_name in file_names:
        tail_df = pd.read_csv(dest_dir+file_name,usecols=None).tail(tail_num)
        #columns = tail_df.columns.values.tolist()
        #print('columns',columns)
        prefile_name = file_name.split('.')[0]
        if prefile_slip_num:
            prefile_name = prefile_name[prefile_slip_num:]
        tail_df['code'] = prefile_name
        #tail_df['name'] = tail_df['code'].apply(lambda x: pds.format_name_by_code(x,CHINESE_DICT))
        """
        if CHINESE_DICT:#添加中文代码
            try:
                tail_df['name'] = CHINESE_DICT[prefile_name]
            except:
                tail_df['name'] = '某指数'
        """
        df=df.append(tail_df)
    return df
#df = combine_file(tail_num=1,dest_dir='d:/work/temp2/')

def get_latest_yh_k_stocks(write_file_name=fc.ALL_YH_KDATA_FILE,data_dir=fc.YH_SOURCE_DATA_DIR):
    """
    获取所有银河最后一个K线的数据：特定目录下
    """
    columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
    columns = pds.get_data_columns(dest_dir=data_dir)
    df = combine_file(tail_num=1,dest_dir=data_dir,keyword='',prefile_slip_num=0,columns=columns)
    if df.empty:
        return df
    df['counts']=df.index
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']+['counts','code']]
    df['code'] = df['code'].apply(lambda x: pds.format_code(x))
    df['name'] = df['code'].apply(lambda x: pds.format_name_by_code(x,CHINESE_DICT))
    df = df.set_index('code')
    """
    if CHINESE_DICT:#添加中文代码
            try:
                tail_df['name'] = CHINESE_DICT[prefile_name]
            except:
                tail_df['name'] = '某指数'
    """
    if write_file_name:
        try:
            df.to_csv(write_file_name,encoding='utf-8')
        except Exception as e:
            print('get_latest_yh_k_stocks： ',e)
    return df
#get_latest_yh_k_stocks()
def get_latest_yh_k_stocks_from_csv(file_name=fc.ALL_YH_KDATA_FILE):
    """
    获取股票K线数据，数据来源银河证券
    """
    #file_name = 'C:/work/result/all_yh_stocks.csv'
    #columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']+['counts','code']
    columns = pds.get_data_columns(dest_dir=fc.YH_SOURCE_DATA_DIR) + ['counts','code']
    #try:
    if True:
        df = pd.read_csv(file_name)#,usecols=columns)
        #print(df)
        #print(type(df['code']))
        df['code'] = df['name'].apply(lambda x:pds.format_code(x))
        df['name'] = df['code'].apply(lambda x: pds.format_name_by_code(x,CHINESE_DICT))
        df = df.set_index('code')
        return df
    #except:
    #    return get_latest_yh_k_stocks(write_file_name=file_name)
#print(get_latest_yh_k_stocks_from_csv())
def get_stop_stock(last_date_str,source='from_yh'):
    """
    获取停牌股票，数据来源银河证券
    """
    df = get_latest_yh_k_stocks_from_csv(write_file_name=fc.ALL_YH_KDATA_FILE)
    if df.empty:
            return pd.DataFrame({})
    stop_df = df[df.date<last_date_str]
    return stop_df
    
def update_history_postion():
    #freeze_support()
    #update_type = ''
    update_type = 'index'
    #update_type = 'position'
    #update_type = 'stock'
    update_type = 'yh'
    #update_type = 'aa'
    
    now_time =datetime.datetime.now()
    now_time_str = now_time.strftime('%Y/%m/%d %X')
    last_date_str = pds.tt.get_last_trade_date(date_format='%Y/%m/%d')
    print('now_time = ',now_time_str)
    print('last_trade_date = ',last_date_str)
 
    if len(sys.argv)>=2:
        if sys.argv[1] and isinstance(sys.argv[1], str):
            update_type = sys.argv[1]  #start date string   
    """
    #update_type = 'index'
    #update_type = 'position'
    #update_type = 'aa'
    #update_k_data(update_type)
    all_codes = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
    #all_codes = ['999999', '000016', '399007', '399008', '399006', '000300', '399005', '399001',
    #             '399004','399106','000009','000010','000903','000905']
    #all_codes=['300162']
    code_list_dict = seprate_list(all_codes,4)
    #print('code_list_dict=',code_list_dict)
    
    #multiprocess_update_k_data(code_list_dict)  #apply,非阻塞，传不同参数，支持回调函数
    multiprocess_update_k_data(all_codes,update_type='yh')  #map，阻塞，一个参数
    
    """
    stock_sql = StockSQL()
    pre_is_tdx_uptodate,pre_is_pos_uptodate,pre_is_backtest_uptodate,systime_dict = stock_sql.is_histdata_uptodate()
    print(pre_is_tdx_uptodate,pre_is_pos_uptodate,pre_is_backtest_uptodate,systime_dict)
    #pre_is_tdx_uptodate,pre_is_pos_uptodate=True,False
    pre_is_tdx_uptodate = False
    if not pre_is_tdx_uptodate:#更新历史数据
        update_state = update_hist_k_datas(update_type)
        if update_state:
            """写入数据库:标识已经更新通达信历史数据 """
            #stock_sql.write_tdx_histdata_update_time(now_time_str)
            stock_sql.update_system_time(update_field='tdx_update_time')
            
            """更新all-in-one历史数据文件"""
            get_latest_yh_k_stocks(fc.ALL_YH_KDATA_FILE)
    else:
        print('历史数据已经更新，无需更新;上一次更新时间：%s' % systime_dict['tdx_update_time'])
    #stock_sql.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
    #stock_sql.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
    if not pre_is_pos_uptodate:
        """更新持仓数据"""
        trader_api='shuangzixing'
        op_tdx = trader(trade_api='shuangzixing',acc='331600036005',bebug=False)
        if not op_tdx:
            print('Error')
        """
        op_tdx =trader(trade_api,bebug=True)
        op_tdx.enable_debug(debug=True)
        """
        #pre_position = op_tdx.getPositionDict()
        position = op_tdx.get_all_position()
        #position,avl_sell_datas,monitor_stocks = op_tdx.get_all_positions()
        print('position=',position)
        pos_df = pds.position_datafrom_from_dict(position)
       
        if not pos_df.empty:
            """写入数据库:标识已经更新持仓数据 """
            stock_sql.update_all_position(pos_df,table_name='allpositions')
            #stock_sql.write_position_update_time(now_time_str)
            stock_sql.update_system_time(update_field='pos_update_time')
            """持仓数据写入CSV文件"""
            try:
                pos_df.to_csv(fc.POSITION_FILE,encoding='gb2312')#encoding='utf-8')
            except:
                pass
        df_dict = stock_sql.get_systime()
        print(df_dict)
    else:
        print('持仓数据已经更新，无需更新；上一次更新时间：%s' % systime_dict['pos_update_time'])
    
    is_tdx_uptodate,is_pos_uptodate,is_backtest_uptodate,systime_dict = stock_sql.is_histdata_uptodate()
    if pre_is_tdx_uptodate!=is_tdx_uptodate:
        print('完成历史数据更新！')
    if pre_is_pos_uptodate!=is_pos_uptodate:
        print('完成持仓数据更新！')
    #print( 'is_tdx_uptodate=%s, is_pos_uptodate=%s'% (is_tdx_uptodate,is_pos_uptodate))
    
    
    """
    print('Parent process %s.' % os.getpid())
    #update_yh_hist_data(codes_list=[],process_id=0)
    p = Pool()
    for i in range(4):
        p.apply_async(update_yh_hist_data, args=(code_list_dict[i],i,last_date_str,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    
    
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