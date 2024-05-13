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

rootpath= "D:/project/finlabexportdata/"

yesterday = fm.getLastFileDate(f"{rootpath}/volumeData", "ma_")

df5k = pd.read_json(f"{rootpath}paras/mapping5K.json")
dfv = pd.read_csv(f"{rootpath}volumeData/ma_{yesterday}.csv")
dfv["id"] = dfv["id"].astype("string")
# dfv = dfv.drop(columns=['close'])
#print(dfv[dfv["id"] == "3265"])

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
}

url4 = "https://www.wantgoo.com/investrue/all-alive"
r3 = requests.get(url4, headers = headers).content
soup = BeautifulSoup(r3, "html.parser")
rr3 = soup.prettify()
dfn = pd.read_json(StringIO(rr3))
dfn = dfn[(dfn["id"]>="1101") & (dfn["id"]<="9999") & (dfn["id"].str.len() == 4)] # & (dfn["market"] != "Emerging")
dfn = dfn.drop(columns=['type','country','url', 'industries'])
dfn["id"] = dfn["id"].astype("string")
dfn = dfn.sort_values("id")

def comp_stockName(r):
    id, name, market = r["id"], r["name"],r["market"]
    return f"{id},{name},{market}"

dfn["comp"] = dfn.apply(comp_stockName, axis = 1)

stockNameStr = ""

for c in dfn["comp"].tolist():
    stockNameStr += f"{c}\n"
fm.write_LogFile(f"{rootpath}paras/股票名稱.csv", stockNameStr)  
# %%
