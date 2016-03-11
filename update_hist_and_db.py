# -*- coding:utf-8 -*-
from pdSql import *
from fileOperation import *

if __name__ == '__main__': 
    #removeFileInFirstDir(RAW_HIST_DIR)
    #removeFileInFirstDir(HIST_DIR)
    #export history file
    codes=get_all_code(RAW_HIST_DIR)
    #codes=['000987','000060','600750','600979','000875','600103','002678']
    #update_hist_data_tosql(codes)
    update_all_hist_data(codes,update_db=True)