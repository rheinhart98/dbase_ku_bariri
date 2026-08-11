import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & THEME
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Bariri Atmospheric Observatory",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e364f;
    }
    div[data-testid="stSidebarUserContent"] {
        background-color: #161b26;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. LOAD DATA DARI GITHUB DATABASE
# ------------------------------------------------------------------------------
URL_PICARRO = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/PICARRO_FULL_TIMESERIES_QC.csv"
URL_OZON = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/OZON_ACOEM_ALL_YEARS_hourly_clean.csv"

@st.cache_data(ttl=1800)
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

# Baseline / Standar Global Acuan (WMO / WDCGG / WHO)
GLOBAL_BENCHMARKS = {
    "CO2_sync": {"name": "Rata-Rata CO2 Global (WMO 2024)", "val": 422.0, "unit": "ppm"},
    "CO2_dry_sync": {"name": "Rata-Rata CO2 Dry Global", "val": 422.0, "unit": "ppm"},
    "CH4_sync": {"name": "Rata-Rata CH4 Global (WMO)", "val": 1.93, "unit": "ppm"},
    "CH4_dry_sync": {"name": "Rata-Rata CH4 Dry Global", "val": 1.93, "unit": "ppm"},
    "CO_sync": {"name": "Latar Belakang CO Global", "val": 0.10, "unit": "ppm"},
    "O3_Concentration_ppb": {"name": "Batas Pedoman Udara Ambien WHO (O3)", "val": 50.0, "unit": "ppb"}
}

# ------------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & FILTER
# ------------------------------------------------------------------------------
st.sidebar.title("🌍 Bariri Observatory")
st.sidebar.caption("Sistem Monitoring Kualitas Udara & Gas Rumah Kaca")
st.sidebar.markdown("---")

instrument = st.sidebar.radio("📌 Pilih Instrumen / Alat:", ["Picarro (GHG)", "Ozon (ACOEM)"])

if instrument == "Picarro (GHG)":
    df = load_data(URL_PICARRO)
    available_params = ["CO2_sync", "CO2_dry_sync", "CH4_sync", "CH4_dry_sync", "CO_sync", "H2O_sync"]
else:
    df = load_data(URL_OZON)
    available_params = ["O3_Concentration_ppb", "Chassis_Temp_C", "Lamp_Temp_C", "Ambient_Pressure_torr"]

selected_param = st.sidebar.selectbox("📊 Pilih Parameter:", available_params)

# Filter Tanggal
min_date = df['Date_Time'].min().date()
max_date = df['Date_Time'].max().date()

start_date, end_date = st.sidebar.date_input(
    "📅 Rentang Waktu Tanggal:", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# Smooth Moving Average
apply_ma = st.sidebar.checkbox("Gunakan Moving Average (Smoothening)")
ma_window = st.sidebar.slider("Jendela Jam (MA):", 3, 72, 24) if apply_ma else 1

# Filtering Data
mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()

# Filter nilai -9999
df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, np.nan)

# Calculate Moving Average
if apply_ma:
    df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param].rolling(window=ma_window, min_periods=1).mean()
else:
    df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param]

# ------------------------------------------------------------------------------
# 4. DASHBOARD HEADER & METRICS
# ------------------------------------------------------------------------------
st.title(f"📡 Dashboard Monitoring: {instrument}")
st.caption(f"Lokasi: Stasiun Bariri, Sulawesi Tengah | Periode: {start_date} s/d {end_date}")

valid_series = df_filtered[selected_param].dropna()
mean_val = valid_series.mean() if not valid_series.empty else 0
max_val = valid_series.max() if not valid_series.empty else 0
min_val = valid_series.min() if not valid_series.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-Rata Lokal", f"{mean_val:.3f}")
col2.metric("Nilai Maksimum", f"{max_val:.3f}")
col3.metric("Nilai Minimum", f"{min_val:.3f}")

# Cek apakah parameter punya baseline global
has_benchmark = selected_param in GLOBAL_BENCHMARKS
if has_benchmark:
    bench_val = GLOBAL_BENCHMARKS[selected_param]["val"]
    diff = mean_val - bench_val
    col4.metric(
        label=f"Acuan Global ({GLOBAL_BENCHMARKS[selected_param]['unit']})", 
        value=f"{bench_val}", 
        delta=f"{diff:+.3f} vs Global",
        delta_color="inverse" if diff > 0 else "normal"
    )
else:
    col4.metric("Ketersediaan Data Valid", f"{(len(valid_series)/len(df_filtered)*100):.1f}%")

st.markdown("---")

# ------------------------------------------------------------------------------
# 5. TABS INTERFACE (TIME SERIES, GLOBAL COMPARISON, STATS, DOWNLOAD)
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Time Series Interaktif", 
    "🌍 Perbandingan Global", 
    "📊 Analisis Statistik", 
    "📥 Custom Download Data"
])

# --- TAB 1: TIME SERIES ---
with tab1:
    fig = px.line(
        df_filtered, 
        x="Date_Time", 
        y=f"{selected_param}_plot", 
        title=f"Tren Waktu: {selected_param} {'(Moving Average)' if apply_ma else ''}",
        labels={"Date_Time": "Waktu (WITA)", f"{selected_param}_plot": selected_param},
        template="plotly_dark"
    )
    fig.update_traces(line_color='#00d2ff', line_width=1.5)
    
    # Tambah garis acuan global jika tersedia
    if has_benchmark:
        fig.add_hline(
            y=GLOBAL_BENCHMARKS[selected_param]["val"], 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"Global Ref: {GLOBAL_BENCHMARKS[selected_param]['val']}"
        )
    
    fig.update_layout(hovermode="x unified", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: PERBANDINGAN GLOBAL ---
with tab2:
    st.subheader("🌍 Perbandingan Konsentrasi Lokal vs Acuan Standar Global")
    if has_benchmark:
        bench_info = GLOBAL_BENCHMARKS[selected_param]
        st.info(f"**Baseline Acuan:** {bench_info['name']} = **{bench_info['val']} {bench_info['unit']}**")
        
        # Grafik Perbandingan Bar Chart
        comp_df = pd.DataFrame({
            "Kategori": ["Pengamatan Bariri (Rata-Rata)", bench_info["name"]],
            "Nilai": [mean_val, bench_info["val"]]
        })
        
        fig_comp = px.bar(
            comp_df, 
            x="Kategori", 
            y="Nilai", 
            color="Kategori", 
            text_auto='.2f',
            title=f"Rata-Rata Bariri vs {bench_info['name']}",
            template="plotly_dark",
            color_discrete_sequence=['#00d2ff', '#ff4b4b']
        )
        fig_comp.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.write(f"""
        **Analisis Perbandingan:**
        - Nilai pengamatan Bariri berada **{abs(diff):.3f} {bench_info['unit']} {'di atas' if diff > 0 else 'di bawah'}** nilai acuan global.
        - Penjelasan: Variasi lokal dipengaruhi oleh dinamika cuaca lokal, siklus vegetasi harian, dan tutupan lahan sekitar Stasiun Bariri.
        """)
    else:
        st.warning("Parameter ini tidak memiliki acuan baseline global spesifik.")

# --- TAB 3: STATISTIK & DISTRIBUSI ---
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Boxplot Distribusi Data")
        fig_box = px.box(df_filtered, y=selected_param, points="outliers", template="plotly_dark")
        st.plotly_chart(fig_box, use_container_width=True)
    
    with c2:
        st.subheader("Profil Rata-Rata Diurnal (Jam-jaman)")
        diurnal = df_filtered.groupby("Jam")[selected_param].mean().reset_index()
        fig_diurnal = px.bar(diurnal, x="Jam", y=selected_param, template="plotly_dark", color_discrete_sequence=['#57b8ff'])
        st.plotly_chart(fig_diurnal, use_container_width=True)

# --- TAB 4: CUSTOM DOWNLOAD DATA ---
with tab4:
    st.subheader("📥 Filter & Unduh Data kustom")
    st.write("Pilih kolom data yang ingin Anda unduh:")
    
    all_cols = list(df_filtered.columns)
    selected_cols = st.multiselect("Pilih Kolom:", all_cols, default=['Tahun', 'Bulan', 'Tanggal', 'Jam', selected_param])
    
    # Checkbox hilangkan missing data
    drop_missing = st.checkbox("Keluarkan data missing (-9999 / NaN)", value=True)
    
    df_download = df_filtered[selected_cols].copy()
    if drop_missing and selected_param in df_download.columns:
        df_download = df_download.dropna(subset=[selected_param])
    
    # Preview Data
    st.dataframe(df_download.head(50), use_container_width=True)
    
    # Export Button
    csv_bytes = df_download.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Unduh Dataset Terfilter (CSV)",
        data=csv_bytes,
        file_name=f"Bariri_{selected_param}_{start_date}_to_{end_date}.csv",
        mime="text/csv"
    )
