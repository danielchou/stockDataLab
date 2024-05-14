import ftplib
import time
import os

def upload_file_to_ftp(hostname, username, password, local_file_path, remote_file_path):
    try:
        # 連線到遠端FTP伺服器
        ftp = ftplib.FTP(hostname)
        ftp.login(username, password)

        # 設定檔名的編碼格式
        ftp.encoding = 'utf-8'

        # 以二進制模式開啟本地檔案
        with open(local_file_path, 'rb') as file:
            # 使用FTP的STOR命令上傳檔案
            ftp.storbinary('STOR ' + remote_file_path, file)

        print(f"成功上傳檔案至 {hostname} 的 {remote_file_path}")
    except ftplib.all_errors as e:
        print(f"上傳失敗：{e}")
    finally:
        # 關閉FTP連線
        ftp.quit()

# 設定遠端主機的FTP資訊
hostname = 'win5181.site4now.net'
username = 'danielchou-beow2'
password = 'Apple005'

# 設定本地檔案路徑和遠端檔案路徑
o_nowDate = time.strftime("%Y%m%d", time.localtime()) 
print(o_nowDate)
current_path = os.getcwd()
local_file_path = f"{current_path}/data/json/turnover_{o_nowDate}.json"
remote_file_path = 'static/turnover_20240105.json'
upload_file_to_ftp(hostname, username, password, local_file_path, remote_file_path) # 呼叫上傳檔案函式

# 開收、跳空、Kbar、預估量、周轉率資料
local_file_path = f"{current_path}/data/json/all_info.json"
remote_file_path = 'static/all_info.json'
upload_file_to_ftp(hostname, username, password, local_file_path, remote_file_path)
