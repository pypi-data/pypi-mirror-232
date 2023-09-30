# process serial data for AI training
# 人工智能训练中,对于时间断层数据的处理工具包

- 根据断点,分配数据集,保证训练数据的连续性
- allocate data set according to breakpoints, to ensure the continuity of training data

## code demo

```python
# Attention:
# 传入的数据必须指定时间列(或其他顺序列)
# You must specify the time column (or other sequential column) of the incoming data
# 传入的数据必须已按顺序排列好
# The incoming data must be sorted in order

from datetime import timedelta
from serial_data_handler_zxw import 生成训练数据_避开时间断点, 时间列_三角函数化
import pandas as pd

csv_path = "/Volumes/time_serial_data.csv"
data = pd.read_csv(csv_path)

# specific the time column named '收盘时间' , 
# and set the gap is 2 minutes , 
# it means that if the gap between two adjacent data > 2 minutes, it will be considered as a breakpoint
# 生成训练数据
x = 生成训练数据_避开时间断点(data, column_timestamp='收盘时间', gap=timedelta(minutes=2))
print(x.断点)
训练数据index = x.数据划分_避开断点(input长度=100, output长度=100, step=1)
print(len(训练数据index))

# If your data interval < 1s, please do the corresponding multiplication conversion
# for example: 1ms data, you should multiply by 1000, convert to second-level data
# time column trigonometric function
# 如果您的数据间隔小于1秒,请做相应的乘法转换, 例如: 1毫秒的数据,请乘以1000,转换为秒级数据
# 时间列_三角函数化
data['收盘时间'] = pd.to_datetime(data['收盘时间'])
data['收盘时间'] = 时间列_三角函数化(data['收盘时间'], 周期=timedelta(days=1))
print(data['收盘时间'])
```


python setup.py sdist bdist_wheel
twine upload dist/*

