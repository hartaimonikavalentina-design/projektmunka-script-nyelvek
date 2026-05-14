import duckdb
import streamlit as st
import plotly.express as px
import zipfile
import pandas as pd

# ---------------------------------------------------------
# Alapbeállítások
# ---------------------------------------------------------
st.set_page_config(page_title="Meteorológiai idősorok – projektmunka", layout="wide")

st.title("Meteorológiai idősorok feldolgozása Pythonban")
st.subheader("hiányzó adatok, rugalmas beolvasás és interaktív megjelenítés")

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
<h2 style='display:block; text-align:right; width:100%;'>Tartalom</h2>

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

""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. Bevezetés
# ---------------------------------------------------------
st.markdown("<h2 style='display:block; text-align:right; width:100%;'>1. Bevezetés</h2>", unsafe_allow_html=True)

st.markdown("""
Az alábbi GitHub‑linken érhető el.  
A README-ben található *Open in Colab* gombbal a notebook egy kattintással megnyitható,  
majd a Colab felületén futtatható.

**GitHub repó:**  
https://github.com/hartaimonikavalentina-design/projektmunka-script-nyelvek/tree/main

Ebben a projektmunkában egy nagyméretű, valós meteorológiai adathalmazt dolgozok fel Python nyelv segítségével. 
A választott adatforrás egy több százezer sort tartalmazó CSV-fájl (adatok meteorológia.csv), 
amely egy meteorológiai állomás méréseinek több éves adatait tartalmazza. 
Az adatok időbélyeggel, hőmérséklet-, szélsebesség- és légnyomás-értékekkel rendelkeznek.

A feladat célja az volt, hogy olyan megoldást készítsek, amely:

- rugalmasan olvassa be az adatokat,  
- kezeli a hibás és hiányzó értékeket,  
- vizuálisan is bemutatja az adatok főbb mintázatait,  
- és lehetőséget ad a megjelenítés befolyásolására (szűrés, változóválasztás) anélkül, hogy magát az adatot módosítanám.

Különösen fontos volt számomra, hogy a „nyers” adatok mögött milyen történet rajzolódik ki; 
hogyan változik az évek során a hőmérséklet, mennyire megbízhatóak a mérések, 
és mit kezdünk azzal, ha az adatok „nem tökéletesek”.
""")

# ---------------------------------------------------------
# 2. Az adatforrás bemutatása
# ---------------------------------------------------------
st.markdown("<h2 style='display:block; text-align:right; width:100%;'>2. Az adatforrás bemutatása</h2>", unsafe_allow_html=True)

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
""")

# ---------------------------------------------------------
# 3. Adatbeolvasás és hibakezelés
# ---------------------------------------------------------
st.markdown("<h2 style='display:block; text-align:right; width:100%;'>3. Adatbeolvasás és hibakezelés</h2>", unsafe_allow_html=True)

st.markdown("""
A projekt egyik kulcspontja a rugalmas adatbeolvasás volt. 
A CSV elején metaadat-blokkok találhatók, ezért a fejléc nem az első sorban van.

A beolvasás fő lépései:
- hibás sorok átugrása (`on_bad_lines="skip"`),
- a -999 értékek NaN-ná alakítása,
- a dátumok konvertálása (`errors="coerce"`).
""")

# ---------------------------------------------------------
# 4. Időbeli bontás és aggregáció
# ---------------------------------------------------------
st.markdown("<h2 style='display:block; text-align:right; width:100%;'>4. Időbeli bontás és aggregáció</h2>", unsafe_allow_html=True)

st.markdown("""
A **Time** oszlopból két új oszlopot hoztam létre:
- **Év**
- **Hónap**

Ez lehetővé tette:
- éves átlagok számítását (t, fs, p),
- havi átlagok számítását (t),
- havi eloszlások (boxplot) készítését.
""")

# ---------------------------------------------------------
# 5. Megjelenítés – grafikonok
# ---------------------------------------------------------
st.markdown("<h2 style='display:block; text-align:right; width:100%;'>5. Megjelenítés – grafikonok</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------
# ZIP → CSV → DataFrame beolvasás
# ---------------------------------------------------------
ZIP_PATH = "adatok_meteorologia.zip"

@st.cache_data
def load_dataframe():
    with zipfile.ZipFile(ZIP_PATH) as z:
        files = z.namelist()
        csv_files = [f for f in files if f.lower().endswith(".csv")]
        csv_name = csv_files[0]

        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                sep=r"\s*;\s*",
                engine="python",
                header=5,
                encoding="latin2",
                on_bad_lines="skip"
            )

    df["Time"] = pd.to_datetime(df["Time"], format="%Y%m%d", errors="coerce")
    df.columns = df.columns.str.strip()
    return df

# ---------------------------------------------------------
# DuckDB kapcsolat
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    con = duckdb.connect(database=":memory:")
    df = load_dataframe()
    con.register("adatok", df)
    return con

# ---------------------------------------------------------
# Alap metaadatok
# ---------------------------------------------------------
@st.cache_data
def load_basic_info():
    con = get_connection()
    df = con.execute("""
        SELECT 
            MIN(year(Time)) AS ev_min,
            MAX(year(Time)) AS ev_max
        FROM adatok
    """).fetchdf()
    return int(df["ev_min"][0]), int(df["ev_max"][0])

# ---------------------------------------------------------
# Aggregált adatok
# ---------------------------------------------------------
@st.cache_data
def load_aggregated(ev_from, ev_to):
    con = get_connection()

    ev_df = con.execute(f"""
        SELECT
            year(Time) AS Ev,
            AVG(t) AS atlag_homerseklet,
            AVG(p) AS atlag_legnyomas,
            AVG(fs) AS atlag_szelsebesseg
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev
        ORDER BY Ev
    """).fetchdf()

    havi_df = con.execute(f"""
        SELECT
            year(Time) AS Ev,
            month(Time) AS Honap,
            AVG(t) AS atlag_homerseklet
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev, Honap
        ORDER BY Ev, Honap
    """).fetchdf()

    box_df = con.execute(f"""
        SELECT
            month(Time) AS Honap,
            t AS Homerseklet
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
    """).fetchdf()

    return ev_df, havi_df, box_df

# ---------------------------------------------------------
# Dashboard adatok
# ---------------------------------------------------------
@st.cache_data
def load_dashboard(ev_from, ev_to):
    con = get_connection()

    df = con.execute(f"""
        SELECT
            Time AS Datum,
            year(Time) AS Ev,
            month(Time) AS Honap,
            t AS Homerseklet,
            p AS Legnyomas,
            fs AS Szelsebesseg
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
        ORDER BY Datum
    """).fetchdf()

    df.columns = df.columns.str.strip()
    return df

# ---------------------------------------------------------
# Adatbeolvasás
# ---------------------------------------------------------
st.header("Adatbeolvasás")

try:
    ev_min, ev_max = load_basic_info()
    st.success("Az adatok sikeresen beolvasva ZIP → CSV → DuckDB útvonalon!")
    st.write(f"Elérhető év tartomány: **{ev_min} – {ev_max}**")
except Exception as e:
    st.error("Hiba történt az adatok beolvasása közben.")
    st.exception(e)
    st.stop()

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

ev_df, havi_df, box_df = load_aggregated(ev_from, ev_to)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Éves átlaghőmérséklet")
    st.line_chart(ev_df.set_index("Ev")["atlag_homerseklet"])

with col2:
    st.subheader("Éves átlagos légnyomás")
    st.line_chart(ev_df.set_index("Ev")["atlag_legnyomas"])

with col3:
    st.subheader("Éves átlagos szélsebesség")
    st.line_chart(ev_df.set_index("Ev")["atlag_szelsebesseg"])

# ---------------------------------------------------------
# Havi átlaghőmérséklet
# ---------------------------------------------------------
st.header("Havi átlaghőmérséklet")

pivot_havi = havi_df.pivot(index="Ev", columns="Honap", values="atlag_homerseklet")
st.line_chart(pivot_havi)

# ---------------------------------------------------------
# Boxplot
# ---------------------------------------------------------
st.header("Havi hőmérséklet-eloszlások (boxplot)")

fig_box = px.box(
    box_df,
    x="Honap",
    y="Homerseklet",
    title="Havi hőmérséklet-eloszlások"
)
st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# Interaktív dashboard
# ---------------------------------------------------------
st.header("Interaktív dashboard")

dashboard_df = load_dashboard(ev_from, ev_to)
dashboard_df.columns = dashboard_df.columns.str.strip()

valaszthato = {
    "Hőmérséklet (t)": "Homerseklet",
    "Légnyomás (p)": "Legnyomas",
    "Szélsebesség (fs)": "Szelsebesseg"
}

valaszthato = {k: v for k, v in valaszthato.items() if v in dashboard_df.columns}

valasztott = st.selectbox("Válassz változót:", list(valaszthato.keys()))
valasztott_oszlop = valaszthato[valasztott]

st.subheader("Idősoros grafikon")
st.line_chart(dashboard_df.set_index("Datum")[valasztott_oszlop])

st.subheader("Havi eloszlás")
fig_dash = px.box(
    dashboard_df,
    x="Honap",
    y=valasztott_oszlop,
    title=f"{valasztott} havi eloszlása"
)
st.plotly_chart(fig_dash, use_container_width=True)
