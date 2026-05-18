# 1. Gunakan base image Python resmi berbasis Linux Alpine yang sangat ringan
FROM python:3.11-alpine

# 2. Instal Nginx (Web Server) dan Cron (Otomatisasi Jadwal Linux)
RUN apk add --no-cache nginx dcron tzdata

# 3. Atur zona waktu ke Asia/Jakarta (WIB) agar jadwal penarikan data sinkron
ENV TZ=Asia/Jakarta

# 4. Tentukan folder kerja di dalam Linux Kontainer
WORKDIR /app

# 5. Salin file requirements atau langsung instal library Python yang dibutuhkan
RUN pip install --no-cache-requests pandas openpyxl

# 6. Salin seluruh file proyek lokal ke dalam kontainer Docker
COPY . .

# 7. Konfigurasi agar Nginx menyajikan file HTML di folder /app
RUN mkdir -p /run/nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 8. Daftarkan skrip cron untuk otomatisasi penarikan data (Setiap hari jam 06:00 WIB)
RUN echo "0 6 * * * cd /app && python scripts/rup/generate_rup.py && python scripts/pengadaan/generate_pengadaan.py" > /etc/crontabs/root

# 9. Jalankan Nginx web server dan sistem Cron secara bersamaan saat kontainer aktif
EXPOSE 80
CMD ["sh", "-c", "crond && nginx -g 'daemon off;'"]