import json
import pandas as pd
import os
from datetime import datetime

# =========================
# LOAD DATA JSON (DATA MURNI / BELUM FILTER)
# =========================
with open("data/rekap.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# =========================
# HITUNG KOLOM TAMBAHAN
# =========================
df["Selisih RUP Terumumkan"] = df["Total RUP Terumumkan"] - df["Pagu Pengadaan"]
df["Persentase"] = df["Total RUP Terumumkan"] / df["Pagu Pengadaan"].replace(0, 1) * 100

# ======================================================
# SIMPAN & DOWNLOAD EXCEL KE FOLDER OUTPUT
# ======================================================
tanggal = datetime.now().strftime('%Y-%m-%d')
tahun = '2026'

nama_file = f"Rekap RUP Tahun {tahun} ({tanggal}) Legacy.xlsx"

output_path = os.path.join("output", nama_file)

# =========================
# PAKAI DATA MURNI (TANPA FILTER 0-0-0)
# =========================
df.to_excel(output_path, index=False)

print("Excel berhasil dibuat:", output_path)