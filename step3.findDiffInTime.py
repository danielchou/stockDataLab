#------------------------------------------------------
import pandas as pd
import _beowFmt as fm 

import os

rootpath= "D:/project/finlabexportdata"

last1_file_name = fm.getLastFileDate(f"{rootpath}/xq_import", "量比大")  #PROD
last2_file_name = fm.getLast2FileDate(f"{rootpath}/xq_import", "量比大")

df1 = pd.read_csv(f"{rootpath}/xq_import/{last1_file_name}.csv")
df2 = pd.read_csv(f"{rootpath}/xq_import/{last2_file_name}.csv")
list1 = df1.columns.tolist()[:-1]
list2 = df2.columns.tolist()[:-1]

# print(df1)
# print(df2)
diff2 = list(set(list1) - set(list2))    # 找出差異的資料
# print(diff2)

last_date = last1_file_name.split("_")[0]

# 將".TW"移出，使用列表解析
stock_diff = [stock.replace('.TW', '') for stock in diff2]

df_diff = pd.DataFrame(stock_diff, columns = ["stockId"])
# df_diff["time"] = o_nowTime                                                           # PROD
df_diff["time"] = last1_file_name.removesuffix("_量比大").removeprefix("量價型態2024")   # DEV

## 取股票名稱 #--------------------------------------------------
dfStockName = pd.read_csv(f"{rootpath}/paras/股票名稱.csv")
dfStockName.columns = ["stockId", "中文名稱","market"]
dfStockName["stockId"] = dfStockName["stockId"].astype('str')
## -------------------------------------------------------------

dfc = pd.merge(df_diff, dfStockName, left_on="stockId", right_on="stockId")
csv_file_path = f"{rootpath}/xq_turnover/{last_date}_turnover.csv"

if not os.path.exists(csv_file_path) or os.path.getsize(csv_file_path) == 0:
  df_combined = pd.DataFrame(columns=['stockId', '中文名稱', 'time']).astype({'stockId': int, '中文名稱': str, 'time': str})
else:
  df_combined = pd.read_csv(csv_file_path, sep='\t')


df_combined2 = pd.concat([dfc, df_combined], ignore_index=True)
df_combined3 = df_combined2.drop_duplicates(subset=['stockId', '中文名稱']).sort_values(by=['time','stockId'], ascending=False)
df_combined3 = df_combined3[['time', 'stockId', '中文名稱']]

print(df_combined3)
df_combined3.to_csv(csv_file_path, index=False, sep='\t')

# 每天只要匯入同一個檔案就好
ss= ""
df4 = df_combined3["stockId"].tolist()
for d in df4:
  ss += f"{d}.TW,"
fm.write_LogFile(f"{rootpath}/xq_import_today/{last_date}_量比大.csv", ss)


# print(f"?? {last_date}")
js_file_path = f"{rootpath}/data/json/turnover_{last_date}.json"

from datetime import datetime

# 定義轉換函數
def format_time(time_str):
    time_obj = datetime.strptime(time_str, "%Y%m%d_%H%M")
    return time_obj.strftime("%H:%M")

# 將轉換函數應用到時間欄位
df_combined3['time'] = df_combined3['time'].apply(format_time)
df_combined3.rename(columns={'stockId': 'id'}, inplace=True)

print(df_combined3)
with open(js_file_path, 'w') as js_file:
    js_file.write('var jsonData = ')
df_combined3.to_json(js_file_path, orient='records', lines=False, default_handler=None)

print(f'DataFrame已写入到JavaScript文件: {js_file_path}')