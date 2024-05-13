from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd
import time
import asyncio
import os
import re


async def getYuantaETFDataAsync(stockId):
    url = f"https://www.yuantaetfs.com/product/detail/{stockId}/ratio"
    driver = webdriver.Chrome() # 使用Selenium启动一个浏览器
    driver.get(url)

    # 等待具有特定class属性的div标签出现并点击
    wait = WebDriverWait(driver, 9)
    div_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.moreBtn")))
    div_element.click()

    html_content = driver.page_source

    # 使用Beautiful Soup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser') #使用解析器 html5libhtml.parser (python內建)
    rows = soup.select('div.table div.tbody div.tr')

    eft_data = []
    for row in rows:
        cols = row.find_all('div', class_='td')
        if len(cols) == 4:
            product_code = cols[0].text.strip().split(" ")[1]  # 商品代碼
            product_name = cols[1].text.strip().split(" ")[1]  # 商品名稱
            product_quantity = int(int(cols[2].text.strip().split(" ")[1])/1000)  # 商品數量
            product_weight = cols[3].text.strip().split(" ")[1]  # 商品權重
            eft_data.append({'代碼': product_code, '名稱': product_name, '數量': product_quantity, '權重': product_weight})

    df = pd.DataFrame(eft_data) # 将字典列表转换为 DataFrame
    # print(df)


    rootPath= "D:/project/finlabexportdata/Lab001_ETF"  #已經改過
    nowDate = time.strftime("%Y%m%d", time.localtime())
    df.to_csv(f"{rootPath}/data/{stockId}/{nowDate}.csv", index=False, sep='\t') #儲存成CSV

    driver.quit() # 关闭浏览器


async def getAllEtfData(stockId):
# 設置 CSV 檔案目錄
    # read_csv_dir = f"D:/project/finlabexportdata/Lab001_ETF/data/{stockId}"
    # write_csv_dir = f"D:/project/finlabexportdata/Lab001_ETF/data/compared/{stockId}"

    read_csv_dir = f"data/{stockId}"
    write_csv_dir = f"data/compared/{stockId}"

    # 初始化一個空的 DataFrame
    merged_data = pd.DataFrame()

    # 讀取每個 CSV 檔案並合併
    for file in os.listdir(read_csv_dir):
        if file.endswith('.csv'):  # 排除包含 2024 年份的檔案
            # 使用正則表達式提取檔案名稱中的 MMDD
            match = re.search(r'(\d{4})(\d{2})(\d{2})', file)
            if match:
                mmdd = match.group(2) + match.group(3)
                file_path = os.path.join(read_csv_dir, file)
                df = pd.read_csv(file_path, delimiter='\t', header=None, skiprows=[0], names=['代碼', '名稱', '數量', '權重'])
                df.set_index(['代碼', '名稱'], inplace=True)
                merged_data[mmdd] = df['數量']

    # 創建一個新的欄位存儲最後兩個數量的差值
    merged_data['差值'] = merged_data.iloc[:, -1] - merged_data.iloc[:, -2]
    # 按照差值由大到小排列整個 DataFrame
    sorted_data = merged_data.sort_values(by='差值', ascending=False)

    # 刪除 'V' 欄位
    # sorted_data.drop(columns=['V'], inplace=True)
    # print(sorted_data)

    # from datetime import datetime #, timedelta
    # todayFile = datetime.today().strftime("%Y%m%d")                 # 取得今天的日期
    df = pd.DataFrame(sorted_data) # 将字典列表转换为 DataFrame
    df.to_csv(f"{write_csv_dir}.csv", index=True, sep='\t') #儲存成CSV


async def main():
    # await getYuantaETFDataAsync('00940')
    # await getYuantaETFDataAsync('0050')
    # await getYuantaETFDataAsync('0056')

    await getAllEtfData('00940')
    await getAllEtfData('0050')
    await getAllEtfData('0056')
