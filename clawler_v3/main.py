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


def preprocess_data(corps_code, corps_service, data):
    processed_data = []

    for entry in data[corps_service]["row"]:

        entry_date = parse_date(entry['dates'])  # 날짜 객체로 변환

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

                menu, allergies = extract_menu_and_allergies(meal_info)
                meal_document["meals"][meal_type] = {
                    "menu": menu,
                    "calories": float(calories.replace('kcal', '').strip()) if calories.endswith('kcal') else None,
                    "allergies": allergies,
                }

        # 전체 칼로리
        sum_calories = entry.get("sum_cal", "")
        if sum_calories.endswith('kcal'):
            meal_document["sum_calories"] = float(sum_calories.replace('kcal', '').strip())

        processed_data.append(meal_document)

    return processed_data


def preprocess_by_mealtype(corps_code, corps_service, data):
    # 날짜를 키로 하여 식사 데이터를 정리할 딕셔너리
    processed_data = {}

    for entry in data:
        # 날짜를 파싱
        date_key = entry['date']

        if date_key not in processed_data:
            processed_data[date_key] = entry
            processed_data[date_key]['meals'] = {}

        # 각 식사 유형에 대한 데이터 처리
        for meal_type, meal_info in entry['meals'].items():
            if processed_data[date_key]['meals'].get(meal_type) is None:
                processed_data[date_key]['meals'][meal_type] = []
            processed_data[date_key]['meals'][meal_type].append(meal_info)

    # 딕셔너리를 리스트로 변환하여 반환합니다.
    return list(processed_data.values())


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


def slack_msg(msg):
    SLACK_TOKEN = os.getenv('SLACK_TOKEN')
    SLACK_CHANNEL = "#" + os.getenv('SLACK_CHANNEL', 'wookingwoo-bot-playground')

    # now = datetime.now()
    # text_msg =  f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"

    text_msg = msg

    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + SLACK_TOKEN},
                             data={"channel": SLACK_CHANNEL, "text": text_msg})

    if response.status_code == 200:
        print("✉ [slack msg]: " + text_msg)
    else:
        print("❌ Failed to send slack message")
        print("✉ [slack msg]: " + text_msg)
        print(response.json())


def main():
    try:
        slack_msg("🍚 짬봇 - 식단 수집을 시작합니다 🍚")

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
            processed_data = preprocess_by_mealtype(corps_code, corps_service, processed_data)
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
