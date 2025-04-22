FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё
COPY . .

ENV PYTHONPATH=/app

# Миграция и запуск
CMD ["sh", "-c", "alembic upgrade head && python src/entrypoint.py"]
