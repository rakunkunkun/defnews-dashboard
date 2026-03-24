import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
import glob

# 1. AKILLI ELEK
SIEVE = {
    'aselsan': 'Aselsan',
    'roketsan': 'Roketsan',
    'havelsan': 'Havelsan',
    'stm': 'STM',
    'makine ve kimya': 'MKE',
    'bmc': 'BMC',
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
    'dcns': 'Naval Group',
    'casic': 'CASIC',
    'china aerospace': 'CASIC'
}

def clean_company_name(name):
    lower_name = str(name).lower()
    for keyword, standard_name in SIEVE.items():
        if keyword in lower_name:
            return standard_name
            
    name_clean = re.sub(r'\(\d+\)', '', lower_name)
    name_clean = re.sub(r'[^\w\s]', ' ', name_clean)
    takilar = [r'\bcorp\b', r'\binc\b', r'\bltd\b', r'\bco\b', r'\bplc\b', r'\ba s\b', r'\bs a\b', r'\bcompany\b', r'\bgroup\b']
    for taki in takilar:
        name_clean = re.sub(taki, '', name_clean)
        
    return " ".join(name_clean.split()).title()

# 2. VERİ TOPLAYICI
@st.cache_data
def load_and_merge_data():
    all_data = []
    files = glob.glob("*DefNews*.csv")
    
    if not files:
        return pd.DataFrame()
        
    for file in files:
        try:
            year_match = re.search(r'(\d{4})', file)
            if not year_match: continue
            year = int(year_match.group(1))
            
            df = pd.read_csv(file)
            cols = df.columns.astype(str).str.lower()
            
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            
            rev_cols = [c for c in df.columns if 'defen' in c.lower() and 'rev' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_cols[0] if rev_cols else None
            
            # Oran sütununu bul ("from" ve "defen" kelimeleri genelde bu sütundadır)
            pct_cols = [c for c in df.columns if 'from' in c.lower() and 'defen' in c.lower()]
            pct_col = pct_cols[0] if pct_cols else None
            
            if not (company_col and rank_col and rev_col):
                continue
                
            temp_df = pd.DataFrame()
            temp_df["Yıl"] = [year] * len(df)
            temp_df["Şirket"] = df[company_col].apply(clean_company_name)
            temp_df["Sıralama"] = pd.to_numeric(df[rank_col], errors='coerce')
            
            temiz_ciro = df[rev_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace(' ', '', regex=False)
            temp_df["Savunma Cirosu"] = pd.to_numeric(temiz_ciro, errors='coerce')
            temp_df.loc[temp_df["Savunma Cirosu"] > 1000000, "Savunma Cirosu"] /= 1000000
            
            # SAVUNMA DIŞI (SİVİL) GELİR HESAPLAMASI
            if pct_col:
                temiz_oran = df[pct_col].astype(str).str.replace('%', '', regex=False)
                savunma_orani = pd.to_numeric(temiz_oran, errors='coerce')
                
                # Değer 1'den küçükse (Örn: 0.96) bunu yüzdeye (96) çevir.
                savunma_orani = savunma_orani.apply(lambda x: x * 100 if pd.notnull(x) and x <= 1.0 else x)
                
                # 100'den çıkararak Sivil Oranı bul
                temp_df["Savunma Dışı Oran (%)"] = 100 - savunma_orani
            else:
                temp_df["Savunma Dışı Oran (%)"] = np.nan
            
            temp_df = temp_df.dropna(subset=["Şirket", "Sıralama", "Savunma Cirosu"])
            all_data.append(temp_df)
            
        except Exception as e:
            continue

    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df = merged_df.groupby(["Şirket", "Yıl"]).mean().reset_index()
        merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
        return merged_df
    return pd.DataFrame()

# 3. KONTROL PANELİ VE GÖRSELLEŞTİRME
st.title("Tarihsel Performans ve 5 Yıllık Tahmin")

df = load_and_merge_data()

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket].copy()
    
    st.markdown("---")
    
    # TAHMİN (FORECASTING)
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

        st.subheader("Gelecek 5 Yıl Projeksiyonu")
        met1, met2, met3 = st.columns(3)
        met1.metric(label=f"Son Gerçekleşen Ciro ({son_yil})", value=f"${son_ciro:,.0f} M")
        met2.metric(label=f"Tahmini Ciro ({hedef_yil})", value=f"${hedef_ciro:,.0f} M", delta=f"{hedef_ciro - son_ciro:,.0f} M Büyüme")
        met3.metric(label="Yıllık Ortalama İvme", value=f"${z[0]:,.0f} M / Yıl")
    
    st.markdown("---")
    
    # 1. SATIR: CİRO VE SIRALAMA
    col1, col2 = st.columns(2)
    with col1:
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
        fig_siralama = px.line(
            sirket_verisi, x="Yıl", y="Sıralama", markers=True,
            title="Sıralama Değişimi"
        )
        fig_siralama.update_yaxes(autorange="reversed")
        fig_siralama.update_traces(line_color='#2ca02c', line_width=3)
        st.plotly_chart(fig_siralama, use_container_width=True)
        
    # 2. SATIR: SAVUNMA DIŞI (SİVİL) GELİR ORANI
    st.markdown("---")
    
    # Sadece oran verisi hesaplanabilen yılları filtrele
    oran_verisi = sirket_verisi.dropna(subset=["Savunma Dışı Oran (%)"]).copy()
    
    if not oran_verisi.empty:
        fig_oran = px.area(
            oran_verisi, 
            x="Yıl", 
            y="Savunma Dışı Oran (%)",
            title="Savunma Dışı (Sivil) Sektörlerden Elde Edilen Gelir Oranı",
            markers=True,
            color_discrete_sequence=['#ff7f0e'] # Turuncu renk
        )
        fig_oran.update_layout(
            yaxis_title="Sivil Gelir Oranı (%)",
            yaxis=dict(range=[0, 100]), # Oran grafiği her zaman 0-100 arasında sabitlenir
            hovermode="x unified"
        )
        st.plotly_chart(fig_oran, use_container_width=True)
    else:
        st.info("Bu şirket için savunma dışı gelir oranı verisi bulunmuyor veya hesaplanamadı.")

else:
    st.error("Veri işlenemedi. Lütfen klasörde CSV dosyalarının olduğundan emin olun.")
