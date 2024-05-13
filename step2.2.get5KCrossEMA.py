# %%
#前置作業準備，只要一次!!
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json
import _beowFmt as fm
import _beowSet as bs
import time

from finlab import data
import os
from io import StringIO

rootpath= "D:/project/finlabexportdata/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
}

# r3 = requests.get("https://www.wantgoo.com/investrue/all-alive", headers = headers).content
# soup = BeautifulSoup(r3, "html.parser")
# rr3 = soup.prettify()
# dfn = pd.read_json(rr3)
# dfn = dfn[(dfn["id"]>="1101") & (dfn["id"]<="9999") & (dfn["id"].str.len() == 4)]
# dfn = dfn.drop(columns=['type','country','url', 'industries'])
# dfn["id"] = dfn["id"].astype("string")

## 取股票名稱 #-----------------------------------------------------------------
dfStockName = pd.read_csv(f"{rootpath}/paras/股票名稱.csv")
dfStockName.columns = ["id", "name","market"]
dfStockName["id"] = dfStockName["id"].astype('str')

## 開始抓即股價資料 ---------------------------------------------------------------------------------
r = requests.get("https://www.wantgoo.com/investrue/all-quote-info", headers = headers).content
soup = BeautifulSoup(r, "html.parser")
rr = soup.prettify()
df = pd.read_json(StringIO(rr))
df = df.drop(columns=['tradeDate', 'time','millionAmount'])
df["id"] = df["id"].astype("string")
df = pd.merge(df, dfStockName, left_on="id", right_on="id")  ## 結合股票名稱
df["volume"] = df["volume"].astype("float")
df["amp"] = ((df["close"] - df["previousClose"])/df["previousClose"] * 100).round(2)
df["jump"] = df["open"] - df["previousClose"]
df["jumpRate"] = (df["jump"] / df["open"] * 100).round(2)

## 剔除金融股、興櫃、ETF 等股票
unwanted = ["2809","2867","2880","2881","2882","2883","2884","2885","2886","2887","2888","2889","2890","2891","2892",  "2412","2303","1605","2027","2023","2313"]
df = df[~df["id"].isin(unwanted)]
df = df[(df["id"]>="1101") & (df["id"]<="9999") & (df["id"].str.len() == 4) & (df["market"] != "Emerging")].sort_values("jumpRate", ascending=False)


nowtime = time.localtime()
# 抓取五分K資料寫入到sqllite DB ###
df2 = df.loc[:, ["id","close","open","high","low","volume"]]
df2["dt"] = time.strftime("%Y%m%d %H:%M", nowtime)
df2['volume'] = pd.to_numeric(df['volume'], errors='coerce')

print(df2)
sql_command = '''
    INSERT INTO stockdata (stockId, o, c, h, l, v, dt) VALUES (?, ?, ?, ?, ?, ?, ?)
'''

# 設定分批寫入的數量
batch_size = 1000

# 拆分 DataFrame 並進行批量寫入
for i in range(0, len(df2), batch_size):
    df_batch = df2.iloc[i:i+batch_size]
    rec_array = df_batch.to_records(index=False)
    data_to_insert = [tuple(record) for record in rec_array]

    # 在這裡換成你的實際資料庫寫入函數
    # bs.ExecuteSqllite("D:\\project\\finlabexportdata\\stock.db", sql_command, data_to_insert)

