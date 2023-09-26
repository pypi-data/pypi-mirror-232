"""
# File       : get_train_data.py
# Time       ：2023/9/25 17:00
# Author     ：xuewei zhang
# Email      ：jingmu_predict@qq.com
# version    ：python 3.8
# Description：
1. 根据传入的数据,生成训练数据,并保证训练数据的连续性
1. Generate training data based on the incoming data, and ensure the continuity of the training data

# Attention:
传入的数据必须指定时间列(或其他顺序列)
You must specify the time column (or other sequential column) of the incoming data
传入的数据必须已按顺序排列好
The incoming data must be sorted in order
"""
import numpy as np
import pandas as pd
from datetime import timedelta

from typing import List, Tuple


class SplitTimeSerialData:
    断点: np.ndarray  # 断点序号,即数据连续位置的最后一行行号

    def __init__(self, data: pd.DataFrame, column_timestamp='timestamp', gap=timedelta(minutes=2)):
        self.data = data
        self.column_timestamp = column_timestamp
        self.gap = gap
        # 检查数据是否连续
        self.断点 = self.查找断点(data, column_timestamp, gap)

    @staticmethod
    def 查找断点(_df: pd.DataFrame, 时间栏='收盘时间', gap=timedelta(minutes=2)) -> np.ndarray:
        _df[时间栏] = pd.to_datetime(_df[时间栏])
        # cal diff
        _df['diff'] = _df['收盘时间'].diff()
        # 断点序号
        断点序号 = _df[_df['diff'] > gap].index.to_numpy()
        return 断点序号

    def 数据划分_避开断点(self, input长度: int, output长度: int, step=1) -> List[Tuple[int, int]]:
        """
        生成训练数据
        :param input长度: 输入数据长度
        :param output长度: 输出数据长度,
        :param step: 步长
        :return:训练数据序号表
        """
        训练数据序号表 = []
        # 一条数据链的长度
        链长度 = input长度 + output长度
        # 数据总长度
        数据总长度 = len(self.data)
        # 生成训练数据序号表,即每条数据链的起始位置,如果该数据链横跨断点位置,则不生成该数据链
        for i in range(0, 数据总长度 - 链长度 + 1, step):
            start, end = i, i + 链长度
            # 如果该数据链横跨断点位置,则不生成该数据链: 如果横跨断点,则值中包含-1,否则不包含-1
            是否横跨断点 = np.divide((start - self.断点), np.abs(start - self.断点)) * \
                           np.divide((end - self.断点), np.abs(end - self.断点))
            # np累乘
            是否横跨断点 = np.prod(是否横跨断点)
            if 是否横跨断点 == -1:
                print(f"数据链横跨断点,20不生成该数据链: {start} - {end}")
            else:
                训练数据序号表.append((start, end))

        return 训练数据序号表


if __name__ == '__main__':
    csv_path = "/Volumes/AI_1505056/量化交易/币安_K线数据/BTCUSDT-1m-201909-202308.csv"
    dfx = pd.read_csv(csv_path)

    x = SplitTimeSerialData(dfx, column_timestamp='收盘时间', gap=timedelta(minutes=2))
    print(x.断点)
    xx = x.数据划分_避开断点(input长度=100, output长度=100, step=1)
    print(len(xx))
