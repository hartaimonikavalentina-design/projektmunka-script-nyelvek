import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# Alapbeállítások
# ---------------------------------------------------------
st.set_page_config(page_title="Meteorológiai idősorok – projektmunka", layout="wide")

st.title("Meteorológiai idősorok feldolgozása Pythonban")
st.subheader("hiányzó adatok kezelése, rugalmas beolvasás és interaktív megjelenítés")

st.markdown("""
### Készítette:
**Hartai Mónika Valentina**  
levelezős hallgató  
Mesterséges Intelligencia Alkalmazásai szakirányú továbbképzés
""")

# ---------------------------------------------------------
# Tartalomjegyzék
# ---------------------------------------------------------
st.markdown("""
## Tartalom

1. Bevezetés  
2. Az adatforrás bemutatása  
3. Adatbeolvasás és hibakezelés  
4. Időbeli bontás és aggregáció  
5. Megjelenítés – grafikonok  
   5.1. Éves átlaghőmérséklet – vonaldiagram  
   5.2. Éves átlagos légnyomás – vonaldiagram  
   5.3. Éves átlagos szélsebesség – vonaldiagram  
   5.4. Havi átlaghőmérséklet – oszlopdiagram  
6. Boxplot és havi eloszlások  
7. Interaktív megjelenítés – a felhasználó szerepe  
8. Sikeres és sikertelen utak, promptolás  
9. Összegzés  
10. Térképes megjelenítés  
11. Lila pontgrafikon – interaktív dashboard  
""")

# ---------------------------------------------------------
# CSV → DataFrame
# ---------------------------------------------------------
CSV_PATH = "adatok_meteorologia.csv"

@st.cache_data
def load_dataframe():
    df = pd.read_csv(
        CSV_PATH,
        sep=r"\s*;\s*",     # pontosvessző + whitespace
        header=5,           # valódi fejléc a 6. sorban
        encoding="cp1250",
        engine="python"
    )

    # Oszlopnevek tisztítása
    df.columns = df.columns.str.strip()

    # Dátum konvertálása
    df["Time"] = pd.to_datetime(df["Time"], format="%Y%m%d", errors="coerce")

    # Év, hónap
    df["Év"] = df["Time"].dt.year
    df["Hónap"] = df["Time"].dt.month

    # -999 hibás értékek kezelése
    for col in ["t", "p", "fs"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].replace([-999, -999.0, 999, 999.0], np.nan)

    return df

df = load_dataframe()

# ---------------------------------------------------------
# Alap metaadatok
# ---------------------------------------------------------
ev_min = int(df["Év"].min())
ev_max = int(df["Év"].max())

st.header("Adatbeolvasás")
st.success("Az adatok sikeresen beolvasva közvetlen CSV-ből!")
st.write(f"Elérhető év tartomány: **{ev_min} – {ev_max}**")

# ---------------------------------------------------------
# Éves átlagok
# ---------------------------------------------------------
st.header("Éves átlagok")

ev_from, ev_to = st.slider(
    "Év tartomány:",
    min_value=ev_min,
    max_value=ev_max,
    value=(ev_min, ev_max)
)

df_filtered = df[(df["Év"] >= ev_from) & (df["Év"] <= ev_to)]

ev_df = df_filtered.groupby("Év").agg({
    "t": "mean",
    "p": "mean",
    "fs": "mean"
}).reset_index()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Éves átlaghőmérséklet")
    st.line_chart(ev_df.set_index("Év")["t"])

with col2:
    st.subheader("Éves átlagos légnyomás")
    st.line_chart(ev_df.set_index("Év")["p"])

with col3:
    st.subheader("Éves átlagos szélsebesség")
    st.line_chart(ev_df.set_index("Év")["fs"])

# ---------------------------------------------------------
# Havi átlaghőmérséklet
# ---------------------------------------------------------
st.header("Havi átlaghőmérséklet")

havi_df = df_filtered.groupby(["Év", "Hónap"])["t"].mean().reset_index()
pivot_havi = havi_df.pivot(index="Év", columns="Hónap", values="t")

st.line_chart(pivot_havi)

# ---------------------------------------------------------
# Boxplot – havi eloszlások
# ---------------------------------------------------------
st.header("Havi hőmérséklet-eloszlások (boxplot)")

honap_sorrend = [
    "január", "február", "március", "április", "május", "június",
    "július", "augusztus", "szeptember", "október", "november", "december"
]

honap_map = {i+1: honap_sorrend[i] for i in range(12)}

box_df = df_filtered.copy()
box_df["Hónap_név"] = box_df["Hónap"].map(honap_map)

fig_box = px.box(
    box_df,
    x="Hónap_név",
    y="t",
    category_orders={"Hónap_név": honap_sorrend},
    title="Havi hőmérséklet-eloszlások"
)

st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# Interaktív dashboard – vonaldiagram
# ---------------------------------------------------------
st.header("Interaktív dashboard – vonaldiagram")

dashboard_df = df_filtered.rename(columns={
    "t": "Homerseklet",
    "p": "Legnyomas",
    "fs": "Szelsebesseg"
})

valaszthato = {
    "Hőmérséklet (t)": "Homerseklet",
    "Légnyomás (p)": "Legnyomas",
    "Szélsebesség (fs)": "Szelsebesseg"
}

valasztott = st.selectbox("Válassz változót:", list(valaszthato.keys()))
oszlop = valaszthato[valasztott]

st.subheader("Idősoros grafikon")
st.line_chart(dashboard_df.set_index("Time")[oszlop])

st.subheader("Havi eloszlás")
fig_dash = px.box(
    dashboard_df,
    x="Hónap",
    y=oszlop,
    title=f"{valasztott} havi eloszlása"
)
st.plotly_chart(fig_dash, use_container_width=True)

# ---------------------------------------------------------
# Lila pontgrafikon + dropdown
# ---------------------------------------------------------
st.header("Interaktív lila pontgrafikon – változó szerint")

scatter_df = df.copy()
scatter_df = scatter_df[scatter_df["t"] > -900]

valtozok = {
    "Hőmérséklet (t)": "t",
    "Szélsebesség (fs)": "fs",
    "Légnyomás (p)": "p"
}

fig_scatter = px.scatter(
    scatter_df,
    x="Time",
    y="t",
    title="Hőmérséklet (t) – idősor",
    template="plotly_white",
    color_discrete_sequence=["purple"],
    opacity=0.7
)

fig_scatter.update_layout(
    updatemenus=[
        {
            "buttons": [
                {
                    "label": nev,
                    "method": "update",
                    "args": [
                        {"y": [scatter_df[oszlop]]},
                        {
                            "title": f"{nev} – idősor",
                            "yaxis": {"title": nev},
                        }
                    ]
                }
                for nev, oszlop in valtozok.items()
            ],
            "direction": "down",
            "showactive": True,
            "x": 1.15,
            "y": 1.0
        }
    ],
    xaxis_title="Dátum",
    yaxis_title="Érték"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# Térképes megjelenítés
# ---------------------------------------------------------
st.header("Mérőállomás térképen")

station_lat = 47.7147
station_lon = 16.6658

st.subheader("OpenStreetMap térkép")

fig_map_osm = px.scatter_mapbox(
    lat=[station_lat],
    lon=[station_lon],
    hover_name=["Fertőrákos"],
    zoom=7,
    title="Mérőállomás térképen (OpenStreetMap)"
)

fig_map_osm.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map_osm, use_container_width=True)

st.subheader("Magyar nyelvű topo térkép")

fig_map_hu = px.scatter_mapbox(
    lat=[station_lat],
    lon=[station_lon],
    hover_name=["Fertőrákos"],
    zoom=7,
    title="Mérőállomás térképen (Topo térkép)"
)

fig_map_hu.update_layout(
    mapbox=dict(
        style="white-bg",
        center=dict(lat=station_lat, lon=station_lon),
        zoom=7,
        layers=[
            dict(
                sourcetype="raster",
                source=[
                    "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
                ],
                below="traces"
            )
        ]
    ),
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig_map_hu, use_container_width=True)

# ---------------------------------------------------------
# Szöveges részek – Colab szöveg átemelve
# ---------------------------------------------------------

st.markdown("## 1. Bevezetés")
st.markdown("""
Ebben a projektmunkában egy nagyméretű, valós meteorológiai adathalmazt dolgozok fel Python nyelv segítségével.
A választott adatforrás egy több százezer sort tartalmazó CSV-fájl (adatok_meteorologia.csv), amely egy meteorológiai
állomás méréseinek több éves adatait tartalmazza. Az adatok időbélyeggel, hőmérséklet-, szélsebesség- és
légnyomás-értékekkel rendelkeznek.

A feladat célja az volt, hogy olyan megoldást készítsek, amely:
- rugalmasan olvassa be az adatokat,
- kezeli a hibás és hiányzó értékeket,
- vizuálisan is bemutatja az adatok főbb mintázatait,
- és lehetőséget ad a megjelenítés befolyásolására (szűrés, változóválasztás) anélkül, hogy magát az adatot módosítanám.

Különösen fontos volt számomra, hogy a „nyers” adatok mögött milyen történet rajzolódik ki; hogyan változik az évek során
a hőmérséklet, mennyire megbízhatóak a mérések, és mit kezdünk azzal, ha az adatok „nem tökéletesek”.
""")

st.markdown("## 2. Az adatforrás bemutatása")
st.markdown("""
A feldolgozott fájl neve: **adatok_meteorologia.csv**.

A fájl jellemzői:
- mérete több mint 2,7 MB,
- több százezer sor,
- a fejléc a 6. sorban található,
- az oszlopok pontosvesszővel (;) és whitespace-szel vannak elválasztva,
- a szélsebesség oszlopban a hiányzó értékeket a -999 érték jelöli.

A legfontosabb oszlopok:
- Time – időbélyeg
- t – hőmérséklet (°C)
- fs – szélsebesség (m/s)
- p – légnyomás (hPa)

Az adathalmaz komplexitását egyrészt a nagy méret, másrészt a hibás és hiányzó adatok jelenléte adja.
Ez utóbbi különösen fontos, mert a hiányzó értékek kezelésének módja alapvetően befolyásolja az eredmények értelmezését.
""")

st.markdown("## 3. Adatbeolvasás és hibakezelés")
st.markdown("""
A projekt egyik kulcspontja a rugalmas adatbeolvasás volt. A CSV elején metaadat-blokkok találhatók, ezért a fejléc nem
az első sorban van. A beolvasás fő lépései:

- a fejléc sorának manuális azonosítása (header=5),
- hibás sorok átugrása (on_bad_lines=\"skip\" – Colabban),
- a -999 értékek NaN-ná alakítása,
- a dátumok konvertálása (errors=\"coerce\").

A szélsebesség esetében külön probléma volt, hogy a hiányzó értékeket -999 jelölte. Első futtatáskor az éves átlagos
szélsebesség minden évben -999 lett, ami nyilvánvalóan hibás. Ez mutatta meg, hogy a hiányzó adatok felismerése és
kezelése nem pusztán technikai részlet, hanem az értelmezés szempontjából is döntő.
""")

st.markdown("## 4. Időbeli bontás és aggregáció")
st.markdown("""
A Time oszlopból két új oszlopot hoztam létre:
- Év
- Hónap

Ez lehetővé tette:
- éves átlagok számítását (t, fs, p),
- havi átlagok számítását (t),
- havi eloszlások (boxplot) készítését.
""")

st.markdown("## 5. Megjelenítés – grafikonok")
st.markdown("""
**5.1. Éves átlaghőmérséklet – vonaldiagram**  
A hőmérséklet éves átlagait vonaldiagramon ábrázoltam. A grafikon jól mutatja az évek közötti ingadozásokat és a hosszú távú trendeket.

**5.2. Éves átlagos légnyomás – vonaldiagram**  
A légnyomás éves átlagai kisebb ingadozásokat mutatnak, ami meteorológiai szempontból természetes.

**5.3. Éves átlagos szélsebesség – vonaldiagram**  
A szélsebesség esetében a hiányzó adatok miatt a grafikon inkább azt mutatja meg, hogy mely években áll rendelkezésre
értelmezhető mennyiségű adat. A -999 értékeket NaN-ná alakítottam, így az éves átlagok csak a valós mérésekből számolódnak.

**5.4. Havi átlaghőmérséklet – oszlopdiagram**  
A havi átlaghőmérsékletek szépen kirajzolják az évszakok ritmusát.
""")

st.markdown("## 6. Boxplot és havi eloszlások")
st.markdown("""
A boxplot megmutatja a hőmérséklet eloszlását hónaponként, beleértve a mediánt, szórást és szélsőértékeket.
A category_orders paraméter biztosítja, hogy a hónapok időrendben szerepeljenek, ne ábécé szerint.
""")

st.markdown("## 7. Interaktív megjelenítés – a felhasználó szerepe")
st.markdown("""
A felhasználó:
- kiválaszthatja a változót (t, fs, p),
- beállíthatja az év tartományt,
- interaktív idősorokat és havi eloszlásokat láthat,
- térképen megjelenik a Fertőrákos állomás.

Ez a projekt egyik legfontosabb része, mert a megjelenítés befolyásolható anélkül, hogy az adatot módosítanánk.
""")

st.markdown("## 8. Sikeres és sikertelen utak, promptolás")
st.markdown("""
- A szélsebesség átlagolása elsőre hibás volt (minden év -999).
- A fejléc nem az első sorban volt → rugalmas beolvasás kellett.
- A promptolás segített a hibák felismerésében és javításában.
""")

st.markdown("## 9. Összegzés")
st.markdown("""
A projektmunka során sikerült:

- rugalmas adatbeolvasást készíteni,
- a hiányzó adatokat megfelelően kezelni,
- többféle statikus és interaktív grafikont készíteni,
- a felhasználót bevonni a vizualizációba.

A projekt teljesíti a Script nyelvek tárgy követelményeit.
""")

st.markdown("## 10. Hivatalos megszólítások, köszönetnyilvánítás")
st.markdown("""
Tisztelt Dr. Tornai Kálmán Dékánhelyettes, Egyetemi Docens Úr!

A projektmunka interaktív elemei (grafikonok, csúszkák, térképes megjelenítés) a Google Colab környezetben
futtathatók. A jegyzetfüzet teljes tartalmának megjelenítéséhez az alábbi lépések követése szükséges:

1. A notebook megnyitása után kérem válassza a felső menüsorban a 'Runtime' / 'Futtatás' menüpontot.
2. Ezen belül kérem indítsa el az 'Run all' / 'Összes futtatása' parancsot.
3. A futtatás néhány másodpercet igénybe vehet. A cellák egymás után lefutnak, és megjelennek:
   - a statikus grafikonok,
   - a szélsebesség pontdiagram,
   - valamint az interaktív dashboard, amelyben a változó és az év tartomány szabadon állítható.
4. Az interaktív elemek (Plotly grafikonok, csúszkák, térkép) a futtatás után azonnal használhatók.

Köszönöm szépen a beadandó megtekintését és értékelését!

Tisztelettel:  
**Hartai Mónika Valentina**
""")

st.markdown("## 11. Fájlok és mellékletek")
st.markdown("""
A notebook futtatása során létrejött fájlok (PNG, HTML stb.) a Colab környezetben érhetők el, például:

- eves_atlaghomerseklet.png  
- eves_atlag_legnyomas.png  
- eves_atlag_szel.png  
- havi_atlaghomerseklet.png  
- boxplot_havi_homerseklet.png  
- szelsebesseg_fs.png  
- dashboard_kepernyokepek  

A PNG fájlokat a Colab bal oldali 'Files' paneljén lehet feltölteni vagy letölteni.
""")
