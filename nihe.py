import numpy as np
from scipy.optimize import leastsq
import pylab as pl

def duoxiangshi(x,y,n):
    """多项式拟合
    x: list, x轴数列
    y: list, y轴数值
    n: int, 多项式自由度，即最高次方数
    """
    x_max = max(x)
    y_max = max(y)
    y_min = min(y)
    x = np.array(x)
    y = np.array(y)
    z = np.polyfit(x, y, n)
    #print('z=',z)
    p = np.poly1d(z)
    #x1 = 6.0
    y1 = p(len(y)+1)
    #print('y1=',y1)
    """
    y2 = p(y1+1)
    print('y2=',y2)
    
    y3 = p(y2+1)
    print('y3=',y3)
    
    z1 = np.polyfit(x, y, 3)
    p1 = np.poly1d(z1)
    
    z2 = np.polyfit(x, y, 10)
    p2 = np.poly1d(z2)
    pl.plot(x, y, 'b^-', label='Origin Line')
    pl.plot(x, p1(x), 'gv--', label='Poly Fitting Line(deg=3)')
    pl.plot(x, p2(x), 'r*', label='Poly Fitting Line(deg=6)')
    pl.axis([0, x_max+1, y_min-2, y_max+2])
    pl.legend()# Save figure
    pl.savefig('scipy10.png', dpi=96)
    """
    
    return p,y1

def get_nihe_num(x,y):
    """
    多项式预测值平滑
    """
    var_err_std = 10000.0
    #var_err_std_dict = {}
    varerr_list = []
    y_pridict = []
    yn = y[-1]
    for i in range(1,11):
        p,y1 = duoxiangshi(x,y,i)
        var_err_std = round(np.sqrt(sum((p(x)-y)*(p(x)-y))/len(y)),2)
        if y1<yn*0.9 or y1>yn*1.1:
            #print('invalid %s' % i)
            pass
        else:
            print('y1_%s = %s， err=%s ' %(i,y1,var_err_std))
            y_pridict.append(y1)
            varerr_list.append(var_err_std)
            #var_err_std_dict[i] = var_err_std
    varerr_list.remove(max(varerr_list))
    varerr_list.remove(min(varerr_list))
    avrg_err = sum(varerr_list)/len(varerr_list)
    y_pridict.remove(max(y_pridict))
    y_pridict.remove(min(y_pridict))
    avrg_y_pridict = sum(y_pridict)/len(y_pridict)
    return avrg_y_pridict,avrg_err


y=[15.09,14.77,14.84,15.24,15.71,15.71,15.78,15.61,15.09,15.08,14.93,14.83,15.02,15.27,15.12,15.22,15.68,15.40,
   14.80,14.93,15.39,15.62,15.37,15.98,16.15,15.74,15.73,16.38,16.30,16.40,16.11]

x= range(len(y))

avrg_y_pridict,avrg_err = get_nihe_num(x, y)
print(avrg_y_pridict,avrg_err)
"""
#16.8282089324 0.285714285714
p = duoxiangshi(x,y,4)

print('p=',p)
#py=p(x)
#print('py=',(py-y))
#val_err = (py-y)*(py-y)  #误差
var_err_std = np.sqrt(sum((p(x)-y)*(p(x)-y))/len(y))
#print('val_err=',val_err)
print('var_err_std=',var_err_std)
"""

#y1 = p(x)