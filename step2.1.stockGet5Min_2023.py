# %%
#前置作業準備，只要一次!!
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json
import _beowFmt as fm
import _beowSet as bs

from finlab import data
import os
from io import StringIO
from datetime import datetime
import time

rootpath= "D:/project/stockDataLab/"

yesterday = fm.getLastFileDate(f"{rootpath}/volumeData", "ma_")

df5k = pd.read_json(f"{rootpath}paras/mapping5K.json")
dfv = pd.read_csv(f"{rootpath}volumeData/ma_{yesterday}.csv")
dfv["id"] = dfv["id"].astype("string")

### 計算量比參數 ###

def getRate5K():
    localtime = time.localtime()
    nowTime = time.strftime("%H:%M", localtime)
    Rate5k = df5k[(df5k["e"] >= nowTime) & (df5k["b"] <= nowTime)]["w"].values[0]  #五分K量比預估放大參數 
    print(f"目前時間：{nowTime},預估量放大係數:{Rate5k}")
    return Rate5k

## 取股票名稱 #-----------------------------------------------
dfStockName = pd.read_csv(f"{rootpath}/paras/股票名稱.csv")
dfStockName.columns = ["id", "name","market"]
dfStockName["id"] = dfStockName["id"].astype('str')
## ----------------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
}
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

unwanted = ["2809","2880","2881","2882","2883","2884","2885","2886","2887","2888","2889","2890","2891","2892",  "2412","2303","1605","2027","2023","2313"]
df = df[~df["id"].isin(unwanted)]
df = df[(df["id"]>="1101") & (df["id"]<="9999") & (df["id"].str.len() == 4)].sort_values("jumpRate", ascending=False)
# df.info()
# print(df.head(50))

## 取得即時股價收盤價資料 ----------------------------------------------------------------------------------------
r2 = requests.get("https://www.wantgoo.com/stock/all-turnover-rates", headers = headers).content
soup = BeautifulSoup(r2, "html.parser")
rr2 = soup.prettify()
dfa = pd.read_json(StringIO(rr2))
# print(dfv)
from IPython.display import display
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 500)
pd.set_option("expand_frame_repr", False)
pd.set_option('display.width', 180)    

dfa["investrueId"] = dfa["investrueId"].astype("string")
dfb = pd.merge(df, dfa, left_on="id", right_on="investrueId")
dfb = dfb.drop(columns=['investrueId'])          
dfb["周轉率"] = dfb["value"].round(2) #周轉率

dfc = pd.merge(dfb, dfv, left_on="id", right_on="id")
dfc["預估量"] = (dfc["volume"] * getRate5K()).astype(int)        ##預估量
dfc["量比"] = (dfc["預估量"] / dfc["yVolume"]).round(2)
dfc["週量比"] = (dfc["預估量"] / dfc["ma5"]).round(2)
dfc["月量比"] = (dfc["預估量"] / dfc["ma20"]).round(2)
dfc["季量比"] = (dfc["預估量"] / dfc["ma60"]).round(2)
dfc["半年量比"] = (dfc["預估量"] / dfc["ma120"]).round(2)
dfc["年量比"] = (dfc["預估量"] / dfc["ma240"]).round(2)
dfc["量比周轉"] = ((dfc["量比"] + dfc["value"]) / 2).round(4)
dfc.replace([np.inf, -np.inf], 0, inplace=True)
dfc["json"] = dfc.apply(fm.fmt_all_infor_stock, axis=1)
print(dfc["json"])
## 策略2:找出周轉率高 、不包含興櫃公司
dfc2 = dfc[ (dfc["yVolume"] > 2000) & (dfc["close"] < 600) & (dfc["amp"] > 2) & (dfc["量比"] >= 2) & (dfc["預估量"] > 1000 ) & (dfc["周轉率"] > 1.5) & (dfc["market"] != "Emerging") ]
df2a   = dfc2.loc[:, ["id","market","name","yClose","low","open","close","jump","amp","jumpRate","yVolume","預估量","量比","週量比","月量比","季量比","半年量比","年量比","周轉率","量比周轉"]].sort_values("周轉率", ascending=False)

nowtime = time.localtime()
s1 ,s2 ,s3, o_nowDate, o_nowTime = '', '', '', time.strftime("%Y%m%d", nowtime) , time.strftime("%Y%m%d_%H%M", nowtime)

df4 = df2a["id"].tolist()
for d in df4:
  s2 += f"{d}.TW,"
fm.write_LogFile(f"{rootpath}xq_import/{o_nowTime}_量比大.csv", s2)

all_info_path, dtm1 = f"{rootpath}data/json/all_info.json", datetime.now()

# 刪除文件（如果存在）
if os.path.exists(all_info_path):
    os.remove(all_info_path)

df5 = dfc["json"].tolist()
for d in df5:
  s3 += "{" + d + "},"
s3 = s3[:-1]
fm.write_LogFile(all_info_path, f"[{s3}]")

# 等待文件生成完成，否則後面的都不會執行
while not os.path.exists(all_info_path):
    time.sleep(1)  # 每秒檢查一次，可以根據實際情況調整等待時間

dtm2 = datetime.now()
time_difference = dtm2 - dtm1
milliseconds_difference = time_difference.total_seconds() * 1000
print(f"產生all stock info的時間，{milliseconds_difference}毫秒")




