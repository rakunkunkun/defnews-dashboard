import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# 1. AKILLI ELEK: Kök kelimelere göre isim birleştirme
# Soldaki kelime veri setinde geçiyorsa, sağdaki standart isme dönüştürülür.
SIEVE = {
    'aselsan': 'Aselsan',
    'roketsan': 'Roketsan',
    'havelsan': 'Havelsan',
    'stm': 'STM',
    'tai': 'TUSAŞ',
    'tusaş': 'TUSAŞ',
    'turkish aerospace': 'TUSAŞ',
    'lockheed': 'Lockheed Martin',
    'boeing': 'Boeing',
    'raytheon': 'RTX',
    'rtx': 'RTX',
    'united technologies': 'RTX',
    'northrop': 'Northrop Grumman',
    'general dynamics': 'General Dynamics',
    'bae': 'BAE Systems',
    'british aerospace': 'BAE Systems',
    'eads': 'Airbus',
    'airbus': 'Airbus',
    'finmeccanica': 'Leonardo',
    'leonardo': 'Leonardo',
    'thomson': 'Thales',
    'thales': 'Thales',
    'l-3': 'L3Harris',
    'l3': 'L3Harris',
    'harris': 'L3Harris',
    'kongsberg': 'Kongsberg',
    'saab': 'Saab',
    'dassault': 'Dassault',
    'rheinmetall': 'Rheinmetall',
    'textron': 'Textron',
    'huntington': 'Huntington Ingalls',
    'rolls-royce': 'Rolls-Royce',
    'rolls royce': 'Rolls-Royce',
    'mitsubishi': 'Mitsubishi',
    'elbit': 'Elbit Systems',
    'rafael': 'Rafael',
    'israel aerospace': 'IAI',
    'iai': 'IAI',
    'naval group': 'Naval Group',
    'dcns': 'Naval Group'
}

def clean_company_name(name):
    lower_name = str(name).lower()
    
    # Önce sözlükteki kök kelimeleri ara
    for keyword, standard_name in SIEVE.items():
        if keyword in lower_name:
            return standard_name
            
    # Sözlükte yoksa, genel temizlik yap (Rakamları, parantezleri ve şirket takılarını at)
    name_clean = re.sub(r'\(\d+\)', '', lower_name)
    name_clean = re.sub(r'[^\w\s]', ' ', name_clean)
    takilar = [r'\bcorp\b', r'\binc\b', r'\bltd\b', r'\bco\b', r'\bplc\b', r'\ba s\b', r'\bs a\b', r'\bcompany\b', r'\bgroup\b']
    for taki in takilar:
        name_clean = re.sub(taki, '', name_clean)
        
    return " ".join(name_clean.split()).title()

# 2. VERİ TOPLAYICI
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
            merged_df = merged_df.groupby(["Şirket", "Yıl"]).mean().reset_index()
            merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
            return merged_df
        return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Veri okunurken hata oluştu: {e}")
        return pd.DataFrame()

# 3. KONTROL PANELİ VE GÖRSELLEŞTİRME
st.title("Tarihsel Performans ve 5 Yıllık Tahmin")

df = load_and_merge_excel("DefNews100.xlsx")

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket]
    
    st.markdown("---")
    
    # TAHMİN (FORECASTING) HESAPLAMALARI
    tahmin_yapildi = False
    if len(sirket_verisi) > 2:
        z = np.polyfit(sirket_verisi["Yıl"], sirket_verisi["Savunma Cirosu"], 1)
        p = np.poly1d(z)
        son_yil = int(sirket_verisi["Yıl"].max())
        son_ciro = sirket_verisi[sirket_verisi["Yıl"] == son_yil]["Savunma Cirosu"].values[0]
        
        gelecek_yillar = np.array([son_yil + i for i in range(1, 6)])
        tahmini_cirolar = p(gelecek_yillar)
        hedef_yil = gelecek_yillar[-1]
        hedef_ciro = tahmini_cirolar[-1]
        tahmin_yapildi = True

        # Rakamsal Özet Paneli
        st.subheader("Gelecek 5 Yıl Projeksiyonu")
        met1, met2, met3 = st.columns(3)
        met1.metric(label=f"Son Gerçekleşen Ciro ({son_yil})", value=f"${son_ciro:,.0f} M")
        met2.metric(label=f"Tahmini Ciro ({hedef_yil})", value=f"${hedef_ciro:,.0f} M", delta=f"{hedef_ciro - son_ciro:,.0f} M Büyüme")
        met3.metric(label="Yıllık Ortalama İvme", value=f"${z[0]:,.0f} M / Yıl")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ciro ve Tahmin Grafiği
        fig_ciro = go.Figure()
        fig_ciro.add_trace(go.Scatter(
            x=sirket_verisi["Yıl"], y=sirket_verisi["Savunma Cirosu"],
            mode='lines+markers', name='Gerçekleşen Ciro', line=dict(color='#1f77b4', width=3)
        ))
        
        if tahmin_yapildi:
            fig_ciro.add_trace(go.Scatter(
                x=gelecek_yillar, y=tahmini_cirolar,
                mode='lines+markers', name='5 Yıllık Tahmin Modeli', 
                line=dict(color='#d62728', dash='dot', width=3)
            ))
            
        fig_ciro.update_layout(title="Savunma Cirosu Değişimi", yaxis_title="Ciro (Milyon $)", hovermode="x unified")
        st.plotly_chart(fig_ciro, use_container_width=True)

    with col2:
        # Sıralama grafiği
        fig_siralama = px.line(
            sirket_verisi, x="Yıl", y="Sıralama", markers=True,
            title="Sıralama Değişimi"
        )
        fig_siralama.update_yaxes(autorange="reversed")
        fig_siralama.update_traces(line_color='#2ca02c', line_width=3)
        st.plotly_chart(fig_siralama, use_container_width=True)
else:
    st.error("Veri işlenemedi. 'DefNews100.xlsx' dosyasının GitHub'da olduğundan emin olun.")
