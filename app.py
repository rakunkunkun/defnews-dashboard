import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import re
import os

# 1. TOPLAYICI: Veriyi okuma ve temizleme kısmı (Performans için önbelleğe alınır)
@st.cache_data
def load_and_merge_data(folder_path="."):
    all_data = []
    
    # Klasördeki tüm ilgili CSV dosyalarını bul
    file_pattern = os.path.join(folder_path, "DefNews100.xlsx - *.csv")
    files = glob.glob(file_pattern)
    
    for file in files:
        try:
            # Dosya adından yılı çıkar (Örn: "DefNews100.xlsx - 2023.csv" -> 2023)
            year_match = re.search(r'- (\d{4})\.csv', file)
            if not year_match:
                continue
            year = int(year_match.group(1))
            
            # Veriyi oku
            df = pd.read_csv(file)
            
            # Sütunları standartlaştırmak için esnek arama yap
            cols = df.columns.astype(str).str.lower()
            
            # Şirket ve Ülke sütunlarını bul
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            country_col = df.columns[cols.str.contains("country")][0] if any(cols.str.contains("country")) else None
            
            # Sıralama sütununu bul (İçinde 'rank' geçen ve 'last' geçmeyen ilk sütun)
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            
            # Ciro sütununu bul (İçinde 'defence revenue' geçen ve 'change' geçmeyen)
            rev_col = [c for c in df.columns if 'defence revenue' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_col[0] if rev_col else None
            
            if not (company_col and rank_col and rev_col):
                continue # Gerekli temel sütunlar yoksa bu dosyayı atla
                
            # İhtiyaç duyulan verileri alıp standart isimlere ata
            temp_df = pd.DataFrame()
            temp_df["Yıl"] = [year] * len(df)
            temp_df["Şirket"] = df[company_col].astype(str).str.strip()
            temp_df["Ülke"] = df[country_col] if country_col else "Bilinmiyor"
            
            # Sıralamayı sayısal değere çevir (NEW, NR gibi metinleri NaN yapar)
            temp_df["Sıralama"] = pd.to_numeric(df[rank_col], errors='coerce')
            
            # Ciroyu temizle ve sayısal değere çevir (Virgülleri ve boşlukları at)
            temp_df["Savunma Cirosu"] = pd.to_numeric(
                df[rev_col].astype(str).str.replace(',', '').str.replace(' ', ''), 
                errors='coerce'
            )
            
            # Hatalı/Boş şirket satırlarını temizle
            temp_df = temp_df.dropna(subset=["Şirket", "Sıralama", "Savunma Cirosu"])
            all_data.append(temp_df)
            
        except Exception as e:
            st.warning(f"Dosya okunurken hata: {file} - Detay: {e}")

    # Tüm yılları tek bir tabloda birleştir
    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        # Yıla göre sırala
        merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
        return merged_df
    else:
        return pd.DataFrame()

# 2. KONTROL PANELİ: Arayüz ve Seçim
st.title("Defence News Top 100 Analizi")

# Veriyi yükle
df = load_and_merge_data()

if df.empty:
    st.error("Veri bulunamadı veya işlenemedi. CSV dosyalarının programla aynı klasörde olduğundan emin olun.")
else:
    # Şirket listesini oluştur (Alfabetik sırada)
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    
    # Sadece seçilen şirketin verilerini filtrele
    sirket_verisi = df[df["Şirket"] == secilen_sirket]
    
    # 3. GÖRSELLEŞTİRİCİ: Grafikler
    st.subheader(f"{secilen_sirket} - Tarihsel Performans")
    
    # Düzen için iki kolon oluştur
    col1, col2 = st.columns(2)
    
    with col1:
        # Ciro Grafiği
        fig_ciro = px.line(
            sirket_verisi, 
            x="Yıl", 
            y="Savunma Cirosu", 
            markers=True,
            title="Savunma Cirosu Değişimi",
            labels={"Savunma Cirosu": "Ciro (Milyon $)"}
        )
        st.plotly_chart(fig_ciro, use_container_width=True)

    with col2:
        # Sıralama Grafiği (Y ekseni ters çevrilir, 1 numara en üstte olmalıdır)
        fig_siralama = px.line(
            sirket_verisi, 
            x="Yıl", 
            y="Sıralama", 
            markers=True,
            title="Sıralama Değişimi"
        )
        fig_siralama.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_siralama, use_container_width=True)
