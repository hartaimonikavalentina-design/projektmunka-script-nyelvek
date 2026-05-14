import streamlit as st

st.set_page_config(page_title="Meteorológiai projektmunka", layout="wide")

st.title("Meteorológiai idősorok – projektmunka")
st.write("Hartai Mónika Valentina – Script nyelvek beadandó")

st.markdown("""
### Bevezetés

Ez egy Streamlit alapú webes felület, amely a meteorológiai adatok vizsgálatára készült.
A következő lépésekben ide fogjuk beépíteni:
- az adatbeolvasást,
- a grafikonokat,
- az interaktív csúszkákat és választólistákat,
- valamint a projektmunka szöveges fejezeteit.
""")

import pandas as pd

st.header("Adatbeolvasás")

# CSV beolvasása
df = pd.read_csv(
    "adatok meterológia.csv",
    sep=";",
    skiprows=5,
    encoding="utf-8",
    on_bad_lines="skip"
)

# Oszlopok tisztítása
df.columns = [c.strip() for c in df.columns]

# Dátum konvertálása
df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

# Szám típusú oszlopok konvertálása
for col in ["t", "v", "p", "fs"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].replace([-999, -999.0], None)

# Év és hónap oszlopok
df["Év"] = df["Time"].dt.year
df["Hónap"] = df["Time"].dt.month

st.success("Az adatok sikeresen beolvasva!")
st.write(df.head())

import plotly.express as px

st.header("Éves átlaghőmérséklet")

# Éves átlag számítása
eves_atlag_hom = df.groupby("Év")["t"].mean().reset_index()

# Vonaldiagram Plotly-val
fig = px.line(
    eves_atlag_hom,
    x="Év",
    y="t",
    title="Éves átlaghőmérséklet (°C)",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

st.header("Éves átlagos légnyomás")

eves_atlag_legny = df.groupby("Év")["p"].mean().reset_index()

fig_legny = px.line(
    eves_atlag_legny,
    x="Év",
    y="p",
    title="Éves átlagos légnyomás (hPa)",
    markers=True
)

st.plotly_chart(fig_legny, use_container_width=True)

st.header("Éves átlagos szélsebesség")

eves_atlag_szel = df.groupby("Év")["fs"].mean().reset_index()

fig_szel = px.line(
    eves_atlag_szel,
    x="Év",
    y="fs",
    title="Éves átlagos szélsebesség (m/s)",
    markers=True
)

st.plotly_chart(fig_szel, use_container_width=True)

st.header("Havi átlaghőmérséklet")

havi_atlag = df.groupby("Hónap")["t"].mean().reset_index()

fig_havi = px.bar(
    havi_atlag,
    x="Hónap",
    y="t",
    title="Havi átlaghőmérséklet (°C)",
    labels={"Hónap": "Hónap", "t": "Hőmérséklet (°C)"},
)

st.plotly_chart(fig_havi, use_container_width=True)

st.header("Havi hőmérséklet-eloszlások (boxplot)")

fig_box = px.box(
    df,
    x="Hónap",
    y="t",
    title="Havi hőmérséklet-eloszlások",
    labels={"Hónap": "Hónap", "t": "Hőmérséklet (°C)"},
)

st.plotly_chart(fig_box, use_container_width=True)

st.header("Interaktív dashboard")

# Változóválasztó lenyíló lista
valtozo = st.selectbox(
    "Válassz változót:",
    options={
        "Hőmérséklet (t)": "t",
        "Szélsebesség (fs)": "fs",
        "Légnyomás (p)": "p"
    }
)

# Év tartomány csúszka
ev_min = int(df["Év"].min())
ev_max = int(df["Év"].max())

ev_tartomany = st.slider(
    "Év tartomány:",
    min_value=ev_min,
    max_value=ev_max,
    value=(ev_min, ev_max)
)

# Adatok szűrése
d = df[(df["Év"] >= ev_tartomany[0]) & (df["Év"] <= ev_tartomany[1])]

# Idősoros grafikon
fig_ts = px.line(
    d,
    x="Time",
    y=valtozo,
    title=f"{valtozo} idősor ({ev_tartomany[0]}–{ev_tartomany[1]})",
    labels={"Time": "Dátum", valtozo: "Érték"}
)

st.plotly_chart(fig_ts, use_container_width=True)

# Éves átlag grafikon
eves = d.groupby("Év")[valtozo].mean().reset_index()

fig_year = px.line(
    eves,
    x="Év",
    y=valtozo,
    markers=True,
    title=f"Éves átlagos {valtozo}",
    labels={"Év": "Év", valtozo: "Éves átlag"}
)

st.plotly_chart(fig_year, use_container_width=True)

st.header("Mérőállomás térképen")

# Mérőállomás metaadat
station_name = "Fertőrákos"
station_lat = 47.7147
station_lon = 16.6658

df_station = pd.DataFrame({
    "StationName": [station_name],
    "Lat": [station_lat],
    "Lon": [station_lon]
})

# Térkép megjelenítése
fig_map = px.scatter_mapbox(
    df_station,
    lat="Lat",
    lon="Lon",
    hover_name="StationName",
    zoom=7,
    title="Mérőállomás térképen – Fertőrákos"
)

fig_map.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("<h2 style='text-align:right;'>1. Bevezetés</h2>", unsafe_allow_html=True)

st.markdown("""
Tisztelt Tanár Úr!

A projektmunkám az alábbi GitHub‑linken érhető el. A README-ben található *Open in Colab* gombbal a notebook egy kattintással megnyitható és futtatható.

**GitHub repó:**  
https://github.com/hartaimonikavalentina-design/projektmunka-script-nyelvek/tree/main

Ebben a projektmunkában egy nagyméretű, valós meteorológiai adathalmazt dolgozok fel Python nyelv segítségével. A választott adatforrás egy több százezer sort tartalmazó CSV-fájl (adatok meteorológia.csv), amely egy meteorológiai állomás méréseinek több éves adatait tartalmazza. Az adatok időbélyeggel, hőmérséklet-, szélsebesség- és légnyomás-értékekkel rendelkeznek.

A feladat célja az volt, hogy olyan megoldást készítsek, amely:
- rugalmasan olvassa be az adatokat,
- kezeli a hibás és hiányzó értékeket,
- vizuálisan is bemutatja az adatok főbb mintázatait,
- és lehetőséget ad a megjelenítés befolyásolására (szűrés, változóválasztás) anélkül, hogy magát az adatot módosítanám.

Különösen fontos volt számomra, hogy a „nyers” adatok mögött milyen történet rajzolódik ki; hogyan változik az évek során a hőmérséklet, mennyire megbízhatóak a mérések, és mit kezdünk azzal, ha az adatok „nem tökéletesek”.
""")

st.markdown("<h2 style='text-align:right;'>2. Az adatforrás bemutatása</h2>", unsafe_allow_html=True)

st.markdown("""
A feldolgozott fájl neve: **adatok meteorológia.csv**.

A fájl jellemzői:
- mérete több mint 2,7 MB,
- több százezer sor,
- a fejléc a 6. sorban található,
- az oszlopok pontosvesszővel (;) vannak elválasztva,
- a szélsebesség oszlopban a hiányzó értékeket a -999 érték jelöli.

A legfontosabb oszlopok:
- **Time** – időbélyeg (dátum és idő),
- **t** – hőmérséklet (°C),
- **fs** – szélsebesség (m/s),
- **p** – légnyomás (hPa).

Az adathalmaz komplexitását egyrészt a nagy méret, másrészt a hibás és hiányzó adatok jelenléte adja. Ez utóbbi különösen fontos, mert a hiányzó értékek kezelésének módja alapvetően befolyásolja az eredmények értelmezését.
""")

st.markdown("<h2 style='text-align:right;'>3. Adatbeolvasás és hibakezelés</h2>", unsafe_allow_html=True)

st.markdown("""
A projekt egyik kulcspontja a rugalmas adatbeolvasás volt. A CSV elején metaadat-blokkok találhatók, ezért a fejléc nem az első sorban van.

A beolvasás fő lépései:
- a fejléc sorának manuális azonosítása,
- hibás sorok átugrása (`on_bad_lines="skip"`),
- a -999 értékek NaN-ná alakítása,
- a dátumok konvertálása (`errors="coerce"`).

A szélsebesség esetében külön probléma volt, hogy a hiányzó értékeket -999 jelölte. Első futtatáskor az éves átlagos szélsebesség minden évben -999 lett, ami nyilvánvalóan hibás. Ez mutatta meg, hogy a hiányzó adatok felismerése és kezelése nem pusztán technikai részlet, hanem az értelmezés szempontjából is döntő.
""")

st.markdown("<h2 style='text-align:right;'>4. Időbeli bontás és aggregáció</h2>", unsafe_allow_html=True)

st.markdown("""
A **Time** oszlopból két új oszlopot hoztam létre:
- **Év**
- **Hónap**

Ez lehetővé tette:
- éves átlagok számítását (t, fs, p),
- havi átlagok számítását (t),
- havi eloszlások (boxplot) készítését.
""")

st.markdown("<h2 style='text-align:right;'>5. Megjelenítés – grafikonok</h2>", unsafe_allow_html=True)

st.markdown("""
A projektben többféle diagramtípust használtam, hogy az adatok különböző aspektusait emeljem ki.
""")

st.markdown("<h2 style='text-align:right;'>5.1. Éves átlaghőmérséklet – vonaldiagram</h2>", unsafe_allow_html=True)

st.markdown("""
A hőmérséklet éves átlagait vonaldiagramon ábrázoltam. A grafikon jól mutatja az évek közötti ingadozásokat és a hosszú távú trendeket.
""")

st.markdown("<h2 style='text-align:right;'>5.2. Éves átlagos légnyomás – vonaldiagram</h2>", unsafe_allow_html=True)

st.markdown("""
A légnyomás éves átlagai kisebb ingadozásokat mutatnak, ami meteorológiai szempontból természetes.
""")

st.markdown("<h2 style='text-align:right;'>5.3. Éves átlagos szélsebesség – vonaldiagram</h2>", unsafe_allow_html=True)

st.markdown("""
A szélsebesség esetében a hiányzó adatok miatt a grafikon inkább azt mutatja meg, hogy mely években áll rendelkezésre értelmezhető mennyiségű adat.  
Ez önmagában is tanulságos: nem minden mérés egyformán megbízható, és az adatok minősége is része a történetnek.

A -999 értékeket NaN-ná alakítottam, így az éves átlagok csak a valós mérésekből számolódnak.
""")

st.markdown("<h2 style='text-align:right;'>5.4. Havi átlaghőmérséklet – oszlopdiagram</h2>", unsafe_allow_html=True)

st.markdown("""
A havi átlaghőmérsékletek szépen kirajzolják az évszakok ritmusát.
""")

st.markdown("<h2 style='text-align:right;'>6. Boxplot és havi eloszlások</h2>", unsafe_allow_html=True)

st.markdown("""
A boxplot megmutatja a hőmérséklet eloszlását hónaponként, beleértve a mediánt, szórást és szélsőértékeket.
""")

st.markdown("<h2 style='text-align:right;'>7. Interaktív megjelenítés – a felhasználó szerepe</h2>", unsafe_allow_html=True)

st.markdown("""
A felhasználó:
- kiválaszthatja a változót (t, fs, p),
- beállíthatja az év tartományt,
- interaktív idősorokat és éves átlagokat láthat,
- térképen megjelenik a Fertőrákos állomás.

Ez a projekt egyik legfontosabb része, mert a megjelenítés befolyásolható anélkül, hogy az adatot módosítanánk.
""")

st.markdown("<h2 style='text-align:right;'>8. Sikeres és sikertelen utak, promptolás</h2>", unsafe_allow_html=True)

st.markdown("""
- A szélsebesség átlagolása elsőre hibás volt (minden év -999).
- A fejléc nem az első sorban volt → rugalmas beolvasás kellett.
- A promptolás segített a hibák felismerésében és javításában.

A hibák és zsákutcák végigkísérték a munkát, de ezekből tanultam a legtöbbet: hogyan lehet a hibás eredmények mögé nézni, és hogyan lehet a kódot lépésről lépésre javítani.
""")

st.markdown("<h2 style='text-align:right;'>9. Összegzés</h2>", unsafe_allow_html=True)

st.markdown("""
A projektmunka során sikerült:
- rugalmas adatbeolvasást készíteni,
- a hiányzó adatokat megfelelően kezelni,
- többféle statikus és interaktív grafikont készíteni,
- a felhasználót bevonni a vizualizációba.

A projekt teljesíti a **Script nyelvek** tárgy követelményeit.
""")

st.markdown("<h2 style='text-align:right;'>Záró megjegyzés a futtatáshoz</h2>", unsafe_allow_html=True)

st.markdown("""
Tisztelt Dr. Tornai Kálmán Dékánhelyettes, Egyetemi Docens Úr!

A projektmunka interaktív elemei (grafikonok, csúszkák, térképes megjelenítés) a Google Colab és a Streamlit környezetben futtathatók.

A Colab jegyzetfüzet teljes tartalmának megjelenítéséhez az alábbi lépések követése szükséges:
1. A notebook megnyitása után a felső menüsorban válassza a **Runtime / Futtatás** menüpontot.
2. Ezen belül indítsa el az **Run all / Összes futtatása** parancsot.
3. A futtatás néhány másodpercet igénybe vehet. A cellák egymás után lefutnak, és megjelennek:
   - a statikus grafikonok,
   - a szélsebesség pontdiagram,
   - valamint az interaktív dashboard, amelyben a változó és az év tartomány szabadon állítható.
4. Az interaktív elemek (Plotly grafikonok, csúszkák, térkép) a futtatás után azonnal használhatók.

Köszönöm szépen a beadandó megtekintését és értékelését!

**Tisztelettel:**  
Hartai Mónika Valentina
""")
