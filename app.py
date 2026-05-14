import duckdb
import streamlit as st
import plotly.express as px
import zipfile
import pandas as pd

st.set_page_config(page_title="Meteorológiai idősorok – projektmunka", layout="wide")

st.title("Meteorológiai idősorok – projektmunka")
st.subheader("Hartai Mónika Valentina – Script nyelvek beadandó")

st.markdown("""
Ez az alkalmazás egy nagy méretű meteorológiai adatbázisra épül,
és interaktív grafikonokkal, szűrőkkel és szöveges magyarázatokkal mutatja be az eredményeket.
""")

ZIP_PATH = "adatok_meteorologia.zip"

# ---------------------------------------------------------
# ZIP → CSV → DataFrame beolvasás (diagnosztikával)
# ---------------------------------------------------------
@st.cache_data
def load_dataframe():
    with zipfile.ZipFile(ZIP_PATH) as z:

        files = z.namelist()
        st.write("ZIP tartalma:", files)

        csv_files = [f for f in files if f.lower().endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError("A ZIP-ben nincs CSV fájl.")

        csv_name = csv_files[0]
        st.write("Felismert CSV fájl:", csv_name)

        # --- DIAGNOSZTIKA: első 20 sor kiolvasása ---
        with z.open(csv_name) as f:
            raw_lines = f.read().decode("latin2").splitlines()
            st.write("Első 20 sor:", raw_lines[:20])

        # --- BEOLVASÁS: egyelőre header=None, hogy lássuk az oszlopokat ---
        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                sep=";",
                header=None,
                encoding="latin2",
                on_bad_lines="skip"
            )

        st.write("Beolvasott oszlopok (header=None):", df.columns.tolist())
        st.write(df.head())

        return df

# ---------------------------------------------------------
# A további részek csak akkor futnak, ha már tudjuk a fejlécet
# ---------------------------------------------------------
st.header("Adatbeolvasás")

try:
    df_test = load_dataframe()
    st.warning("A fejléc még nincs beállítva. A fenti diagnosztika alapján fogjuk pontosan meghatározni.")
    st.stop()

except Exception as e:
    st.error("Hiba történt az adatok beolvasása közben.")
    st.exception(e)
    st.stop()
