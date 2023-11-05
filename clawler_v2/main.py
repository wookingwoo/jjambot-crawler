import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv


def preprocess_data(data):
    processed_data = []

    for entry in data["DS_TB_MNDT_DATEBYMLSVC_5322"]["row"]:
        # 'dates' 필드를 datetime 객체로 변환
        entry['dates'] = datetime.strptime(entry['dates'], '%Y-%m-%d')

        # 각 식사 유형에 대해 데이터 처리
        for meal_type in ["brst", "lunc", "dinr", "adspcfd"]:
            if entry.get(meal_type):  # 해당 식사 유형의 데이터가 있을 경우에만 처리
                meal_data = {
                    "date": entry['dates'],
                    "meal_type": meal_type,
                    "menu": entry[meal_type],
                    "calories": float(entry.get(f"{meal_type}_cal", "").replace('kcal', '').strip()) if entry.get(
                        f"{meal_type}_cal", "").endswith('kcal') else None,
                    "sum_cal": float(entry.get("sum_cal", "").replace('kcal', '').strip()) if entry.get("sum_cal",
                                                                                                        "").endswith(
                        'kcal') else None
                }
                processed_data.append(meal_data)

    return processed_data


load_dotenv()
url = os.getenv('API_URL')

try:
    response = requests.get(url)

    response.raise_for_status()  # 오류가 있을 경우 예외 발생

    data = response.json()
    data = preprocess_data(data)
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
except json.JSONDecodeError as json_err:
    print(f"JSON decoding error occurred: {json_err}")
