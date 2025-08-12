#!/bin/bash
set -e

IMAGE_NAME="botreport"

echo "🚀 Билд образа $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

echo "✅ Образ $IMAGE_NAME успешно собран!"
