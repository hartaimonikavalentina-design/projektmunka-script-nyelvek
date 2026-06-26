import streamlit as st
import pandas as pd
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
# CSV → DataFrame (ugyanaz, mint a Colabban)
# ---------------------------------------------------------
CSV_PATH = "adatok_meteorologia.csv"

@st.cache_data
def load_dataframe():
    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        header=5,
        encoding="cp1250",
        engine="python"
    )
    df.columns = [c.strip() for c in df.columns]
    df["Time"] = pd.to_datetime(df["Time"], format="%Y%m%d", errors="coerce")
    return df

df = load_dataframe()

# ---------------------------------------------------------
# Alap metaadatok
# ---------------------------------------------------------
ev_min = int(df["Time"].dt.year.min())
ev_max = int(df["Time"].dt.year.max())

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

df_filtered = df[(df["Time"].dt.year >= ev_from) & (df["Time"].dt.year <= ev_to)]

ev_df = df_filtered.groupby(df_filtered["Time"].dt.year).agg({
    "t": "mean",
    "p": "mean",
    "fs": "mean"
}).reset_index().rename(columns={"Time": "Ev"})

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Éves átlaghőmérséklet")
    st.line_chart(ev_df.set_index("Time")["t"])

with col2:
    st.subheader("Éves átlagos légnyomás")
    st.line_chart(ev_df.set_index("Time")["p"])

with col3:
    st.subheader("Éves átlagos szélsebesség")
    st.line_chart(ev_df.set_index("Time")["fs"])

# ---------------------------------------------------------
# Havi átlaghőmérséklet
# ---------------------------------------------------------
st.header("Havi átlaghőmérséklet")

df_filtered["Ev"] = df_filtered["Time"].dt.year
df_filtered["Honap"] = df_filtered["Time"].dt.month

havi_df = df_filtered.groupby(["Ev", "Honap"])["t"].mean().reset_index()

pivot_havi = havi_df.pivot(index="Ev", columns="Honap", values="t")
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
box_df["Hónap_név"] = box_df["Honap"].map(honap_map)

fig_box = px.box(
    box_df,
    x="Hónap_név",
    y="t",
    category_orders={"Hónap_név": honap_sorrend},
    title="Havi hőmérséklet-eloszlások"
)

st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# Interaktív dashboard
# ---------------------------------------------------------
st.header("Interaktív dashboard")

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
    x="Honap",
    y=oszlop,
    title=f"{valasztott} havi eloszlása"
)
st.plotly_chart(fig_dash, use_container_width=True)

# ---------------------------------------------------------
# Összegzés
# ---------------------------------------------------------
st.markdown("## 9. Összegzés")

st.markdown("""
A projektmunka során sikerült:

- közvetlen CSV-beolvasást készíteni,
- a hiányzó adatokat megfelelően kezelni,
- többféle statikus és interaktív grafikont készíteni,
- a felhasználót bevonni a vizualizációba.

A projekt teljesíti a Script nyelvek tárgy követelményeit.

**Köszönöm szépen a Tanár úrnak az útmutatásokat!**
""")
