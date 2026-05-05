import pandas as pd
import json
import re
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# ===============================
# PATH
# ===============================
BASE_PATH = r'D:\rup-2026-inaproc'
DATA_PATH = os.path.join(BASE_PATH, 'data')
LOG_PATH = os.path.join(BASE_PATH, 'tools', 'log_pengadaan.txt')
OUTPUT_JSON = os.path.join(DATA_PATH, 'rekap_pengadaan.json')

# ===============================
# LOGGING
# ===============================
def log(msg):
    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{waktu}] {msg}\n")
    print(msg)

log("START generate_pengadaan")

# ===============================
# LOAD JSON SAFE
# ===============================
def load_json_safe(filename, label):
    path = os.path.join(DATA_PATH, filename + '.json')
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        if isinstance(data, list):
            df = pd.json_normalize(data)
        elif isinstance(data, dict):
            for k in ['data','items','results']:
                if k in data and isinstance(data[k], list):
                    df = pd.json_normalize(data[k])
                    break
            else:
                df = pd.json_normalize(data)
        else:
            df = pd.DataFrame()

        log(f"LOAD {label} | rows: {len(df)}")
        return df

    except Exception as e:
        log(f"ERROR {label} | {str(e)}")
        return pd.DataFrame()

# ===============================
# LOAD SEMUA SUMBER
# ===============================
df1 = load_json_safe('Legacy_rup_paket-penyedia-terumumkan_2026','Sumber 1')
df1_2 = load_json_safe('Legacy_rup_paket-swakelola-terumumkan_2026','Sumber 1_2')
df2 = load_json_safe('Legacy_tender_non-tender-pengumuman_2026','Sumber 2')
df2_1 = load_json_safe('Legacy_tender_non-tender-selesai_2026','Sumber 2_1')
df2_2 = load_json_safe('Legacy_tender_non-tender-ekontrak-sppbj_2026','Sumber 2_2')
df2_3 = load_json_safe('Legacy_tender_non-tender-ekontrak-kontrak_2026','Sumber 2_3')
df2_4 = load_json_safe('Legacy_tender_non-tender-ekontrak-spmkspp_2026','Sumber 2_4')
df2_5 = load_json_safe('Legacy_tender_non-tender-ekontrak-bapbast_2026','Sumber 2_5')
df3 = load_json_safe('Legacy_tender_pencatatan-non-tender_2026','Sumber 3')
df4 = load_json_safe('Legacy_tender_pencatatan-swakelola_2026','Sumber 4')
df5 = load_json_safe('Legacy_tender_pengumuman_2026','Sumber 5')
df5_1 = load_json_safe('Legacy_tender_tender-selesai_2026','Sumber 5_1')
df5_1_1 = load_json_safe('Legacy_tender_tender-nilai_2026','Sumber 5_1_1')
df5_2 = load_json_safe('Legacy_tender_tender-ekontrak-sppbj_2026','Sumber 5_2')
df5_3 = load_json_safe('Legacy_tender_tender-ekontrak-kontrak_2026','Sumber 5_3')
df5_4 = load_json_safe('Legacy_tender_tender-ekontrak-spmkspp_2026','Sumber 5_4')
df5_5 = load_json_safe('Legacy_tender_tender-ekontrak-bapbast_2026','Sumber 5_5')
df6 = load_json_safe('Legacy_ekatalog_paket-e-purchasing_2026','Sumber 6')
df7 = load_json_safe('Legacy_ekatalog-archive_paket-e-purchasing_2026','Sumber 7')

# ===============================
# FILTER
# ===============================
if not df2.empty and 'status_nontender' in df2.columns:
    df2 = df2[df2['status_nontender'] != 'Gagal/Batal']

if not df5.empty and 'status_tender' in df5.columns:
    df5 = df5[df5['status_tender'] != 'Gagal/Batal']

# ===============================
# HELPER
# ===============================
def get_set(df, col):
    if df.empty or col not in df.columns:
        return set()
    return set(df[col].astype(str).str.split(';').explode().str.strip())

def split_kd_list(x):
    try:
        if pd.isna(x):
            return []
        return [int(i.strip()) for i in str(x).split(';') if i.strip().isdigit()]
    except:
        return []

def standardize_kd_rup(df, col):
    if df.empty or col not in df.columns:
        return df
    df[col+'_raw'] = df[col]
    df[col+'_list'] = df[col].apply(split_kd_list)
    df[col] = df[col].apply(lambda x: split_kd_list(x)[0] if len(split_kd_list(x))>0 else None)
    return df

def clean_illegal_chars(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: re.sub(r'[\x00-\x1F]', '', str(x)) if isinstance(x, str) else x)
    return df

# ===============================
# STANDARDIZE
# ===============================
df1 = standardize_kd_rup(df1,'kd_rup')
df1_2 = standardize_kd_rup(df1_2,'kd_rup')
df2 = standardize_kd_rup(df2,'kd_rup')
df3 = standardize_kd_rup(df3,'kd_rup')
df4 = standardize_kd_rup(df4,'kd_rup')
df5 = standardize_kd_rup(df5,'kd_rup')
df6 = standardize_kd_rup(df6,'rup_code')
df7 = standardize_kd_rup(df7,'kd_rup')

# ===============================
# PROSES MINIMAL (UNTUK JSON WEB)
# ===============================
data = []

def safe(val):
    return "" if pd.isna(val) else val

def process_df(df, metode, sumber):
    if df.empty:
        return
    for _, r in df.iterrows():
        data.append({
            'Kode RUP': safe(r.get('kd_rup_raw') or r.get('rup_code_raw')),
            'Satuan Kerja': safe(r.get('nama_satker')),
            'Nama Paket': safe(r.get('nama_paket') or r.get('rup_name')),
            'Metode Pengadaan': metode,
            'Jenis Pengadaan': safe(r.get('jenis_pengadaan')),
            'Sumber Dana': safe(r.get('sumber_dana') or r.get('funding_source')),
            'PDN': safe(r.get('status_pdn')),
            'UKM': safe(r.get('status_ukm')),
            'Nilai Pagu RUP': safe(r.get('pagu')),
            'Nilai Hasil Pemilihan': safe(r.get('total') or r.get('total_harga')),
            'Status': safe(r.get('status_nontender') or r.get('status_tender') or r.get('status')),
            'Kode Paket': safe(r.get('kd_nontender') or r.get('kd_tender') or r.get('order_id')),
            'Nilai HPS': safe(r.get('hps')),
            'Nilai PDN': safe(r.get('nilai_pdn_kontrak')),
            'Nilai UMK': safe(r.get('nilai_umk_kontrak')),
            'Versi': safe(r.get('versi_nontender')),
            'Metode': metode,
            'Sumber': sumber
        })

process_df(df2, 'Non Tender', 'Sumber 2')
process_df(df3, 'Pencatatan Non Tender', 'Sumber 3')
process_df(df4, 'Swakelola', 'Sumber 4')
process_df(df5, 'Tender', 'Sumber 5')
process_df(df6, 'E-Purchasing', 'Sumber 6')
process_df(df7, 'E-Purchasing', 'Sumber 7')

# ===============================
# FINAL
# ===============================
final_df = pd.DataFrame(data)
final_df = clean_illegal_chars(final_df)

# ===============================
# EXPORT JSON
# ===============================
try:
    final_df.to_json(OUTPUT_JSON, orient='records', force_ascii=False, indent=2)
    log(f"EXPORT JSON berhasil: {OUTPUT_JSON}")
    log(f"TOTAL DATA: {len(final_df)}")
except Exception as e:
    log(f"ERROR EXPORT JSON | {str(e)}")

log("SELESAI generate_pengadaan")