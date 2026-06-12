import streamlit as st
import pandas as pd
from collections import Counter

# Set halaman web
st.set_page_config(page_title="Detektor Kemiripan Jawaban", layout="wide")

st.title("📊 Alat Deteksi Kemiripan Jawaban")
st.write("Masukkan data teks mentah Anda untuk melihat siapa yang jawabannya murni vs pasaran.")

# Kotak Input Data
raw_text = st.text_area(
    "Masukkan data teks mentah di sini:",
    height=250,
    placeholder="Contoh:\nElittas\n02 03 07 08 09 20 30 70 80 90\nDrengez\n60 62 63 65 67 68 69 66"
)

if st.button("Analisis Statistik Jawaban", type="primary"):
    if not raw_text.strip():
        st.warning("Silakan masukkan data terlebih dahulu!")
    else:
        # 1. Parsing data teks mentah
        lines = raw_text.strip().split("\n")
        data_orang = []
        current_nama = None

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            # Cek apakah baris ini berisi kumpulan angka atau nama
            tokens = clean_line.split()
            if not tokens[0].isdigit():
                current_nama = clean_line
            else:
                if current_nama:
                    data_orang.append({"nama": current_nama, "angka": tokens})

        if not data_orang:
            st.error("Format teks tidak dikenali. Pastikan selang-seling Nama dan Angka.")
        else:
            # 2. Hitung statistik kemunculan angka
            semua_angka = []
            peta_angka = {} # {angka: [nama1, nama2]}
            
            for orang in data_orang:
                for num in orang["angka"]:
                    semua_angka.append(num)
                    if num not in peta_angka:
                        peta_angka[num] = []
                    if orang["nama"] not in peta_angka[num]:
                        peta_angka[num].append(orang["nama"])

            total_frekuensi = Counter(semua_angka)

            # Buat Kolom Tampilan di Web
            col1, col2 = st.columns(2)

            # --- KOLOM 1: Frekuensi Angka (FORMAT BARU BERDASARKAN JUMLAH PEMILIH) ---
            with col1:
                st.subheader("🔢 Frekuensi Angka Pasaran")
                st.caption("Angka-angka yang memiliki jumlah total pemilih yang sama.")
                
                # Mengelompokkan angka berdasarkan JUMLAH (FREKUENSI) pemilihnya
                # Key: jumlah orang (int), Value: { "angka": [list angka], "nama": set(semua nama unik) }
                peta_jumlah_pemilih = {}
                
                for num, daftar_nama in peta_angka.items():
                    jumlah_pemilih = len(daftar_nama)
                    
                    if jumlah_pemilih not in peta_jumlah_pemilih:
                        peta_jumlah_pemilih[jumlah_pemilih] = {
                            "angka": [],
                            "nama": set()
                        }
                    
                    peta_jumlah_pemilih[jumlah_pemilih]["angka"].append(num)
                    # Gabungkan nama-nama yang memilih angka ini ke dalam set unik
                    peta_jumlah_pemilih[jumlah_pemilih]["nama"].update(daftar_nama)
                
                # Urutkan dari jumlah orang terbanyak ke terkecil
                jumlah_terurut = sorted(peta_jumlah_pemilih.items(), key=lambda x: x[0], reverse=True)
                
                for jumlah_orang, data_kelompok in jumlah_terurut:
                    # Urutkan nama secara alfabetis untuk tampilan
                    daftar_nama_unik = sorted(list(data_kelompok["nama"]))
                    string_nama = ", ".join(daftar_nama_unik)
                    
                    # Urutkan angka dan gabungkan dengan tanda bintang (*)
                    daftar_angka_urut = sorted(data_kelompok["angka"])
                    string_angka = "*".join(daftar_angka_urut)
                    
                    # Tampilan output sesuai request baru
                    st.markdown(f"**Dipilih oleh {jumlah_orang} orang** (`{string_nama}`)")
                    st.markdown(f"👉 **Angka:** `{string_angka}`")
                    st.divider()

            # --- KOLOM 2: Analisis Tingkat Kemiripan ---
            with col2:
                st.subheader("🧐 Indikasi Mencontek / Ikut Arus")
                st.caption("Skor tinggi = hampir semua angkanya sama dengan mayoritas kelompok.")
                
                hasil_orang = []
                for orang in data_orang:
                    total_skor = 0
                    detail_bobot = []
                    
                    for num in orang["angka"]:
                        bobot = len(peta_angka.get(num, []))
                        total_skor += bobot
                        detail_bobot.append(f"{num}({bobot}x)")
                    
                    # Hitung rata-rata ke-pasaran angka yang dia pilih
                    skor_rata_rata = round(total_skor / len(orang["angka"]), 2) if orang["angka"] else 0
                    
                    if skor_rata_rata > 5.0:
                        status = "🔴 Indikasi Contek Tinggi (Sangat Pasaran)"
                    elif skor_rata_rata > 3.0:
                        status = "🟠 Normal / Sama Sebagian"
                    else:
                        status = "🟢 Murni Pikir Sendiri (Unik)"
                        
                    hasil_orang.append({
                        "Nama": orang["nama"],
                        "Skor Pasaran": skor_rata_rata,
                        "Status": status,
                        "Detail": ", ".join(detail_bobot)
                    })
                
                # Urutkan dari skor tertinggi ke terendah
                df_orang = pd.DataFrame(hasil_orang).sort_values(by="Skor Pasaran", ascending=False)
                
                # Tampilkan data dengan visualisasi tabel Streamlit yang rapi
                for index, row in df_orang.iterrows():
                    st.markdown(f"### {row['Nama']}")
                    st.markdown(f"**Skor:** `{row['Skor Pasaran']}` | **Status:** {row['Status']}")
                    st.caption(f"Detail kemunculan angka: [{row['Detail']}]")
                    st.divider()

