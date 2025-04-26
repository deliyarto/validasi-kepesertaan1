import streamlit as st
import pandas as pd

st.set_page_config(page_title="Validasi Kepesertaan", layout="wide")

# Judul Umum
st.title("🔍 Aplikasi Validasi Kepesertaan")

# Password Admin
admin_password = "admin123"  # Ganti sesuai keinginan

# Cek login admin
is_admin = False

with st.expander("🔒 Login Admin (Khusus Admin)"):
    password_input = st.text_input("Masukkan Password Admin", type="password")
    if password_input == admin_password:
        st.success("Login sebagai Admin berhasil!")
        is_admin = True
    elif password_input:
        st.error("Password salah!")

# Simpan data file di session
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# ===================
# Bagian Admin
# ===================
if is_admin:
    st.header("🛠 Admin Panel – Upload / Hapus File Data")

    uploaded_file = st.file_uploader("📤 Upload file Excel (.xlsx) atau CSV (.csv)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        try:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file, dtype=str)
            else:
                df = pd.read_excel(uploaded_file, dtype=str)
            df.fillna("-", inplace=True)
            st.session_state.uploaded_files[uploaded_file.name] = df
            st.success(f"✅ File {uploaded_file.name} berhasil diupload!")
        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")

    if st.session_state.uploaded_files:
        st.subheader("🗂 File yang Diupload")
        for file_name in list(st.session_state.uploaded_files.keys()):
            col1, col2 = st.columns([6,1])
            with col1:
                st.write(f"📄 {file_name}")
            with col2:
                if st.button(f"Hapus", key=f"hapus_{file_name}"):
                    del st.session_state.uploaded_files[file_name]
                    st.success(f"✅ File {file_name} berhasil dihapus!")
                    st.experimental_rerun()
else:
    st.info("Login admin untuk mengupload atau menghapus file.")

# ===================
# Bagian User Umum
# ===================

st.header("🔎 Pencarian Data Peserta")

if st.session_state.uploaded_files:
    search_nama = st.text_input("Cari berdasarkan Nama").strip().lower()
    search_nopek = st.text_input("Cari berdasarkan Nopek").strip()

    all_dataframes = []
    for file_name, df in st.session_state.uploaded_files.items():
        all_dataframes.append(df)
    final_df = pd.concat(all_dataframes, ignore_index=True)

    if search_nama or search_nopek:
        filtered_df = final_df[
            final_df['NAMA'].str.lower().str.contains(search_nama, na=False) &
            final_df['NOPEK'].str.contains(search_nopek, na=False)
        ]
        st.write(f"🔎 Hasil pencarian ({len(filtered_df)} data):")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.write("Masukkan Nama atau Nopek untuk mencari data peserta.")

else:
    st.warning("⚠️ Belum ada file yang diupload.")
