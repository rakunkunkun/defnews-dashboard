import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# 1. DERİN ELEK (Kapsamlı ve Öncelikli Sözlük)
SIEVE = {
    'aselsan': 'Aselsan',
    'roketsan': 'Roketsan',
    'havelsan': 'Havelsan',
    'stm': 'STM',
    'makine ve kimya': 'MKE',
    'bmc': 'BMC',
    'askeri fabrika': 'ASFAT',
    'fnss': 'FNSS',
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
    'l3harris': 'L3Harris',
    
    'kongsberg': 'Kongsberg',
    'saab': 'Saab',
    'dassault': 'Dassault',
    
    'rheinmetall': 'Rheinmetall',
    'textron': 'Textron',
    'huntington': 'Huntington Ingalls',
    'hii': 'Huntington Ingalls',
    
    'rolls-royce': 'Rolls-Royce',
    'rolls royce': 'Rolls-Royce',
    
    'elbit': 'Elbit Systems',
    'rafael': 'Rafael',
    
    'israel aerospace': 'IAI',
    'iai': 'IAI',
    'israel aircraft': 'IAI',
    'israel military': 'IMI Systems',
    'imi systems': 'IMI Systems',
    
    'naval group': 'Naval Group',
    'dcns': 'Naval Group',
    'direction des constructions': 'Naval Group',
    'dcn': 'Naval Group',
    
    'casic': 'CASIC',
    'china aerospace science and industry': 'CASIC',
    
    'casc': 'CASC',
    'china aerospace science and technology': 'CASC',
    
    'china north': 'NORINCO',
    'norinco': 'NORINCO',
    
    'china south': 'CSGC',
    'csgc': 'CSGC',
    
    'china state': 'CSSC',
    'cssc': 'CSSC',
    
    'cobham': 'Cobham',
    
    'concern radio': 'KRET',
    'kret': 'KRET',
    'concern rdaio': 'KRET',
    
    'curtis': 'Curtiss-Wright',
    'curtiss': 'Curtiss-Wright',
    
    'denel': 'Denel',
    'heico': 'HEICO',
    'ukroboronprom': 'Ukroboronprom',
    'indra': 'Indra',
    
    'mitsubishi heavy': 'Mitsubishi Heavy',
    'mitsubishi heaby': 'Mitsubishi Heavy',
    'mitsubishi electric': 'Mitsubishi Electric',
    'mitsubishi': 'Mitsubishi',
    
    'booz allen': 'Booz Allen Hamilton',
    'booz-allen': 'Booz Allen Hamilton',
    
    'caci': 'CACI',
    'computer sciences': 'CSC',
    'csc': 'CSC',
    'csra': 'CSC',
    
    'drs': 'DRS Technologies',
    
    'almaz': 'Almaz-Antey',
    'antei': 'Almaz-Antey',
    'antey': 'Almaz-Antey',
    
    'sukhoi': 'Sukhoi',
    'mig': 'MiG',
    'irkut': 'Irkut',
    
    'alliant techsystems': 'Orbital ATK',
    'orbital': 'Orbital ATK',
    'atk': 'Orbital ATK',
    
    'smiths': 'Smiths Group',
    'babcock': 'Babcock',
    'backbock': 'Babcock',
    
    'battelle': 'Battelle',
    'bearingpoint': 'BearingPoint',
    'bechtel': 'Bechtel',
    'bharat': 'Bharat Electronics',
    'cae': 'CAE',
    'chemring': 'Chemring',
    'cubic': 'Cubic',
    'day & zimmerman': 'Day & Zimmermann',
    'day & zimmermann': 'Day & Zimmermann',
    'diehl': 'Diehl',
    'flir': 'FLIR',
    'gkn': 'GKN',
    'jacobs': 'Jacobs',
    'kawasaki': 'Kawasaki',
    'komatsu': 'Komatsu',
    'nec': 'NEC',
    'oshkosh': 'Oshkosh',
    'qinetiq': 'QinetiQ',
    'sagem': 'SAGEM',
    'saic': 'SAIC',
    'science applications': 'SAIC'
}

# Çakışmaları önlemek için kelimeleri karakter uzunluğuna göre büyükten küçüğe sırala
SORTED_SIEVE_KEYS = sorted(SIEVE.keys(), key=len, reverse=True)

def clean_company_name(name):
    lower_name = str(name).lower()
    
    # 1. Kelime sınırlarıyla (Word Boundary) hassas arama yap
    for keyword in SORTED_SIEVE_KEYS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', lower_name):
            return SIEVE[keyword]
            
    # 2. Özel eşleşme bulunamazsa genel temizlik yap
    name_clean = re.sub(r'\d+', '', lower_name)
    name_clean = re.sub(r'[^\w\s]', ' ', name_clean)
    
    takilar = [
        r'\bcorp\b', r'\bcorporation\b', r'\binc\b', r'\bltd\b', r'\bco\b', 
        r'\bplc\b', r'\ba s\b', r'\bs a\b', r'\bcompany\b', r'\bgroup\b', 
        r'\bholding\b', r'\bholdings\b', r'\bsystems\b', r'\bllc\b', r'\bspa\b',
        r'\bindustries\b', r'\blimited\b'
    ]
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
            year_match = re.search(r'(\d{4})', str(sheet_name))
            if not year_match: 
                continue
            year = int(year_match.group(1))
            
            cols = df.columns.astype(str).str.lower()
            
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            
            rev_cols = [c for c in df.columns if 'defen' in c.lower() and 'rev' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_cols[0] if rev_cols else None
            
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
            
            if pct_col:
                temiz_oran = df[pct_col].astype(str).str.replace('%', '', regex=False)
                savunma_orani = pd.to_numeric(temiz_oran, errors='coerce')
                savunma_orani = savunma_orani.apply(lambda x: x * 100 if pd.notnull(x) and x <= 1.0 else x)
                temp_df["Savunma Dışı Oran (%)"] = 100 - savunma_orani
            else:
                temp_df["Savunma Dışı Oran (%)"] = np.nan
            
            temp_df = temp_df.dropna(subset=["Şirket", "Sıralama", "Savunma Cirosu"])
            all_data.append(temp_df)
            
    except Exception as e:
        st.error(f"Excel okunurken hata oluştu: {e}")
        return pd.DataFrame()

    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df = merged_df.groupby(["Şirket", "Yıl"]).mean().reset_index()
        merged_df = merged_df.sort_values(by=["Şirket", "Yıl"])
        return merged_df
    return pd.DataFrame()

# 3. KONTROL PANELİ VE GÖRSELLEŞTİRME
st.title("Tarihsel Performans ve 5 Yıllık Tahmin")

df = load_and_merge_excel("DefNews100.xlsx")

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket].copy()
    
    st.markdown("---")
    
    # TAHMİN (FORECASTING) - AĞIRLIKLI MOTOR
    tahmin_yapildi = False
    if len(sirket_verisi) > 2:
        yillar = sirket_verisi["Yıl"].values
        cirolar = sirket_verisi["Savunma Cirosu"].values
        son_yil = int(np.max(yillar))
        
        son_ciro_row = sirket_verisi[sirket_verisi["Yıl"] == son_yil]
        son_ciro = son_ciro_row["Savunma Cirosu"].values[0] if not son_ciro_row.empty else cirolar[-1]
        
        agirliklar = np.exp((yillar - son_yil) / 4.0)
        
        z = np.polyfit(yillar, cirolar, 1, w=agirliklar)
        p = np.poly1d(z)
        
        gelecek_yillar = np.array([son_yil + i for i in range(1, 6)])
        tahmini_cirolar = p(gelecek_yillar)
        hedef_yil = gelecek_yillar[-1]
        hedef_ciro = tahmini_cirolar[-1]
        tahmin_yapildi = True

        st.subheader("Gelecek 5 Yıl Projeksiyonu (Güncel İvme Ağırlıklı)")
        met1, met2, met3 = st.columns(3)
        met1.metric(label=f"Son Gerçekleşen Ciro ({son_yil})", value=f"${son_ciro:,.0f} M")
        met2.metric(label=f"Tahmini Ciro ({hedef_yil})", value=f"${hedef_ciro:,.0f} M", delta=f"{hedef_ciro - son_ciro:,.0f} M Büyüme")
        met3.metric(label="Mevcut Yıllık İvme Hızı", value=f"${z[0]:,.0f} M / Yıl")
    
    st.markdown("---")
    
    # GRAFİKLER
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
                mode='lines+markers', name='5 Yıllık Tahmin (Trend)', 
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
        
    st.markdown("---")
    oran_verisi = sirket_verisi.dropna(subset=["Savunma Dışı Oran (%)"]).copy()
    
    if not oran_verisi.empty:
        fig_oran = px.area(
            oran_verisi, x="Yıl", y="Savunma Dışı Oran (%)",
            title="Savunma Dışı (Sivil) Sektörlerden Elde Edilen Gelir Oranı",
            markers=True, color_discrete_sequence=['#ff7f0e']
        )
        fig_oran.update_layout(yaxis_title="Sivil Gelir Oranı (%)", yaxis=dict(range=[0, 100]), hovermode="x unified")
        st.plotly_chart(fig_oran, use_container_width=True)
    else:
        st.info("Bu şirket için savunma dışı gelir oranı verisi bulunmuyor veya hesaplanamadı.")

else:
    st.error("Veri işlenemedi. Lütfen 'DefNews100.xlsx' dosyasının doğru konumda olduğundan emin olun.")
