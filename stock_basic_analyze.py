# -*- coding:utf-8 -*-
import datetime
import tushare as ts
import pandas as pd
import numpy as np
import low_high33_backtest as lhb
import stock_basic_config as bc

def evaluate_realtime(y=2017,this_quater_num=4):
    """
    当期市值估算: 基于蓝筹的估值，参考工行、茅台、格力电器等
    """
    basic_df = ts.get_stock_basics()
    #df2 = df2.set_index('name')
    basic_df['code'] = basic_df.index
    #print(basic_df.head(5))
    
    #today_df1 = ts.get_today_all()
    """
    today_df= today_df1.set_index('code')
    today_df = today_df[['trade','volume','amount','turnoverratio']]
    """
   
    #temp_df = lhb.get_latest_temp_datas_from_csv()
    temp_df = pd.read_csv(lhb.fc.ALL_TEMP_FILE)
    temp_df['code'] = temp_df['name'].apply(lambda x: lhb.pds.format_code(x))
   
    #temp_df['code'] = temp_df['name']
    today_df1 = temp_df[['code','MA30', 'MA60']]
    print(today_df1.head(5))
    report_df = ts.get_report_data(y,this_quater_num)
    report_df['net_profits'] = (report_df['net_profits']*0.0001).round(2)
    #print(today_df1)
    print(report_df.head(5))
    result = pd.merge(today_df1, report_df, on='code',right_index=True)
    print('result:\n',result)
    
    df4 = pd.merge(basic_df, result, on='code',left_index=True)
    #print('result1:\n',result)
    """
    report_df= report_df.set_index('code')[['roe','net_profits']]
    print(report_df.head(5))
    df1 = pd.concat([basic_df,report_df], axis=1,verify_integrity=False)#, join_axes=[basic_df.index]) #join='inner')
    print('df1: \n',df1)
    df4 = pd.concat([df1,today_df], axis=1)#, join='inner')
    """
    df4=df4.drop_duplicates('code')
    #print(df4)
    df4 = df4.sort_index(axis=0,by='net_profits',ascending=False)
    df4= df4.set_index('code')
    df4['market_value'] = df4['totals']*df4['MA30']#df4['settlement']  #基于30日均价进行估值
    df4['market_evaluate'] = df4['market_value']/df4['net_profits']
    baseline_stocks =['601398','600519','000651','300498','002415','000333','002027','600030','600029','300059','300296','300124','300296']
    #print('df4[df4.index.isin(baseline_stocks)]',df4[df4.index.isin(baseline_stocks)])
    baseline_evaluate = df4[df4.index.isin(baseline_stocks)]['market_evaluate'].mean()
    print('baseline_evaluate=',baseline_evaluate)
    df4['evaluate_rate'] = baseline_evaluate/df4['market_evaluate']
    #print(df4.head(int(len(df4)/4)))
    #df4.to_csv('D:/work/temp1/baisc.csv',encoding='GB18030')
    #df3['trade']
    return df4,baseline_evaluate

def get_report_data(year=2017,quater=3):
    return ts.get_report_date(year,quater).sort_index(axis=0,by='net_profits',ascending=False)

def get_quater_num():
    q = datetime.datetime.now().month
    y = datetime.datetime.now().year
    qt = 4
    if q%3==0:
        qt = q/3
    else:
        qt = int(q/3) + 1
    return y,qt

def get_last_quater():
    y,this_quater_num = get_quater_num()
    if this_quater_num>=2:
        this_quater_num = this_quater_num -1
    else:
        y = y-1
        this_quater_num = 4
    return y,this_quater_num

def report_analyze(y=2017,this_quater_num=4,year_count=3,dir='D:/work/result/'):
    """
    最近几年年报分析
    """
    """
    this_quater_num = get_recent_quater_num()
    y = datetime.datetime.now().year
    if this_quater_num>=1:
        pass
    else:
        y = y-1
        this_quater_num = 4
    #this_quater_num = 3
    y = 2017
    """
    #y,this_quater_num = get_last_quater()
    i = year_count
    
    all_df = pd.DataFrame({})
    prof_list = []
    profit_ratio_list=[]
    roe_list = []
    return_columns = []
    q_name = '%sQ%s' % (y,this_quater_num)
    while i>0:
        if i==year_count:
            profit_df = ts.get_report_data(y,this_quater_num)
            
            profit_df['net_profits'] = profit_df['net_profits'] / this_quater_num * 4.0 *0.0001
            profit_df['roe'] = profit_df['roe'] / this_quater_num * 4.0
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = profit_df
            return_columns = profit_df.columns.values.tolist()
            
        else:
            profit_df = ts.get_report_data(y,4)
            profit_df['net_profits'] = profit_df['net_profits'] *0.0001  #净利润： 万转化位亿
            profit_df['roe'] = profit_df['roe'] 
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = pd.merge(all_df, profit_df, on='code')
        prof_list.append('net_profits%s'%y)
        profit_ratio_list.append('profits_yoy%s'%y)
        roe_list.append('roe%s'% y)
        #profit_df = profit_df.set_index('code')
        #print(profit_df)
        i = i - 1
        y = y - 1
    
    all_df = all_df.drop_duplicates('code')
    #三年利润的平均，亿元
    profit_column = 'net_profits_avrg_%syear'%year_count
    all_df[profit_column] = all_df[prof_list].apply(lambda x: x.sum(), axis=1)/year_count
    #三年利润率的平均，%
    profit_ratio_avrg_column = 'net_profit_ratio_avrg_%syear'%year_count
    all_df[profit_ratio_avrg_column] = all_df[profit_ratio_list].apply(lambda x: x.sum(), axis=1)/year_count
    #buss_df = all_df[business_income_list]
    #三年净资产收益率的平均
    roe_column = 'roe_avrg_%syear'%year_count
    all_df[roe_column] = all_df[roe_list].apply(lambda x: x.sum(), axis=1)/year_count
    #profit_rate_column = 'net_profits_rate_%syear'%year_count
    #all_df[profit_rate_column] = all_df[profit_column] /all_df[income_column]
    
    all_df['min_roe_rate'] = all_df[roe_list].min(1)
    all_df['min_net_profit_ratio'] = all_df[profit_ratio_list].min(1)
    all_df.to_csv(dir +q_name + '.csv',encoding='GB18030')
    ROE_RATE = 8.0
    NET_PROFIT_RATIO = 10
    ROE_RATE_AVRG = 10
    all_df = all_df[(all_df['min_roe_rate']>=ROE_RATE) & (all_df['min_net_profit_ratio']>=NET_PROFIT_RATIO) & (all_df[roe_column]>=ROE_RATE_AVRG)]
    all_df = all_df.sort_values(axis=0,by=profit_ratio_avrg_column,ascending=False)
    #print(all_df['net_profits_avrg'])
    #df.loc['Row_sum'] = df.apply(lambda x: x.sum())
    all_df.to_csv(dir + 'report_best' +q_name + '.csv',encoding='GB18030')
    return_columns = return_columns + [profit_column,profit_ratio_avrg_column,roe_column]    
    return all_df[return_columns]


def profit_analyze(y=2017,this_quater_num=4,year_count=3,dir='D:/work/result/'):
    """
    最近几年盈利能力分析
    """
    #y,this_quater_num = get_last_quater()
    i = year_count
    all_df = pd.DataFrame({})
    prof_list = []
    profit_ratio_list=[]
    business_income_list = []
    ore_ratio_list = []
    return_columns = []
    q_name = '%sQ%s' % (y,this_quater_num)
    last_profit_column = 'net_profits%s'%y
    while i>0:
        if i==year_count:
            profit_df = ts.get_profit_data(y,this_quater_num)
            profit_df['net_profits'] = profit_df['net_profits'] / this_quater_num * 4.0 *0.01
            profit_df['business_income'] = profit_df['business_income'] / this_quater_num * 4.0 *0.01
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            profit_df.rename(columns={'name%s'% y:'name'},inplace=True)
            all_df = profit_df
            return_columns = profit_df.columns.values.tolist()
            """
            report data
            """
            report_df = ts.get_report_data(y,this_quater_num)
        else:
            profit_df = ts.get_profit_data(y,4)
            profit_df['net_profits'] = profit_df['net_profits'] *0.01  #净利润： 百万转化位亿
            profit_df['business_income'] = profit_df['business_income'] *0.01  #净利润： 百万转化位亿
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = pd.merge(all_df, profit_df, on='code')
        prof_list.append('net_profits%s'%y)
        profit_ratio_list.append('net_profit_ratio%s'%y)
        business_income_list.append('business_income%s'% y)
        ore_ratio_list.append('roe%s'% y)
        #profit_df = profit_df.set_index('code')
        #print(profit_df)
        i = i - 1
        y = y - 1
    #prof_df = all_df[prof_list]
    all_df = all_df.drop_duplicates('code')
    #三年利润的平均，亿元
    profit_column = '%s年平均净利润亿'%year_count
    all_df[profit_column] = all_df[prof_list].apply(lambda x: x.sum(), axis=1)/year_count
    #三年利润率的平均，%
    profit_ratio_avrg_column = '%s年平均净利率'%year_count
    #profit_ratio_avrg_column = 'net_profit_ratio_avrg_%syear'%year_count
    all_df[profit_ratio_avrg_column] = all_df[profit_ratio_list].apply(lambda x: x.sum(), axis=1)/year_count
    net_profit_ratio_min_column = '%s年最小净利率' % year_count
    #net_profit_ratio_min_3year
    all_df[net_profit_ratio_min_column] = all_df[profit_ratio_list].apply(lambda x: x.min(), axis=1)
    
    roe_ratio_avrg_column = '%s年平均ROE' % year_count
    all_df[roe_ratio_avrg_column] = all_df[ore_ratio_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    roe_ratio_min_column = '%s年最小ROE' % year_count
    all_df[roe_ratio_min_column] = all_df[ore_ratio_list].apply(lambda x: x.min(), axis=1)
    #三年收入的平均，亿元
    income_column = '%s年平均营业收入亿'%year_count
    #business_income_avrg_3year
    all_df[income_column] = all_df[business_income_list].apply(lambda x: x.sum(), axis=1)/year_count
    #三年平均利润与平均收入的比例，%
    #profit_rate_column = 'net_profits_rate_%syear'%year_count
    profit_rate_column = '%s年净利营收比'%year_count
    all_df[profit_rate_column] = all_df[profit_column] /all_df[income_column]*100
    all_df = all_df.sort_values(axis=0,by=profit_rate_column,ascending=False)
    #print(all_df['net_profits_avrg'])
    #df.loc['Row_sum'] = df.apply(lambda x: x.sum())
    all_df.rename(columns={last_profit_column:'net_profits'},inplace=True)
    all_df.to_csv(dir + 'profit_' +q_name + '.csv',encoding='GB18030')
    filter = (all_df[roe_ratio_min_column]>=bc.ROE_RATION_MIN
              ) & (all_df[profit_rate_column]>=bc.PROFIT_INCOME_RATION
                   ) & (all_df[net_profit_ratio_min_column]>=bc.PROFIT_RATION_MIN)
    filter_df = all_df[filter].sort_values(axis=0,by=roe_ratio_min_column,ascending=False)
    filter_df.to_csv(dir + '近%s年盈利能力-优选'%year_count +q_name + '.csv',encoding='GB18030') 
    #all_df.rename(columns={last_profit_column:'net_profits'},inplace=True)
    return_columns = ['code','name','net_profits'] + [profit_column,income_column,profit_rate_column,profit_ratio_avrg_column,roe_ratio_min_column,roe_ratio_avrg_column]    
    return all_df[return_columns],filter_df[return_columns]

def growth_analyze(y=2017,this_quater_num=4,year_count=3,dir='D:/work/result/'):
    """
    最近几年成长能力分析
    """
    #y,this_quater_num = get_last_quater()
    i = year_count
    all_df = pd.DataFrame({})
    mbrg_list = []#主营增长率
    nprg_list=[]#净利增长率
    business_income_list = []
    ore_ratio_list = []
    return_columns = []
    q_name = '%sQ%s' % (y,this_quater_num)
    while i>0:
        if i==year_count:
            growth_df = ts.get_growth_data(y,this_quater_num)
            
            #growth_df['net_profits'] = growth_df['net_profits'] / this_quater_num * 4.0 *0.01
            #growth_df['business_income'] = growth_df['business_income'] / this_quater_num * 4.0 *0.01
            growth_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            growth_df.rename(columns={'code%s'% y:'code'},inplace=True)
            growth_df.rename(columns={'name%s'% y:'name'},inplace=True)
            all_df = growth_df
            return_columns = growth_df.columns.values.tolist()
            """
            report data
            """
            #report_df = ts.get_report_data(y,this_quater_num)
        else:
            growth_df = ts.get_growth_data(y,4)
            #growth_df['net_profits'] = growth_df['net_profits'] *0.01  #净利润： 百万转化位亿
            #growth_df['business_income'] = growth_df['business_income'] *0.01  #净利润： 百万转化位亿
            growth_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            growth_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = pd.merge(all_df, growth_df, on='code')
        mbrg_list.append('mbrg%s'%y)
        nprg_list.append('nprg%s'%y)
        
        #growth_df = growth_df.set_index('code')
        #print(growth_df)
        i = i - 1
        y = y - 1
    prof_df = all_df[mbrg_list]
    all_df = all_df.drop_duplicates('code')
    
    #三年主营增长率的平均，%
    mbrg_avrg_column = '%s年平均主营增长率'%year_count
    all_df[mbrg_avrg_column] = all_df[mbrg_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    mbrg_min_column = '%s年最小主营增长率' % year_count
    #net_profit_ratio_min_3year
    all_df[mbrg_min_column] = all_df[mbrg_list].apply(lambda x: x.min(), axis=1)
    
    #三年利润率的平均，%
    nprg_avrg_column = '%s年平均净利润增长率'%year_count
    all_df[nprg_avrg_column] = all_df[nprg_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    nprg_min_column = '%s年最小净利润增长率' % year_count
    #net_profit_ratio_min_3year
    all_df[nprg_min_column] = all_df[nprg_list].apply(lambda x: x.min(), axis=1)
    
    sort_growth_column = 'sort_growth_value'
    all_df[sort_growth_column]  = bc.INCOME_GROWTH_WEIGHT * all_df[mbrg_avrg_column] + (1-bc.INCOME_GROWTH_WEIGHT) * all_df[nprg_avrg_column]
    all_df = all_df.sort_values(axis=0,by=sort_growth_column,ascending=False)
    #print(all_df['net_profits_avrg'])
    #df.loc['Row_sum'] = df.apply(lambda x: x.sum())
    all_df.to_csv(dir + 'growth_' +q_name + '.csv',encoding='GB18030')
    filter = (all_df[mbrg_min_column]>=bc.MBRG_MIN) & (all_df[nprg_min_column]>=bc.NPRG_MIN) 
    filter_df = all_df[filter]#.sort_index(axis=0,by=roe_ratio_min_column,ascending=False)
    filter_df.to_csv(dir + '近%s年成长能力-优选'%year_count +q_name + '.csv',encoding='GB18030') 
    new_column = [mbrg_avrg_column,mbrg_min_column,nprg_avrg_column,nprg_min_column] 
    return_columns = ['code', 'name'] + [mbrg_avrg_column,mbrg_min_column,nprg_avrg_column,nprg_min_column,sort_growth_column] 
    return all_df[return_columns],filter_df[return_columns]

def profit_growth_analyze(year=2017,quater=4,year_count=5,dir='D:/work/result/',best_percentage=0):
    """
    最近几年盈利能力、成长能力综合分析： 默认按照条件限定过滤；如果给定best_percentage，比如二八定律，0.2对应20%， 将分别
    按照盈利能力最强的20% 和成长能力最强的20%，综合评判。
    """
    profit_df,profit_filter_df = profit_analyze(year,quater,year_count)
    growth_df,growth_filter_df = growth_analyze(year,quater,year_count)
    df  = pd.merge(profit_df, growth_df, on='code')
    file_name = '近%s年盈利成长按条件优选_%sQ%s'%(year_count,year,quater)
    if best_percentage: #20%
        file_name = '近%s年盈利成长按比例优选_%sQ%s'%(year_count,year,quater)
        total_stock_num = len(profit_df)
        temp_filer_num = int(total_stock_num*best_percentage*1.5)
        final_filer_num = int(total_stock_num*best_percentage)
        #df  = pd.merge(profit_df.head(temp_filer_num), growth_df.head(temp_filer_num), on='code')
        sort_growth_column = 'sort_growth_value'
        sort_column = 'sort_value'
        avrg_ore_col = ''
        min_ore_col = ''
        min_profit_incr_rate_col =''
        min_income_incr_rate_col =''
        for c in df.columns.values.tolist():
            if '平均ROE' in c:
                avrg_ore_col = c
            if '最小ROE' in c:
                min_ore_col = c
            if '最小净利润增长率' in c:
                min_profit_incr_rate_col = c
            if '最小主营增长率' in c:
                min_income_incr_rate_col = c
            if min_profit_incr_rate_col and min_profit_incr_rate_col and  avrg_ore_col and min_ore_col:
                break;
        p_df = profit_df[profit_df[min_ore_col]>1.0].sort_values(axis=0,by=avrg_ore_col,ascending=False).head(temp_filer_num)
        g_df = growth_df[(growth_df[min_income_incr_rate_col]>-5.0) & (growth_df[min_income_incr_rate_col]>=5)]
        d_df = g_df.sort_values(axis=0,by=min_profit_incr_rate_col,ascending=False).head(temp_filer_num)
        df  = pd.merge(p_df,g_df,on='code')
        df[sort_column]  = bc.GROW_WEIGHT * df[sort_growth_column] + (1-bc.GROW_WEIGHT) * df[avrg_ore_col]
        df = df.sort_values(axis=0,by=sort_column,ascending=False)
        df = df.head(final_filer_num)
    del df['name_y']
    df.rename(columns={'name_x':'name'},inplace=True)
    df.to_csv(dir + file_name+ '.csv',encoding='GB18030')
    #gl = df['name'].values.tolist()
    return df



def debtpaying_analyze(y=2017,this_quater_num=4,year_count=3,dir='D:/work/result/'):
    """
    最近几年偿债能力分析
    """
    #y,this_quater_num = get_last_quater()
    i = year_count
    all_df = pd.DataFrame({})
    mbrg_list = []#主营增长率
    nprg_list=[]#净利增长率
    #business_income_list = []
    icratio_list = []
    return_columns = []
    q_name = '%sQ%s' % (y,this_quater_num)
    while i>0:
        if i==year_count:
            growth_df = ts.get_debtpaying_data(y,this_quater_num).replace('--',np.float64(0))
            
            #growth_df['net_profits'] = growth_df['net_profits'] / this_quater_num * 4.0 *0.01
            #growth_df['business_income'] = growth_df['business_income'] / this_quater_num * 4.0 *0.01
            growth_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            growth_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = growth_df
            return_columns = growth_df.columns.values.tolist()
            """
            report data
            """
            #report_df = ts.get_report_data(y,this_quater_num)
        else:
            growth_df = ts.get_debtpaying_data(y,4).replace('--',np.float64(0))
            #growth_df['net_profits'] = growth_df['net_profits'] *0.01  #净利润： 百万转化位亿
            #growth_df['business_income'] = growth_df['business_income'] *0.01  #净利润： 百万转化位亿
            growth_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            growth_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = pd.merge(all_df, growth_df, on='code')
        mbrg_list.append('currentratio%s'%y)
        nprg_list.append('quickratio%s'%y)
        icratio_list.append('icratio%s'%y)
        
        #growth_df = growth_df.set_index('code')
        #print(growth_df)
        i = i - 1
        y = y - 1
    all_df = all_df.drop_duplicates('code')
    
    #三年主营增长率的平均，%
    
    mbrg_avrg_column = '%s年平均流动比率'%year_count
    #temp_df = all_df.replace('--',np.nan)
    #all_df = temp_df.fillna(0)#.astype(float)
    all_df.to_csv(dir + 'debtpaying_' +q_name + '.csv',encoding='GB18030')
    print(all_df[mbrg_list].astype(np.float64))
    all_df[mbrg_list+nprg_list+icratio_list] = all_df[mbrg_list+nprg_list+icratio_list].astype(np.float64)
    #all_df[mbrg_avrg_column] = all_df[mbrg_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    all_df[mbrg_avrg_column] = all_df[mbrg_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    mbrg_min_column = '%s年最小流动比率' % year_count
    #net_profit_ratio_min_3year
    all_df[mbrg_min_column] = all_df[mbrg_list].apply(lambda x: x.min(), axis=1)
    
    #三年利润率的平均，%
    nprg_avrg_column = '%s年平均速动比率'%year_count
    #all_df[nprg_list] = all_df[nprg_list].astype(np.float64)
    all_df[nprg_avrg_column] = all_df[nprg_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    nprg_min_column = '%s年最小速动比率' % year_count
    #net_profit_ratio_min_3year
    all_df[nprg_min_column] = all_df[nprg_list].apply(lambda x: x.min(), axis=1)
    
    
    #三年利润率的平均，%
    icratio_avrg_column = '%s年平均利息支付倍数'%year_count
    #all_df[icratio_list] = all_df[icratio_list].astype(np.float64)
    all_df[icratio_avrg_column] = all_df[icratio_list].apply(lambda x: x.sum(), axis=1)/year_count
    
    icratio_min_column = '%s年最小利息支付倍数' % year_count
    #net_profit_ratio_min_3year
    all_df[icratio_min_column] = all_df[icratio_list].apply(lambda x: x.min(), axis=1)
    
    all_df = all_df.sort_values(axis=0,by=nprg_avrg_column,ascending=False)
    #print(all_df['net_profits_avrg'])
    #df.loc['Row_sum'] = df.apply(lambda x: x.sum())
    all_df.to_csv(dir + 'growth_' +q_name + '.csv',encoding='GB18030')
    filter = (all_df[mbrg_min_column]>=1.5) & (all_df[nprg_min_column]>=1.5) 
    filter_df = all_df[filter]#.sort_index(axis=0,by=roe_ratio_min_column,ascending=False)
    filter_df.to_csv(dir + '%s偿债能力-优选'%year_count +q_name + '.csv',encoding='GB18030') 
    return_columns = return_columns + [mbrg_avrg_column,mbrg_min_column,nprg_avrg_column,nprg_min_column,icratio_avrg_column,icratio_min_column]    
    return filter_df[return_columns]


def profit_and_evaluate(y=2017,this_quater_num=4,year_count=3):
    """
    根据蓝筹股相对净利润进行估值 其他股票
    """
    evaluate_df,baseline_evaluate = evaluate_realtime(y,this_quater_num)
    evaluate_df['code'] = evaluate_df.index
    profit_df,filter_df = profit_analyze(y,this_quater_num,year_count)
    #profit_df=report_analyze(y,this_quater_num)
    profit_column = '%s年平均净利润亿'%year_count
    """
    print('profit_df:', profit_df)
    print(profit_df['code'])
    print(profit_df.dtypes)
    print('evaluate_df:',evaluate_df)
    print(evaluate_df['code'])
    print(evaluate_df.dtypes)
    """
    df = pd.merge(evaluate_df, profit_df, on='code')#,validate='1:1')
    c = ''
    for s in df.columns.values.tolist():
        if 'net_profits' in s:
            c = s
            print('net_profits_c=',c)
            break
        
    
    
    #相对基准蓝筹股的平均估值,基于近几年的利润
    df['market_avrg'] = df[profit_column] * baseline_evaluate
    #相对基准蓝筹股的今年估值,基于今年的预期利润
    print(df)
    df['market_this_year'] = df[c] * baseline_evaluate
    #相对基准蓝筹股的估值比率，越大越便宜，越有高估的潜力
    df['future_evaluate_rate'] = df['market_avrg']/df['market_value']
    #加权平均估值，越大越便宜，越有高估的潜力
    df['final_evaluate_rate'] = df['future_evaluate_rate'] * 0.3 + df['evaluate_rate'] * 0.3 + df['market_this_year']/df['market_value'] * 0.4
    df = df.sort_values(axis=0,by='final_evaluate_rate',ascending=False)
    file_name = 'D:/work/result/baisc%sQ%s_%s.csv'% (y,this_quater_num,int(baseline_evaluate))
    #print(df)
    df.to_csv(file_name,encoding='GB18030')
    return df

def get_middle_value(str_value):
    """
    字符%处理
    """
    values = []
    try:
        if isinstance(str_value, float) or isinstance(str_value, int):
            return str_value
        else:
            values = str_value.split('~')
    except:
        return 0
    v = 0
    if len(values)==2:
        v0 = values[0]
        v1 = values[1]
        if '%' in v0:
            v0 = v0[:-1]
        if '%' in v1:
            v1 = v1[:-1]  
        v = 0.5* (float(v0)+ float(v1))
    elif len(values)==1:
        v0 = values[0]
        if '%' in v0:
            v0 = v0[:-1]
        v = float(v0)
    else:
        pass
    #v = format(v*0.01, '.2%')
    v= round(v * 0.01,2)
    return v



def get_predict_profit(year=2017,quater=4):
    """
    获取年报预测数据
    """
    df = ts.forecast_data(year,quater)
    df=df.drop_duplicates('code')
    print('get_predict')
    print(df)
    df['profit_r'] = df['range'].apply(lambda x: get_middle_value(x))
    df = df.sort_index(axis=0,by='profit_r',ascending=False)
    df.to_csv('D:/work/result/profit_predict_%sQ%s.csv'%(year,quater),encoding='GB18030')
    print(df)
    return df
#"""
y,this_quater_num = get_last_quater()
this_quater_num = 4
#y = 2017
print('y,this_quater_num:',y,this_quater_num)
profit_and_evaluate(y,this_quater_num)
report_analyze(y,this_quater_num)
#"""


profit_growth_analyze(year=y, quater=this_quater_num, year_count=6,best_percentage=0.2)


#np.float64(0)

debtpaying_df = debtpaying_analyze(y, this_quater_num, 3)

get_predict_profit(year=y, quater=this_quater_num)