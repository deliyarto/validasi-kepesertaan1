import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Validasi Kepesertaan", layout="wide")

# --- SETUP FOLDER DATA ---
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# --- SETUP ADMIN ---
admin_password = "admin123"
is_admin = False

with st.expander("🔒 Login Admin (Khusus Admin)"):
    password_input = st.text_input("Masukkan Password Admin", type="password")
    if password_input == admin_password:
        st.success("Login sebagai Admin berhasil!")
        is_admin = True
    elif password_input:
        st.error("Password salah!")

# ===================
# BAGIAN ADMIN
# ===================
if is_admin:
    st.header("🛠 Admin Panel – Upload / Hapus File Data")

    uploaded_file = st.file_uploader("📤 Upload file Excel (.xlsx) atau CSV (.csv)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        file_path = os.path.join(DATA_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File {uploaded_file.name} berhasil disimpan!")

    st.subheader("🗂 File Tersimpan")
    file_list = os.listdir(DATA_FOLDER)
    for file_name in file_list:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write(f"📄 {file_name}")
        with col2:
            if st.button(f"Hapus {file_name}", key=f"hapus_{file_name}"):
                os.remove(os.path.join(DATA_FOLDER, file_name))
                st.success(f"✅ File {file_name} berhasil dihapus!")
                st.experimental_rerun()

else:
    st.info("Login admin untuk mengupload atau menghapus file.")

# ===================
# BAGIAN USER UMUM
# ===================
st.header("🔎 Pencarian Data Peserta")

file_list = os.listdir(DATA_FOLDER)

if file_list:
    search_nama = st.text_input("Cari berdasarkan Nama").strip().lower()
    search_nopek = st.text_input("Cari berdasarkan Nopek").strip()

    all_dataframes = []
    for file_name in file_list:
        file_path = os.path.join(DATA_FOLDER, file_name)
        try:
            if file_name.endswith(".csv"):
                df = pd.read_csv(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path, dtype=str)
            df.fillna("-", inplace=True)
            all_dataframes.append(df)
        except Exception as e:
            st.error(f"Gagal membaca {file_name}: {e}")

    final_df = pd.concat(all_dataframes, ignore_index=True)

    if search_nama or search_nopek:
        filtered_df = final_df[
            (final_df['NAMA'].str.lower().str.contains(search_nama, na=False)) &
            (final_df['NOPEK'].str.contains(search_nopek, na=False))
        ]
        st.write(f"🔎 Hasil pencarian ({len(filtered_df)} data):")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.write("Masukkan Nama atau Nopek untuk mencari data peserta.")
else:
    st.warning("⚠️ Belum ada file di folder data.")
