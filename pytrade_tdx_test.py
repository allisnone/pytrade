# -*- encoding: utf8 -*-

from pytrade_tdx import OperationTdx

if __name__ == '__main__':
    #time.sleep(60)
    debug = True
    op_tdx = OperationTdx(debug)
    op_tdx.getMoney()
    pre_position = op_tdx.getPosition()
    print('pre_position=',pre_position)
    pre_position = op_tdx.getPositionDict() 
    code = '601166'
    direction = 'B'
    quantity = 100
    actual_price = 16.24
    limit_price = [17.86,15.04]
    #op_tdx.order(code, direction, quantity,actual_price,limit_price)
    #op_tdx.order(code='300431', direction='B', quantity=300, actual_price=60.06)
    cur_position =  op_tdx.getPosition()
    hold_num,available_to_sell = op_tdx.getCodePosition(code)
    print('available_to_sell=',available_to_sell)
    #op_tdx。getCodePosition(code)
    #op_tdx.getDeal(code,pre_position,cur_position)
    #op_tdx.clickRefreshButton()

    post_position = op_tdx.getPositionDict() 
    print('post_position=',post_position)
    pos_chg = op_tdx.getPostionChange(pre_position,post_position)
    #print('pos_chg=',pos_chg)
    
    #acc_id,current_combobox_id =op_tdx.get_acc_combobox_id(position_dict={})
    """
    acc_id,current_box_id = op_tdx.get_acc_combobox_id(position_dict={})
    print(acc_id,current_box_id)
    exchange_id = op_tdx.change_account(acc_id,current_box_id,position_dict={})
    print('exchange_id=',exchange_id)
    """
    
    position,avl_sell,monitor_stocks = op_tdx.get_all_position()
    
    print(position)
    print(avl_sell)
    
    
    #op_tdx.getRealtimeQuotation(code='300431')
    
    op_tdx._new_stock_order()