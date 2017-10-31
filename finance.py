import tushare as ts
import datetime


def get_hist_profit_data(start_years=2014,quater=4):
    year = start_years
    end_year = datetime.datetime.now().year
    all_hist_profit = None
    while year<end_year:
        profit = ts.get_profit_data(year,quater)
        profit['quater'] = '%sQ%s' % (year,quater)
        if year==start_years:
            all_hist_profit =profit
        else:
            all_hist_profit = all_hist_profit.append(profit)
        year = year + 1
    all_hist_profit.to_csv('all_hist_profit.csv')    
    return all_hist_profit
all_hist_profit = get_hist_profit_data()
"""
basic_df = ts.get_stock_basics()
basic_df = basic_df.sort_index(axis=0, by='totalAssets', ascending=False)
#print(basic_df)
#profit = ts.get_profit_data(2017,2)
#print(profit)
#ts.get_profit_statement()

today_df = ts.get_today_all()
count = int(len(today_df)*0.1)
#print(today_df)
today_df = today_df[(today_df['per']>0) & (today_df['high']>0)]
today_df_top_cap = today_df.sort_index(axis=0, by='mktcap', ascending=False)
today_df_top_per = today_df.sort_index(axis=0, by='per', ascending=False)
#today_df_top_per = today_df_top_per[today_df_top_per['per']>0&today_df_top_per['high']>0]
print(today_df_top_cap.head(count))
print(today_df_top_per.tail(count))


"""