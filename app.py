import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Alapbeállítások
# ---------------------------------------------------------
st.set_page_config(
    page_title="Meteorológiai idősorok – projektmunka",
    layout="wide"
)

st.title("Meteorológiai idősorok – projektmunka")
st.subheader("Hartai Mónika Valentina – Script nyelvek beadandó")

st.markdown(
    """
Ez az alkalmazás egy nagy méretű meteorológiai adatbázisra épül,  
és interaktív grafikonokkal, szűrőkkel és szöveges magyarázatokkal mutatja be az eredményeket.
"""
)

# ---------------------------------------------------------
# DuckDB kapcsolat és adatbeolvasás (nagy CSV-hez optimalizálva)
# ---------------------------------------------------------

CSV_PATH = "adatok_meteorologia.csv"

@st.cache_resource
def get_connection():
    con = duckdb.connect(database=":memory:")
    return con

@st.cache_data
def load_basic_info():
    con = get_connection()

    query_years = f"""
        SELECT MIN(Ev) AS ev_min, MAX(Ev) AS ev_max
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
    """
    years_df = con.execute(query_years).fetchdf()
    ev_min = int(years_df["ev_min"][0])
    ev_max = int(years_df["ev_max"][0])

    query_months = f"""
        SELECT DISTINCT Honap
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        ORDER BY Honap
    """
    months_df = con.execute(query_months).fetchdf()
    honapok = months_df["Honap"].tolist()

    return ev_min, ev_max, honapok

@st.cache_data
def load_aggregated_data(ev_min, ev_max):
    con = get_connection()

    query_ev = f"""
        SELECT
            Ev,
            AVG(Homerseklet) AS atlag_homerseklet,
            AVG(Legnyomas)   AS atlag_legnyomas,
            AVG(Szelsebesseg) AS atlag_szelsebesseg
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE Ev BETWEEN {ev_min} AND {ev_max}
        GROUP BY Ev
        ORDER BY Ev
    """
    ev_df = con.execute(query_ev).fetchdf()

    query_havi = f"""
        SELECT
            Ev,
            Honap,
            AVG(Homerseklet) AS atlag_homerseklet
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE Ev BETWEEN {ev_min} AND {ev_max}
        GROUP BY Ev, Honap
        ORDER BY Ev, Honap
    """
    havi_df = con.execute(query_havi).fetchdf()

    query_box = f"""
        SELECT
            Ev,
            Honap,
            Homerseklet
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE Ev BETWEEN {ev_min} AND {ev_max}
    """
    box_df = con.execute(query_box).fetchdf()

    return ev_df, havi_df, box_df

@st.cache_data
def load_for_dashboard(ev_from, ev_to):
    con = get_connection()
    query = f"""
        SELECT
            Ev,
            Honap,
            Homerseklet,
            Legnyomas,
            Szelsebesseg
        FROM read_csv_auto('{CSV_PATH}', delim=';', header=True)
        WHERE Ev BETWEEN {ev_from} AND {ev_to}
        ORDER BY Ev, Honap
    """
    df = con.execute(query).fetchdf()
    return df

# ---------------------------------------------------------
# Adatbeolvasás blokk
# ---------------------------------------------------------

st.header("Adatbeolvasás")

try:
    ev_min, ev_max, honapok = load_basic_info()
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

ev_tartomany = st.slider(
    "Év tartomány:",
    min_value=ev_min,
    max_value=ev_max,
    value=(ev_min, ev_max)
)

ev_from, ev_to = ev_tartomany

ev_df, havi_df, box_df = load_aggregated_data(ev_from, ev_to)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Éves átlaghőmérséklet")
    if not ev_df.empty:
        st.line_chart(ev_df.set_index("Ev")["atlag_homerseklet"])
    else:
        st.info("Nincs adat a megadott év tartományra.")

with col2:
    st.subheader("Éves átlagos légnyomás")
    if not ev_df.empty:
        st.line_chart(ev_df.set_index("Ev")["atlag_legnyomas"])
    else:
        st.info("Nincs adat a megadott év tartományra.")

with col3:
    st.subheader("Éves átlagos szélsebesség")
    if not ev_df.empty:
        st.line_chart(ev_df.set_index("Ev")["atlag_szelsebesseg"])
    else:
        st.info("Nincs adat a megadott év tartományra.")

# ---------------------------------------------------------
# Havi átlaghőmérséklet
# ---------------------------------------------------------

st.header("Havi átlaghőmérséklet")

if not havi_df.empty:
    pivot_havi = havi_df.pivot(index="Ev", columns="Honap", values="atlag_homerseklet")
    st.line_chart(pivot_havi)
else:
    st.info("Nincs havi adat a megadott év tartományra.")

# ---------------------------------------------------------
# Havi hőmérséklet-eloszlások (boxplot)
# ---------------------------------------------------------

st.header("Havi hőmérséklet-eloszlások (boxplot)")

if not box_df.empty:
    fig_box = px.box(
        box_df,
        x="Honap",
        y="Homerseklet",
        points="outliers",
        title="Havi hőmérséklet-eloszlások"
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("Nincs elegendő adat a boxplot megjelenítéséhez.")

# ---------------------------------------------------------
# Interaktív dashboard
# ---------------------------------------------------------

st.header("Interaktív dashboard")

valtozo = st.selectbox(
    "Változó:",
    options=["Hőmérséklet (Homerseklet)", "Légnyomás (Legnyomas)", "Szélsebesség (Szelsebesseg)"]
)

if valtozo.startswith("Hőmérséklet"):
    oszlop = "Homerseklet"
elif valtozo.startswith("Légnyomás"):
    oszlop = "Legnyomas"
else:
    oszlop = "Szelsebesseg"

dashboard_df = load_for_dashboard(ev_from, ev_to)

if dashboard_df.empty:
    st.info("Nincs adat a megadott szűrési feltételekkel.")
else:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"{valtozo} – időbeli alakulás")
        dashboard_df["EvHonap"] = dashboard_df["Ev"].astype(str) + "-" + dashboard_df["Honap"].astype(str)
        st.line_chart(dashboard_df.set_index("EvHonap")[oszlop])

    with col_b:
        st.subheader(f"{valtozo} – havi eloszlás")
        fig_dash_box = px.box(
            dashboard_df,
            x="Honap",
            y=oszlop,
            points="outliers",
            title=f"{valtozo} havi eloszlása"
        )
        st.plotly_chart(fig_dash_box, use_container_width=True)

# ---------------------------------------------------------
# Szöveges összefoglaló blokk
# ---------------------------------------------------------

st.header("Szöveges értelmezés, következtetések")

st.markdown(
    """
Itt foglalhatod össze a legfontosabb megállapításokat:

- hogyan változott az éves átlaghőmérséklet az idők során,
- mely hónapok a leghidegebbek / legmelegebbek,
- hogyan alakul a légnyomás és a szélsebesség,
- milyen szélsőségek látszanak a boxplotokon,
- milyen összefüggések figyelhetők meg az interaktív dashboard alapján.

Ez a rész szolgálhat a beadandó **szöveges magyarázó** részének is.
"""
)
