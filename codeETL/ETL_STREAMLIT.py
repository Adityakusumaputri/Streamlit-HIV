import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine
import logging
import shutil  # Untuk copy file backup

# ================================
# KONFIGURASI LOGGING
# ================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ================================
# KONFIGURASI FOLDER
# ================================
MASTER_FOLDER = "master_data"  # Folder utama untuk file master
BACKUP_FOLDER = os.path.join(MASTER_FOLDER, "backup")  # Subfolder untuk backup

# Pastikan folder ada
os.makedirs(MASTER_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ================================
# KONFIGURASI DATABASE
# ================================
def create_connection():
    """
    Membuat koneksi ke database PostgreSQL menggunakan SQLAlchemy.
    Menggunakan variabel lingkungan untuk keamanan.
    """
    try:
        db_user = os.environ.get('DB_USER', 'username')
        db_password = os.environ.get('DB_PASSWORD', 'password')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'your_database')
        
        db_url = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        engine = create_engine(db_url)
        logging.info("Koneksi database berhasil dibuat.")
        return engine
    except Exception as e:
        logging.error(f"Gagal membuat koneksi database: {e}")
        raise

# ================================
# BACKUP DATA MASTER
# ================================
def backup_master(master_file):
    """
    Buat backup file master sebelum digabungkan.
    Backup disimpan di folder backup dengan timestamp.
    """
    try:
        if os.path.exists(master_file):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"{os.path.splitext(os.path.basename(master_file))[0]}_backup_{timestamp}.xlsx"
            backup_path = os.path.join(BACKUP_FOLDER, backup_filename)
            shutil.copy2(master_file, backup_path)  # Copy file dengan metadata
            logging.info(f"Backup berhasil dibuat: {backup_path}")
        else:
            logging.info(f"File master {master_file} tidak ada, tidak perlu backup.")
    except Exception as e:
        logging.error(f"Error saat membuat backup: {e}")
        raise

# ================================
# TRANSFORMASI DATA (tetap sama)
# ================================
def transform_jeniskelamin(df):
    """Transform data jenis kelamin"""
    try:
        logging.info("Transform jenis kelamin...")
        if len(df) < 2:
            raise ValueError("Data tidak cukup untuk transformasi (minimal 2 baris).")
        
        header = df.iloc[0]
        data = df.iloc[1:].copy()
        data.columns = ["Tahun", header.iloc[1] if len(header) > 1 else "Laki-laki", header.iloc[2] if len(header) > 2 else "Perempuan"]
        
        data["Tahun"] = data["Tahun"].astype(str).str.replace("2025 (hingga bulan Juli)", "2025", regex=False)
        data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")
        
        kolom_angka = data.columns.drop("Tahun")
        data[kolom_angka] = data[kolom_angka].apply(pd.to_numeric, errors="coerce")
        
        data = data[data["Tahun"].notna()].reset_index(drop=True)
        logging.info(f"{len(data)} baris berhasil di-transform untuk jenis kelamin.")
        return data
    except Exception as e:
        logging.error(f"Error transform_jeniskelamin: {e}")
        raise

def transform_statuspasien(df):
    """Transform data status pasien"""
    try:
        logging.info("Transform status pasien...")
        if len(df.columns) < 3:
            raise ValueError("Data tidak memiliki cukup kolom untuk status pasien.")
        
        data = df.copy()
        data.columns = ["Tahun", "Hidup", "Meninggal"]
        
        data["Tahun"] = data["Tahun"].astype(str).str.replace("2025 (hingga bulan Juli)", "2025", regex=False)
        data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")
        
        data[["Hidup", "Meninggal"]] = data[["Hidup", "Meninggal"]].apply(pd.to_numeric, errors="coerce")
        
        data = data[data["Tahun"].notna()].reset_index(drop=True)
        logging.info(f"{len(data)} baris berhasil di-transform untuk status pasien.")
        return data
    except Exception as e:
        logging.error(f"Error transform_statuspasien: {e}")
        raise

# ================================
# DETEKSI JENIS DATA (tetap sama)
# ================================
def detect_data_type(df):
    """Auto-detect jenis data berdasarkan kolom pertama dan isi data"""
    try:
        logging.info("Mendeteksi jenis data...")
        if df.empty:
            logging.warning("Data kosong, menggunakan default.")
            return 'default'
        
        first_col = str(df.columns[0]).lower()
        logging.info(f"Kolom pertama: {first_col}")
        
        if 'jenis' in first_col and 'kelamin' in first_col:
            logging.info("Terdeteksi: jeniskelamin")
            return 'jeniskelamin'
        
        if 'status' in first_col or ('hidup' in str(df.iloc[0, 1]).lower() if len(df) > 0 else False):
            logging.info("Terdeteksi: statuspasien")
            return 'statuspasien'
        
        logging.info("Menggunakan default.")
        return 'default'
    except Exception as e:
        logging.error(f"Error detect_data_type: {e}")
        return 'default'

# ================================
# GABUNG DATA MASTER (tetap sama)
# ================================
def merge_with_master(df_new, master_file):
    """
    Gabungkan data baru dengan data master yang ada.
    Jika master tidak ada, gunakan data baru sebagai master.
    Gabungan berdasarkan kolom 'Tahun'.
    """
    try:
        full_master_path = os.path.join(MASTER_FOLDER, master_file)  # Path lengkap di folder master
        if os.path.exists(full_master_path):
            logging.info(f"Membaca data master dari {full_master_path}...")
            df_master = pd.read_excel(full_master_path, engine='openpyxl')
            logging.info(f"Data master memiliki {len(df_master)} baris.")
            
            df_master = df_master.set_index('Tahun')
            df_new = df_new.set_index('Tahun')
            df_master.update(df_new)
            df_combined = df_master.combine_first(df_new).reset_index()
            logging.info(f"Data berhasil digabungkan: {len(df_combined)} baris total.")
        else:
            logging.info(f"File master {full_master_path} tidak ditemukan. Menggunakan data baru sebagai master.")
            df_combined = df_new
        
        return df_combined
    except Exception as e:
        logging.error(f"Error saat menggabungkan data master: {e}")
        raise

# ================================
# PROSES ETL
# ================================
def run_etl(file_path, save_to_db=False):
    """
    Proses ETL - Transformasi, backup, gabung dengan master, dan simpan ke Excel atau Database
    Mengembalikan path file master jika disimpan ke Excel.
    """
    try:
        logging.info("="*70)
        logging.info("MEMULAI PROSES ETL")
        logging.info("="*70)
        
        # STEP 1: EXTRACT
        logging.info("STEP 1: EXTRACT - Membaca data...")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
        
        df_new = pd.read_excel(file_path, engine='openpyxl')
        logging.info(f"Berhasil membaca {len(df_new)} baris, {len(df_new.columns)} kolom")
        
        # STEP 2: DETECT DATA TYPE
        logging.info("STEP 2: DETECT DATA TYPE")
        data_type = detect_data_type(df_new)
        logging.info(f"Jenis data: '{data_type}'")
        
        # STEP 3: TRANSFORM
        logging.info("STEP 3: TRANSFORM - Memproses data...")
        transform_functions = {
            'jeniskelamin': transform_jeniskelamin,
            'statuspasien': transform_statuspasien,
            'default': lambda df: df
        }
        
        transform_func = transform_functions.get(data_type, lambda df: df)
        logging.info(f"Menggunakan fungsi transform: {transform_func.__name__}")
        
        df_transformed = transform_func(df_new)
        logging.info(f"Data berhasil di-transform: {len(df_transformed)} baris, {len(df_transformed.columns)} kolom")
        
        # Tentukan nama file master
        master_file_map = {
            "jeniskelamin": "fact_jenkel_statuspasien.xlsx",
            "statuspasien": "fact_jenkel_surabaya.xlsx",
            "default": "fact_default_data.xlsx"
        }
        master_file = master_file_map.get(data_type, "fact_unknown.xlsx")
        full_master_path = os.path.join(MASTER_FOLDER, master_file)
        
        # STEP 4: BACKUP MASTER
        logging.info("STEP 4: BACKUP - Membuat backup data master lama...")
        backup_master(full_master_path)
        
        # STEP 5: MERGE WITH MASTER
        logging.info("STEP 5: MERGE - Menggabungkan dengan data master...")
        df_master_combined = merge_with_master(df_transformed, master_file)
        
        # STEP 6: LOAD
        logging.info("STEP 6: LOAD - Menyimpan data...")
        if save_to_db:
            engine = create_connection()
            df_master_combined.to_sql('hiv_surabaya', engine, index=False, if_exists='replace')
            logging.info("Data berhasil disimpan ke database!")
            return None
        else:
            df_master_combined.to_excel(full_master_path, index=False, engine='openpyxl')
            logging.info(f"Data master berhasil diperbarui dan disimpan ke {full_master_path}!")
            return full_master_path
        
        logging.info("="*70)
        logging.info("PROSES ETL SELESAI!")
        logging.info("="*70)
        
    except Exception as e:
        logging.error(f"ERROR dalam ETL: {e}")
        raise

if __name__ == "__main__":
    # Contoh penggunaan untuk testing
    try:
        result = run_etl('data_2026.xlsx', save_to_db=False)
        print(f"ETL selesai. File master: {result}")
    except Exception as e:
        print(f"Gagal menjalankan ETL: {e}")