import os
import re
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# SETUP PATH UTAMA
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_MASTER_DIR = os.path.join(BASE_DIR, 'data_master')

# ==========================================
# PALET WARNA TEMA
# ==========================================
TEMA_TERANG = {
    'bg': '#f1f5f9', 'card': '#ffffff', 'fg': '#0f172a', 'muted': '#64748b',
    'border': '#d5dde8', 'accent': '#4f46e5', 'accent_hover': '#4338ca',
    'accent_fg': '#ffffff', 'btn': '#e2e8f0', 'btn_hover': '#cbd5e1',
    'danger': '#dc2626', 'danger_hover': '#b91c1c',
    'header_bg': '#4f46e5', 'header_fg': '#ffffff', 'header_sub': '#c7d2fe',
    'row_alt': '#f8fafc', 'highlight_bg': '#fde047', 'highlight_fg': '#000000',
    'ok': '#16a34a', 'info': '#2563eb', 'warn': '#d97706',
    'j_key': '#4338ca', 'j_str': '#059669', 'j_num': '#d97706',
    'j_kw': '#db2777', 'j_mark': '#0369a1',
}
TEMA_GELAP = {
    'bg': '#0b1120', 'card': '#151e32', 'fg': '#e2e8f0', 'muted': '#94a3b8',
    'border': '#2a3652', 'accent': '#818cf8', 'accent_hover': '#6366f1',
    'accent_fg': '#0b1120', 'btn': '#25314d', 'btn_hover': '#34436a',
    'danger': '#f87171', 'danger_hover': '#ef4444',
    'header_bg': '#151e32', 'header_fg': '#f1f5f9', 'header_sub': '#94a3b8',
    'row_alt': '#1a2540', 'highlight_bg': '#ca8a04', 'highlight_fg': '#ffffff',
    'ok': '#4ade80', 'info': '#60a5fa', 'warn': '#fbbf24',
    'j_key': '#a5b4fc', 'j_str': '#6ee7b7', 'j_num': '#fbbf24',
    'j_kw': '#f9a8d4', 'j_mark': '#7dd3fc',
}

FONT_UI = ('Segoe UI', 10)
FONT_UI_BOLD = ('Segoe UI', 10, 'bold')
FONT_KODE = ('Consolas', 10)

POLA_JSON = re.compile(
    r'(?P<key>"(?:\\.|[^"\\])*"(?=\s*:))'
    r'|(?P<str>"(?:\\.|[^"\\])*")'
    r'|(?P<num>-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)'
    r'|(?P<kw>\b(?:true|false|null)\b)'
    r'|(?P<mark>^(?:===|---|>>>|❌).*$)'
)


class AppPelacakJSON(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Detective - Pelacak & Perbandingan Kode Paket JSON")
        self.geometry("1200x750")
        self.minsize(980, 620)

        try:
            self.state('zoomed')
        except Exception:
            pass

        self.hasil_pencarian = {}
        self.mode_perbandingan = False
        self.dict_file_viewer = {}

        # === TEMA ===
        self.mode_gelap = True  # default: mode gelap
        self.warna = TEMA_GELAP
        self.daftar_text = []
        self.status_kind = 'muted'
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # 'clam' wajib agar warna bisa diubah

        # === HEADER ===
        self.header = tk.Frame(self)
        self.header.pack(fill="x")
        kiri = tk.Frame(self.header)
        kiri.pack(side="left", padx=20, pady=12)
        self.lbl_judul = tk.Label(kiri, text="🕵️  Data Detective", font=('Segoe UI', 17, 'bold'))
        self.lbl_judul.pack(anchor="w")
        self.lbl_sub = tk.Label(kiri, text="Pelacak & Perbandingan Kode Paket JSON", font=('Segoe UI', 10))
        self.lbl_sub.pack(anchor="w")
        self.header_kiri = kiri

        self.btn_tema = tk.Button(self.header, text="🌙  Mode Gelap", command=self.toggle_tema,
                                  relief="flat", bd=0, cursor="hand2", font=FONT_UI_BOLD,
                                  padx=16, pady=7)
        self.btn_tema.pack(side="right", padx=20)

        # === BODY ===
        body = ttk.Frame(self, padding=(14, 12, 14, 12))
        body.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook, padding=12)
        self.tab2 = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab1, text="  🔍  Pencari & Pembanding  ")
        self.notebook.add(self.tab2, text="  📂  Viewer Data JSON  ")

        self.create_top_frame_tab1()
        self.create_main_layout_tab1()
        self.create_layout_tab2()

        # Terapkan tema awal (paling akhir)
        self.terapkan_tema()

    # ==========================================
    # TEMA TERANG / GELAP
    # ==========================================
    def toggle_tema(self):
        self.mode_gelap = not self.mode_gelap
        self.terapkan_tema()

    def terapkan_tema(self):
        w = TEMA_GELAP if self.mode_gelap else TEMA_TERANG
        self.warna = w
        s = self.style

        self.configure(bg=w['bg'])
        self.option_add('*TCombobox*Listbox.background', w['card'])

        # --- Header ---
        self.header.configure(bg=w['header_bg'])
        self.header_kiri.configure(bg=w['header_bg'])
        self.lbl_judul.configure(bg=w['header_bg'], fg=w['header_fg'])
        self.lbl_sub.configure(bg=w['header_bg'], fg=w['header_sub'])
        self.btn_tema.configure(
            text="☀️  Mode Terang" if self.mode_gelap else "🌙  Mode Gelap",
            bg=w['accent'] if self.mode_gelap else '#ffffff',
            fg=w['accent_fg'] if self.mode_gelap else w['accent'],
            activebackground=w['accent_hover'],
            activeforeground='#ffffff')

        # --- Default ttk ---
        s.configure('.', background=w['bg'], foreground=w['fg'], font=FONT_UI,
                    fieldbackground=w['card'], bordercolor=w['border'],
                    lightcolor=w['border'], darkcolor=w['border'],
                    troughcolor=w['bg'], focuscolor=w['bg'])
        s.configure('TFrame', background=w['bg'])
        s.configure('TLabel', background=w['bg'], foreground=w['fg'])
        s.configure('TLabelframe', background=w['bg'], bordercolor=w['border'], relief='solid', borderwidth=1)
        s.configure('TLabelframe.Label', background=w['bg'], foreground=w['accent'], font=FONT_UI_BOLD)
        s.configure('TPanedwindow', background=w['bg'])
        s.configure('TCheckbutton', background=w['bg'], foreground=w['fg'], font=FONT_UI)
        s.map('TCheckbutton', background=[('active', w['bg'])])

        # --- Tombol ---
        s.configure('TButton', background=w['btn'], foreground=w['fg'], padding=(14, 7),
                    borderwidth=0, relief='flat', font=FONT_UI_BOLD)
        s.map('TButton', background=[('active', w['btn_hover']), ('disabled', w['border'])],
              foreground=[('disabled', w['muted'])])
        s.configure('Accent.TButton', background=w['accent'], foreground=w['accent_fg'])
        s.map('Accent.TButton', background=[('active', w['accent_hover']), ('disabled', w['border'])],
              foreground=[('disabled', w['muted'])])
        s.configure('Danger.TButton', background=w['danger'], foreground='#ffffff')
        s.map('Danger.TButton', background=[('active', w['danger_hover'])])

        # --- Entry ---
        s.configure('TEntry', fieldbackground=w['card'], foreground=w['fg'],
                    insertcolor=w['fg'], padding=6, bordercolor=w['border'])
        s.map('TEntry', bordercolor=[('focus', w['accent'])],
              lightcolor=[('focus', w['accent'])], darkcolor=[('focus', w['accent'])])

        # --- Notebook / Tab ---
        s.configure('TNotebook', background=w['bg'], borderwidth=0, tabmargins=(0, 0, 0, 0))
        s.configure('TNotebook.Tab', background=w['btn'], foreground=w['muted'],
                    padding=(14, 9), font=FONT_UI_BOLD, borderwidth=0)
        s.map('TNotebook.Tab',
              background=[('selected', w['accent']), ('active', w['btn_hover'])],
              foreground=[('selected', w['accent_fg']), ('active', w['fg'])])

        # --- Treeview ---
        s.configure('Treeview', background=w['card'], foreground=w['fg'],
                    fieldbackground=w['card'], rowheight=28, borderwidth=0, font=FONT_UI)
        s.map('Treeview', background=[('selected', w['accent'])],
              foreground=[('selected', w['accent_fg'])])
        s.configure('Treeview.Heading', background=w['btn'], foreground=w['fg'],
                    font=FONT_UI_BOLD, padding=(8, 7), relief='flat', borderwidth=0)
        s.map('Treeview.Heading', background=[('active', w['btn_hover'])])
        for tree in (self.tree, self.tree_viewer):
            tree.tag_configure('odd', background=w['row_alt'])
            tree.tag_configure('even', background=w['card'])

        # --- Scrollbar ---
        s.configure('Vertical.TScrollbar', background=w['btn'], troughcolor=w['bg'],
                    bordercolor=w['bg'], arrowcolor=w['muted'], relief='flat')
        s.configure('Horizontal.TScrollbar', background=w['btn'], troughcolor=w['bg'],
                    bordercolor=w['bg'], arrowcolor=w['muted'], relief='flat')
        s.map('Vertical.TScrollbar', background=[('active', w['btn_hover'])])
        s.map('Horizontal.TScrollbar', background=[('active', w['btn_hover'])])

        # --- Widget Text (manual) ---
        for txt in self.daftar_text:
            txt.configure(bg=w['card'], fg=w['fg'], insertbackground=w['fg'],
                          selectbackground=w['accent'], selectforeground=w['accent_fg'],
                          highlightbackground=w['border'], highlightcolor=w['accent'],
                          highlightthickness=1, relief='flat', padx=10, pady=8)
            txt.tag_config('j_key', foreground=w['j_key'])
            txt.tag_config('j_str', foreground=w['j_str'])
            txt.tag_config('j_num', foreground=w['j_num'])
            txt.tag_config('j_kw', foreground=w['j_kw'], font=('Consolas', 10, 'bold'))
            txt.tag_config('j_mark', foreground=w['j_mark'], font=('Consolas', 10, 'bold'))
            txt.tag_config('highlight_search', background=w['highlight_bg'], foreground=w['highlight_fg'])
            txt.tag_raise('highlight_search')

        self.set_status(self.lbl_status.cget('text'), self.status_kind)

    def set_status(self, teks, kind='muted'):
        self.status_kind = kind
        warna = self.warna.get(kind, self.warna['muted'])
        self.lbl_status.config(text=teks, foreground=warna)

    # ==========================================
    # HELPER TEKS
    # ==========================================
    def buat_text(self, parent):
        txt = tk.Text(parent, wrap="none", font=FONT_KODE, undo=False)
        txt.bind("<Key>", self.kunci_teks)
        self.daftar_text.append(txt)
        return txt

    def warnai_json(self, txt, content):
        if len(content) > 400000:  # terlalu besar, lewati pewarnaan agar tetap ringan
            return
        for no, baris in enumerate(content.split("\n"), 1):
            if not baris:
                continue
            for m in POLA_JSON.finditer(baris):
                txt.tag_add('j_' + m.lastgroup, f"{no}.{m.start()}", f"{no}.{m.end()}")

    def isi_teks(self, txt, content):
        txt.delete(1.0, tk.END)
        txt.insert(tk.END, content)
        self.warnai_json(txt, content)
        txt.tag_raise('highlight_search')

    @staticmethod
    def json_cantik(data):
        return json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)

    # ==========================================
    # KONTEN TAB 1: PENCARI & PEMBANDING
    # ==========================================
    def create_top_frame_tab1(self):
        self.frame_top = ttk.LabelFrame(self.tab1, text="  Mesin Pencari & Pembanding  ", padding=(15, 12))
        self.frame_top.pack(side="top", fill="x", pady=(0, 12))

        ttk.Label(self.frame_top, text="Kata Kunci 1:", font=FONT_UI_BOLD).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.ent_cari = ttk.Entry(self.frame_top, width=30, font=('Segoe UI', 11))
        self.ent_cari.grid(row=0, column=1, padx=(0, 15), sticky="w")
        self.ent_cari.bind("<Return>", lambda e: self.mulai_pencarian())

        self.btn_mode_banding = ttk.Button(self.frame_top, text="🆚 Aktifkan Perbandingan", command=self.toggle_mode_perbandingan)
        self.btn_mode_banding.grid(row=0, column=2, padx=(0, 10), sticky="w")

        self.btn_cari = ttk.Button(self.frame_top, text="🔍 Lacak Data", style='Accent.TButton', command=self.mulai_pencarian)
        self.btn_cari.grid(row=0, column=3, padx=(0, 10), sticky="w")

        self.lbl_status = ttk.Label(self.frame_top, text="Siap digunakan.", foreground="gray")
        self.lbl_status.grid(row=0, column=4, sticky="e", padx=(20, 0))
        self.frame_top.columnconfigure(4, weight=1)

        self.lbl_cari_2 = ttk.Label(self.frame_top, text="Kata Kunci 2:", font=FONT_UI_BOLD)
        self.ent_cari_2 = ttk.Entry(self.frame_top, width=30, font=('Segoe UI', 11))
        self.ent_cari_2.bind("<Return>", lambda e: self.mulai_pencarian())

    def toggle_mode_perbandingan(self):
        self.mode_perbandingan = not self.mode_perbandingan
        if self.mode_perbandingan:
            self.btn_mode_banding.config(text="✖️ Matikan Perbandingan")
            self.lbl_cari_2.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(10, 0))
            self.ent_cari_2.grid(row=1, column=1, padx=(0, 15), sticky="w", pady=(10, 0))
            self.lbl_status.grid(row=1, column=4, sticky="e")
            self.frame_p2.pack(side="left", fill="both", expand=True, padx=(5, 0))
            self.set_status("Mode Perbandingan Aktif. Masukkan Kode ke-2.", 'info')
        else:
            self.btn_mode_banding.config(text="🆚 Aktifkan Perbandingan")
            self.lbl_cari_2.grid_forget()
            self.ent_cari_2.grid_forget()
            self.ent_cari_2.delete(0, tk.END)
            self.lbl_status.grid(row=0, column=4, sticky="e")
            self.frame_p2.pack_forget()
            self.txt_preview_2.delete(1.0, tk.END)
            self.set_status("Kembali ke Mode Tunggal.", 'muted')

    def create_main_layout_tab1(self):
        paned_window = ttk.PanedWindow(self.tab1, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)

        frame_kiri = ttk.LabelFrame(paned_window, text="  Ditemukan di File Berikut  ", padding=6)
        paned_window.add(frame_kiri, weight=1)

        kolom = ("tahun", "file", "jumlah")
        self.tree = ttk.Treeview(frame_kiri, columns=kolom, show="headings", selectmode="browse")
        self.tree.heading("tahun", text="Tahun")
        self.tree.heading("file", text="Nama File JSON")
        self.tree.heading("jumlah", text="Match")
        self.tree.column("tahun", width=60, anchor="center")
        self.tree.column("file", width=250, anchor="w")
        self.tree.column("jumlah", width=110, anchor="center")

        scrollbar_tree = ttk.Scrollbar(frame_kiri, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar_tree.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.tampilkan_isi_data)

        self.frame_kanan_container = ttk.Frame(paned_window)
        paned_window.add(self.frame_kanan_container, weight=3)

        frame_cari_t1 = ttk.Frame(self.frame_kanan_container)
        frame_cari_t1.pack(fill="x", pady=(0, 8))
        ttk.Label(frame_cari_t1, text="Cari Kata di Hasil JSON:", font=FONT_UI_BOLD).pack(side="left")
        self.ent_cari_internal_t1 = ttk.Entry(frame_cari_t1, width=30)
        self.ent_cari_internal_t1.pack(side="left", padx=8)
        self.ent_cari_internal_t1.bind("<Return>", lambda e: self.cari_internal_semua())
        ttk.Button(frame_cari_t1, text="⚡ Highlight Kata", command=self.cari_internal_semua).pack(side="left")

        self.frame_p1 = ttk.LabelFrame(self.frame_kanan_container, text="  Hasil Kata Kunci 1  ", padding=6)
        self.frame_p1.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.txt_preview_1 = self.buat_text(self.frame_p1)
        scroll_y1 = ttk.Scrollbar(self.frame_p1, orient="vertical", command=self.txt_preview_1.yview)
        scroll_x1 = ttk.Scrollbar(self.frame_p1, orient="horizontal", command=self.txt_preview_1.xview)
        self.txt_preview_1.configure(yscrollcommand=scroll_y1.set, xscrollcommand=scroll_x1.set)
        scroll_x1.pack(side="bottom", fill="x")
        self.txt_preview_1.pack(side="left", fill="both", expand=True)
        scroll_y1.pack(side="right", fill="y")

        self.frame_p2 = ttk.LabelFrame(self.frame_kanan_container, text="  Hasil Kata Kunci 2  ", padding=6)
        self.txt_preview_2 = self.buat_text(self.frame_p2)
        scroll_y2 = ttk.Scrollbar(self.frame_p2, orient="vertical", command=self.txt_preview_2.yview)
        scroll_x2 = ttk.Scrollbar(self.frame_p2, orient="horizontal", command=self.txt_preview_2.xview)
        self.txt_preview_2.configure(yscrollcommand=scroll_y2.set, xscrollcommand=scroll_x2.set)
        scroll_x2.pack(side="bottom", fill="x")
        self.txt_preview_2.pack(side="left", fill="both", expand=True)
        scroll_y2.pack(side="right", fill="y")

    # ==========================================
    # LOGIKA PROSES TAB 1
    # ==========================================
    def mulai_pencarian(self):
        kw1 = self.ent_cari.get().strip()
        kw2 = self.ent_cari_2.get().strip() if self.mode_perbandingan else ""

        if len(kw1) < 3:
            messagebox.showwarning("Peringatan", "Kata kunci 1 terlalu pendek! Masukkan minimal 3 karakter.")
            return
        if self.mode_perbandingan and len(kw2) < 3:
            messagebox.showwarning("Peringatan", "Mode Perbandingan Aktif! Masukkan Kata Kunci 2 minimal 3 karakter.")
            return

        self.btn_cari.config(state="disabled")
        self.btn_mode_banding.config(state="disabled")
        self.set_status("Sedang menyisir data JSON...", 'info')

        for i in self.tree.get_children():
            self.tree.delete(i)
        self.txt_preview_1.delete(1.0, tk.END)
        self.txt_preview_2.delete(1.0, tk.END)
        self.hasil_pencarian.clear()

        thread = threading.Thread(target=self.proses_pencarian, args=(kw1, kw2))
        thread.daemon = True
        thread.start()

    def proses_pencarian(self, kw1, kw2):
        if not os.path.exists(DATA_DIR):
            self.after(0, self.update_ui_selesai, "Folder 'data' tidak ditemukan!")
            return

        total_file_diperiksa = 0
        total_ditemukan = 0

        for root, dirs, files in os.walk(DATA_DIR):
            nama_folder = os.path.basename(root)
            tahun = nama_folder if nama_folder.isdigit() else "-"

            for file in files:
                if file.endswith(".json"):
                    total_file_diperiksa += 1
                    filepath = os.path.join(root, file)
                    m1, m2 = self.ekstrak_data_json(filepath, kw1, kw2)

                    if m1 or m2:
                        total_ditemukan += 1
                        key_unik = f"{tahun}|{file}"
                        self.hasil_pencarian[key_unik] = {"m1": m1, "m2": m2}
                        info_jumlah = f"KW1: {len(m1)}"
                        if self.mode_perbandingan:
                            info_jumlah += f" | KW2: {len(m2)}"
                        self.after(0, self.tambah_baris_tabel, tahun, file, info_jumlah, key_unik)

        pesan_akhir = f"Selesai! Diperiksa: {total_file_diperiksa} file | Ditemukan: {total_ditemukan} file."
        self.after(0, self.update_ui_selesai, pesan_akhir)

    def ekstrak_data_json(self, filepath, kw1, kw2=""):
        m1, m2 = [], []
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            has_kw1 = kw1 in content
            has_kw2 = kw2 in content if kw2 else False
            if not has_kw1 and not has_kw2:
                return m1, m2

            data = json.loads(content)
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    items = data['data']
                else:
                    items = [data]

            for item in items:
                item_str = json.dumps(item)
                if has_kw1 and kw1 in item_str:
                    m1.append(item)
                if has_kw2 and kw2 in item_str:
                    m2.append(item)
        except Exception:
            pass
        return m1, m2

    def tambah_baris_tabel(self, tahun, file, jumlah, key_unik):
        zebra = 'odd' if len(self.tree.get_children()) % 2 else 'even'
        self.tree.insert("", "end", values=(tahun, file, jumlah), tags=(key_unik, zebra))

    def update_ui_selesai(self, pesan):
        self.set_status(pesan, 'ok')
        self.btn_cari.config(state="normal")
        self.btn_mode_banding.config(state="normal")
        if not self.hasil_pencarian:
            self.isi_teks(self.txt_preview_1, ">>> KODE TIDAK DITEMUKAN DI FILE MANAPUN <<<")
            if self.mode_perbandingan:
                self.isi_teks(self.txt_preview_2, ">>> KODE TIDAK DITEMUKAN DI FILE MANAPUN <<<")

    def tampilkan_isi_data(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        key_unik = self.tree.item(selected_item[0], "tags")[0]
        data_packet = self.hasil_pencarian.get(key_unik, {"m1": [], "m2": []})

        if data_packet["m1"]:
            teks = ""
            for i, data in enumerate(data_packet["m1"], 1):
                teks += f"=== MATCH KW1 KE-{i} ===\n" + self.json_cantik(data) + "\n\n"
            self.isi_teks(self.txt_preview_1, teks)
        else:
            self.isi_teks(self.txt_preview_1, "--- Tidak ada match untuk Kata Kunci 1 di file ini ---")

        self.txt_preview_2.delete(1.0, tk.END)
        if self.mode_perbandingan:
            if data_packet["m2"]:
                teks = ""
                for i, data in enumerate(data_packet["m2"], 1):
                    teks += f"=== MATCH KW2 KE-{i} ===\n" + self.json_cantik(data) + "\n\n"
                self.isi_teks(self.txt_preview_2, teks)
            else:
                self.isi_teks(self.txt_preview_2, "--- Tidak ada match untuk Kata Kunci 2 di file ini ---")

    # ==========================================
    # KONTEN TAB 2: VIEWER DATA JSON & FILTER
    # ==========================================
    def create_layout_tab2(self):
        frame_top_t2 = ttk.LabelFrame(self.tab2, text="  Kontrol Penjelajah Folder  ", padding=(15, 12))
        frame_top_t2.pack(side="top", fill="x", pady=(0, 12))

        btn_scan_all = ttk.Button(frame_top_t2, text="📁 Pilih & Scan Folder", style='Accent.TButton',
                                  command=self.pilih_folder_scan)
        btn_scan_all.grid(row=0, column=0, padx=(0, 20), sticky="w")

        ttk.Label(frame_top_t2, text="Cari di Teks Terbuka:", font=FONT_UI_BOLD).grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.ent_filter_internal = ttk.Entry(frame_top_t2, width=35, font=('Segoe UI', 11))
        self.ent_filter_internal.grid(row=0, column=2, padx=(0, 10), sticky="w")
        self.ent_filter_internal.bind("<Return>", lambda e: self.eksekusi_cari_internal_text())

        btn_cari_internal = ttk.Button(frame_top_t2, text="⚡ Cari Kata", command=self.eksekusi_cari_internal_text)
        btn_cari_internal.grid(row=0, column=3, sticky="w")

        # --- Filter nama file ---
        ttk.Label(frame_top_t2, text="Filter Nama File:", font=FONT_UI_BOLD).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.ent_filter_file = ttk.Entry(frame_top_t2, width=35, font=('Segoe UI', 11))
        self.ent_filter_file.grid(row=1, column=1, columnspan=2, sticky="w", pady=(10, 0), padx=(0, 5))

        def eksekusi_filter_file(event):
            keyword = self.ent_filter_file.get().lower().replace('_', '').replace('-', '')
            for i in self.tree_viewer.get_children():
                self.tree_viewer.delete(i)

            hitung = 0
            for key_id, path_file in self.dict_file_viewer.items():
                nama_file = os.path.basename(path_file)
                root_dir = os.path.dirname(path_file)
                parts = root_dir.replace('\\', '/').split('/')
                letak_folder = " / ".join(parts[-3:])

                nama_bersih = nama_file.lower().replace('_', '').replace('-', '')
                if keyword in nama_bersih:
                    zebra = 'odd' if hitung % 2 else 'even'
                    self.tree_viewer.insert("", "end", values=(letak_folder, nama_file), tags=(key_id, zebra))
                    hitung += 1

        self.ent_filter_file.bind("<KeyRelease>", eksekusi_filter_file)

        # --- Filter isi JSON (tampil match) ---
        ttk.Label(frame_top_t2, text="Filter Isi JSON (Tampil Match):", font=FONT_UI_BOLD).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.ent_filter_isi_json = ttk.Entry(frame_top_t2, width=35, font=('Segoe UI', 11))
        self.ent_filter_isi_json.grid(row=2, column=1, columnspan=2, sticky="w", pady=(10, 0), padx=(0, 5))
        self.ent_filter_isi_json.bind("<Return>", lambda e: self.eksekusi_filter_isi_json())

        btn_filter_isi_json = ttk.Button(frame_top_t2, text="⚡ Filter Match", command=self.eksekusi_filter_isi_json)
        btn_filter_isi_json.grid(row=2, column=3, sticky="w", pady=(10, 0))

        # --- Filter pengecualian ---
        ttk.Label(frame_top_t2, text="Filter Pengecualian (Tampil Selain Match):", font=FONT_UI_BOLD).grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.ent_filter_kecuali_json = ttk.Entry(frame_top_t2, width=35, font=('Segoe UI', 11))
        self.ent_filter_kecuali_json.grid(row=3, column=1, columnspan=2, sticky="w", pady=(10, 0), padx=(0, 5))
        self.ent_filter_kecuali_json.bind("<Return>", lambda e: self.eksekusi_filter_kecuali_json())

        btn_filter_kecuali_json = ttk.Button(frame_top_t2, text="⛔ Filter Kecuali", style='Danger.TButton',
                                             command=self.eksekusi_filter_kecuali_json)
        btn_filter_kecuali_json.grid(row=3, column=3, sticky="w", pady=(10, 0))

        # --- Split utama ---
        paned_t2 = ttk.PanedWindow(self.tab2, orient=tk.HORIZONTAL)
        paned_t2.pack(fill="both", expand=True)

        frame_kiri_t2 = ttk.LabelFrame(paned_t2, text="  Daftar Semua File JSON  ", padding=6)
        paned_t2.add(frame_kiri_t2, weight=1)

        self.tree_viewer = ttk.Treeview(frame_kiri_t2, columns=("tahun", "file"), show="headings", selectmode="browse")
        self.tree_viewer.heading("tahun", text="Tahun")
        self.tree_viewer.heading("file", text="Nama File")
        self.tree_viewer.column("tahun", width=60, anchor="center")
        self.tree_viewer.column("file", width=250, anchor="w")

        scroll_tree_t2 = ttk.Scrollbar(frame_kiri_t2, orient="vertical", command=self.tree_viewer.yview)
        self.tree_viewer.configure(yscroll=scroll_tree_t2.set)
        self.tree_viewer.pack(side="left", fill="both", expand=True)
        scroll_tree_t2.pack(side="right", fill="y")
        self.tree_viewer.bind("<<TreeviewSelect>>", self.baca_dan_tampilkan_file_viewer)

        frame_kanan_t2 = ttk.LabelFrame(paned_t2, text="  Isi Konten File (Urut A-Z)  ", padding=6)
        paned_t2.add(frame_kanan_t2, weight=3)

        self.txt_viewer = self.buat_text(frame_kanan_t2)
        scroll_y_t2 = ttk.Scrollbar(frame_kanan_t2, orient="vertical", command=self.txt_viewer.yview)
        scroll_x_t2 = ttk.Scrollbar(frame_kanan_t2, orient="horizontal", command=self.txt_viewer.xview)
        self.txt_viewer.configure(yscrollcommand=scroll_y_t2.set, xscrollcommand=scroll_x_t2.set)

        scroll_x_t2.pack(side="bottom", fill="x")
        self.txt_viewer.pack(side="left", fill="both", expand=True)
        scroll_y_t2.pack(side="right", fill="y")

    # ==========================================
    # LOGIKA PROSES TAB 2
    # ==========================================
    def pilih_folder_scan(self):
        w = self.warna
        top = tk.Toplevel(self)
        top.title("Pilih Folder Scan")
        top.geometry("420x480")
        top.configure(bg=w['bg'])
        top.transient(self)
        top.grab_set()

        ttk.Label(top, text="Centang folder yang ingin di-scan:", font=FONT_UI_BOLD).pack(pady=(14, 8))

        frame_canvas = ttk.Frame(top)
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=5)

        canvas = tk.Canvas(frame_canvas, highlightthickness=0, bg=w['bg'])
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        folder_tersedia = []
        if os.path.exists(BASE_DIR):
            for d in os.listdir(BASE_DIR):
                path_d = os.path.join(BASE_DIR, d)
                if os.path.isdir(path_d) and not d.startswith('.'):
                    folder_tersedia.append((f"📁 {d}", path_d))

        folder_tersedia.sort(key=lambda x: x[0].lower())

        self.checkbox_vars = {}
        for nama_tampil, path_asli in folder_tersedia:
            var = tk.BooleanVar(value=False)
            self.checkbox_vars[path_asli] = var
            cb = ttk.Checkbutton(scrollable_frame, text=nama_tampil, variable=var)
            cb.pack(anchor="w", padx=5, pady=4)

        def mulai_scan():
            path_terpilih = [path for path, var in self.checkbox_vars.items() if var.get()]
            if not path_terpilih:
                messagebox.showwarning("Peringatan", "Centang minimal 1 folder!", parent=top)
                return
            top.destroy()
            self.eksekusi_scan_folder(path_terpilih)

        frame_btn = ttk.Frame(top)
        frame_btn.pack(pady=15)

        def centang_semua():
            for var in self.checkbox_vars.values():
                var.set(True)

        ttk.Button(frame_btn, text="Centang Semua", command=centang_semua).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Mulai Scan Terpilih", style='Accent.TButton', command=mulai_scan).pack(side="left", padx=5)

    def eksekusi_scan_folder(self, list_folder):
        for i in self.tree_viewer.get_children():
            self.tree_viewer.delete(i)
        self.dict_file_viewer.clear()
        self.txt_viewer.delete(1.0, tk.END)

        self.tree_viewer.heading("tahun", text="Letak Folder")
        self.tree_viewer.column("tahun", width=180, anchor="w")

        temp_list = []
        for target_dir in list_folder:
            if not os.path.exists(target_dir):
                continue

            for root, dirs, files in os.walk(target_dir):
                parts = root.replace('\\', '/').split('/')
                letak_folder = " / ".join(parts[-3:])

                for file in files:
                    if file.endswith(".json"):
                        full_path = os.path.join(root, file)
                        temp_list.append((letak_folder, file, full_path))

        temp_list.sort(key=lambda x: (x[0].lower(), x[1].lower()))

        for counter, (letak, file, full_path) in enumerate(temp_list, 1):
            key_id = f"v_file_{counter}"
            self.dict_file_viewer[key_id] = full_path
            zebra = 'odd' if counter % 2 == 0 else 'even'
            self.tree_viewer.insert("", "end", values=(letak, file), tags=(key_id, zebra))

        messagebox.showinfo("Scan Selesai", f"Berhasil memuat {len(temp_list)} file JSON dari folder terpilih.")

    def baca_dan_tampilkan_file_viewer(self, event):
        selected = self.tree_viewer.selection()
        if not selected:
            return

        key_id = self.tree_viewer.item(selected[0], "tags")[0]
        full_path = self.dict_file_viewer.get(key_id)

        self.txt_viewer.delete(1.0, tk.END)
        self.ent_filter_internal.delete(0, tk.END)

        if not full_path or not os.path.exists(full_path):
            self.isi_teks(self.txt_viewer, "❌ Gagal memuat file, path tidak valid.")
            return

        try:
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                raw_data = json.load(f)
            self.isi_teks(self.txt_viewer, self.json_cantik(raw_data))
        except Exception as err:
            self.isi_teks(self.txt_viewer, f"❌ Terjadi kesalahan membaca JSON:\n{str(err)}")

    @staticmethod
    def ambil_items(raw_data):
        if isinstance(raw_data, dict):
            if 'data' in raw_data and isinstance(raw_data['data'], list):
                return raw_data['data']
            return [raw_data]
        if isinstance(raw_data, list):
            return raw_data
        return []

    def eksekusi_filter_isi_json(self):
        selected = self.tree_viewer.selection()
        if not selected:
            return messagebox.showwarning("Peringatan", "Pilih file JSON terlebih dahulu!")

        keyword = self.ent_filter_isi_json.get().strip().lower()
        keyword_padat = keyword.replace(" ", "")

        full_path = self.dict_file_viewer.get(self.tree_viewer.item(selected[0], "tags")[0])
        self.txt_viewer.delete(1.0, tk.END)
        if not full_path or not os.path.exists(full_path):
            return

        try:
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                raw_data = json.load(f)
            if not keyword:
                self.isi_teks(self.txt_viewer, self.json_cantik(raw_data))
                return

            filtered = []
            for item in self.ambil_items(raw_data):
                item_str_padat = json.dumps(item, ensure_ascii=False).lower().replace(" ", "")
                if keyword_padat in item_str_padat:
                    filtered.append(item)

            if filtered:
                teks = self.json_cantik(filtered)
                teks += f"\n\n=== Berhasil memfilter {len(filtered)} data (Match '{keyword}') ==="
                self.isi_teks(self.txt_viewer, teks)
            else:
                self.isi_teks(self.txt_viewer, "❌ Tidak ditemukan data.")
        except Exception as err:
            self.isi_teks(self.txt_viewer, f"❌ Error:\n{str(err)}")

    def eksekusi_filter_kecuali_json(self):
        selected = self.tree_viewer.selection()
        if not selected:
            return messagebox.showwarning("Peringatan", "Pilih file JSON terlebih dahulu!")

        keyword = self.ent_filter_kecuali_json.get().strip().lower()
        keyword_padat = keyword.replace(" ", "")

        full_path = self.dict_file_viewer.get(self.tree_viewer.item(selected[0], "tags")[0])
        self.txt_viewer.delete(1.0, tk.END)
        if not full_path or not os.path.exists(full_path):
            return

        try:
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                raw_data = json.load(f)
            if not keyword:
                self.isi_teks(self.txt_viewer, self.json_cantik(raw_data))
                return

            filtered = []
            for item in self.ambil_items(raw_data):
                item_str_padat = json.dumps(item, ensure_ascii=False).lower().replace(" ", "")
                if keyword_padat not in item_str_padat:
                    filtered.append(item)

            if filtered:
                teks = self.json_cantik(filtered)
                teks += f"\n\n=== Berhasil menampilkan {len(filtered)} data (Mengecualikan '{keyword}') ==="
                self.isi_teks(self.txt_viewer, teks)
            else:
                self.isi_teks(self.txt_viewer, "❌ Semua data mengandung kata tersebut (Tidak ada yang tersisa).")
        except Exception as err:
            self.isi_teks(self.txt_viewer, f"❌ Error:\n{str(err)}")

    def eksekusi_cari_internal_text(self):
        self.txt_viewer.tag_remove('highlight_search', '1.0', tk.END)

        keyword = self.ent_filter_internal.get().strip()
        if not keyword:
            return

        posisi_index = '1.0'
        jumlah_cocok = 0

        while True:
            posisi_index = self.txt_viewer.search(keyword, posisi_index, nocase=True, stopindex=tk.END)
            if not posisi_index:
                break

            jumlah_cocok += 1
            akhir_posisi = f"{posisi_index}+{len(keyword)}c"
            self.txt_viewer.tag_add('highlight_search', posisi_index, akhir_posisi)

            if jumlah_cocok == 1:
                self.txt_viewer.see(posisi_index)

            posisi_index = akhir_posisi

        if jumlah_cocok == 0:
            messagebox.showinfo("Pencarian", f"Kata '{keyword}' tidak ditemukan pada teks JSON ini.")

    def kunci_teks(self, event):
        # Izinkan Ctrl+C (copy) dan tombol navigasi, selain itu dikunci
        if (event.state & 4 and event.keysym.lower() == 'c') or event.keysym in ('Up', 'Down', 'Left', 'Right', 'Prior', 'Next'):
            return None
        return "break"

    def cari_internal_semua(self):
        keyword = self.ent_cari_internal_t1.get().strip()
        for txt in [self.txt_preview_1, self.txt_preview_2]:
            txt.tag_remove('highlight_search', '1.0', tk.END)
            if not keyword:
                continue

            pos = '1.0'
            while True:
                pos = txt.search(keyword, pos, nocase=True, stopindex=tk.END)
                if not pos:
                    break
                akhir = f"{pos}+{len(keyword)}c"
                txt.tag_add('highlight_search', pos, akhir)
                txt.see(pos)
                pos = akhir


if __name__ == "__main__":
    app = AppPelacakJSON()
    app.mainloop()