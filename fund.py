# -*- coding:utf-8 -*-

price_dict={'000001':4.5,'000002':115.6, '600001':115.0, '200001':210.5,'300001':118.7,'300002':123.4,'300003':117.9}
def get_code_price(code):
    """
    :param code: str type
    :return: float type, price of certain stock
    """
    return price_dict[code]

def buy1_utilization(code,fund_total):
    """
    :param code: str type, stock symbol
    :param fund_total: float type, total available fund 
    :return: fund utilization and num of stock to buy(shou)
    """
    utilization=0.0
    code_price=get_code_price(code)
    if code_price>0:
        num_shou=int(fund_total/code_price/100)
        if num_shou>=1 and fund_total>0:
            utilization=round(num_shou*100*code_price/fund_total,4)
    else:
        pass
    print(code,utilization,num_shou)
    return utilization,num_shou
        
def buy1_multi_choice_utilization(code_list,fund_total):
    """
    :param code_list: list type, several stock symbols
    :param fund_total: float type, total available fund 
    :return:  the max fund utilization and num of stock to buy(shou)
    """
    max_utilization=0.0
    max_utilization_code=''
    max_utilization_num_shou=0
    if isinstance(code_list, list):
        for code in code_list:
            this_utilization,num_shou=buy1_utilization(code, fund_total)
            if this_utilization>max_utilization:
                max_utilization=this_utilization
                max_utilization_code=code
                max_utilization_num_shou=num_shou
            else:
                pass
    else:
        pass
    return max_utilization,max_utilization_code,max_utilization_num_shou

def buyX_multi_choice_utilization(code_list,fund_total):
    #Given multi stock choices, equally buy several stocks with max utilization
    """
    :param code_list: list type, several stock symbols
    :param fund_total: float type, total available fund 
    :return:  
        utilization: float type, the fund utilization
        final_buy_dict: dict type, set of stock can be buy; key: stock symble, value: num of stock to buy(shou)
    """
    utilization=0.0
    potential_buy_dict={}
    final_buy_dict={}
    remain_fund=fund_total
    if isinstance(code_list, list):
        for code in code_list:
            this_utilization,num_shou=buy1_utilization(code, fund_total)
            if num_shou>=1:
                potential_buy_dict[code]=num_shou
            else:
                pass
        valid_codes=potential_buy_dict.keys()
        first_loop=True
        while True:
            sub_fund_total=remain_fund/len(valid_codes)
            filter_num_shou_dict={}
            for code in valid_codes:
                this_utilization,num_shou=buy1_utilization(code, sub_fund_total)
                if num_shou>=1:
                    filter_num_shou_dict[code]=num_shou
                    remain_fund=remain_fund-num_shou*100*get_code_price(code)
                else:
                    pass
            valid_codes=filter_num_shou_dict.keys()
            if valid_codes:
                if first_loop:
                    final_buy_dict=filter_num_shou_dict
                    first_loop=False
                else:
                    for code in valid_codes:
                        final_buy_dict[code]=final_buy_dict[code]+filter_num_shou_dict[code]
            else:
                break
        utilization=round((1-remain_fund/fund_total),4)
    else:
        pass
    return utilization,final_buy_dict


def test():
    fund_total=100000.0
    code='600001'
    #utilization,num_shou=buy1_utilization(code, fund_total)
    code_list=['000001','000002','600001','200001','300002','300003','300001']
    #max_utilization,max_utilization_code,max_utilization_num_shou=buy1_multi_choice_utilization(code_list, fund_total)
    #print(max_utilization_code,max_utilization,max_utilization_num_shou)
    max_utilization,final_buy_dict=buyX_multi_choice_utilization(code_list, fund_total)
    print(max_utilization,final_buy_dict)
    
#test()