import duckdb
import streamlit as st
import plotly.express as px

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

CSV_PATH = "adatok_meteorologia.csv"

# ---------------------------------------------------------
# DuckDB kapcsolat
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    return duckdb.connect(database=":memory:")

# ---------------------------------------------------------
# Alap metaadatok lekérése (év tartomány)
# ---------------------------------------------------------
@st.cache_data
def load_basic_info():
    con = get_connection()

    query = f"""
        SELECT 
            MIN(year(CAST(Time AS DATE))) AS ev_min,
            MAX(year(CAST(Time AS DATE))) AS ev_max
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
    """

    df = con.execute(query).fetchdf()
    return int(df["ev_min"][0]), int(df["ev_max"][0])

# ---------------------------------------------------------
# Aggregált adatok lekérése
# ---------------------------------------------------------
@st.cache_data
def load_aggregated(ev_from, ev_to):
    con = get_connection()

    # Éves átlagok
    q_ev = f"""
        SELECT
            year(CAST(Time AS DATE)) AS Ev,
            AVG(t) AS atlag_homerseklet,
            AVG(p) AS atlag_legnyomas,
            AVG(fs) AS atlag_szelsebesseg
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE year(CAST(Time AS DATE)) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev
        ORDER BY Ev
    """
    ev_df = con.execute(q_ev).fetchdf()

    # Havi átlaghőmérséklet
    q_havi = f"""
        SELECT
            year(CAST(Time AS DATE)) AS Ev,
            month(CAST(Time AS DATE)) AS Honap,
            AVG(t) AS atlag_homerseklet
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE year(CAST(Time AS DATE)) BETWEEN {ev_from} AND {ev_to}
        GROUP BY Ev, Honap
        ORDER BY Ev, Honap
    """
    havi_df = con.execute(q_havi).fetchdf()

    # Boxplot adatok
    q_box = f"""
        SELECT
            month(CAST(Time AS DATE)) AS Honap,
            t AS Homerseklet
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE year(CAST(Time AS DATE)) BETWEEN {ev_from} AND {ev_to}
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
            CAST(Time AS DATE) AS Datum,
            year(CAST(Time AS DATE)) AS Ev,
            month(CAST(Time AS DATE)) AS Honap,
            t AS Homerseklet,
            p AS Legnyomas,
            fs AS Szelsebesseg
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE year(CAST(Time AS DATE)) BETWEEN {ev_from} AND {ev_to}
        ORDER BY Datum
    """
    return con.execute(q).fetchdf()

# ---------------------------------------------------------
# Adatbeolvasás
# ---------------------------------------------------------
st.header("Adatbeolvasás")

try:
    ev_min, ev_max = load_basic_info()
    st.success("Az adatok sikeresen beolvasva DuckDB-n keresztül!")
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
