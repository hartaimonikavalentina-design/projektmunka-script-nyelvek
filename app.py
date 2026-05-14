import duckdb
import streamlit as st
import plotly.express as px
import zipfile
import pandas as pd

# ---------------------------------------------------------
# Alapbeállítások
# ---------------------------------------------------------
st.set_page_config(page_title="Meteorológiai idősorok – projektmunka", layout="wide")

st.title("Meteorológiai idősorok – projektmunka")
st.subheader("Hartai Mónika Valentina – Script nyelvek beadandó")

st.markdown("""
Ez az alkalmazás egy nagy méretű meteorológiai adatbázisra épül,
és interaktív grafikonokkal, szűrőkkel és szöveges magyarázatokkal mutatja be az eredményeket.
""")

ZIP_PATH = "adatok_meteorologia.zip"

# ---------------------------------------------------------
# ZIP → CSV → DataFrame beolvasás (regex szeparátor + header=5)
# ---------------------------------------------------------
@st.cache_data
def load_dataframe():
    with zipfile.ZipFile(ZIP_PATH) as z:

        files = z.namelist()
        csv_files = [f for f in files if f.lower().endswith(".csv")]
        csv_name = csv_files[0]

        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                sep=r"\s*;\s*",     # whitespace + pontosvessző
                engine="python",
                header=5,
                encoding="latin2",
                on_bad_lines="skip"
            )

    # Time oszlop dátummá alakítása
    df["Time"] = pd.to_datetime(df["Time"], format="%Y%m%d", errors="coerce")

    # Oszlopnevek tisztítása
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
# Alap metaadatok lekérése (év tartomány)
# ---------------------------------------------------------
@st.cache_data
def load_basic_info():
    con = get_connection()

    query = """
        SELECT 
            MIN(year(Time)) AS ev_min,
            MAX(year(Time)) AS ev_max
        FROM adatok
    """

    df = con.execute(query).fetchdf()
    return int(df["ev_min"][0]), int(df["ev_max"][0])

# ---------------------------------------------------------
# Aggregált adatok lekérése
# ---------------------------------------------------------
@st.cache_data
def load_aggregated(ev_from, ev_to):
    con = get_connection()

    q_ev = f"""
        SELECT
            year(Time) AS Ev,
            AVG(t) AS atlag_homerseklet,
            AVG(p) AS atlag_legnyomas,
            AVG(fs) AS atlag_szelsebesseg
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev
        ORDER BY Ev
    """
    ev_df = con.execute(q_ev).fetchdf()

    q_havi = f"""
        SELECT
            year(Time) AS Ev,
            month(Time) AS Honap,
            AVG(t) AS atlag_homerseklet
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev, Honap
        ORDER BY Ev, Honap
    """
    havi_df = con.execute(q_havi).fetchdf()

    q_box = f"""
        SELECT
            month(Time) AS Honap,
            t AS Homerseklet
        FROM adatok
        WHERE year(Time) BETWEEN {ev_from} AND {ev_to}
    """
    box_df = con.execute(q_box).fetchdf()

    return ev_df, havi_df, box_df

# ---------------------------------------------------------
# Dashboard részletes adatok
# ---------------------------------------------------------
@st.cache_data
def load_dashboard(ev_from, ev_to):
    con = get_connection()

    q = f"""
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
    """
    df = con.execute(q).fetchdf()

    # Oszlopnevek tisztítása
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

valasztott = st.selectbox(
    "Válassz változót:",
    {
        "Hőmérséklet (t)": "Homerseklet",
        "Légnyomás (p)": "Legnyomas",
        "Szélsebesség (fs)": "Szelsebesseg"
    }
)

dashboard_df = load_dashboard(ev_from, ev_to)

st.subheader("Idősoros grafikon")
st.line_chart(dashboard_df.set_index("Datum")[valasztott])

st.subheader("Havi eloszlás")
fig_dash = px.box(
    dashboard_df,
    x="Honap",
    y=valasztott,
    title=f"{valasztott} havi eloszlása"
)
st.plotly_chart(fig_dash, use_container_width=True)
