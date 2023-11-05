import time

import clawler
import unit_test
import write_menu_data
from write_log import write_all_log, slack_msg
from firestore import store_menu_firestore


def main():
    start_time = time.time()  # 시작 시간 저장

    all_corps_menu = clawler.menu_crawler()  # 크롤링하기

    print()

    unit_test.IsBlankedCorps(all_corps_menu)  # 메뉴가 빈 부대 있는지 유닛테스트 진행
    try:
        unit_test.IsMenuCorrect(all_corps_menu)  # 샘플 메뉴와 비교하여 정상적으로 크롤링 되었는지 유닛테스트 진행
    except Exception as ex:  # 에러 종류
        write_all_log('unit_test.IsMenuCorrect_유닛 테스트중 에러가 발생 했습니다, 오류 메시지: ' + str(ex))  # ex는 발생한 에러의 이름을 받아오는 변수

    all_corps_menu = write_menu_data.writeAllCorpsMenu_TXT(
        all_corps_menu)  # 전부대 전메뉴를 allCorpsMenu.txt에 저장, 기존 메뉴에 크롤링한 메뉴를 추가한 dic을 all_corps_menu에 다시 담음.
    write_menu_data.writeMenuAsDate_TXT(all_corps_menu)  # 전부대 전메뉴를 부대별, 날짜별로 분류하여 각각 디렉토리별로 저장.
    store_menu_firestore(corps_menu=all_corps_menu, start_date_interval=31 * 1)  # 1달 전부터의 식단 데이터를 firestore에 저장
    write_all_log("")
    working_time = time.time() - start_time
    write_all_log("WorkingTime: {} sec".format(working_time))  # 크롤링 시간 계산 후 출력
    write_all_log("끝.")

    return working_time


if __name__ == "__main__":
    try:
        slack_msg(f"짬봇 데이터 수집을 시작합니다.")  # 슬랙 메시지 전송
        working_time = main()
        slack_msg(f"짬봇 데이터 수집을 완료했습니다. (working_time: {round(working_time, 3)}sec)")  # 슬랙 메시지 전송

    except Exception as e:
        error = str(e)
        write_all_log("\n\n\t***에러가 발생하였습니다ㅠㅠ")
        write_all_log(error + "\n")

        slack_msg("`[jjambot-crawler] 에러 발생`")  # 슬랙 메시지 전송
        slack_msg(error + "\n")  # 슬랙 메시지 전송
