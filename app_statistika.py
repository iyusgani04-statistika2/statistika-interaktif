import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math
import random
import os
import base64

# ============================================================
# PENGATURAN JUDUL & IDENTITAS UMUM (BISA DIUBAH KAPAN SAJA)
# Bapak/Ibu cukup mengubah tulisan di dalam tanda kutip "..." di bawah ini:
# ============================================================
NAMA_APLIKASI       = "Media Pembelajaran Interaktif"
MATA_PELAJARAN      = "Matematika"
NAMA_GURU_SEKOLAH   = "Iyus Ruslan A.G,ST.,S.Pd"  # Opsional, contoh: "Oleh: Iyus Gani, S.Pd."

SUBJUDUL_BERANDA    = "Portal Belajar Mandiri, Diskusi LKPD, Simulasi & Evaluasi Siswa"
SUBJUDUL_MATERI     = "Modul Bahan Ajar & Ringkasan Konsep Pembelajaran"
SUBJUDUL_LKPD       = "Kegiatan Diskusi Kelompok & Penugasan Mandiri Peserta Didik"
SUBJUDUL_KALKULATOR = "Alat Bantu Eksplorasi Perhitungan & Visualisasi Grafik"
SUBJUDUL_QUIZ       = "Evaluasi Mandiri & Uji Pemahaman Materi Pembelajaran"

LINK_PENGUMPULAN    = "https://forms.gle/2w9YxHCiUoHpVutC7"  # Isi link Google Form jika ada pengumpulan tugas
LINK_VIDEO_YOUTUBE  = "https://www.youtube.com/watch?v=XQ8UJAMJcUQ&t=2s"  # Isi link YouTube jika ingin menampilkan video materi

# Ubah menjadi False jika sedang mengajar bab lain dan ingin menyembunyikan tab rumus Statistika
TAMPILKAN_RINGKASAN_STATISTIKA = True

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title=f"{NAMA_APLIKASI} - {MATA_PELAJARAN}",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE (Untuk Quiz & Dark Mode)
# ============================================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0

# ============================================================
# CSS TAMPILAN (Terang & Gelap)
# ============================================================
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #1a1a2e; color: #e0e0e0; }
        .main-header {
            background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
            padding: 2rem; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 2rem;
        }
        .main-header h1, .main-header p { color: white; margin: 0.3rem 0; }
        .metric-card {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;
            border-left: 5px solid #e94560; color: #e0e0e0; margin-bottom: 1rem;
        }
        .metric-card h3 { color: #e0e0e0; }
        .metric-card .value { font-size: 2rem; font-weight: bold; color: #e94560; }
        .formula-box {
            background: #0d1117; color: #7ee787; padding: 1.2rem;
            border-radius: 10px; font-family: 'Courier New', monospace;
            font-size: 1.1rem; border: 1px solid #30363d;
        }
        .step-box {
            background: #16213e; border-left: 4px solid #e94560;
            padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
            color: #e0e0e0;
        }
        .materi-box {
            background: #16213e; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #30363d; margin: 1rem 0; color: #e0e0e0;
        }
        .quiz-box {
            background: #16213e; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #30363d; margin: 1rem 0; color: #e0e0e0;
        }
        .quiz-benar { background: #1a3a1a; border: 2px solid #4caf50; padding: 1rem; border-radius: 8px; color: #4caf50; }
        .quiz-salah { background: #3a1a1a; border: 2px solid #f44336; padding: 1rem; border-radius: 8px; color: #f44336; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 2rem;
        }
        .main-header h1, .main-header p { color: white; margin: 0.3rem 0; }
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;
            border-left: 5px solid #667eea; margin-bottom: 1rem;
        }
        .metric-card h3 { color: #333; }
        .metric-card .value { font-size: 2rem; font-weight: bold; color: #667eea; }
        .formula-box {
            background: #1e1e2e; color: #a6e3a1; padding: 1.2rem;
            border-radius: 10px; font-family: 'Courier New', monospace;
            font-size: 1.1rem; border: 1px solid #45475a;
        }
        .step-box {
            background: #f0f4ff; border-left: 4px solid #667eea;
            padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
        }
        .materi-box {
            background: #f8f9ff; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #e0e4f0; margin: 1rem 0;
        }
        .quiz-box {
            background: #fffdf0; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #f0e6c0; margin: 1rem 0;
        }
        .quiz-benar { background: #e8f5e9; border: 2px solid #4caf50; padding: 1rem; border-radius: 8px; color: #2e7d32; }
        .quiz-salah { background: #ffebee; border: 2px solid #f44336; padding: 1rem; border-radius: 8px; color: #c62828; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# FUNGSI PEMISAH FILE MATERI VS LKPD & PRATINJAU PDF
# ============================================================
def adalah_file_lkpd(nama_file):
    kata_kunci_lkpd = ["lkpd", "lembar kerja", "lembar_kerja", "lks", "worksheet"]
    nama_kecil = nama_file.lower()
    return any(k in nama_kecil for k in kata_kunci_lkpd)

def tampilkan_pratinjau_pdf(isi_bytes):
    base64_pdf = base64.b64encode(isi_bytes).decode('utf-8')
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 15px;
                background-color: #525659;
                font-family: Arial, sans-serif;
                text-align: center;
            }}
            #loading-msg {{
                color: #ffffff;
                font-size: 14px;
                padding: 20px;
            }}
            .page-label {{
                color: #f0f0f0;
                font-size: 13px;
                margin: 8px 0 6px 0;
            }}
            canvas {{
                display: block;
                margin: 0 auto 20px auto;
                max-width: 100%;
                height: auto !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.45);
                border-radius: 6px;
                background-color: #ffffff;
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
                const blob = new Blob([
                    "importScripts('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js');"
                ], {{ type: 'application/javascript' }});
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
                    const loadingTask = pdfjsLib.getDocument({{ data: uint8Array }});
                    const pdf = await loadingTask.promise;
                    const container = document.getElementById('pdf-container');
                    const loadingMsg = document.getElementById('loading-msg');
                    loadingMsg.innerText = '⏳ Menampilkan ' + pdf.numPages + ' halaman...';

                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                        const page = await pdf.getPage(pageNum);
                        const scale = 1.6;
                        const viewport = page.getViewport({{ scale: scale }});

                        const label = document.createElement('div');
                        label.className = 'page-label';
                        label.innerText = 'Halaman ' + pageNum + ' dari ' + pdf.numPages;
                        container.appendChild(label);

                        const canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        container.appendChild(canvas);

                        await page.render({{
                            canvasContext: context,
                            viewport: viewport
                        }}).promise;
                    }}
                    loadingMsg.style.display = 'none';
                }} catch (err) {{
                    document.getElementById('loading-msg').innerText = '⚠️ Gagal memuat pratinjau: ' + err.message + '. Silakan gunakan tombol Download di atas.';
                }}
            }}
            renderPDF();
        </script>
    </body>
    </html>
    """
    components.html(pdf_html, height=650, scrolling=True)

# ============================================================
# FUNGSI PERHITUNGAN
# ============================================================
def buat_distribusi_frekuensi(data, jumlah_kelas):
    data = sorted(data)
    data_min, data_max = min(data), max(data)
    jangkauan = data_max - data_min
    panjang_kelas = max(1, math.ceil(jangkauan / jumlah_kelas))
    tabel = []
    batas_bawah = data_min
    for i in range(jumlah_kelas):
        batas_atas = batas_bawah + panjang_kelas - 1
        tepi_bawah = batas_bawah - 0.5
        tepi_atas = batas_atas + 0.5
        titik_tengah = (batas_bawah + batas_atas) / 2
        if i == jumlah_kelas - 1:
            frekuensi = sum(1 for d in data if d >= batas_bawah)
        else:
            frekuensi = sum(1 for d in data if batas_bawah <= d <= batas_atas)
        tabel.append({
            'No': i + 1,
            'Kelas': f"{batas_bawah:.0f} - {batas_atas:.0f}",
            'Tepi': f"{tepi_bawah:.1f} - {tepi_atas:.1f}",
            'xi': titik_tengah,
            'fi': frekuensi,
            'fi_xi': frekuensi * titik_tengah,
            'Tepi Bawah': tepi_bawah,
            'Tepi Atas': tepi_atas,
        })
        batas_bawah = batas_atas + 1
    fk = 0
    for row in tabel:
        fk += row['fi']
        row['Fk'] = fk
    return pd.DataFrame(tabel), panjang_kelas

def hitung_mean(df):
    return df['fi_xi'].sum() / df['fi'].sum() if df['fi'].sum() > 0 else 0

def hitung_modus(df):
    idx = df['fi'].idxmax()
    row = df.loc[idx]
    p = row['Tepi Atas'] - row['Tepi Bawah']
    Tb = row['Tepi Bawah']
    f_sebelum = df.loc[idx - 1, 'fi'] if idx > 0 else 0
    f_sesudah = df.loc[idx + 1, 'fi'] if idx < len(df) - 1 else 0
    d1 = row['fi'] - f_sebelum
    d2 = row['fi'] - f_sesudah
    if d1 + d2 == 0:
        return Tb + p * 0.5, Tb, p, d1, d2, row
    return Tb + p * (d1 / (d1 + d2)), Tb, p, d1, d2, row

def hitung_median(df):
    n = df['fi'].sum()
    setengah_n = n / 2
    for idx, row in df.iterrows():
        if row['Fk'] >= setengah_n:
            p = row['Tepi Atas'] - row['Tepi Bawah']
            Tb = row['Tepi Bawah']
            Fk_sebelum = df.loc[idx - 1, 'Fk'] if idx > 0 else 0
            fi = row['fi']
            median = Tb + p * ((setengah_n - Fk_sebelum) / fi)
            return median, Tb, p, setengah_n, Fk_sebelum, fi, row
    return 0, 0, 0, 0, 0, 0, None

# ============================================================
# SIDEBAR NAVIGASI (UMUM)
# ============================================================
with st.sidebar:
    st.markdown(f"## 🎓 {MATA_PELAJARAN} Interaktif")
    if NAMA_GURU_SEKOLAH.strip():
        st.caption(NAMA_GURU_SEKOLAH)
    st.markdown("---")

    if st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False
    st.markdown("---")

    halaman = st.radio(
        "📌 Pilih Menu Belajar:",
        ["🏠 Beranda", "📖 Materi", "📄 LKPD", "🧮 Kalkulator", "📝 Quiz"],
        index=0
    )
    st.markdown("---")
    st.markdown("### ℹ️ Tentang Portal")
    st.markdown(f"""
    **{NAMA_APLIKASI} {MATA_PELAJARAN}** untuk mendukung kegiatan belajar siswa secara interaktif, mandiri, maupun berkelompok.
    """)

# ============================================================
# HALAMAN BERANDA
# ============================================================
if halaman == "🏠 Beranda":
    info_guru_html = f"<p style='font-size:0.95rem; opacity:0.9;'>{NAMA_GURU_SEKOLAH}</p>" if NAMA_GURU_SEKOLAH.strip() else ""
    st.markdown(f"""
    <div class="main-header">
        <h1>🎓 Selamat Datang!</h1>
        <p>{NAMA_APLIKASI} {MATA_PELAJARAN} — {SUBJUDUL_BERANDA}</p>
        {info_guru_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Menu Pembelajaran yang Tersedia")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📖 Materi</h3>
            <p>Pelajari modul bahan ajar guru & ringkasan konsep materi pembelajaran.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📄 LKPD</h3>
            <p>Baca & unduh Lembar Kerja Peserta Didik serta kumpulkan tugas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🧮 Kalkulator</h3>
            <p>Simulasi eksplorasi perhitungan & visualisasi grafik secara otomatis.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📝 Quiz</h3>
            <p>Uji pemahamanmu dengan latihan soal interaktif dan lihat skormu!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Petunjuk Penggunaan")
    st.markdown("""
    1. 👈 Buka **panel menu di kiri** (klik tanda panah `>>` di pojok kiri atas jika memakai HP)
    2. 📖 Pilih **Materi** untuk membaca bahan ajar dan konsep rumus
    3. 📄 Pilih **LKPD** untuk melihat & mengunduh lembar kerja siswa
    4. 🧮 Pilih **Kalkulator** untuk mencoba simulasi perhitungan & grafik
    5. 📝 Pilih **Quiz** untuk mengerjakan latihan evaluasi mandiri
    """)

# ============================================================
# HALAMAN MATERI
# ============================================================
elif halaman == "📖 Materi":
    st.markdown(f"""
    <div class="main-header">
        <h1>📖 Materi Pembelajaran</h1>
        <p>{SUBJUDUL_MATERI}</p>
    </div>
    """, unsafe_allow_html=True)

    ekstensi_materi = (".pdf", ".pptx", ".ppt", ".docx", ".doc", ".png", ".jpg", ".jpeg")
    daftar_materi_guru = sorted([
        f for f in os.listdir(".")
        if f.lower().endswith(ekstensi_materi) and not adalah_file_lkpd(f)
    ])

    def render_bahan_ajar_guru():
        if LINK_VIDEO_YOUTUBE.strip():
            st.markdown("### 🎬 Video Pembelajaran")
            st.video(LINK_VIDEO_YOUTUBE.strip())
            st.markdown("---")

        st.markdown("### 📚 Modul & Bahan Ajar")
        if not daftar_materi_guru:
            st.info(
                "ℹ️ Saat ini belum ada file modul tambahan yang diunggah. "
                "Silakan pelajari ringkasan konsep pada tab materi yang tersedia."
            )
        else:
            for idx, nama_file in enumerate(daftar_materi_guru):
                with open(nama_file, "rb") as file_data:
                    isi_bytes = file_data.read()

                nama_kecil = nama_file.lower()
                if nama_kecil.endswith(".pdf"):
                    ikon, mime_type = "📕", "application/pdf"
                elif nama_kecil.endswith((".pptx", ".ppt")):
                    ikon, mime_type = "📙", "application/octet-stream"
                elif nama_kecil.endswith((".png", ".jpg", ".jpeg")):
                    ikon, mime_type = "🖼️", "image/png"
                else:
                    ikon, mime_type = "📘", "application/octet-stream"

                col_nama, col_unduh = st.columns([3, 1])
                with col_nama:
                    st.markdown(f"#### {ikon} {nama_file}")
                with col_unduh:
                    st.download_button(
                        label="⬇️ Download Materi",
                        data=isi_bytes,
                        file_name=nama_file,
                        mime=mime_type,
                        key=f"unduh_materi_{idx}",
                        use_container_width=True,
                        type="primary"
                    )

                if nama_kecil.endswith(".pdf"):
                    with st.expander(f"👁️ Baca Materi {nama_file} di Layar", expanded=True):
                        tampilkan_pratinjau_pdf(isi_bytes)
                elif nama_kecil.endswith((".png", ".jpg", ".jpeg")):
                    st.image(isi_bytes, caption=nama_file, use_container_width=True)

                st.markdown("---")

    if TAMPILKAN_RINGKASAN_STATISTIKA:
        materi_tab0, materi_tab1, materi_tab2, materi_tab3, materi_tab4 = st.tabs([
            "📚 Bahan Ajar Guru", "📌 Pengantar", "📈 Rata-rata", "🏔️ Modus", "📏 Median"
        ])

        with materi_tab0:
            render_bahan_ajar_guru()

        with materi_tab1:
            st.markdown("### Apa itu Data Kelompok?")
            st.markdown("""
            <div class="materi-box">
            <b>Data kelompok</b> adalah data yang disajikan dalam bentuk
            <b>kelas-kelas interval</b>, bukan data individual satu per satu.<br><br>
            Data kelompok digunakan ketika jumlah data cukup banyak sehingga
            lebih praktis disajikan dalam bentuk tabel distribusi frekuensi.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Istilah Penting")
            st.markdown("""
            | Istilah | Simbol | Keterangan |
            |---------|--------|------------|
            | Frekuensi | fi | Banyaknya data dalam setiap kelas |
            | Titik Tengah | xi | Nilai tengah setiap kelas = (batas bawah + batas atas) / 2 |
            | Tepi Bawah | Tb | Batas bawah - 0.5 |
            | Tepi Atas | Ta | Batas atas + 0.5 |
            | Panjang Kelas | p | Selisih tepi atas dan tepi bawah |
            | Frekuensi Kumulatif | Fk | Jumlah frekuensi dari kelas pertama sampai kelas tertentu |
            """)

            st.markdown("### Aturan Sturges")
            st.markdown("""
            <div class="materi-box">
            Untuk menentukan <b>jumlah kelas</b>, digunakan rumus:<br><br>
            <b>k = 1 + 3,322 × log(n)</b><br><br>
            Dimana <b>n</b> = jumlah data.<br>
            <b>Contoh:</b> Jika n = 30, maka k = 1 + 3,322 × log(30) = 1 + 4,91 = 5,91 ≈ 6 kelas
            </div>
            """, unsafe_allow_html=True)

        with materi_tab2:
            st.markdown("### 📈 Rata-rata (Mean) Data Kelompok")
            st.markdown('<div class="formula-box">x̄ = Σ(fi × xi) / Σfi</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="materi-box">
            <b>Langkah-langkah:</b><br>
            1. Tentukan titik tengah (xi) setiap kelas: xi = (batas bawah + batas atas) / 2<br>
            2. Kalikan frekuensi dengan titik tengah (fi × xi)<br>
            3. Jumlahkan semua fi × xi → Σ(fi × xi)<br>
            4. Bagi Σ(fi × xi) dengan total frekuensi (Σfi)
            </div>
            """, unsafe_allow_html=True)

        with materi_tab3:
            st.markdown("### 🏔️ Modus Data Kelompok")
            st.markdown('<div class="formula-box">Mo = Tb + p × (d1 / (d1 + d2))</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="materi-box">
            <b>Keterangan:</b><br>
            • <b>Tb</b> = Tepi bawah kelas modus (kelas dengan frekuensi paling tinggi)<br>
            • <b>p</b> = Panjang kelas<br>
            • <b>d1</b> = Selisih frekuensi kelas modus dengan kelas <b>sebelumnya</b><br>
            • <b>d2</b> = Selisih frekuensi kelas modus dengan kelas <b>sesudahnya</b>
            </div>
            """, unsafe_allow_html=True)

        with materi_tab4:
            st.markdown("### 📏 Median Data Kelompok")
            st.markdown('<div class="formula-box">Me = Tb + p × ((½n - Fk) / fi)</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="materi-box">
            <b>Keterangan:</b><br>
            • <b>½n</b> = Setengah dari jumlah total data<br>
            • <b>Kelas Median</b> = Kelas pertama yang nilai Fk-nya ≥ ½n<br>
            • <b>Tb</b> = Tepi bawah kelas median<br>
            • <b>p</b> = Panjang kelas<br>
            • <b>Fk</b> = Frekuensi kumulatif <b>sebelum</b> kelas median<br>
            • <b>fi</b> = Frekuensi pada kelas median
            </div>
            """, unsafe_allow_html=True)
    else:
        render_bahan_ajar_guru()

# ============================================================
# HALAMAN LKPD
# ============================================================
elif halaman == "📄 LKPD":
    st.markdown(f"""
    <div class="main-header">
        <h1>📄 Lembar Kerja Peserta Didik (LKPD)</h1>
        <p>{SUBJUDUL_LKPD}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="materi-box">
        <b>📋 Petunjuk Pengerjaan LKPD:</b><br>
        1. Baca pratinjau LKPD di layar atau unduh filenya melalui tombol <b>Download LKPD</b>.<br>
        2. Kerjakan secara mandiri/berkelompok sesuai instruksi Bapak/Ibu Guru.<br>
        3. Gunakan menu <b>🧮 Kalkulator</b> jika ingin memverifikasi hasil perhitunganmu.<br>
        4. Kumpulkan hasil pekerjaan sesuai arahan Guru.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📥 Daftar File LKPD")

    daftar_lkpd = sorted([
        f for f in os.listdir(".")
        if f.lower().endswith((".pdf", ".docx", ".doc")) and adalah_file_lkpd(f)
    ])

    if not daftar_lkpd:
        st.info("ℹ️ Belum ada file LKPD yang diunggah (Pastikan nama file mengandung kata 'LKPD' atau 'Lembar Kerja').")
    else:
        for idx, nama_file in enumerate(daftar_lkpd):
            with open(nama_file, "rb") as file_data:
                isi_bytes = file_data.read()

            ikon = "📕" if nama_file.lower().endswith(".pdf") else "📘"
            col_nama, col_unduh = st.columns([3, 1])

            with col_nama:
                st.markdown(f"#### {ikon} {nama_file}")
            with col_unduh:
                st.download_button(
                    label="⬇️ Download LKPD",
                    data=isi_bytes,
                    file_name=nama_file,
                    mime="application/pdf" if nama_file.lower().endswith(".pdf") else "application/octet-stream",
                    key=f"unduh_lkpd_{idx}",
                    use_container_width=True,
                    type="primary"
                )

            if nama_file.lower().endswith(".pdf"):
                with st.expander(f"👁️ Lihat Pratinjau {nama_file} di Layar", expanded=True):
                    tampilkan_pratinjau_pdf(isi_bytes)
            st.markdown("---")

    if LINK_PENGUMPULAN.strip():
        st.markdown("### 📤 Pengumpulan Hasil Kerja Siswa")
        st.markdown("Sudah selesai mengerjakan LKPD? Silakan kirim hasil pekerjaanmu melalui tombol di bawah ini:")
        st.link_button("📤 Kumpulkan Tugas / Jawaban LKPD", LINK_PENGUMPULAN, type="primary")

# ============================================================
# HALAMAN KALKULATOR
# ============================================================
elif halaman == "🧮 Kalkulator":
    st.markdown(f"""
    <div class="main-header">
        <h1>🧮 Simulasi & Kalkulator Interaktif</h1>
        <p>{SUBJUDUL_KALKULATOR}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📥 Input Data Simulasi")
        input_method = st.radio(
            "Pilih cara input:",
            ["Contoh data otomatis", "Ketik manual", "Upload file CSV"],
            index=0, key="kalk_input"
        )
        data = []
        if input_method == "Ketik manual":
            raw = st.text_area(
                "Masukkan angka (pisah koma/spasi):",
                value="45, 50, 55, 60, 65, 70, 75, 48, 52, 58",
                height=100, key="kalk_text"
            )
            raw = raw.replace(",", " ")
            try:
                data = [float(x) for x in raw.split() if x.strip()]
            except:
                st.error("⚠️ Format data tidak valid!")
        elif input_method == "Contoh data otomatis":
            contoh = st.selectbox("Pilih dataset:", [
                "Nilai Ujian (30 siswa)",
                "Tinggi Badan (25 siswa)",
                "Berat Badan (20 siswa)",
            ], key="kalk_contoh")
            if "Nilai" in contoh:
                data = [45,50,55,60,65,70,75,48,52,58,62,68,72,78,53,57,63,67,73,77,49,54,59,64,69,74,51,56,61,66]
            elif "Tinggi" in contoh:
                data = [150,155,158,160,162,163,165,165,167,168,170,170,172,173,175,155,160,163,166,169,171,174,152,157,164]
            else:
                data = [45,48,50,52,55,56,58,60,62,63,65,67,68,70,72,55,58,61,64,69]
        elif input_method == "Upload file CSV":
            uploaded = st.file_uploader("Upload file .csv", type=["csv"], key="kalk_upload")
            if uploaded:
                df_upload = pd.read_csv(uploaded)
                col = st.selectbox("Pilih kolom:", df_upload.columns, key="kalk_col")
                data = df_upload[col].dropna().tolist()

        st.markdown("---")
        if data:
            n = len(data)
            k_default = math.ceil(1 + 3.322 * math.log10(n))
            jumlah_kelas = st.slider(
                "Jumlah kelas:", 3, 15, k_default, key="kalk_slider"
            )
            st.markdown(f"**n:** {n} | **Min:** {min(data)} | **Max:** {max(data)}")

    if not data:
        st.warning("👈 Masukkan data di panel kiri.")
        st.stop()

    df_tabel, panjang_kelas = buat_distribusi_frekuensi(data, jumlah_kelas)
    mean_val = hitung_mean(df_tabel)
    modus_val, Tb_mo, p_mo, d1, d2, row_mo = hitung_modus(df_tabel)
    median_val, Tb_me, p_me, half_n, Fk_me, fi_me, row_me = hitung_median(df_tabel)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>📈 Rata-rata</h3><div class="value">{mean_val:.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>🏔️ Modus</h3><div class="value">{modus_val:.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>📏 Median</h3><div class="value">{median_val:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    ktab1, ktab2, ktab3, ktab4, ktab5 = st.tabs([
        "📋 Tabel", "📈 Mean", "🏔️ Modus", "📏 Median", "📊 Grafik"
    ])

    with ktab1:
        st.markdown("### Tabel Distribusi Frekuensi")
        df_display = df_tabel[['No', 'Kelas', 'Tepi', 'xi', 'fi', 'fi_xi', 'Fk']].copy()
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with ktab2:
        st.markdown("### Perhitungan Rata-rata")
        st.markdown('<div class="formula-box">x̄ = Σ(fi × xi) / Σfi</div>', unsafe_allow_html=True)
        for _, row in df_tabel.iterrows():
            st.markdown(f'<div class="step-box">Kelas <b>{row["Kelas"]}</b>: {row["fi"]} × {row["xi"]:.1f} = <b>{row["fi_xi"]:.1f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-box"><b>x̄ = {df_tabel["fi_xi"].sum():.1f} / {df_tabel["fi"].sum()} = {mean_val:.2f}</b></div>', unsafe_allow_html=True)

    with ktab3:
        st.markdown("### Perhitungan Modus")
        st.markdown('<div class="formula-box">Mo = Tb + p × (d1 / (d1 + d2))</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-box">
        Kelas Modus: <b>{row_mo['Kelas']}</b> (fi = {row_mo['fi']})<br>
        Tb = {Tb_mo:.1f} | p = {p_mo:.1f} | d1 = {d1} | d2 = {d2}<br><br>
        Mo = {Tb_mo:.1f} + {p_mo:.1f} × ({d1} / {d1 + d2})<br>
        <b>Mo = {modus_val:.2f}</b>
        </div>
        """, unsafe_allow_html=True)

    with ktab4:
        st.markdown("### Perhitungan Median")
        st.markdown('<div class="formula-box">Me = Tb + p × ((½n - Fk) / fi)</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="step-box">
        Kelas Median: <b>{row_me['Kelas']}</b> (Fk pertama ≥ {half_n:.1f})<br>
        Tb = {Tb_me:.1f} | p = {p_me:.1f} | ½n = {half_n:.1f} | Fk = {Fk_me} | fi = {fi_me}<br><br>
        Me = {Tb_me:.1f} + {p_me:.1f} × (({half_n:.1f} - {Fk_me}) / {fi_me})<br>
        <b>Me = {median_val:.2f}</b>
        </div>
        """, unsafe_allow_html=True)

    with ktab5:
        st.markdown("### 📊 Visualisasi Grafik")
        gc1, gc2 = st.columns(2)
        with gc1:
            fig_hist = px.bar(df_tabel, x='Kelas', y='fi', title="Histogram",
                              color='fi', color_continuous_scale='Blues',
                              labels={'fi': 'Frekuensi', 'Kelas': 'Kelas'})
            fig_hist.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig_hist, use_container_width=True)
        with gc2:
            fig_ogive = go.Figure()
            fig_ogive.add_trace(go.Scatter(
                x=df_tabel['Tepi Atas'], y=df_tabel['Fk'],
                mode='lines+markers', name='Ogive',
                line=dict(color='#667eea', width=3), marker=dict(size=8)
            ))
            fig_ogive.update_layout(title="Ogive", xaxis_title="Tepi Atas", yaxis_title="Fk")
            st.plotly_chart(fig_ogive, use_container_width=True)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=['Mean', 'Median', 'Modus'],
            y=[mean_val, median_val, modus_val],
            marker_color=['#667eea', '#764ba2', '#f093fb'],
            text=[f"{mean_val:.2f}", f"{median_val:.2f}", f"{modus_val:.2f}"],
            textposition='auto'
        ))
        fig_comp.update_layout(title="Perbandingan Mean, Median, Modus")
        st.plotly_chart(fig_comp, use_container_width=True)

# ============================================================
# HALAMAN QUIZ
# ============================================================
elif halaman == "📝 Quiz":
    st.markdown(f"""
    <div class="main-header">
        <h1>📝 Quiz Interaktif</h1>
        <p>{SUBJUDUL_QUIZ}</p>
    </div>
    """, unsafe_allow_html=True)

    soal_bank = [
        {
            "soal": "Rumus rata-rata (mean) data kelompok adalah...",
            "pilihan": [
                "x̄ = Σfi / Σxi",
                "x̄ = Σ(fi × xi) / Σfi",
                "x̄ = Σfi × Σxi",
                "x̄ = Σxi / n"
            ],
            "jawaban": 1,
            "penjelasan": "Rata-rata data kelompok = jumlah (fi × xi) dibagi jumlah fi."
        },
        {
            "soal": "Tepi bawah kelas 50 - 59 adalah...",
            "pilihan": ["49", "49.5", "50", "50.5"],
            "jawaban": 1,
            "penjelasan": "Tepi bawah = batas bawah - 0.5 = 50 - 0.5 = 49.5"
        },
        {
            "soal": "Titik tengah (xi) dari kelas 60 - 69 adalah...",
            "pilihan": ["64", "64.5", "65", "65.5"],
            "jawaban": 1,
            "penjelasan": "xi = (60 + 69) / 2 = 129 / 2 = 64.5"
        },
        {
            "soal": "Kelas modus adalah kelas yang memiliki...",
            "pilihan": [
                "Frekuensi terkecil",
                "Frekuensi terbesar",
                "Nilai tengah terbesar",
                "Tepi bawah terkecil"
            ],
            "jawaban": 1,
            "penjelasan": "Kelas modus = kelas dengan frekuensi tertinggi."
        },
        {
            "soal": "Dalam rumus modus Mo = Tb + p × (d1/(d1+d2)), d1 adalah...",
            "pilihan": [
                "Selisih fi modus dengan fi kelas sesudahnya",
                "Selisih fi modus dengan fi kelas sebelumnya",
                "Frekuensi kumulatif",
                "Panjang kelas"
            ],
            "jawaban": 1,
            "penjelasan": "d1 = fi kelas modus - fi kelas sebelumnya."
        },
        {
            "soal": "Median data kelompok terletak di kelas yang Fk-nya pertama kali...",
            "pilihan": [
                "Lebih dari n",
                "Lebih dari atau sama dengan ½n",
                "Sama dengan n",
                "Kurang dari ½n"
            ],
            "jawaban": 1,
            "penjelasan": "Kelas median = kelas pertama dengan Fk ≥ ½n."
        },
        {
            "soal": "Jika n = 40, maka ½n untuk mencari median adalah...",
            "pilihan": ["10", "15", "20", "25"],
            "jawaban": 2,
            "penjelasan": "½n = ½ × 40 = 20."
        },
        {
            "soal": "Aturan Sturges untuk menentukan jumlah kelas adalah...",
            "pilihan": [
                "k = 1 + 3.322 × n",
                "k = 1 + 3.322 × log(n)",
                "k = n / 2",
                "k = √n"
            ],
            "jawaban": 1,
            "penjelasan": "Aturan Sturges: k = 1 + 3.322 × log(n)."
        },
        {
            "soal": "Panjang kelas dihitung dengan rumus...",
            "pilihan": [
                "p = jangkauan × jumlah kelas",
                "p = jangkauan / jumlah kelas",
                "p = jumlah kelas / jangkauan",
                "p = data max + data min"
            ],
            "jawaban": 1,
            "penjelasan": "Panjang kelas = jangkauan (R) / jumlah kelas (k)."
        },
        {
            "soal": "Frekuensi kumulatif (Fk) adalah...",
            "pilihan": [
                "Frekuensi terbesar",
                "Jumlah frekuensi dari kelas pertama sampai kelas tertentu",
                "Frekuensi kelas terakhir",
                "Selisih frekuensi antar kelas"
            ],
            "jawaban": 1,
            "penjelasan": "Fk = penjumlahan frekuensi secara bertahap dari kelas pertama."
        }
    ]

    random.seed(42)
    soal_terpilih = random.sample(soal_bank, 5)

    st.markdown("### 📋 Jawab 5 soal berikut ini!")
    st.markdown("Pilih jawaban yang paling tepat, lalu klik **Cek Jawaban** di bawah.")
    st.markdown("---")

    for i, soal in enumerate(soal_terpilih):
        st.markdown(f"""
        <div class="quiz-box">
        <b>Soal {i+1}:</b> {soal['soal']}
        </div>
        """, unsafe_allow_html=True)

        jawaban_user = st.radio(
            f"Pilihan jawaban soal {i+1}:",
            soal['pilihan'],
            key=f"soal_{i}",
            index=None
        )

        if st.session_state.quiz_submitted:
            if jawaban_user == soal['pilihan'][soal['jawaban']]:
                st.markdown(f'<div class="quiz-benar">✅ Benar! {soal["penjelasan"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="quiz-salah">❌ Salah. Jawaban yang benar: <b>{soal["pilihan"][soal["jawaban"]]}</b><br>{soal["penjelasan"]}</div>', unsafe_allow_html=True)

        st.markdown("---")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Cek Jawaban", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            skor = 0
            for i, soal in enumerate(soal_terpilih):
                jawaban_user = st.session_state.get(f"soal_{i}", None)
                if jawaban_user == soal['pilihan'][soal['jawaban']]:
                    skor += 1
            st.session_state.quiz_score = skor
            st.rerun()

    with col_btn2:
        if st.button("🔄 Ulangi Quiz", use_container_width=True):
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_answers = {}
            st.rerun()

    if st.session_state.quiz_submitted:
        skor = st.session_state.quiz_score
        total = len(soal_terpilih)
        persen = (skor / total) * 100

        if persen == 100:
            emoji = "🏆"
            pesan = "SEMPURNA! Kamu luar biasa!"
        elif persen >= 80:
            emoji = "🌟"
            pesan = "Hebat! Kamu sudah sangat paham!"
        elif persen >= 60:
            emoji = "👍"
            pesan = "Bagus! Terus belajar ya!"
        elif persen >= 40:
            emoji = "📖"
            pesan = "Cukup baik. Coba baca lagi materinya."
        else:
            emoji = "💪"
            pesan = "Jangan menyerah! Pelajari materinya lagi ya."

        st.markdown(f"""
        <div class="metric-card" style="margin-top: 1rem;">
            <h3>{emoji} Skor Quiz Kamu</h3>
            <div class="value">{skor} / {total}</div>
            <p style="font-size: 1.2rem;">{pesan}</p>
            <p>Nilai: <b>{persen:.0f}</b> / 100</p>
        </div>
        """, unsafe_allow_html=True)
