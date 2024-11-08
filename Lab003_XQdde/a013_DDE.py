import pandas as pd
import _beowFmt as fm
import _beowDDE as bwdde
import time


import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import fcluster, linkage
import itertools

# 自定義距離函數：基於百分比的相對差距
def relative_difference(x, y):
    return abs(x - y) / min(x, y)

def permutationIndex():
    return {
 ('a', 'b', 'c', 'd', 'e'):1, ('b', 'a', 'c', 'd', 'e'):2,('c', 'a', 'b', 'd', 'e'):3,  ('d', 'a', 'b', 'c', 'e'):4,  ('e', 'a', 'b', 'c', 'd'):5, 
 ('a', 'b', 'c', 'e', 'd'):6, ('b', 'a', 'c', 'e', 'd'):7,('c', 'a', 'b', 'e', 'd'):8,  ('d', 'a', 'b', 'e', 'c'):9,  ('e', 'a', 'b', 'd', 'c'):10, 
 ('a', 'b', 'd', 'c', 'e'):11, ('b', 'a', 'd', 'c', 'e'):12,('c', 'a', 'd', 'b', 'e'):13,  ('d', 'a', 'c', 'b', 'e'):14,  ('e', 'a', 'c', 'b', 'd'):15, 
 ('a', 'b', 'd', 'e', 'c'):16, ('b', 'a', 'd', 'e', 'c'):17,('c', 'a', 'd', 'e', 'b'):18,  ('d', 'a', 'c', 'e', 'b'):19,  ('e', 'a', 'c', 'd', 'b'):20, 
 ('a', 'b', 'e', 'c', 'd'):21, ('b', 'a', 'e', 'c', 'd'):22,('c', 'a', 'e', 'b', 'd'):23,  ('d', 'a', 'e', 'b', 'c'):24,  ('e', 'a', 'd', 'b', 'c'):25, 
 ('a', 'b', 'e', 'd', 'c'):26, ('b', 'a', 'e', 'd', 'c'):27,('c', 'a', 'e', 'd', 'b'):28,  ('d', 'a', 'e', 'c', 'b'):29,  ('e', 'a', 'd', 'c', 'b'):30, 
 ('a', 'c', 'b', 'd', 'e'):31, ('b', 'c', 'a', 'd', 'e'):32,('c', 'b', 'a', 'd', 'e'):33,  ('d', 'b', 'a', 'c', 'e'):34,  ('e', 'b', 'a', 'c', 'd'):35, 
 ('a', 'c', 'b', 'e', 'd'):36, ('b', 'c', 'a', 'e', 'd'):37,('c', 'b', 'a', 'e', 'd'):38,  ('d', 'b', 'a', 'e', 'c'):39,  ('e', 'b', 'a', 'd', 'c'):40, 
 ('a', 'c', 'd', 'b', 'e'):41, ('b', 'c', 'd', 'a', 'e'):42,('c', 'b', 'd', 'a', 'e'):43,  ('d', 'b', 'c', 'a', 'e'):44,  ('e', 'b', 'c', 'a', 'd'):45, 
 ('a', 'c', 'd', 'e', 'b'):46, ('b', 'c', 'd', 'e', 'a'):47,('c', 'b', 'd', 'e', 'a'):48,  ('d', 'b', 'c', 'e', 'a'):49,  ('e', 'b', 'c', 'd', 'a'):50, 
 ('a', 'c', 'e', 'b', 'd'):51, ('b', 'c', 'e', 'a', 'd'):52,('c', 'b', 'e', 'a', 'd'):53,  ('d', 'b', 'e', 'a', 'c'):54,  ('e', 'b', 'd', 'a', 'c'):55, 
 ('a', 'c', 'e', 'd', 'b'):56, ('b', 'c', 'e', 'd', 'a'):57,('c', 'b', 'e', 'd', 'a'):58,  ('d', 'b', 'e', 'c', 'a'):59,  ('e', 'b', 'd', 'c', 'a'):60, 
 ('a', 'd', 'b', 'c', 'e'):61, ('b', 'd', 'a', 'c', 'e'):62,('c', 'd', 'a', 'b', 'e'):63,  ('d', 'c', 'a', 'b', 'e'):64,  ('e', 'c', 'a', 'b', 'd'):65, 
 ('a', 'd', 'b', 'e', 'c'):66, ('b', 'd', 'a', 'e', 'c'):67,('c', 'd', 'a', 'e', 'b'):68,  ('d', 'c', 'a', 'e', 'b'):69,  ('e', 'c', 'a', 'd', 'b'):70, 
 ('a', 'd', 'c', 'b', 'e'):71, ('b', 'd', 'c', 'a', 'e'):72,('c', 'd', 'b', 'a', 'e'):73,  ('d', 'c', 'b', 'a', 'e'):74,  ('e', 'c', 'b', 'a', 'd'):75, 
 ('a', 'd', 'c', 'e', 'b'):76, ('b', 'd', 'c', 'e', 'a'):77,('c', 'd', 'b', 'e', 'a'):78,  ('d', 'c', 'b', 'e', 'a'):79,  ('e', 'c', 'b', 'd', 'a'):80, 
 ('a', 'd', 'e', 'b', 'c'):81, ('b', 'd', 'e', 'a', 'c'):82,('c', 'd', 'e', 'a', 'b'):83,  ('d', 'c', 'e', 'a', 'b'):84,  ('e', 'c', 'd', 'a', 'b'):85, 
 ('a', 'd', 'e', 'c', 'b'):86, ('b', 'd', 'e', 'c', 'a'):87,('c', 'd', 'e', 'b', 'a'):88,  ('d', 'c', 'e', 'b', 'a'):89,  ('e', 'c', 'd', 'b', 'a'):90, 
 ('a', 'e', 'b', 'c', 'd'):91, ('b', 'e', 'a', 'c', 'd'):92,('c', 'e', 'a', 'b', 'd'):93,  ('d', 'e', 'a', 'b', 'c'):94,  ('e', 'd', 'a', 'b', 'c'):95, 
 ('a', 'e', 'b', 'd', 'c'):96, ('b', 'e', 'a', 'd', 'c'):97,('c', 'e', 'a', 'd', 'b'):98,  ('d', 'e', 'a', 'c', 'b'):99,  ('e', 'd', 'a', 'c', 'b'):100, 
 ('a', 'e', 'c', 'b', 'd'):101, ('b', 'e', 'c', 'a', 'd'):102,('c', 'e', 'b', 'a', 'd'):103,  ('d', 'e', 'b', 'a', 'c'):104,  ('e', 'd', 'b', 'a', 'c'):105, 
 ('a', 'e', 'c', 'd', 'b'):106, ('b', 'e', 'c', 'd', 'a'):107,('c', 'e', 'b', 'd', 'a'):108,  ('d', 'e', 'b', 'c', 'a'):109,  ('e', 'd', 'b', 'c', 'a'):110, 
 ('a', 'e', 'd', 'b', 'c'):111, ('b', 'e', 'd', 'a', 'c'):112,('c', 'e', 'd', 'a', 'b'):113,  ('d', 'e', 'c', 'a', 'b'):114,  ('e', 'd', 'c', 'a', 'b'):115, 
 ('a', 'e', 'd', 'c', 'b'):116, ('b', 'e', 'd', 'c', 'a'):117,('c', 'e', 'd', 'b', 'a'):118, ('d', 'e', 'c', 'b', 'a'):119,  ('e', 'd', 'c', 'b', 'a'):120 }

def convert_and_round(str_value):
    if str_value == '':
        return None
    try:
        # 將字符串轉換為浮點數
        float_value = float(str_value)
        # 將浮點數四捨五入到小數點第二位
        rounded_value = round(float_value, 2)
        return rounded_value
    except ValueError:
        # 如果轉換失敗，返回 None 或其他你希望的值
        return None


def replace_permutations(A, B):
    # 生成 B 代碼的所有排列組合
    permutations = [''.join(p) for p in itertools.permutations(B)]
    TangleLine = ''

    if B == '':
        return A, TangleLine

    # 遍歷所有排列組合，檢查糾結的均線TangleLine是否存在於 A 字串中    
    for perm in permutations:
        if perm in A:
            # 如果存在，則將其替換為 'T'
            A = A.replace(perm, 'T')
            TangleLine = perm
            break  # 只替換第一個匹配的排列組合
    return A, TangleLine

def cal_nearBy(r):
    Price,ema5,ema13,ema50,ema200 = r["成交"], r["ema5"],r["ema13"],r["ema50"],r["ema200"]
    # 定義數列
    data = {
        'a': Price, #日
        'b': ema5,  #週 
        'c': ema13, #月 
        'd': ema50, #季  
        'e': ema200 #年
    }
    values = np.array(list(data.values()))
    labels = list(data.keys())

    # 自定義距離函數：基於百分比的相對差距
    # def relative_difference(x, y):
    #     return abs(x - y) / min(x, y)
    def relative_difference(x, y):
        min_value = min(x, y)
        if min_value == 0:
            return 0  # 返回無窮大，或者你可以選擇返回其他特定值
        return abs(x - y) / min_value

    # 計算距離矩陣
    distances = pdist(values[:, None], relative_difference)

    # 檢查並處理非有限值
    if not np.all(np.isfinite(distances)):
        # 找到非有限值的位置
        non_finite_indices = np.where(~np.isfinite(distances))
        print("Non-finite values found at indices:", non_finite_indices)

        # 替換非有限值為一個有限值（例如，0）
        distances[non_finite_indices] = 0

    # 轉換為方形距離矩陣
    dist_matrix = squareform(distances)

    # 轉換回條件距離矩陣
    condensed_dist_matrix = squareform(dist_matrix, checks=False)

    # 使用層次聚類找到在1%內的群組
    Z = linkage(condensed_dist_matrix, method='single')
    threshold = 0.015  # 1% 差距閾值
    clusters = fcluster(Z, threshold, criterion='distance')

    # 將群組結果映射回標籤
    result_groups = {}
    for i, cluster_id in enumerate(clusters):
        if cluster_id not in result_groups:
            result_groups[cluster_id] = []
        result_groups[cluster_id].append((labels[i], values[i]))

    # 篩選出包含多個元素的群組，並計算每組的平均值
    final_groups = []
    for group in result_groups.values():
        if len(group) > 1:
            group_labels = [item[0] for item in group]
            group_values = [item[1] for item in group]
            average_value = np.mean(group_values)
            final_groups.append((group_labels, average_value))

    # 將所有變數按值排序（由大到小）
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    sorted_data_tuple = tuple(sorted_data)  # 轉換為單一tuple
    # 只提取排序后的標籤 (只保留 'a', 'b', 'c', 'd', 'e' 的部分)
    sorted_labels = tuple(label for label, value in sorted_data)
    
    # 顯示結果
    # print("變數的由大到小排列:")
    sortMa, nearBy, avg = '', '', ''
    # for label, value in sorted_data:
    #     sortMa += f"{label}:{value},"

    # print("\n相距小於 1% 的數值群組及其平均值:")
    for group_labels, avg in final_groups:
        nearBy = group_labels
        avg = avg
    
    permutation_to_index_tuple = permutationIndex()

    A = ''.join(sorted_labels)
    B = ''.join(nearBy)
        # nearBy = f"群組: {group_labels}，平均值為: {avg:.2f}")
    aa, tangle_line = replace_permutations(A, B) 
    r['sortData'] = sorted_data_tuple
    r['sortLabel'] = aa
    r['sortCode'] = permutation_to_index_tuple.get(sorted_labels, "未找到該排列") # 查找該排列的順序編號
    r['nearBy'] = tangle_line
    r['nearByAvg'] = convert_and_round(avg)

    return r['sortData'], r['sortLabel'], r['sortCode'], r['nearBy'], r['nearByAvg']


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
    
    sql = f'"id":{stockId},"n":"{stockName}","k":{k},"j":{jmp},"c":{close},"yc":{yesterdayClose},"v":{totalValue},"vE":{estValue},"amp":{amplitude},"vR":{volRate},"turOv":{turnOver},"ind":"{market}","wts":{whaleSpread},"wtr":{whaleSpreadRatio},"ln":{ln},"roe":{roe},"pe":{pe},"pb":{pb},"yy":{yoy},"mm":{mom},"nt":{net},"dd":"{dvd}","fo":"{info}","gp":"{group}","sh":"{shh}","iv":"{inv}","mn":"{mn}","srlb":"{srlb}","srCd":{srCd},"nrBy":"{nrBy}","nrAvg":"{nrAvg}"'
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
        print(len(stockList))
        # time.sleep(5)
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

        str2Float_columns = ['漲幅%', '成交', '昨收', '開盤', '最低', '最高', '換手率%', '大戶差比', '量比', '融資使用率%']
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
        # print('篩選有效來統計', len(df2))

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


        targe_file = r"webJson\currStockMarket.json"
        ss = ''.join(df_group['json'].fillna('').astype(str))[:-1]
        fm.write_LogFile(targe_file, f"[{ss}]")
        fm.FtpFile(targe_file, 'static/currStockMarket.json')

        #--合併財務資訊--------------------------------------------------------------------------------
        financeData_file = r'webJson\\stock_finance.csv'
        financeData = pd.read_csv(financeData_file, encoding='utf-8')
        financeData = financeData.fillna('')
        financeData.columns = ["id","cap","roe","pe","pb","yoy","mom","net","dvd","info","shh","mm","inv"]
        # print('財務資料', len(financeData))
        df = pd.merge(df, financeData, left_on="ID", right_on="id", how='left')  ## 結合股票名稱
        # print('整併財務', len(df))

        #--合併均線訊號是否糾結?大概在哪個價位反彈? 盤中的反應如何?---------------------------------------
        ema_file = r'webJson\\stock_EMA_All.csv'
        ema_data = pd.read_csv(ema_file, encoding='utf-8')
        ema_data = ema_data.fillna('')
        ema_data.columns = ["ema1","ma_stockId","ema5","ema13","ema50","ema200"]
        del ema_data['ema1']
        # print('均線資料', len(ema_data))
        df = pd.merge(df, ema_data, left_on="ID", right_on="ma_stockId", how='left')   ## left join 股票均線資料
        # print('整併均線', len(df))
        # 篩選出三個欄位同時為 0.0 的列
        # filtered_df = df[(df['成交'] == 0.0) & (df['最低'] == 0.0) & (df['最高'] == 0.0)]
        # print(f'過濾無效資料{len(filtered_df)}筆')
        df[['sortData', 'sortLabel', 'sortCode', 'nearBy', 'nearByAvg']]  = df.apply(cal_nearBy, axis=1, result_type='expand')

        df['mm'] = df['mm'].str.replace('2024/', '') #營收月份 2024/08
        df['json']= df.apply(fmt_xq2json, axis = 1) 
        # print('最後成果', len(df))
        # print(df.head(100))
        # print(df[df['ID']==2421]["sortData"])

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
            'Open': '開盤',
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
            