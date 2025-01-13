# 換乘公寓 (love apartment)

# 重點
## 步驟還沒搞清楚

### 筆記
- 讓NPC一直跑直到可以使用到物件或沒有 暫時記憶
- 動作生成整合 直接生出互動物件
- 模型生成處理丟佇列
- 地圖物件只需要輸入有什麼物件 不用輸入數字

- 架構

(larry)
- 檢索意義函數
- 發起話題
- 動作轉座標

### 模型選用
- Qwen/Qwen2.5-3B-Instruct
- THUDM/glm-4-9b-chat (要用ollama搞參數較小的模型)

### 例行行程
- daily_routine
- 輸入人物記憶
```json
{
    "time": "07:00", "action": "起床，刷牙、吃早餐",
    "time": "08:30", "action": "去Willow Market藥房上班",
    "time": "12:00", "action": "午餐",
    "time": "13:00", "action": "繼續工作",
    "time": "17:00", "action": "下班回家",
    "time": "18:00", "action": "晚餐",
    "time": "20:00", "action": "開始跑步"
}
```

### 決定動作
- design action
- 輸入人物動作歷史、記憶、行程、觀察、當前地點、現在時間
```json
{
    "location": "藥房",
    "action": "開始檢查藥房庫存清單"
}
```

### 對話

### 整理記憶

### 反思