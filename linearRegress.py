# -*- coding:utf-8 -*-
# Required Packages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model

# Function to get data
def get_data(data_df, count=20,column='close'):
    li=data_df.index.values.tolist()
    #print(type(data.index))
    #print(type(data['change']))
    data_df['X']=pd.core.series.Series(li,index=data_df.index)
    data = data_df.tail(count)
    #print(data)
    X_parameter = []
    Y_parameter = []
    for single_square_feet ,single_price_value in zip(data['X'],data[column]):
        X_parameter.append([float(single_square_feet)])
        Y_parameter.append(float(single_price_value))
    min_X = X_parameter[0][0]
    for i in range(0,len(X_parameter)):
        X_parameter[i][0] = X_parameter[i][0] - min_X + 1
    next_X = X_parameter[-1][0] + 1
    return X_parameter,Y_parameter,next_X
 
 # Function for Fitting our data to Linear model
def linear_model_main(X_parameters,Y_parameters,predict_value):
    # Create linear regression object
    regr = linear_model.LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    predict_outcome = regr.predict(predict_value)
    predictions = dict()
    predictions['intercept'] = round(regr.intercept_,6)#.tolist()[0]
    predictions['coefficient'] = round(regr.coef_.tolist()[0],6)
    predictions['predicted_value'] = round(predict_outcome.tolist()[0],6)
    return predictions
 
# Function to show the resutls of linear fit model
def show_linear_line(X_parameters,Y_parameters):
    # Create linear regression object
    regr = linear_model.LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    plt.scatter(X_parameters,Y_parameters,color='blue')
    plt.plot(X_parameters,regr.predict(X_parameters),color='red',linewidth=4)
    plt.xticks(())
    plt.yticks(())
    plt.show()

def get_linear_result(data, count=30,col='close'):
    X,Y,next_X = get_data(data, count=30,column= col)
    result = linear_model_main(X,Y,next_X)
    result['uniform'] = round(result['coefficient']/(sum(Y)/len(Y)),6)
    print('----%s--------' % col)
    print(result)
    show_linear_line(X,Y)
    return result

def get_all_ma_linear(data, count=30):
    columns = ['close', 'ma5','ma10', 'ma20','ma30', 'ma60','ma120','ma250']
    all_result = {}
    for col in columns:
        result = get_linear_result(data, count,col)
        all_result[col] = result
    return all_result

def linear_test():
    file_name = 'C:/Users/Administrator/pytrade/temp/000525.csv'
    data = pd.read_csv(file_name)
    count = 30
    all_result = get_all_ma_linear(data, count)
    print('all_result=', all_result)

def linear_test0():
    columns = ['close', 'ma10', 'ma30', 'ma60','ma120']
    file = 'C:/Users/Administrator/pytrade/temp/002060.csv'
    for col in columns:
        data = pd.read_csv(file_name)
        X,Y,next_X = get_data(data, count=30,column= col)#'stock_300162.csv')
        #print(type(X))
        print(X)
        print(Y)
        """
        TRADE_FEE_PER_1W=16.23#16.23RMB fee to complete PER 10000 trade(buy&sell) if total trade amount great then 16600 RMB
        TRADE_FEE_1W=20.20#20.20RMB fee to complete 10000 trade(buy&sell)
        TRADE_FEE_8000=18.20#18.2RMB fee to complete 8000 trade(buy&sell)
        TRADE_FEE_5000=15.20#15.2RMB fee to complete 5000 trade(buy&sell)
        TRADE_FEE_3000=13.20#13.2RMB fee to complete 3000 trade(buy&sell)
        X = [[3000],[5000],[8000],[10000],[16600]]
        Y = [13.2,15.2,18.2,20.2,27.0]
        print(X)
        """
        #predictvalue = X[-1][-1]+1
        predictvalue = next_X#7500
        result = linear_model_main(X,Y,predictvalue)
        print('----%s--------' % col)
        print("Intercept value " , result['intercept'])
        print("coefficient" , result['coefficient'])
        print("Predicted value: ",result['predicted_value'])
        print("coefficient1 value: ",result['coefficient']/(sum(Y)/len(Y)))
        show_linear_line(X,Y)
    
    #Y = X * result['coefficient'] +  result['intercept']
linear_test()