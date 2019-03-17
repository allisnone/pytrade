from low_high33_backtest import *
from yh_kdatas import get_latest_yh_k_stocks
if __name__ == '__main__':
    #freeze_support()
    #
    #get_chinese_dict = get_chinese_dict()
    #可能重复
    get_latest_yh_k_stocks(write_file_name=fc.ALL_YH_KDATA_FILE)
    #
    back_test_yh_only(given_codes=[],except_stocks=[],mark_insql=True)