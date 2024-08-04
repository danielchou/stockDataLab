import pandas as pd
import win32com.client
import os
import _beowFmt as fm 

# pd.set_option('display.unicode.ambiguous_as_wide', True)
# pd.set_option('display.unicode.east_asian_width', True)
# pd.set_option('display.width', 380)  

def save_excel_file(file_path):
    # 獲取檔案的絕對路徑
    abs_path = os.path.abspath(file_path)
    
    # 創建 Excel 應用程式對象
    excel = win32com.client.Dispatch("Excel.Application")
    excel.DisplayAlerts = False  # 禁用警告和提示框
    excel.Visible = False  # 隐藏Excel应用程序窗口

    try:
        # 開啟工作簿
        wb = excel.Workbooks.Open(abs_path)
        
        # 儲存並關閉
        wb.Save()
        wb.Close()
        
        print(f"檔案 {file_path} 已成功儲存。")
    except Exception as e:
        print(f"儲存檔案時發生錯誤: {str(e)}")
    finally:
        # 確保 Excel 應用程式被關閉
        excel.Quit()

def get_first_item(text):
    if ',' in text:
        return text.split(',')[0]
    return text


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


def fmt_xq2json(r):
    stockId, stockName, low, close, yesterdayClose, amplitude, estValue, totalValue, volRate, turnOver, roe, ioRate, industry, vMa5, mur, whaleSpread, info = r["代碼"], r["商品"], r["最低"], r["成交"], r["昨收"], r["漲幅%"], r["估計量"],r["總量"], r["量比"], r["換手率%"], r["ROE%"], r["內外盤比圖"], r["產業2"], r["五日量比"], r["融資使用率%"], r["大戶差2"], r["公司動態"]
   
    mur = 0 if (mur == '--') else mur   #Margin Utilized Ratio 融資使用率
    roe = 0 if (roe == '--') else roe
    estValue = 0 if (estValue == '--') else estValue
        
    sql = f'"id":{stockId},"n":"{stockName}","l":"{low}","c":{close},"yc":{yesterdayClose},"amp":{amplitude},"estV":{estValue},"tV":{totalValue},"vR":{volRate},"turOv":{turnOver},"roe":{roe},"ioR":{ioRate},"ind":"{industry}","v5":{vMa5},"mur":{mur},"wts":{whaleSpread},"info":"{info}"'
    return "{" + sql + "},"

def filter_stocks(file_path):
    # 首先儲存 Excel 檔案
    save_excel_file(file_path)
    # 讀取 Excel 文件
    df = pd.read_excel(file_path)
    
    # 將百分比列轉換為浮點數
    df['漲幅%'] = df['漲幅%'].astype(float)
    # df['estV%'] = df['ROE%'].astype(float)
    
    # 應用篩選條件
    df['產業2'] = df['細產業'].apply(get_first_item)
    df['大戶差2'] =df['大戶差'].apply(to_billion)           #全部改以億為單位
    df['五日量比'] = df.apply(lambda r: round(float(r['總量']) / float(r['五日均量']),2) if r['估計量'] == '--' else round(float(r['估計量']) / float(r['五日均量']),2), axis=1)

    # 顯示結果
    df['json']= df.apply(fmt_xq2json, axis = 1) 
    
    # df[(df['漲幅%'] > 2) & (df['量比'] > 2) & (df['ROE%'] > 1)]
    # result = df[['代碼', '商品', '成交', '漲幅%', '量比','換手率%', 'ROE%','內外盤比圖','產業2','五日均量','融資使用率%']].sort_values(["量比","換手率%"], ascending=False)
    result = df[["json"]]
    return result

# 使用函數
file_path = r"D:\project\stockDataLab\Lab\量比大100a.xlsx"
filtered_stocks = filter_stocks(file_path)

# 打印結果
# print(filtered_stocks.head())

current_path = os.getcwd()
targe_file = r"D:\project\stockDataLab\Lab\data\webJson\currentMaxValue.100.json"
ss = ''.join(filtered_stocks['json'].fillna('').astype(str))[:-1]
fm.write_LogFile(targe_file, f"[{ss}]") 

remote_file_path = 'static/currentMaxValue.100.json'
fm.FtpFile(targe_file, remote_file_path)