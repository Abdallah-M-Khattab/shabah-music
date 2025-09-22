FROM python:3.10-slim

WORKDIR /app

# نسخ المتطلبات
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات البوت
COPY . .

# أمر تشغيل البوت
CMD ["python", "main.py"]
