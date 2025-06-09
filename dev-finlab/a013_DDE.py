import pandas as pd
import _beowFmt as fm
import _beowDDE as bwdde
import time
import numpy as np
from finlab import data
from datetime import datetime

import finlab
finlab.login(open("config.txt", "r").read())

# 設置顯示選項
# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)
# pd.set_option('display.width', 1280)  # 設置顯示寬度
# pd.set_option('display.max_columns', None)  # 顯示所有列
# pd.set_option('display.max_rows', 140)  # 顯示所有行
# pd.set_option('display.expand_frame_repr', True)  # 不自動換行


def process_dde_data(columns, data, sep):
    # 打印原始數據以檢查格式
    # print("Raw DDE data:")
    # for item in data:
    #     print(item) 

    processed_data = []
    for item in data:
        # 如果數據是單個字符串，嘗試分割
        if isinstance(item, str):
            # 這裡使用製表符（\t）分割，您可能需要根據實際格式調整
            processed_item = item.split(sep)
            if len(processed_item) != len(columns):
                print(len(processed_item),len(columns))
                print(f"Warning: Unexpected number of fields in item: {item}")
                continue
        else:
            print(f"Warning: Unexpected data type for item: {type(item)}")
            continue
        processed_data.append(processed_item)
    
    return pd.DataFrame(processed_data, columns=columns)




def fmt_xq2json(r):
    stockId, stockName,k, opened, low, high, close, yesterdayClose, \
    amplitude, estValue, totalValue, volRate, volMaxDays, turnOver,\
    market, whaleSpread, whaleSpreadRatio,ln, \
    roe, pe, pb, yoy, mom, net, dvd, info, group, shh, inv, mn, \
    srlb, srCd, nrBy, nrAvg, snv, far = \
        r["代碼"], r["商品"], r["多空"], r["開盤"], r["最低"], r["最高"], r["成交"], r["昨收"], \
        r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["大量天數"], r["換手率%"], \
        r["market"], r["大戶差2"], r["大戶差比"], r["融資使用率%"], \
        r["roe"],r["PE"],r['pb'],r['yoy'],r['mom'],r['net'],r["dvd"],r["info"],r["group"],r['shh'],r['inv'],r['mm'], \
        r["sortLabel"], r["sortCode"], r["nearBy"], r["nearByAvg"], r["snv"], r["far"]
    
    if(np.isnan(nrAvg)):
        isCross = -1 #表示根本沒有均線糾結
        nrAvg = (opened +  low +high + close) /4  #假設為四個數字的平均值，這裡將來要修正。
    else:
        if (k==1):
            isCross = 1 if (close >=nrAvg and nrAvg >= opened) else 0
        else:
            isCross = 1 if (opened >= nrAvg and nrAvg >= close) else 0

    ln = "" if (ln == '--') else ln   # Finance Used Ratio 融資使用率
    roe = 0 if (roe == '--') else roe
    # ioRate = 0 if (ioRate == '--') else ioRate
    estValue = 0 if (estValue == '--') else estValue
    yoy = 0 if (yoy == '--') else yoy
    mom = 0 if (mom == '--') else mom
    net = 0 if (net == '--') else net
    info = '' if (info == '-') else info
    try:
        if low == '0' or high == '0' or yesterdayClose == '0':
            jmp = 0
        else:
            jmp = round(low - yesterdayClose,1) if amplitude > 0 else round(yesterdayClose - high,1)
    except Exception as e:
        print(low, high, yesterdayClose)
        print(f"An error occurred: {e}")
        jmp = 0
    
    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"o":{opened},"l":{low},"h":{high},"cr":{isCross},"yc":{yesterdayClose},"v":{totalValue},"vE":{estValue},"amp":{amplitude},"vR":{volRate},"vmd":{volMaxDays},"turOv":{turnOver},"ind":"{market}","wts":{whaleSpread},"wtr":{whaleSpreadRatio},"ln":{ln},"roe":{roe},"pe":{pe},"pb":{pb},"yy":{yoy},"mm":{mom},"nt":{net},"dd":"{dvd}","fo":"{info}","gp":"{group}","sh":"{shh}","iv":"{inv}","mn":"{mn}","srlb":"{srlb}","srCd":{srCd},"nrBy":"{nrBy}","nrAvg":{nrAvg},"snv":{snv},"far":{far}'
    return "{" + sql + "},"


def fmt_group_json(r):
    market, vrMean, turnOverMean, k, count, bigSum, bigCount, details = r['market'], r['平均量比'], r['換手率%'], r['多空'], r['筆數'], r['大戶買總額'],r['大戶買多的股票數量'], r['相關股票明細']
        
    sql = f'"market":"{market}","vmn":{vrMean},"tov":{turnOverMean},"k":{k},"cc":{count},"sum":{bigSum},"bigCC":{bigCount},"dls":"{details}"'
    # sql = f'"market":"{market}","dls":"{details}"'
    return "{" + sql + "},"


def find_first_larger_volume(series, target):
    for i, value in enumerate(series[::-1]):
        if value >= target:
            return i
    return len(series)


def Main(topic, ddeDict, stockFiles, sep):
    service = "XQLITE"

    dde_List = list(ddeDict.keys())   #將dictionary物件轉換成list欄位
    
    stockLists = []
    for stockFile in stockFiles:
        stock_Ids = open(stockFile, "r").read().split(",")
        ddeItems = [f"{code}.TW-{",".join(dde_List)}" for code in stock_Ids]
        stockList = bwdde.fetch_multiple_dde_data(service, topic, ddeItems)
        print(len(stockList))
        # time.sleep(5)
        stockLists += stockList
    dde_data = stockLists
    
    if dde_data:
        df = process_dde_data(dde_List, dde_data, sep)
        # 重命名列名
        df = df.rename(columns=ddeDict)

       # 將百分比列轉換為浮點數
        df['ID'] = df['代碼'].astype(int)
        # df['內外盤%'] = df['內外盤%'].str.replace('%', '')
        df['漲幅%'] = df['漲幅%'].str.replace('%', '').replace('+', '')

        str2Float_columns = ['漲幅%', '成交', 'PE', '昨收', '開盤', '最低', '最高', '換手率%', '大戶差比', '量比', '融資使用率%','總委買','總委賣']
        df[str2Float_columns] = df[str2Float_columns].replace('--', '').replace('-', '').replace('', '0').astype(float)        
        df['總量'] = pd.to_numeric(df['總量'])
        df['總量'] = df['總量'].astype(int)
        df['多空'] = df['漲幅%'].apply(lambda x: 1 if x > 0 else 0)
        df['大戶差2'] = df['大戶差'].apply(bwdde.to_billion)            # 全部改以億為單位
        # df['far'] = df['總委賣']/df['總委買']                           # 計算委賣買進五盤的比率
        # df['far'] = df['總委賣'].div(df['總委買'], fill_value=np.nan)    # 使用 div 方法进行除法运算，并设置 fill_value 参数来处理无穷大值。
        df['far'] = np.where(df['總委買'] != 0, df['總委賣'] / df['總委買'], np.nan)
        df['far'] = df['far'].fillna(0).round(2)                       # 將 NaN 填充為 0
        # del df['總委賣']
        # del df['總委買']
        print(df[df['ID']==2609])

        #--量大天數-----------------------------------------------------------------------------
        df_estVols = df[(df["量比"] >= 1.2) & (df["大戶差2"] > 0.005)]  
        # print(f'量比大於2且大戶有買的共{len(df_estVols)}筆')
        # print(df_estVols[["ID","量比","大戶差2","估計量","總量"]])
        
        data.use_local_data_only = False    #使用local資料
        vols = data.get("price:成交股數").astype(float)[500: ]
        vols = (vols / 1000).fillna(0).astype(int)  # 將 NaN 填充為 0
        closes = data.get("price:收盤價").astype(float)[500: ]
        opens = data.get("price:開盤價").astype(float)[500: ]
        kbars = closes < opens
        vols[kbars] = 100

        # 將 df_estVols 預估量加入到vols的最新當下
        now = datetime.now()
        start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=13, minute=30, second=0, microsecond=0)
        estVolsName = '估計量' if start_time <= now <= end_time else '總量'
        new_data = pd.Series(df_estVols.set_index('ID')[estVolsName].astype(float), name=pd.Timestamp.now().normalize())
        new_data.index = new_data.index.astype(str) # 確保索引（股票代碼）的類型一致
        vols = pd.concat([vols, new_data.to_frame().T]).astype(float) # 合併數據
        vols = vols[df_estVols["ID"].astype(str).tolist()][-500:] #不用找太遠的日期
        # print(vols)
        last_target_vol_day = -1  #SET: 以哪天為基準推估等了幾天才出大量? ex: -1 => 最後一天
        result_vols_days_df = pd.DataFrame({
            'ID': vols.columns.astype(int),
            '大量天數': [find_first_larger_volume(vols.iloc[:last_target_vol_day, i], vols.iloc[last_target_vol_day, i]) 
                        for i in range(len(vols.columns))]
        })  # 直接指定大量天數為整數型態
        # print(result_vols_days_df.sort_values(by='大量天數', ascending=False).head(10))

        df = pd.merge(df, result_vols_days_df, on="ID", how='left', validate='1:1')  ## 結合股票名稱
        df['大量天數'] = df['大量天數'].fillna(0).astype(int)
        # print('整併大量天數', len(df))

        #--合併產業資訊--------------------------------------------------------------------------------
        stock_subject_file = rf"{root}\webJson\stock_subject.csv"
        stockSubject = pd.read_csv(stock_subject_file, encoding='utf-8')
        stockSubject.columns = ["name","id","market"]
        # print(stockMarket.head())
        df = pd.merge(df, stockSubject, left_on="ID", right_on="id")  ## 結合股票名稱
        # print('整併產業', len(df))

        #--合併集團年底作帳資訊--------------------------------------------------------------------------------
        stock_group_file = rf"{root}\webJson\stock_group.csv"
        stockGroup = pd.read_csv(stock_group_file, encoding='utf-8')
        stockGroup.columns = ["id","group"]
        # print(stockMarket.head())
        # 進行左外連接
        df = pd.merge(df, stockGroup, left_on="ID", right_on="id", how='left')
        # print('整併集團', len(df))
        # print(df[df['ID']==2330][['ID','總量','量比','大量天數']])
       
        df2 = df[((df['大戶差比'] > 6) & (df['大戶差2'] >= 0.8)) | ((df['大戶差比'] < -1) & (df['大戶差2'] <= -0.6))]
        # print('篩選有效來統計', len(df2), df2[['ID','商品','量比','大戶差2','大戶差比']])

        grouped = df2.groupby(['market','多空']).agg({
            '量比': ['mean','count'],
            '換手率%': ['mean'],
            '大戶差2': ['sum','mean','count']
        })
        grouped.columns = ['平均量比', '筆數', '換手率%', '大戶買總額','大戶買平均','大戶買多的股票數量']
        grouped = grouped.round(1)
        # print(grouped)

        df_group = grouped[(grouped['大戶買總額'] >= 0.3) | (grouped['大戶買總額'] <= 0)].sort_values(by='大戶買平均', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # 統計題材之後，產出對應的股票名稱，以量比由大到小排列，可快速瀏覽...
        df_group['相關股票明細'] = df2.groupby(['market','多空']).apply(lambda x: ','.join(x.sort_values(by='大戶差2', ascending=False)['商品']), include_groups=False)
        df_group = df_group.reset_index() # 重置索引，使market成為一個欄位
        df_group['json'] = df_group.apply(fmt_group_json, axis=1)

        #代表性不夠的就予以排除
        # df_filtered = df_group[~((df_group['平均量比'] <= 1.2) & (df_group['筆數'] == 1))]
        # df_filtered = df_filtered[~((df_filtered['多空'] == 1) & (df_filtered['大戶買總額'] < 0))]
        # print(df_group)


        targe_file = rf"{root}\webJson\currStockMarket.json"
        ss = ''.join(df_group['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')

        #--合併財務資訊--------------------------------------------------------------------------------
        financeData_file = rf'{root}\webJson\stock_finance.csv'
        financeData = pd.read_csv(financeData_file, encoding='utf-8')
        financeData = financeData.fillna('')
        financeData.columns = ["id","cap","roe","pb","yoy","mom","net","dvd","info","shh","mm","inv","snv"]
        # print('財務資料', len(financeData))
        df = pd.merge(df, financeData, left_on="ID", right_on="id", how='left')  ## 結合股票名稱
        # print('整併財務', len(df))

        #--合併均線訊號是否糾結?大概在哪個價位反彈? 盤中的反應如何?---------------------------------------
        ema_file = rf'{root}\webJson\stock_EMA_All.csv'
        ema_data = pd.read_csv(ema_file, encoding='utf-8')
        ema_data = ema_data.fillna('')
        ema_data.columns = ["ema1","ma_stockId","ema5","ema13","ema50","ema200"]
        del ema_data['ema1']
        # print('均線資料', len(ema_data))
        df = pd.merge(df, ema_data, left_on="ID", right_on="ma_stockId", how='left')   ## left join 股票均線資料
        # print('整併均線', len(df))
        # 篩選出三個欄位同時為 0.0 的列
        filtered_out_condition = (df['成交'] == 0.0) & (df['最低'] == 0.0) & (df['最高'] == 0.0)
        filtered_df = df[filtered_out_condition]
        # print(f'過濾無效資料{len(filtered_df)}筆')
        # print(filtered_df[['代碼','商品','成交','總量']])
        df=df[~filtered_out_condition]
        df[['sortData', 'sortLabel', 'sortCode', 'nearBy', 'nearByAvg']]  = df.apply(bwdde.cal_nearBy, axis=1, result_type='expand')

        df['mm'] = df['mm'].str.replace('2025/', '') #營收月份 2024/08
        # print(df[['代碼','商品','成交','總量']])
        df['json']= df.apply(fmt_xq2json, axis = 1) 
        # print('最後成果', len(df))
        # print(df.head(100))
        # print(df[df['ID']==4979]["sortData"])

        targe_file = r"webJson\currentMaxValue.100.json" #產出json資料到WebJson目錄下
        ss = ''.join(df['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")     #送出到網站    
        fm.FtpFile(targe_file, 'static/currentMaxValue.100.json')
    else:
        print("Failed to fetch data")


# 追蹤股票號碼
root = r"d:\project\stockDataLab\Lab003_XQdde"
stock_Files = [rf"{root}\stock\sorted.txt"] 
dde_basic_dict={
            'ID': '代碼', 
            'Name': '商品',
            'Price': '成交',
            'Low': '最低',
            'High': '最高',
            'Open': '開盤',
            'PERatio': 'PE',
            'TotalVolume': '總量',
            'VolumeRatio': '量比',
            'TurnoverRatio': '換手率%',
            'PreClose': '昨收',
            'PriceChangeRatio': '漲幅%',
            'MajorOrderDif': '大戶差',
            'MajorOrderDifRatio': '大戶差比',
            'EstimatedTotalVolume': '估計量',
            'FinanceUsedRatio': '融資使用率%',
            'FiveBidSize': '總委買',
            'FiveAskSize': '總委賣',
        }
Main("Quote", dde_basic_dict, stock_Files, ";")
            