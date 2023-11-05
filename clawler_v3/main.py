import requests
import os
from datetime import datetime, timezone, timedelta
import json
import re
import traceback

from dotenv import load_dotenv
from pymongo import MongoClient

# 환경변수 로드
load_dotenv()


def convert_calories(calories_str):
    return float(calories_str.replace('kcal', '').strip()) if calories_str.endswith('kcal') else None


def extract_menu_and_allergies(meal_info):
    # 끝에 있는 괄호로 둘러싸인 숫자들을 찾기 위한 정규표현식 패턴
    pattern = r'(.*?)(\(\d{2}\))+$'

    # 정규표현식으로 문자열을 검색
    match = re.search(pattern, meal_info)

    if match:
        # 첫 번째 그룹은 끝에 있는 괄호로 둘러싸인 숫자들을 제외한 모든 문자
        menu = match.group(1).rstrip()
        # 두 번째 그룹은 끝에 있는 괄호로 둘러싸인 숫자들의 연속된 부분
        # 괄호로 둘러싸인 숫자들만 찾아 리스트로 변환
        allergy_numbers = re.findall(r'\((\d{2})\)', match.group())

        # 알러지 정보를 정수 리스트로 변환
        allergy_numbers_int_list = []
        for allergy_number in allergy_numbers:
            try:
                allergy_numbers_int_list.append(int(allergy_number))
            except ValueError:
                print(f"Failed to convert allergy numbers to integers: {allergy_numbers}")

        return menu, allergy_numbers_int_list
    else:
        # 알러지 정보가 없는 경우, 전체 문자열이 메뉴 이름
        return meal_info, []


def parse_date(date_string, format1='%Y-%m-%d', format2='%Y%m%d'):
    try:
        date_string = date_string.split("(")[0].strip()  # 요일 정보 제거 ex: 2023-11-05(일)
        entry_date = datetime.strptime(date_string, format1)  # format1으로 파싱을 시도
    except ValueError:
        try:
            # 실패하면 format2로 파싱을 시도
            entry_date = datetime.strptime(date_string, format2)
        except ValueError:
            # 두 형식 모두 실패할 경우 None 반환
            print(f"Unexpected date format: {date_string}")
            return None

    # ISO 한국 시간으로 설정
    entry_date = entry_date.replace(tzinfo=timezone(timedelta(hours=9)))

    return entry_date


def create_meal_document(corps_code, entry):
    entry_date = parse_date(entry['dates'])

    meal_document = {"date": entry_date, "meals": {}, "corps": corps_code}  # 부대명 추가
    for meal_type in ["brst", "lunc", "dinr", "adspcfd"]:
        meal_info = entry.get(meal_type)
        if meal_info:
            calories = convert_calories(entry.get(f"{meal_type}_cal", ""))
            menu, allergy_numbers = extract_menu_and_allergies(meal_info)
            meal_document["meals"][meal_type] = {"menu": menu, "calories": calories, "allergy_numbers": allergy_numbers}
    meal_document["sum_calories"] = convert_calories(entry.get("sum_cal", ""))
    return meal_document


def preprocess_data(corps_code, corps_service, data):
    return [create_meal_document(corps_code, entry) for entry in data[corps_service]["row"]]


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
        HOST = os.getenv('HOST', 'https://openapi.mnd.go.kr')
        API_KEY = os.getenv('API_KEY')
        TYPE = os.getenv('TYPE', 'json')
        START_INDEX = os.getenv('START_INDEX')
        END_INDEX = os.getenv('END_INDEX')

        service_dict = {}
        corps = ["3lsc", "ATC", "1691", "2171", "3296", "3389", "5322", "6176", "6282", "6335", "7369", "8623", "8902",
                 "9030"]

        for i in corps:
            if i == "3lsc":
                service_dict["3lsc"] = 'DS_TB_MNDT_DATEBYMLSVC'
            else:
                service_dict[i] = "DS_TB_MNDT_DATEBYMLSVC_" + i

        print("service: ", service_dict)

        for corps_code, corps_service in service_dict.items():
            print("corps_code: ", corps_code)
            print("corps_service: ", corps_service)
            url = f"{HOST}/{API_KEY}/{TYPE}/{corps_service}/{START_INDEX}/{END_INDEX}"

            data = fetch_data(url)
            processed_data = preprocess_data(corps_code, corps_service, data)
            print(json.dumps(processed_data, indent=2, default=str, ensure_ascii=False))
            save_to_mongoDB(processed_data)

    except requests.exceptions.RequestException as err:
        print(f"Network error occurred: {err}")
    except ValueError as ve:
        print(f"Data processing error occurred: {ve}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
