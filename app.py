import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# 1. TEMİZLEME MOTORU: İsimleri standartlaştırır
def clean_company_name(name):
    name = str(name).lower()
    
    # Parantezleri ve içindeki sayıları sil
    name = re.sub(r'\(\d+\)', '', name)
    # Noktalama işaretlerini boşluğa çevir
    name = re.sub(r'[^\w\s]', ' ', name)
    
    # Hukuki takıları temizle
    takilar = [r'\bcorp\b', r'\binc\b', r'\bltd\b', r'\bco\b', r'\bplc\b', r'\ba s\b', r'\bs a\b', r'\bcompany\b', r'\bgroup\b', r'\bholding\b', r'\bsystems\b']
    for taki in takilar:
        name = re.sub(taki, '', name)
        
    # Fazlalık boşlukları temizle
    name = " ".join(name.split())
    
    # İsim değişikliklerini ortak dile çevir
    degisimler = {
        'eads': 'Airbus',
        'thomson csf': 'Thales',
        'raytheon': 'RTX',
        'rtx': 'RTX',
        'finmeccanica': 'Leonardo',
        'l 3': 'L3Harris',
        'harris': 'L3Harris',
        'l3harris': 'L3Harris',
        'bae': 'BAE Systems',
        'tai': 'TUSAŞ'
    }
    
    for eski, yeni in degisimler.items():
        if eski in name:
            return yeni
            
    return name.title()

# 2. VERİ TOPLAYICI: Excel'i okur ve filtreler
@st.cache_data
def load_and_merge_excel(file_path="DefNews100.xlsx"):
    try:
        excel_data = pd.read_excel(file_path, sheet_name=None)
        all_data = []
        
        for sheet_name, df in excel_data.items():
            if not str(sheet_name).strip().isdigit():
                continue
            year = int(sheet_name)
            
            cols = df.columns.astype(str).str.lower()
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            rev_col = [c for c in df.columns if 'defence revenue' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_col[0] if rev_col else None
            
            if not (company_col and rank_col and rev_col):
                continue
                
            temp_df = pd.DataFrame()
            temp_df["Yıl"] = [year] * len(df)
            temp_df["Şirket"] = df[company_col].apply(clean_company_name)
            temp_df["Sıralama"] = pd.to_numeric(df[rank_col], errors='coerce')
            temp_df["Savunma Cirosu"] = pd.to_numeric(
                df[rev_col].astype(str).str.replace(',', '').str.replace(' ', ''), 
                errors='coerce'
            )
            
            temp_df = temp_df.dropna(subset=["Şirket", "Sıralama", "Savunma Cirosu"])
            all_data.append(temp_df)

        if all_data:
            merged_df = pd.concat(all_data, ignore_index=True)
            # Aynı yıl içindeki mükerrer kayıtların ortalamasını alarak tekilleştirir
            merged_df = merged_df.groupby(["Şirket", "Yıl"]).mean().reset_index()
            merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
            return merged_df
        return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Veri okunurken hata oluştu: {e}")
        return pd.DataFrame()

# 3. KONTROL PANELİ VE GÖRSELLEŞTİRME
st.title("Tarihsel Performans ve Tahmin Modeli")

df = load_and_merge_excel("DefNews100.xlsx")

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket]
    
    st.subheader(f"{secilen_sirket} Analizi")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gerçek veriler
        fig_ciro = go.Figure()
        fig_ciro.add_trace(go.Scatter(
            x=sirket_verisi["Yıl"], y=sirket_verisi["Savunma Cirosu"],
            mode='lines+markers', name='Gerçekleşen Ciro', line=dict(color='blue')
        ))
        
        # 5 Yıllık Tahmin (Regresyon Modeli)
        if len(sirket_verisi) > 2:
            z = np.polyfit(sirket_verisi["Yıl"], sirket_verisi["Savunma Cirosu"], 1)
            p = np.poly1d(z)
            son_yil = sirket_verisi["Yıl"].max()
            gelecek_yillar = np.array([son_yil + i for i in range(1, 6)])
            tahmini_cirolar = p(gelecek_yillar)
            
            fig_ciro.add_trace(go.Scatter(
                x=gelecek_yillar, y=tahmini_cirolar,
                mode='lines+markers', name='5 Yıllık Tahmin', 
                line=dict(color='red', dash='dash')
            ))
            
        fig_ciro.update_layout(title="Savunma Cirosu & Tahmin", yaxis_title="Ciro (Milyon $)")
        st.plotly_chart(fig_ciro, use_container_width=True)

    with col2:
        # Sıralama grafiği
        fig_siralama = px.line(
            sirket_verisi, x="Yıl", y="Sıralama", markers=True,
            title="Sıralama Değişimi"
        )
        fig_siralama.update_yaxes(autorange="reversed")
        fig_siralama.update_traces(line_color='green')
        st.plotly_chart(fig_siralama, use_container_width=True)
else:
    st.error("Veri işlenemedi. Lütfen dosya adının doğru olduğunu kontrol edin.")
