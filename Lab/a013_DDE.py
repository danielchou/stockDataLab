import win32ui
import win32gui
import dde
import pandas as pd
import _beowFmt as fm 

# 設置顯示選項
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 480)  # 設置顯示寬度
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
    return round(number, 2)

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
    stockId, stockName,k, low, close, yesterdayClose, amplitude, estValue, totalValue, volRate, turnOver, roe, ioRate, market, vMa5, mur, whaleSpread, info = r["代碼"], r["商品"], r["多空"], r["最低"], r["成交"], r["昨收"], r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["換手率%"], r["ROE%"], r["內外盤%"], r["market"], r["五日量比"], r["融資使用率%"], r["大戶差2"], r["公司動態"]
   
    mur = 0 if (mur == '--') else mur   #Margin Utilized Ratio 融資使用率
    roe = 0 if (roe == '--') else roe
    low = 0 if (low == '--') else low
    close = 0 if (close == '--') else close
    yesterdayClose = 0 if (yesterdayClose == '--') else yesterdayClose
    ioRate = 0 if (ioRate == '--') else ioRate
    estValue = 0 if (estValue == '--') else estValue
    info = '' if (info == '-') else info

    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"l":{low},"c":{close},"yc":{yesterdayClose},"amp":{amplitude},"estV":{estValue},"tV":{totalValue},"vR":{volRate},"turOv":{turnOver},"roe":{roe},"ioR":{ioRate},"ind":"{market}","v5":{vMa5},"mur":{mur},"wts":{whaleSpread},"info":"{info}"'
    return "{" + sql + "},"

def fmt_group_json(r):
    market, vrMean, vrMax, turnOverMean, k, count, details = r['market'], r['平均量比'],r['最大量比'], r['換手率%'], r['多空'], r['筆數'], r['相關股票明細']
        
    sql = f'"market":"{market}","vmn":{vrMean},"vmx":{vrMax},"tov":{turnOverMean},"k":{k},"cc":{count},"dls":"{details}"'
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
            'Low': '最低',
            'ROE': 'ROE%',
            'InOutRatio': '內外盤%',
            'EstimatedTotalVolume': '估計量',
            '5DayAvgVol': '五日均量',
            'FinanceUsedRatio': '融資使用率%',
            'ChipsField25': '除息日',
            'DetailIndustry':'細產業',
            'CompanyNews':'公司動態',
            })
        # print(df)

        # 將百分比列轉換為浮點數
        df['ID'] = df['代碼'].astype(int)
        df['內外盤%'] = df['內外盤%'].str.replace('%', '')
        df['漲幅%'] = df['漲幅%'].str.replace('%', '').str.replace('+', '').str.replace('--','0')
        df['漲幅%'] = df['漲幅%'].astype(float)
        df['換手率%'] = df['換手率%'].str.replace('--','0').astype(float)
        df['量比'] = df['量比'].astype(float)
        df['總量'] = pd.to_numeric(df['總量'])
        df['總量'] = df['總量'].astype(int)
        df['多空'] = df['漲幅%'].apply(lambda x: 1 if x > 0 else 0)
        df['大戶差2'] =df['大戶差'].apply(to_billion)           #全部改以億為單位
        df['五日量比'] = df.apply(lambda r: round(float(r['總量']) / float(r['五日均量']), 2) if r['估計量'] == '--' and float(r['五日均量']) != 0 else
                           round(float(r['估計量']) / float(r['五日均量']), 2) if float(r['五日均量']) != 0 else
                           0, axis=1)
        # df['estV%'] = df['ROE%'].astype(float)
        # df['產業2'] = df['細產業'].apply(get_first_item)
        # del df['細產業']
        # df['量比B'] = df['量比'] + df['五日量比']*1/3 
        
        #--合併產業資訊---------------------------------------------------------------
        stock_group_file = r"D:\project\stockDataLab\Lab\data\webJson\stock_group.csv"
        stockMarket = pd.read_csv(stock_group_file)
        stockMarket.columns = ["name","id","market"]
        # print(stockMarket.head())
        
        df = pd.merge(df, stockMarket, left_on="ID", right_on="id")  ## 結合股票名稱
        
        grouped = df.groupby(['market','多空']).agg({
            '量比': ['mean','max','count'],
            '換手率%': ['mean']
        })
        grouped.columns = ['平均量比','最大量比', '筆數', '換手率%']
        grouped = grouped.round(2)
        # 添加一個欄位來標記換手率是否大於0
        
        df_group = grouped[grouped['平均量比'] > 1.8].sort_values(by='平均量比', ascending=False)
        # 統計題材之後，產出對應的股票名稱，可快速瀏覽...
        df_group['相關股票明細'] = df.groupby(['market','多空'])['商品'].apply(lambda x: ','.join(x))
        # 重置索引，使market成為一個欄位
        df_group = df_group.reset_index()
        df_group['json'] = df_group.apply(fmt_group_json, axis=1)
        # print(df_group)

        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currStockMarket.json"
        ss = ''.join(df_group['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')
        

        # print("\nProcessed data:")
        # print(df.head())

        df['json']= df.apply(fmt_xq2json, axis = 1) 
        #產出json資料到WebJson目錄下
        targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currentMaxValue.100.json"
        ss = ''.join(df['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]") 
        # 送出到網站
        fm.FtpFile(targe_file, 'static/currentMaxValue.100.json')
    else:
        print("Failed to fetch data")



# 假設我們有100個股票代碼，這裡只列出了5個作為示例 
# stock_codes = ["2312","4510","1617","5426","2405","6218","1618","1616","3013","8105","3712","9105","2349","4533","3047","2474","3029","6788","5309","1608","3060","2888","6806","9938","3260","3685","6143","6603","6805","6016","3673","2834","1612","8096","6841","5475","6546","1319","4160","3711","8111","3312","4915","8059","3149","2025","1609","2382","5351","2867","6117"]
               
stock_codes = ["2312","4510","1617","5426","2405","6218","1618","1616","3013","8105","3712","9105","2349","4533","3047","2474","3029","6788","5309","1608","3060","2888","6806","9938","3260","3685","6143","6603","6805","6016","3673","2834","1612","8096","6841","5475","6546","1319","4160","3711","8111","3312","4915","8059","3149","2025","1609","2382","5351","2867","6117","4956","2353","6782","3491","3622","4768","4123","3706","1528","1524","2385","2347","2392","5425","6026","4167","2449","2387","8112","6235","6005","4707","4977","2201","6643","3217","3014","1909","2367","3710","3265","8046","8277","2327","5474","2442","6116","2408","2547","2892","5469","1603","3050","2851","8935","6120","2439","4532","3686","3535","9955","1312","1304","1540","5381","1308","6411","9945","1529","1611","1313","3702","1110","2915","2905","2409","4157","9941","6151","3049","2027","6462","9904","6442","8390","2103","6264","3189","2399","1477","5347","9103","9921","2890","1301","1605","3019","1905","1303","2404","2515","2633","2108","1305","1440","6215","1718","4109","2489","1710","2104","2383","2006","6505","2061","1597","3714","6592","2903","1309","6477","1102","4938","1326","2477","3008","8054","8299","1316","4714","3607","6015","2317","4726","2379","2886","1310","2406","3362","1717","3645","3339","1444","6869","8076","1456","8064","5443","8028","1783","2607","6197","1455","2601","4142","3376","2419","1711","1784","4916","1802","2838","2641","2897","3147","4919","6550","6163","5512","1709","6021","4566","2524","1720","5515","2645","2606","1789","3188","5905","2609","3380","2360","8104","2883","2009","3583","2467","9933","2534","2371","6288","2539","1702","2617","1799","2451","6605","3051","5608","4414","2836","3576","3489","2889","1582","2812","9907","4976","8926","1449","3211","9902","8069","9906","1808","4968","1229","2002","3293","2912","3033","3406","3006","2530","1216","5234","3081","2357","5876","1584","2884","3533","6451","3338","3016","2352","6285","2882","1217","6176","5009","2376","3036","6415","2454","6669","2328","3034","2330","1409","2887","9939","2332","4958","5483","6284","2880","2301","2206","2337","2809","2049","3231","2308","3030","4113","2303","5439","9802","2331","3024","6274","2329","2455","3689","6180","6133","5213","4933","3229","3443","4306","6147","1314","1806","3209","3450","3105","3518","2511","6531","1210","6239","6219","4564","4303","3675","2070","2801","2316","2881","2062","3661","2545","5522","5531","6768","9946","2528","3078","2855","2393","4763","5225","6188","2542","3056","3035","2731","4562","2548","4903","3374","4513","2501","2438","5508","5534","2520","5452","3708","8011","9958","8464","2506","2388","8374","6684","6187","2031","2536","3290","2344","3715","3321","2615","3167","3548","3005","2107","2596","2486","6191","8050","3663","8201","6231","2495","4402","3044","5864","6412","2436","3042","3228","6257","1560","2603","6121","3703","2476","2020","3313","6446","5388","3466","2359","1519","1536","3322","2348","5871","2059","8110","2891","1503","9934","1453","2204","4729","3481","8927","9914","2492","8039","4720","2363","6153","8936","5525","6548","5364","8440","1436","6271","3230","3498","6706","3037","6127","2368","8210","4960","2313","6177","8070","3631","4526","5328","4907","2362","3284","8086","1463","6125","6640","2324","1522","2421","2351","5392","1569","3624","3665","6189","2614","1447","3048","1454","2374","9940","1714","2464","5880","3045","4906","5371","2634","6425","1442","2543","2913","2355","2365","8071","4967","1438","8996","5484","2613","6789","4904","2236","8027","2458","2845","4927","3653","2402","2412","4961","1513","2610","1722","6698","1101","1504","6126","2885","3324","3017"]


 # 假設每個項目是一個字符串，包含所有字段
QuoteColumns = ['ID', 'Name',  'Price',
                'VolumeRatio', 
                'TurnoverRatio',  #換手%
                'PriceChangeRatio', #漲幅%
                'DLOrderValueDiffRatio', #大單差%
                'MajorOrderDif', #大戶差
                'TotalVolume',      #總量
                'PreClose',         #昨收
                'Low',
                'ROE',
                'InOutRatio', #內外盤%
                'EstimatedTotalVolume', #估計量
                '5DayAvgVol', #五日均量
                'FinanceUsedRatio', #融資使用率%
                'ChipsField25', #除息日
                # 'DetailIndustry', #細產業
                'CompanyNews', #公司動態
                ]
                # 'PriceChange', #漲跌
                # 'MajorOrderBidAskRatio', 
                # 'DXLOrderValueDiffRatio', #特大單差
                # 'DIndexPtsContributionRate', #佔大盤比
                # 'CompanyPos', #產業地位
                # 'MonthReturn',    #1月%
                # 'QuarterReturn',  #一季%
                # 'HalfYearReturn', #半年%
                # 'YearReturn',     #一年%
                # 'RevenueMonth','EstimatedTotalVolume','5DayAvgVol']

QuoteItems = [f"{code}.TW-{",".join(QuoteColumns)}" for code in stock_codes]
Main("Quote", QuoteColumns, QuoteItems, ";")


# HistColumns = ["F001","F002","F009"]
# HistItems = [f"{code}.TW-day-1-{",".join(HistColumns)}" for code in stock_codes]
# Main("Hist", HistColumns, HistItems, ",")
