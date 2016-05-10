# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt


class Stockfilter():
    
    
    def __init__(self):
        pass
    
    def get_all_symbols(self):
        return
    
    def get_all_on_trade_symbols(self):
        return
    
    def filter(self, filter_type, symbols=None):
        target_symbols=[]
        if symbols and isinstance(symbols, str):
            target_symboles = [symbols]
        elif symbols and isinstance(symbols, str):
            target_symboles = symbols
        else:
            target_symboles = self.get_all_symbols()
        stock_hist_anlyse = tds.Stockhistory(code_str='000001',ktype='D')
        for symbol in target_symboles:
            pass    
        
        return