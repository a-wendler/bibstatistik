import pandas as pd
import streamlit as st
import altair as alt

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("bibstatistik/berlin-data/AusEx_Pankow_2023.csv", low_memory=False)
    df = df[df['Ausleihtyp'] != 'O']
    return df

df = load_data()
geschlecht = df.groupby("Geschlecht").agg({"Mediennummer":"count"})
geschlecht["prozent"] = (geschlecht['Mediennummer'] / geschlecht['Mediennummer'].sum()) * 100
st.dataframe(geschlecht)

tortendiagram = alt.Chart(geschlecht.reset_index()).mark_arc(innerRadius=50).encode(
    theta="Mediennummer",
    color="Geschlecht:N",
)

st.altair_chart(tortendiagram, use_container_width=True)