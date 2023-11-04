import requests
import os
import json
from datetime import datetime

from dotenv import load_dotenv


# 데이터 전처리
def data_type_preprocess(data):
    processed_data = []

    for entry in data["DS_TB_MNDT_DATEBYMLSVC_5322"]["row"]:
        # 각 항목에서 칼로리 값이 'kcal'로 끝나면 숫자로 변환
        for key, value in entry.items():
            if isinstance(value, str) and value.endswith('kcal'):
                # 'kcal'을 제거하고 실수로 변환
                entry[key] = float(value.replace('kcal', '').strip() or None)

        # 'dates' 필드를 datetime 객체로 변환
        entry['dates'] = datetime.strptime(entry['dates'], '%Y-%m-%d')

        processed_data.append(entry)

    return processed_data


def menu_type_preprocess(data):
    result = []
    for item in data:
        # 날짜 추출
        date = item["dates"]

        # 아침 식사 데이터 추가
        if item["brst"]:
            result.append({
                "date": date,
                "type": "breakfast",
                "menu": item["brst"],
                "calories": item.get("brst_cal", ""),
                "sum_cal": item.get("sum_cal", "")
            })

        # 점심 식사 데이터 추가
        if item["lunc"]:
            result.append({
                "date": date,
                "type": "lunch",
                "menu": item["lunc"],
                "calories": item.get("lunc_cal", ""),
                "sum_cal": item.get("sum_cal", "")
            })

        # 저녁 식사 데이터 추가
        if item["dinr"]:
            result.append({
                "date": date,
                "type": "dinner",
                "menu": item["dinr"],
                "calories": item.get("dinr_cal", ""),
                "sum_cal": item.get("sum_cal", "")
            })

        # 부식 데이터 추가 (해당하는 경우)
        if item["adspcfd"]:
            result.append({
                "date": date,
                "type": "special",
                "menu": item["adspcfd"],
                "calories": item.get("adspcfd_cal", ""),
                "sum_cal": item.get("sum_cal", "")
            })

    return result


load_dotenv()
url = os.getenv('API_URL')

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    data = data_type_preprocess(data)
    data = menu_type_preprocess(data)
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
else:
    print("Error: ", response.status_code)
