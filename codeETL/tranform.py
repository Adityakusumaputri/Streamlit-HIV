from extract import extract_data
import pandas as pd
import os

# 1. Missing Values
#mendeteksi kolom yang memiliki nilai kosong (NaN)
def check_missing_values(data):
    print("\n #memeriksa missing values")

    for nama_file, df in data.items():
        print("\n----------------------------------------")
        print(f"DATA {nama_file.upper()}")
        print("----------------------------------------")
    #isnull = mengecek nilai kosong
    #sum menghitung jumlah nan
        missing = df.isnull().sum()
        missing_only = missing[missing > 0]
    #Menampilkan hanya kolom yang benar-benar bermasalah
        if missing_only.empty:
            print("Tidak terdapat missing values")
        else:
            print("Kolom yang terdapat missing values:")
            print(missing_only)

nama_kecamatan = [
    "Asemrowo", "Benowo", "Bubutan", "Bulak", "Dukuh Pakis",
    "Gayungan", "Genteng", "Gubeng", "Gunung Anyar", "Jambangan",
    "Karang Pilang", "Kenjeran", "Krembangan", "Lakarsantri",
    "Mulyorejo", "Pabean Cantian", "Pakal", "Rungkut",
    "Sambikerep", "Sawahan", "Semampir", "Simokerto",
    "Sukolilo", "Sukomanunggal", "Tambaksari", "Tandes",
    "Tegalsari", "Tenggilis Mejoyo", "Wiyung",
    "Wonocolo", "Wonokromo", "Surabaya"
]

def cek_kata_kecamatan(data):
    print("\n #cek nama kecamatan")
    for nama_file, df in data.items():
        for col in df.columns:
            if "kecamatan" in str(col).lower():
                print(f"\nDATA {nama_file.upper()} | Kolom: {col}")

                nilai_unik = (
                    df[col]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .unique()
                )

                for nilai in nilai_unik:
                    if nilai in nama_kecamatan :
                        print(f"{nilai} -> sesuai")
                    else:
                        print(f"{nilai} -> tidak sesuai")

# 2. memperbaiki nama kecamatan
memperbaiki_kecamatan = {
    "Karangpilang": "Karang Pilang",
    "Pabean Cantikan": "Pabean Cantian",
    "semrowo": "Asemrowo",
    "Bulak Banteng": "Bulak",
    "Suko Manunggal": "Sukomanunggal",
}
def benarkan_kata_kecamatan(data):
    print("\n #membenarkan nama kecamatan")
    for nama_file, df in data.items():
        for col in df.columns:
            if "kecamatan" in str(col).lower():
                sebelum = df[col].copy()

                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .replace(memperbaiki_kecamatan)
                )

                if not sebelum.equals(df[col]):
                    print(f"DATA {nama_file.upper()} | Kolom: {col} → diperbaiki")

    return data

#namakolom, foemat tahun, data numerik, baris tidak valid
# 3. Tranfsform Function
def transform_temuantahun(df):
    data = df.copy()

    # file temuan kasus
    data.columns = ["Tahun", "Jumlah Temuan Kasus HIV"]

    # memperbaiki kolom tahun
    data["Tahun"] = data["Tahun"].replace(
        "2025 (hingga bulan Juli)", "2025"
    )
    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    # memastikan numeric
    data["Jumlah Temuan Kasus HIV"] = pd.to_numeric(
        data["Jumlah Temuan Kasus HIV"], errors="coerce"
    )

    # menghapus baris tahun kosong
    data = data[data["Tahun"].notna()]
    data.reset_index(drop=True, inplace=True)

    return data


def transform_statuspasien(df):
    data = df.copy()

    # file status pasien
    data.columns = ["Tahun", "Hidup", "Meninggal"]

    # memperbaiki kolom tahun
    data["Tahun"] = data["Tahun"].replace(
        "2025 (hingga bulan Juli)", "2025"
    )
    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    kolom_angka = ["Hidup", "Meninggal"]
    data[kolom_angka] = data[kolom_angka].apply(
        pd.to_numeric, errors="coerce"
    )

    data = data[data["Tahun"].notna()]
    data.reset_index(drop=True, inplace=True)
    return data
 
def transform_jeniskelamin(df):
    header = df.iloc[0]
    data = df.iloc[1:].copy()
    data.columns = ["Tahun", header.iloc[1], header.iloc[2]]

    # memperbaiki kolom tahun
    data["Tahun"] = data["Tahun"].replace(
        "2025 (hingga bulan Juli)", "2025"
    )
    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    kolom_angka = data.columns.drop("Tahun")
    data[kolom_angka] = data[kolom_angka].apply(
        pd.to_numeric, errors="coerce"
    )

    data.reset_index(drop=True, inplace=True)
    return data

def transform_jeniskelaminsby(df):
    header = df.iloc[0]
    data = df.iloc[1:].copy()
    data.columns = ["Tahun", header.iloc[1], header.iloc[2]]

    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    kolom_angka = data.columns.drop("Tahun")
    data[kolom_angka] = data[kolom_angka].apply(
        pd.to_numeric, errors="coerce"
    )

    data.reset_index(drop=True, inplace=True)
    return data

def transform_umur(df):
    header = df.iloc[0]
    data = df.iloc[1:].copy()

    data = data.iloc[:, :7]
    data.columns = ["Tahun"] + list(header.iloc[1:7])

    # memperbaiki kolom tahun
    data["Tahun"] = data["Tahun"].replace(
        "2025 (hingga bulan Juli)", "2025"
    )
    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    kolom_umur = data.columns.drop("Tahun")
    data[kolom_umur] = data[kolom_umur].apply(
        pd.to_numeric, errors="coerce"
    )

    # menghapus baris tahun kosong
    data = data[data["Tahun"].notna()]

    data.reset_index(drop=True, inplace=True)
    return data

def transform_umursby(df):
    header = df.iloc[0]
    data = df.iloc[1:].copy()

    data = data.iloc[:, :7]
    data.columns = ["Tahun"] + list(header.iloc[1:7])

    data["Tahun"] = pd.to_numeric(data["Tahun"], errors="coerce")

    kolom_umur = data.columns.drop("Tahun")
    data[kolom_umur] = data[kolom_umur].apply(
        pd.to_numeric, errors="coerce"
    )

    # menghapus baris tahun kosong
    data = data[data["Tahun"].notna()]

    data.reset_index(drop=True, inplace=True)
    return data

def transform_perkecamatan(df):
    header = df.iloc[0]
    data = df.iloc[1:].copy()

    kolom_baru = []
    tahun = None

    for col in df.columns:
        col_str = str(col)

        if col_str.isdigit():
            tahun = col_str
            kolom_baru.append(f"{tahun}_Temuan kasus")

        elif col_str.lower().startswith("unnamed") and tahun:
            kolom_baru.append(f"{tahun}_{header[col]}")

        else:
            kolom_baru.append(col_str)

    data.columns = kolom_baru

    # Menghapus baris yang memiliki 'Luar Surabaya' pada kolom 'No.' atau kolom yang sesuai
    data = data[~data.apply(lambda row: row.astype(str).str.contains("Luar Surabaya", case=False).any(), axis=1)]

    # Menghapus baris yang memiliki 'TOTAL' pada kolom 'No.'
    data = data[~data['No.'].str.contains("TOTAL", case=False, na=False)]

    # Mengonversi kolom angka
    kolom_angka = data.columns.difference(["No.", "Kecamatan Wilayah Surabaya"])
    data[kolom_angka] = data[kolom_angka].apply(pd.to_numeric, errors="coerce").fillna(0)

    data.reset_index(drop=True, inplace=True)
    return data


def transform_default(df):
    return df.copy()

# 3. SIMPAN KE CSV
# =====================================================
def simpan_ke_csv(data, folder_output="output_csv"):
    os.makedirs(folder_output, exist_ok=True)

    for nama, df in data.items():
        path = os.path.join(folder_output, f"{nama}.csv")
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"✅ Data {nama.upper()} disimpan ke {path}")

# 3. main pipeline
def transform_all():
    data = extract_data()

    # 1 AUDIT DATA
    check_missing_values(data)
    cek_kata_kecamatan(data)

    # pembenaran kata
    data = benarkan_kata_kecamatan(data)

    # transform
    hasil = {
    "jeniskelamin": transform_jeniskelamin(data["jeniskelamin"]),
    "jeniskelaminsby": transform_jeniskelaminsby(data["jeniskelaminsby"]),
    "umur": transform_umur(data["umur"]),
    "umursby": transform_umursby(data["umursby"]),
    "perkecamatan": transform_perkecamatan(data["perkecamatan"]),
    "statuspasien": transform_statuspasien(data["statuspasien"]),
    "temuantahun": transform_temuantahun(data["temuantahun"]),
    "upk": transform_default(data["upk"]),
}


    # OUTPUT
     # output dan numeric 
    for nama, df in hasil.items():
        print(f"\n=== Data {nama.upper()} final ===")
        print(df)

        # ✅ TAMBAHAN PENTING (INI SAJA YANG BARU)
        print("DTYPES:")
        print(df.dtypes)


     # SIMPAN KE CSV
    simpan_ke_csv(hasil)

    return hasil


# 4. EKSEKUSI
if __name__ == "__main__":
    transform_all()