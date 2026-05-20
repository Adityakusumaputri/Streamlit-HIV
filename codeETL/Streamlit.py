import streamlit as st
from streamlit_option_menu import option_menu
import os
import pandas as pd
import subprocess
from ETL_STREAMLIT import run_etl  # Pastikan file ini ada

# ================================
# 🔹 Konfigurasi
# ================================
st.set_page_config(page_title="PORTAL DATA HIV SURABAYA", layout="wide")

# Path yang dapat dikonfigurasi (update sesuai kebutuhan)
LOGO_PATH = "logo.png"  # Ganti dengan path logo yang benar
BACKGROUND_URL = "https://your-image-url.com/your-background-image.jpg"  # Ganti dengan URL gambar nyata atau path lokal
INPUT_FOLDER = "inputan_data"

# ================================
# 🔹 CSS Styling
# ================================
st.markdown(f"""
    <style>
    .stApp {{
        background: url('{BACKGROUND_URL}') no-repeat center center fixed;
        background-size: cover;
    }}
    .sidebar .sidebar-content {{
        background-color: #f0f4f7;
        padding: 20px;
        border-radius: 8px;
    }}
    .header {{
        background: linear-gradient(45deg, #6bb9f0, #4caf50);
        padding: 20px;
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-size: 36px;
        font-weight: bold;
        color: #ffffff;
        border-radius: 8px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# ================================
# 🔹 Logo dan Menu Sidebar
# ================================
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=500)  # Ukuran dikurangi untuk pas di sidebar
else:
    st.sidebar.warning("File logo tidak ditemukan. Silakan tambahkan 'logo.png' ke direktori.")

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Tambah Data", "Lihat Visualisasi", "Tentang"],
        icons=["cloud-upload", "bar-chart-line", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f0f4f7"},
            "icon": {"color": "#4CAF50", "font-size": "22px"},
            "nav-link": {
                "font-size": "16px", "text-align": "left", "margin": "10px", "color": "#333"},
            "nav-link-selected": {"background-color": "#0288d1", "color": "white"},
        }
    )

# ================================
# 🔹 Header
# ================================
st.markdown('<div class="header">SELAMAT DATANG, DI PORTAL DATA HIV SURABAYA</div>', unsafe_allow_html=True)

# ================================
# 🔹 Halaman: Tambah Data
# ================================
if selected == "Tambah Data":
    st.subheader("📂 Silahkan Upload Data HIV Surabaya Baru Anda")

    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

    if uploaded_file is not None:
        os.makedirs(INPUT_FOLDER, exist_ok=True)
        save_path = os.path.join(INPUT_FOLDER, uploaded_file.name)

        try:
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            df = pd.read_excel(save_path)
            st.write("📊 Preview data:")
            st.dataframe(df)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Simpan Saja"):
                    st.success(f"✅ File berhasil disimpan sementara: {save_path}")
                    st.session_state["last_saved_file"] = save_path

            with col2:
                if st.button("⚡ Jalankan ETL"):
                    try:
                        output_file = run_etl(save_path)
                        st.success("🚀 Proses ETL berhasil dijalankan!")
                        st.info(f"✅ Data master berhasil diperbarui: {output_file}")
                        st.session_state["etl_success"] = True
                        st.session_state["etl_file_path"] = output_file
                    except Exception as e:
                        st.error(f"❌ Gagal menjalankan ETL: {str(e)}")
                        st.session_state["etl_success"] = False

            if st.session_state.get("etl_success", False):
                if st.button("💾 Load ke Database"):
                    try:
                        result_load = subprocess.run(
                            ["python", "load.py", st.session_state["etl_file_path"]],
                            capture_output=True,
                            text=True,
                            encoding="utf-8"
                        )
                        if result_load.returncode == 0:
                            st.success("✅ Data berhasil dimasukkan ke database!")
                            st.text(result_load.stdout)
                        else:
                            st.error("❌ Terjadi error saat load ke database.")
                            st.text(result_load.stderr)
                    except Exception as e:
                        st.error(f"Gagal load ke database: {str(e)}")
        except Exception as e:
            st.error(f"Error memproses file: {str(e)}")

# ================================
# 🔹 Halaman: Lihat Visualisasi
# ================================
elif selected == "Lihat Visualisasi":
    st.subheader("📊 Silahkan Kunjungi Visualisasi Data HIV Surabaya")
    powerbi_url = "https://app.powerbi.com/groups/me/reports/91b4a222-8dfc-4ba4-975f-51db712c3e01/1bbc63950dc702b41c2a?experience=power-bi"
    st.markdown(f'<a href="{powerbi_url}" target="_blank">👉 Buka Visualisasi Power BI</a>', unsafe_allow_html=True)

# ================================
# 🔹 Halaman: Tentang
# ================================
elif selected == "Tentang":
    st.subheader("ℹ️ Tentang Portal Data HIV Surabaya")
    st.markdown("""
        <div class="about-section">
        <h3>🌐 Portal Data HIV Surabaya – Analisis Data HIV di Surabaya 2025</h3>
        <p>Portal ini merupakan sistem <strong>Business Intelligence</strong> yang dibuat untuk mendukung analisis dan visualisasi data <strong>HIV di Surabaya</strong>.</p>
        <p><strong>Fitur yang tersedia:</strong></p>
        <ul>
            <li>➕ <strong>Tambah Data</strong> → Mengunggah dan memperbarui data HIV</li>
            <li>📊 <strong>Lihat Visualisasi</strong> → Melihat grafik, peta, dan laporan interaktif melalui Power BI</li>
        </ul>
        <p>Dengan adanya portal ini, pengguna diharapkan dapat:</p>
        <ul>
            <li>Memantau tren penanggulangan HIV di Surabaya</li>
            <li>Mendukung pengambilan keputusan yang cepat dan berbasis data</li>
            <li>Memberikan wawasan yang bermanfaat bagi masyarakat dan instansi terkait</li>
        </ul>
        <p><em>Dibangun menggunakan Python & Streamlit sebagai bagian dari implementasi Business Intelligence.</em></p>
        </div>
    """, unsafe_allow_html=True)