# -*- coding:utf-8 -*-
from numpy import save

#SURVEILLANT_FEE=0.0002 #buy and sell,证券监管费
#TRADE_HANDLE_FEE_A=0.000487    #buy and sell，沪深交易所，交易经手费
#TRADE_TRANSFER_FEE_A=0.0002    #buy and sell, 中国结算公司，交易过户费
#TRADE_FEE_B=0.000001    #buy and sell
#TRADE_FEE_FUND=0.0000975    #buy and sell
#TRADE_FEE_QUANZHENG=0.000045    #buy and sell
#TRANSFER_FEE_FUND=0.001 #buy and sell, 1.0/1000 share
def get_commisson_fee(trade_total,COMMISSION_YH=0.000301):#both sell and buy
    """
    :param trade_total: float type
    :return: float, stock commission fee
    """
    #COMMISSION_YH=0.000301    #buy and sell  交易佣金费率
    COMMISSION_MIN=5.0
    return max(round(trade_total*COMMISSION_YH,2),COMMISSION_MIN)

def get_transfer_fee(trade_total,stock_symbol): #both sell and buy
    """
    :param trade_total: float type
    :param stock_symbol: str type.
    :return: float, stock commission fee
    """
    TRANSFER_FEE_SH=0.00002  #buy and sell SH stock
    transfer_fee=0.0
    if stock_symbol>'600000':
        transfer_fee=round(trade_total*TRANSFER_FEE_SH,2)
    return transfer_fee

def get_all_trade_fee(trade_total,stock_symbol,trade_type='buy',yongjin=0.000301):
    """
    :param trade_total: float type
    :param stock_symbol: str type.
    :return: float, all trade fee
    """
    STAMP_TAX_SELL=0.001 #sell only
    #print(trade_type,'',stock_symbol,':',trade_total)
    commission_fee=get_commisson_fee(trade_total,yongjin)
    transfer_fee=get_transfer_fee(trade_total, stock_symbol)
    stamp_tax=0.0
    if trade_type=='sell':
        stamp_tax=STAMP_TAX_SELL*trade_total
    fee_total=round(commission_fee+transfer_fee+stamp_tax,2)
    #print('commission_fee=',commission_fee,'transfer_fee=',transfer_fee,'stamp_tax=',stamp_tax)
    fee_rate=round(fee_total/trade_total,4)
    #print('fee_total=',fee_total)
    #print('fee_rate=',fee_rate)
    if trade_type=='sell':
        pass
        #print('Return cash=',trade_total-fee_total)
    elif trade_type=='buy':
        pass
        #print('Spend cash=', trade_total+fee_total)
    return fee_total

def get_saving_share(stock_price,COMMISSION_YH=0.000301):
    """
    根据佣金率，得出最小经济交易额度
    :param stock_price: float type
    :return: int, share(shou*100)
    """
    #COMMISSION_YH=0.000301    #buy and sell
    COMMISSION_MIN=5.0
    effective_share=(round(COMMISSION_MIN/COMMISSION_YH/stock_price/100)*100)
    saving_amount = stock_price * effective_share
    print('stock_price=%s,effective_share=%s, effevtive_mount=%s' % (stock_price,effective_share,saving_amount))
    return effective_share,saving_amount

def get_trade_feee(amount,yongjin=0.000301):
    print('佣金率=',yongjin)
    #print(effective_share*6.7)
    #get_all_trade_fee(700, 23.0, '600002', 'sell')
    EFFECTIVE_TRADE_FUND=amount
    #EFFECTIVE_TRADE_FUND=EFFECTIVE_TRADE_FUND*2
    fee_sz_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'buy',yongjin)
    fee_sz_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'sell',yongjin)
    
    fee_sh_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'buy',yongjin)
    fee_sh_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'sell',yongjin)
    fee_1w=(fee_sz_b+fee_sz_s+fee_sh_b+fee_sh_s)*0.5/(EFFECTIVE_TRADE_FUND/10000)
    print('买卖%s元,深市佣金总计=%s'%(EFFECTIVE_TRADE_FUND,fee_sz_b+fee_sz_s))
    print('买卖%s元,沪市佣金总计=%s'%(EFFECTIVE_TRADE_FUND,fee_sh_b+fee_sh_s))
    print('平均一万块钱的卖卖双向佣金总计=',fee_1w)
    return fee_1w
get_trade_feee(1000)
EFFECTIVE_TRADE_FUND=16600
EFFECTIVE_TRADE_FEE_RATE_B=0.000301
EFFECTIVE_TRADE_FEE_RATE_S=0.001321
TRADE_FEE_PER_1W=16.23#16.23RMB fee to complete PER 10000 trade(buy&sell) if total trade amount great then 16600 RMB
TRADE_FEE_1W=20.20#20.20RMB fee to complete 10000 trade(buy&sell)
TRADE_FEE_8000=18.20#18.2RMB fee to complete 8000 trade(buy&sell)
TRADE_FEE_5000=15.20#15.2RMB fee to complete 5000 trade(buy&sell)
TRADE_FEE_3000=13.20#13.2RMB fee to complete 3000 trade(buy&sell)
MIN_PROFIT_PRICE_RATE_1w=1.001623
MIN_PROFIT_PRICE_RATE=1.002

TEN_TIMES_THAN_TRADE_FEE_RATE = 1.018
TEN_TIMES_THAN_TRADE_FEE_RATE_1w = 1.022
TEN_TIMES_THAN_TRADE_FEE_RATE_5K = 1.033

def get_approximate_trade_fee(total_buy_amount,yongjin=0.000301):
    """
    :param total_buy_amount: float type
    :return: float, total fee and fee rate(min profit rate) of du-direct (buy & sell)
    """
    TRADE_FEE_PER_1W = get_trade_feee(100000,yongjin)
    effective_share,saving_amount=get_saving_share(10, yongjin)
    trade_fee = 10.0
    min_profit_rate = 1.0016
    ten_time_trade_fee_rate = 1.018
    if total_buy_amount >= saving_amount:
        trade_fee = TRADE_FEE_PER_1W * 0.0001 * total_buy_amount
    else:
        trade_fee = 0.00101 * total_buy_amount + 10.12
        if total_buy_amount>=8000:
            min_profit_rate = 1.0022
            ten_time_trade_fee_rate = 1.021
        elif total_buy_amount>=5000:
            min_profit_rate = 1.0037
            ten_time_trade_fee_rate = 1.031
        else:
            min_profit_rate = 1.0045
            ten_time_trade_fee_rate = 1.051
    trade_fee = round(trade_fee,2)
    return trade_fee, min_profit_rate,ten_time_trade_fee_rate

"""
multiple_num = 10
for total_buy_amount in [100000,50000,30000,20000,10000,8000,5000,3000,2000]:
    trade_fee,min_profit_rate,ten_time_trade_fee_rate = get_approximate_trade_fee(total_buy_amount)
    expect_rate = round((multiple_num+1)*trade_fee/total_buy_amount + 1.0,4)
    print(total_buy_amount,trade_fee,min_profit_rate,expect_rate, round(multiple_num*trade_fee,2))
"""
"""
def test():
    yongjin=0.000301
    yongjin=0.000161

    print('佣金率=',yongjin)
    effective_share,saving_amount=get_saving_share(10, yongjin)
    #print(effective_share*6.7)
    #get_all_trade_fee(700, 23.0, '600002', 'sell')
    EFFECTIVE_TRADE_FUND=1000
    #EFFECTIVE_TRADE_FUND=EFFECTIVE_TRADE_FUND*2
    fee_sz_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'buy',yongjin)
    fee_sz_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'sell',yongjin)
    
    fee_sh_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'buy',yongjin)
    fee_sh_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'sell',yongjin)
    fee_1w=(fee_sz_b+fee_sz_s+fee_sh_b+fee_sh_s)*0.5/(EFFECTIVE_TRADE_FUND/10000)
    print('买卖%s元,深市佣金总计=%s'%(EFFECTIVE_TRADE_FUND,fee_sz_b+fee_sz_s))
    print('买卖%s元,沪市佣金总计=%s'%(EFFECTIVE_TRADE_FUND,fee_sh_b+fee_sh_s))
    print('平均一万块钱的卖卖双向佣金总计=',fee_1w)
    
test()

"""


"""
测试结果：



+++++++++++++++++++++++++++++++++++++++++++万分之1.6的佣金时，各种金额对应费率

佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖100000元,深市佣金总计=132.2
买卖100000元,沪市佣金总计=136.2
平均一万块钱的卖卖双向佣金总计= 13.419999999999998


佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖50000元,深市佣金总计=66.1
买卖50000元,沪市佣金总计=68.1
平均一万块钱的卖卖双向佣金总计= 13.419999999999998



佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖20000元,深市佣金总计=30.0
买卖20000元,沪市佣金总计=30.799999999999997
平均一万块钱的卖卖双向佣金总计= 15.2

佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖15000元,深市佣金总计=25.0
买卖15000元,沪市佣金总计=25.6
平均一万块钱的卖卖双向佣金总计= 16.866666666666667


佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖10000元,深市佣金总计=20.0
买卖10000元,沪市佣金总计=20.4
平均一万块钱的卖卖双向佣金总计= 20.2



佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖5000元,深市佣金总计=15.0
买卖5000元,沪市佣金总计=15.2
平均一万块钱的卖卖双向佣金总计= 30.200000000000003


佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖2500元,深市佣金总计=12.5
买卖2500元,沪市佣金总计=12.6
平均一万块钱的卖卖双向佣金总计= 50.2


佣金率= 0.000161
effective_share=3100, effevtive_mount=31000
买卖1000元,深市佣金总计=11.0
买卖1000元,沪市佣金总计=11.04
平均一万块钱的卖卖双向佣金总计= 110.19999999999999




+++++++++++++++++++++++++++++++++++++++++++万分之3.0的佣金时，各种金额对应费率

佣金率= 0.000301
effective_share=1700, effevtive_mount=17000
买卖100000元,深市佣金总计=160.2
买卖100000元,沪市佣金总计=164.2
平均一万块钱的卖卖双向佣金总计= 16.22


佣金率= 0.000301
effective_share=1700, effevtive_mount=17000
买卖50000元,深市佣金总计=80.1
买卖50000元,沪市佣金总计=82.1
平均一万块钱的卖卖双向佣金总计= 16.22


佣金率= 0.000301
effective_share=1700, effevtive_mount=17000
买卖20000元,深市佣金总计=32.04
买卖20000元,沪市佣金总计=32.84
平均一万块钱的卖卖双向佣金总计= 16.22


佣金率= 0.000301
effective_share=1700, effevtive_mount=17000
买卖15000元,深市佣金总计=25.0
买卖15000元,沪市佣金总计=25.6
平均一万块钱的卖卖双向佣金总计= 16.866666666666667


佣金率= 0.000301
买卖10000元,深市佣金总计=20.0
买卖10000元,沪市佣金总计=20.4
平均一万块钱的卖卖双向佣金总计= 20.2



佣金率= 0.000301
买卖5000元,深市佣金总计=15.0
买卖5000元,沪市佣金总计=15.2
平均一万块钱的卖卖双向佣金总计= 30.200000000000003


佣金率= 0.000301
买卖2500元,深市佣金总计=12.5
买卖2500元,沪市佣金总计=12.6
平均一万块钱的卖卖双向佣金总计= 50.2



佣金率= 0.000301
买卖1000元,深市佣金总计=11.0
买卖1000元,沪市佣金总计=11.04
平均一万块钱的卖卖双向佣金总计= 110.19999999999999






总结：
1. 万分之3.0的佣金时， 每次交易超过17000才划算，总费率大约0.1622% （包括买卖完整一次交易）；
2. 万分之1.6的佣金时， 每次交易超过31000才划算，总费率大约0.1342% （包括买卖完整一次交易）；
3. 每次交易金额超过2万，选择低佣金券商才有优势；低于17000，总费率没有优势。
4. 每次交易金额越低，折算费率越大，大约0.3%，最高达1%;当每次交易大约1万块时，费率大约是千分之二



"""