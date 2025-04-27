import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# Konstanta
UPLOAD_FOLDER = "uploaded_files"
ADMIN_PASSWORD = "admin123"  # Ganti sesuai kebutuhan

# Pastikan folder upload ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cek status login
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Sidebar login/logout
with st.sidebar:
    if st.session_state.is_admin:
        st.success("Login sebagai Admin ✅")
        if st.button("Logout"):
            st.session_state.is_admin = False
    else:
        password = st.text_input("Masuk sebagai Admin", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("Login berhasil!")
            else:
                st.error("Password salah!")

# Fungsi untuk load semua file Excel/CSV
def load_all_data():
    all_dfs = []
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if filename.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine='openpyxl')
            all_dfs.append(df)
        elif filename.endswith(".csv"):
            df = pd.read_csv(file_path)
            all_dfs.append(df)
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return pd.DataFrame()

# Halaman utama
st.title("🔎 Cek Kepesertaan")

if st.session_state.is_admin:
    st.header("📤 Upload File Baru")

    uploaded_file = st.file_uploader("Upload file Excel/CSV", type=["xlsx", "csv"])
    if uploaded_file is not None:
        # Simpan file ke folder UPLOAD_FOLDER
        file_ext = uploaded_file.name.split(".")[-1]
        save_path = os.path.join(UPLOAD_FOLDER, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File berhasil diupload: {save_path}")

    st.header("🗑️ Hapus File yang Ada")
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        file_to_delete = st.selectbox("Pilih file untuk dihapus", files)
        if st.button("Hapus File"):
            os.remove(os.path.join(UPLOAD_FOLDER, file_to_delete))
            st.success(f"File {file_to_delete} berhasil dihapus!")
    else:
        st.info("Belum ada file yang diupload.")

st.header("🔍 Cari Peserta")

# Search input (hanya satu, tidak per file)
search_nama = st.text_input("Cari berdasarkan Nama").lower()
search_nopek = st.text_input("Cari berdasarkan Nopek").lower()

df = load_all_data()

if not df.empty:
    # Filter kolom yang mau ditampilkan
    selected_columns = [
        "PERUSAHAAN", "NOPEK", "NAMA", "PENANGGUNG", "NAMA_KARTU",
        "STS", "KD_STS", "DOB", "KELAS", "KELAS_RAWAT_INAP"
    ]

    if search_nama or search_nopek:
        filtered_df = df[
            (df['NAMA'].str.lower().str.contains(search_nama)) &
            (df['NOPEK'].str.lower().str.contains(search_nopek))
        ]
    else:
        filtered_df = df

    display_df = filtered_df[selected_columns]

    st.dataframe(display_df)

    # Tombol download hasil pencarian
    if not display_df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            display_df.to_excel(writer, index=False)
        buffer.seek(0)

        st.download_button(
            label="💾 Download Hasil sebagai Excel",
            data=buffer,
            file_name=f"hasil_pencarian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("Belum ada data tersedia. Admin perlu upload file dulu.")
