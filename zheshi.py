# -*- coding:utf-8 -*-

def get_index():
    index_postion =0.8
    delta_position = -0.2
    category_data = []
    if index_postion>=0.6:
        lanchou = 0.2
        chengzhang = 0.2
        dapan = 0
        houyue = (1-lanchou-chengzhang-dapan) 
        if delta_position<0 and huoyue >0.3:
            huoyue = huoyue + delta_position/0.1*0.05
            dapan = (1-lanchou-chengzhang-huoyue) 
    elif index_postion>0.3:
        lanchou = 0.2
        chengzhang = 0.2
        dapan = 0.2
        houyue = (1-lanchou-chengzhang-dapan) 
        if delta_position<0 and huoyue >0.2:
            huoyue = huoyue + delta_position/0.1*0.05
            dapan = (1-lanchou-chengzhang-huoyue) 
    else:
        lanchou = 0.2
        houyue = 0.0
        dapan = 0.3
        chengzhang = 0.0
    return

def update_db_category():
    return