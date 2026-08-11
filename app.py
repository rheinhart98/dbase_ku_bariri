import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Kualitas Udara Bariri", layout="wide")

st.title("📊 Dashboard Monitoring Kualitas Udara - Stasiun Bariri")

# RAW URL GitHub Database
URL_PICARRO = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/PICARRO_FULL_TIMESERIES_QC.csv"
URL_OZON = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/OZON_ACOEM_ALL_YEARS_hourly_clean.csv"

@st.cache_data(ttl=3600)
def load_data(url):
    df = pd.read_csv(url)
    df['Date_Time'] = pd.to_datetime(
        df['Tahun'].astype(str) + '-' + 
        df['Bulan'].astype(str) + '-' + 
        df['Tanggal'].astype(str) + ' ' + 
        df['Jam'].astype(str) + ':00:00', 
        errors='coerce'
    )
    return df

# Sidebar Filter
st.sidebar.header("⚙️ Filter Data")
instrument = st.sidebar.radio("Pilih Instrumen:", ["Picarro (GHG)", "Ozon (ACOEM)"])

if instrument == "Picarro (GHG)":
    df = load_data(URL_PICARRO)
    params = ["CO_sync", "CO2_sync", "CO2_dry_sync", "CH4_sync", "CH4_dry_sync", "H2O_sync"]
else:
    df = load_data(URL_OZON)
    params = ["O3_Concentration_ppb", "Chassis_Temp_C", "Lamp_Temp_C", "Ambient_Pressure_torr"]

selected_param = st.sidebar.selectbox("Pilih Parameter:", params)

# Filter Tanggal
min_date = df['Date_Time'].min().date()
max_date = df['Date_Time'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu:", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# Filter Dataset
mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()

# Ganti -9999 dengan None untuk Plotting
df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, None)

# Kartu Statistik
valid_data = df_filtered[selected_param].dropna()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-Rata", f"{valid_data.mean():.2f}" if not valid_data.empty else "-")
col2.metric("Maksimum", f"{valid_data.max():.2f}" if not valid_data.empty else "-")
col3.metric("Minimum", f"{valid_data.min():.2f}" if not valid_data.empty else "-")
col4.metric("Jumlah Jam Valid", f"{len(valid_data)} jam")

# Grafik Time Series Interaktif
st.subheader(f"📈 Grafik Time Series: {selected_param}")
fig = px.line(df_filtered, x="Date_Time", y=selected_param, labels={"Date_Time": "Waktu", selected_param: "Konsentrasi / Nilai"})
st.plotly_chart(fig, use_container_width=True)

# Tabel Data Preview
st.subheader("📋 Preview Data")
st.dataframe(df_filtered[['Tahun', 'Bulan', 'Tanggal', 'Jam', selected_param]].head(100))
