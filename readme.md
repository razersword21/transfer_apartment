# 換乘公寓 (love apartment)

# 重點
## 步驟還沒搞清楚

### 筆記
- 讓NPC一直跑直到可以使用到物件或沒有 暫時記憶
- 動作生成整合 直接生出互動物件
- 模型生成處理丟佇列
- 地圖物件只需要輸入有什麼物件 不用輸入數字
- 人物離開地圖應把地圖記憶清空

- 架構
    - 當兩人開始談話 第3個人不能動作 和聊天內容怎麼寫到兩個人的記憶系統裡面 模型寫成另一API
    - 還沒寫反應提示詞等內容
    - 需要測試所有函式是否正常
    - 流程是否為所想
    - 對話系統

(larry)
- 檢索意義函數 done:重要 關聯
- 動作轉座標

https://drive.google.com/drive/folders/1SD53_r1VxMABdSjVPnNsgGkesOH4Se0r?usp=sharing


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