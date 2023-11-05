import requests
import os
from datetime import datetime
import json

from dotenv import load_dotenv

# from pymongo import MongoClient

# 환경변수 로드
load_dotenv()


# MongoDB 클라이언트 설정
# mongo_url = os.getenv('MONGO_URL')
# db_name = os.getenv('DB_NAME')
# collection_name = os.getenv('COLLECTION_NAME')
# client = MongoClient(mongo_url)
# db = client[db_name]
# collection = db[collection_name]

def preprocess_data(data):
    processed_data = []

    for entry in data["DS_TB_MNDT_DATEBYMLSVC_5322"]["row"]:
        # 날짜 객체로 변환
        entry_date = datetime.strptime(entry['dates'], '%Y-%m-%d')

        # 식사 데이터 문서 구조화
        meal_document = {
            "date": entry_date,
            "meals": {}
        }

        # 각 식사 유형에 대한 데이터 처리
        for meal_type in ["brst", "lunc", "dinr", "adspcfd"]:
            meal_info = entry.get(meal_type)
            if meal_info:  # 해당 식사 유형의 데이터가 있을 경우에만 처리
                calories = entry.get(f"{meal_type}_cal", "")
                meal_document["meals"][meal_type] = {
                    "menu": meal_info,
                    "calories": float(calories.replace('kcal', '').strip()) if calories.endswith('kcal') else None
                }

        # 전체 칼로리
        sum_calories = entry.get("sum_cal", "")
        if sum_calories.endswith('kcal'):
            meal_document["sum_calories"] = float(sum_calories.replace('kcal', '').strip())

        processed_data.append(meal_document)

    return processed_data


def preprocess_by_mealtype(data):
    # 날짜를 키로 하여 식사 데이터를 정리할 딕셔너리
    processed_data = {}

    for entry in data:
        # 날짜를 파싱
        date_key = entry['date']

        # 해당 날짜에 대한 데이터가 이미 존재하는 경우, 항목을 업데이트
        if date_key not in processed_data:
            processed_data[date_key] = entry
            processed_data[date_key]['meals'] = {}

        # 모든 식사에 대해 반복하며 총 칼로리를 계산
        for meal_type, meal_info in entry['meals'].items():
            processed_data[date_key]['meals'].setdefault(meal_type, [])
            processed_data[date_key]['meals'][meal_type].append(meal_info)

    # 딕셔너리를 리스트로 변환하여 반환합니다.
    return list(processed_data.values())


url = os.getenv('API_URL')

try:
    response = requests.get(url)
    response.raise_for_status()  # 오류가 있을 경우 예외 발생
    data = response.json()
    processed_data = preprocess_data(data)
    processed_data = preprocess_by_mealtype(processed_data)

    print(json.dumps(processed_data, indent=2, default=str, ensure_ascii=False))

    # 데이터베이스에 저장
    # collection.insert_many(processed_data)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
except Exception as e:
    print(f"An error occurred: {e}")
