import json
import re


def check_json_format(data: str, flag: bool):
    try:
        result = json.loads(data)
        flag = True
    except json.JSONDecodeError:
        try:
            json_string = re.search(r"```json(.*)```", data, re.DOTALL).group(1).strip()
            result = json.loads(json_string)
            flag = True
        except (json.JSONDecodeError, AttributeError):
            result = None
    return result, flag