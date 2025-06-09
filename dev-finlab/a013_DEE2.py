import win32ui
import win32gui
import dde
import pandas as pd
import _beowFmt as fm
from datetime import datetime

# 設置顯示選項
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 880)  # 設置顯示寬度
# pd.set_option('display.max_columns', None)  # 顯示所有列
pd.set_option('display.max_rows', None)  # 顯示所有行
pd.set_option('display.expand_frame_repr', False)  # 不自動換行

import re
def to_billion(value):
    # 移除所有空白字符
    value = value.replace(' ', '')
    
    # 使用正則表達式提取數字和單位
    match = re.match(r'^(-?\d+\.?\d*)([萬億])?$', value)
    if not match:
        raise ValueError(f"無法解析的值: {value}")

    number, unit = match.groups()
    number = float(number)

    # 根據單位轉換為億
    if unit == '萬':
        number /= 10000  # 1億 = 10000萬
    elif unit == '億':
        pass  # 已經是億單位，不需要轉換
    else:
        number /= 100000000  # 假設無單位時為元，1億 = 100000000元

    # 四捨五入到小數點後三位
    return round(number, 1)

def get_first_item(text):
    if ',' in text:
        return text.split(',')[0]
    return text
    
def fetch_multiple_dde_data(service, topic, items):
    try:
        dde_client = dde.CreateServer()
        dde_client.Create("MyClient")
        
        conversation = dde.CreateConversation(dde_client)
        conversation.ConnectTo(service, topic)
        
        results = []
        for item in items:
            result = conversation.Request(item)
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        dde_client.Destroy()

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
    stockId, stockName,k, low, high, close, yesterdayClose, amplitude, estValue, totalValue, volRate, turnOver, roe, ioRate, market, vMa5, ln, whaleSpread, whaleSpreadRatio, info, chipsFields25  = r["代碼"], r["商品"], r["多空"], r["最低"], r["最高"], r["成交"], r["昨收"], r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["換手率%"], r["ROE%"], r["內外盤%"], r["market"], r["五日量比"], r["融資使用率%"], r["大戶差2"], r["大戶差比"], r["公司動態"],r["除息日"]
  
    ln = 0 if (ln == '--') else ln   # Finance Used Ratio 融資使用率
    roe = 0 if (roe == '--') else roe
    ioRate = 0 if (ioRate == '--') else ioRate
    estValue = 0 if (estValue == '--') else estValue
    # YoY = 0 if (YoY == '--') else YoY
    # MoM = 0 if (MoM == '--') else MoM
    # Net = 0 if (Net == '--') else Net
    info = '' if (info == '-') else info
    chipsFields25 = '' if (chipsFields25 == '--') else chipsFields25
    try:
        if low == '0' or high == '0' or yesterdayClose == '0':
            jmp = 0
        else:
            jmp = round(low - yesterdayClose,2) if amplitude > 0 else round(yesterdayClose - high,2)
    except Exception as e:
        print(low, high, yesterdayClose)
        print(f"An error occurred: {e}")
        jmp = 0
    
    # sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"yc":{yesterdayClose},"v":{totalValue},"amp":{amplitude},"estV":{estValue},"tV":{totalValue},"vR":{volRate},"turOv":{turnOver},"roe":{roe},"ioR":{ioRate},"ind":"{market}","v5":{vMa5},"ln":{ln},"wts":{whaleSpread},"wtr":{whaleSpreadRatio},"YoY":{YoY},"MoM":{MoM},"Net":{Net},"info":"{info}","cp":"{chipsFields25}"'
    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"yc":{yesterdayClose},"v":{totalValue},"amp":{amplitude},"estV":{estValue},"tV":{totalValue},"vR":{volRate},"turOv":{turnOver},"roe":{roe},"ioR":{ioRate},"ind":"{market}","v5":{vMa5},"ln":{ln},"wts":{whaleSpread},"wtr":{whaleSpreadRatio},"info":"{info}","cp":"{chipsFields25}"'
    return "{" + sql + "},"

def fmt_group_json(r):
    market, vrMean, turnOverMean, k, count, bigSum, details = r['market'], r['平均量比'], r['換手率%'], r['多空'], r['筆數'], r['大戶買總額'], r['相關股票明細']
        
    sql = f'"market":"{market}","vmn":{vrMean},"tov":{turnOverMean},"k":{k},"cc":{count},"sum":{bigSum},"dls":"{details}"'
    # sql = f'"market":"{market}","dls":"{details}"'
    return "{" + sql + "},"


def Main(topic, columns, ddeItems, sep):
    service = "XQLITE"

    data = fetch_multiple_dde_data(service, topic, ddeItems)
    if data:
        df = process_dde_data(columns, data, sep)
        # 重命名列名
        df = df.rename(columns={
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
            # 'MonthlyNetSalesYoY': '當月營收YOY',
            # 'TFXRatio':            '當月營收MOM',
            # 'NetIncomeGrowthRate': '稅後淨利成長率%',
            'ChipsField25': '除息日',
            'DetailIndustry':'細產業',
            'CompanyNews':'公司動態',
            })
        # print(df.head())

        # 將百分比列轉換為浮點數
        df['ID'] = df['代碼'].astype(int)
        df['內外盤%'] = df['內外盤%'].str.replace('%', '')
        df['漲幅%'] = df['漲幅%'].str.replace('%', '').str.replace('+', '').str.replace('--','0')
        df['漲幅%'] = df['漲幅%'].astype(float)
        df['成交'] = df['成交'].replace('--', '0').astype(float)
        df['昨收'] = df['昨收'].replace('--', '0').astype(float)
        df['最低'] = df['最低'].replace('--', '0').astype(float)
        df['最高'] = df['最高'].replace('--', '0').astype(float)
        df['換手率%'] = df['換手率%'].str.replace('--','0').astype(float)
        df['大單差%'] = df['大單差%'].str.replace('--','0').astype(float)
        df['大戶差比'] = df['大戶差比'].str.replace('--','0').astype(float)
        df['量比'] = df['量比'].astype(float)
        df['總量'] = pd.to_numeric(df['總量'])
        df['總量'] = df['總量'].astype(int)
        df['多空'] = df['漲幅%'].apply(lambda x: 1 if x > 0 else 0)
        df['大戶差2'] =df['大戶差'].apply(to_billion)           #全部改以億為單位
        df['五日量比'] = df.apply(lambda r: round(float(r['總量']) / float(r['五日均量']), 2) if r['估計量'] == '--' and float(r['五日均量']) != 0 else
                           round(float(r['估計量']) / float(r['五日均量']), 2) if float(r['五日均量']) != 0 else
                           0, axis=1)

        today = datetime.now().date()
        # 篩選出日期大於今天的行，否則設為空字串
        df['除息日'] = df['除息日'].str.replace('--','2022/1/1')
        df['除息日'] = pd.to_datetime(df['除息日'], format='%Y/%m/%d')
        df['除息日'] = df['除息日'].apply(lambda x: x if x.date() > today else '')
        df['除息日'] = df['除息日'].apply(lambda x: x.strftime('%Y/%m/%d') if isinstance(x, pd.Timestamp) else '')

        # df['estV%'] = df['ROE%'].astype(float)
        # df['產業2'] = df['細產業'].apply(get_first_item)
        # del df['細產業']
        # df['量比B'] = df['量比'] + df['五日量比']*1/3 
        
        #--合併產業資訊---------------------------------------------------------------
        stock_group_file = r"D:\project\stockDataLab\Lab\data\webJson\stock_group.csv"
        stockMarket = pd.read_csv(stock_group_file, encoding='utf-8')
        stockMarket.columns = ["name","id","market"]
        # print(stockMarket.head())
        
        df = pd.merge(df, stockMarket, left_on="ID", right_on="id")  ## 結合股票名稱
        # df2 = df[(df['大戶差2'] > 0.7) & (df['大戶差比'] > 10)]
        # df2 = df[(df['大戶差比'] > 15) | (df['大戶差比'] < -15)]
        df2 = df[((df['大戶差比'] > 6) & (df['大戶差2'] >= 0.8)) | ((df['大戶差比'] < -6) & (df['大戶差2'] <= -1.1))]
        
        grouped = df2.groupby(['market','多空']).agg({
            '量比': ['mean','count'],
            '換手率%': ['mean'],
            '大戶差2': ['sum'],
        })
        grouped.columns = ['平均量比', '筆數', '換手率%', '大戶買總額']
        grouped = grouped.round(1)
        # 添加一個欄位來標記換手率是否大於0
        
        df_group = grouped[grouped['平均量比'] >= 0.5].sort_values(by='大戶買總額', ascending=False)
        # df_group = grouped[grouped['平均大戶差比'] >= 10].sort_values(by='平均量比', ascending=False)
        # 統計題材之後，產出對應的股票名稱，以量比由大到小排列，可快速瀏覽...
        df_group['相關股票明細'] = df2.groupby(['market','多空']).apply(lambda x: ','.join(x.sort_values(by='量比', ascending=False)['商品']))

        # 重置索引，使market成為一個欄位
        df_group = df_group.reset_index()
        df_group['json'] = df_group.apply(fmt_group_json, axis=1)
        # print(df_group)

        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currStockMarket.json"
        ss = ''.join(df_group['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')
        
        print("\nProcessed data:")
        # print(df.head())

        df['json']= df.apply(fmt_xq2json, axis = 1) 
        #產出json資料到WebJson目錄下
        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currentMaxValue.100.json"
        ss = ''.join(df['json'].fillna('').astype(str))[:-1]
        #送出到網站
        fm.write_LogFile(targe_file, f"[{ss}]")         
        fm.FtpFile(targe_file, 'static/currentMaxValue.100.json')
    else:
        print("Failed to fetch data")


# 追蹤股票號碼
stock_Ids = open("data\\webJson\\a013_stockIds.txt", "r").read().split(",")

 # 假設每個項目是一個字符串，包含所有字段
QuoteColumns = ['ID','Name','Price','Low','High','ROE','PreClose','TotalVolume',
                'VolumeRatio', 
                'TurnoverRatio',  #換手%
                'PriceChangeRatio', #漲幅%
                'MajorOrderDif',      #大戶差
                'MajorOrderDifRatio', #大戶差比
                'DLOrderValueDiffRatio', #大單差%
                'InOutRatio', #內外盤%
                'EstimatedTotalVolume', #估計量
                '5DayAvgVol', #五日均量
                'FinanceUsedRatio', #融資使用率%
                # 'MonthlyNetSalesYoY',    #當月營收YOY
                # 'TFXRatio',              #當月營收MOM
                # 'NetIncomeGrowthRate',   #稅後淨利成長率%
                'ChipsField25', #除息日
                'CompanyNews', #公司動態
                ]

QuoteItems = [f"{code}.TW-{",".join(QuoteColumns)}" for code in stock_Ids]
Main("Quote", QuoteColumns, QuoteItems, ";")


                # 'CompanyPos', #產業地位
                # 'DetailIndustry', #細產業
                # 'MonthlyNetSalesYoY',    #當月營收YOY
                # 'TFXRatio',              #當月營收MOM
                # 'NetIncomeGrowthRate',   #稅後淨利成長率%
                # 'PERatio',    # PE 
                # 'PBRatio',    # PB 
                # 'Capital',                     #股本
                # 'DateofMeetingofShareHolders', #股東會日
                # 'InvestorConferenceDate',      #法說會日
                # 'PriceChange',                 #漲跌
                # 'MajorOrderBidAskRatio', 
                # 'DXLOrderValueDiffRatio',      #特大單差
                # 'DIndexPtsContributionRate',   #佔大盤比
                # 'MonthReturn',    #1月%
                # 'QuarterReturn',  #一季%
                # 'HalfYearReturn', #半年%
                # 'YearReturn',     #一年%
                # 'RevenueMonth','EstimatedTotalVolume','5DayAvgVol']
                
# HistColumns = ["F001","F002","F009"]
# HistItems = [f"{code}.TW-day-1-{",".join(HistColumns)}" for code in stock_Ids]
# Main("Hist", HistColumns, HistItems, ",")
