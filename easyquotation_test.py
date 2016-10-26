import easyquotation
from pdSql_common import get_HO_dapan
easy_q = easyquotation.use('qq')

all_q = easy_q.all
da_pan = []
print(all_q['000651'])
for code in list(all_q.keys()):
    liutong_amount =all_q[code]['流通市值']
    total_amount =all_q[code]['总市值']
    if liutong_amount and total_amount:
        if float(total_amount)>1000 or float(liutong_amount)>500:
            da_pan.append(code)
print( 'da_pan=',da_pan)
print(len(da_pan))            
ho_codes = get_HO_dapan(codes = da_pan,ho_rate=0.0026, stock_sql=None)
print(ho_codes)
