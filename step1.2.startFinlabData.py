# %%
## 找出今天數量，各種均量
rootpath= "D:/project/finlabexportdata/"
import finlab
finlab.login(open(f"{rootpath}config.txt", "r").read())

from finlab import data
import pandas as pd
import _beowFmt as fm 

def combineStr(r):
    stockId, open, close, high, ma1, ma5, ma20, ma60, ma120, ma240 = r["stockId"], r["open"], r["close"], r["high"], r["ma1"], r["ma5"], r["ma20"], r["ma60"], r["ma120"], r["ma240"]
    kbar = 'R' if (close > open) else 'G'
    return f"{stockId},{kbar},{open},{close},{high},{ma1},{ma5},{ma20},{ma60},{ma120},{ma240}"

##
opens    = data.get("price:開盤價").fillna(0).astype(float).tail(1)      #如果資料有空白自動填0
closes   = data.get("price:收盤價").fillna(0).astype(float).tail(1)
highs    = data.get("price:最高價").fillna(0).astype(float).tail(1)
volumns  = data.get("price:成交股數").fillna(0).astype(float)[250: ]  
v = (volumns/1000).round(0).astype(int)
vMa5 = v.rolling(5, min_periods=1).mean().round(0).astype(int).tail(1)
vMa20 = v.rolling(20, min_periods=1).mean().round(0).astype(int).tail(1)
vMa60 = v.rolling(60, min_periods=1).mean().round(0).astype(int).tail(1)
vMa120 = v.rolling(120, min_periods=1).mean().round(0).astype(int).tail(1)
vMa240 = v.rolling(240, min_periods=1).mean().round(0).astype(int).tail(1)

## 本益比、EPS
pER = data.get('price_earning_ratio:本益比')
#print(pER["2328"])

sss = data.get('trading_attention')
# print(sss["2328"])

vdf = v.iloc[-1:].transpose()
vdf["stock"] = vdf.index
vdf.columns = ["ma1", "stockId"]
vdf["ma5"] = vMa5.iloc[-1:].transpose()
vdf["ma20"] = vMa20.iloc[-1:].transpose()
vdf["ma60"] = vMa60.iloc[-1:].transpose()
vdf["ma120"] = vMa120.iloc[-1:].transpose()
vdf["ma240"] = vMa240.iloc[-1:].transpose()
vdf["open"] = opens.iloc[-1:].transpose()
vdf["close"] = closes.iloc[-1:].transpose()
vdf["high"] = highs.iloc[-1:].transpose()
vdf["comp"] = vdf.apply(combineStr, axis = 1)
vdf2 = vdf[ (vdf["stockId"].str.len() == 4)].dropna(axis = 0, how ='any')
# print(vdf2)

s1 = 'id,kbar,yOpen,yClose,yHigh,yVolume,ma5,ma20,ma60,ma120,ma240\n'
for c in vdf2["comp"].tolist():
    s1 += f"{c}\n"
# print(s1)

from datetime import date, timedelta
import time

today = date.today()                        # 取得今天的日期
yesterday = today - timedelta(days=1)       # 計算昨天的日期
yesterday = yesterday.strftime("%Y%m%d")    # 將日期轉換為指定的格式
fm.write_LogFile(f"{rootpath}volumeData/ma_{yesterday}.csv", s1)
