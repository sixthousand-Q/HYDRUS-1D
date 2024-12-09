# -*-coding:utf-8-*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# pd.options.display.max_columns = 999
# open files
BF_collect = open('BF-collect.txt', 'r')
WC_collect = open('Water Content-collect.txt', 'r')
BF_measured = open('A_BF_measured.csv', 'r')
WC_measured = open('A_WC_measured.csv', 'r')
BF_simulated = open('A_BF_simulated.csv', 'w')
WC_simulated = open('A_WC_simulated.csv', 'w')

# copy BF file
title_BF = BF_collect.readline()
BF_simulated.write(title_BF)
for line_BF in BF_collect.readlines():
    if line_BF[0] != 'K':
        BF_simulated.writelines(line_BF)
# print('line type', type(line_BF))

# copy WC file
title_WC = WC_collect.readline()
WC_simulated.write(title_WC)
for line_WC in WC_collect.readlines():
    if line_WC[0] != 'K':
        WC_simulated.writelines(line_WC)

BF_collect.close()
WC_collect.close()
BF_measured.close()
WC_measured.close()
BF_simulated.close()
WC_simulated.close()

# deal with BF
BF_simulated = pd.read_csv('A_BF_simulated.csv')
BF_measured = pd.read_csv('A_BF_measured.csv', dtype=float)
BF_ERROR = BF_simulated.merge(BF_measured, on='time', how='left')  # match
BF_ERROR['bot_error_sqr'] = (BF_ERROR['vBot'] - BF_ERROR['vbot']) ** 2
BF_ERROR.dropna(axis=0, how='any', inplace=True)  # inplace,whether or not to change the original file.
BF_ERROR.reset_index(inplace=True)
BF_ERROR_sum = BF_ERROR.groupby(by=['Ks', 'alpha'])['bot_error_sqr'].sum().round(2)
# print(BF_ERROR.head(90))
# print(BF_ERROR_sum.head(30))
BF_ERROR_sum.to_csv('BF_ERROR_sum.csv', sep=',', header=True)

# deal with WC
WC_simulated = pd.read_csv('A_WC_simulated.csv', dtype=float)
WC_measured = pd.read_csv('A_WC_measured.csv', dtype=float)
WC_ERROR = WC_simulated.merge(WC_measured, on='time', suffixes=['_S', '_M'], how='left')
WC_ERROR.dropna(axis=0, how='any', inplace=True)
temp_WC_ERROR = WC_ERROR.diff(periods=11, axis=1)
temp_WC_ERROR.dropna(axis=1, inplace=True)
temp_WC_ERROR.drop(['Node11', 'Node101_S', 'Node121_S', 'Node141'], axis=1, inplace=True)
temp_WC_ERROR['wc_error_sum'] = temp_WC_ERROR.apply(lambda x: (x ** 2).sum(), axis=1)
WC_ERROR = WC_ERROR.join(temp_WC_ERROR['wc_error_sum'])
WC_ERROR_sum = WC_ERROR.groupby(by=['Ks', 'alpha'])['wc_error_sum'].sum().round(5)
WC_ERROR_sum.to_csv('WC_ERROR_sum.csv', sep=',', header=True)


# print(WC_ERROR.head(30))
# print(WC_ERROR.loc[24])
# print(WC_ERROR_sum.head(10))
# print(temp_WC_ERROR.head())
# print(temp_WC_ERROR.loc[35])

# sum of weighted squared errors (WC+BF)

def error_surface():
    global weight_BF
    global weight_WC
    global n_samples
    BF_ERROR_sum = pd.read_csv('BF_ERROR_sum.csv')
    WC_ERROR_sum = pd.read_csv('WC_ERROR_sum.csv')
    ERROR_SURFACE = BF_ERROR_sum.join(WC_ERROR_sum['wc_error_sum'])
    # ERROR_SURFACE['RMSE'] = (ERROR_SURFACE['bot_error_sqr'] * (weight_BF ** 2) + ERROR_SURFACE['wc_error_sum'] * (
    #         weight_WC ** 2)) / (n_samples - 1)  #  wrong function
    ERROR_SURFACE['RMSE'] = ((ERROR_SURFACE['bot_error_sqr'] * weight_BF + ERROR_SURFACE['wc_error_sum'] *
                              weight_WC) / (n_samples - 2)) ** 0.5  # modified
    # ERROR_SURFACE.round(5)
    ERROR_SURFACE.drop(['bot_error_sqr', 'wc_error_sum'], axis=1, inplace=True)
    ERROR_SURFACE.to_csv('A_ERROR_SURFACE_alpha_Ks.csv', index=None, float_format='%.5f')
    # print(ERROR_SURFACE.loc[100:130])

    # seek the minim values
    id_RMSE_min = ERROR_SURFACE['RMSE'].idxmin()
    print(id_RMSE_min)
    print(ERROR_SURFACE.iloc[id_RMSE_min])


weight_BF = 0.36643
weight_WC = 5.317474
n_samples = 211
error_surface()
