import streamlit as st
import pandas as pd
import os
from datetime import datetime
import shutil

# Konfigurasi halaman
st.set_page_config(page_title="Cek Kepesertaan", layout="wide")

# Folder penyimpanan file upload
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fungsi simpan file permanen
def save_uploaded_file(uploadedfile):
    filepath = os.path.join(UPLOAD_FOLDER, uploadedfile.name)
    with open(filepath, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return filepath

# Fungsi load semua data dari folder
def load_all_data():
    all_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filepath, engine='openpyxl')
        elif filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            continue
        all_data.append(df)
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Halaman Admin
def admin_page():
    st.header("Admin Area 👨‍💻")

    uploaded_file = st.file_uploader("Upload file Excel atau CSV", type=['xlsx', 'csv'])
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
        st.success(f"File {uploaded_file.name} berhasil di-upload!")

    st.subheader("File yang sudah diupload:")
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        for file in files:
            col1, col2 = st.columns([5,1])
            with col1:
                st.write(file)
            with col2:
                if st.button(f"Hapus {file}", key=file):
                    os.remove(os.path.join(UPLOAD_FOLDER, file))
                    st.success(f"File {file} berhasil dihapus.")
                    st.experimental_rerun()
    else:
        st.info("Belum ada file yang diupload.")

# Halaman User
def user_page():
    st.header("Cari Data Peserta 📄")

    df = load_all_data()

    if df.empty:
        st.info("Belum ada data yang tersedia.")
        return

    # Form pencarian
    search_term = st.text_input("Cari berdasarkan Nama, Nopek, Perusahaan, Penanggung, atau Tanggal Lahir (YYYY-MM-DD):").lower()

    if search_term:
        filtered_df = df[
            df['NAMA'].astype(str).str.lower().str.contains(search_term) |
            df['NOPEK'].astype(str).str.lower().str.contains(search_term) |
            df['PERUSAHAAN'].astype(str).str.lower().str.contains(search_term) |
            df['PENANGGUNG'].astype(str).str.lower().str.contains(search_term) |
            df['DOB'].astype(str).str.lower().str.contains(search_term)
        ]
    else:
        filtered_df = df.copy()

    # Tampilkan hanya kolom tertentu
    kolom_tampil = ['PERUSAHAAN', 'NOPEK', 'NAMA', 'PENANGGUNG', 'NAMA_KARTU', 'STS', 'DOB', 'KELAS_RAWAT_INAP']
    available_cols = [col for col in kolom_tampil if col in filtered_df.columns]
    display_df = filtered_df[available_cols]

    # Tampilkan tabel besar tanpa scroll kanan kiri
    st.dataframe(display_df, use_container_width=True, height=600)

# Main
def main():
    st.sidebar.title("Navigasi")
    page = st.sidebar.selectbox("Pilih Mode", ("User", "Admin"))

    if page == "Admin":
        st.sidebar.subheader("Login Admin")
        password = st.sidebar.text_input("Password", type="password")

        if password == "admin123":  # <-- GANTI password sesuai keinginanmu
            admin_page()
        elif password:
            st.sidebar.error("Password salah!")
    else:
        user_page()

if __name__ == "__main__":
    main()
