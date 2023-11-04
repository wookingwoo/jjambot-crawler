import requests
import os
import json
from datetime import datetime

from dotenv import load_dotenv


# 데이터 전처리
def preprocess_for_mongodb(data):
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


load_dotenv()
url = os.getenv('API_URL')

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    mongodb_ready_data = preprocess_for_mongodb(data)
    print(json.dumps(mongodb_ready_data, indent=2, default=str, ensure_ascii=False))
else:
    print("Error: ", response.status_code)
