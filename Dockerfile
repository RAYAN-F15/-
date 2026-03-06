# استخدام نسخة بايثون خفيفة وسريعة
FROM python:3.12-slim

# تحديث النظام وتثبيت أداة FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات البوت
COPY . .

# أمر تشغيل البوت
CMD ["python", "bot.py"]
