import streamlit as st
import pandas as pd

st.set_page_config(page_title="Validasi Kepesertaan", layout="wide")
st.title("🔍 Aplikasi Validasi Kepesertaan")

# Cek apakah sudah ada session untuk file
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# Upload file baru
uploaded_file = st.file_uploader("Upload file Excel (.xlsx) atau CSV (.csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1]

    try:
        if file_type == "csv":
            df = pd.read_csv(uploaded_file, dtype=str)
        else:
            df = pd.read_excel(uploaded_file, dtype=str)

        df.fillna("-", inplace=True)

        # Simpan file ke session_state
        st.session_state.uploaded_files[uploaded_file.name] = df
        st.success(f"File {uploaded_file.name} berhasil diupload!")

    except Exception as e:
        st.error(f"Gagal membaca file: {e}")

# Tampilkan form pencarian sekali saja di atas
if st.session_state.uploaded_files:
    st.subheader("🔎 Form Pencarian")
    search_nama = st.text_input("Cari berdasarkan NAMA").strip().lower()
    search_nopek = st.text_input("Cari berdasarkan NOPEK").strip()

    st.subheader("📂 Daftar File yang Diupload:")

    # Tampilkan semua file yang sudah diupload
    for file_name, df in st.session_state.uploaded_files.items():
        with st.expander(f"📄 {file_name}", expanded=True):

            if search_nama or search_nopek:
                filtered_df = df[
                    df['NAMA'].str.lower().str.contains(search_nama, na=False) &
                    df['NOPEK'].str.contains(search_nopek, na=False)
                ]
                st.write(f"Hasil pencarian ({len(filtered_df)} data):")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

            # Tombol delete file
            if st.button(f"Hapus {file_name}", key=f"hapus_{file_name}"):
                del st.session_state.uploaded_files[file_name]
                st.success(f"File {file_name} berhasil dihapus!")
                st.experimental_rerun()
else:
    st.info("Belum ada file yang diupload.")
