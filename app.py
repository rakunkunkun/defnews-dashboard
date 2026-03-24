import streamlit as st
import pandas as pd
import plotly.express as px

# 1. TOPLAYICI: Excel dosyasını okuma
@st.cache_data
def load_and_merge_excel(file_path="DefNews100.xlsx"):
    try:
        # Excel'deki tüm sayfaları oku (Her yılın ayrı bir sayfa olduğu varsayımıyla)
        excel_data = pd.read_excel(file_path, sheet_name=None)
        all_data = []
        
        for sheet_name, df in excel_data.items():
            # Sayfa adından yılı al (Sadece rakam olan sayfaları işleme al)
            if not str(sheet_name).strip().isdigit():
                continue
            year = int(sheet_name)
            
            # Sütunları standartlaştırmak için esnek arama yap
            cols = df.columns.astype(str).str.lower()
            
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            country_col = df.columns[cols.str.contains("country")][0] if any(cols.str.contains("country")) else None
            
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            
            rev_col = [c for c in df.columns if 'defence revenue' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_col[0] if rev_col else None
            
            if not (company_col and rank_col and rev_col):
                continue
                
            temp_df = pd.DataFrame()
            temp_df["Yıl"] = [year] * len(df)
            temp_df["Şirket"] = df[company_col].astype(str).str.strip()
            temp_df["Ülke"] = df[country_col] if country_col else "Bilinmiyor"
            temp_df["Sıralama"] = pd.to_numeric(df[rank_col], errors='coerce')
            
            # Ciroyu temizle ve sayısal değere çevir
            temp_df["Savunma Cirosu"] = pd.to_numeric(
                df[rev_col].astype(str).str.replace(',', '').str.replace(' ', ''), 
                errors='coerce'
            )
            
            temp_df = temp_df.dropna(subset=["Şirket", "Sıralama", "Savunma Cirosu"])
            all_data.append(temp_df)

        if all_data:
            merged_df = pd.concat(all_data, ignore_index=True)
            merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
            return merged_df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Veri okunurken hata oluştu: {e}")
        return pd.DataFrame()

# 2. KONTROL PANELİ
st.title("Defence News Top 100 Analizi")

# Dosya isminin GitHub'daki isimle birebir aynı (büyük/küçük harf dahil) olduğundan emin ol
df = load_and_merge_excel("DefNews100.xlsx")

if df.empty:
    st.error("Veri işlenemedi. 'DefNews100.xlsx' dosyasının GitHub'da olduğundan emin olun.")
else:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    
    sirket_verisi = df[df["Şirket"] == secilen_sirket]
    
    # 3. GÖRSELLEŞTİRİCİ
    st.subheader(f"{secilen_sirket} - Tarihsel Performans")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ciro = px.line(
            sirket_verisi, x="Yıl", y="Savunma Cirosu", markers=True,
            title="Savunma Cirosu Değişimi", labels={"Savunma Cirosu": "Ciro (Milyon $)"}
        )
        st.plotly_chart(fig_ciro, use_container_width=True)

    with col2:
        fig_siralama = px.line(
            sirket_verisi, x="Yıl", y="Sıralama", markers=True,
            title="Sıralama Değişimi"
        )
        fig_siralama.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_siralama, use_container_width=True)
