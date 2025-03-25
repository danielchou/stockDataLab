# genTableSchema
Generating the sql table schema and store procedure by configuration in excel sheet.

# 版本資訊
- 2025/02/22: 更新 finlab 套件從 1.1.1 至 1.2.20 版本

# 功能說明

## 股票資訊輸出
- 支援將股票資訊輸出為 JSON 格式
- 輸出檔案位置：`webJson/stock_category.json`
- 輸出格式：以類股(cg)為 key，股票名稱陣列為 value 的 JSON 物件
  ```json
  {"塑化":["台塑","南亞","台聚"],"半導體":["台積電","聯電","世界"]}
  ```
