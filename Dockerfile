FROM python:3.10-slim

# Gerekli sistem kütüphanelerini kuralım
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kütüphaneleri yükleyelim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyalayalım
COPY . .

# Flask uygulamasını dış dünyaya açalım (Gunicorn ile)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]