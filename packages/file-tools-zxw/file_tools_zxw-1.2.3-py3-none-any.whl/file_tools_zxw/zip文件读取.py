"""
# File       : zip文件读取.py
# Time       ：2023/9/25 15:00
# Author     ：xuewei zhang
# Email      ：jingmu_predict@qq.com
# version    ：python 3.8
# Description：
"""
import zipfile


class ZIP文件_读取:
    def __init__(self, zip_file: str):
        self.__opened_zip = zipfile.ZipFile(zip_file, 'r')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__opened_zip.close()

    def __del__(self):
        self.__opened_zip.close()

    def 所有文件名(self, 文件后缀: str = None):
        # 列出ZIP中的所有文件
        _file_list = self.__opened_zip.namelist()
        # 找到所有以suffix结尾的文件
        if 文件后缀 is not None:
            _csv_filename = [filename for filename in _file_list if filename.endswith(文件后缀)]
        else:
            _csv_filename = _file_list
        return _csv_filename

    def 打开文件(self, zip内的文件名: str):
        return self.__opened_zip.open(zip内的文件名)


if __name__ == '__main__':
    import pandas as pd

    file = "/Volumes/AI_1505056/量化交易/币安_K线数据/BTCUSDT-1m-2019-09.zip"
    with ZIP文件_读取(file) as f:
        n = f.所有文件名(".csv")
        print(n)

        # read csv from bytes
        p = pd.read_csv(f.打开文件(n[0]))
        print(p.head())
