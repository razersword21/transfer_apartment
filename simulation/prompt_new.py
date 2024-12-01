person_system = """<人物資訊>{person_information}</人物資訊>你是一位人物角色，人物背景資料參考"人物資訊"，根據該人物的"人物資訊"決定所有想法、行為和講話方式。"""

daily_routine = """<人物記憶>{memory}</人物記憶>
<今日時間>{current_time}</今日時間>"""
daily_routine_prompt = """根據"人物記憶"中的重要事情，生成你今天的例行行程，符合以下"安排行程規則"
<安排行程規則>
- 行程中一定包含起床、吃飯(早、中、晚)、上班或上學、放學或下班、上床睡覺5項必定行程，若沒有包含任一項必定行程則更正
- 以每30分為一個單位
- 行程的時間可與範例中的時間不同
- 行程間的順序要合理，生成時檢查結果行程間的順序是否合理，若不合理則更正
- 行程描述應用詞一致
- 盡可能生成適合該人物的行程，且時間點與對應行程內容合理，若不合理則更正
- 使用繁體中文
</安排行程規則>
以json回傳，回傳範例格式如下:
{
    "today_schedule": {
        "07:00":"起床，刷牙洗臉",
        "07:30":"吃早餐",
        "08:00":"去該人物職業地點上班或上學",
        "23:00":"上床睡覺"
    }
}
最少生成6條行程，行程越多越好，不需要包含其他內容"""

design_action = """<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>
<地點物件資訊>{map}<地點物件資訊>"""
design_action_prompt = """根據提供的所有資訊，為當前時間點決定你接下來要做的動作，遵循以下"動作決定規則"
<動作決定規則>
- 動作描述不要包含自己名字、人物想法、後續行程內容和原因
- 動作描述應包含"地點物件資訊"中的地點，若有互動物件則包含互動物件名稱
- 與他人互動的描述要包含其他人物名字
- 動作應在合適的地點做合理的事情
- 使用繁體中文
<動作決定規則>
"地點物件資訊"表示地圖中所有地點和各地點的物件，數字為0表示物件都被使用中。當物件數字為0則應該決定等待或更改動作
以json回傳，回傳範例格式如下:
{
    "action": "該動作描述"
}
不需要包含其他內容"""

transfor_action = """<動作描述>{action_content}</動作描述>
<地點列表>{location_list}<地點列表>
<地點物件資訊>{map_object}<地點物件資訊>"""
transfor_action_prompt = """根據輸入的"動作描述"，分析動作內容中的地點為"地點列表"中的哪一個地點並判斷是否有與他人或"地圖資訊"中的物件互動，回傳分析結果，遵循以下"動作轉換規則"
<動作轉換規則>
- 有與他人互動則回傳人物名字，若無與他人互動，"person"回傳"None"
- 有使用物件則"object"回傳"地點物件資訊"中的物件名稱，若無與物件互動，"object"回傳"None"，例如坐下需要與椅子互動，"object"回傳"椅子"
- "location"只能從"地點列表"中選一個
- 使用繁體中文
<動作轉換規則>
"地點物件資訊"表示地圖中所有地點和各地點的物件，數字表示未使用的物件數量
以json回傳，回傳範例格式如下:
{
    "action": "該動作簡要描述",
    "location": "執行動作地點名稱",
    "person":"互動對象名稱",
    "object": "互動物件名稱"
}
不需要包含其他內容"""

change_action_prefix = """<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>
<地點物件資訊>{map}<地點物件資訊>"""

change_action_profix = """根據你現在的位置和時間點，你現在想換動作或跟某人說話？
- 聊天則 "action"回傳<聊天>而"person"回傳聊天對象
- 換動作 "action"回傳換的動作描述而"person"回傳None
遵循以下"動作決定規則"
<動作決定規則>
- 動作描述不要包含自己名字、人物想法、後續行程內容和原因
- 動作描述應包含"地點物件資訊"中的地點，若有互動物件則包含互動物件名稱
- 與他人互動的描述要包含其他人物名字
- 動作應在合適的地點做合理的事情
- 使用繁體中文
<動作決定規則>
以json回傳，回傳範例格式如下:
{
    "action": "該動作描述",
    "person":"互動對象名稱"
}
不需要包含其他內容"""

create_thought = """<人物記憶>{memory}</人物記憶>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>"""
create_thought_prompt = """根據提供的所有資訊，為當前時間點生成你目前的想法，用一段話表示，遵循以下"想法規則"
<想法規則>
- 不要包含自己名字，可包含其他人名字
- 使用繁體中文
<想法規則>
以json回傳，回傳範例格式如下:
{
    "thought": "想法內容",
}
不需要包含其他內容"""

check_adjust = """<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<當前時間>{current_time}</當前時間>"""
check_adjust_prompt = """根據提供的所有資訊，判斷是否會影響到"人物行程"，若會影響則回傳True，若不會則回傳False
<範例情況>
原本行程中下午1點到下午5點為上班時間
{
    "07:00": "起床，刷牙、吃早餐",
    "08:30": "去Willow Market藥房上班",
    "12:00": "午餐",
    "13:00": "繼續工作",
    "17:00": "下班回家",
    "18:00": "晚餐",
    "20:00": "開始跑步"
}
但在"人物記憶"或"觀察事項"中提到答應同事下午請假釣魚，則須調整原本的"人物行程"，去掉其中下午上班和下班行程，改為釣魚
{
    "07:00": "起床，刷牙、吃早餐",
    "08:30": "去Willow Market藥房上班",
    "12:00": "午餐",
    "14:00": "請假與同事釣魚",
    "16:30": "收拾釣魚器具準備回家",
    "18:00": "晚餐",
    "20:00": "開始跑步"
}
上述情況回傳true
</範例情況>
以json回傳，回傳範例格式如下:
{
    "need_adjust": bool
}
不需要包含其他內容"""

adjust_routine = """<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<當前時間>{current_time}</當前時間>"""
adjust_routine_prompt = """根據提供的所有資訊，對於"人物行程"進行調整，重新安排行程
以json回傳調整後的行程，回傳範例格式如下:
{
    "adjust_schedule": {
        "07:00":"起床，刷牙洗臉",
        "07:30":"與家人一起吃早餐",
        "08:00":"去<職業地點>上班",
        "23:00":"上床睡覺"
    }
}
不需要包含其他內容，使用繁體中文"""

create_dialogue = """<人物記憶>{memory}</人物記憶>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>
<對話歷史>{dialogue_history}</對話歷史>"""
create_dialogue_prompt = """根據你的人物背景和提供的所有資訊，特別是參考"對話歷史"，生成你想說的話，遵循以下"對話規則"
<對話規則>
- 若要結束聊天則結果回傳"<結束對話>"
- 使用繁體中文
</對話規則>
以json回傳，回傳範例格式如下:
{
    "dialogue": ""
}"""

organize = """<人物記憶>{memory}</人物記憶>
<觀察事項>{observes}</觀察事項>
<對話歷史>{dialogue_history}</對話歷史>"""
organize_prompt = """根據你的人物背景和提供的所有資訊，將其中你認為重要的事情整理成條列式的內容作為記憶，遵循以下<整理記憶規則>
<整理記憶規則>
- 按照對你的重要程度排序，最重要的記憶排第一
- 使用繁體中文
</整理記憶規則>
以json回傳，回傳範例格式如下:
{
    "memory": [
        {"1": "重要事情描述"},
        ...
    ]
}
"""

reflection = """<人物資訊>{person_info}</人物資訊>
<人物記憶>{memory}</人物記憶>
"""
reflection_prompt = """根據今天發生的"人物記憶"以及你的人物資訊，反思你的人物背景資訊使否有需要調整或補充的地方，針對其中職業、興趣、人物特質、角色描述和人際關係進行判別，遵循以下"反思改動規則"
<反思改動規則>
- 若判斷無須改動或補充，則回傳原本描述內容
- 改動幅度不能太大
- 若有需要補充內容，可改寫成通順的描述
- 若有新認識的人，在人際關係列表中添加，其格式為{"name":"人名","relationship":"你認為與該人物的關係"}，僅從人物記憶中的人名挑選，不要包含自己
- 使用繁體中文
</反思改動規則>
以json回傳，回傳範例格式如下:
{
    "job_occupation": "",
    "interests": "",
    "personality": "",
    "character_description": "",
    "interpersonal_relationships": []
}"""