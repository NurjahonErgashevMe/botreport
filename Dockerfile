FROM python:3.11-slim AS build

# Устанавливаем системные пакеты (ffmpeg, для pydub и SpeechRecognition) 
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект 
COPY . .

CMD ["python", "main.py"]
