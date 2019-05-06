import os
from os import path
import pandas as pd
import tushare as ts

BASE_DIR = os.path.dirname(__file__)

# A股股票代码
K_SAND_BOX_CN = ['sz002230', 'sz300104', 'sz300059', 'sh601766', 'sh600085', 'sh600036',
                 'sh600809', 'sz000002', 'sz002594', 'sz002739']
# 港股股票代码
# K_SAND_BOX_HK = ['hk03333', 'hk00700', 'hk02333', 'hk01359', 'hk00656', 'hk03888', 'hk02318']

_rom_dir = path.join(path.dirname(path.abspath(path.realpath(__file__))), '..\\agu')

_stock_code_cn = os.path.join('E:\Test', 'stock_code_CN.csv')
data = pd.read_csv(_stock_code_cn)
ts_code = data['ts_code']



def get_stock_list(stock_list):
    sy_name_dict = {}
    for sy in K_SAND_BOX_CN:
        for code in ts_code:
            s_code = sy[-6:]
            if s_code == code[:6]:
                sy_name = data[data['ts_code'].isin([code])]['name'].values
                sy_name_dict[sy] = sy_name
    return sy_name_dict


# print(path.join(path.dirname(path.abspath(path.realpath(__file__))), '../RomDataBu'))