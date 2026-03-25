import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# 1. KÖK KELİME MIKNATISI (Tüm Varyasyonlar ve Çift İsimler Temizlendi)
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
    'huntington': 'Huntington Ingalls', 'hii': 'Huntington Ingalls', 'newport news': 'Huntington Ingalls', 'hunting': 'Hunting', 
    'rolls': 'Rolls-Royce',
    'el op': 'Elbit Systems', 'elbit': 'Elbit Systems', 'tadiran': 'Elbit Systems', 'elisra': 'Elbit Systems',
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
    'indra': 'Indra', 
    'mitsubishi': 'Mitsubishi', 'misubishi': 'Mitsubishi', 'mitsui': 'Mitsui', 
    'itochu': 'Itochu', 'kawasaki': 'Kawasaki', 'komatsu': 'Komatsu', 'fuji': 'Fuji', 'hitachi': 'Hitachi', 'toshiba': 'Toshiba', 
    'nec': 'NEC', 'ishikawajima': 'IHI', 'ihi': 'IHI', 
    'booz': 'Booz Allen Hamilton', 'computer science': 'CSC', 'csc': 'CSC', 'csra': 'CSC', 'drs': 'DRS Technologies',
    'almaz': 'Almaz-Antey', 'antei': 'Almaz-Antey', 'antey': 'Almaz-Antey', 
    'sukhoi': 'Sukhoi', 'mig': 'MiG', 'irkut': 'Irkut', 'salyut': 'Salyut', 'izhmash': 'Izhmash', 'sevmash': 'Sevmash', 
    'admiralteisk': 'Admiralteiskie Verfi', 'severnaya': 'Severnaya Verf', 
    'russia s helicopter': 'Russian Helicopters', 'russian helicopter': 'Russian Helicopters',
    'tactical missile': 'Tactical Missiles Corp', 'oboronitelniye': 'Tactical Missiles Corp', 
    'united engine': 'United Engine Corp', 'ufa': 'United Engine Corp',
    'alliant': 'Orbital ATK', 'orbital': 'Orbital ATK', 'atk': 'Orbital ATK',
    'smiths': 'Smiths Group', 'babcock': 'Babcock', 'backbock': 'Babcock', 'battelle': 'Battelle', 
    'bearingpoint': 'BearingPoint', 'kpmg': 'BearingPoint', 'bechtel': 'Bechtel', 'bharat': 'Bharat Electronics', 
    'cae': 'CAE', 'chemring': 'Chemring', 'cubic': 'Cubic', 
    'zimmermann': 'Day & Zimmermann', 'zimmerman': 'Day & Zimmermann', 'day &': 'Day & Zimmermann',
    'diehl': 'Diehl', 'flir': 'FLIR', 'gkn': 'GKN', 'jacobs': 'Jacobs', 'qinetiq': 'QinetiQ', 
    'sagem': 'Safran', 'safran': 'Safran', 'sextant': 'Safran',
    'saic': 'SAIC', 'science application': 'SAIC', 'aerospace equipment': 'Aerospace Equipment', 'aerokosmicheskoe': 'Aerospace Equipment', 
    'advanced technical': 'Advanced Technical Products', 'advanced technology': 'Advanced Technology International', 
    'teledyne': 'Teledyne', 'allegheny': 'Teledyne', 
    'thyssenkrupp': 'ThyssenKrupp', 'ball': 'Ball', 'caci': 'CACI', 
    'aselsan': 'Aselsan', 'roketsan': 'Roketsan', 'havelsan': 'Havelsan', 'hava elektronik': 'Havelsan', 
    'stm': 'STM', 'makine ve kimya': 'MKE', 'bmc': 'BMC', 'askeri fabrika': 'ASFAT', 'fnss': 'FNSS', 
    'tusaş': 'TUSAŞ', 'tusas': 'TUSAŞ', 'tai': 'TUSAŞ', 'turkish aerospace': 'TUSAŞ', 
    'krauss': 'KNDS', 'nexter': 'KNDS', 'giat': 'KNDS', 'knds': 'KNDS', 'korea aerospace': 'KAI', 'korean aerospace': 'KAI', 
    'hanwha': 'Hanwha', 'hyundai': 'Hyundai Rotem', 'rotem': 'Hyundai Rotem', 'lig nex': 'LIG Nex1', 'mazagon': 'Mazagon Dock', 
    'hindustan': 'Hindustan Aeronautics', 'embraer': 'Embraer', 'aar': 'AAR', 'aerojet': 'Aerojet Rocketdyne', 
    'am general': 'AM General', 'amphenol': 'Amphenol', 'armor holding': 'Armor Holdings', 'austal': 'Austal', 
    'bwx': 'BWX Technologies', 'camber': 'Camber', 'celsius': 'Celsius', 'dyncorp': 'DynCorp', 'edo': 'EDO', 
    'eg g': 'EG&G', 'engility': 'Engility', 'force protection': 'Force Protection', 'griffon': 'Griffon', 'hensoldt': 'Hensoldt', 
    'leidos': 'Leidos', 'lumen': 'Lumen Technologies', 'maxar': 'Maxar Technologies', 'mercury': 'Mercury Systems',
    'nammo': 'Nammo', 'palantir': 'Palantir Technologies', 'parker': 'Parker Hannifin', 'parsons': 'Parsons',
    'peraton': 'Peraton', 'perspecta': 'Perspecta', 'primex': 'Primex Technologies', 'serco': 'Serco',
    'sierra nevada': 'Sierra Nevada', 'stork': 'Stork', 'telesat': 'Telesat', 'tenix': 'Tenix', 
    'ultra electronic': 'Ultra Electronics', 'veridian': 'Veridian', 'vse': 'VSE', 'wyle': 'Wyle', 
    'fincantieri': 'Fincantieri', 'cantieri': 'Fincantieri', 
    'priborostroyeniya': 'KBP Instrument Design Bureau', 'instrument design': 'KBP Instrument Design Bureau',
    'john cockerill': 'John Cockerill', 'edge': 'EDGE Group', 'bazan': 'Navantia', 'izar': 'Navantia', 'navantia': 'Navantia', 
    'ge': 'GE Aerospace', 'general electric': 'GE Aerospace', 'oshkosh': 'Oshkosh', 'patria': 'Patria', 'rti': 'RTI', 
    'sra': 'SRA International', 'src': 'SRC', 'st engineering': 'ST Engineering', 'singapore technologies': 'ST Engineering', 
    'vt': 'VT Group', 'vosper': 'VT Group'
}

SORTED_MAGNETS = sorted(ROOT_MAGNETS.keys(), key=len, reverse=True)

# 2. ŞİRKET KÜNYE VERİTABANI (Kapsamlı Sürüm)
KUNYE_VERITABANI = {
    "Lockheed Martin": {
        "Tam İsim": "Lockheed Martin Corporation", "Ülke": "ABD", "CEO": "James D. Taiclet", "Çalışan": "~122.000",
        "Faaliyet": "Havacılık, Uzay, Füze Sistemleri, Savunma Elektroniği",
        "Tarihçe & Birleşmeler": "1995'te Lockheed Corp. ve Martin Marietta birleşti. 2015'te Sikorsky Aircraft bünyeye katıldı.",
        "En Bilinen Ürünler/Markalar": "F-35 Lightning II, F-16, HIMARS, PAC-3 füzeleri, Black Hawk helikopterleri",
        "Analiz Notu": "Cironun büyük bölümü ABD devleti ile yapılan platform sözleşmelerine dayanır. Sivil pazar ağırlığı düşüktür."
    },
    "RTX": {
        "Tam İsim": "RTX Corporation (Eski: Raytheon Technologies)", "Ülke": "ABD", "CEO": "Christopher T. Calio", "Çalışan": "~185.000",
        "Faaliyet": "Hava Savunma, Havacılık Motorları, Aviyonik",
        "Tarihçe & Birleşmeler": "2020'de Raytheon ve United Technologies birleşti. 2023'te RTX adını aldı.",
        "En Bilinen Ürünler/Markalar": "Patriot hava savunma sistemi, Tomahawk füzeleri, Pratt & Whitney motorları, Collins aviyonikleri",
        "Analiz Notu": "Askeri ve sivil havacılık portföyü dengelidir. Pratt & Whitney motor arızaları son dönemde sivil bilançosunu etkilemiştir."
    },
    "BAE Systems": {
        "Tam İsim": "BAE Systems plc", "Ülke": "İngiltere", "CEO": "Charles Woodburn", "Çalışan": "~93.000",
        "Faaliyet": "Savaş Uçakları, Denizaltı, Kara Araçları, Elektronik Harp",
        "Tarihçe & Birleşmeler": "1999'da British Aerospace ve Marconi birleşti. ABD'li United Defense ve Armor Holdings satın alındı.",
        "En Bilinen Ürünler/Markalar": "Eurofighter Typhoon (ortak), Bradley zırhlı araçları, Astute sınıfı denizaltılar",
        "Analiz Notu": "İngiltere merkezli olmasına rağmen, ABD Savunma Bakanlığı ihalelerinden elde ettiği gelir toplam cirosunda yüksek ağırlığa sahiptir."
    },
    "Northrop Grumman": {
        "Tam İsim": "Northrop Grumman Corporation", "Ülke": "ABD", "CEO": "Kathy J. Warden", "Çalışan": "~101.000",
        "Faaliyet": "Stratejik Bombardıman, Otonom Sistemler, Uzay, Radarlar",
        "Tarihçe & Birleşmeler": "1994'te Northrop ve Grumman birleşti. 2018'de Orbital ATK satın alındı.",
        "En Bilinen Ürünler/Markalar": "B-21 Raider, B-2 Spirit, RQ-4 Global Hawk, AESA radarları, James Webb Uzay Teleskobu (katkı)",
        "Analiz Notu": "Havacılık tasarımları, sensör mimarileri ve uzay fırlatma sistemlerinde yoğunlaşmaktadır."
    },
    "General Dynamics": {
        "Tam İsim": "General Dynamics Corporation", "Ülke": "ABD", "CEO": "Phebe N. Novakovic", "Çalışan": "~100.000",
        "Faaliyet": "Denizaltı, Kara Araçları, Sivil Havacılık, Bilişim",
        "Tarihçe & Birleşmeler": "Uçak bölümünü geçmişte Lockheed'e devretmiş, kara, deniz ve IT sistemlerine odaklanmıştır.",
        "En Bilinen Ürünler/Markalar": "M1 Abrams tankları, Virginia ve Columbia sınıfı nükleer denizaltılar, Gulfstream iş jetleri",
        "Analiz Notu": "Kara ve deniz platformlarında ana üreticidir. Gulfstream jetleri ile sivil sektörde istikrarlı gelir yaratır."
    },
    "Boeing": {
        "Tam İsim": "The Boeing Company", "Ülke": "ABD", "CEO": "Kelly Ortberg", "Çalışan": "~171.000",
        "Faaliyet": "Sivil Uçaklar, Askeri Uçaklar, Uzay Sistemleri",
        "Tarihçe & Birleşmeler": "1997'de McDonnell Douglas'ı satın alarak savunma operasyonlarını genişletti.",
        "En Bilinen Ürünler/Markalar": "F-15EX, F/A-18 Super Hornet, AH-64 Apache, C-17 Globemaster, 737/777/787 sivil serileri",
        "Analiz Notu": "Sivil ticari uçak üretimindeki krizler nedeniyle şirketin savunma gelirlerinin toplam ciro içindeki oransal ağırlığı artmıştır."
    },
    "Airbus": {
        "Tam İsim": "Airbus SE", "Ülke": "Avrupa (Hollanda/Fransa/Almanya)", "CEO": "Guillaume Faury", "Çalışan": "~147.000",
        "Faaliyet": "Sivil Havacılık, Askeri Kargo, Helikopter, Uzay",
        "Tarihçe & Birleşmeler": "EADS (European Aeronautic Defence and Space) olarak kuruldu, 2014'te Airbus Group adını aldı.",
        "En Bilinen Ürünler/Markalar": "A400M Atlas, Eurofighter (ortak), H145/H225M helikopterleri, Ariane uzay sistemleri",
        "Analiz Notu": "Cironun büyük çoğunluğu sivil havacılıktan sağlanır. Savunma operasyonları konsorsiyum bazlı ilerler."
    },
    "Thales": {
        "Tam İsim": "Thales Group", "Ülke": "Fransa", "CEO": "Patrice Caine", "Çalışan": "~81.000",
        "Faaliyet": "Aviyonik, Optronik Sistemler, Radarlar, Siber Güvenlik",
        "Tarihçe & Birleşmeler": "Eski adı Thomson-CSF'dir. 2000 yılında Thales adını aldı.",
        "En Bilinen Ürünler/Markalar": "Rafale aviyonikleri, Sea Fire radarları, Starstreak (Thales UK), iletişim uyduları",
        "Analiz Notu": "Sensör ve elektronik mimarisinde Avrupa'nın ana tedarikçisidir. Sivil ve askeri operasyonları dengelidir."
    },
    "Leonardo": {
        "Tam İsim": "Leonardo S.p.A.", "Ülke": "İtalya", "CEO": "Roberto Cingolani", "Çalışan": "~53.000",
        "Faaliyet": "Helikopter, Elektronik, Uçak Sistemleri",
        "Tarihçe & Birleşmeler": "Eski adı Finmeccanica'dır. AgustaWestland, Selex ES tek çatı altında birleştirildi.",
        "En Bilinen Ürünler/Markalar": "AW139/AW159 helikopterleri, M-346 eğitim uçağı, Kronos radarları",
        "Analiz Notu": "İtalya'nın birincil savunma yüklenicisidir. Helikopter ve savunma elektroniği ana gelir kaynağıdır."
    },
    "L3Harris": {
        "Tam İsim": "L3Harris Technologies", "Ülke": "ABD", "CEO": "Christopher E. Kubasik", "Çalışan": "~50.000",
        "Faaliyet": "Taktik Haberleşme, Elektro-Optik, Sensör, Elektronik Harp",
        "Tarihçe & Birleşmeler": "2019'da L3 Technologies ve Harris Corp. birleşti. 2023'te Aerojet Rocketdyne'i satın aldı.",
        "En Bilinen Ürünler/Markalar": "Falcon telsiz serisi, WESCAM elektro-optik kameralar, Viper gece görüş sistemleri",
        "Analiz Notu": "Haberleşme, optik sensörler ve taktik ağ sistemlerinde altyapı tedarikçisidir."
    },
    "Elbit Systems": {
        "Tam İsim": "Elbit Systems Ltd.", "Ülke": "İsrail", "CEO": "Bezhalel Machlis", "Çalışan": "~19.000",
        "Faaliyet": "İHA, Elektro-Optik, Komuta Kontrol, Elektronik Harp",
        "Tarihçe & Birleşmeler": "2000'de El-Op'u, 2007'de Tadiran'ı, 2018'de IMI Systems'i satın aldı.",
        "En Bilinen Ürünler/Markalar": "Hermes 450/900 İHA, JHMCS (kaska entegre nişangah), Iron Fist aktif koruma",
        "Analiz Notu": "Platform üretmekten ziyade, mevcut platformları modernize eden ve elektronik altyapı sağlayan bir firmadır."
    },
    "Safran": {
        "Tam İsim": "Safran S.A.", "Ülke": "Fransa", "CEO": "Olivier Andriès", "Çalışan": "~92.000",
        "Faaliyet": "Havacılık Motorları, Optronik, Navigasyon, Aviyonik",
        "Tarihçe & Birleşmeler": "2005'te SNECMA ve SAGEM'in birleşmesiyle kuruldu. Zodiac Aerospace'i satın aldı.",
        "En Bilinen Ürünler/Markalar": "M88 (Rafale motoru), CFM56 (Sivil motor), AASM Hammer mühimmat, Patroller İHA",
        "Analiz Notu": "Fransız havacılık sanayiinin itki (motor) ve hassas optik sistemler merkezidir."
    },
    "Dassault": {
        "Tam İsim": "Dassault Aviation", "Ülke": "Fransa", "CEO": "Éric Trappier", "Çalışan": "~12.000",
        "Faaliyet": "Savaş Uçakları, İş Jetleri",
        "Tarihçe & Birleşmeler": "Dassault Group'un havacılık koludur.",
        "En Bilinen Ürünler/Markalar": "Rafale savaş uçağı, Mirage serisi, Falcon iş jetleri",
        "Analiz Notu": "İhracat başarıları Rafale üretim bandını güvenceye almıştır. Falcon iş jetleri sivil gelirlerini destekler."
    },
    "Rheinmetall": {
        "Tam İsim": "Rheinmetall AG", "Ülke": "Almanya", "CEO": "Armin Papperger", "Çalışan": "~30.000",
        "Faaliyet": "Zırhlı Araçlar, Mühimmat, Otomotiv Parçaları",
        "Tarihçe & Birleşmeler": "Otomotiv ve savunma birimlerine sahiptir. Son dönemde Expal'i satın alarak mühimmat kapasitesini artırdı.",
        "En Bilinen Ürünler/Markalar": "Leopard 2 ana topu (L55), KF51 Panther, Puma (ortak), 155mm topçu mühimmatı",
        "Analiz Notu": "Avrupa'nın ana mühimmat ve zırh çeliği sağlayıcısıdır. Küresel krizler şirketin kapasite kullanımını maksimize etmiştir."
    },
    "KNDS": {
        "Tam İsim": "KNDS (KMW+Nexter Defense Systems)", "Ülke": "Almanya/Fransa", "CEO": "Frank Haun", "Çalışan": "~9.000",
        "Faaliyet": "Ana Muharebe Tankları, Topçu Sistemleri",
        "Tarihçe & Birleşmeler": "2015'te Alman Krauss-Maffei Wegmann (KMW) ve Fransız Nexter (eski GIAT) birleşti.",
        "En Bilinen Ürünler/Markalar": "Leopard 2 tankı, Leclerc tankı, CAESAR obüsü, PzH 2000 obüsü",
        "Analiz Notu": "Kara sistemlerinde Avrupa standardizasyonunu sağlamak amacıyla kurulmuş stratejik konsorsiyumdur."
    },
    "Aselsan": {
        "Tam İsim": "ASELSAN Elektronik Sanayi ve Ticaret A.Ş.", "Ülke": "Türkiye", "CEO": "Ahmet Akyol", "Çalışan": "~10.500",
        "Faaliyet": "Haberleşme, Radar, Elektronik Harp, Elektro-Optik, Komuta Kontrol",
        "Tarihçe & Birleşmeler": "1975 Kıbrıs Barış Harekatı sonrası TSKGV bünyesinde kuruldu.",
        "En Bilinen Ürünler/Markalar": "KORKUT, Hisar-A/O/Siper (radar/elektronik), ASELFLIR, ÇAFRAD, CATS",
        "Analiz Notu": "Türkiye'nin askeri elektronik sistemlerdeki teknolojik bağımsızlığının merkezidir. Küresel listelerde düzenli yükseliş trendindedir."
    },
    "TUSAŞ": {
        "Tam İsim": "Türk Havacılık ve Uzay Sanayii A.Ş.", "Ülke": "Türkiye", "CEO": "Mehmet Demiroğlu", "Çalışan": "~15.000",
        "Faaliyet": "Hava Platformları, İHA, Uzay Sistemleri",
        "Tarihçe & Birleşmeler": "Başlangıçta F-16 üretimi için kurulan TAI ve TUSAŞ, 2005 yılında birleşerek millileşti.",
        "En Bilinen Ürünler/Markalar": "KAAN (MMU), T129 ATAK, GÖKBEY, HÜRJET, ANKA, AKSUNGUR, GÖKTÜRK uyduları",
        "Analiz Notu": "Özgün tasarım ve üretim kapasitesi ile Türkiye'nin en yüksek bütçeli Ar-Ge ve havacılık programlarını yürütmektedir."
    },
    "Roketsan": {
        "Tam İsim": "Roketsan Roket Sanayii ve Ticaret A.Ş.", "Ülke": "Türkiye", "CEO": "Murat İkinci", "Çalışan": "~4.000",
        "Faaliyet": "Füze Sistemleri, Roketler, Hassas Güdümlü Mühimmatlar",
        "Tarihçe & Birleşmeler": "1988 yılında uluslararası füze programları (Stinger vb.) üretimi için kuruldu.",
        "En Bilinen Ürünler/Markalar": "MAM-L/MAM-C, HİSAR Füzeleri, BORA, TAYFUN, SOM, ATMACA, OMTAS",
        "Analiz Notu": "İnsansız hava araçlarının vurucu gücünü sağlayan mikro mühimmatlarda ve balistik füze sistemlerinde tekel konumundadır."
    },
    "Havelsan": {
        "Tam İsim": "HAVELSAN A.Ş.", "Ülke": "Türkiye", "CEO": "Mehmet Akif Nacar", "Çalışan": "~2.500",
        "Faaliyet": "Komuta Kontrol, Simülasyon, Siber Güvenlik, Otonom Sistemler",
        "Tarihçe & Birleşmeler": "1982 yılında TSKGV bünyesinde kuruldu.",
        "En Bilinen Ürünler/Markalar": "ADVENT (Savaş Yönetim Sistemi), BARKAN, BAHA, F-16/Helikopter Simülatörleri",
        "Analiz Notu": "Yazılım ağırlıklı bir savunma şirketidir. Donanım üretiminden ziyade komuta-kontrol mimarilerine odaklanır."
    },
    "STM": {
        "Tam İsim": "STM Savunma Teknolojileri Mühendislik ve Ticaret A.Ş.", "Ülke": "Türkiye", "CEO": "Özgür Güleryüz", "Çalışan": "~1.500",
        "Faaliyet": "Askeri Denizcilik, Kamikaze İHA, Siber Güvenlik, Danışmanlık",
        "Tarihçe & Birleşmeler": "1991 yılında SSM (SSB) projelerine mühendislik desteği vermek amacıyla kuruldu.",
        "En Bilinen Ürünler/Markalar": "MİLGEM (Tasarım/Mühendislik), KARGU (Kamikaze İHA), TOGAN, ALPAGU",
        "Analiz Notu": "Askeri tersanecilik modernizasyonları ve taktik vurucu İHA (dron) sistemlerinde niş bir pazar payına sahiptir."
    },
    "BMC": {
        "Tam İsim": "BMC Otomotiv Sanayi ve Ticaret A.Ş.", "Ülke": "Türkiye", "CEO": "Murat Yalçıntaş", "Çalışan": "~3.000",
        "Faaliyet": "Zırhlı Kara Araçları, Ticari Kamyon/Otobüs, Tank (Altay)",
        "Tarihçe & Birleşmeler": "1964'te kuruldu. 2014'te TMSF'den Es Mali Yatırım'a geçti, günümüzde Tosyalı Holding çoğunluk hissesine sahiptir.",
        "En Bilinen Ürünler/Markalar": "KİRPİ, VURAN, AMAZON, ALTAY Tankı (Seri Üretim)",
        "Analiz Notu": "Mayına karşı korumalı (MRAP) araç segmentinde yoğun üretime sahiptir. Altay tankının seri üretimi şirketin savunma yükünü artırmaktadır."
    },
    "FNSS": {
        "Tam İsim": "FNSS Savunma Sistemleri A.Ş.", "Ülke": "Türkiye", "CEO": "Nail Kurt", "Çalışan": "~1.000",
        "Faaliyet": "Zırhlı Muharebe Araçları, Silah Kuleleri",
        "Tarihçe & Birleşmeler": "1989'da Nurol Holding ve BAE Systems ortak girişimi olarak kuruldu.",
        "En Bilinen Ürünler/Markalar": "PARS, KAPLAN, ZAHA, ACV-15, SAMUR",
        "Analiz Notu": "Yabancı ortaklı yapısı ile ihracat pazarlarında (özellikle Asya-Pasifik ve Ortadoğu) etkin bir zırhlı araç üreticisidir."
    },
    "MKE": {
        "Tam İsim": "Makine ve Kimya Endüstrisi A.Ş.", "Ülke": "Türkiye", "CEO": "İlhami Keleş", "Çalışan": "~5.500",
        "Faaliyet": "Silah, Mühimmat, Patlayıcı, Roket",
        "Tarihçe & Birleşmeler": "Kökleri 15. yüzyıla (Tophane-i Amire) dayanır. 2021'de A.Ş. statüsüne geçirilerek yeniden yapılandırıldı.",
        "En Bilinen Ürünler/Markalar": "MPT-76, MPT-55, BORAN (105mm Obüs), PANTER, Uçak Bombaları, Topçu Mühimmatları",
        "Analiz Notu": "TSK'nın temel mühimmat ve hafif/ağır silah tedarikçisidir. A.Ş. dönüşümü sonrası ihracat odaklı büyüme hedeflenmektedir."
    },
    "ASFAT": {
        "Tam İsim": "Askeri Fabrika ve Tersane İşletme A.Ş.", "Ülke": "Türkiye", "CEO": "Esad Akgün", "Çalışan": "~500 (Yönetim)",
        "Faaliyet": "Askeri Fabrika İşletimi, Gemi İnşa, Bakım Onarım",
        "Tarihçe & Birleşmeler": "2018 yılında Milli Savunma Bakanlığı bünyesindeki fabrika ve tersanelerin kapasitesini ihracata yöneltmek için kuruldu.",
        "En Bilinen Ürünler/Markalar": "PN MİLGEM (Pakistan MİLGEM projesi), Açık Deniz Karakol Gemileri, MEMATT",
        "Analiz Notu": "Kamuya ait askeri fabrikaların ve tersanelerin (Gölcük, İstanbul Tersanesi vb.) sivil/özel sektör dinamikleriyle uluslararası pazarda iş yapmasını sağlayan aracı kurumdur."
    },
    "CASIC": {
        "Tam İsim": "China Aerospace Science and Industry Corporation", "Ülke": "Çin", "CEO": "Yuan Jie", "Çalışan": "~150.000",
        "Faaliyet": "Füze Sistemleri, Radar, Uzay",
        "Tarihçe & Birleşmeler": "Çin devletinin ana stratejik füze üreticisidir.",
        "En Bilinen Ürünler/Markalar": "Dongfeng (DF) balistik füzeleri, HQ serisi hava savunma sistemleri",
        "Analiz Notu": "Çin'in stratejik caydırıcılığının ve uzay/füze yeteneklerinin omurgasıdır."
    },
    "CASC": {
        "Tam İsim": "China Aerospace Science and Technology Corporation", "Ülke": "Çin", "CEO": "Wu Yansheng", "Çalışan": "~170.000",
        "Faaliyet": "Uzay Fırlatma Sistemleri, Uydular, İHA'lar",
        "Tarihçe & Birleşmeler": "Uzay programının sivil ve askeri ayağını yürütmek üzere kurulmuştur.",
        "En Bilinen Ürünler/Markalar": "Long March fırlatma roketleri, CH (Caihong) serisi silahlı İHA'lar",
        "Analiz Notu": "Özellikle silahlı İHA ihracatında küresel pazarda önemli bir oyuncudur."
    },
    "NORINCO": {
        "Tam İsim": "China North Industries Group Corporation", "Ülke": "Çin", "CEO": "Liu Daqun", "Çalışan": "~200.000",
        "Faaliyet": "Kara Sistemleri, Mühimmat, Zırhlı Araçlar",
        "Tarihçe & Birleşmeler": "Çin kara ordusunun ana teçhizat sağlayıcısıdır.",
        "En Bilinen Ürünler/Markalar": "Type 99 tankları, VT serisi zırhlı araçlar, topçu roketleri",
        "Analiz Notu": "Afrika ve Ortadoğu pazarında uygun maliyetli kara sistemleri tedariki ile öne çıkar."
    },
    "Day & Zimmermann": {
        "Tam İsim": "Day & Zimmermann", "Ülke": "ABD", "CEO": "Hal Yoh III", "Çalışan": "~41.000",
        "Faaliyet": "Mühimmat, Tesis Yönetimi, İnşaat, Güvenlik",
        "Tarihçe & Birleşmeler": "1901'de mühendislik firması olarak kuruldu. ABD ordusu için mühimmat üretim tesisleri işletir.",
        "En Bilinen Ürünler/Markalar": "Çeşitli kalibrelerde topçu ve havan mühimmatı üretim operasyonları",
        "Analiz Notu": "Kendi tasarımlarından ziyade, devlete ait mühimmat tesislerinin işletmeciliğini yapan köklü bir hizmet ve üretim firmasıdır."
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
def load_and_merge_excel(file_path="DefNews100.xlsx", cache_buster="v10"):
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

df = load_and_merge_excel("DefNews100.xlsx", cache_buster="v10")

if not df.empty:
    sirketler = sorted(df["Şirket"].unique())
    secilen_sirket = st.selectbox("İncelemek istediğiniz şirketi seçin:", sirketler)
    sirket_verisi = df[df["Şirket"] == secilen_sirket].copy()
    
    # ---------------- ŞİRKET KÜNYESİ ---------------- #
    if secilen_sirket in KUNYE_VERITABANI:
        k = KUNYE_VERITABANI[secilen_sirket]
        st.info(f"**{k.get('Tam İsim', secilen_sirket)} ({k.get('Ülke', '-')})**\n\n"
                f"👤 **Mevcut CEO:** {k.get('CEO', '-')} | 👥 **Çalışan:** {k.get('Çalışan', '-')}\n\n"
                f"⚙️ **Faaliyet Alanı:** {k.get('Faaliyet', '-')}\n\n"
                f"🔗 **Tarihçe & Birleşmeler:** {k.get('Tarihçe & Birleşmeler', '-')}\n\n"
                f"🏷️ **En Bilinen Ürünler/Markalar:** {k.get('En Bilinen Ürünler/Markalar', '-')}\n\n"
                f"📊 **Analitik Not:** {k.get('Analiz Notu', '-')}")
    else:
        st.warning(f"💡 {secilen_sirket} şirketine ait detaylı künye bilgisi ana veritabanında yer almıyor. Analizlerini aşağıda inceleyebilirsiniz.")
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
