# ---------------------------------------------------------
# Interaktív dashboard  **JAVÍTOTT, MŰKÖDŐ VERZIÓ**
# ---------------------------------------------------------
st.header("Interaktív dashboard")

dashboard_df = load_dashboard(ev_from, ev_to)

# Oszlopnevek tisztítása
dashboard_df.columns = dashboard_df.columns.str.strip()

# Valós oszlopnevek automatikus felismerése
valaszthato = {
    "Hőmérséklet (t)": "Homerseklet",
    "Légnyomás (p)": "Legnyomas",
    "Szélsebesség (fs)": "Szelsebesseg"
}

# Csak a ténylegesen létező oszlopokat tartjuk meg
valaszthato = {k: v for k, v in valaszthato.items() if v in dashboard_df.columns}

valasztott = st.selectbox("Válassz változót:", valaszthato)

# Idősoros grafikon
st.subheader("Idősoros grafikon")
st.line_chart(
    dashboard_df.set_index("Datum")[valasztott]
)

# Havi eloszlás
st.subheader("Havi eloszlás")
fig_dash = px.box(
    dashboard_df,
    x="Honap",
    y=valasztott,
    title=f"{valasztott} havi eloszlása"
)
st.plotly_chart(fig_dash, use_container_width=True)
