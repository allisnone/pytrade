# -*- coding:utf-8 -*-
import datetime
import tushare as ts
import pandas as pd

def evaluate_realtime():
    basic_df = ts.get_stock_basics()
    #df2 = df2.set_index('name')
    basic_df['code'] = basic_df.index
    print(basic_df.head(5))
    today_df1 = ts.get_today_all()
    today_df= today_df1.set_index('code')
    today_df = today_df[['trade','volume','amount','turnoverratio']]
    print(today_df.head(5))
    report_df = ts.get_report_data(2017,3)
    report_df['net_profits'] = (report_df['net_profits']*0.0001).round(2)
    
    result = pd.merge(today_df1, report_df, on='code')
    print('result:\n',result)
    
    df4 = pd.merge(basic_df, result, on='code',left_index=True)
    print('result1:\n',result)
    """
    report_df= report_df.set_index('code')[['roe','net_profits']]
    print(report_df.head(5))
    df1 = pd.concat([basic_df,report_df], axis=1,verify_integrity=False)#, join_axes=[basic_df.index]) #join='inner')
    print('df1: \n',df1)
    df4 = pd.concat([df1,today_df], axis=1)#, join='inner')
    """
    df4=df4.drop_duplicates('code')
    print(df4)
    df4 = df4.sort_index(axis=0,by='net_profits',ascending=False)
    df4= df4.set_index('code')
    df4['market_value'] = df4['totals']*df4['settlement']
    df4['market_evaluate'] = df4['market_value']/df4['net_profits']
    baseline_stocks =['601398','600519','000651','300498','002415']
    print('df4[df4.index.isin(baseline_stocks)]',df4[df4.index.isin(baseline_stocks)])
    baseline_evaluate = df4[df4.index.isin(baseline_stocks)]['market_evaluate'].mean()
    print('baseline_evaluate=',baseline_evaluate)
    df4['evaluate_rate'] =df4['market_evaluate']/baseline_evaluate
    print(df4.head(int(len(df4)/4)))
    df4.to_csv('D:/work/temp1/baisc.csv',encoding='GB18030')
    #df3['trade']

def get_report_data(year=2017,quater=3):
    return ts.get_report_date(year,quater).sort_index(axis=0,by='net_profits',ascending=False)

def get_recent_quater_num():
    q = datetime.datetime.now().month
    if q%3==0:
        return q/3
    else:
        return int(q/3) + 1

def profit_analyze(year_count=3):
    this_quater_num = get_recent_quater_num()
    y = datetime.datetime.now().year
    if this_quater_num>2:
        pass
    else:
        y = y-1
        this_quater_num = 4
    i = year_count
    this_quater_num = 3
    y = 2017
    all_df = pd.DataFrame({})
    prof_list = []
    business_income_list = []
    while i>0:
        if i==year_count:
            profit_df = ts.get_profit_data(y,this_quater_num)
            profit_df['net_profits'] = profit_df['net_profits'] / this_quater_num * 4.0 *0.01
            profit_df['business_income'] = profit_df['business_income'] / this_quater_num * 4.0 *0.01
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = profit_df
            #all_df = profit_df.set_index('code')['name']
            #code_name ='code%s'% y
            #name_stock = 'name%s'%y
            #profit_df.rename(columns={'code%s'% y:'code', 'name%s'%y: 'name'},inplace=True)
            #del profit_df['code%s'%y]
            #del profit_df['name%s'%y]
        else:
            profit_df = ts.get_profit_data(y,4)
            profit_df['net_profits'] = profit_df['net_profits'] *0.01  #净利润： 百万转化位亿
            profit_df['business_income'] = profit_df['business_income'] *0.01  #净利润： 百万转化位亿
            #del profit_df['code%s'%y]
            #del profit_df['name%s'%y]
            profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
            profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
            all_df = pd.merge(all_df, profit_df, on='code')
        prof_list.append('net_profits%s'%y)
        business_income_list.append('business_income%s'% y)
        #profit_df.rename(columns=lambda x:x+'%s'%y, inplace=True)
        #profit_df.rename(columns={'code%s'% y:'code'},inplace=True)
        #del profit_df['code%s'%y]
        #profit_df = profit_df.set_index('code')
        
        #profit_df['code'] = profit_df['code%s'%y]
        #del profit_df['code%s'%y]
        #profit_df = profit_df.set_index('code')
        print(profit_df)
        i = i - 1
        y = y - 1
    prof_df = all_df[prof_list]
    all_df = all_df.drop_duplicates('code')
    all_df['net_profits_avrg'] = prof_df.apply(lambda x: x.sum(), axis=1)/year_count
    buss_df = all_df[business_income_list]
    all_df['business_income_avrg'] = buss_df.apply(lambda x: x.sum(), axis=1)/year_count
    all_df['net_profits_rate'] = all_df['net_profits_avrg'] /all_df['business_income_avrg']
    all_df = all_df.sort_index(axis=0,by='net_profits_avrg',ascending=False)
    #print(all_df['net_profits_avrg'])
    #df.loc['Row_sum'] = df.apply(lambda x: x.sum())
    all_df.to_csv('D:/work/temp1/baisc3.csv',encoding='GB18030')    
    return 


profit_analyze()