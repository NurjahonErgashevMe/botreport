#!/bin/bash
set -e

IMAGE_NAME="botreport"
CONTAINER_NAME="botreport-container"

# Если контейнер уже запущен — останавливаем и удаляем
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Останавливаю старый контейнер..."
    docker stop $CONTAINER_NAME || true
    echo "🗑 Удаляю старый контейнер..."
    docker rm $CONTAINER_NAME || true
fi

echo "▶ Запуск контейнера $CONTAINER_NAME..."
docker run -d --name $CONTAINER_NAME $IMAGE_NAME

echo "✅ Контейнер $CONTAINER_NAME запущен!"
