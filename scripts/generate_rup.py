# ======================================================
# REKAP RUP FINAL 2026 - VERSI LOKAL (UNTUK WEBSITE)
# ======================================================

import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ======================================================
# FUNGSI LOAD JSON (ANTI BOM + AMAN)
# ======================================================
def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('data', [])
            else:
                return []
    except Exception as e:
        print(f"Gagal load: {path}")
        return []

# ======================================================
# PATH (SESUAIKAN)
# ======================================================
base = "D:/rup-2026-inaproc/data/"

sumber_master_satker = base + "Legacy_rup_master-satker_2026.json"
sumber_penyedia      = base + "Legacy_rup_paket-penyedia-terumumkan_2026.json"
sumber_swakelola     = base + "Legacy_rup_paket-swakelola-terumumkan_2026.json"
sumber_program       = base + "Legacy_rup_program-master_2026.json"
sumber_struktur      = base + "Legacy_rup_struktur-anggaran-pd_2026.json"

# ======================================================
# LOAD DATA
# ======================================================
df_master   = pd.DataFrame(load_json(sumber_master_satker))
df_penyedia = pd.DataFrame(load_json(sumber_penyedia))
df_swakelola= pd.DataFrame(load_json(sumber_swakelola))
df_program  = pd.DataFrame(load_json(sumber_program))
df_struktur = pd.DataFrame(load_json(sumber_struktur))

print("Jumlah data:")
print("MASTER   :", len(df_master))
print("PENYEDIA :", len(df_penyedia))
print("SWAKELOLA:", len(df_swakelola))
print("PROGRAM  :", len(df_program))
print("STRUKTUR :", len(df_struktur))

# ======================================================
# MASTER SATKER
# ======================================================
df_master = df_master[df_master['tahun_aktif'].astype(str).str.contains('2026', na=False)]

master_satker = df_master[['kd_satker','nama_satker']].drop_duplicates()
master_satker.rename(columns={'nama_satker':'Satuan Kerja'}, inplace=True)

# ======================================================
# RUP PENYEDIA
# ======================================================
rup_penyedia = (
    df_penyedia
    .groupby('kd_satker', as_index=False)['pagu']
    .sum()
    .rename(columns={'pagu':'RUP Penyedia'})
)

# ======================================================
# RUP SWAKELOLA
# ======================================================
rup_swakelola = (
    df_swakelola
    .groupby('kd_satker', as_index=False)['pagu']
    .sum()
    .rename(columns={'pagu':'RUP Swakelola'})
)

# ======================================================
# PAGU PROGRAM (FIX DUPLIKAT + FILTER M)
# ======================================================
kolom_duplikat = ['kd_satker', 'nama_program', 'kd_program_str', 'kd_program']

kolom_ada = [c for c in kolom_duplikat if c in df_program.columns]

df_program = df_program.drop_duplicates(subset=kolom_ada)

df_program = df_program[
    ~df_program['nama_program']
    .astype(str)
    .str.strip()
    .str.contains(r'( M$|\(M\)$)', regex=True)
]

pagu_program = (
    df_program
    .groupby('kd_satker', as_index=False)['pagu_program']
    .sum()
    .rename(columns={'pagu_program':'Pagu Program'})
)

# ======================================================
# STRUKTUR ANGGARAN (HANYA AMBIL PAGU PENGADAAN)
# ======================================================
struktur = (
    df_struktur
    .groupby('kd_satker', as_index=False)['belanja_pengadaan']
    .sum()
    .rename(columns={'belanja_pengadaan':'Pagu Pengadaan'})
)

# ======================================================
# MERGE
# ======================================================
df = master_satker.merge(pagu_program, on='kd_satker', how='left')
df = df.merge(rup_penyedia, on='kd_satker', how='left')
df = df.merge(rup_swakelola, on='kd_satker', how='left')
df = df.merge(struktur, on='kd_satker', how='left')

# ======================================================
# ISI NILAI KOSONG
# ======================================================
df.fillna(0, inplace=True)

# ======================================================
# HITUNG NILAI FINAL
# ======================================================
df['Total RUP Terumumkan'] = df['RUP Penyedia'] + df['RUP Swakelola']
df['Selisih RUP Terumumkan'] = df['Total RUP Terumumkan'] - df['Pagu Program']

df['Persentase'] = (
    df['Total RUP Terumumkan'] / df['Pagu Program']
).replace([float('inf')], 0).fillna(0) * 100

# ======================================================
# SUSUN KOLOM (FINAL UNTUK WEBSITE)
# ======================================================
df_final = df[[
    'Satuan Kerja',
    'Pagu Program',
    'Pagu Pengadaan',
    'RUP Penyedia',
    'RUP Swakelola',
    'Total RUP Terumumkan',
    'Selisih RUP Terumumkan',
    'Persentase'
]]

# ======================================================
# SORT A-Z
# ======================================================
df_final['_sort'] = df_final['Satuan Kerja'].str.lower()
df_final = df_final.sort_values('_sort').drop(columns='_sort').reset_index(drop=True)

# ======================================================
# SIMPAN JSON
# ======================================================
output_json = base + "rekap.json"

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(df_final.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

# ======================================================
# SIMPAN LAST UPDATE
# ======================================================
with open(base + "last-update.txt", "w") as f:
    f.write(datetime.now().strftime("%d %B %Y %H:%M WIB"))

print("\nSELESAI: rekap.json berhasil dibuat!")