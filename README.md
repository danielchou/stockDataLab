# genTableSchema
Generating the sql table schema and store procedure by configuration in excel sheet.

# 版本資訊
- 2025/06/09: 更新 .gitignore 文件，增加更多忽略項目
- 2025/02/22: 更新 finlab 套件從 1.1.1 至 1.2.20 版本

# 功能說明

## Git 版本控制

### .gitignore 設定
專案中的 `.gitignore` 文件已更新，包含以下主要類別的忽略項目：

- **配置文件**：敏感資訊如 API 金鑰和環境變數
- **數據目錄**：各種數據資料夾和數據庫文件
- **虛擬環境**：`dev-finlab` 及其他虛擬環境目錄
- **Python 相關文件**：編譯文件、緩存和構建目錄
- **編輯器和 IDE 文件**：如 `.idea/`、`.vscode/` 等
- **日誌文件**：所有日誌文件和目錄
- **備份文件**：臨時和備份文件

## 股票資訊輸出
- 支援將股票資訊輸出為 JSON 格式
- 輸出檔案位置：`webJson/stock_category.json`
- 輸出格式：以類股(cg)為 key，股票名稱陣列為 value 的 JSON 物件
  ```json
  {"塑化":["台塑","南亞","台聚"],"半導體":["台積電","聯電","世界"]}
  ```
