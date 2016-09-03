import pandas as pd
import pdSql as pds
import myBackTest as bt

def get_corr_hist_data(ref_index='sh', data_dir="C:/中国银河证券海王星/T0002/export/",column_name='change'):
    index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                     'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
    if ref_index in list(index_symbol_maps.keys()):
        ref_index = index_symbol_maps[ref_index]
    ref_index_file = data_dir + '%s.csv' % ref_index
    ref_data_df = pd.read_csv(ref_index_file,encoding='GBK')#'gb2312')
    ref_data_df[column_name] = ref_data_df['close']/ref_data_df['close'].shift(1)-1
    #sh_data_df = sh_data_df.set_index('date')
    ref_data_df = ref_data_df[['date',column_name]]
    #pch_sh_data_df = pch_sh_data_df.set_index('date')
    #pch_sh_data_df_dates = pch_sh_data_df.index.values.tolist()
    return ref_data_df

def get_corr(ref_hist_df,stock_hist_df, recent_count=12000):
    new_df = pd.merge(ref_hist_df,stock_hist_df,on='date')#left_index=True,right_on='date')#right_index=False) 
    new_df = new_df.fillna(0.000001)
    if new_df.empty:
        return 0.0
    #new_df = pch_sh_data_df.join(pch_stock_data_df,on='date')
    new_df = new_df.set_index('date')
    if len(new_df)>recent_count:
        new_df =new_df.tail(recent_count)
    corr_df = new_df.corr()#new_df['p_change'],new_df['s_p_change'])
    corr_value = corr_df.iloc[0].s_change
    return corr_value

#get_hist_corr(ref_index='sh', stock='601857')
def get_all_corr(ref_stocks=['sh','cyb'],stocks=['601857'],recent=12000):
    all_corr =[]
    for ref_stock in ref_stocks:
        #print('ref_stock=',ref_stock)
        ref_hist_df = get_corr_hist_data(ref_stock)
        if ref_hist_df.empty:
            continue
        corr_dict = {'ref': ref_stock}
        for stock in stocks:
            #print('stock=',stock)
            if ref_stock==stock:
                corr_dict[stock] = 1.0
            else:
                stock_hist_df= get_corr_hist_data(stock,column_name='s_change')
                if stock_hist_df.empty:
                    continue
                corr_value = get_corr(ref_hist_df, stock_hist_df, recent_count=recent)
                corr_dict[stock] = round(corr_value,4)
        #all_corr.append({ref_stock:corr_dict})
        all_corr.append(corr_dict)
          
    print(all_corr)
    column = list(all_corr[0].keys())
    all_corr_df = pd.DataFrame(all_corr,columns=column)
    all_corr_df = all_corr_df.set_index('ref')
    print(all_corr_df)
    return all_corr_df

given_stocks =['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
                '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']

hist_dir='C:/中国银河证券海王星/T0002/export/'
        #print(given_codes,except_stocks)
#all_stop_codes,all_stocks = bt.get_stopped_stocks(hist_dir='C:/中国银河证券海王星/T0002/export/')

all_stocks = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
all_corr_df = get_all_corr(ref_stocks=['sh','cyb']+all_stocks,stocks=all_stocks,recent=1000)
#all_corr_df = get_all_corr(ref_stocks=['sh'],stocks=all_stocks,recent=12000)
all_corr_df.to_csv('./temp/all_corr_df.csv')

"""
ref_hist_df = get_corr_hist_data('sh')
#print(ref_hist_df)
stock_hist_df= get_corr_hist_data('002281',column_name='s_change')
#$stock_hist_df['s_p_change'] = stock_hist_df['p_change']
#del stock_hist_df['p_change']
corr_value = get_corr(ref_hist_df, stock_hist_df)
print('corr_value=',corr_value)
"""
"""
sh_data_df = pd.read_csv('C:/hist/day/temp/sh.csv',encoding='GBK')#'gb2312')
#sh_data_df = sh_data_df.set_index('date')
pch_sh_data_df = sh_data_df[['date','p_change']]
#pch_sh_data_df = pch_sh_data_df.set_index('date')
#pch_sh_data_df_dates = pch_sh_data_df.index.values.tolist()
stock_code = '601857'

stock_data_df = pd.read_csv('C:/hist/day/temp/%s.csv' % stock_code,encoding='GBK')#'gb2312')
stock_data_df['s_p_change'] = stock_data_df['p_change']
#stock_data_df = stock_data_df.set_index('date')


pch_stock_data_df = stock_data_df[['date','s_p_change']]
pch_stock_data_df0 = pch_stock_data_df.set_index('date')
#pch_stock_data_df_dates = pch_stock_data_df.index.values.tolist()
#print(pch_stock_data_df_dates)
#overlap =list(set(pch_stock_data_df_dates) & set(pch_sh_data_df_dates)) 
#print(overlap)
#new_df = pd.merge(pch_sh_data_df,pch_stock_data_df,left_index=True,right_on='date')#right_index=False) 
new_df = pd.merge(pch_sh_data_df,pch_stock_data_df,on='date')#left_index=True,right_on='date')#right_index=False) 
#new_df = pch_sh_data_df.join(pch_stock_data_df,on='date')
new_df = new_df.set_index('date')
new_df =new_df.tail(30)
print(new_df)
corr = new_df.corr()#new_df['p_change'],new_df['s_p_change'])
print(corr)
corr_value = corr.iloc[0].s_p_change
print(corr_value)


#corr = new_df.corrwith(pch_stock_data_df0,0)#new_df['p_change'],new_df['s_p_change'])
#print(corr)
"""
"""
index_symbol_maps = {'sh':'999999','sz':'399001','zxb':'399005','cyb':'399006',
                     'sh50':'000016','sz300':'399007','zx300':'399008','hs300':'000300'}
print(index_symbol_maps.values())


print(pch_sh_data_df)
print(pch_stock_data_df)

new_df = pch_sh_data_df.join(pch_stock_data_df,on='date',rsuffix='date')
print(new_df)
"""
