import pandas as pd
import _beowFmt as fm
import _beowDDE as bwdde
import time

# 設置顯示選項
# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)
# pd.set_option('display.width', 880)  # 設置顯示寬度
# # pd.set_option('display.max_columns', None)  # 顯示所有列
# pd.set_option('display.max_rows', 40)  # 顯示所有行
# pd.set_option('display.expand_frame_repr', False)  # 不自動換行


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
    market, whaleSpread, whaleSpreadRatio,ln, \
    roe, pe, pb, yoy, mom, net, dvd, info, group, shh, inv, mn, \
    srlb, srCd, nrBy, nrAvg = \
        r["代碼"], r["商品"], r["多空"], r["最低"], r["最高"], r["成交"], r["昨收"], r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["換手率%"], \
        r["market"], r["大戶差2"], r["大戶差比"], r["融資使用率%"], \
        r["roe"],r["pe"],r['pb'],r['yoy'],r['mom'],r['net'],r["dvd"],r["info"],r["group"],r['shh'],r['inv'],r['mm'], \
        r["sortLabel"], r["sortCode"], r["nearBy"], r["nearByAvg"]    
    
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
    
    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"yc":{yesterdayClose},"v":{totalValue},"vE":{estValue},"amp":{amplitude},"vR":{volRate},"turOv":{turnOver},"ind":"{market}","wts":{whaleSpread},"wtr":{whaleSpreadRatio},"ln":{ln},"roe":{roe},"pe":{pe},"pb":{pb},"yy":{yoy},"mm":{mom},"nt":{net},"dd":"{dvd}","fo":"{info}","gp":"{group}","sh":"{shh}","iv":"{inv}","mn":"{mn}","srlb":"{srlb}","srCd":"{srCd}","nrBy":"{nrBy}","nrAvg":"{nrAvg}"'
    return "{" + sql + "},"


def fmt_group_json(r):
    market, vrMean, turnOverMean, k, count, bigSum, bigCount, details = r['market'], r['平均量比'], r['換手率%'], r['多空'], r['筆數'], r['大戶買總額'],r['大戶買多的股票數量'], r['相關股票明細']
        
    sql = f'"market":"{market}","vmn":{vrMean},"tov":{turnOverMean},"k":{k},"cc":{count},"sum":{bigSum},"bigCC":{bigCount},"dls":"{details}"'
    # sql = f'"market":"{market}","dls":"{details}"'
    return "{" + sql + "},"

def Main(topic, ddeDict, stockFiles, sep):
    service = "XQLITE"

    dde_List = list(ddeDict.keys())   #將dictionary物件轉換成list欄位
    
    stockLists = []
    for stockFile in stockFiles:
        stock_Ids = open(stockFile, "r").read().split(",")
        ddeItems = [f"{code}.TW-{",".join(dde_List)}" for code in stock_Ids]
        stockList = bwdde.fetch_multiple_dde_data(service, topic, ddeItems)
        # print(len(stockList))
        time.sleep(5)
        stockLists += stockList
    data = stockLists
    
    if data:
        df = process_dde_data(dde_List, data, sep)
        # 重命名列名
        df = df.rename(columns=ddeDict)

       # 將百分比列轉換為浮點數
        df['ID'] = df['代碼'].astype(int)
        # df['內外盤%'] = df['內外盤%'].str.replace('%', '')
        df['漲幅%'] = df['漲幅%'].str.replace('%', '').replace('+', '')

        str2Float_columns = ['漲幅%', '成交', '昨收', '最低', '最高', '換手率%', '大戶差比', '量比', '融資使用率%']
        df[str2Float_columns] = df[str2Float_columns].replace('--', '').replace('-', '').replace('', '0').astype(float)        
        df['總量'] = pd.to_numeric(df['總量'])
        df['總量'] = df['總量'].astype(int)
        df['多空'] = df['漲幅%'].apply(lambda x: 1 if x > 0 else 0)
        df['大戶差2'] =df['大戶差'].apply(bwdde.to_billion)           #全部改以億為單位
        # df['五日量比'] = df.apply(lambda r: round(float(r['總量']) / float(r['五日均量']), 1) if r['估計量'] == '--' and float(r['五日均量']) != 0 else
        #                    round(float(r['估計量']) / float(r['五日均量']), 1) if float(r['五日均量']) != 0 else
        #                    0, axis=1)
        
        #--合併產業資訊--------------------------------------------------------------------------------
        stock_subject_file = r"webJson\stock_subject.csv"
        stockSubject = pd.read_csv(stock_subject_file, encoding='utf-8')
        stockSubject.columns = ["name","id","market"]
        # print(stockMarket.head())
        df = pd.merge(df, stockSubject, left_on="ID", right_on="id")  ## 結合股票名稱
        # print('整併產業', len(df))

        #--合併集團年底作帳資訊--------------------------------------------------------------------------------
        stock_group_file = r"webJson\stock_group.csv"
        stockGroup = pd.read_csv(stock_group_file, encoding='utf-8')
        stockGroup.columns = ["id","group"]
        # print(stockMarket.head())
        # 進行左外連接
        df = pd.merge(df, stockGroup, left_on="ID", right_on="id", how='left')
        # print('整併集團', len(df))
        # print(df[df['ID']==6488])
       
        # df2 = df[(df['大戶差2'] > 0.7) & (df['大戶差比'] > 10)]
        # df2 = df[(df['大戶差比'] > 15) | (df['大戶差比'] < -15)]
        df2 = df[((df['大戶差比'] > 6) & (df['大戶差2'] >= 0.8)) | ((df['大戶差比'] < -1) & (df['大戶差2'] <= -0.6))]
        print('篩選有效來統計', len(df2))

        grouped = df2.groupby(['market','多空']).agg({
            '量比': ['mean','count'],
            '換手率%': ['mean'],
            '大戶差2': ['sum','mean','count']
        })
        grouped.columns = ['平均量比', '筆數', '換手率%', '大戶買總額','大戶買平均','大戶買多的股票數量']
        grouped = grouped.round(1)
        # print(grouped)

        df_group = grouped[(grouped['大戶買總額'] >= 0.8) | (grouped['大戶買總額'] <= 0)].sort_values(by='大戶買平均', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # 統計題材之後，產出對應的股票名稱，以量比由大到小排列，可快速瀏覽...
        df_group['相關股票明細'] = df2.groupby(['market','多空']).apply(lambda x: ','.join(x.sort_values(by='量比', ascending=False)['商品']), include_groups=False)
        df_group = df_group.reset_index() # 重置索引，使market成為一個欄位
        df_group['json'] = df_group.apply(fmt_group_json, axis=1)

        #代表性不夠的就予以排除
        # df_filtered = df_group[~((df_group['平均量比'] <= 1.2) & (df_group['筆數'] == 1))]
        # df_filtered = df_filtered[~((df_filtered['多空'] == 1) & (df_filtered['大戶買總額'] < 0))]
        # print(df_group)


        targe_file = r"webJson\currStockMarket.json"
        ss = ''.join(df_group['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')

        #--合併財務資訊--------------------------------------------------------------------------------
        financeData_file = r'webJson\\stock_finance.csv'
        financeData = pd.read_csv(financeData_file, encoding='utf-8')
        financeData = financeData.fillna('')
        financeData.columns = ["id","cap","roe","pe","pb","yoy","mom","net","dvd","info","shh","mm","inv"]
        # print(financeData.head(60))
        df = pd.merge(df, financeData, left_on="ID", right_on="id")  ## 結合股票名稱
        # print('整併財務', len(df))
        #--合併均線訊號是否糾結?大概在哪個價位反彈? 盤中的反應如何?---------------------------------------
        ema_file = r'webJson\\stock_EMA.csv'
        ema_data = pd.read_csv(ema_file, encoding='utf-8')
        ema_data = ema_data[(ema_data['stockId'].str.len() == 4)].fillna('')
        ema_data.columns = ["stockId","sortLabel","sortCode","nearBy","nearByAvg"]
        ema_data["ma_stockId"] = ema_data['stockId'].astype(int)
        # print(ema_data.head(60))
        df = pd.merge(df, ema_data, left_on="ID", right_on="ma_stockId")  ## 結合股票名稱
        

        df['mm'] = df['mm'].str.replace('2024/', '') #營收月份 2024/08
        df['json']= df.apply(fmt_xq2json, axis = 1) 
        # print('最後成果', len(df))
        # print(print(df[df['ID']==2330]["json"]))

        targe_file = r"webJson\currentMaxValue.100.json" #產出json資料到WebJson目錄下
        ss = ''.join(df['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")     #送出到網站    
        fm.FtpFile(targe_file, 'static/currentMaxValue.100.json')
    else:
        print("Failed to fetch data")


# 追蹤股票號碼
stock_Files = [r"stock\sorted.txt"] 
dde_basic_dict={
            'ID': '代碼', 
            'Name': '商品',
            'Price': '成交',
            'Low': '最低',
            'High': '最高',
            'TotalVolume': '總量',
            'VolumeRatio': '量比',
            'TurnoverRatio': '換手率%',
            'PreClose': '昨收',
            'PriceChangeRatio': '漲幅%',
            'MajorOrderDif': '大戶差',
            'MajorOrderDifRatio': '大戶差比',
            'EstimatedTotalVolume': '估計量',
            'FinanceUsedRatio': '融資使用率%',
        }
Main("Quote", dde_basic_dict, stock_Files, ";")
            