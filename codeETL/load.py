import mysql.connector
import pandas as pd
import re
import sys
import codecs

# Menambahkan support untuk karakter unicode
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

# 1. menkoneksi dan membuat db 
# =============================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = db.cursor()

cursor.execute("DROP DATABASE IF EXISTS datawarehouse_hiv")
cursor.execute("CREATE DATABASE datawarehouse_hiv")
cursor.execute("USE datawarehouse_hiv")

# 2. TABEL DIMENSI
# =============================

cursor.execute("""
CREATE TABLE dim_waktu (
    id_waktu INT AUTO_INCREMENT PRIMARY KEY,
    tahun INT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE dim_kecamatan (
    id_kecamatan INT AUTO_INCREMENT PRIMARY KEY,
    nama_kecamatan VARCHAR(500) UNIQUE
)
""")

cursor.execute("""
CREATE TABLE dim_kelompok_umur (
    id_kelompok_umur INT AUTO_INCREMENT PRIMARY KEY,
    kelompok_umur VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE dim_jenis_kelamin (
    id_jenis_kelamin INT AUTO_INCREMENT PRIMARY KEY,
    jenis_kelamin VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE dim_status_pasien (
    id_status_pasien INT AUTO_INCREMENT PRIMARY KEY,
    status_pasien VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE dim_upk (
    id_upk INT AUTO_INCREMENT PRIMARY KEY,
    id_kecamatan INT,
    nama_upk VARCHAR(500),
    status_pemilik VARCHAR(100),
    jenis_pemilik VARCHAR(100),
    alamat TEXT
)
""")

cursor.execute("""
CREATE TABLE dim_jenis_layanan (
    id_jenis_layanan INT AUTO_INCREMENT PRIMARY KEY,
    id_kecamatan INT,
    layanan_tes_hiv VARCHAR(255),
    layanan_pdp VARCHAR(255),
    layanan_vl VARCHAR(255),
    layanan_tes_eid VARCHAR(255),
    layanan_tes_cd4 VARCHAR(255)
)
""")


# 3. tabel fakta
# =============================

cursor.execute("""
CREATE TABLE fact_kasus_perkecamatan (
    id_fact_kasus_perkecamatan INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT,
    id_kecamatan INT,
    temuan_kasus INT,
    ART INT
)
""")

cursor.execute("""
CREATE TABLE fact_perkelompok_umur (
    id_fact_perkelompok_umur INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT,
    id_kelompok_umur INT,
    temuan_kasus INT
)
""")

cursor.execute("""
CREATE TABLE fact_jenkel_statuspasien (
    id_fact INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT NOT NULL,
    kategori ENUM('JK','SP') NOT NULL,
    id_dimensi INT NOT NULL,
    temuan_kasus INT NOT NULL,
    FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu)
)
""")

cursor.execute("""
CREATE TABLE fact_umur_surabaya (
    id_fact_umur_surabaya INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT,
    id_kelompok_umur INT,
    temuan_kasus_surabaya INT,
    FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu),
    FOREIGN KEY (id_kelompok_umur) REFERENCES dim_kelompok_umur(id_kelompok_umur)
)
""")

cursor.execute("""
CREATE TABLE fact_jenkel_surabaya (
    id_fact_jenkel_surabaya INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT,
    id_jenis_kelamin INT,
    temuan_kasus_surabaya INT,
    FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu),
    FOREIGN KEY (id_jenis_kelamin) REFERENCES dim_jenis_kelamin(id_jenis_kelamin)
)
""")
db.commit()
print("✅ Database dan tabel berhasil dibuat")

# 4. load atau memasukan data ke dimensi
# =============================

# ---- dim_waktu
df = pd.read_csv("output_csv/temuantahun.csv")
for _, r in df.iterrows():
    cursor.execute(
        "INSERT INTO dim_waktu (tahun) VALUES (%s)",
        (int(r["Tahun"]),)
    )
db.commit()

# ---- dim_kecamatan
df = pd.read_csv("output_csv/perkecamatan.csv")
for kec in df["Kecamatan Wilayah Surabaya"].dropna().unique():
    cursor.execute(
        "INSERT INTO dim_kecamatan (nama_kecamatan) VALUES (%s)",
        (kec.strip(),)
    )
db.commit()

# ---- dim_kelompok_umur
df = pd.read_csv("output_csv/umur.csv")
for col in df.columns:
    if col != "Tahun":
        cursor.execute(
            "INSERT INTO dim_kelompok_umur (kelompok_umur) VALUES (%s)",
            (col,)
        )
db.commit()

# ---- dim_jenis_kelamin
df = pd.read_csv("output_csv/jeniskelamin.csv")
for col in df.columns:
    if col != "Tahun":
        cursor.execute(
            "INSERT INTO dim_jenis_kelamin (jenis_kelamin) VALUES (%s)",
            (col,)
        )
db.commit()

# ---- dim_status_pasien
for sp in ["Hidup", "Meninggal"]:
    cursor.execute(
        "INSERT INTO dim_status_pasien (status_pasien) VALUES (%s)",
        (sp,)
    )
db.commit()

# ---- dim_upk & dim_jenis_layanan
df_upk = pd.read_csv("output_csv/upk.csv")  # Ganti dengan path file Anda
df_upk.columns = df_upk.columns.str.strip().str.lower().str.replace(" ", "_")  # Menjaga format konsisten

for _, r in df_upk.iterrows():
    # Mendapatkan ID kecamatan berdasarkan nama kecamatan
    cursor.execute("SELECT id_kecamatan FROM dim_kecamatan WHERE nama_kecamatan=%s", (r["kecamatan"],))
    res = cursor.fetchone()

    if not res:
        print(f"Kecamatan tidak ditemukan: {r['kecamatan']}")
        continue  # Lewati data jika kecamatan tidak ditemukan

    id_kec = res[0]  # ID kecamatan yang valid

    # Memasukkan data ke dalam tabel dim_upk
    cursor.execute("""
        INSERT INTO dim_upk
        (id_kecamatan, nama_upk, status_pemilik, jenis_pemilik, alamat)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        id_kec,
        r["nama"],           # Nama UPK
        r["status_pemilik"], # Status pemilik (Pemerintah, Swasta, dll)
        r["jenis_pemilik"],  # Jenis pemilik (Pemda, Organisasi, dll)
        r["alamat"]          # Alamat
    ))

    # Memasukkan data layanan ke dalam tabel dim_jenis_layanan
    cursor.execute("""
    INSERT INTO dim_jenis_layanan
    (id_kecamatan, layanan_tes_hiv, layanan_pdp, layanan_vl, layanan_tes_eid, layanan_tes_cd4)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (
    id_kec,
    "Ya" if r["layanan_tes_hiv"] == "Ya" else "Tidak",  # Menggunakan 'Ya' atau 'Tidak' sebagai string
    "Ya" if r["layanan_pdp"] == "Ya" else "Tidak",
    "Ya" if r["layanan_tes_vl"] == "Ya" else "Tidak",
    "Ya" if r["layanan_tes_eid"] == "Ya" else "Tidak",
    "Ya" if r["layanan_tes_cd4"] == "Ya" else "Tidak"
))


db.commit()
print("✅ Data UPK dan layanan berhasil dimuat.")


#Mencocokkan data teks dengan ID yang sudah ada, menghubungkan fakta ke dim
# 5. mapping dimensi
# =============================

cursor.execute("SELECT id_waktu, tahun FROM dim_waktu")
map_waktu = {t: i for i, t in cursor.fetchall()}

cursor.execute("SELECT id_kecamatan, nama_kecamatan FROM dim_kecamatan")
map_kec = {n: i for i, n in cursor.fetchall()}

cursor.execute("SELECT id_kelompok_umur, kelompok_umur FROM dim_kelompok_umur")
map_umur = {n: i for i, n in cursor.fetchall()}

cursor.execute("SELECT id_jenis_kelamin, jenis_kelamin FROM dim_jenis_kelamin")
map_jk = {n: i for i, n in cursor.fetchall()}

cursor.execute("SELECT id_status_pasien, status_pasien FROM dim_status_pasien")
map_sp = {n: i for i, n in cursor.fetchall()}

# 6. load atau memasukan data ke tabel fakta
# =============================

cursor.execute("TRUNCATE fact_kasus_perkecamatan")

df = pd.read_csv("output_csv/perkecamatan.csv")

for _, r in df.iterrows():
    kecamatan = str(r["Kecamatan Wilayah Surabaya"]).strip()
    id_kec = map_kec.get(kecamatan)
    if not id_kec:
        print("Kecamatan tidak ketemu:", kecamatan)
        continue

    for col in df.columns:
        if "Temuan" in col:
            tahun = int(re.search(r"\d{4}", col).group())
            id_waktu = map_waktu.get(tahun)

            col_art = [c for c in df.columns if str(tahun) in c and "ART" in c]
            if not col_art or not id_waktu:
                continue

            temuan = 0 if pd.isna(r[col]) else int(r[col])
            art = 0 if pd.isna(r[col_art[0]]) else int(r[col_art[0]])

            cursor.execute("""
                INSERT INTO fact_kasus_perkecamatan
                (id_waktu, id_kecamatan, temuan_kasus, ART)
                VALUES (%s, %s, %s, %s)
            """, (id_waktu, id_kec, temuan, art))

db.commit()


# ---- fact_perkelompok_umur
df = pd.read_csv("output_csv/umur.csv")
for _, r in df.iterrows():
    id_waktu = map_waktu.get(int(r["Tahun"]))
    for col in df.columns:
        if col != "Tahun":
            cursor.execute("""
                INSERT INTO fact_perkelompok_umur
                (id_waktu, id_kelompok_umur, temuan_kasus)
                VALUES (%s, %s, %s)
            """, (id_waktu, map_umur[col], int(r[col])))
db.commit()

# ---- fact_jenis kelamin dan status pasien
df_jk = pd.read_csv("output_csv/jeniskelamin.csv")
df_sp = pd.read_csv("output_csv/statuspasien.csv")

for i in range(len(df_jk)):
    tahun = int(df_jk.loc[i, "Tahun"])
    id_waktu = map_waktu.get(tahun)

    # ====== INSERT JENIS KELAMIN ======
    for jk in map_jk:
        cursor.execute("""
            INSERT INTO fact_jenkel_statuspasien
            (id_waktu, kategori, id_dimensi, temuan_kasus)
            VALUES (%s, 'JK', %s, %s)
        """, (id_waktu, map_jk[jk], int(df_jk.loc[i, jk])))

    # ====== INSERT STATUS PASIEN ======
    for sp in map_sp:
        cursor.execute("""
            INSERT INTO fact_jenkel_statuspasien
            (id_waktu, kategori, id_dimensi, temuan_kasus)
            VALUES (%s, 'SP', %s, %s)
        """, (id_waktu, map_sp[sp], int(df_sp.loc[i, sp])))

db.commit()

# ---- fact_perkelompok_umur
df = pd.read_csv("output_csv/umursby.csv")
for _, r in df.iterrows():
    id_waktu = map_waktu.get(int(r["Tahun"]))
    for col in df.columns:
        if col != "Tahun":
            cursor.execute("""
                INSERT INTO fact_umur_surabaya
                (id_waktu, id_kelompok_umur, temuan_kasus_surabaya)
                VALUES (%s, %s, %s)
            """, (id_waktu, map_umur[col], int(r[col])))
db.commit()

# ---- fact_jenkel_sby
df_jenkel_sby = pd.read_csv("output_csv/jeniskelaminsby.csv")  
for _, r in df_jenkel_sby.iterrows():
    id_waktu = map_waktu.get(int(r["Tahun"]))
    for col in df_jenkel_sby.columns:
        if col != "Tahun":
            cursor.execute("""
                INSERT INTO fact_jenkel_surabaya
                (id_waktu, id_jenis_kelamin, temuan_kasus_surabaya)
                VALUES (%s, %s, %s)
            """, (id_waktu, map_jk[col], int(r[col])))
db.commit()

# =============================
# 7️⃣ TUTUP KONEKSI
# =============================
cursor.close()
db.close()

print("berhasil load semuanya")