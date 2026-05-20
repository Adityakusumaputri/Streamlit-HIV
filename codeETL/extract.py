import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

def extract_data():
    data = {
        "jeniskelamin": pd.read_excel(os.path.join(DATA_DIR, "jeniskelamin.xlsx")),
        "perkecamatan": pd.read_excel(os.path.join(DATA_DIR, "perkecamatan.xlsx")),
        "statuspasien": pd.read_excel(os.path.join(DATA_DIR, "statuspasien.xlsx")),
        "temuantahun":  pd.read_excel(os.path.join(DATA_DIR, "temuantahun.xlsx")),
        "umur":         pd.read_excel(os.path.join(DATA_DIR, "umur.xlsx")),
        "upk":          pd.read_excel(os.path.join(DATA_DIR, "upk.xlsx")),
        "jeniskelaminsby":  pd.read_excel(os.path.join(DATA_DIR, "jenkelsby.xlsx")),
        "umursby":          pd.read_excel(os.path.join(DATA_DIR, "umursby.xlsx")),
    }
    return data


# menampilkan hasil
if __name__ == "__main__":
    data = extract_data()

    print("Haasil dari Extract")
    for nama, df in data.items():
        print(f"\nData {nama.upper()}")
        print(df.head())

# #semua
#if __name__ == "__main__":
#     data = extract_data()

#     print("=== HASIL EXTRACT (SEMUA DATA) ===")
#     for nama, df in data.items():
#         print(f"\nData {nama.upper()}")
#         print(df.to_string())

