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

