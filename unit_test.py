from write_log import *


def IsBlankedCorps(dic):
    ifAnyoneBlanked = False
    blankedCorps = []

    for key, value in dic.items():

        if value == {}:
            ifAnyoneBlanked = True

            blankedCorps.append(key)

    if ifAnyoneBlanked:
        write_all_log("")
        write_all_log("************ 오류 ************")
        write_all_log("아래의 값이 비었습니다.")
        for i in range(len(blankedCorps)):

            if blankedCorps[i] == "3296":
                write_all_log(blankedCorps[i])
                write_all_log(": (api 준비중인 부대)")
            else:
                write_all_log(blankedCorps[i])

        write_all_log("")
        write_all_log("갯수: ")
        write_all_log(str(len(blankedCorps)))
        write_all_log("******************************")
    else:
        write_all_log("UnitTest(메뉴가 빈 부대 확인): 없음. 성공!")


def IsMenuCorrect(dic):
    right = 0
    wrong = 0

    right_data = {'breakfast': ['떡만둣국 (1)(5)(6)(10)(16)', '쇠고기호박볶음 (5)(6)(9)(16)', '배추김치(3~4월)'],
                  'lunch': ['밥', '감자국 (5)', '돼지고기고추장볶음 (5)(6)(10)', '양배추쌈/쌈장 (5)(6)', '배추김치(3~4월)'],
                  'dinner': ['비빔밥 (5)(6)(16)', '팽이버섯된장국 (5)(6)', '삶은달걀 (1)', '배추김치(3~4월)'],
                  'specialFood': ['백색우유(200ml) (2)', '과일젤리']}

    f = open('./crawling_data/sort_menuData/{}/year_{}/month_{}/{}_menu.txt'.format("ATC", "2020", "03",
                                                                                    "2020_03"), 'r')
    file_data = eval(f.read())
    f.close()

    if (dic["ATC"]["20200322"] == right_data) and (file_data == right_data):
        right += 1
    else:
        wrong += 1
        write_all_log("육훈소 20200322 데이터 오류.")

    if dic["5322"]["20200416"] == {'breakfast': ['밥1', '생선묵국 (5)(6)(9)', '돼지고기김치볶음 (6)(10)', '맛김'],
                                   'lunch': ['잡곡밥', '북어채국 (1)(5)(9)(18)', '오징어볶음 (5)(6)(17)', '깐풍기 (1)(5)(6)(15)',
                                             '배추김치(3~4월)'],
                                   'dinner': ['잡곡밥', '닭고기육개장 (1)(5)(15)', '카레떡볶이 (10)', '야채튀김 (6)', '깍두기(임가공)'],
                                   'specialFood': ['우유(백색우유(200ML,연간)) (2)', '레몬에이드', '요구르트,떠먹는형 (2)']}:
        right += 1
    else:
        wrong += 1
        write_all_log("5322부대(1급양대) 20200416 데이터 오류.")

    if dic["3lsc"]["20180715"] == {
        'breakfast': ['밥1', '생선묵국 (5)(6)(9)', '소시지야채볶음 (10)', '맛김', '배추김치(7~9월)'],
        'lunch': ['돼지고기부추덮밥 (1)(5)(6)(10)', '콩나물김치국 (5)', '오이무침 (5)(6)', '총각김치'],
        'dinner': ['밥', '버섯된장찌개 (5)(6)(9)', '돼지고기가지볶음 (5)(6)(10)', '감자조림 (5)(6)', '배추김치(7~9월)']}:
        right += 1
    else:
        wrong += 1
        write_all_log("3lsc 부대 20180715 데이터 오류.")

    write_all_log("UnitTest(데이터 비교 테스트)")
    write_all_log("[성공 횟수: {}/{}]".format(right, right + wrong))
