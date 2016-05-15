# -*- coding:utf-8 -*-

#SURVEILLANT_FEE=0.0002 #buy and sell,证券监管费
#TRADE_HANDLE_FEE_A=0.000487    #buy and sell，沪深交易所，交易经手费
#TRADE_TRANSFER_FEE_A=0.0002    #buy and sell, 中国结算公司，交易过户费
#TRADE_FEE_B=0.000001    #buy and sell
#TRADE_FEE_FUND=0.0000975    #buy and sell
#TRADE_FEE_QUANZHENG=0.000045    #buy and sell
#TRANSFER_FEE_FUND=0.001 #buy and sell, 1.0/1000 share
def get_commisson_fee(trade_total):#both sell and buy
    """
    :param trade_total: float type
    :return: float, stock commission fee
    """
    COMMISSION_YH=0.000301    #buy and sell
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

def get_all_trade_fee(trade_total,stock_symbol,trade_type='buy'):
    """
    :param trade_total: float type
    :param stock_symbol: str type.
    :return: float, all trade fee
    """
    STAMP_TAX_SELL=0.001 #sell only
    print(trade_type,'',stock_symbol,':',trade_total)
    commission_fee=get_commisson_fee(trade_total)
    transfer_fee=get_transfer_fee(trade_total, stock_symbol)
    stamp_tax=0.0
    if trade_type=='sell':
        stamp_tax=STAMP_TAX_SELL*trade_total
    fee_total=round(commission_fee+transfer_fee+stamp_tax,2)
    #print('commission_fee=',commission_fee,'transfer_fee=',transfer_fee,'stamp_tax=',stamp_tax)
    fee_rate=round(fee_total/trade_total,4)
    print('fee_total=',fee_total)
    print('fee_rate=',fee_rate)
    if trade_type=='sell':
        print('Return cash=',trade_total-fee_total)
    elif trade_type=='buy':
        print('Spend cash=', trade_total+fee_total)
    return fee_total

def get_saving_share(stock_price,stock_symbol):
    """
    :param stock_price: float type
    :param stock_symbol: str type.
    :return: int, share(shou*100)
    """
    COMMISSION_YH=0.000301    #buy and sell
    COMMISSION_MIN=5.0
    effective_share=(round(COMMISSION_MIN/COMMISSION_YH/stock_price/100)*100)
    print('effective_share=',effective_share)
    return effective_share

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

def get_approximate_trade_fee(total_buy_amount):
    """
    :param total_buy_amount: float type
    :return: float, total fee and fee rate(min profit rate) of du-direct (buy & sell)
    """
    TRADE_FEE_PER_1W=16.23
    trade_fee = 10.0
    min_profit_rate = 1.0016
    if total_buy_amount >= 16600:
        trade_fee = TRADE_FEE_PER_1W * 0.0001 * total_buy_amount
    else:
        trade_fee = 0.00101 * total_buy_amount + 10.12
        if total_buy_amount>=8000:
            min_profit_rate = 1.0022
        elif total_buy_amount>=5000:
            min_profit_rate = 1.0037
        else:
            min_profit_rate = 1.0045
    trade_fee = round(trade_fee,2)
    return trade_fee, min_profit_rate
"""
multiple_num = 10
for total_buy_amount in [100000,50000,30000,20000,10000,8000,5000,3000,2000]:
    trade_fee,min_profit_rate = get_approximate_trade_fee(total_buy_amount)
    expect_rate = round((multiple_num+1)*trade_fee/total_buy_amount + 1.0,4)
    print(total_buy_amount,trade_fee,min_profit_rate,expect_rate, round(multiple_num*trade_fee,2))

def test():
    trade_num=13.64
    trade_price=1600
    trade_total=trade_num*trade_price
    get_all_trade_fee(trade_total, '000060', 'sell')
    
    trade_num=8.1
    trade_price=100
    trade_total=trade_num*trade_price
    get_all_trade_fee(trade_total, '600979', 'sell')
    
    trade_num=14.25
    trade_price=2000
    trade_total=trade_num*trade_price
    get_all_trade_fee(trade_total, '002461', 'sell')
    
    trade_num=7000
    trade_price=6.41
    trade_total=round(trade_num*trade_price,2)
    get_all_trade_fee(trade_total, '000807', 'buy')
    
    #get_all_trade_fee(trade_total, '000060', 'buy')
    
    effective_share=get_saving_share(6.7, '600002')
    #print(effective_share*6.7)
    #get_all_trade_fee(700, 23.0, '600002', 'sell')
    EFFECTIVE_TRADE_FUND=5000
    #EFFECTIVE_TRADE_FUND=EFFECTIVE_TRADE_FUND*2
    fee_sz_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'buy')
    fee_sz_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '000807', 'sell')
    
    fee_sh_b=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'buy')
    fee_sh_s=get_all_trade_fee(EFFECTIVE_TRADE_FUND, '600807', 'sell')
    fee_1w=(fee_sz_b+fee_sz_s+fee_sh_b+fee_sh_s)*0.5/(EFFECTIVE_TRADE_FUND/10000)
    print(fee_sz_b+fee_sz_s)
    print(fee_sh_b+fee_sh_s)
    print('fee_1w=',fee_1w)
    
test()

"""