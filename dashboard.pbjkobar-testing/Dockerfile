# Menggunakan sistem operasi Linux Alpine dengan Python yang sangat ringan
FROM python:3.10-alpine

# Mengatur folder kerja di dalam Docker
WORKDIR /app

# Menginstal modul Python yang dibutuhkan
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menginstal Nginx, Task Scheduler (Cron), Zona Waktu, dan Pembuat Password
RUN apk add --no-cache nginx dcron tzdata apache2-utils

# Membuat Gembok Akses (Username: adminpbj | Password: RahasiaKobar123)
# SILAKAN UBAH PASSWORD DI BAWAH INI SESUAI KEINGINAN ANDA
RUN htpasswd -bc /etc/nginx/.htpasswd adminpbj RahasiaKobar123

# Menyalin seluruh file website dan kode Python Anda ke dalam Docker
COPY . .

# Mengatur konfigurasi Nginx
RUN cp docker/nginx.conf /etc/nginx/nginx.conf

# Memastikan folder output sudah ada dan bisa dibaca oleh Nginx
RUN mkdir -p /app/output && chown -R nginx:nginx /app/output

# Memasukkan Jadwal Otomatis (Task Scheduler Linux / Cron)
# Jadwal sudah diatur canggih sesuai hari dan akhir bulan
RUN echo '0 5,6,7,8,9,10,11,14,17,20 * * * cd /app && python scripts/rup/generate_rup.py' > /etc/crontabs/root && \
    echo '0 5,6,7,8,9,10,11,14,17,20 * * 1,4 cd /app && python scripts/pengadaan/generate_pengadaan.py' >> /etc/crontabs/root && \
    echo '0 5,6,7,8,9,10,11,14,17,20 1 * * cd /app && python scripts/pengadaan/generate_pengadaan.py' >> /etc/crontabs/root && \
    echo '0 5,6,7,8,9,10,11,14,17,20 28,29,30,31 * * cd /app && python -c "import datetime,calendar; d=datetime.date.today(); exit(0 if d.day==calendar.monthrange(d.year,d.month)[1] else 1)" && python scripts/pengadaan/generate_pengadaan.py' >> /etc/crontabs/root

# Membuka jalur komunikasi (Port 80)
EXPOSE 80

# Menyalakan Task Scheduler dan Website Server (Nginx) secara bersamaan
CMD crond -b && nginx -g 'daemon off;'