import pandas as pd
import math

def diffRatio(r):
    w1 , m1, q1, y1 = r["ma5"], r["ma20"], r["ma60"], r["ma240"]
    wmqy_dscr2 = ""                              #有按照大小排列
    dic = { "w" : w1, "m" : m1, "q" : q1, "y": y1 }  #以dict作為排列的工具
    dic2 = { k: v for k, v in sorted( dic.items(), key=lambda item: item[1], reverse = True )}
    wmqy_dscr2 = ",".join(dic2)
    return wmqy_dscr2

def setKbarTop(r):
    return r["close"] if(r["kbar"] == "R") else r["open"]

def setKbarBottom(r):
    return r["close"] if(r["kbar"] == "G") else r["open"]

def isCrossMA5(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma5"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA10(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma10"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA20(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma20"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA60(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma60"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""

def isCrossMA240(r):
    top, bottom, ma, ytop = r["kbar_top"], r["kbar_bottom"], r["ma240"], r["kbar_top_y"]
    return "C" if ( top >= ma and ma >= bottom) else "J" if(bottom >= ma and ma >= ytop) else ""
    
# 判斷上下彎勾 ####################################################
def fmtGetCurvHookMa5(r):
    rs, flagN, _n, _y = "", r["crvFlagMa5"], r["sMa5"], r["sMa5y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa10(r):
    rs, flagN, _n, _y = "", r["crvFlagMa10"], r["sMa10"], r["sMa10y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa20(r):
    rs, flagN, _n, _y = "", r["crvFlagMa20"], r["sMa20"], r["sMa20y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa60(r):
    rs, flagN, _n, _y = "", r["crvFlagMa60"], r["sMa60"], r["sMa60y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtGetCurvHookMa240(r):
    rs, flagN, _n, _y = "", r["crvFlagMa240"], r["sMa240"], r["sMa240y"]
    if (flagN == -1):
        rs = "H" if (_n > _y and _n != _y) else "C"
    return rs

def fmtUpperShadow(r):
    kbar_top, h = r["kbar_top"], r["high"]
    return 0 if (kbar_top == 0) else round((h - kbar_top) / kbar_top * 100, 2)

def fmtLowerShadow(r):
    kbar_bottom, l = r["kbar_bottom"], r["low"]
    return 0 if (l == 0) else round((kbar_bottom - l) / l * 100, 2)

def fmtKbarBody(r):
    kbar_bottom, kbar_top = r["kbar_bottom"], r["kbar_top"]
    return 0 if (kbar_bottom ==0) else round((kbar_top - kbar_bottom) / kbar_bottom * 100, 2)

def fmtAmplitude(r):
    yc, close = r["yc"], r["close"]
    return 0 if (yc ==0) else round((close - yc) / yc * 100, 2)

def fmtCtnC(r):
    yc, close = r["yc"], r["close"]
    return 1 if (yc > close) else 0

#描述價格往上跳空缺口
def fmtIGap(r):
    low, yh, h, ylow= r["low"], r["yh"], r["high"], r["yl"] 
    gap1 = 0 if (math.isnan(yh) or math.isnan(low)) else round(low - yh, 2)
    gap1 = gap1 if(gap1 > 0) else 0
    
    if (gap1 == 0):
        gap2 = 0 if (math.isnan(ylow) or math.isnan(h)) else round(ylow - h, 2)
        return gap2 if(gap2 > 0) else 0
    else:
        return gap1 

def fmtSql_stockParas(r):
    stockId, today, kbar, v, o, c, h, l, yc, iGap, amplitude, k ,d, head, body, footer = r["stockId"], r["today"], r["kbar"], r["volumn"], r["open"], r["close"], r["high"], r["low"], r["yc"], r["iGap"], r["amplitude"], r["k"], r["d"], r["upper-shadow"], r["kbar-body"], r["lower-shadow"]
    k = 0 if (math.isnan(k)) else k
    d = 0 if (math.isnan(d)) else d
    # insert into dbo.StockParas (stockId, closeDate,kbar, v, o, c, h, l, yc,iGap,amplitude,k,d) values 
    sql = f"""('{stockId}','{today}','{kbar}',{v},{o},{c},{h},{l},{yc},{head},{body},{footer},{iGap},{amplitude},{k},{d}) """
    return sql

def fmtSql_stockMA(r):
    stockId, today, kbar, ma_dscr           = r["stockId"], r["today"], r["kbar"], r["ma_dscr"]
    ma5, ma7, ma10, ma20, ma60, ma240       = r["ma5"], r["ma7"], r["ma10"], r["ma20"], r["ma60"], r["ma240"]
    maF5, maF10, maF20, maF60, maF240       = r["maF5"], r["maF10"], r["maF20"], r["maF60"], r["maF240"]
    maS5, maS10, maS20, maS60, maS240       = r["sMa5a"], r["sMa10a"], r["sMa20a"], r["sMa60a"], r["sMa240a"]   #計算斜率
    d_ma5, d_ma10, d_ma20, d_ma60, d_ma240  = r["d_ma5"], r["d_ma10"], r["d_ma20"], r["d_ma60"], r["d_ma240"]
    
    # ma5 = 0 if (math.isfinite(ma5)) else ma5
    # ma10 = 0 if (math.isfinite(ma10)) else ma10
    # ma20 = 0 if (math.isfinite(ma20)) else ma20
    # ma60 = 0 if (math.isfinite(ma60)) else ma60
    # ma240 = 0 if (math.isfinite(ma240)) else ma240

    # maS5 = 0 if (math.isfinite(maS5) or math.isinf(maS5)) else maS5
    # maS10 = 0 if (math.isfinite(maS10) or math.isinf(maS10)) else maS10
    # maS20 = 0 if (math.isfinite(maS20) or math.isinf(maS20)) else maS20
    # maS60 = 0 if (math.isfinite(maS60) or math.isinf(maS60)) else maS60
    # maS240 = 0 if (math.isfinite(maS240) or math.isinf(maS240)) else maS240


    #insert into dbo.StockMA (stockId, closeDate,kbar,ma_dscr, ma5, ma7, ma10, ma20, ma60, ma240, d_ma5, d_ma10, d_ma20, d_ma60, d_ma240, maF5, maF10, maF20, maF60, maF240) values 
    sql = f"""({stockId},'{today}','{kbar}','{ma_dscr}',{ma5},{ma7},{ma10},{ma20},{ma60},{ma240},'{d_ma5}','{d_ma10}','{d_ma20}','{d_ma60}','{d_ma240}','{maF5}','{maF10}','{maF20}','{maF60}','{maF240}',{maS5},{maS10},{maS20},{maS60},{maS240}) """
    return sql

def fmtSql_Volumn(r):
    stockId, dt, fc, ic, dealer, yv, v, ma5, ma20, ma60 = r["stock_id"], r["dt"], r["_fc"], r["_ic"],r["_dc"], r["yv"], r["v"], r["ma5"], r["ma20"], r["ma60"]
    #"insert into volumn(stockId,closeDate,fc,ic,dealer,accu_fc,accu_ic,k_fc,k_ic,yv,v,ma5,ma20,ma60) values 
    sql = f"('{stockId}','{dt}',{fc},{ic},{dealer},0,0,0,0,{yv},{v},{ma5},{ma20},{ma60})"                # Python 語法解析器把 f-string
    return sql

def fmtSQL_maxMMRevenue(r):
    stockId, nowDate, nowRvn, lastMaxDt, lastMaxV = r["stockId"], r["nowDt"], r["now"], r["max2Dt"], r["max2"]

    return f"""if (select count(*) from maxMMRevenue where stockId={stockId} and nowDate='{nowDate}') = 0
    begin insert into maxMMRevenue (stockId,nowDate,nowRvn,lastMaxDate,lastMaxRvn,createdDate) values ('{stockId}','{nowDate}',{nowRvn},'{lastMaxDt}',{lastMaxV},getdate());  end
    """
    
def fmtSql_capital(r):
    stockId, cap = r["stockId"], r["cap"]
    return f"update stock set capital={cap},modifiedDate=getdate() where id='{stockId}'"

def fmt_all_infor_stock(r):
    id, market, open, close, estVolume, amp, jumpRate, vR, inV, vMM, vHYY = r["id"], r["market"], r["open"], r["close"], r["預估量"], r["amp"], r["jumpRate"], r["量比"], r["周轉率"], r["月量比"], r["半年量比"]
    ss = f'"id":{id},"mk":"{market}","o":{open},"c":{close},"v":{estVolume},"amp":{amp},"jR":{jumpRate},"vR":{vR},"inV":{inV},"vMM":{vMM},"vYY":{vHYY}'
    return ss

import os
import codecs 

def write_LogFile(fileName, write_content):
    os.makedirs(os.path.dirname(fileName), exist_ok=True)
    f = codecs.open(fileName, mode="w", encoding="utf-8", errors="strict")
    f.write(write_content)
    f.close()

def getLastFileDate(directory, trimStr):

    # 列出目錄中的所有檔案
    items = os.listdir(directory)

    # 過濾出只有檔案的項目，並提取檔案名稱部分
    files = [os.path.splitext(item)[0] for item in items if os.path.isfile(os.path.join(directory, item))]

    # 對檔案名稱進行排序
    sorted_files = sorted(files)

    # 取得排序後的檔案名稱中的最後一個（最大的）
    max_filename = sorted_files[-1]
    lastFileDate = max_filename.removeprefix(trimStr) #例如：ma_20230622 只取出20230622
    print("最新的檔案日期：", lastFileDate)
    return lastFileDate

def getLast2FileDate(directory, trimStr):

    # 列出目錄中的所有檔案
    items = os.listdir(directory)

    # 過濾出只有檔案的項目，並提取檔案名稱部分
    files = [os.path.splitext(item)[0] for item in items if os.path.isfile(os.path.join(directory, item))]

    # 對檔案名稱進行排序
    sorted_files = sorted(files)

    # 取得排序後的檔案名稱中的最後一個（最大的）
    max_filename = sorted_files[-2]
    lastFileDate = max_filename.removeprefix(trimStr) #例如：ma_20230622 只取出20230622
    print("次新的檔案日期：", lastFileDate)
    return lastFileDate


def lastFinlabStockIdList(positionData):
    dff = positionData.iloc[-1:].transpose()
    dff["stock"] = dff.index
    dff.columns = ["val", "stock"]
    df2 = dff[ (dff["val"] == True) & (dff["stock"].str.len() == 4)].dropna(axis = 0, how ='any')
    # print(df2)
    return df2.index.tolist()

def fmtSql_stockb(r):
    stockId, dt, v, o, c, h, l = r["id"], r["dt"], r["volume"], r["open"], r["close"], r["high"], r["low"]
    # insert into dbo.StockParas (stockId, dt, v, o, c, h, l) values 
    sql = f"""('{stockId}','{dt}',{v},{o},{c},{h},{l})"""
    return sql

import ftplib
import time
def FtpFile(local_file_path, remote_file_path):
    try:
        # 設定遠端主機的FTP資訊
        hostname = 'win5181.site4now.net'
        username = 'danielchou-beow2'
        password = 'Apple005'
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



from datetime import date

def trans2CSVfile(df, filePath):
    dff = df.iloc[-1:].transpose()
    dff["stockId"] = dff.index
    dff.columns = ["val", "stockId"]
    dff = dff[ (dff["stockId"].str.len() == 4) & (dff["val"] == True) ]

    nowDate, ss = date.today().strftime("%Y%m%d"), ''
    print(f"匯出共 {len(dff)} 檔股票")
    for c in dff["stockId"].tolist():
        ss += f"{c}.TW,"
    write_LogFile(f"{filePath}{nowDate}.csv", ss) 

