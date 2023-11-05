import requests
import os
from datetime import datetime
import json

from dotenv import load_dotenv
from pymongo import MongoClient

# 환경변수 로드
load_dotenv()


def convert_calories(calories_str):
    return float(calories_str.replace('kcal', '').strip()) if calories_str.endswith('kcal') else None


def create_meal_document(entry):
    entry_date = datetime.strptime(entry['dates'], '%Y-%m-%d')
    meal_document = {"date": entry_date, "meals": {}, "corps": "5322"}  # 부대명 추가
    for meal_type in ["brst", "lunc", "dinr", "adspcfd"]:
        meal_info = entry.get(meal_type)
        if meal_info:
            calories = convert_calories(entry.get(f"{meal_type}_cal", ""))
            meal_document["meals"][meal_type] = {"menu": meal_info, "calories": calories}
    meal_document["sum_calories"] = convert_calories(entry.get("sum_cal", ""))
    return meal_document


def preprocess_data(data):
    return [create_meal_document(entry) for entry in data["DS_TB_MNDT_DATEBYMLSVC_5322"]["row"]]


def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_to_mongoDB(processed_data):
    # 환경변수에서 데이터베이스와 컬렉션 이름을 가져옴
    db_name = os.getenv('MONGODB_DB_NAME')
    collection_name = os.getenv('MONGODB_COLLECTION_NAME')

    # MongoDB 클라이언트 생성
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))

    # 데이터베이스와 컬렉션 선택
    db = client[db_name]
    collection = db[collection_name]

    # MongoDB에 데이터 삽입
    # insert_many를 사용하여 모든 문서를 한 번에 삽입
    result = collection.insert_many(processed_data)

    # 성공적으로 삽입된 문서의 ID를 출력
    print(f"Inserted document IDs: {result.inserted_ids}")

    # 클라이언트 연결을 닫음
    client.close()


def main():
    try:
        url = os.getenv('API_URL')
        data = fetch_data(url)
        processed_data = preprocess_data(data)
        print(json.dumps(processed_data, indent=2, default=str, ensure_ascii=False))
        save_to_mongoDB(processed_data)

    except requests.exceptions.RequestException as err:
        print(f"Network error occurred: {err}")
    except ValueError as ve:
        print(f"Data processing error occurred: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
