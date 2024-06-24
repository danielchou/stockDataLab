import finlab
finlab.login(open("config.txt", "r").read())

from finlab import data
from finlab.data import indicator
import pandas as pd
import _beowFmt as fm
import time
today, s1 = time.strftime("%Y%m%d_%H%M", time.localtime()) , ""

iStart = -240
opens    = data.get("price:開盤價").astype(float)[iStart: ]  #移除 .fillna(0) 如果資料有空白自動填0，這會與XQ計算的不吻合。
closes   = data.get("price:收盤價").astype(float)[iStart: ]
ycloses   = closes.shift(1, axis=0)
# highs    = data.get("price:最高價").fillna(0).astype(float)[iStart: ]
# lows     = data.get("price:最低價").fillna(0).astype(float)[iStart: ]
volumns  = data.get("price:成交股數").fillna(0).astype(float)[iStart: ]/1000
volumns  = volumns.astype(int)
yv       = volumns.shift(1, axis = 0).fillna(0).astype(int)
cEma13 = closes.ewm(span=13, adjust=False).mean().round(3).astype(float)
cEma34 = closes.ewm(span=34, adjust=False).mean().round(3).astype(float)
cEma55 = closes.ewm(span=55, adjust=False).mean().round(3).astype(float)
cEma89 = closes.ewm(span=89, adjust=False).mean().round(3).astype(float)
cEma144 = closes.ewm(span=144, adjust=False).mean().round(3).astype(float)
cEma200 = closes.ewm(span=200, adjust=False).mean().round(3).astype(float)
# kd_k, kd_s  = data.indicator('STOCH')[iStart: ] 
# pd.set_option('display.expand_frame_repr', False)

# ## 三大法人資料 ###
# fcb     = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')[-70: ]
# ic      = data.get('institutional_investors_trading_summary:投信買賣超股數')[-70: ]
# dealer  = data.get('institutional_investors_trading_summary:自營商買賣超股數(自行買賣)')[-70: ]
# dealer2 = data.get('institutional_investors_trading_summary:自營商買賣超股數(避險)')[-70: ]
# _v      = volumns.fillna(0).astype(float)[-70: ]

cond1 = closes > opens 
cond2 = opens > cEma34 
cond3_1 = cEma13 >= cEma34 
cond3_2 = cEma34 >= cEma55
cond3_3 = cEma55 >= cEma89
cond3_4 = cEma89 >= cEma144
cond3_5 = cEma144 >= cEma200
cond4   = volumns >= 2500


position = cond1 & cond3_1 & cond3_2 & cond3_3 & cond3_4 & cond3_5 & cond4
stockLists = fm.lastFinlabStockIdList(positionData = position) 
unwanted = ["2809","2880","2881","2882","2883","2884","2885","2886","2887","2888","2889","2890","2891","2892"] #清除不必要的金融股
filterdStock = [code for code in stockLists if code not in unwanted]
for c in filterdStock:
    s1 += f"{c}.TW,"
# fm.write_LogFile(f"xq_lab/{today}_跳過EMA3455均線.csv", s1)
fm.write_LogFile(f"xq_lab/{today}_均線多頭排列.csv", s1)