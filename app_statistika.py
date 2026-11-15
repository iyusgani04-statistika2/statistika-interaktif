import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math
import random
import os
import json
import base64
from datetime import datetime

# ============================================================
# 1. PENGATURAN IDENTITAS PORTAL, PIN GURU & KURIKULUM KELAS
# ============================================================
PIN_GURU            = "1977"  # PIN Khusus Guru untuk menu Buat Soal Guru
NAMA_APLIKASI       = "Media Pembelajaran Matematika"
NAMA_GURU_SEKOLAH   = "Iyus Ruslan, ST., S.Pd"      # Contoh: "Oleh: Iyus Gani, S.Pd."
KELAS_AWAL_INDEX    = 2       # 0 = Kelas 10, 1 = Kelas 11, 2 = Kelas 12

LINK_PENGUMPULAN    = "https://forms.gle/Sr3tFKnaZnJ6Tsvf9"      # Isi link Google Form jika ada pengumpulan tugas/quiz
LINK_VIDEO_YOUTUBE  = "https://www.youtube.com/watch?v=XQ8UJAMJcUQ&t=82s"      # Isi link YouTube jika ada video pembelajaran

KURIKULUM_KELAS = {
    "Kelas 10": [
        ("eksponen",     "🔢 Bab 1: Eksponen & Logaritma"),
        ("barisan",      "📈 Bab 2: Barisan & Deret"),
        ("trigonometri", "📐 Bab 3: Trigonometri"),
        ("statistika",   "📊 Bab 4: Statistika (Data Kelompok)"),
        ("peluang",      "🎲 Bab 5: Peluang Kejadian"),
    ],
    "Kelas 11": [
        ("matriks",      "🧮 Bab 1: Matriks & Determinan"),
        ("transformasi", "🔄 Bab 2: Transformasi Geometri"),
        ("geometri",     "📐 Bab 3: Geometri (Bangun Ruang)"),
        ("statistika",   "📊 Bab 4: Statistika (Data Kelompok)"),
    ],
    "Kelas 12": [
        ("statistika",   "📊 Bab 1: Statistika (Data Kelompok)"),
        ("geometri",     "📐 Bab 2: Geometri (Bangun Ruang / Dimensi Tiga)"),
        ("peluang",      "🎲 Bab 3: Peluang & Kaidah Pencacahan"),
        ("turunan",      "📉 Bab 4: Limit & Turunan Fungsi"),
    ],
}

KATA_KUNCI_FILE_BAB = {
    "statistika":   ["statistika", "statistik", "data kelompok", "pemusatan", "mean", "modus", "median"],
    "geometri":     ["geometri", "bangun ruang", "dimensi tiga", "dimensi 3", "kubus", "balok"],
    "peluang":      ["peluang", "pencacahan", "permutasi", "kombinasi", "dadu", "koin"],
    "eksponen":     ["eksponen", "logaritma", "bentuk pangkat"],
    "barisan":      ["barisan", "deret", "aritmetika", "aritmatika"],
    "trigonometri": ["trigonometri", "sinus", "cosinus", "tangen", "sudut"],
    "matriks":      ["matriks", "determinan"],
    "transformasi": ["transformasi", "translasi", "refleksi", "rotasi", "dilatasi"],
    "turunan":      ["limit", "turunan", "diferensial"],
}

# ============================================================
# 2. KONFIGURASI HALAMAN & SESSION STATE
# ============================================================
st.set_page_config(
    page_title=NAMA_APLIKASI,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "quiz_submitted_key" not in st.session_state:
    st.session_state.quiz_submitted_key = ""
if "guru_unlocked" not in st.session_state:
    st.session_state.guru_unlocked = False
if "draft_bank" not in st.session_state:
    st.session_state.draft_bank = {}

# ============================================================
# 3. CSS TAMPILAN (TERANG & GELAP)
# ============================================================
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #1a1a2e; color: #e0e0e0; }
        .main-header {
            background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
            padding: 1.8rem; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 1.5rem;
        }
        .main-header h1, .main-header p { color: white; margin: 0.3rem 0; }
        .badge-aktif {
            display: inline-block; background: rgba(255,255,255,0.2);
            padding: 5px 14px; border-radius: 20px; font-size: 0.9rem;
            margin-bottom: 8px; color: #ffffff; font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 1.4rem; border-radius: 12px; text-align: center;
            border-left: 5px solid #e94560; color: #e0e0e0; margin-bottom: 1rem;
        }
        .metric-card h3 { color: #e0e0e0; margin-top: 0; }
        .metric-card .value { font-size: 1.9rem; font-weight: bold; color: #e94560; }
        .formula-box {
            background: #0d1117; color: #7ee787; padding: 1.1rem;
            border-radius: 10px; font-family: 'Courier New', monospace;
            font-size: 1.05rem; border: 1px solid #30363d; margin: 0.6rem 0;
        }
        .step-box {
            background: #16213e; border-left: 4px solid #e94560;
            padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; color: #e0e0e0;
        }
        .materi-box, .quiz-box {
            background: #16213e; padding: 1.4rem; border-radius: 12px;
            border: 1px solid #30363d; margin: 0.8rem 0; color: #e0e0e0;
        }
        .quiz-benar { background: #1a3a1a; border: 2px solid #4caf50; padding: 1rem; border-radius: 8px; color: #81c784; margin-top: 0.5rem; }
        .quiz-salah { background: #3a1a1a; border: 2px solid #f44336; padding: 1rem; border-radius: 8px; color: #e57373; margin-top: 0.5rem; }
        .quiz-info  { background: #1e293b; border: 2px solid #38bdf8; padding: 1rem; border-radius: 8px; color: #7dd3fc; margin-top: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            padding: 1.8rem; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 1.5rem;
        }
        .main-header h1, .main-header p { color: white; margin: 0.3rem 0; }
        .badge-aktif {
            display: inline-block; background: rgba(255,255,255,0.22);
            padding: 5px 14px; border-radius: 20px; font-size: 0.9rem;
            margin-bottom: 8px; color: #ffffff; font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1.4rem; border-radius: 12px; text-align: center;
            border-left: 5px solid #4f46e5; margin-bottom: 1rem;
        }
        .metric-card h3 { color: #1e293b; margin-top: 0; }
        .metric-card .value { font-size: 1.9rem; font-weight: bold; color: #4f46e5; }
        .formula-box {
            background: #1e1e2e; color: #a6e3a1; padding: 1.1rem;
            border-radius: 10px; font-family: 'Courier New', monospace;
            font-size: 1.05rem; border: 1px solid #45475a; margin: 0.6rem 0;
        }
        .step-box {
            background: #eef2ff; border-left: 4px solid #4f46e5;
            padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
        }
        .materi-box {
            background: #f8faff; padding: 1.4rem; border-radius: 12px;
            border: 1px solid #e0e7ff; margin: 0.8rem 0;
        }
        .quiz-box {
            background: #fffbeb; padding: 1.4rem; border-radius: 12px;
            border: 1px solid #fde68a; margin: 0.8rem 0;
        }
        .quiz-benar { background: #e8f5e9; border: 2px solid #4caf50; padding: 1rem; border-radius: 8px; color: #2e7d32; margin-top: 0.5rem; }
        .quiz-salah { background: #ffebee; border: 2px solid #f44336; padding: 1rem; border-radius: 8px; color: #c62828; margin-top: 0.5rem; }
        .quiz-info  { background: #eff6ff; border: 2px solid #3b82f6; padding: 1rem; border-radius: 8px; color: #1d4ed8; margin-top: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 4. FUNGSI DETEKSI FILE MATERI, LKPD, SOAL QUIZ & PDF CANVAS
# ============================================================
def adalah_file_lkpd(nama_file):
    kata_lkpd = ["lkpd", "lembar kerja", "lembar_kerja", "lks", "worksheet"]
    return any(k in nama_file.lower() for k in kata_lkpd)

def file_cocok_dengan_bab(nama_file, id_bab, nama_kelas):
    nama_kecil = nama_file.lower().replace("_", " ").replace("-", " ")
    angka_kelas = nama_kelas.split()[-1]
    for kls in ["10", "11", "12"]:
        if f"kelas {kls}" in nama_kecil or f"kls {kls}" in nama_kecil or f"kelas{kls}" in nama_kecil:
            if kls != angka_kelas:
                return False

    kata_bab_ini = KATA_KUNCI_FILE_BAB.get(id_bab, [])
    if any(k in nama_kecil for k in kata_bab_ini):
        return True

    for bab_lain, daftar_kata in KATA_KUNCI_FILE_BAB.items():
        if bab_lain != id_bab and any(k in nama_kecil for k in daftar_kata):
            return False

    return None

def tampilkan_pratinjau_pdf(isi_bytes):
    base64_pdf = base64.b64encode(isi_bytes).decode("utf-8")
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 15px; background-color: #525659; font-family: Arial, sans-serif; text-align: center; }}
            #loading-msg {{ color: #ffffff; font-size: 14px; padding: 20px; }}
            .page-label {{ color: #f0f0f0; font-size: 13px; margin: 8px 0 6px 0; }}
            canvas {{
                display: block; margin: 0 auto 20px auto; max-width: 100%; height: auto !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.45); border-radius: 6px; background-color: #ffffff;
            }}
        </style>
    </head>
    <body>
        <div id="loading-msg">⏳ Memuat pratinjau dokumen...</div>
        <div id="pdf-container"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <script>
            const pdfjsLib = window['pdfjs-dist/build/pdf'];
            try {{
                const blob = new Blob(["importScripts('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js');"], {{ type: 'application/javascript' }});
                pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(blob);
            }} catch (e) {{
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            }}
            const raw = atob("{base64_pdf}");
            const uint8Array = new Uint8Array(raw.length);
            for (let i = 0; i < raw.length; i++) {{
                uint8Array[i] = raw.charCodeAt(i);
            }}
            async function renderPDF() {{
                try {{
                    const pdf = await pdfjsLib.getDocument({{ data: uint8Array }}).promise;
                    const container = document.getElementById('pdf-container');
                    const loadingMsg = document.getElementById('loading-msg');
                    loadingMsg.innerText = '⏳ Menampilkan ' + pdf.numPages + ' halaman...';
                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                        const page = await pdf.getPage(pageNum);
                        const viewport = page.getViewport({{ scale: 1.55 }});
                        const label = document.createElement('div');
                        label.className = 'page-label';
                        label.innerText = 'Halaman ' + pageNum + ' dari ' + pdf.numPages;
                        container.appendChild(label);
                        const canvas = document.createElement('canvas');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        container.appendChild(canvas);
                        await page.render({{ canvasContext: canvas.getContext('2d'), viewport: viewport }}).promise;
                    }}
                    loadingMsg.style.display = 'none';
                }} catch (err) {{
                    document.getElementById('loading-msg').innerText = '⚠️ Gagal memuat pratinjau. Silakan klik tombol Download di atas.';
                }}
            }}
            renderPDF();
        </script>
    </body>
    </html>
    """
    components.html(pdf_html, height=640, scrolling=True)

# ============================================================
# 5. BANK KONTEN MATERI & SOAL BAWAAN SELURUH BAB
# ============================================================
DATA_BAB = {
    "statistika": {
        "nama": "Statistika (Data Kelompok)",
        "deskripsi": "Ukuran Pemusatan Data Kelompok: Tabel Distribusi Frekuensi, Rata-rata (Mean), Modus, dan Median.",
        "materi": [
            ("📌 Pengantar & Sturges", """
            <div class="materi-box">
            <b>Data Kelompok</b> adalah data statistik yang dikelompokkan ke dalam kelas-kelas interval dengan panjang kelas yang sama.<br><br>
            <b>Rumus Aturan Sturges (Menentukan Banyak Kelas):</b>
            </div>
            <div class="formula-box">k = 1 + 3,322 × log(n)  |  Jangkauan (R) = Xmax - Xmin  |  Panjang Kelas (p) = R / k</div>
            <div class="materi-box">
            • <b>Titik Tengah (xi)</b> = ½ × (Batas Bawah + Batas Atas)<br>
            • <b>Tepi Bawah (Tb)</b> = Batas Bawah − 0,5 &nbsp;|&nbsp; <b>Tepi Atas (Ta)</b> = Batas Atas + 0,5
            </div>
            """),
            ("📈 Rata-rata (Mean)", """
            <div class="formula-box">x̄ = Σ(fi × xi) / Σfi</div>
            <div class="materi-box">
            <b>Langkah menghitung Mean Data Kelompok:</b><br>
            1. Tentukan titik tengah (<b>xi</b>) masing-masing kelas interval.<br>
            2. Kalikan frekuensi kelas dengan titik tengahnya (<b>fi × xi</b>).<br>
            3. Jumlahkan seluruh hasil kali tersebut, lalu bagi dengan jumlah total frekuensi (<b>Σfi</b>).
            </div>
            """),
            ("🏔️ Modus & 📏 Median", """
            <div class="formula-box">Modus (Mo) = Tb + p × [ d1 / (d1 + d2) ]</div>
            <div class="materi-box">
            • <b>Kelas Modus</b> = Kelas dengan frekuensi (fi) paling besar.<br>
            • <b>d1</b> = Selisih fi kelas modus dengan kelas sebelumnya &nbsp;|&nbsp; <b>d2</b> = Selisih fi dengan kelas sesudahnya.
            </div>
            <div class="formula-box">Median (Me) = Tb + p × [ (½n − Fk) / fi ]</div>
            <div class="materi-box">
            • <b>Kelas Median</b> = Kelas pertama yang Frekuensi Kumulatifnya (Fk) ≥ ½n.<br>
            • <b>Fk</b> = Frekuensi kumulatif sebelum kelas median &nbsp;|&nbsp; <b>fi</b> = Frekuensi kelas median.
            </div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Rumus rata-rata (mean) data kelompok adalah...", "pilihan": ["x̄ = Σfi / Σxi", "x̄ = Σ(fi × xi) / Σfi", "x̄ = Σfi × Σxi", "x̄ = Σxi / n"], "jawaban": 1, "penjelasan": "Mean data kelompok = Σ(fi × xi) dibagi total frekuensi Σfi."},
            {"tipe": "pg", "bobot": 20, "soal": "Tepi bawah (Tb) dari kelas interval 50 - 59 adalah...", "pilihan": ["49", "49,5", "50", "50,5"], "jawaban": 1, "penjelasan": "Tb = Batas bawah - 0,5 = 50 - 0,5 = 49,5."},
            {"tipe": "pg", "bobot": 20, "soal": "Titik tengah (xi) dari kelas interval 60 - 69 adalah...", "pilihan": ["64", "64,5", "65", "65,5"], "jawaban": 1, "penjelasan": "xi = (60 + 69) / 2 = 64,5."},
            {"tipe": "pernyataan", "bobot": 20, "soal": "Perhatikan kelas interval 70 - 79 dengan frekuensi 12. Tentukan kebenaran pernyataan berikut:", "label_opsi": ["Benar", "Salah"], "daftar_pernyataan": [{"teks": "Tepi bawah kelas tersebut adalah 69,5", "kunci": "Benar"}, {"teks": "Panjang kelas interval tersebut adalah 9", "kunci": "Salah"}], "penjelasan": "Tb = 70 - 0,5 = 69,5 (Benar). Panjang kelas p = 79,5 - 69,5 = 10, bukan 9 (Salah)."},
            {"tipe": "essay", "bobot": 20, "soal": "Jika jumlah seluruh data (n) adalah 40, maka kelas median terletak pada data urutan ke berapa? (Tuliskan angkanya)", "kata_kunci": ["20", "dua puluh"], "tampilkan_kunci": True, "penjelasan": "Letak median = ½ × n = ½ × 40 = 20."},
        ]
    },
    "geometri": {
        "nama": "Geometri (Bangun Ruang & Dimensi Tiga)",
        "deskripsi": "Unsur Bangun Ruang, Volume, Luas Permukaan, serta Jarak Titik, Garis, dan Bidang pada Dimensi Tiga.",
        "materi": [
            ("🧊 Dimensi Tiga (Kubus)", """
            <div class="materi-box">
            Pada kubus <b>ABCD.EFGH</b> dengan panjang rusuk <b>s</b>:<br>
            • Memiliki <b>6 sisi</b> kongruen, <b>12 rusuk</b> sama panjang, dan <b>8 titik sudut</b>.<br>
            • Memiliki <b>12 diagonal bidang</b> (contoh: AC, BD, BG, AF) dan <b>4 diagonal ruang</b> (AG, BH, CE, DF).
            </div>
            <div class="formula-box">Diagonal Bidang = s√2  |  Diagonal Ruang = s√3</div>
            <div class="materi-box">
            <b>Konsep Jarak pada Dimensi Tiga:</b><br>
            • <b>Jarak titik ke titik:</b> Panjang ruas garis terpendek yang menghubungkan kedua titik (Teorema Pythagoras).<br>
            • <b>Jarak titik ke garis/bidang:</b> Panjang ruas garis proyeksi yang tegak lurus dari titik ke garis/bidang tersebut.
            </div>
            """),
            ("📦 Bangun Ruang Sisi Datar & Lengkung", """
            <div class="formula-box">Kubus: V = s³  |  Lp = 6s²</div>
            <div class="formula-box">Balok: V = p × l × t  |  Lp = 2(pl + pt + lt)</div>
            <div class="formula-box">Tabung: V = πr²t  |  Lp = 2πr(r + t)</div>
            <div class="formula-box">Kerucut: V = ⅓πr²t  |  Bola: V = ⁴⁄₃πr³ , Lp = 4πr²</div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Diketahui kubus ABCD.EFGH dengan panjang rusuk 6 cm. Panjang diagonal bidang AC adalah...", "pilihan": ["6 cm", "6√2 cm", "6√3 cm", "12 cm"], "jawaban": 1, "penjelasan": "Diagonal bidang kubus = s√2 = 6√2 cm."},
            {"tipe": "pg", "bobot": 20, "soal": "Pada kubus ABCD.EFGH dengan rusuk 8 cm, panjang diagonal ruang AG adalah...", "pilihan": ["8 cm", "8√2 cm", "8√3 cm", "16 cm"], "jawaban": 2, "penjelasan": "Diagonal ruang kubus = s√3 = 8√3 cm."},
            {"tipe": "pg", "bobot": 20, "soal": "Banyaknya rusuk dan titik sudut pada kubus berturut-turut adalah...", "pilihan": ["6 dan 8", "8 dan 12", "12 dan 8", "12 dan 6"], "jawaban": 2, "penjelasan": "Kubus memiliki 12 rusuk, 8 titik sudut, dan 6 bidang sisi."},
            {"tipe": "pg", "bobot": 20, "soal": "Sebuah balok berukuran panjang 10 cm, lebar 5 cm, dan tinggi 4 cm. Volumenya adalah...", "pilihan": ["90 cm³", "180 cm³", "200 cm³", "220 cm³"], "jawaban": 2, "penjelasan": "Volume balok = p × l × t = 10 × 5 × 4 = 200 cm³."},
            {"tipe": "pg", "bobot": 20, "soal": "Jarak dari suatu titik ke bidang adalah panjang ruas garis yang...", "pilihan": ["Sejajar bidang", "Miring terhadap bidang", "Tegak lurus dari titik ke bidang", "Memotong rusuk terpanjang"], "jawaban": 2, "penjelasan": "Jarak selalu diukur menggunakan garis proyeksi yang tegak lurus (90°)."},
        ]
    },
    "peluang": {
        "nama": "Peluang & Kaidah Pencacahan",
        "deskripsi": "Aturan Perkalian, Faktorial, Permutasi, Kombinasi, serta Peluang Kejadian Majemuk.",
        "materi": [
            ("🔢 Pencacahan, Permutasi & Kombinasi", """
            <div class="formula-box">Faktorial: n! = n × (n−1) × (n−2) × ... × 1   (dengan 0! = 1)</div>
            <div class="formula-box">Permutasi (Memperhatikan Urutan): P(n, r) = n! / (n − r)!</div>
            <div class="formula-box">Kombinasi (Tanpa Memperhatikan Urutan): C(n, r) = n! / [ r! × (n − r)! ]</div>
            <div class="materi-box">
            • Gunakan <b>Permutasi</b> untuk pemilihan jabatan (Ketua-Sekretaris), susunan angka/PIN, posisi duduk.<br>
            • Gunakan <b>Kombinasi</b> untuk pemilihan tim/delegasi, mengambil bola sekaligus, jabat tangan.
            </div>
            """),
            ("🎲 Peluang & Frekuensi Harapan", """
            <div class="formula-box">P(A) = n(A) / n(S)   dengan   0 ≤ P(A) ≤ 1</div>
            <div class="formula-box">Peluang Komplemen: P(A') = 1 − P(A)  |  Frekuensi Harapan: Fh(A) = P(A) × N</div>
            <div class="materi-box">
            • <b>Ruang Sampel (S):</b> Himpunan semua hasil yang mungkin terjadi pada suatu percobaan.<br>
            • 1 Koin: n(S) = 2 &nbsp;|&nbsp; 1 Dadu: n(S) = 6 &nbsp;|&nbsp; 2 Dadu: n(S) = 36.
            </div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari 5! (5 faktorial) adalah...", "pilihan": ["25", "60", "120", "240"], "jawaban": 2, "penjelasan": "5! = 5 × 4 × 3 × 2 × 1 = 120."},
            {"tipe": "pg", "bobot": 20, "soal": "Banyak cara memilih Ketua dan Wakil Ketua dari 6 kandidat adalah...", "pilihan": ["15 cara", "30 cara", "36 cara", "12 cara"], "jawaban": 1, "penjelasan": "Karena memperhatikan urutan jabatan, gunakan Permutasi: P(6,2) = 6 × 5 = 30 cara."},
            {"tipe": "pg", "bobot": 20, "soal": "Banyak cara memilih 3 siswa untuk mewakili sekolah dari 6 siswa adalah...", "pilihan": ["18 cara", "20 cara", "120 cara", "36 cara"], "jawaban": 1, "penjelasan": "Tanpa urutan: Kombinasi C(6,3) = 6! / (3! × 3!) = 20 cara."},
            {"tipe": "pg", "bobot": 20, "soal": "Sebuah dadu dilempar satu kali. Peluang muncul mata dadu bilangan genap adalah...", "pilihan": ["1/6", "1/3", "1/2", "2/3"], "jawaban": 2, "penjelasan": "Mata dadu genap = {2, 4, 6} ada 3. P(A) = 3/6 = 1/2."},
            {"tipe": "pg", "bobot": 20, "soal": "Jika peluang hari ini hujan adalah 0,35, maka peluang hari ini TIDAK hujan adalah...", "pilihan": ["0,35", "0,55", "0,65", "0,75"], "jawaban": 2, "penjelasan": "P(A') = 1 - 0,35 = 0,65."},
        ]
    },
    "eksponen": {
        "nama": "Eksponen & Logaritma",
        "deskripsi": "Sifat-sifat Bilangan Berpangkat (Eksponen), Fungsi Eksponen, dan Logaritma.",
        "materi": [
            ("⚡ Sifat Eksponen", """
            <div class="formula-box">aᵐ × aⁿ = aᵐ⁺ⁿ  |  aᵐ : aⁿ = aᵐ⁻ⁿ  |  (aᵐ)ⁿ = aᵐˣⁿ  |  a⁰ = 1  |  a⁻ⁿ = 1 / aⁿ</div>
            <div class="materi-box">
            <b>Fungsi Eksponen</b> berbentuk <b>f(x) = aˣ</b> dengan a &gt; 0 dan a ≠ 1.<br>
            • Jika <b>a &gt; 1</b>, grafik monoton naik (pertumbuhan eksponensial).<br>
            • Jika <b>0 &lt; a &lt; 1</b>, grafik monoton turun (peluruhan eksponensial).
            </div>
            """),
            ("🪵 Konsep & Sifat Logaritma", """
            <div class="formula-box">ᵃlog b = c  ⟺  aᶜ = b   (dengan a &gt; 0, a ≠ 1, b &gt; 0)</div>
            <div class="formula-box">ᵃlog(x × y) = ᵃlog x + ᵃlog y  |  ᵃlog(x / y) = ᵃlog x − ᵃlog y  |  ᵃlog(xⁿ) = n · ᵃlog x</div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Bentuk sederhana dari 2³ × 2⁴ adalah...", "pilihan": ["2⁷", "2¹²", "4⁷", "2¹"], "jawaban": 0, "penjelasan": "aᵐ × aⁿ = aᵐ⁺ⁿ → 2³⁺⁴ = 2⁷ = 128."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari 5⁰ + 2⁻¹ adalah...", "pilihan": ["0,5", "1", "1,5", "2,5"], "jawaban": 2, "penjelasan": "5⁰ = 1 dan 2⁻¹ = 0,5. Maka 1 + 0,5 = 1,5."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari ²log 8 adalah...", "pilihan": ["2", "3", "4", "6"], "jawaban": 1, "penjelasan": "Karena 2³ = 8, maka ²log 8 = 3."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari ³log 9 + ³log 3 adalah...", "pilihan": ["2", "3", "4", "6"], "jawaban": 1, "penjelasan": "³log 9 + ³log 3 = 2 + 1 = 3."},
            {"tipe": "pg", "bobot": 20, "soal": "Grafik fungsi f(x) = 2ˣ memotong sumbu-Y di titik...", "pilihan": ["(0, 0)", "(0, 1)", "(1, 0)", "(0, 2)"], "jawaban": 1, "penjelasan": "Saat x = 0, f(0) = 2⁰ = 1. Titik potongnya (0, 1)."},
        ]
    },
    "barisan": {
        "nama": "Barisan & Deret (Aritmetika & Geometri)",
        "deskripsi": "Pola Bilangan, Suku ke-n (Un), dan Jumlah n Suku Pertama (Sn) Aritmetika serta Geometri.",
        "materi": [
            ("➕ Barisan & Deret Aritmetika", """
            <div class="materi-box">Barisan dengan selisih/beda (<b>b = U₂ − U₁</b>) antar suku berurutan yang selalu tetap.</div>
            <div class="formula-box">Suku ke-n: Un = a + (n − 1)b</div>
            <div class="formula-box">Jumlah n suku: Sn = ½n × [ 2a + (n − 1)b ] = ½n × (a + Un)</div>
            """),
            ("✖️ Barisan & Deret Geometri", """
            <div class="materi-box">Barisan dengan rasio/pembanding (<b>r = U₂ / U₁</b>) antar suku berurutan yang selalu tetap.</div>
            <div class="formula-box">Suku ke-n: Un = a × rⁿ⁻¹</div>
            <div class="formula-box">Jumlah n suku: Sn = a(rⁿ − 1) / (r − 1)   |   Deret Tak Hingga (|r| &lt; 1): S∞ = a / (1 − r)</div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Diketahui barisan aritmetika: 3, 7, 11, 15, ... Suku ke-10 adalah...", "pilihan": ["35", "39", "43", "47"], "jawaban": 1, "penjelasan": "a = 3, b = 4. U10 = 3 + 9(4) = 3 + 36 = 39."},
            {"tipe": "pg", "bobot": 20, "soal": "Jumlah 10 suku pertama dari deret aritmetika 2 + 4 + 6 + 8 + ... adalah...", "pilihan": ["90", "100", "110", "120"], "jawaban": 2, "penjelasan": "a = 2, U10 = 20. S10 = ½(10)(2 + 20) = 5 × 22 = 110."},
            {"tipe": "pg", "bobot": 20, "soal": "Rasio dari barisan geometri 2, 6, 18, 54, ... adalah...", "pilihan": ["2", "3", "4", "6"], "jawaban": 1, "penjelasan": "r = 6 / 2 = 3."},
            {"tipe": "pg", "bobot": 20, "soal": "Suku ke-5 dari barisan geometri dengan suku pertama 2 dan rasio 2 adalah...", "pilihan": ["16", "32", "64", "10"], "jawaban": 1, "penjelasan": "U5 = a × r⁴ = 2 × 2⁴ = 32."},
            {"tipe": "pg", "bobot": 20, "soal": "Jumlah deret geometri tak hingga 8 + 4 + 2 + 1 + ... adalah...", "pilihan": ["12", "15", "16", "20"], "jawaban": 2, "penjelasan": "a = 8, r = ½. S∞ = 8 / (1 - ½) = 16."},
        ]
    },
    "trigonometri": {
        "nama": "Trigonometri",
        "deskripsi": "Perbandingan Trigonometri Segitiga Siku-siku, Sudut Istimewa, dan Grafik Fungsi Trigonometri.",
        "materi": [
            ("📐 Perbandingan Segitiga Siku-siku", """
            <div class="formula-box">sin θ = Depan / Miring (DeMi)  |  cos θ = Samping / Miring (SaMi)  |  tan θ = Depan / Samping (DeSa)</div>
            <div class="materi-box">
            <b>Identitas Dasar & Konversi Sudut:</b><br>
            • sin²θ + cos²θ = 1 &nbsp;|&nbsp; tan θ = sin θ / cos θ<br>
            • π radian = 180° &nbsp;⟹&nbsp; 1 radian ≈ 57,3°
            </div>
            """),
            ("🌟 Sudut Istimewa Kuadran I", """
            <div class="materi-box">
            <b>Nilai Perbandingan Sudut Istimewa (0° sampai 90°):</b><br><br>
            • <b>sin θ :</b> 0° = 0 &nbsp;|&nbsp; 30° = ½ &nbsp;|&nbsp; 45° = ½√2 &nbsp;|&nbsp; 60° = ½√3 &nbsp;|&nbsp; 90° = 1<br>
            • <b>cos θ :</b> 0° = 1 &nbsp;|&nbsp; 30° = ½√3 &nbsp;|&nbsp; 45° = ½√2 &nbsp;|&nbsp; 60° = ½ &nbsp;|&nbsp; 90° = 0<br>
            • <b>tan θ :</b> 0° = 0 &nbsp;|&nbsp; 30° = ⅓√3 &nbsp;|&nbsp; 45° = 1 &nbsp;|&nbsp; 60° = √3 &nbsp;|&nbsp; 90° = Tak Terdefinisi
            </div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Pada segitiga siku-siku, jika sisi depan sudut θ = 3 dan sisi miring = 5, maka nilai sin θ adalah...", "pilihan": ["3/4", "4/5", "3/5", "5/3"], "jawaban": 2, "penjelasan": "sin θ = Depan / Miring = 3/5."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari sin 30° + cos 60° adalah...", "pilihan": ["0", "½", "1", "√3"], "jawaban": 2, "penjelasan": "sin 30° = ½ dan cos 60° = ½. Maka ½ + ½ = 1."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari tan 45° adalah...", "pilihan": ["0", "½√2", "1", "√3"], "jawaban": 2, "penjelasan": "Sudut istimewa tan 45° = 1."},
            {"tipe": "pg", "bobot": 20, "soal": "Sudut 90° jika dinyatakan dalam satuan radian sama dengan...", "pilihan": ["¼ π rad", "½ π rad", "π rad", "2π rad"], "jawaban": 1, "penjelasan": "90° / 180° × π = ½ π radian."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai maksimum dari fungsi f(x) = 3 sin(x) adalah...", "pilihan": ["1", "2", "3", "6"], "jawaban": 2, "penjelasan": "Amplitudo A = 3, sehingga nilai maksimumnya adalah 3."},
        ]
    },
    "matriks": {
        "nama": "Matriks & Determinan",
        "deskripsi": "Konsep Matriks, Operasi Aljabar Matriks, Determinan, dan Invers Matriks Ordo 2×2.",
        "materi": [
            ("🧮 Operasi Matriks & Determinan", """
            <div class="materi-box">
            • <b>Penjumlahan/Pengurangan:</b> Menjumlahkan elemen-elemen yang seletak (ordo matriks harus sama).<br>
            • <b>Perkalian Matriks A × B:</b> Mengalikan elemen baris matriks A dengan elemen kolom matriks B.
            </div>
            <div class="formula-box">Jika A = [[a, b], [c, d]], maka Determinan det(A) = |A| = (a × d) − (b × c)</div>
            <div class="formula-box">Invers A⁻¹ = (1 / det(A)) × [[d, −b], [−c, a]]   (syarat: det(A) ≠ 0)</div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Determinan dari matriks A = [[5, 2], [3, 4]] adalah...", "pilihan": ["14", "26", "-14", "10"], "jawaban": 0, "penjelasan": "det(A) = (5 × 4) - (2 × 3) = 20 - 6 = 14."},
            {"tipe": "pg", "bobot": 20, "soal": "Matriks yang nilai determinannya sama dengan nol disebut matriks...", "pilihan": ["Identitas", "Singular", "Simetris", "Diagonal"], "jawaban": 1, "penjelasan": "Matriks singular memiliki det = 0 dan tidak memiliki invers."},
            {"tipe": "pg", "bobot": 20, "soal": "Jika matriks A berordo 2×3 dan B berordo 3×4, maka ordo matriks A × B adalah...", "pilihan": ["2×3", "3×3", "2×4", "3×4"], "jawaban": 2, "penjelasan": "Ordo hasil kali: (2×3) × (3×4) = 2×4."},
            {"tipe": "pg", "bobot": 20, "soal": "Hasil penjumlahan elemen baris 1 kolom 1 dari [[2, 1], [0, 3]] + [[4, -1], [5, 2]] adalah...", "pilihan": ["0", "5", "6", "8"], "jawaban": 2, "penjelasan": "Elemen (1,1) = 2 + 4 = 6."},
            {"tipe": "pg", "bobot": 20, "soal": "Matriks identitas I berordo 2×2 adalah...", "pilihan": ["[[1, 1], [1, 1]]", "[[1, 0], [0, 1]]", "[[0, 1], [1, 0]]", "[[1, 0], [1, 0]]"], "jawaban": 1, "penjelasan": "Matriks identitas memiliki diagonal utama 1 dan elemen lainnya 0."},
        ]
    },
    "transformasi": {
        "nama": "Transformasi Geometri",
        "deskripsi": "Pergeseran (Translasi), Pencerminan (Refleksi), Perputaran (Rotasi), dan Perkalian (Dilatasi).",
        "materi": [
            ("🔄 Rumus Bayangan Titik P(x, y)", """
            <div class="formula-box">Translasi T(a, b)  ⟹  P'(x + a, y + b)</div>
            <div class="formula-box">Refleksi Sumbu-X ⟹ P'(x, −y)  |  Sumbu-Y ⟹ P'(−x, y)  |  Garis y = x ⟹ P'(y, x)</div>
            <div class="formula-box">Rotasi Pusat O(0,0): +90° ⟹ P'(−y, x)  |  −90° ⟹ P'(y, −x)  |  180° ⟹ P'(−x, −y)</div>
            <div class="formula-box">Dilatasi [O, k]  ⟹  P'(k·x, k·y)</div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Bayangan titik P(3, -2) oleh translasi T(4, 5) adalah...", "pilihan": ["P'(7, 3)", "P'(7, -7)", "P'(-1, 3)", "P'(12, -10)"], "jawaban": 0, "penjelasan": "P'(3+4, -2+5) = P'(7, 3)."},
            {"tipe": "pg", "bobot": 20, "soal": "Bayangan titik A(4, 6) jika dicerminkan terhadap sumbu-X adalah...", "pilihan": ["A'(-4, 6)", "A'(4, -6)", "A'(-4, -6)", "A'(6, 4)"], "jawaban": 1, "penjelasan": "Refleksi sumbu-X mengubah tanda koordinat y: A'(4, -6)."},
            {"tipe": "pg", "bobot": 20, "soal": "Bayangan titik B(2, 5) jika dicerminkan terhadap garis y = x adalah...", "pilihan": ["B'(-2, -5)", "B'(5, 2)", "B'(-5, -2)", "B'(2, -5)"], "jawaban": 1, "penjelasan": "Refleksi terhadap garis y = x menukar posisi x dan y: B'(5, 2)."},
            {"tipe": "pg", "bobot": 20, "soal": "Bayangan titik C(3, -4) oleh dilatasi [O, 2] adalah...", "pilihan": ["C'(5, -2)", "C'(6, -8)", "C'(6, -4)", "C'(1.5, -2)"], "jawaban": 1, "penjelasan": "Dilatasi [O, 2]: C'(2×3, 2×(-4)) = C'(6, -8)."},
            {"tipe": "pg", "bobot": 20, "soal": "Bayangan titik D(4, 1) oleh rotasi 180° dengan pusat O(0,0) adalah...", "pilihan": ["D'(-1, 4)", "D'(1, -4)", "D'(-4, -1)", "D'(4, -1)"], "jawaban": 2, "penjelasan": "Rotasi 180° terhadap O(0,0) menghasilkan (-x, -y) = (-4, -1)."},
        ]
    },
    "turunan": {
        "nama": "Limit & Turunan Fungsi Aljabar",
        "deskripsi": "Konsep Limit Fungsi, Aturan Turunan (Diferensial), Gradien Garis Singgung, dan Titik Stasioner.",
        "materi": [
            ("📉 Aturan Dasar Turunan & Aplikasi", """
            <div class="formula-box">Jika f(x) = a · xⁿ , maka turunan pertamanya: f'(x) = n · a · xⁿ⁻¹</div>
            <div class="formula-box">Turunan Konstanta: f(x) = c ⟹ f'(x) = 0  |  Gradien Garis Singgung di x = x₁ : m = f'(x₁)</div>
            <div class="materi-box">
            • Fungsi naik saat <b>f'(x) &gt; 0</b> dan fungsi turun saat <b>f'(x) &lt; 0</b>.<br>
            • Titik stasioner (puncak/lembah) dicapai pada saat <b>f'(x) = 0</b>.
            </div>
            """),
        ],
        "quiz": [
            {"tipe": "pg", "bobot": 20, "soal": "Turunan pertama dari fungsi f(x) = 4x³ - 6x² + 5x - 9 adalah...", "pilihan": ["12x² - 12x + 5", "12x² - 6x + 5", "4x² - 12x + 5", "12x³ - 12x"], "jawaban": 0, "penjelasan": "f'(x) = 3(4)x² - 2(6)x + 5 = 12x² - 12x + 5."},
            {"tipe": "pg", "bobot": 20, "soal": "Nilai dari limit x → 3 untuk fungsi (2x + 5) adalah...", "pilihan": ["6", "8", "11", "13"], "jawaban": 2, "penjelasan": "Substitusi langsung: 2(3) + 5 = 11."},
            {"tipe": "pg", "bobot": 20, "soal": "Gradien garis singgung kurva f(x) = x² + 2x di titik dengan absis x = 2 adalah...", "pilihan": ["4", "6", "8", "10"], "jawaban": 1, "penjelasan": "f'(x) = 2x + 2. Untuk x = 2, maka m = f'(2) = 2(2) + 2 = 6."},
            {"tipe": "pg", "bobot": 20, "soal": "Turunan pertama dari fungsi konstan f(x) = 2025 adalah...", "pilihan": ["2025", "2024", "1", "0"], "jawaban": 3, "penjelasan": "Turunan dari konstanta berapa pun adalah 0."},
            {"tipe": "pg", "bobot": 20, "soal": "Syarat suatu fungsi f(x) mencapai titik stasioner adalah...", "pilihan": ["f(x) = 0", "f'(x) = 0", "f'(x) > 0", "f'(x) < 0"], "jawaban": 1, "penjelasan": "Titik stasioner tercapai ketika gradien garis singgungnya nol: f'(x) = 0."},
        ]
    },
}

# ============================================================
# 6. FUNGSI PEMUAT SOAL QUIZ CUSTOM GURU (.JSON) & PENILAIAN
# ============================================================
def muat_soal_quiz(id_bab, nama_kelas):
    angka_kls = nama_kelas.split()[-1]
    kandidat_prioritas = [
        f"QUIZ_{id_bab.upper()}_KELAS_{angka_kls}.json",
        f"QUIZ_{id_bab.upper()}.json",
    ]
    semua_file = os.listdir(".")
    peta_lower = {f.lower(): f for f in semua_file}

    for target in kandidat_prioritas:
        if target.lower() in peta_lower:
            nama_asli = peta_lower[target.lower()]
            try:
                with open(nama_asli, "r", encoding="utf-8") as fq:
                    data_json = json.load(fq)
                if isinstance(data_json, list) and len(data_json) > 0:
                    return data_json, nama_asli
            except Exception:
                pass

    # Cek file .json lain yang mengandung kata quiz/soal dan cocok dengan bab
    for f in sorted(semua_file):
        fl = f.lower()
        if fl.endswith(".json") and ("quiz" in fl or "soal" in fl):
            if file_cocok_dengan_bab(f, id_bab, nama_kelas) is True:
                try:
                    with open(f, "r", encoding="utf-8") as fq:
                        data_json = json.load(fq)
                    if isinstance(data_json, list) and len(data_json) > 0:
                        return data_json, f
                except Exception:
                    pass

    return DATA_BAB[id_bab]["quiz"], ""

def evaluasi_jawaban_quiz(daftar_soal, prefix_key):
    poin_diperoleh = 0.0
    poin_maks_otomatis = 0.0
    ada_essay_manual = False
    rincian = []

    for i, s in enumerate(daftar_soal):
        tipe = s.get("tipe", "pg")
        bobot = float(s.get("bobot", 10))

        if tipe == "pg":
            poin_maks_otomatis += bobot
            jwb = st.session_state.get(f"{prefix_key}_pg_{i}")
            benar_teks = s["pilihan"][s["jawaban"]]
            is_benar = (jwb == benar_teks)
            skor_item = bobot if is_benar else 0.0
            poin_diperoleh += skor_item
            rincian.append({
                "no": i + 1, "tipe": "Pilihan Ganda", "soal": s["soal"],
                "jawaban_siswa": jwb or "(Kosong)", "kunci": benar_teks,
                "status": "benar" if is_benar else "salah",
                "skor": skor_item, "bobot": bobot
            })

        elif tipe == "pernyataan":
            poin_maks_otomatis += bobot
            daftar_p = s.get("daftar_pernyataan", [])
            jml_p = max(1, len(daftar_p))
            jml_benar = 0
            ringkasan_jwb = []
            ringkasan_kunci = []
            for j, item_p in enumerate(daftar_p):
                jwb_p = st.session_state.get(f"{prefix_key}_st_{i}_{j}")
                kunci_p = item_p["kunci"]
                if jwb_p == kunci_p:
                    jml_benar += 1
                ringkasan_jwb.append(f"P{j+1}: {jwb_p or '-'}")
                ringkasan_kunci.append(f"P{j+1}: {kunci_p}")

            skor_item = bobot * (jml_benar / jml_p)
            poin_diperoleh += skor_item
            status_st = "benar" if jml_benar == jml_p else ("sebagian" if jml_benar > 0 else "salah")
            rincian.append({
                "no": i + 1, "tipe": "Pernyataan", "soal": s["soal"],
                "jawaban_siswa": ", ".join(ringkasan_jwb),
                "kunci": ", ".join(ringkasan_kunci),
                "status": status_st, "jml_benar": jml_benar, "jml_total": jml_p,
                "skor": skor_item, "bobot": bobot
            })

        elif tipe == "essay":
            jwb_es = (st.session_state.get(f"{prefix_key}_es_{i}") or "").strip()
            kata_kunci = [k.strip().lower() for k in s.get("kata_kunci", []) if k.strip()]
            if kata_kunci:
                poin_maks_otomatis += bobot
                jwb_norm = jwb_es.lower()
                cocok = any(k in jwb_norm for k in kata_kunci) and len(jwb_norm) > 0
                skor_item = bobot if cocok else 0.0
                poin_diperoleh += skor_item
                rincian.append({
                    "no": i + 1, "tipe": "Essay (Cek Kata Kunci)", "soal": s["soal"],
                    "jawaban_siswa": jwb_es or "(Kosong)",
                    "kunci": " / ".join(s.get("kata_kunci", [])),
                    "status": "benar" if cocok else "salah",
                    "skor": skor_item, "bobot": bobot
                })
            else:
                ada_essay_manual = True
                rincian.append({
                    "no": i + 1, "tipe": "Essay (Uraian Manual)", "soal": s["soal"],
                    "jawaban_siswa": jwb_es or "(Kosong)",
                    "kunci": "Diperiksa Guru",
                    "status": "manual",
                    "skor": 0.0, "bobot": bobot
                })

    nilai_100 = (poin_diperoleh / poin_maks_otomatis * 100.0) if poin_maks_otomatis > 0 else 0.0
    return nilai_100, poin_diperoleh, poin_maks_otomatis, ada_essay_manual, rincian

def buat_teks_lembar_jawaban(nama_siswa, kelas_rombel, nama_bab, nilai_100, ada_manual, rincian):
    waktu = datetime.now().strftime("%d-%m-%Y %H:%M")
    baris = [
        "============================================================",
        "         LEMBAR BUKTI HASIL QUIZ & JAWABAN SISWA",
        "============================================================",
        f"Nama Siswa   : {nama_siswa or '-'}",
        f"Kelas/Rombel : {kelas_rombel or '-'}",
        f"Bab Materi   : {nama_bab}",
        f"Waktu Submit : {waktu}",
        f"Skor Otomatis: {nilai_100:.1f} / 100" + (" (Belum termasuk Essay Manual Guru)" if ada_manual else ""),
        "============================================================",
        ""
    ]
    for r in rincian:
        baris.append(f"Soal {r['no']} [{r['tipe']}]")
        baris.append(f"Pertanyaan   : {r['soal']}")
        baris.append(f"Jawaban Siswa: {r['jawaban_siswa']}")
        if r["status"] == "manual":
            baris.append(f"Status       : Menunggu Pemeriksaan Guru (Bobot maks: {r['bobot']:g})")
        else:
            baris.append(f"Poin         : {r['skor']:g} / {r['bobot']:g}")
        baris.append("------------------------------------------------------------")
    return "\n".join(baris)

# ============================================================
# 7. FUNGSI KALKULATOR & SIMULASI PER BAB
# ============================================================
def kalkulator_statistika():
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        metode = st.radio("Sumber Data:", ["Contoh Data Otomatis", "Ketik Data Manual", "Upload CSV"], horizontal=True)
    data = []
    if metode == "Contoh Data Otomatis":
        paket = st.selectbox("Pilih Dataset:", [
            "Nilai Ujian Matematika (30 Siswa)",
            "Tinggi Badan Siswa (25 Siswa)",
            "Berat Badan Siswa (20 Siswa)"
        ])
        if "Nilai" in paket:
            data = [45,50,55,60,65,70,75,48,52,58,62,68,72,78,53,57,63,67,73,77,49,54,59,64,69,74,51,56,61,66]
        elif "Tinggi" in paket:
            data = [150,155,158,160,162,163,165,165,167,168,170,170,172,173,175,155,160,163,166,169,171,174,152,157,164]
        else:
            data = [45,48,50,52,55,56,58,60,62,63,65,67,68,70,72,55,58,61,64,69]
    elif metode == "Ketik Data Manual":
        raw = st.text_area("Masukkan angka (pisahkan dengan koma atau spasi):", "45, 50, 55, 60, 65, 70, 75, 48, 52, 58, 62, 68, 72, 78")
        try:
            data = [float(x) for x in raw.replace(",", " ").split() if x.strip()]
        except ValueError:
            st.error("⚠️ Pastikan seluruh input berupa angka.")
    else:
        up = st.file_uploader("Upload file .csv", type=["csv"])
        if up:
            dfc = pd.read_csv(up)
            kol = st.selectbox("Pilih kolom angka:", dfc.columns)
            data = pd.to_numeric(dfc[kol], errors="coerce").dropna().tolist()

    if len(data) < 3:
        st.warning("Masukkan minimal 3 angka untuk membuat tabel distribusi frekuensi.")
        return

    n = len(data)
    k_sturges = max(3, math.ceil(1 + 3.322 * math.log10(n)))
    with col_in2:
        jumlah_kelas = st.slider("Jumlah Kelas Interval (k):", 3, 15, min(15, k_sturges))

    data = sorted(data)
    d_min, d_max = min(data), max(data)
    panjang_kelas = max(1, math.ceil((d_max - d_min) / jumlah_kelas))
    rows, bb, fk = [], d_min, 0
    for i in range(jumlah_kelas):
        ba = bb + panjang_kelas - 1
        tb, ta = bb - 0.5, ba + 0.5
        xi = (bb + ba) / 2
        fi = sum(1 for d in data if d >= bb) if i == jumlah_kelas - 1 else sum(1 for d in data if bb <= d <= ba)
        fk += fi
        rows.append({"No": i+1, "Kelas": f"{bb:.0f} - {ba:.0f}", "Tepi": f"{tb:.1f} - {ta:.1f}", "xi": xi, "fi": fi, "fi_xi": fi*xi, "Fk": fk, "Tb": tb, "Ta": ta})
        bb = ba + 1
    df = pd.DataFrame(rows)

    mean_val = df["fi_xi"].sum() / df["fi"].sum()
    idx_mo = df["fi"].idxmax()
    r_mo = df.loc[idx_mo]
    p_kls = r_mo["Ta"] - r_mo["Tb"]
    d1 = r_mo["fi"] - (df.loc[idx_mo-1, "fi"] if idx_mo > 0 else 0)
    d2 = r_mo["fi"] - (df.loc[idx_mo+1, "fi"] if idx_mo < len(df)-1 else 0)
    modus_val = r_mo["Tb"] + p_kls * (0.5 if (d1+d2) == 0 else d1/(d1+d2))

    half_n = n / 2
    idx_me = df[df["Fk"] >= half_n].index[0]
    r_me = df.loc[idx_me]
    fk_sblm = df.loc[idx_me-1, "Fk"] if idx_me > 0 else 0
    median_val = r_me["Tb"] + p_kls * ((half_n - fk_sblm) / max(1, r_me["fi"]))

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><h3>📈 Rata-rata (Mean)</h3><div class="value">{mean_val:.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h3>🏔️ Modus</h3><div class="value">{modus_val:.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h3>📏 Median</h3><div class="value">{median_val:.2f}</div></div>', unsafe_allow_html=True)

    ktab1, ktab2, ktab3, ktab4, ktab5 = st.tabs(["📋 Tabel", "📈 Mean", "🏔️ Modus", "📏 Median", "📊 Grafik"])
    with ktab1:
        st.dataframe(df[["No", "Kelas", "Tepi", "xi", "fi", "fi_xi", "Fk"]], use_container_width=True, hide_index=True)
    with ktab2:
        st.markdown('<div class="formula-box">x̄ = Σ(fi × xi) / Σfi</div>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            st.markdown(f'<div class="step-box">Kelas <b>{r["Kelas"]}</b>: {r["fi"]} × {r["xi"]:.1f} = <b>{r["fi_xi"]:.1f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-box"><b>x̄ = {df["fi_xi"].sum():.1f} / {n} = {mean_val:.2f}</b></div>', unsafe_allow_html=True)
    with ktab3:
        st.markdown('<div class="formula-box">Mo = Tb + p × (d1 / (d1 + d2))</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-box">Kelas Modus: <b>{r_mo["Kelas"]}</b> (fi = {r_mo["fi"]})<br>Tb = {r_mo["Tb"]:.1f} | p = {p_kls:.1f} | d1 = {d1} | d2 = {d2}<br><b>Mo = {modus_val:.2f}</b></div>', unsafe_allow_html=True)
    with ktab4:
        st.markdown('<div class="formula-box">Me = Tb + p × ((½n - Fk) / fi)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-box">Kelas Median: <b>{r_me["Kelas"]}</b> (Fk pertama ≥ {half_n:.1f})<br>Tb = {r_me["Tb"]:.1f} | p = {p_kls:.1f} | ½n = {half_n:.1f} | Fk = {fk_sblm} | fi = {r_me["fi"]}<br><b>Me = {median_val:.2f}</b></div>', unsafe_allow_html=True)
    with ktab5:
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.bar(df, x="Kelas", y="fi", title="Histogram Frekuensi", color="fi", color_continuous_scale="Blues"), use_container_width=True)
        with g2:
            fig_o = go.Figure(go.Scatter(x=df["Ta"], y=df["Fk"], mode="lines+markers", line=dict(width=3, color="#4f46e5")))
            fig_o.update_layout(title="Kurva Ogive Positif", xaxis_title="Tepi Atas", yaxis_title="Fk")
            st.plotly_chart(fig_o, use_container_width=True)
        fig_comp = go.Figure(go.Bar(
            x=["Mean", "Median", "Modus"], y=[mean_val, median_val, modus_val],
            marker_color=["#4f46e5", "#7c3aed", "#ec4899"],
            text=[f"{mean_val:.2f}", f"{median_val:.2f}", f"{modus_val:.2f}"], textposition="auto"
        ))
        fig_comp.update_layout(title="Perbandingan Mean, Median, dan Modus")
        st.plotly_chart(fig_comp, use_container_width=True)

def kalkulator_geometri():
    gtab1, gtab2 = st.tabs(["🧊 Simulasi Kubus 3D Interaktif (Dimensi Tiga)", "📦 Kalkulator Volume & Luas Bangun Ruang"])
    with gtab1:
        st.info("💡 Sentuh/klik tahan dan geser gambar kubus di bawah ini untuk memutarnya secara 3 Dimensi!")
        c_kiri, c_kanan = st.columns([1, 2])
        with c_kiri:
            s = st.slider("Panjang Rusuk Kubus ABCD.EFGH (cm):", 2, 20, 8)
            pilihan_garis = st.radio("Tampilkan Garis Jarak pada Kubus:", [
                "Diagonal Bidang AC (s√2)",
                "Diagonal Ruang AG (s√3)",
                "Jarak Titik A ke Tengah BC (½s√5)",
                "Jarak Titik A ke Tengah Bidang EFGH (½s√6)"
            ])
            if "AC" in pilihan_garis:
                hasil, ket, gx, gy, gz = s*math.sqrt(2), f"{s}√2", [0, s], [0, s], [0, 0]
            elif "AG" in pilihan_garis:
                hasil, ket, gx, gy, gz = s*math.sqrt(3), f"{s}√3", [0, s], [0, s], [0, s]
            elif "BC" in pilihan_garis:
                hasil, ket, gx, gy, gz = 0.5*s*math.sqrt(5), f"½({s})√5", [0, s], [0, 0.5*s], [0, 0]
            else:
                hasil, ket, gx, gy, gz = 0.5*s*math.sqrt(6), f"½({s})√6", [0, 0.5*s], [0, 0.5*s], [0, s]

            st.markdown(f'<div class="metric-card"><h3>📏 Panjang Garis Merah</h3><div class="value">{hasil:.2f} cm</div><p>Bentuk Akar: <b>{ket} cm</b></p></div>', unsafe_allow_html=True)

        with c_kanan:
            pts = {"A":(0,0,0), "B":(s,0,0), "C":(s,s,0), "D":(0,s,0), "E":(0,0,s), "F":(s,0,s), "G":(s,s,s), "H":(0,s,s)}
            edges = [("A","B"),("B","C"),("C","D"),("D","A"),("E","F"),("F","G"),("G","H"),("H","E"),("A","E"),("B","F"),("C","G"),("D","H")]
            ex, ey, ez = [], [], []
            for u, v in edges:
                ex += [pts[u][0], pts[v][0], None]
                ey += [pts[u][1], pts[v][1], None]
                ez += [pts[u][2], pts[v][2], None]

            fig3d = go.Figure()
            fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode="lines", line=dict(color="#4f46e5", width=6), name="Rusuk Kubus"))
            fig3d.add_trace(go.Scatter3d(
                x=[p[0] for p in pts.values()], y=[p[1] for p in pts.values()], z=[p[2] for p in pts.values()],
                mode="markers+text", text=list(pts.keys()), textposition="top center",
                marker=dict(size=6, color="#1e293b"), textfont=dict(size=15, color="#dc2626"), name="Titik Sudut"
            ))
            fig3d.add_trace(go.Scatter3d(x=gx, y=gy, z=gz, mode="lines+markers", line=dict(color="#ef4444", width=8, dash="dash"), marker=dict(size=8, color="#ef4444"), name="Garis Jarak"))
            fig3d.update_layout(height=480, margin=dict(l=0, r=0, b=0, t=30), title=f"Visualisasi 3D Kubus ABCD.EFGH (s = {s} cm)")
            st.plotly_chart(fig3d, use_container_width=True)

    with gtab2:
        bangun = st.selectbox("Pilih Bangun Ruang:", ["Kubus", "Balok", "Tabung", "Kerucut", "Bola"])
        if bangun == "Kubus":
            r = st.number_input("Rusuk s (cm):", 1.0, 500.0, 6.0)
            vol, lp = r**3, 6*(r**2)
        elif bangun == "Balok":
            c1, c2, c3 = st.columns(3)
            p = c1.number_input("Panjang p:", 1.0, 500.0, 10.0)
            l = c2.number_input("Lebar l:", 1.0, 500.0, 5.0)
            t = c3.number_input("Tinggi t:", 1.0, 500.0, 4.0)
            vol, lp = p*l*t, 2*(p*l + p*t + l*t)
        elif bangun == "Tabung":
            c1, c2 = st.columns(2)
            r = c1.number_input("Jari-jari r:", 1.0, 500.0, 7.0)
            t = c2.number_input("Tinggi t:", 1.0, 500.0, 10.0)
            vol, lp = math.pi*(r**2)*t, 2*math.pi*r*(r+t)
        elif bangun == "Kerucut":
            c1, c2 = st.columns(2)
            r = c1.number_input("Jari-jari r:", 1.0, 500.0, 7.0)
            t = c2.number_input("Tinggi t:", 1.0, 500.0, 24.0)
            pelukis = math.sqrt(r**2 + t**2)
            vol, lp = (1/3)*math.pi*(r**2)*t, math.pi*r*(r + pelukis)
        else:
            r = st.number_input("Jari-jari Bola r:", 1.0, 500.0, 7.0)
            vol, lp = (4/3)*math.pi*(r**3), 4*math.pi*(r**2)

        k1, k2 = st.columns(2)
        k1.markdown(f'<div class="metric-card"><h3>📦 Volume {bangun}</h3><div class="value">{vol:.2f} cm³</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card"><h3>📐 Luas Permukaan</h3><div class="value">{lp:.2f} cm²</div></div>', unsafe_allow_html=True)

def kalkulator_peluang():
    ptab1, ptab2 = st.tabs(["🔢 Kalkulator Permutasi & Kombinasi", "🎲 Simulasi Percobaan Lempar Dadu"])
    with ptab1:
        c1, c2 = st.columns(2)
        n = int(c1.number_input("Jumlah total unsur (n):", 1, 20, 6))
        r = int(c2.number_input("Unsur yang dipilih (r):", 0, n, min(2, n)))
        n_fak = math.factorial(n)
        perm = math.factorial(n) // math.factorial(n - r)
        komb = perm // math.factorial(r)
        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="metric-card"><h3>{n}! (Faktorial)</h3><div class="value">{n_fak:,}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card"><h3>Permutasi P({n},{r})</h3><div class="value">{perm:,}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="metric-card"><h3>Kombinasi C({n},{r})</h3><div class="value">{komb:,}</div></div>', unsafe_allow_html=True)
    with ptab2:
        lemparan = st.slider("Banyaknya pelemparan sebuah dadu (N):", 12, 1200, 120, step=12)
        hasil_dadu = [random.randint(1, 6) for _ in range(lemparan)]
        label_mata = [f"Mata {i}" for i in range(1, 7)]
        frek_muncul = [hasil_dadu.count(i) for i in range(1, 7)]
        frek_harapan = [lemparan / 6.0] * 6
        fig_d = go.Figure(data=[
            go.Bar(name="Frekuensi Simulasi", x=label_mata, y=frek_muncul, marker_color="#4f46e5"),
            go.Bar(name="Frekuensi Harapan Teoretis", x=label_mata, y=frek_harapan, marker_color="#f59e0b")
        ])
        fig_d.update_layout(barmode="group", title=f"Hasil Simulasi {lemparan} Kali Lempar Dadu")
        st.plotly_chart(fig_d, use_container_width=True)

def kalkulator_eksponen():
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ⚡ Hitung Eksponen & Grafik f(x) = aˣ")
        basis = st.slider("Pilih basis a:", 0.2, 5.0, 2.0, 0.1)
        pangkat = st.number_input("Masukkan pangkat x:", -10.0, 10.0, 3.0)
        st.markdown(f'<div class="metric-card"><h3>Nilai ({basis})^{pangkat}</h3><div class="value">{basis**pangkat:.4f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("#### 🪵 Hitung Logaritma (ᵃlog b)")
        a_log = st.number_input("Basis a (a > 0, a ≠ 1):", 0.1, 100.0, 2.0)
        b_log = st.number_input("Numerus b (b > 0):", 0.01, 100000.0, 8.0)
        if abs(a_log - 1.0) > 1e-9:
            val_log = math.log(b_log, a_log)
            st.markdown(f'<div class="metric-card"><h3>Nilai {a_log} log {b_log}</h3><div class="value">{val_log:.4f}</div></div>', unsafe_allow_html=True)
        else:
            st.warning("Basis logaritma tidak boleh bernilai 1.")
    xs = np.linspace(-3, 4, 100)
    fig = go.Figure(go.Scatter(x=xs, y=basis**xs, mode="lines", line=dict(width=3, color="#4f46e5")))
    fig.update_layout(title=f"Grafik Fungsi Eksponen f(x) = ({basis})ˣ", xaxis_title="x", yaxis_title="f(x)")
    st.plotly_chart(fig, use_container_width=True)

def kalkulator_barisan():
    jenis = st.radio("Pilih Jenis Barisan:", ["Barisan & Deret Aritmetika", "Barisan & Deret Geometri"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("Suku pertama (a):", -500.0, 500.0, 3.0)
    n = int(c3.slider("Suku ke-n yang dicari:", 2, 20, 8))
    if "Aritmetika" in jenis:
        b = c2.number_input("Beda (b):", -100.0, 100.0, 4.0)
        suku_list = [a + i*b for i in range(n)]
    else:
        r = c2.number_input("Rasio (r):", -10.0, 10.0, 2.0)
        suku_list = [a * (r**i) for i in range(n)]
    un, sn = suku_list[-1], sum(suku_list)

    k1, k2 = st.columns(2)
    k1.markdown(f'<div class="metric-card"><h3>Suku ke-{n} (U{n})</h3><div class="value">{un:,.2f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><h3>Jumlah {n} Suku (S{n})</h3><div class="value">{sn:,.2f}</div></div>', unsafe_allow_html=True)
    teks_barisan = ", ".join(f"{x:g}" for x in suku_list)
    st.markdown(f'<div class="step-box"><b>Urutan Barisan:</b> {teks_barisan}</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Bar(x=[f"U{i+1}" for i in range(n)], y=suku_list, marker_color="#4f46e5"))
    fig.update_layout(title="Visualisasi Pertumbuhan Nilai Suku", xaxis_title="Urutan Suku", yaxis_title="Nilai")
    st.plotly_chart(fig, use_container_width=True)

def kalkulator_trigonometri():
    t1, t2 = st.tabs(["📐 Segitiga Siku-siku", "🌊 Grafik Gelombang Sinus & Cosinus"])
    with t1:
        c1, c2 = st.columns(2)
        depan = c1.number_input("Sisi Depan sudut θ:", 0.1, 500.0, 3.0)
        samping = c2.number_input("Sisi Samping sudut θ:", 0.1, 500.0, 4.0)
        miring = math.sqrt(depan**2 + samping**2)
        sudut_deg = math.degrees(math.atan2(depan, samping))
        st.markdown(f'<div class="step-box">Sisi Miring = √({depan}² + {samping}²) = <b>{miring:.2f}</b> &nbsp;|&nbsp; Besar Sudut θ ≈ <b>{sudut_deg:.2f}°</b></div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("sin θ (De/Mi)", f"{depan/miring:.4f}")
        k2.metric("cos θ (Sa/Mi)", f"{samping/miring:.4f}")
        k3.metric("tan θ (De/Sa)", f"{depan/samping:.4f}")
    with t2:
        c1, c2 = st.columns(2)
        amp = c1.slider("Amplitudo (A):", 1.0, 5.0, 2.0, 0.5)
        k_freq = c2.slider("Banyak gelombang (k):", 1, 5, 1)
        deg = np.linspace(0, 360, 361)
        rad = np.radians(deg)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=deg, y=amp*np.sin(k_freq*rad), name=f"{amp} sin({k_freq}x)"))
        fig.add_trace(go.Scatter(x=deg, y=amp*np.cos(k_freq*rad), name=f"{amp} cos({k_freq}x)"))
        fig.update_layout(title="Grafik Fungsi Trigonometri (0° - 360°)", xaxis_title="Sudut (°)", yaxis_title="y")
        st.plotly_chart(fig, use_container_width=True)

def kalkulator_matriks():
    st.markdown("#### 🧮 Kalkulator Matriks Ordo 2 × 2")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Matriks A**")
        a1, a2 = st.columns(2)
        a11 = a1.number_input("a11", value=4.0)
        a12 = a2.number_input("a12", value=2.0)
        a21 = a1.number_input("a21", value=3.0)
        a22 = a2.number_input("a22", value=2.0)
    with col_b:
        st.markdown("**Matriks B**")
        b1, b2 = st.columns(2)
        b11 = b1.number_input("b11", value=1.0)
        b12 = b2.number_input("b12", value=5.0)
        b21 = b1.number_input("b21", value=2.0)
        b22 = b2.number_input("b22", value=3.0)

    A = np.array([[a11, a12], [a21, a22]])
    B = np.array([[b11, b12], [b21, b22]])
    det_a = a11*a22 - a12*a21
    st.markdown(f'<div class="metric-card"><h3>Determinan Matriks A</h3><div class="value">{det_a:.2f}</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**Penjumlahan (A + B):**")
        st.dataframe(pd.DataFrame(A + B), hide_index=True)
    with c2:
        st.write("**Perkalian (A × B):**")
        st.dataframe(pd.DataFrame(A @ B), hide_index=True)
    with c3:
        st.write("**Invers Matriks A (A⁻¹):**")
        if det_a != 0:
            inv_a = (1/det_a) * np.array([[a22, -a12], [-a21, a11]])
            st.dataframe(pd.DataFrame(np.round(inv_a, 3)), hide_index=True)
        else:
            st.warning("Matriks singular (det = 0), tidak memiliki invers.")

def kalkulator_transformasi():
    st.markdown("#### 🔄 Simulator Bayangan Titik P(x, y) pada Bidang Kartesius")
    c1, c2, c3 = st.columns(3)
    px_in = c1.number_input("Koordinat x awal:", -20.0, 20.0, 3.0)
    py_in = c2.number_input("Koordinat y awal:", -20.0, 20.0, 2.0)
    jenis = c3.selectbox("Jenis Transformasi:", [
        "Translasi T(a, b)", "Refleksi Sumbu-X", "Refleksi Sumbu-Y",
        "Refleksi Garis y = x", "Rotasi +90° Pusat O(0,0)", "Rotasi 180° Pusat O(0,0)", "Dilatasi [O, k]"
    ])
    if "Translasi" in jenis:
        ta = st.slider("Geser mendatar (a):", -10.0, 10.0, 4.0)
        tb = st.slider("Geser tegak (b):", -10.0, 10.0, -3.0)
        bx, by = px_in + ta, py_in + tb
    elif "Sumbu-X" in jenis:
        bx, by = px_in, -py_in
    elif "Sumbu-Y" in jenis:
        bx, by = -px_in, py_in
    elif "y = x" in jenis:
        bx, by = py_in, px_in
    elif "+90°" in jenis:
        bx, by = -py_in, px_in
    elif "180°" in jenis:
        bx, by = -px_in, -py_in
    else:
        k = st.slider("Faktor skala (k):", -4.0, 4.0, 2.0, 0.5)
        bx, by = k * px_in, k * py_in

    st.markdown(f'<div class="metric-card"><h3>Koordinat Bayangan P\'</h3><div class="value">P\'({bx:g}, {by:g})</div><p>Titik Awal: P({px_in:g}, {py_in:g})</p></div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[px_in], y=[py_in], mode="markers+text", text=[f"P({px_in:g},{py_in:g})"], textposition="top center", marker=dict(size=14, color="#4f46e5"), name="Titik Awal P"))
    fig.add_trace(go.Scatter(x=[bx], y=[by], mode="markers+text", text=[f"P'({bx:g},{by:g})"], textposition="top center", marker=dict(size=14, color="#ef4444"), name="Bayangan P'"))
    fig.update_layout(xaxis=dict(zeroline=True, zerolinewidth=2), yaxis=dict(zeroline=True, zerolinewidth=2), title="Posisi Titik Awal (Biru) & Bayangan (Merah)")
    st.plotly_chart(fig, use_container_width=True)

def kalkulator_turunan():
    st.markdown("#### 📉 Kalkulator Turunan & Garis Singgung Kurva f(x) = ax³ + bx² + cx + d")
    c1, c2, c3, c4 = st.columns(4)
    a = c1.number_input("Koefisien a (x³):", -10.0, 10.0, 0.0)
    b = c2.number_input("Koefisien b (x²):", -10.0, 10.0, 1.0)
    c = c3.number_input("Koefisien c (x):", -20.0, 20.0, -2.0)
    d = c4.number_input("Konstanta d:", -50.0, 50.0, 1.0)
    x0 = st.slider("Pilih titik singgung absis x₀:", -5.0, 5.0, 2.0, 0.5)

    y0 = a*(x0**3) + b*(x0**2) + c*x0 + d
    m = 3*a*(x0**2) + 2*b*x0 + c
    st.markdown(f'<div class="formula-box">Turunan Pertama: f\'(x) = {3*a:g}x² + ({2*b:g})x + ({c:g})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><h3>Gradien Garis Singgung di x₀ = {x0:g}</h3><div class="value">m = {m:.2f}</div><p>Titik Singgung: ({x0:g}, {y0:.2f})</p></div>', unsafe_allow_html=True)

    xs = np.linspace(x0 - 4, x0 + 4, 200)
    ys = a*(xs**3) + b*(xs**2) + c*xs + d
    y_singgung = m*(xs - x0) + y0
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, name="Kurva f(x)", line=dict(width=3, color="#4f46e5")))
    fig.add_trace(go.Scatter(x=xs, y=y_singgung, name="Garis Singgung", line=dict(width=2, dash="dash", color="#ef4444")))
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode="markers", marker=dict(size=11, color="#ef4444"), name="Titik Singgung"))
    fig.update_layout(title="Kurva f(x) dan Garis Singgungnya", xaxis_title="x", yaxis_title="y")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 8. SIDEBAR NAVIGASI (TINGKAT KELAS -> BAB MATERI -> KEGIATAN)
# ============================================================
with st.sidebar:
    st.markdown(f"## 🎓 {NAMA_APLIKASI}")
    if NAMA_GURU_SEKOLAH.strip():
        st.caption(NAMA_GURU_SEKOLAH)

    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.markdown("---")

    daftar_nama_kelas = list(KURIKULUM_KELAS.keys())
    kelas_aktif = st.radio("🏫 Pilih Tingkat Kelas:", daftar_nama_kelas, index=KELAS_AWAL_INDEX, horizontal=True)

    daftar_bab_kelas = KURIKULUM_KELAS[kelas_aktif]
    label_bab_list = [label for _, label in daftar_bab_kelas]
    bab_label_aktif = st.radio(f"📚 Pilih Bab Materi ({kelas_aktif}):", label_bab_list)
    id_bab_aktif = dict((lbl, kode) for kode, lbl in daftar_bab_kelas)[bab_label_aktif]

    st.markdown("---")
    halaman = st.radio(
        "📌 Pilih Kegiatan Belajar:",
        ["🏠 Beranda", "📖 Materi", "📄 LKPD", "🧮 Kalkulator & Simulasi", "📝 Quiz", "🛠️ Buat Soal Guru"],
        index=0
    )

info_bab = DATA_BAB[id_bab_aktif]
badge_html = f'<div class="badge-aktif">🏫 {kelas_aktif} &nbsp;│&nbsp; {bab_label_aktif}</div>'

# ============================================================
# 9. TAMPILAN HALAMAN UTAMA
# ============================================================
if halaman == "🏠 Beranda":
    guru_sub = f"<p style='font-size:0.95rem; opacity:0.92;'>{NAMA_GURU_SEKOLAH}</p>" if NAMA_GURU_SEKOLAH.strip() else ""
    st.markdown(f"""
    <div class="main-header">
        {badge_html}
        <h1>🎓 {NAMA_APLIKASI}</h1>
        <p>Bab Aktif Saat Ini: <b>{info_bab['nama']}</b> ({kelas_aktif})</p>
        {guru_sub}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗺️ Peta Kurikulum Materi Pembelajaran (Kelas 10, 11 & 12)")
    st.caption("Pilih Tingkat Kelas dan Bab Materi melalui panel menu di sebelah kiri layar.")

    k_col1, k_col2, k_col3 = st.columns(3)
    for kol, nama_kls in zip([k_col1, k_col2, k_col3], ["Kelas 10", "Kelas 11", "Kelas 12"]):
        isi_pohon = "<br>".join([
            f"{'└──' if idx == len(KURIKULUM_KELAS[nama_kls])-1 else '├──'} {lbl}"
            for idx, (_, lbl) in enumerate(KURIKULUM_KELAS[nama_kls])
        ])
        sorot = "border: 2px solid #4f46e5;" if nama_kls == kelas_aktif else ""
        with kol:
            st.markdown(f"""
            <div class="materi-box" style="{sorot}">
                <h3 style="margin-top:0;">🏫 {nama_kls}</h3>
                <div style="line-height:1.9; font-size:0.95rem;">{isi_pohon}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🎯 Fasilitas Belajar pada Setiap Bab")
    f1, f2, f3, f4 = st.columns(4)
    f1.markdown('<div class="metric-card"><h3>📖 Materi</h3><p>Modul bahan ajar guru & ringkasan konsep tiap bab.</p></div>', unsafe_allow_html=True)
    f2.markdown('<div class="metric-card"><h3>📄 LKPD</h3><p>Lembar kerja siswa sesuai bab aktif & pratinjau langsung.</p></div>', unsafe_allow_html=True)
    f3.markdown('<div class="metric-card"><h3>🧮 Simulasi</h3><p>Kalkulator interaktif, grafik 2D & bangun ruang 3D.</p></div>', unsafe_allow_html=True)
    f4.markdown('<div class="metric-card"><h3>📝 Quiz</h3><p>Soal Pilihan Ganda, Pernyataan (AKM) & Essay Uraian.</p></div>', unsafe_allow_html=True)

elif halaman == "📖 Materi":
    st.markdown(f"""
    <div class="main-header">
        {badge_html}
        <h1>📖 Materi: {info_bab['nama']}</h1>
        <p>{info_bab['deskripsi']}</p>
    </div>
    """, unsafe_allow_html=True)

    ekstensi_materi = (".pdf", ".pptx", ".ppt", ".docx", ".doc", ".png", ".jpg", ".jpeg")
    semua_materi = sorted([f for f in os.listdir(".") if f.lower().endswith(ekstensi_materi) and not adalah_file_lkpd(f)])
    materi_bab = [f for f in semua_materi if file_cocok_dengan_bab(f, id_bab_aktif, kelas_aktif) is True]
    materi_umum = [f for f in semua_materi if file_cocok_dengan_bab(f, id_bab_aktif, kelas_aktif) is None]

    judul_tabs = ["📚 Bahan Ajar Guru"] + [j for j, _ in info_bab["materi"]]
    tabs_obj = st.tabs(judul_tabs)

    with tabs_obj[0]:
        if LINK_VIDEO_YOUTUBE.strip():
            st.markdown("### 🎬 Video Pembelajaran")
            st.video(LINK_VIDEO_YOUTUBE.strip())
            st.markdown("---")

        daftar_tampil = materi_bab + materi_umum
        if not daftar_tampil:
            st.info(
                f"ℹ️ Belum ada file modul tambahan yang diunggah untuk {info_bab['nama']}. "
                f"Silakan pelajari ringkasan konsep pada tab di sebelah kanan atas."
            )
        else:
            for idx, nama_file in enumerate(daftar_tampil):
                with open(nama_file, "rb") as fd:
                    isi_bytes = fd.read()
                nk = nama_file.lower()
                ikon = "📕" if nk.endswith(".pdf") else ("🖼️" if nk.endswith((".png", ".jpg", ".jpeg")) else "📘")
                c_nm, c_dl = st.columns([3, 1])
                c_nm.markdown(f"#### {ikon} {nama_file}")
                c_dl.download_button("⬇️ Download Materi", isi_bytes, file_name=nama_file, key=f"dl_m_{id_bab_aktif}_{idx}", use_container_width=True, type="primary")
                if nk.endswith(".pdf"):
                    with st.expander(f"👁️ Baca {nama_file} di Layar", expanded=True):
                        tampilkan_pratinjau_pdf(isi_bytes)
                elif nk.endswith((".png", ".jpg", ".jpeg")):
                    st.image(isi_bytes, caption=nama_file, use_container_width=True)
                st.markdown("---")

    for idx_t, (_, konten_html) in enumerate(info_bab["materi"], start=1):
        with tabs_obj[idx_t]:
            st.markdown(konten_html, unsafe_allow_html=True)

elif halaman == "📄 LKPD":
    st.markdown(f"""
    <div class="main-header">
        {badge_html}
        <h1>📄 LKPD: {info_bab['nama']}</h1>
        <p>Lembar Kerja Peserta Didik — {kelas_aktif}</p>
    </div>
    """, unsafe_allow_html=True)

    semua_lkpd = sorted([f for f in os.listdir(".") if f.lower().endswith((".pdf", ".docx", ".doc")) and adalah_file_lkpd(f)])
    lkpd_bab = [f for f in semua_lkpd if file_cocok_dengan_bab(f, id_bab_aktif, kelas_aktif) is True]
    lkpd_umum = [f for f in semua_lkpd if file_cocok_dengan_bab(f, id_bab_aktif, kelas_aktif) is None]

    daftar_lkpd = lkpd_bab + lkpd_umum
    if not daftar_lkpd:
        st.info(f"ℹ️ Belum ada file LKPD yang diunggah untuk bab {info_bab['nama']}.")
    else:
        for idx, nama_file in enumerate(daftar_lkpd):
            with open(nama_file, "rb") as fd:
                isi_bytes = fd.read()
            c_nm, c_dl = st.columns([3, 1])
            c_nm.markdown(f"#### 📕 {nama_file}")
            c_dl.download_button("⬇️ Download LKPD", isi_bytes, file_name=nama_file, key=f"dl_l_{id_bab_aktif}_{idx}", use_container_width=True, type="primary")
            if nama_file.lower().endswith(".pdf"):
                with st.expander(f"👁️ Lihat Pratinjau {nama_file} di Layar", expanded=True):
                    tampilkan_pratinjau_pdf(isi_bytes)
            st.markdown("---")

    if LINK_PENGUMPULAN.strip():
        st.markdown("### 📤 Pengumpulan Hasil Kerja Siswa")
        st.link_button("📤 Kumpulkan Tugas / Jawaban LKPD", LINK_PENGUMPULAN, type="primary")

elif halaman == "🧮 Kalkulator & Simulasi":
    st.markdown(f"""
    <div class="main-header">
        {badge_html}
        <h1>🧮 Simulasi Interaktif: {info_bab['nama']}</h1>
        <p>Eksplorasi Perhitungan & Visualisasi Grafik Secara Langsung</p>
    </div>
    """, unsafe_allow_html=True)

    if id_bab_aktif == "statistika":
        kalkulator_statistika()
    elif id_bab_aktif == "geometri":
        kalkulator_geometri()
    elif id_bab_aktif == "peluang":
        kalkulator_peluang()
    elif id_bab_aktif == "eksponen":
        kalkulator_eksponen()
    elif id_bab_aktif == "barisan":
        kalkulator_barisan()
    elif id_bab_aktif == "trigonometri":
        kalkulator_trigonometri()
    elif id_bab_aktif == "matriks":
        kalkulator_matriks()
    elif id_bab_aktif == "transformasi":
        kalkulator_transformasi()
    elif id_bab_aktif == "turunan":
        kalkulator_turunan()

# ============================================================
# 10. HALAMAN QUIZ SISWA (MENDUKUNG PG, PERNYATAAN & ESSAY)
# ============================================================
elif halaman == "📝 Quiz":
    st.markdown(f"""
    <div class="main-header">
        {badge_html}
        <h1>📝 Quiz Evaluasi: {info_bab['nama']}</h1>
        <p>Kerjakan soal evaluasi berikut dengan teliti ({kelas_aktif})</p>
    </div>
    """, unsafe_allow_html=True)

    daftar_soal, sumber_file = muat_soal_quiz(id_bab_aktif, kelas_aktif)
    quiz_key_unik = f"qz_{kelas_aktif}_{id_bab_aktif}"
    sudah_submit = (st.session_state.quiz_submitted_key == quiz_key_unik)

    # Identitas Siswa
    id_c1, id_c2 = st.columns(2)
    nama_siswa = id_c1.text_input("👤 Nama Lengkap Siswa:", key=f"{quiz_key_unik}_nama", placeholder="Ketik nama lengkapmu...")
    rombel_siswa = id_c2.text_input("🏫 Kelas / Rombel:", value=kelas_aktif, key=f"{quiz_key_unik}_rombel")
    if sumber_file:
        st.caption(f"📄 Paket Soal Aktif: **{sumber_file}** ({len(daftar_soal)} butir soal)")
    st.markdown("---")

    for i, soal in enumerate(daftar_soal):
        tipe = soal.get("tipe", "pg")
        bobot = soal.get("bobot", 10)
        tampil_kunci = soal.get("tampilkan_kunci", True)
        label_tipe = {"pg": "Pilihan Ganda", "pernyataan": "Pernyataan", "essay": "Essay / Uraian"}.get(tipe, "Soal")

        st.markdown(f"""
        <div class="quiz-box">
            <b>Soal {i+1}</b> <span style="opacity:0.75; font-size:0.9rem;">[{label_tipe} • Bobot: {bobot:g} poin]</span><br><br>
            {soal['soal']}
        </div>
        """, unsafe_allow_html=True)

        if tipe == "pg":
            jwb = st.radio(f"Pilih jawaban soal {i+1}:", soal["pilihan"], key=f"{quiz_key_unik}_pg_{i}", index=None)
            if sudah_submit and tampil_kunci:
                benar_teks = soal["pilihan"][soal["jawaban"]]
                if jwb == benar_teks:
                    st.markdown(f'<div class="quiz-benar">✅ <b>Benar!</b> {soal.get("penjelasan", "")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quiz-salah">❌ <b>Kurang tepat.</b> Kunci Jawaban: <b>{benar_teks}</b><br>{soal.get("penjelasan", "")}</div>', unsafe_allow_html=True)

        elif tipe == "pernyataan":
            opsi_st = soal.get("label_opsi", ["Benar", "Salah"])
            daftar_p = soal.get("daftar_pernyataan", [])
            semua_tepat = True
            for j, item_p in enumerate(daftar_p):
                cp1, cp2 = st.columns([3, 2])
                cp1.markdown(f"**{j+1}.** {item_p['teks']}")
                pil_p = cp2.radio(
                    f"Pernyataan {i+1}.{j+1}", opsi_st,
                    key=f"{quiz_key_unik}_st_{i}_{j}", index=None,
                    horizontal=True, label_visibility="collapsed"
                )
                if pil_p != item_p["kunci"]:
                    semua_tepat = False

            if sudah_submit and tampil_kunci:
                teks_kunci_st = " &nbsp;|&nbsp; ".join([f"({j+1}) <b>{p['kunci']}</b>" for j, p in enumerate(daftar_p)])
                if semua_tepat:
                    st.markdown(f'<div class="quiz-benar">✅ <b>Semua Pernyataan Tepat!</b> ({teks_kunci_st})<br>{soal.get("penjelasan", "")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quiz-salah">❌ <b>Belum semuanya tepat.</b> Kunci: {teks_kunci_st}<br>{soal.get("penjelasan", "")}</div>', unsafe_allow_html=True)

        elif tipe == "essay":
            jwb_es = st.text_area(
                f"Ketik jawaban uraian soal {i+1}:",
                key=f"{quiz_key_unik}_es_{i}",
                height=110,
                placeholder="Tuliskan langkah penyelesaian atau jawabanmu di sini..."
            )
            if sudah_submit:
                kata_kunci = [k.strip().lower() for k in soal.get("kata_kunci", []) if k.strip()]
                if kata_kunci:
                    cocok = any(k in jwb_es.lower() for k in kata_kunci) and len(jwb_es.strip()) > 0
                    if cocok:
                        st.markdown(f'<div class="quiz-benar">✅ <b>Jawaban Sesuai Kunci!</b><br>{soal.get("penjelasan", "") if tampil_kunci else ""}</div>', unsafe_allow_html=True)
                    else:
                        kunci_info = f"Kunci Utama: <b>{' / '.join(soal.get('kata_kunci', []))}</b><br>" if tampil_kunci else ""
                        st.markdown(f'<div class="quiz-salah">❌ <b>Belum sesuai kata/angka kunci.</b> {kunci_info}{soal.get("penjelasan", "") if tampil_kunci else ""}</div>', unsafe_allow_html=True)
                else:
                    pedoman = f"<br><b>Pedoman / Pembahasan:</b> {soal.get('penjelasan', '')}" if (tampil_kunci and soal.get("penjelasan")) else ""
                    st.markdown(f'<div class="quiz-info">📝 <b>Jawaban uraian tersimpan</b> dan akan diperiksa oleh Bapak/Ibu Guru.{pedoman}</div>', unsafe_allow_html=True)

        st.markdown("---")

    b1, b2 = st.columns(2)
    if b1.button("✅ Selesai & Cek Skor Jawaban", type="primary", use_container_width=True):
        st.session_state.quiz_submitted_key = quiz_key_unik
        st.rerun()

    if b2.button("🔄 Ulangi Quiz Bab Ini", use_container_width=True):
        st.session_state.quiz_submitted_key = ""
        hapus_keys = [k for k in st.session_state.keys() if k.startswith(f"{quiz_key_unik}_pg_") or k.startswith(f"{quiz_key_unik}_st_") or k.startswith(f"{quiz_key_unik}_es_")]
        for hk in hapus_keys:
            st.session_state.pop(hk, None)
        st.rerun()

    if sudah_submit:
        nilai_100, poin_dapat, poin_maks, ada_manual, rincian = evaluasi_jawaban_quiz(daftar_soal, quiz_key_unik)
        catatan_manual = "<p style='font-size:0.9rem;'>ℹ️ <i>Terdapat soal Essay Uraian yang diperiksa manual oleh Guru. Silakan unduh Bukti Jawaban di bawah ini.</i></p>" if ada_manual else ""
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏆 Hasil Evaluasi: {nama_siswa or 'Siswa'} ({rombel_siswa})</h3>
            <div class="value">{nilai_100:.0f} / 100</div>
            <p>Total Poin Objektif: <b>{poin_dapat:g}</b> dari <b>{poin_maks:g}</b> poin</p>
            {catatan_manual}
        </div>
        """, unsafe_allow_html=True)

        teks_bukti = buat_teks_lembar_jawaban(nama_siswa, rombel_siswa, f"{info_bab['nama']} ({kelas_aktif})", nilai_100, ada_manual, rincian)
        nama_bersih = (nama_siswa.strip().replace(" ", "_") if nama_siswa.strip() else "Siswa")
        dl_col1, dl_col2 = st.columns(2)
        dl_col1.download_button(
            "⬇️ Download Lembar Bukti & Jawaban Essay (.txt)",
            data=teks_bukti.encode("utf-8"),
            file_name=f"Hasil_Quiz_{id_bab_aktif}_{nama_bersih}.txt",
            mime="text/plain",
            use_container_width=True
        )
        if LINK_PENGUMPULAN.strip():
            dl_col2.link_button("📤 Kirim Bukti Jawaban ke Guru", LINK_PENGUMPULAN, type="primary", use_container_width=True)

# ============================================================
# 11. STUDIO PEMBUAT SOAL GURU (DILINDUNGI PIN: 1977)
# ============================================================
elif halaman == "🛠️ Buat Soal Guru":
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ Studio Pembuat Soal Guru</h1>
        <p>Buat Soal Pilihan Ganda, Pernyataan (Benar/Salah), dan Essay Tanpa Ngoding</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.guru_unlocked:
        st.markdown("""
        <div class="materi-box" style="max-width:480px; margin: 1rem auto; text-align:center;">
            <h3>🔒 Area Khusus Bapak/Ibu Guru</h3>
            <p>Masukkan PIN Guru untuk membuka Studio Pembuat Soal.</p>
        </div>
        """, unsafe_allow_html=True)
        c_kiri, c_tengah, c_kanan = st.columns([1, 1.2, 1])
        with c_tengah:
            pin_input = st.text_input("🔑 Masukkan PIN Guru:", type="password", placeholder="Ketik PIN...")
            if st.button("🔓 Masuk Mode Guru", type="primary", use_container_width=True):
                if pin_input.strip() == PIN_GURU:
                    st.session_state.guru_unlocked = True
                    st.rerun()
                else:
                    st.error("❌ PIN salah! Silakan coba lagi.")
    else:
        top_c1, top_c2 = st.columns([4, 1])
        top_c1.success("✅ Mode Guru Aktif! Bapak/Ibu dapat menyusun soal evaluasi di bawah ini.")
        if top_c2.button("🔒 Keluar Mode Guru", use_container_width=True):
            st.session_state.guru_unlocked = False
            st.rerun()

        with st.expander("📖 Petunjuk 3 Langkah Cara Memasang Soal Buatan Sendiri ke Website", expanded=False):
            st.markdown("""
            1. **Pilih Target Bab & Kelas** di bawah ini, lalu tambahkan soal (**Pilihan Ganda**, **Pernyataan**, atau **Essay**).
            2. Setelah semua soal selesai disusun, gulir ke bagian paling bawah lalu klik tombol biru **⬇️ Download File Soal (.json)**.
            3. Buka repositori **GitHub** Bapak/Ibu ➡️ klik **Add file (`+`) → Upload files** ➡️ masukkan file `.json` tersebut *(jangan ubah nama filenya)* ➡️ klik **Commit changes**. Soal otomatis langsung tampil di menu **📝 Quiz** siswa!
            """)

        st.markdown("### 1️⃣ Pilih Target Bab & Kelas")
        tg1, tg2 = st.columns(2)
        daftar_id_bab = list(DATA_BAB.keys())
        idx_bab_default = daftar_id_bab.index(id_bab_aktif) if id_bab_aktif in daftar_id_bab else 0
        pilih_bab_soal = tg1.selectbox(
            "📚 Pilih Bab Materi:",
            daftar_id_bab,
            index=idx_bab_default,
            format_func=lambda k: f"{DATA_BAB[k]['nama']} ({k.upper()})"
        )
        pilih_target_kls = tg2.selectbox(
            "🏫 Berlaku untuk Tingkat Kelas:",
            ["Semua Kelas pada Bab Ini", "Khusus Kelas 10", "Khusus Kelas 11", "Khusus Kelas 12"]
        )

        if pilih_target_kls == "Semua Kelas pada Bab Ini":
            nama_file_target = f"QUIZ_{pilih_bab_soal.upper()}.json"
            kls_acuan = kelas_aktif
        else:
            angka_t = pilih_target_kls.split()[-1]
            nama_file_target = f"QUIZ_{pilih_bab_soal.upper()}_KELAS_{angka_t}.json"
            kls_acuan = f"Kelas {angka_t}"

        if nama_file_target not in st.session_state.draft_bank:
            st.session_state.draft_bank[nama_file_target] = []

        draft_list = st.session_state.draft_bank[nama_file_target]

        # Tombol bantu muat soal yang sudah ada / upload file lama / kosongkan
        act1, act2, act3 = st.columns(3)
        if act1.button("📂 Muat Soal yang Sedang Aktif di Bab Ini", use_container_width=True):
            soal_aktif, _ = muat_soal_quiz(pilih_bab_soal, kls_acuan)
            st.session_state.draft_bank[nama_file_target] = json.loads(json.dumps(soal_aktif))
            st.rerun()
        if act2.button("🗑️ Kosongkan Daftar Draft (Mulai dari Nol)", use_container_width=True):
            st.session_state.draft_bank[nama_file_target] = []
            st.rerun()
        with act3:
            up_json = st.file_uploader("📤 Edit File .json Lama", type=["json"], label_visibility="collapsed")
            if up_json is not None:
                try:
                    isi_lama = json.load(up_json)
                    if isinstance(isi_lama, list):
                        st.session_state.draft_bank[nama_file_target] = isi_lama
                        st.success("File soal berhasil dimuat!")
                except Exception:
                    st.error("Format file .json tidak valid.")

        st.markdown("---")
        st.markdown("### 2️⃣ Tambah Butir Soal Baru")
        tab_pg, tab_st, tab_es = st.tabs([
            "🅰️ Bentuk Pilihan Ganda",
            "✅ Bentuk Pernyataan (Benar/Salah)",
            "✍️ Bentuk Essay / Uraian"
        ])

        # --- TAB 1: BUAT PILIHAN GANDA ---
        with tab_pg:
            pg_soal = st.text_area("Pertanyaan Pilihan Ganda:", key="in_pg_soal", placeholder="Ketik soal pilihan ganda di sini...")
            oc1, oc2 = st.columns(2)
            op_a = oc1.text_input("Pilihan A:", key="in_pg_a")
            op_b = oc2.text_input("Pilihan B:", key="in_pg_b")
            op_c = oc1.text_input("Pilihan C:", key="in_pg_c")
            op_d = oc2.text_input("Pilihan D:", key="in_pg_d")
            op_e = st.text_input("Pilihan E (Opsional — kosongkan jika hanya sampai D):", key="in_pg_e")

            kc1, kc2, kc3 = st.columns([1.5, 1, 2])
            opsi_tersedia = ["A", "B", "C", "D"] + (["E"] if op_e.strip() else [])
            kunci_huruf = kc1.selectbox("Kunci Jawaban Benar:", opsi_tersedia, key="in_pg_kunci")
            pg_bobot = kc2.number_input("Bobot Poin:", 1, 100, 20, key="in_pg_bobot")
            pg_tampil = kc3.checkbox("Tampilkan pembahasan setelah siswa selesai", value=True, key="in_pg_tampil")
            pg_bahas = st.text_input("Pembahasan Singkat (Opsional):", key="in_pg_bahas")

            if st.button("➕ Tambahkan Soal Pilihan Ganda ke Daftar", type="primary"):
                pilihan_list = [op_a.strip(), op_b.strip(), op_c.strip(), op_d.strip()]
                if op_e.strip():
                    pilihan_list.append(op_e.strip())
                if not pg_soal.strip() or any(not x for x in pilihan_list[:4]):
                    st.warning("⚠️ Mohon isi teks pertanyaan dan minimal Pilihan A sampai D.")
                else:
                    idx_jwb = ["A", "B", "C", "D", "E"].index(kunci_huruf)
                    draft_list.append({
                        "tipe": "pg",
                        "soal": pg_soal.strip(),
                        "pilihan": pilihan_list,
                        "jawaban": idx_jwb,
                        "bobot": pg_bobot,
                        "tampilkan_kunci": pg_tampil,
                        "penjelasan": pg_bahas.strip()
                    })
                    st.success("✅ Soal Pilihan Ganda berhasil ditambahkan ke daftar di bawah!")

        # --- TAB 2: BUAT SOAL PERNYATAAN ---
        with tab_st:
            st_soal = st.text_area("Wacana / Pengantar Soal Pernyataan:", key="in_st_soal", placeholder="Contoh: Perhatikan data tabel berikut! Tentukan kebenaran dari tiap pernyataan di bawah ini...")
            sc1, sc2, sc3 = st.columns(3)
            model_label = sc1.selectbox(" Pasangan Opsi:", ["Benar / Salah", "Sesuai / Tidak Sesuai", "Ya / Tidak"], key="in_st_model")
            pasangan_opsi = [x.strip() for x in model_label.split("/")]
            jml_baris = int(sc2.number_input("Jumlah Baris Pernyataan:", 1, 6, 3, key="in_st_jml"))
            st_bobot = sc3.number_input("Bobot Poin Total:", 1, 100, 20, key="in_st_bobot")

            input_pernyataan = []
            for j in range(jml_baris):
                pc1, pc2 = st.columns([3, 1])
                teks_p = pc1.text_input(f"Teks Pernyataan {j+1}:", key=f"in_st_teks_{j}")
                kunci_p = pc2.selectbox(f"Kunci {j+1}:", pasangan_opsi, key=f"in_st_kunci_{j}")
                input_pernyataan.append({"teks": teks_p.strip(), "kunci": kunci_p})

            st_tampil = st.checkbox("Tampilkan kunci & pembahasan setelah siswa selesai", value=True, key="in_st_tampil")
            st_bahas = st.text_input("Pembahasan Pernyataan (Opsional):", key="in_st_bahas")

            if st.button("➕ Tambahkan Soal Pernyataan ke Daftar", type="primary"):
                if not st_soal.strip() or any(not item["teks"] for item in input_pernyataan):
                    st.warning("⚠️ Mohon lengkapi wacana soal dan seluruh baris pernyataan.")
                else:
                    draft_list.append({
                        "tipe": "pernyataan",
                        "soal": st_soal.strip(),
                        "label_opsi": pasangan_opsi,
                        "daftar_pernyataan": input_pernyataan,
                        "bobot": st_bobot,
                        "tampilkan_kunci": st_tampil,
                        "penjelasan": st_bahas.strip()
                    })
                    st.success("✅ Soal Pernyataan berhasil ditambahkan ke daftar di bawah!")

        # --- TAB 3: BUAT SOAL ESSAY / URAIAN ---
        with tab_es:
            es_soal = st.text_area("Pertanyaan Essay / Uraian:", key="in_es_soal", placeholder="Ketik soal uraian / essay di sini...")
            es_kunci_raw = st.text_input(
                "Kata / Angka Kunci Pemeriksaan Otomatis (Opsional — pisahkan dengan titik koma ';' jika ada beberapa penulisan):",
                key="in_es_kunci",
                placeholder="Contoh: 61.7 ; 61,7   (Kosongkan kotak ini jika ingin diperiksa manual oleh Guru)"
            )
            ec1, ec2 = st.columns([1, 2])
            es_bobot = ec1.number_input("Bobot Poin Essay:", 1, 100, 20, key="in_es_bobot")
            es_tampil = ec2.checkbox("Tampilkan pedoman jawaban setelah siswa submit", value=True, key="in_es_tampil")
            es_bahas = st.text_area("Kunci Penyelesaian / Pedoman Penskoran (Opsional):", key="in_es_bahas", height=80)

            if st.button("➕ Tambahkan Soal Essay ke Daftar", type="primary"):
                if not es_soal.strip():
                    st.warning("⚠️ Mohon isi teks pertanyaan essay terlebih dahulu.")
                else:
                    list_kunci = [k.strip() for k in es_kunci_raw.split(";") if k.strip()]
                    draft_list.append({
                        "tipe": "essay",
                        "soal": es_soal.strip(),
                        "kata_kunci": list_kunci,
                        "bobot": es_bobot,
                        "tampilkan_kunci": es_tampil,
                        "penjelasan": es_bahas.strip()
                    })
                    st.success("✅ Soal Essay berhasil ditambahkan ke daftar di bawah!")

        # --- DAFTAR SOAL & TOMBOL DOWNLOAD JSON ---
        st.markdown("---")
        st.markdown(f"### 3️⃣ Daftar Soal Tersusun untuk `{nama_file_target}` ({len(draft_list)} Soal)")

        if not draft_list:
            st.info("Daftar soal masih kosong. Silakan tambahkan soal melalui formulir di atas, atau klik tombol **📂 Muat Soal yang Sedang Aktif**.")
        else:
            total_bobot_draft = sum(float(x.get("bobot", 10)) for x in draft_list)
            st.caption(f"Total Bobot Keseluruhan: **{total_bobot_draft:g} poin** (Sistem otomatis mengonversi nilai akhir siswa ke skala 0–100).")

            for idx, item in enumerate(draft_list):
                tp = item.get("tipe", "pg")
                ikon_tp = {"pg": "🅰️ Pilihan Ganda", "pernyataan": "✅ Pernyataan", "essay": "✍️ Essay"}.get(tp, "Soal")
                c_teks, c_naik, c_turun, c_hapus = st.columns([6, 0.8, 0.8, 0.8])
                with c_teks:
                    ringkas = f"**{idx+1}. [{ikon_tp} • {item.get('bobot', 10)} poin]** {item['soal']}"
                    st.markdown(ringkas)
                if c_naik.button("⬆️", key=f"up_{idx}", disabled=(idx == 0)):
                    draft_list[idx-1], draft_list[idx] = draft_list[idx], draft_list[idx-1]
                    st.rerun()
                if c_turun.button("⬇️", key=f"dn_{idx}", disabled=(idx == len(draft_list)-1)):
                    draft_list[idx+1], draft_list[idx] = draft_list[idx], draft_list[idx+1]
                    st.rerun()
                if c_hapus.button("🗑️", key=f"del_{idx}"):
                    draft_list.pop(idx)
                    st.rerun()

            st.markdown("---")
            json_bytes = json.dumps(draft_list, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                label=f"⬇️ Download File Soal: {nama_file_target} (Upload File Ini ke GitHub)",
                data=json_bytes,
                file_name=nama_file_target,
                mime="application/json",
                type="primary",
                use_container_width=True
            )
