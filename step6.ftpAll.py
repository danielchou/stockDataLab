import _beowFmt as fm
import os

current_path = os.getcwd()
# 提早公佈營收 ####
local_file_path = f"{current_path}/data/json/monthlyRevenue.json"
remote_file_path = 'static/monthlyRevenue.json'
fm.FtpFile(local_file_path, remote_file_path)


