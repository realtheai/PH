FROM python:3.11-slim

WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY ./app ./app

# 포트 노출
EXPOSE 8000

# 실행 (Python에서 PORT 환경변수 읽음)
CMD ["python", "-m", "app.main"]
