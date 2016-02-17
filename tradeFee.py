# -*- coding:utf-8 -*-

STAMP_TAX_SELL=0.001 #sell only
SURVEILLANT_FEE=0.0002 #buy and sell,证券监管费
TRADE_HANDLE_FEE_A=0.000487    #buy and sell，沪深交易所，交易经手费
TRADE_TRANSFER_FEE_A=0.0002    #buy and sell, 中国结算公司，交易过户费
TRADE_FEE_B=0.000001    #buy and sell
TRADE_FEE_FUND=0.0000975    #buy and sell
TRADE_FEE_QUANZHENG=0.000045    #buy and sell
TRANSFER_FEE_SH=0.001  #buy and sell, 1.0/1000 share
TRANSFER_FEE_FUND=0.001 #buy and sell, 1.0/1000 share
COMMISSION_YH=0.0003    #buy and sell
COMMISSION_MIN=5.0


def get_commisson_fee(trade_num,stock_price):
    """
    :param trade_num: int type, num of stock
    :param stock_price: float type
    :return: float, stock commission fee
    """
    return max(round(trade_num*stock_price*COMMISSION_YH,2),COMMISSION_MIN)

def get_transfer_fee(trade_num,stock_symbol):
    """
    :param trade_num: int type, num of stock
    :param stock_symbol: str type.
    :return: float, stock commission fee
    """
    transfer_fee=0.0
    if stock_symbol>'600000':
        transfer_fee=max(1.0,round(trade_num*TRANSFER_FEE_SH,2))
    return transfer_fee

def get_all_trade_fee(trade_num,stock_price,stock_symbol,trade_type='buy'):
    """
    :param trade_num: int type, num of stock
    :param stock_price: float type
    :param stock_symbol: str type.
    :return: float, all trade fee
    """
    commission_fee=get_commisson_fee(trade_num, stock_price)
    transfer_fee=get_transfer_fee(trade_num, stock_symbol)
    stamp_tax=0.0
    if trade_type=='sell':
        stamp_tax=STAMP_TAX_SELL*trade_num*stock_price
        
    trade_fee=round((TRADE_HANDLE_FEE_A+TRADE_TRANSFER_FEE_A+SURVEILLANT_FEE)*trade_num*stock_price,3)
    fee_total=round(commission_fee+transfer_fee+stamp_tax+trade_fee,2)
    print(commission_fee,transfer_fee,stamp_tax,trade_fee)
    #print(fee_total,trade_num*stock_price)
    fee_rate=round(fee_total/(trade_num*stock_price),4)
    print('fee_total=',fee_total)
    print('fee_rate=',fee_rate)
    return fee_total

def get_saving_share(stock_price,stock_symbol):
    """
    :param trade_num: int type, num of stock
    :param stock_price: float type
    :param stock_symbol: str type.
    :return: float, all trade fee
    """
    effective_share=int((COMMISSION_MIN/COMMISSION_YH/stock_price/100))*100
    print('effective_share=',effective_share)
    return effective_share

def test():
    get_all_trade_fee(1000, 23.0, '600002', 'sell')
    
    effective_share=get_saving_share(23, '600002')
    get_all_trade_fee(700, 23.0, '600002', 'sell')
    
    
test()