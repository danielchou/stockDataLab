# 找出提早公布月營收資料的股票
import os
import finlab
finlab.login(open("config.txt", "r").read())

from finlab import data
import _beowFmt as fm 
import pandas as pd

# pd.set_option('display.expand_frame_repr', False)

df = data.get('monthly_revenue:當月營收')
dfm = df.tail(1).to_period('M')

not_nan_columns = dfm.columns[dfm.notna().all()]

print(not_nan_columns)
ss, local_file_path = "", f"D:/project/stockDataLab/data/json/monthlyRevenue.json"

# 刪除文件（如果存在）
if os.path.exists(local_file_path):
    os.remove(local_file_path)

for c in not_nan_columns:
    ss += f'{c},'
fm.write_LogFile(f"data/json/monthlyRevenue.json", f"[{ss[:-1]}]")

# 等待文件生成完成
while not os.path.exists(local_file_path):
    time.sleep(1)  # 每秒檢查一次，可以根據實際情況調整等待時間

fm.FtpFile(local_file_path, 'static/monthlyRevenue.json')