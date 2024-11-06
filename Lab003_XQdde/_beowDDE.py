import win32ui
import win32gui
import dde
import time
import pandas as pd

def fetch_dde_data(service, topic, item):
    try:
        dde_client = dde.CreateServer()
        dde_client.Create("MyClient")
        
        conversation = dde.CreateConversation(dde_client)
        conversation.ConnectTo(service, topic)
        
        # 請求數據
        result = conversation.Request(item)
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # 清理 DDE 連接
        dde_client.Destroy()

# ---20240824 for DDE專案使用-------------------------------------------------------------
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
        dde_client.Create("MyClient2222")
        
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