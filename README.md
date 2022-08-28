# jjambot-crawler (짬봇 크롤러)

짬봇은 군대 식단, 전역일 계산, 각종 군생활 정보등을 카카오톡 챗봇으로 알려주는 서비스입니다.

### 서비스 안내

[짬봇 홈페이지](https://jjambot.wookingwoo.com): https://jjambot.wookingwoo.com

[짬봇 카카오톡 채널 링크](http://pf.kakao.com/_xlVKrxb): http://pf.kakao.com/_xlVKrxb

[카카오톡 검색용 아이디](http://pf.kakao.com/_xlVKrxb): jjambot

### github

[jjambot-chatbot](https://github.com/wookingwoo/jjambot): https://github.com/wookingwoo/jjambot

[jjambot-crawler](https://github.com/wookingwoo/jjambot-crawler): https://github.com/wookingwoo/jjambot-crawler


---

## Linux Setting

### TimeZone

한국 표준시로 변경하는 2가지 방법입니다.

- Timezone 변경하기 1

현재 시간을 확인하는 명령어로 우분투 시스템에서 사용하는 표준 시간을 보여줍니다.

```bash
$ date
```

다음 명령어를 입력 후 원하는 시간대 국가를 선택하세요.

```bash
$ tzselect
```

아래와 같이 오류가 난다면 직접 추가해야합니다. (Timezone 변경하기 2 참고.)

```
You can make this change permanent for yourself by appending the line
        TZ='Asia/Seoul'; export TZ
to the file '.profile' in your home directory; then log out and log in again.

Here is that TZ value again, this time on standard output so that you
can use the /usr/bin/tzselect command in shell scripts:
```

- Timezone 변경하기 2

아래는 Timezone을 직접 변경하는 법입니다.

아래 나온 설정 지역 예시는 Asia/Seoul입니다.

```bash
$ sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
```

---

## Data

### 형식

- allCorpsMenu.txt

크롤링된 데이터는 아래와같은 JSON형식의 txt로 저장됩니다.

```
{
'부대': {'날짜': {'breakfast': ['메뉴1', '메뉴2'], 'lunch': ['메뉴1', '메뉴2'], 'dinner':['메뉴1', '메뉴2'], 'specialFood': ['메뉴1', '메뉴2']},    ...   }

...

}

```

---

## 크롤러 실행

### nohup

- nohup

nohup을 이용하면 터미널을 종료시킨 후에도 프로세스를 계속해서 진행시킬 수 있습니다.

```bash
$ nohup python3 run_server.py &
```

nohup으로 작업할 파일은 755 이상의 권한이 필요합니다.

```bash
$ chmod 755 shell.sh
```

- ps와 kill

해당 프로세스를 종료하고자 할 때에는 ps 명령어와 kill 명령어로 종료할 수 있습니다.

먼저 ps 명령어를 이용해 pid를 확인합니다.

```bash
$ ps -ef | grep [스트립트 / 또는 명령어]
```

해당 프로세스 아이디(PID)를 아래와 같이 kill 하면 프로세스가 종료됩니다.

```bash
$ kill -9 [PID]
```

