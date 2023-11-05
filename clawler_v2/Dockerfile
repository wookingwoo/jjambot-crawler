FROM python:3.9

LABEL maintainer="contact@wookingwoo.com"

RUN apt-get -y update

RUN mkdir /jjambot-crawler

# 컨테이너 내 프로젝트 root directory 설정
WORKDIR /jjambot-crawler

# Install jjambot-crawler dependencies using file requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip # pip 업그레이드
RUN pip install -r requirements.txt # 패키지 설치

# Copy namsigdnag-crawler codes
COPY .. /jjambot-crawler

# 실행
CMD ["python", "main.py"]

# docker build --tag jjambot-crawler:1.0 .
# docker run -it -d -v /host/path/data:/jjambot-crawler/data/:/jjambot-crawler/data/ -e TZ=Asia/Seoul --name jjambot-crawler jjambot-crawler:1.0
