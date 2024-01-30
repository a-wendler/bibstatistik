import pandas as pd
import streamlit as st
import altair as alt

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("https://stash.cat/share/I0HRHpzjWSB6kv?download=true", low_memory=False)
    df = df[df['Ausleihtyp'] != 'O']
    return df

def geschlecht_allgemein():
    st.header('Geschlechtsverteilung der Ausleihen insgesamt')
    geschlecht = df.groupby("Geschlecht").agg({"Mediennummer":"count"})

    tortendiagram = alt.Chart(geschlecht.reset_index()).transform_joinaggregate(
        total = 'sum(Mediennummer)',
    ).transform_calculate(
        Prozent = 'datum.Mediennummer / datum.total'
    ).mark_arc(innerRadius=50).encode(
        theta="Prozent:Q",
        text=alt.Text('Prozent:Q', format='.1%'),
        color="Geschlecht:N",
    )
    
    text = tortendiagram.mark_text(
        radius=25
    ).encode(
        theta='Prozent:Q',
        text=alt.Text('Prozent:Q', format='.1%'),
    )

    return st.altair_chart(tortendiagram+text, use_container_width=True)

def geschlecht_sachgruppen():
    st.header("Sachgruppen")
    sachgruppen = df.Sachgruppe.value_counts().index.to_list()

    sachgruppen_auswahl = st.selectbox("Sachgruppe", sachgruppen)

    sachgruppen_geschlecht = df[df.Sachgruppe == sachgruppen_auswahl].groupby(['Sachgruppe', "Geschlecht"]).agg({"Mediennummer":"count"}).reset_index()

    sachgruppen_torte = alt.Chart(sachgruppen_geschlecht).transform_joinaggregate(
        total = 'sum(Mediennummer)',
    ).transform_calculate(
        Prozent = 'datum.Mediennummer / datum.total'
    ).mark_arc(innerRadius=50).encode(
        theta="Prozent:Q",
        text=alt.Text('Prozent:Q', format='.1%'),
        color="Geschlecht:N",
    )
    text = sachgruppen_torte.mark_text(
        radius=25
    ).encode(
        theta='Prozent:Q',
        text=alt.Text('Prozent:Q', format='.1%'),
    )
    return st.altair_chart(sachgruppen_torte+text, use_container_width=True)

def ausleihzeiten():
    st.header("Ausleihzeiten")
    df_maenner = df.loc[(df.Geschlecht == "M") & (df.Ausleihtyp == "A")].groupby("Uhrzeit").agg({"Mediennummer":"count"}).reset_index().rename({"Mediennummer":"Männer"}, axis=1)

    df_frauen = df.loc[(df.Geschlecht == "W") & (df.Ausleihtyp == "A")].groupby("Uhrzeit").agg({"Mediennummer":"count"}).reset_index().rename({"Mediennummer":"Frauen"}, axis=1)

    df_ausleih_geschlecht = pd.merge(df_maenner, df_frauen, on="Uhrzeit", how="outer").fillna(0)

    ausleih_geschlecht = alt.Chart(df_ausleih_geschlecht).transform_fold(["Männer", "Frauen"]).mark_line().encode(
        x="Uhrzeit:O",
        y="value:Q",
        color="key:N"
    )

    return st.altair_chart(ausleih_geschlecht, use_container_width=True)

def altersgruppen():
    st.header("Altersverteilung")
    df_maenner = df.loc[(df.Geschlecht == "M") & (df.Ausleihtyp == "A")].groupby("Altersgruppe").agg({"Mediennummer":"count"}).reset_index().rename({"Mediennummer":"Männer"}, axis=1)

    df_frauen = df.loc[(df.Geschlecht == "W") & (df.Ausleihtyp == "A")].groupby("Altersgruppe").agg({"Mediennummer":"count"}).reset_index().rename({"Mediennummer":"Frauen"}, axis=1)

    df_altersgruppe_geschlecht = pd.merge(df_maenner, df_frauen, on="Altersgruppe", how="outer").fillna(0)

    df_altersgruppe_geschlecht['m_anteil'] = df_altersgruppe_geschlecht.Männer / (df_altersgruppe_geschlecht.Männer + df_altersgruppe_geschlecht.Frauen) * 100

    df_altersgruppe_geschlecht['f_anteil'] = df_altersgruppe_geschlecht.Frauen / (df_altersgruppe_geschlecht.Männer + df_altersgruppe_geschlecht.Frauen) * 100
    
    df_altersgruppe_geschlecht.Altersgruppe = df_altersgruppe_geschlecht.Altersgruppe.replace('6-10', '06-10')

    altersgruppe_geschlecht = alt.Chart(df_altersgruppe_geschlecht).transform_fold(["m_anteil", "f_anteil"]).mark_bar().encode(
        x="Altersgruppe:O",
        y="value:Q",
        color="key:N"
    )

    return st.altair_chart(altersgruppe_geschlecht, use_container_width=True)

def faecherstatistik():
    st.header("Fächerstatistik")
    df_faecher = df.groupby(['Fächerstatistik', 'Geschlecht']).agg({'Mediennummer':'count'}).reset_index()

    summen = df_faecher.groupby('Fächerstatistik')['Mediennummer'].transform('sum')

    # Berechnen Sie die Prozentsätze
    df_faecher['Prozent'] = (df_faecher['Mediennummer'] / summen) * 100

    chart = alt.Chart(df_faecher).mark_bar().encode(
        x='Fächerstatistik:N',
        y='Prozent:Q',
        color='Geschlecht:N'
    )

    text = chart.mark_text(align='center', baseline='bottom').encode(
        text=alt.Text('Prozent:Q', format='.1f'),
        color=alt.value('black')
    )

    return st.altair_chart(chart+text, use_container_width=True)


if __name__ == "__main__":
    df = load_data()
    st.title("Ausleihen Pankow 2023")
    geschlecht_allgemein()
    geschlecht_sachgruppen()
    ausleihzeiten()
    altersgruppen()
    faecherstatistik()