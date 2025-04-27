import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
from io import BytesIO

# Konfigurasi halaman
st.set_page_config(page_title="Cek Kepesertaan", layout="wide")

# Folder penyimpanan file upload
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========== FUNGSI UTAMA ==========
def save_uploaded_file(uploadedfile):
    filepath = os.path.join(UPLOAD_FOLDER, uploadedfile.name)
    with open(filepath, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return filepath

def load_all_data():
    all_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if filename.endswith('.xlsx'):
                df = pd.read_excel(filepath, engine='openpyxl')
            elif filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                continue
            all_data.append(df)
        except Exception as e:
            st.error(f"Gagal memuat file {filename}: {str(e)}")
            continue
            
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# ========== FITUR BARU ==========
def create_backup():
    """Membuat backup semua data dalam format ZIP"""
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for root, _, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    memory_file.seek(0)
    return memory_file

def validate_data(df):
    """Validasi struktur data yang diupload"""
    required_columns = ['NAMA', 'NOPEK', 'PENANGGUNG']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"Kolom wajib tidak ditemukan: {', '.join(missing_cols)}"
    return True, "Data valid"

def show_stats(df):
    """Menampilkan statistik data yang sudah diurutkan"""
    if not df.empty:
        with st.expander("📊 Statistik Data", expanded=True):
            # Metrics
            cols = st.columns(3)
            cols[0].metric("Total Peserta", len(df))
            cols[1].metric("Jumlah Perusahaan", df['PERUSAHAAN'].nunique())
            cols[2].metric("Jumlah Penanggung", df['PENANGGUNG'].nunique())
            
            # Tab untuk distribusi data
            tab1, tab2 = st.tabs(["📈 Per Perusahaan", "📊 Per Status"])
            
            with tab1:
                # Hitung dan urutkan perusahaan
                perusahaan_counts = df['PERUSAHAAN'].value_counts().sort_values(ascending=False)
                st.write("**10 Perusahaan dengan Peserta Terbanyak:**")
                st.bar_chart(perusahaan_counts.head(10))
                
                # Tabel detail
                st.write("**Detail Jumlah Peserta per Perusahaan:**")
                st.dataframe(perusahaan_counts.reset_index().rename(
                    columns={'index': 'Perusahaan', 'PERUSAHAAN': 'Jumlah Peserta'}
                ), height=300)
            
            with tab2:
                # Hitung dan urutkan status
                sts_counts = df['STS'].value_counts().sort_values(ascending=False)
                st.write("**Distribusi Status Peserta:**")
                st.bar_chart(sts_counts)
                
                # Tabel detail
                st.write("**Detail Jumlah per Status:**")
                st.dataframe(sts_counts.reset_index().rename(
                    columns={'index': 'Status', 'STS': 'Jumlah'}
                ), height=300)

# ========== HALAMAN ADMIN ==========
def admin_page():
    st.header("Admin Area 👨‍💻")
    
    # Tab untuk berbagai fungsi admin
    tab1, tab2, tab3 = st.tabs(["Upload Data", "Manajemen File", "Backup & Restore"])
    
    with tab1:
        st.subheader("Upload Data Baru")
        uploaded_file = st.file_uploader("Pilih file Excel atau CSV", type=['xlsx', 'csv'])
        if uploaded_file is not None:
            try:
                # Validasi file sebelum upload
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    df = pd.read_csv(uploaded_file)
                
                is_valid, msg = validate_data(df)
                if not is_valid:
                    st.error(msg)
                else:
                    save_uploaded_file(uploaded_file)
                    st.success(f"File {uploaded_file.name} berhasil di-upload!")
                    st.balloons()
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal memproses file: {str(e)}")
    
    with tab2:
        st.subheader("File yang Tersedia")
        files = os.listdir(UPLOAD_FOLDER)
        if files:
            for file in files:
                cols = st.columns([4, 1, 1, 1])
                with cols[0]:
                    st.write(f"📄 {file}")
                with cols[1]:
                    if st.button(f"👁️", key=f"view_{file}"):
                        try:
                            if file.endswith('.xlsx'):
                                df = pd.read_excel(os.path.join(UPLOAD_FOLDER, file), engine='openpyxl')
                            else:
                                df = pd.read_csv(os.path.join(UPLOAD_FOLDER, file))
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"Gagal memuat file: {str(e)}")
                with cols[2]:
                    if st.button(f"📥", key=f"dl_{file}"):
                        with open(os.path.join(UPLOAD_FOLDER, file), "rb") as f:
                            st.download_button(
                                "Download File",
                                f,
                                file_name=file,
                                key=f"real_dl_{file}"
                            )
                with cols[3]:
                    if st.button(f"❌", key=f"del_{file}"):
                        os.remove(os.path.join(UPLOAD_FOLDER, file))
                        st.success(f"File {file} berhasil dihapus.")
                        st.experimental_rerun()
        else:
            st.info("Belum ada file yang diupload.")
    
    with tab3:
        st.subheader("Backup & Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Backup Data**")
            if st.button("Buat Backup Sekarang"):
                backup_zip = create_backup()
                st.download_button(
                    "⬇️ Download Backup",
                    data=backup_zip,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
        
        with col2:
            st.write("**Restore Data**")
            restore_file = st.file_uploader("Upload file backup ZIP", type=['zip'])
            if restore_file is not None:
                if st.button("Restore Backup", type="primary"):
                    with st.spinner("Memproses restore..."):
                        try:
                            # Kosongkan folder saat ini
                            for f in os.listdir(UPLOAD_FOLDER):
                                os.remove(os.path.join(UPLOAD_FOLDER, f))
                            
                            # Ekstrak file backup
                            with zipfile.ZipFile(restore_file, 'r') as zip_ref:
                                zip_ref.extractall(UPLOAD_FOLDER)
                            
                            st.success("Backup berhasil di-restore!")
                            st.balloons()
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Gagal restore: {str(e)}")

# ========== HALAMAN USER ==========
def user_page():
    st.header("Cari Data Peserta 📄")
    
    df = load_all_data()
    if df.empty:
        st.info("Belum ada data yang tersedia.")
        return
    
    # Tampilkan statistik
    show_stats(df)
    
    # Form pencarian canggih
    with st.expander("🔍 Pencarian Lanjutan", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("Cari (Nama/Nopek/Perusahaan/Penanggung/DOB):")
        
        with col2:
            selected_penanggung = st.selectbox(
                "Filter Penanggung:",
                ['Semua'] + sorted(df['PENANGGUNG'].unique().tolist())
            )
    
    # Proses pencarian
    filtered_df = df.copy()
    
    if search_term:
        search_term = search_term.lower()
        filtered_df = filtered_df[
            filtered_df['NAMA'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['NOPEK'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['PERUSAHAAN'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['PENANGGUNG'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['DOB'].astype(str).str.lower().str.contains(search_term)
        ]
    
    if selected_penanggung != 'Semua':
        filtered_df = filtered_df[filtered_df['PENANGGUNG'] == selected_penanggung]
    
    # Tampilkan hasil
    kolom_tampil = ['PERUSAHAAN', 'NOPEK', 'NAMA', 'PENANGGUNG', 'STS', 'DOB', 'KELAS_RAWAT_INAP']
    available_cols = [col for col in kolom_tampil if col in filtered_df.columns]
    
    st.write(f"**Hasil Pencarian:** {len(filtered_df)} data ditemukan")
    
    # Tampilkan data dengan pilihan baris
    edited_df = st.data_editor(
        filtered_df[available_cols],
        use_container_width=True,
        height=400,
        disabled=available_cols,
        column_config={
            "_selected": st.column_config.CheckboxColumn(required=True)
        },
        hide_index=True,
        key="user_data_editor"
    )
    
    # Fungsi klik baris
    if "_selected" in edited_df.columns:
        selected_rows = edited_df[edited_df["_selected"]]
        if not selected_rows.empty:
            selected_row = selected_rows.iloc[0]
            
            with st.expander(f"🔍 Detail Peserta: {selected_row['NAMA']}"):
                st.json(selected_row.to_dict())
                
                # Data terkait
                related_data = df[
                    (df['PENANGGUNG'] == selected_row['PENANGGUNG']) & 
                    (df['NOPEK'] != selected_row['NOPEK'])
                ]
                
                if not related_data.empty:
                    st.write(f"**{len(related_data)} peserta lain dengan penanggung sama:**")
                    st.dataframe(related_data[available_cols], height=200)
                
                # Tombol aksi
                st.download_button(
                    "📥 Ekspor Data Ini",
                    data=selected_row.to_csv(index=False).encode('utf-8'),
                    file_name=f"peserta_{selected_row['NOPEK']}.csv",
                    mime="text/csv"
                )
# ========== MAIN APP ==========
def main():
    st.sidebar.title("Navigasi")
    page = st.sidebar.selectbox("Pilih Mode", ("User", "Admin"))



    # Tambahan fitur di sidebar
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi Cek Kepesertaan v1.2")
   
 # Tambahkan logo di sidebar bawah
    st.sidebar.markdown("---")
    st.sidebar.image("ihc_logo.png", width=150)  # Sesuaikan width sesuai kebutuhan
 
    if page == "Admin":
        st.sidebar.subheader("Login Admin")
        password = st.sidebar.text_input("Password", type="password")
        
        if password == "admin123":
            admin_page()
        elif password:
            st.sidebar.error("Password salah!")
    else:
        user_page()

if __name__ == "__main__":
    main()