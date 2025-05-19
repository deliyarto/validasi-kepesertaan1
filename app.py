import streamlit as st
import pandas as pd

# URL CSV export dari Google Sheets (pastikan ini URL CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/1av0iPfTKLKwpsc8XJ_YWesY_MFvhRAN8Nr70Vl0pqbE/export?format=csv&gid=836723519"

# Fungsi untuk membaca data dari Google Sheets
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(sheet_url, dtype=str)
        return df
    except Exception as e:
        st.error(f"Gagal membaca data dari Google Sheets: {e}")
        return pd.DataFrame()
        
# Tombol untuk reload data
if st.button("🔄 Muat Ulang Data Terbaru"):
    st.cache_data.clear()  # Ini akan menghapus cache lama

# Load data
data = load_data()

# Judul Aplikasi
st.title("🔍 Pencarian Data Peserta")

# Form input pencarian
search_query = st.text_input("Masukkan kata kunci (NOPEK, PERUSAHAAN, NAMA, PENANGGUNG, DOB, HC_1, HC_2)")

# Kolom yang ingin ditampilkan
columns_to_show = ['KODE_KARTU','KELUAR', 'PERUSAHAAN', 'NAMA', 'PENANGGUNG', 'STS', 'DOB', 'UMUR', 'KELAS_RAWAT_INAP', 'KELAS_RSPP', 'HC_1', 'HC_2']

# Filter data
if search_query:
    filtered_data = data[
        data['NOPEK'].fillna('').str.contains(search_query, case=False, na=False) |
        data['KODE_KARTU'].fillna('').str.contains(search_query, case=False, na=False) |
        data['PERUSAHAAN'].fillna('').str.contains(search_query, case=False, na=False) |
        data['NAMA'].fillna('').str.contains(search_query, case=False, na=False) |
        data['PENANGGUNG'].fillna('').str.contains(search_query, case=False, na=False) |
        data['DOB'].fillna('').str.contains(search_query, case=False, na=False) |
        data['HC_1'].fillna('').str.contains(search_query, case=False, na=False) |
        data['HC_2'].fillna('').str.contains(search_query, case=False, na=False)
    ]
    if not filtered_data.empty:
        st.success(f"Ditemukan {len(filtered_data)} hasil pencarian.")
        st.dataframe(
            filtered_data[columns_to_show],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Tidak ditemukan data yang cocok.")
else:
    st.info("Silakan masukkan kata kunci untuk mencari.")

# Catatan kecil
st.caption("Data peserta bersumber dari Google Sheets.")
