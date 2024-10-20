person_system = "<人物資訊>{person_information}</人物資訊>你是一位人物角色，人物背景資料參考<人物資訊>，所有行為決定和講話方式都以該人物的視角思考與動作。"

daily_routine = """生成你今天的例行行程，行程一定包含起床、吃飯(早、中、晚)、上班或上學、放學或下班、睡覺，行程的順序要合理，以json回傳，回傳範例格式如下
{
    {"time":"07:00", "action":"起床，刷牙、吃早餐"},
    {"time":"08:00", "action":"準備去健身房上班"},
}
最少生成6條行程，最多10條"""

design_action = """<人物動作歷史>{action_history}</人物動作歷史>
<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>
為當前時間點決定你現在要做的動作，可決定使否留在原地或移動到其他地方，不要包含移動到某地這類動作，以json回傳，回傳範例格式如下
{
    "location": "執行該動作時的地點",
    "action": "該動作描述"
}"""

create_dialogue = """<人物動作歷史>{action_history}</人物動作歷史>
<人物記憶>{memory}</人物記憶>
<人物行程>{schedule}</人物行程>
<觀察事項>{observes}</觀察事項>
<目前地點>{current_location}</目前地點>
<當前時間>{current_time}</當前時間>
<對話歷史>{dialogue_history}</對話歷史>
根據<對話歷史>和所有其他資訊，產生你想說的話，以json回傳，回傳範例格式如下
{
    "dialogue": ""
}"""