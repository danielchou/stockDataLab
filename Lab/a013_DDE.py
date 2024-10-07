import pandas as pd
import _beowFmt as fm
from datetime import datetime
import _beowDDE as bwdde


def process_dde_data(columns, data, sep):

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

def calcX(r):
    volRate, turnOver, whaleSpreadRatio, yoy, mom, net = r["量比"], r["換手率%"], r["大戶差比"], r['yoy'],r['mom'],r['net']
    volRate2, yoymom, net2 = 1, 1, 1
    
    if (yoy > 2.1 and mom > 2.1):
        yoymom = 2
    if (net > 20):
        net2 = round(net/20,1)
    if volRate >= 1.8:
        volRate2 = volRate

    return round(volRate2 * turnOver * whaleSpreadRatio * yoymom * net2 / 100 , 1)

def fmt_xq2json(r):
    stockId, stockName,k, low, high, close, yesterdayClose, amplitude, estValue, totalValue, volRate, turnOver,\
          roe, ioRate, market, vMa5, ln, whaleSpread, whaleSpreadRatio, \
          cap, pe, pb, yoy, mom, net, dvd, info, shh, inv, x, mn = r["代碼"], r["商品"], r["多空"], r["最低"], r["最高"], r["成交"], r["昨收"], r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["換手率%"], \
            r["ROE%"], r["內外盤%"], r["market"], r["五日量比"], r["融資使用率%"], r["大戶差2"], r["大戶差比"], \
            r["cap"],r["pe"],r['pb'],r['yoy'],r['mom'],r['net'],r["dvd"],r["info"],r['shh'],r['inv'],r['x'],r['mm']
   
    # ln = "" if (ln == '--') else ln   # Finance Used Ratio 融資使用率
    roe = 0 if (roe == '--') else roe
    ioRate = 0 if (ioRate == '--') else ioRate
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
    
    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"yc":{yesterdayClose},"v":{totalValue},"vE":{estValue},"amp":{amplitude},"vR":{volRate},"turOv":{turnOver},"roe":{roe},"ioR":{ioRate},"ind":"{market}","v5":{vMa5},"ln":"{ln}","wts":{whaleSpread},"wtr":{whaleSpreadRatio},"pe":{pe},"pb":{pb},"yy":{yoy},"mm":{mom},"nt":{net},"dd":"{dvd}","fo":"{info}","sh":"{shh}","iv":"{inv}","x":{x},"mn":"{mn}"'
    return "{" + sql + "},"


def fmt_group_json(r):
    market, vrMean, turnOverMean, k, count, bigSum, details = r['market'], r['平均量比'], r['換手率%'], r['多空'], r['筆數'], r['大戶買總額'], r['相關股票明細']
        
    sql = f'"market":"{market}","vmn":{vrMean},"tov":{turnOverMean},"k":{k},"cc":{count},"sum":{bigSum},"dls":"{details}"'
    # sql = f'"market":"{market}","dls":"{details}"'
    return "{" + sql + "},"

def Main(topic, ddeDict, stock_Ids, sep):
    service = "XQLITE"

    dde_List = list(ddeDict.keys())   #將dictionary物件轉換成list欄位
    print(dde_List)
    ddeItems = [f"{code}.TW-{",".join(dde_List)}" for code in stock_Ids]
    data = bwdde.fetch_multiple_dde_data(service, topic, ddeItems)

    
    if data:
        df = process_dde_data(dde_List, data, sep)
        # 重命名列名
        df = df.rename(columns=ddeDict)
        

       # 將百分比列轉換為浮點數
        df['ID'] = df['代碼'].astype(int)
        df['內外盤%'] = df['內外盤%'].str.replace('%', '')
        df['漲幅%'] = df['漲幅%'].str.replace('%', '').replace('+', '')
        df['融資使用率%'] = df['融資使用率%'].str.replace('--', '')

        str2Float_columns = ['漲幅%', '成交', '昨收', '最低', '最高', '換手率%', '大單差%', '大戶差比', '量比']
        df[str2Float_columns] = df[str2Float_columns].replace('--', '0').astype(float)        
        df['總量'] = pd.to_numeric(df['總量'])
        df['總量'] = df['總量'].astype(int)
        df['多空'] = df['漲幅%'].apply(lambda x: 1 if x > 0 else 0)
        df['大戶差2'] =df['大戶差'].apply(bwdde.to_billion)           #全部改以億為單位
        df['五日量比'] = df.apply(lambda r: round(float(r['總量']) / float(r['五日均量']), 1) if r['估計量'] == '--' and float(r['五日均量']) != 0 else
                           round(float(r['估計量']) / float(r['五日均量']), 1) if float(r['五日均量']) != 0 else
                           0, axis=1)
        
        
        #--合併產業資訊--------------------------------------------------------------------------------
        stock_group_file = r"D:\project\stockDataLab\Lab\data\webJson\stock_group.csv"
        stockMarket = pd.read_csv(stock_group_file, encoding='utf-8')
        stockMarket.columns = ["name","id","market"]
        # print(stockMarket.head())
        df = pd.merge(df, stockMarket, left_on="ID", right_on="id")  ## 結合股票名稱

       
        # df2 = df[(df['大戶差2'] > 0.7) & (df['大戶差比'] > 10)]
        # df2 = df[(df['大戶差比'] > 15) | (df['大戶差比'] < -15)]
        df2 = df[((df['大戶差比'] > 6) & (df['大戶差2'] >= 0.8)) | ((df['大戶差比'] < -1) & (df['大戶差2'] <= -0.6))]
        
        grouped = df2.groupby(['market','多空']).agg({
            '量比': ['mean','count'],
            '換手率%': ['mean'],
            '大戶差2': ['sum'],
        })
        grouped.columns = ['平均量比', '筆數', '換手率%', '大戶買總額']
        grouped = grouped.round(1)
        
        df_group = grouped[grouped['大戶買平均'] >= 1.2].sort_values(by='大戶買平均', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # 統計題材之後，產出對應的股票名稱，以量比由大到小排列，可快速瀏覽...
        df_group['相關股票明細'] = df2.groupby(['market','多空']).apply(lambda x: ','.join(x.sort_values(by='量比', ascending=False)['商品']))
        df_group = df_group.reset_index() # 重置索引，使market成為一個欄位
        df_group['json'] = df_group.apply(fmt_group_json, axis=1)

        #代表性不夠的就予以排除
        df_filtered = df_group[~((df_group['平均量比'] <= 1.2) & (df_group['筆數'] == 1))]
        print(df_filtered)

        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currStockMarket.json"
        ss = ''.join(df_filtered['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')

        #--合併財務資訊--------------------------------------------------------------------------------
        financeData_file = r'D:\project\stockDataLab\Lab\data\\webJson\\financeData.csv'
        financeData = pd.read_csv(financeData_file, encoding='utf-8')
        financeData = financeData.fillna('')
        financeData.columns = ["id","cap","pe","pb","yoy","mom","net","dvd","info","shh","mm","inv"]
        # print(financeData.head(60))
        df = pd.merge(df, financeData, left_on="ID", right_on="id")  ## 結合股票名稱
        df['x'] = df.apply(calcX, axis=1)
        df['mm'] = df['mm'].str.replace('2024/', '') #營收月份 2024/08
        # print(df.head(50))

        df['json']= df.apply(fmt_xq2json, axis = 1) 
        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currentMaxValue.100.json" #產出json資料到WebJson目錄下
        ss = ''.join(df['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")     #送出到網站    
        fm.FtpFile(targe_file, 'static/currentMaxValue.100.json')
    else:
        print("Failed to fetch data")


# 追蹤股票號碼
stock_Ids = open("a013_stockIds", "r").read().split(",")
dde_basic_dict={
            'ID': '代碼', 
            'Name': '商品',
            'Price': '成交',
            'TotalVolume': '總量',
            'VolumeRatio': '量比',
            'TurnoverRatio': '換手率%',
            'PreClose': '昨收',
            'PriceChangeRatio': '漲幅%',
            'DLOrderValueDiffRatio': '大單差%',
            'MajorOrderDif': '大戶差',
            'MajorOrderDifRatio': '大戶差比',
            'Low': '最低',
            'High': '最高',
            'ROE': 'ROE%',
            'InOutRatio': '內外盤%',
            'EstimatedTotalVolume': '估計量',
            '5DayAvgVol': '五日均量',
            'FinanceUsedRatio': '融資使用率%',
        }
Main("Quote", dde_basic_dict, stock_Ids, ";")