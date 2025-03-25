import finlab
finlab.login(open("config.txt", "r").read())
from finlab import data
from finlab.data import indicator
import pandas as pd
import time
import json 

import _beowDDE as bwdde

pd.reset_option('display.max_rows')
pd.set_option('display.max_rows', 300)
pd.set_option('display.width', 280)

today, s1 = time.strftime("%Y%m%d_%H%M", time.localtime()) , ""

data.use_local_data_only = False

iStart = -880
vols   = data.get("price:成交股數").astype(float)[iStart: ]
vols = vols/1000

print(vols["2317"])

def find_volume_rank(stock_id, target_volume, vols_df=vols):
    """
    找出給定成交量是最近幾天內的最大值
    
    參數:
    stock_id (str): 股票代號
    target_volume (float): 目標成交量（單位：千股）
    vols_df (pd.DataFrame): 成交量資料框架
    
    回傳:
    int: 該成交量是最近幾天內的最大值，如果不是最大值則回傳 -1
    """
    if stock_id not in vols_df.columns:
        return -1
    
    stock_vols = vols_df[stock_id].dropna()  # 移除空值
    if len(stock_vols) == 0:
        return -1
    
    # 從最新的資料開始往前找
    latest_vols = stock_vols.sort_index(ascending=False)
    
    # 如果目標成交量小於最新成交量，直接返回-1
    if target_volume < latest_vols.iloc[0]:
        return -1
    
    for i, vol in enumerate(latest_vols):
        if vol > target_volume:
            return i
    
    return len(latest_vols)  # 如果是整個期間最大值

def analyze_volume_patterns(df_estVols, vols_data):
    """
    分析股票的成交量模式，找出最近的大量成交日
    
    Parameters:
    -----------
    df_estVols : DataFrame
        包含股票ID、量比、估計量、總量和大戶差2的DataFrame
    vols_data : Series
        歷史成交量數據
        
    Returns:
    --------
    DataFrame
        包含原始數據以及最近大量成交日資訊的DataFrame
    """
    results = []
    
    for _, row in df_estVols.iterrows():
        stock_id = row['ID']
        current_vol = row['總量']
        
        # 取得該股票的歷史成交量
        stock_vols = vols_data.get(f"price:{stock_id}:成交股數")
        if stock_vols is None:
            continue
            
        # 轉換成千股並加入當前成交量
        stock_vols = stock_vols[800:].astype(float) / 1000
        all_vols = pd.concat([stock_vols, pd.Series([current_vol])])
        
        # 從最後一天（當前成交量）往前找大量
        last_vol = all_vols.iloc[-1]
        days_since_last_high_vol = 0
        found_high_vol = False
        
        for i, vol in enumerate(all_vols.iloc[:-1][::-1]):  # 反向遍歷，排除最後一天
            if vol >= last_vol:
                days_since_last_high_vol = i + 1  # +1 因為我們從倒數第二天開始算
                found_high_vol = True
                break
        
        result_dict = row.to_dict()
        result_dict['上次大量距今天數'] = days_since_last_high_vol if found_high_vol else -1
        results.append(result_dict)
    
    return pd.DataFrame(results)

# 使用範例
if __name__ == "__main__":
    # 假設我們要檢查鴻海(2317)今天的成交量
    stock_id = "2317"
    today_vol = vols[stock_id].iloc[-1]  # 取得最新的成交量
    days = find_volume_rank(stock_id, today_vol)
    
    if days > 0:
        print(f"{stock_id} 今天成交量 {today_vol:.0f}K股是 {days} 個交易日以內最大的成交量")
    else:
        print(f"{stock_id} 今天成交量 {today_vol:.0f}K股不是近期最大值")