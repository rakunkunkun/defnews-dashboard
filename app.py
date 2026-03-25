import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# 1. KÖK KELİME MIKNATISI (İsim Standartlaştırma)
ROOT_MAGNETS = {
    'lockheed': 'Lockheed Martin', 'boeing': 'Boeing', 
    'rockwell': 'RTX', 'raytheon': 'RTX', 'rtx': 'RTX', 'united technologies': 'RTX',
    'northrop': 'Northrop Grumman', 'general dy': 'General Dynamics', 
    'bae': 'BAE Systems', 'british aerospace': 'BAE Systems', 'united defense': 'BAE Systems', 'vickers': 'BAE Systems', 
    'eads': 'Airbus', 'airbus': 'Airbus', 'european aeronautic': 'Airbus', 
    'finmeccanica': 'Leonardo', 'leonardo': 'Leonardo', 'agusta': 'Leonardo',
    'thomson': 'Thales', 'thales': 'Thales', 
    'itt': 'L3Harris', 'exelis': 'L3Harris', 'l 3': 'L3Harris', 'l3': 'L3Harris', 'harris': 'L3Harris', 'lharris': 'L3Harris',
    'kongsberg': 'Kongsberg', 'saab': 'Saab', 'dassault': 'Dassault', 'rheinmetall': 'Rheinmetall', 'textron': 'Textron',
    'huntington': 'Huntington Ingalls', 'hii': 'Huntington Ingalls', 'newport news': 'Huntington Ingalls', 
    'rolls': 'Rolls-Royce',
    'el op': 'Elbit Systems', 'elbit': 'Elbit Systems', 
    'rafael': 'Rafael', 
    'israel aerospace': 'IAI', 'iai': 'IAI', 'israel aircraft': 'IAI',
    'israel military': 'IMI Systems', 'imi': 'IMI Systems', 
    'naval group': 'Naval Group', 'dcns': 'Naval Group', 'dcn': 'Naval Group', 'direction des constructions': 'Naval Group', 
    'casic': 'CASIC', 'china aerospace science and industry': 'CASIC', 
    'casc': 'CASC', 'china aerospace science and technology': 'CASC',
    'china north': 'NORINCO', 'norinco': 'NORINCO', 
    'china south': 'CSGC', 'csgc': 'CSGC', 
    'cssc': 'CSSC', 'china state': 'CSSC', 'csic': 'CSSC', 'china shipbuilding industry': 'CSSC',
    'aviation industry of china': 'AVIC', 
    'cobham': 'Cobham', 'curtis': 'Curtiss-Wright', 'curtiss': 'Curtiss-Wright',
    'concern radio': 'KRET', 'kret': 'KRET', 'rdaio': 'KRET', 
    'denel': 'Denel', 'heico': 'HEICO', 
    'ukroboronprom': 'Ukroboronprom', 'ukrainian defense': 'Ukroboronprom', 
    'indra': 'Indra', 'mitsubishi': 'Mitsubishi', 'kawasaki': 'Kawasaki',
    'komatsu': 'Komatsu', 'fuji': 'Fuji', 'hitachi': 'Hitachi', 'toshiba': 'Toshiba', 'nec': 'NEC', 'ishikawajima': 'IHI',
    'ihi': 'IHI', 'booz': 'Booz Allen Hamilton', 
    'computer science': 'CSC', 'csc': 'CSC', 'csra': 'CSC', 'drs': 'DRS Technologies',
    'almaz': 'Almaz-Antey', 'antei': 'Almaz-Antey', 'antey': 'Almaz-Antey', 
    'sukhoi': 'Sukhoi', 'mig': 'MiG', 'irkut': 'Irkut', 'salyut': 'Salyut', 'izhmash': 'Izhmash', 'sevmash': 'Sevmash', 
    'admiralteisk': 'Admiralteiskie Verfi', 'severnaya': 'Severnaya Verf', 
    'russia s helicopter': 'Russian Helicopters', 'russian helicopter': 'Russian Helicopters',
    'tactical missile': 'Tactical Missiles Corp', 'oboronitelniye': 'Tactical Missiles Corp', 
    'united engine': 'United Engine Corp', 'ufa': 'United Engine Corp',
    'alliant': 'Orbital ATK', 'orbital': 'Orbital ATK', 'atk': 'Orbital ATK',
    'smiths': 'Smiths Group', 'babcock': 'Babcock', 'backbock': 'Babcock', 'battelle': 'Battelle', 
    'bearingpoint': 'BearingPoint', 'kpmg': 'BearingPoint', 'bechtel': 'Bechtel', 'bharat': 'Bharat Electronics', 
    'cae': 'CAE', 'chemring': 'Chemring', 'cubic': 'Cubic', 'zimmerman': 'Day & Zimmermann', 'diehl': 'Diehl', 
    'flir': 'FLIR', 'gkn': 'GKN', 'jacobs': 'Jacobs', 'qinetiq': 'QinetiQ', 'sagem': 'SAGEM', 'saic': 'SAIC', 
    'science application': 'SAIC', 'aerospace equipment': 'Aerospace Equipment', 'aerokosmicheskoe': 'Aerospace Equipment', 
    'advanced technical': 'Advanced Technical Products', 'advanced technology': 'Advanced Technology International', 
    'teledyne': 'Teledyne', 'allegheny': 'Teledyne', 'thyssenkrupp': 'ThyssenKrupp', 'ball': 'Ball', 'caci': 'CACI', 
    'aselsan': 'Aselsan', 'roketsan': 'Roketsan', 'havelsan': 'Havelsan', 'hava elektronik': 'Havelsan', 
    'stm': 'STM', 'makine ve kimya': 'MKE', 'bmc': 'BMC', 'askeri fabrika': 'ASFAT', 'fnss': 'FNSS', 
    'tusaş': 'TUSAŞ', 'tusas': 'TUSAŞ', 'tai': 'TUSAŞ', 'turkish aerospace': 'TUSAŞ', 
    'krauss': 'KNDS', 'nexter': 'KNDS', 'giat': 'KNDS', 'knds': 'KNDS', 'korea aerospace': 'KAI', 
    'korean aerospace': 'KAI', 'hanwha': 'Hanwha', 'hyundai': 'Hyundai Rotem', 'rotem': 'Hyundai Rotem', 
    'lig nex': 'LIG Nex1', 'mazagon': 'Mazagon Dock', 'hindustan': 'Hindustan Aeronautics', 'embraer': 'Embraer', 
    'aar': 'AAR', 'aerojet': 'Aerojet Rocketdyne', 'am general': 'AM General', 'amphenol': 'Amphenol', 
    'armor holding': 'Armor Holdings', 'austal': 'Austal', 'bwx': 'BWX Technologies', 'camber': 'Camber', 
    'celsius': 'Celsius', 'dyncorp': 'DynCorp', 'edo': 'EDO', 'eg g': 'EG&G', 'engility': 'Engility', 
    'force protection': 'Force Protection', 'griffon': 'Griffon', 'hensoldt': 'Hensoldt', 'leidos': 'Leidos', 
    'lumen': 'Lumen Technologies', 'maxar': 'Maxar Technologies', 'mercury': 'Mercury Systems', 'mitsui': 'Mitsui', 
    'nammo': 'Nammo', 'palantir': 'Palantir Technologies', 'parker': 'Parker Hannifin', 'parsons': 'Parsons',
    'peraton': 'Peraton', 'perspecta': 'Perspecta', 'primex': 'Primex Technologies', 'serco': 'Serco',
    'sierra nevada': 'Sierra Nevada', 'stork': 'Stork', 'telesat': 'Telesat', 'tenix': 'Tenix', 
    'ultra electronic': 'Ultra Electronics', 'veridian': 'Veridian', 'vse': 'VSE', 'wyle': 'Wyle', 
    'fincantieri': 'Fincantieri', 'cantieri': 'Fincantieri', 
    'priborostroyeniya': 'KBP Instrument Design Bureau', 'instrument design': 'KBP Instrument Design Bureau',
    'john cockerill': 'John Cockerill', 'edge': 'EDGE Group', 'elisra': 'Elisra', 'bazan': 'Navantia', 
    'izar': 'Navantia', 'navantia': 'Navantia', 'ge': 'GE Aerospace', 'general electric': 'GE Aerospace', 
    'oshkosh': 'Oshkosh', 'patria': 'Patria', 'rti': 'RTI', 'sra': 'SRA International', 'src': 'SRC', 
    'st engineering': 'ST Engineering', 'singapore technologies': 'ST Engineering', 'vt': 'VT Group', 
    'vosper thornycroft': 'VT Group'
}

SORTED_MAGNETS = sorted(ROOT_MAGNETS.keys(), key=len, reverse=True)

# 2. ŞİRKET KÜNYE VERİTABANI (Ansiklopedi)
KUNYE_VERITABANI = {
    "Lockheed Martin": {
        "Tam İsim": "Lockheed Martin Corporation", "Ülke": "ABD", 
        "Faaliyet": "Havacılık, Uzay, Füze Sistemleri, Savunma Elektroniği (F-35, HIMARS)",
        "Çalışan": "~122.000 (2024)", "CEO": "James D. Taiclet",
        "Tarihçe & Birleşmeler": "1995 yılında Lockheed Corporation ile Martin Marietta'nın birleşmesiyle kuruldu. Sikorsky'i bünyesine kattı.",
        "Analiz Notu": "Dünyanın tartışmasız en büyük savunma yüklenicisi. Gelirinin yaklaşık %96'sı doğrudan savunma sanayii ve devlet ihalelerinden gelmektedir."
    },
    "RTX": {
        "Tam İsim": "RTX Corporation (Eski adıyla Raytheon Technologies)", "Ülke": "ABD", 
        "Faaliyet": "Füze sistemleri, Havacılık Motorları, Hava Savunma (Patriot, Tomahawk)",
        "Çalışan": "~185.000 (2024)", "CEO": "Gregory J. Hayes",
        "Tarihçe & Birleşmeler": "2020'de Raytheon Company ve United Technologies (Pratt & Whitney, Collins Aerospace) birleşti. 2023'te adını RTX olarak değiştirdi.",
        "Analiz Notu": "Sivil havacılık (motor/aviyonik) ve savunma sistemleri arasında çok dengeli bir gelir yapısına (yaklaşık %55 sivil, %45 savunma) sahiptir."
    },
    "BAE Systems": {
        "Tam İsim": "BAE Systems plc", "Ülke": "İngiltere", 
        "Faaliyet": "Savaş uçakları, Nükleer Denizaltılar, Kara Araçları, Elektronik Harp",
        "Çalışan": "~93.000 (2024)", "CEO": "Charles Woodburn",
        "Tarihçe & Birleşmeler": "1999'da British Aerospace (BAe) ile Marconi Electronic Systems'in birleşmesiyle doğdu. United Defense ve Armor Holdings'i bünyesine katarak ABD pazarında çok büyüdü.",
        "Analiz Notu": "Avrupa'nın en büyük savunma şirketi olmasına rağmen, gelirinin yarısına yakınını ABD Savunma Bakanlığı (Pentagon) sözleşmelerinden elde eder."
    },
    "Aselsan": {
        "Tam İsim": "ASELSAN Elektronik Sanayi ve Ticaret A.Ş.", "Ülke": "Türkiye", 
        "Faaliyet": "Haberleşme, Radar, Elektronik Harp, Elektro-Optik, Komuta Kontrol",
        "Çalışan": "~10.500 (2024)", "CEO": "Ahmet Akyol",
        "Tarihçe & Birleşmeler": "1975 Kıbrıs Barış Harekatı sonrası Türk Silahlı Kuvvetlerini Güçlendirme Vakfı (TSKGV) bünyesinde kuruldu.",
        "Analiz Notu": "Türkiye'nin teknolojik bağımsızlık stratejisinin amiral gemisidir. Küresel Top 100 listesinde en istikrarlı büyüme ivmesine sahip şirketlerden biridir."
    },
    "TUSAŞ": {
        "Tam İsim": "Türk Havacılık ve Uzay Sanayii A.Ş. (TAI)", "Ülke": "Türkiye", 
        "Faaliyet": "Hava Platformları (KAAN, HÜRJET, ATAK), İHA/SİHA (ANKA, AKSUNGUR), Uzay Sistemleri",
        "Çalışan": "~15.000 (2024)", "CEO": "Temel Kotil",
        "Tarihçe & Birleşmeler": "Başlangıçta F-16 üretimi için kurulan TAI ve TUSAŞ, 2005 yılında birleşerek yabancı hisselerden arındırıldı ve millileşti.",
        "Analiz Notu": "Özellikle 5. Nesil savaş uçağı KAAN ve döner kanat platform yatırımları ile Ar-Ge yoğunluğu en yüksek Türk savunma şirketidir."
    },
    "Boeing": {
        "Tam İsim": "The Boeing Company", "Ülke": "ABD", 
        "Faaliyet": "Ticari Uçaklar, Askeri Uçaklar (F-15, F/A-18, Apache), Uzay ve Güvenlik",
        "Çalışan": "~171.000 (2024)", "CEO": "David Calhoun",
        "Tarihçe & Birleşmeler": "1997'de rakibi McDonnell Douglas'ı satın alarak savunma kanadını devasa bir boyuta ulaştırdı.",
        "Analiz Notu": "Ticari uçak pazarındaki dalgalanmalar (737 MAX krizleri vb.) şirketin savunma gelirlerinin toplam ciro içindeki yüzdesini (sivil gelirin düşmesi nedeniyle) suni olarak yükseltmektedir."
    }
}

def clean_company_name(name):
    clean_str = re.sub(r'[^a-z0-9\s]', ' ', str(name).lower())
    for keyword in SORTED_MAGNETS:
        if re.search(r'\b' + keyword + r'\b', clean_str):
            return ROOT_MAGNETS[keyword]
            
    clean_str = re.sub(r'\d+', '', clean_str)
    takilar = [
        r'\bcorp\b', r'\bcorporation\b', r'\binc\b', r'\bltd\b', r'\bco\b', 
        r'\bplc\b', r'\ba s\b', r'\bs a\b', r'\bcompany\b', r'\bgroup\b', 
        r'\bholding\b', r'\bholdings\b', r'\bsystems\b', r'\bllc\b', r'\bspa\b',
        r'\bindustries\b', r'\blimited\b', r'\binternational\b', r'\binter tio l\b'
    ]
    for taki in takilar:
        clean_str = re.sub(taki, '', clean_str)
        
    return " ".join(clean_str.split()).title()

# 3. VERİ TOPLAYICI
@st.cache_data
def load_and_merge_excel(file_path="DefNews100.xlsx", cache_buster="v7"):
    try:
        excel_data = pd.read_excel(file_path, sheet_name=None)
        all_data = []
        
        for sheet_name, df in excel_data.items():
            year_match = re.search(r'(\d{4})', str(sheet_name))
            if not year_match: continue
            year = int(year_match.group(1))
            
            cols = df.columns.astype(str).str.lower()
            company_col = df.columns[cols.str.contains("company")][0] if any(cols.str.contains("company")) else None
            rank_col = [c for c in df.columns if 'rank' in c.lower() and 'last' not in c.lower()]
            rank_col = rank_col[0] if rank_col else None
            rev_cols = [c for c in df.columns if 'defen' in c.lower() and 'rev' in c.lower() and 'change' not in c.lower()]
            rev_col = rev_cols[0] if rev_cols else None
            pct_cols = [c for c in df.columns if 'from' in c.lower() and 'defen' in c.lower()]
            pct_col = pct_cols[0] if pct_cols else None
            
            if not (company_col and rank_col and rev_col): continue
                
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

# 4. KONTROL PANELİ VE GÖRSELLEŞTİRME
st.title("Top 100 Savunma Şirketleri Analizi")

df = load_and_merge_excel("DefNews100.xlsx", cache_buster="v7")

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket].copy()
    
    # ---------------- ŞİRKET KÜNYESİ (YENİ MODÜL) ---------------- #
    if secilen_sirket in KUNYE_VERITABANI:
        k = KUNYE_VERITABANI[secilen_sirket]
        st.info(f"**{k['Tam İsim']} ({k['Ülke']})**\n\n"
                f"👤 **Mevcut CEO:** {k['CEO']} | 👥 **Çalışan:** {k['Çalışan']}\n\n"
                f"⚙️ **Faaliyet Alanı:** {k['Faaliyet']}\n\n"
                f"🔗 **Tarihçe & Birleşmeler:** {k['Tarihçe & Birleşmeler']}\n\n"
                f"📊 **Analitik Not:** {k['Analiz Notu']}")
    else:
        st.warning(f"💡 {secilen_sirket} şirketinin detaylı analiz künyesi henüz sisteme işlenmedi. "
                   "KUNYE_VERITABANI sözlüğüne manuel olarak eklenebilir.")
    # ------------------------------------------------------------- #

    st.markdown("---")
    
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
    
    col1, col2 = st.columns(2)
    with col1:
        fig_ciro = go.Figure()
        fig_ciro.add_trace(go.Scatter(x=sirket_verisi["Yıl"], y=sirket_verisi["Savunma Cirosu"], mode='lines+markers', name='Gerçekleşen Ciro', line=dict(color='#1f77b4', width=3)))
        if tahmin_yapildi:
            fig_ciro.add_trace(go.Scatter(x=gelecek_yillar, y=tahmini_cirolar, mode='lines+markers', name='5 Yıllık Tahmin (Trend)', line=dict(color='#d62728', dash='dot', width=3)))
        fig_ciro.update_layout(title="Savunma Cirosu Değişimi", yaxis_title="Ciro (Milyon $)", hovermode="x unified")
        st.plotly_chart(fig_ciro, use_container_width=True)

    with col2:
        fig_siralama = px.line(sirket_verisi, x="Yıl", y="Sıralama", markers=True, title="Sıralama Değişimi")
        fig_siralama.update_yaxes(autorange="reversed")
        fig_siralama.update_traces(line_color='#2ca02c', line_width=3)
        st.plotly_chart(fig_siralama, use_container_width=True)
        
    st.markdown("---")
    oran_verisi = sirket_verisi.dropna(subset=["Savunma Dışı Oran (%)"]).copy()
    if not oran_verisi.empty:
        fig_oran = px.area(oran_verisi, x="Yıl", y="Savunma Dışı Oran (%)", title="Savunma Dışı (Sivil) Sektörlerden Elde Edilen Gelir Oranı", markers=True, color_discrete_sequence=['#ff7f0e'])
        fig_oran.update_layout(yaxis_title="Sivil Gelir Oranı (%)", yaxis=dict(range=[0, 100]), hovermode="x unified")
        st.plotly_chart(fig_oran, use_container_width=True)
    else:
        st.info("Bu şirket için savunma dışı gelir oranı verisi bulunmuyor veya hesaplanamadı.")

else:
    st.error("Veri işlenemedi. Lütfen 'DefNews100.xlsx' dosyasının doğru konumda olduğundan emin olun.")
