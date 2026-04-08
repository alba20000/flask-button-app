FROM python:3.14-slim

# Рабочая директория
WORKDIR /app

# Ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Порт
EXPOSE 5000

# Запуск через gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]