@echo off
REM 設置Python路徑（如果Python未添加到系統PATH中）
REM set PATH=C:\Path\To\Python;%PATH%

:loop
REM 呼叫Python腳本
C:\Users\danie\AppData\Local\Programs\Python\Python312\python.exe D:\project\stockDataLab\Lab\a013_DDE.py

REM 等待30秒
timeout /t 30 /nobreak

REM 返回循環開始處
goto loop
