FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app/src

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем всё остальное
COPY . /app

# Запуск
CMD ["python", "entrypoint.py"]
