# ======================================================
# PAKET PENGADAAN 2026 - VERSI LOKAL
# ======================================================

import pandas as pd
import json
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ======================================================
# PATH SUMBER DATA
# ======================================================
sumber1     = r'D:\rup-2026-inaproc\data\Legacy_rup_paket-penyedia-terumumkan_2026.json'
sumber1_2   = r'D:\rup-2026-inaproc\data\Legacy_rup_paket-swakelola-terumumkan_2026.json'
sumber2     = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-pengumuman_2026.json'
sumber2_1   = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-selesai_2026.json'
sumber2_2   = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-ekontrak-sppbj_2026.json'
sumber2_3   = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-ekontrak-kontrak_2026.json'
sumber2_4   = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-ekontrak-spmkspp_2026.json'
sumber2_5   = r'D:\rup-2026-inaproc\data\Legacy_tender_non-tender-ekontrak-bapbast_2026.json'
sumber3     = r'D:\rup-2026-inaproc\data\Legacy_tender_pencatatan-non-tender_2026.json'
sumber4     = r'D:\rup-2026-inaproc\data\Legacy_tender_pencatatan-swakelola_2026.json'
sumber5     = r'D:\rup-2026-inaproc\data\Legacy_tender_pengumuman_2026.json'
sumber5_1   = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-selesai_2026.json'
sumber5_1_1 = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-selesai-nilai_2026.json'
sumber5_2   = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-ekontrak-sppbj_2026.json'
sumber5_3   = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-ekontrak-kontrak_2026.json'
sumber5_4   = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-ekontrak-spmkspp_2026.json'
sumber5_5   = r'D:\rup-2026-inaproc\data\Legacy_tender_tender-ekontrak-bapbast_2026.json'
sumber6     = r'D:\rup-2026-inaproc\data\Legacy_ekatalog_paket-e-purchasing_2026.json'
sumber7     = r'D:\rup-2026-inaproc\data\Legacy_ekatalog-archive_paket-e-purchasing_2026.json'

# ======================================================
# LOAD JSON
# ======================================================
def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            if isinstance(data, list):
                return pd.json_normalize(data)
            if isinstance(data, dict):
                for k in ['data','items','results']:
                    if k in data and isinstance(data[k], list):
                        return pd.json_normalize(data[k])
            return pd.json_normalize(data)
    except:
        return pd.DataFrame()

print("Load semua sumber...")

df1     = load_json(sumber1)
df1_2   = load_json(sumber1_2)
df2     = load_json(sumber2)
df2_1   = load_json(sumber2_1)
df2_2   = load_json(sumber2_2)
df2_3   = load_json(sumber2_3)
df2_4   = load_json(sumber2_4)
df2_5   = load_json(sumber2_5)
df3     = load_json(sumber3)
df4     = load_json(sumber4)
df5     = load_json(sumber5)
df5_1   = load_json(sumber5_1)
df5_1_1 = load_json(sumber5_1_1)
df5_2   = load_json(sumber5_2)
df5_3   = load_json(sumber5_3)
df5_4   = load_json(sumber5_4)
df5_5   = load_json(sumber5_5)
df6     = load_json(sumber6)
df7     = load_json(sumber7)

# ======================================================
# FILTER
# ======================================================
if not df2.empty and 'status_nontender' in df2.columns:
    df2 = df2[df2['status_nontender'] != 'Gagal/Batal']

if not df5.empty and 'status_tender' in df5.columns:
    df5 = df5[df5['status_tender'] != 'Gagal/Batal']

# ======================================================
# SET KD
# ======================================================
def get_set(df, col):
    if df.empty or col not in df.columns:
        return set()
    return set(df[col].astype(str).str.split(';').explode().str.strip())

set_selesai   = get_set(df2_1,'kd_nontender')
set_sppbj     = get_set(df2_2,'kd_nontender')
set_kontrak   = get_set(df2_3,'kd_nontender')
set_spmkspp   = get_set(df2_4,'kd_nontender')
set_bapbast   = get_set(df2_5,'kd_nontender')

set_t_selesai = get_set(df5_1,'kd_tender')
set_t_sppbj   = get_set(df5_2,'kd_tender')
set_t_kontrak = get_set(df5_3,'kd_tender')
set_t_spmkspp = get_set(df5_4,'kd_tender')
set_t_bapbast = get_set(df5_5,'kd_tender')

# ======================================================
# MAP NILAI KONTRAK (FIX MULTI KD)
# ======================================================
map_nt_kontrak = {}
if not df2_1.empty and 'nilai_kontrak' in df2_1.columns:
    for _, r in df2_1.iterrows():
        kd_list = str(r.get('kd_nontender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_nt_kontrak[k] = r.get('nilai_kontrak')

map_nt_pdn = {}
if not df2_1.empty and 'nilai_pdn_kontrak' in df2_1.columns:
    for _, r in df2_1.iterrows():
        kd_list = str(r.get('kd_nontender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_nt_pdn[k] = r.get('nilai_pdn_kontrak')

map_nt_umk = {}
if not df2_1.empty and 'nilai_umk_kontrak' in df2_1.columns:
    for _, r in df2_1.iterrows():
        kd_list = str(r.get('kd_nontender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_nt_umk[k] = r.get('nilai_umk_kontrak')

map_t_kontrak = {}
if not df5_1_1.empty and 'nilai_kontrak' in df5_1_1.columns:
    for _, r in df5_1_1.iterrows():
        kd_list = str(r.get('kd_tender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_t_kontrak[k] = r.get('nilai_kontrak')

map_t_pdn = {}
if not df5_3.empty and 'nilai_pdn_kontrak' in df5_3.columns:
    for _, r in df5_3.iterrows():
        kd_list = str(r.get('kd_tender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_t_pdn[k] = r.get('nilai_pdn_kontrak')

map_t_umk = {}
if not df5_3.empty and 'nilai_umk_kontrak' in df5_3.columns:
    for _, r in df5_3.iterrows():
        kd_list = str(r.get('kd_tender')).split(';')
        for k in kd_list:
            k = k.strip()
            if k:
                map_t_umk[k] = r.get('nilai_umk_kontrak')

# ======================================================
# STANDARD KD RUP (RAW + EXPLODE)
# ======================================================
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

df1   = standardize_kd_rup(df1,  'kd_rup')
df1_2 = standardize_kd_rup(df1_2,'kd_rup')
df2   = standardize_kd_rup(df2,  'kd_rup')
df3   = standardize_kd_rup(df3,  'kd_rup')
df4   = standardize_kd_rup(df4,  'kd_rup')
df5   = standardize_kd_rup(df5,  'kd_rup')
df6   = standardize_kd_rup(df6,  'rup_code')
df7   = standardize_kd_rup(df7,  'kd_rup')

# ======================================================
# MAP PAGU SUMBER 1 & 1_2
# ======================================================
map_pagu_s1   = df1.set_index('kd_rup')['pagu']   if not df1.empty   else {}
map_pagu_s1_2 = df1_2.set_index('kd_rup')['pagu'] if not df1_2.empty else {}

def get_pagu_multi(kd_list, tipe='s1'):
    total = 0
    if not isinstance(kd_list, list):
        return None
    for k in kd_list:
        try:
            if tipe=='s1' and k in map_pagu_s1:
                total += map_pagu_s1[k]
            if tipe=='s1_2' and k in map_pagu_s1_2:
                total += map_pagu_s1_2[k]
        except:
            pass
    return total if total!=0 else None

# ======================================================
# CLEAN ILLEGAL CHAR
# ======================================================
def clean_illegal_chars(df):
    return df.map(lambda x: re.sub(r'[\x00-\x1F]', '', str(x)) if isinstance(x,str) else x)

# ======================================================
# MAPPING SUMBER 1
# ======================================================
df1_map = df1.set_index('kd_rup') if not df1.empty else pd.DataFrame()

def get_s1(kd, col):
    try:
        if pd.isna(kd) or df1_map.empty:
            return None
        val = df1_map.loc[int(kd), col]
        return None if pd.isna(val) else val
    except:
        return None

# ======================================================
# SUMBER 2
# ======================================================
data_s2=[]
for _,r in df2.iterrows():
    kd=r.get('kd_rup')
    kd_list=r.get('kd_rup_list')
    kd_nt_list = [i.strip() for i in str(r.get('kd_nontender')).split(';')] if pd.notna(r.get('kd_nontender')) else []

    status = r.get('status_nontender')
    for k in kd_nt_list:
        if k in set_bapbast:
            status='BAPBAST'; break
        elif k in set_spmkspp:
            status='SPMKSPP'; break
        elif k in set_kontrak:
            status='Kontrak'; break
        elif k in set_sppbj:
            status='SPPBJ'; break
        elif k in set_selesai:
            status='Non Tender Selesai'; break

    nilai_hasil=None
    found=False
    for k in kd_nt_list:
        if k in map_nt_kontrak:
            nilai_hasil=map_nt_kontrak[k]; found=True; break
    if not found:
        nilai_hasil="N/A"
    elif nilai_hasil is not None and not isinstance(nilai_hasil, str) and pd.isna(nilai_hasil):
        nilai_hasil=""

    nilai_pdn="N/A"
    found=False
    for k in kd_nt_list:
        if k in map_nt_pdn:
            nilai_pdn = map_nt_pdn[k]
            if nilai_pdn is not None and not isinstance(nilai_pdn, str) and pd.isna(nilai_pdn):
                nilai_pdn=""
            found=True
            break

    nilai_umk="N/A"
    found=False
    for k in kd_nt_list:
        if k in map_nt_umk:
            nilai_umk = map_nt_umk[k]
            if nilai_umk is not None and not isinstance(nilai_umk, str) and pd.isna(nilai_umk):
                nilai_umk=""
            found=True
            break

    pagu = get_pagu_multi(kd_list,'s1')

    data_s2.append({
        'Kode RUP':r.get('kd_rup_raw'),
        'Satuan Kerja':r.get('nama_satker'),
        'Nama Paket':r.get('nama_paket'),
        'Metode Pengadaan':r.get('mtd_pemilihan'),
        'Jenis Pengadaan':r.get('jenis_pengadaan'),
        'Sumber Dana':r.get('sumber_dana'),
        'PDN':get_s1(kd,'status_pdn'),
        'UKM':get_s1(kd,'status_ukm'),
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':status,
        'Kode Paket':r.get('kd_nontender'),
        'Nilai HPS':r.get('hps'),
        'Nilai PDN':nilai_pdn,
        'Nilai UMK':nilai_umk,
        'Versi':"",
        'Metode':'Non Tender',
        'Sumber':'Sumber 2'
    })

df_s2=pd.DataFrame(data_s2)

# ======================================================
# SUMBER 3
# ======================================================
data_s3=[]
for _,r in df3.iterrows():
    kd=r.get('kd_rup')
    kd_list=r.get('kd_rup_list')
    pagu = get_pagu_multi(kd_list,'s1')

    nilai_hasil = r.get('total_realisasi')
    if pd.isna(nilai_hasil):
        nilai_hasil=""

    nilai_pdn = r.get('nilai_pdn_pct')
    nilai_umk = r.get('nilai_umk_pct')

    data_s3.append({
        'Kode RUP':r.get('kd_rup_raw'),
        'Satuan Kerja':r.get('nama_satker'),
        'Nama Paket':r.get('nama_paket'),
        'Metode Pengadaan':r.get('mtd_pemilihan'),
        'Jenis Pengadaan':r.get('kategori_pengadaan'),
        'Sumber Dana':r.get('sumber_dana'),
        'PDN':get_s1(kd,'status_pdn'),
        'UKM':get_s1(kd,'status_ukm'),
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':r.get('status_nontender_pct_ket'),
        'Kode Paket':r.get('kd_nontender_pct'),
        'Nilai HPS':pd.NA,
        'Nilai PDN':nilai_pdn,
        'Nilai UMK':nilai_umk,
        'Versi':"",
        'Metode':'Pencatatan Non Tender',
        'Sumber':'Sumber 3'
    })

df_s3=pd.DataFrame(data_s3)

# ======================================================
# SUMBER 4
# ======================================================
data_s4=[]
swakelola_map = df1_2.set_index('kd_rup')['tipe_swakelola'] if not df1_2.empty else {}

for _,r in df4.iterrows():
    kd=r.get('kd_rup')
    kd_list=r.get('kd_rup_list')

    jenis = f"Swakelola {int(swakelola_map[kd])}" if kd in swakelola_map else "N/A"
    pagu = get_pagu_multi(kd_list,'s1_2')

    nilai_hasil = r.get('total_realisasi')
    if pd.isna(nilai_hasil):
        nilai_hasil=""

    nilai_pdn = r.get('nilai_pdn_pct')
    nilai_umk = r.get('nilai_umk_pct')

    data_s4.append({
        'Kode RUP':r.get('kd_rup_raw'),
        'Satuan Kerja':r.get('nama_satker'),
        'Nama Paket':r.get('nama_paket'),
        'Metode Pengadaan':'Swakelola',
        'Jenis Pengadaan':jenis,
        'Sumber Dana':r.get('sumber_dana'),
        'PDN':"PDN" if r.get('nilai_pdn_pct',0)!=0 else "Tidak",
        'UKM':"UKM" if r.get('nilai_umk_pct',0)!=0 else "Tidak",
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':r.get('status_swakelola_pct_ket'),
        'Kode Paket':r.get('kd_swakelola_pct'),
        'Nilai HPS':pd.NA,
        'Nilai PDN':nilai_pdn,
        'Nilai UMK':nilai_umk,
        'Versi':"",
        'Metode':'Pencatatan Swakelola',
        'Sumber':'Sumber 4'
    })

df_s4=pd.DataFrame(data_s4)

# ======================================================
# TAMBAHAN SUMBER 1_2
# ======================================================
data_s1_2=[]
set_s4_kd = set(df4['kd_rup_raw'].astype(str).str.split(';').explode().str.strip()) \
.union(set(pd.Series([i for sub in df4['kd_rup_list'] if isinstance(sub,list) for i in sub]).astype(str))) if not df4.empty else set()

for _,r in df1_2.iterrows():
    kd=r.get('kd_rup')

    if str(kd) not in set_s4_kd:
        jenis = f"Swakelola {int(swakelola_map[kd])}" if kd in swakelola_map else "N/A"

        data_s1_2.append({
            'Kode RUP':kd,
            'Satuan Kerja':r.get('nama_satker'),
            'Nama Paket':r.get('nama_paket'),
            'Metode Pengadaan':'Swakelola',
            'Jenis Pengadaan':jenis,
            'Sumber Dana':None,
            'PDN':None,
            'UKM':None,
            'Nilai Pagu RUP':r.get('pagu'),
            'Nilai Hasil Pemilihan':"",
            'Status':'Pengumuman RUP',
            'Kode Paket':pd.NA,
            'Nilai HPS':pd.NA,
            'Nilai PDN':pd.NA,
            'Nilai UMK':pd.NA,
            'Versi':"",
            'Metode':'Swakelola',
            'Sumber':'Sumber 1_2'
        })

df_s1_2=pd.DataFrame(data_s1_2)

# ======================================================
# SUMBER 5
# ======================================================
data_s5=[]
for _,r in df5.iterrows():
    kd=r.get('kd_rup')
    kd_list=r.get('kd_rup_list')

    kd_t_list = [i.strip() for i in str(r.get('kd_tender')).split(';')] if pd.notna(r.get('kd_tender')) else []

    status = r.get('status_tender')
    for k in kd_t_list:
        if k in set_t_bapbast:
            status='BAPBAST'; break
        elif k in set_t_spmkspp:
            status='SPMKSPP'; break
        elif k in set_t_kontrak:
            status='Kontrak'; break
        elif k in set_t_sppbj:
            status='SPPBJ'; break
        elif k in set_t_selesai:
            status='Tender Selesai'; break

    nilai_hasil=None
    found=False
    for k in kd_t_list:
        if k in map_t_kontrak:
            nilai_hasil=map_t_kontrak[k]; found=True; break
    if not found:
        nilai_hasil="N/A"
    elif nilai_hasil is not None and not isinstance(nilai_hasil, str) and pd.isna(nilai_hasil):
        nilai_hasil=""

    nilai_pdn="N/A"
    found=False
    for k in kd_t_list:
        if k in map_t_pdn:
            nilai_pdn = map_t_pdn[k]
            if nilai_pdn is not None and not isinstance(nilai_pdn, str) and pd.isna(nilai_pdn):
                nilai_pdn=""
            found=True
            break

    nilai_umk="N/A"
    found=False
    for k in kd_t_list:
        if k in map_t_umk:
            nilai_umk = map_t_umk[k]
            if nilai_umk is not None and not isinstance(nilai_umk, str) and pd.isna(nilai_umk):
                nilai_umk=""
            found=True
            break

    pagu = get_pagu_multi(kd_list,'s1')

    data_s5.append({
        'Kode RUP':r.get('kd_rup_raw'),
        'Satuan Kerja':r.get('nama_satker'),
        'Nama Paket':r.get('nama_paket'),
        'Metode Pengadaan':r.get('mtd_pemilihan'),
        'Jenis Pengadaan':r.get('jenis_pengadaan'),
        'Sumber Dana':r.get('sumber_dana'),
        'PDN':get_s1(kd,'status_pdn'),
        'UKM':get_s1(kd,'status_ukm'),
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':status,
        'Kode Paket':r.get('kd_tender'),
        'Nilai HPS':r.get('hps'),
        'Nilai PDN':nilai_pdn,
        'Nilai UMK':nilai_umk,
        'Versi':"",
        'Metode':'Tender',
        'Sumber':'Sumber 5'
    })

df_s5=pd.DataFrame(data_s5)

# ======================================================
# SUMBER 6
# ======================================================
data_s6=[]
for _,r in df6.iterrows():
    kd=r.get('rup_code')
    kd_list=r.get('rup_code_list')
    pagu = get_pagu_multi(kd_list,'s1')

    nilai_hasil = r.get('total')
    if pd.isna(nilai_hasil):
        nilai_hasil=""

    data_s6.append({
        'Kode RUP':r.get('rup_code_raw'),
        'Satuan Kerja':r.get('nama_satker'),
        'Nama Paket':r.get('rup_name'),
        'Metode Pengadaan':'E-Purchasing',
        'Jenis Pengadaan':get_s1(kd,'jenis_pengadaan'),
        'Sumber Dana':r.get('funding_source'),
        'PDN':get_s1(kd,'status_pdn'),
        'UKM':get_s1(kd,'status_ukm'),
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':r.get('status'),
        'Kode Paket':r.get('order_id'),
        'Nilai HPS':pd.NA,
        'Nilai PDN':pd.NA,
        'Nilai UMK':pd.NA,
        'Versi':'Versi 6',
        'Metode':'E-Purchasing',
        'Sumber':'Sumber 6'
    })

df_s6=pd.DataFrame(data_s6)

# ======================================================
# SUMBER 7
# ======================================================
data_s7=[]
for _,r in df7.iterrows():
    kd=r.get('kd_rup')
    kd_list=r.get('kd_rup_list')
    pagu = get_pagu_multi(kd_list,'s1')

    nilai_hasil = r.get('total_harga')
    if pd.isna(nilai_hasil):
        nilai_hasil=""

    data_s7.append({
        'Kode RUP':r.get('kd_rup_raw'),
        'Satuan Kerja':r.get('nama_satker') if pd.notna(r.get('nama_satker')) else get_s1(kd,'nama_satker'),
        'Nama Paket':r.get('nama_paket'),
        'Metode Pengadaan':'E-Purchasing',
        'Jenis Pengadaan':get_s1(kd,'jenis_pengadaan'),
        'Sumber Dana':r.get('nama_sumber_dana'),
        'PDN':get_s1(kd,'status_pdn'),
        'UKM':get_s1(kd,'status_ukm'),
        'Nilai Pagu RUP':pagu,
        'Nilai Hasil Pemilihan':nilai_hasil,
        'Status':r.get('paket_status_str'),
        'Kode Paket':r.get('kd_paket'),
        'Nilai HPS':pd.NA,
        'Nilai PDN':pd.NA,
        'Nilai UMK':pd.NA,
        'Versi':'Versi 5',
        'Metode':'E-Purchasing',
        'Sumber':'Sumber 7'
    })

df_s7=pd.DataFrame(data_s7)

# ======================================================
# TAMBAHAN SUMBER 1 (DUAL FIX)
# ======================================================
def get_all_kd(df, col):
    if df.empty or col not in df.columns:
        return set()
    raw = set(df[col].astype(str).str.split(';').explode().str.strip())
    lst = set(pd.Series([i for sub in df[col.replace('_raw','_list')] if isinstance(sub,list) for i in sub]).astype(str)) if col.replace('_raw','_list') in df.columns else set()
    return raw.union(lst)

set_all = get_all_kd(df2,'kd_rup_raw') \
.union(get_all_kd(df3,'kd_rup_raw')) \
.union(get_all_kd(df4,'kd_rup_raw')) \
.union(get_all_kd(df5,'kd_rup_raw')) \
.union(get_all_kd(df6,'rup_code_raw')) \
.union(get_all_kd(df7,'kd_rup_raw'))

data_s1=[]
for _,r in df1.iterrows():
    kd=r.get('kd_rup')

    if str(kd) not in set_all:
        data_s1.append({
            'Kode RUP':kd,
            'Satuan Kerja':r.get('nama_satker'),
            'Nama Paket':r.get('nama_paket'),
            'Metode Pengadaan':r.get('metode_pengadaan'),
            'Jenis Pengadaan':r.get('jenis_pengadaan'),
            'Sumber Dana':None,
            'PDN':'PDN' if r.get('status_pdn')=='PDN' else 'Non-PDN',
            'UKM':'UKM' if r.get('status_ukm')=='UKM' else 'Non-UKM',
            'Nilai Pagu RUP':r.get('pagu'),
            'Nilai Hasil Pemilihan':"",
            'Status':'Pengumuman RUP',
            'Kode Paket':pd.NA,
            'Nilai HPS':pd.NA,
            'Nilai PDN':pd.NA,
            'Nilai UMK':pd.NA,
            'Versi':"",
            'Metode':r.get('metode_pengadaan'),
            'Sumber':'Sumber 1'
        })

df_s1=pd.DataFrame(data_s1)

# ======================================================
# FILTER FINAL (ANTI DUPLIKAT AMAN)
# ======================================================
def safe_col(df, col):
    if df.empty or col not in df.columns:
        return pd.Series([], dtype=object)
    raw = df[col].astype(str)
    lst = pd.Series([str(i) for sub in df.get(col.replace('Kode RUP','kd_rup_list'),[]) if isinstance(sub,list) for i in sub])
    return pd.concat([raw,lst],ignore_index=True)

df_s1 = df_s1[~safe_col(df_s1,'Kode RUP').isin(pd.concat([
    safe_col(df_s2,'Kode RUP'),
    safe_col(df_s3,'Kode RUP'),
    safe_col(df_s5,'Kode RUP'),
    safe_col(df_s6,'Kode RUP'),
    safe_col(df_s7,'Kode RUP')
]))]

df_s1_2 = df_s1_2[~safe_col(df_s1_2,'Kode RUP').isin(safe_col(df_s4,'Kode RUP'))]

# ======================================================
# CLEAN & GABUNG
# ======================================================
final_df = pd.concat([df_s2,df_s3,df_s4,df_s1_2,df_s5,df_s6,df_s7,df_s1],ignore_index=True)
final_df = clean_illegal_chars(final_df)

# ======================================================
# SUSUN KOLOM
# ======================================================
cols = [
    'Kode RUP','Satuan Kerja','Nama Paket','Metode Pengadaan','Jenis Pengadaan',
    'Sumber Dana','PDN','UKM','Nilai Pagu RUP','Nilai Hasil Pemilihan',
    'Status','Kode Paket','Nilai HPS','Nilai PDN','Nilai UMK','Versi','Metode','Sumber'
]

final_df = final_df[cols]

# ======================================================
# BERSIHKAN NaN AGAR JSON VALID
# ======================================================
final_df = final_df.fillna("")

# ======================================================
# SIMPAN JSON
# ======================================================
output_json = r'D:\rup-2026-inaproc\data\rekap_pengadaan.json'

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(final_df.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

# ======================================================
# SIMPAN LAST UPDATE
# ======================================================
with open(r'D:\rup-2026-inaproc\data\last-update-pengadaan.txt', "w") as f:
    f.write(datetime.now().strftime("%d %B %Y %H:%M WIB"))

print("\nSELESAI | Total data:", len(final_df))
print("Output  :", output_json)