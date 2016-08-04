# -*- coding:utf-8 -*-
# Required Packages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model

# Function to get data
def get_data(file_name, count=20,column='close'):
    data = pd.read_csv(file_name)
    li=data.index.values.tolist()
    #print(type(data.index))
    #print(type(data['change']))
    data['X']=pd.core.series.Series(li,index=data.index)
    data = data.tail(count)
    print(data)
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
    print(predict_value)
    regr = linear_model.LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    predict_outcome = regr.predict(predict_value)
    predictions = {}
    predictions['intercept'] = regr.intercept_
    predictions['coefficient'] = regr.coef_
    predictions['predicted_value'] = predict_outcome
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
 
def linear_test():
    columns = ['close', 'ma10', 'ma30', 'ma60','ma120']
    file = 'C:/Users/Administrator/pytrade/temp/002060.csv'
    for col in columns:
        X,Y,next_X = get_data(file, count=20,column= col)#'stock_300162.csv')
        print(type(X))
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
        print("Intercept value " , result['intercept'])
        print("coefficient" , result['coefficient'])
        print("Predicted value: ",result['predicted_value'])
        show_linear_line(X,Y)
    
    #Y = X * result['coefficient'] +  result['intercept']
linear_test()