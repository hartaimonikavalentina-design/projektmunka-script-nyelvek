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
