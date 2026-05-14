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
