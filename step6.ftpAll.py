import _beowFmt as fm
# 提早公佈營收 ####
local_file_path = f"D:/project/stockDataLab/data/json/monthlyRevenue.json"
remote_file_path = 'static/monthlyRevenue.json'
fm.FtpFile(local_file_path, remote_file_path)


