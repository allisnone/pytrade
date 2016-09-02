
import pandas as pd
import matplotlib.pyplot as plt

data_df = pd.read_csv('C:/Users/ezhguox/Documents/2016/personal/temp/regression_test_20160901.csv',encoding='GBK')#'gb2312')
#data_df = data_df[(data_df['fuli_prf']>0.8)]# & (data_df['count']>15)]
#x_data = data_df['success_rate']
x_data = data_df['count']
y_data = data_df['fuli_prf']
plt.title("success rate diagram.") 
plt.xlim(xmax=25,xmin=0)
plt.ylim(ymax=7,ymin=0)
plt.xlabel("x")
plt.ylabel("y")
plt.plot(x_data, y_data,'ro')
plt.show()