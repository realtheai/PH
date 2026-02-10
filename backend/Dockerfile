FROM python:3.11-slim

WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY ./app ./app

# Entrypoint 스크립트 복사 및 실행 권한 부여
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 포트 노출
EXPOSE 8000

# Entrypoint 실행
ENTRYPOINT ["./entrypoint.sh"]
