# -*- coding:utf-8 -*-

stocks = ['603288','002236']

price = 1.0

m_boll = 1.5
h_boll = 2.5
l_boll = 0.5
delta = 0.02
is_from_high = True
count_up_h_boll = 0
count_down_l_boll = 0
count_up_m_boll = 0
count_down_m_boll = 0

if price > h_boll *(1-delta):
    print('sell all')
    count_up_h_boll =  count_up_h_boll + 1
    count_down_l_boll = 0
    count_down_m_boll = 0
elif price < l_boll * (1+delta):
    print('buy all')
    count_down_l_boll = count_down_l_boll + 1
    count_up_h_boll = 0
    count_up_m_boll = 0
elif price > m_boll *(1-2*delta) and price < m_boll *(1+ 2*delta):
    if count_up_h_boll>0:
        print('buy half')
        count_down_m_boll = count_down_m_boll + 1
        count_up_h_boll = 0
    if count_down_l_boll >0:
        print('sell half')
        count_up_m_boll = count_up_m_boll + 1
        count_down_l_boll = 0
else:
    print('hold and watch')
    if price >= m_boll *(1+ 2*delta):
        print('high wave')
    elif price < m_boll *(1-2*delta):
        print('low wave')
    else:
        pass
        
        