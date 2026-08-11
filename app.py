import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# URL Logo Resmi BMKG
BMKG_LOGO_URL = "https://www.bmkg.go.id/asset/img/logo/logo-bmkg.png"

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & PROTEKSI FRONTEND
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GAW Lore Lindu Bariri", page_icon=BMKG_LOGO_URL, layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2e364f; }
    body, .stApp, p, h1, h2, h3, h4, h5, h6, span {
        -webkit-user-select: none !important; -moz-user-select: none !important; -ms-user-select: none !important; user-select: none !important;
    }
    </style>
""", unsafe_allow_html=True)

components.html(
    """<script>
    const doc = window.parent.document;
    doc.addEventListener('contextmenu', event => event.preventDefault());
    doc.addEventListener('keydown', function(e) {
        if(e.keyCode == 123) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.keyCode == 85) { e.preventDefault(); return false; }
    });
    </script>""", height=0, width=0
)

# ------------------------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------------------------
URL_PICARRO = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/PICARRO_FULL_TIMESERIES_QC.csv"
URL_OZON = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/OZON_ACOEM_ALL_YEARS_hourly_clean.csv"

@st.cache_data(ttl=1800)
def load_data(url):
    df = pd.read_csv(url)
    df['Date_Time'] = pd.to_datetime(df['Tahun'].astype(str) + '-' + df['Bulan'].astype(str) + '-' + df['Tanggal'].astype(str) + ' ' + df['Jam'].astype(str) + ':00:00', errors='coerce') + pd.Timedelta(hours=8)
    df['Tahun'] = df['Date_Time'].dt.year
    df['Bulan'] = df['Date_Time'].dt.month
    df['Tanggal'] = df['Date_Time'].dt.day
    df['Jam'] = df['Date_Time'].dt.hour
    return df

GLOBAL_BENCHMARKS = {
    "CO2_sync": {"name": "CO2 Global (WMO)", "val": 422.0, "unit": "ppm", "max_gauge": 500},
    "CO2_dry_sync": {"name": "CO2 Dry Global", "val": 422.0, "unit": "ppm", "max_gauge": 500},
    "CH4_sync": {"name": "CH4 Global (WMO)", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
    "CH4_dry_sync": {"name": "CH4 Dry Global", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
    "CO_sync": {"name": "Latar Belakang CO", "val": 0.10, "unit": "ppm", "max_gauge": 2.0},
    "O3_Concentration_ppb": {"name": "Pedoman WHO (O3)", "val": 50.0, "unit": "ppb", "max_gauge": 100.0}
}

# ------------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
st.sidebar.image(BMKG_LOGO_URL, width=80)
st.sidebar.title("GAW Lore Lindu Bariri")
st.sidebar.caption("Stasiun Pemantau Atmosfer Global - BMKG")
st.sidebar.markdown("---")

instrument = st.sidebar.radio("📌 Pilih Instrumen:", ["Picarro (GHG)", "Ozon (ACOEM)"])
if instrument == "Picarro (GHG)":
    df = load_data(URL_PICARRO)
    available_params = ["CO2_sync", "CO2_dry_sync", "CH4_sync", "CH4_dry_sync", "CO_sync", "H2O_sync"]
else:
    df = load_data(URL_OZON)
    available_params = ["O3_Concentration_ppb", "Chassis_Temp_C", "Lamp_Temp_C", "Ambient_Pressure_torr"]

selected_param = st.sidebar.selectbox("📊 Pilih Parameter:", available_params)

min_date, max_date = df['Date_Time'].min().date(), df['Date_Time'].max().date()
preset_range = st.sidebar.selectbox("📅 Rentang Waktu:", ["Semua Tahun (Full Data)", "1 Tahun Terakhir", "6 Bulan Terakhir", "1 Bulan Terakhir", "Custom Tanggal"])

if preset_range == "Semua Tahun (Full Data)": start_date, end_date = min_date, max_date
elif preset_range == "1 Tahun Terakhir": start_date, end_date = max_date - pd.Timedelta(days=365), max_date
elif preset_range == "6 Bulan Terakhir": start_date, end_date = max_date - pd.Timedelta(days=180), max_date
elif preset_range == "1 Bulan Terakhir": start_date, end_date = max_date - pd.Timedelta(days=30), max_date
else:
    date_selection = st.sidebar.date_input("Custom:", [min_date, max_date], min_value=min_date, max_value=max_date)
    start_date, end_date = date_selection if len(date_selection) == 2 else (min_date, max_date)

show_trend = st.sidebar.checkbox("📈 Tampilkan Garis Tren", value=True)
apply_ma = st.sidebar.checkbox("🌊 Gunakan Moving Average")
ma_window = st.sidebar.slider("Jendela MA (Jam):", 3, 72, 24) if apply_ma else 1

mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()
df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, np.nan)
df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param].rolling(window=ma_window, min_periods=1).mean() if apply_ma else df_filtered[selected_param]

# ------------------------------------------------------------------------------
# 4. DASHBOARD HEADER & LOKASI
# ------------------------------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(f"📡 Monitoring {instrument}")
    st.caption(f"Lokasi: Bariri, Sulawesi Tengah | Zona Waktu: WITA | Periode: {start_date} s/d {end_date}")
with col_head2:
    with st.expander("📍 Lihat Peta Lokasi Stasiun"):
        # Koordinat Kasar GAW Bariri
        loc_df = pd.DataFrame({'lat': [-1.65], 'lon': [120.16]})
        st.map(loc_df, zoom=10, use_container_width=True)

valid_series = df_filtered[selected_param].dropna()
mean_val, max_val, min_val = (valid_series.mean(), valid_series.max(), valid_series.min()) if not valid_series.empty else (0,0,0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-Rata Lokal", f"{mean_val:.3f}")
col2.metric("Nilai Maksimum", f"{max_val:.3f}")
col3.metric("Nilai Minimum", f"{min_val:.3f}")

has_benchmark = selected_param in GLOBAL_BENCHMARKS
if has_benchmark:
    bench_val = GLOBAL_BENCHMARKS[selected_param]["val"]
    col4.metric(label=f"Acuan Global ({GLOBAL_BENCHMARKS[selected_param]['unit']})", value=f"{bench_val}", delta=f"{mean_val - bench_val:+.3f} vs Global", delta_color="inverse" if (mean_val - bench_val) > 0 else "normal")
else:
    col4.metric("Data Valid", f"{(len(valid_series)/len(df_filtered)*100):.1f}%")

st.markdown("---")

# ------------------------------------------------------------------------------
# 5. TABS INTERFACE (+ HEATMAP & GAUGE)
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Time Series", "📊 Statistik & Heatmap", "🌍 Status Kualitas Udara", "🔒 Download Data"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date_Time"], y=df_filtered[f'{selected_param}_plot'], mode='lines', name=f"Data {selected_param}", line=dict(color='#00d2ff', width=1.5)))
    df_trend_valid = df_filtered.dropna(subset=[selected_param]).copy()
    if show_trend and len(df_trend_valid) > 1:
        x_secs = (df_trend_valid["Date_Time"] - df_trend_valid["Date_Time"].min()).dt.total_seconds()
        slope, intercept = np.polyfit(x_secs, df_trend_valid[selected_param], 1)
        fig.add_trace(go.Scatter(x=df_trend_valid["Date_Time"], y=slope * x_secs + intercept, mode='lines', name='Tren Linear', line=dict(color='#ff007f', width=2.5, dash='dash')))
    if has_benchmark:
        fig.add_hline(y=bench_val, line_dash="dot", line_color="red", annotation_text=f"Global Ref: {bench_val}")
    fig.update_layout(xaxis_title="Waktu (WITA)", yaxis_title=selected_param, hovermode="x unified", template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df_stats = df_filtered.dropna(subset=[selected_param]).copy()
    if not df_stats.empty:
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
        df_stats['Nama_Bulan'] = df_stats['Bulan'].map(month_names)
        
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            fig_yearly = px.box(df_stats, x="Tahun", y=selected_param, color="Tahun", template="plotly_dark", title="Variasi Tahunan")
            st.plotly_chart(fig_yearly, use_container_width=True)
            
        with c_top2:
            df_monthly_agg = df_stats.groupby(['Bulan', 'Nama_Bulan'])[selected_param].mean().reset_index().sort_values('Bulan')
            fig_monthly = px.line(df_monthly_agg, x="Nama_Bulan", y=selected_param, markers=True, template="plotly_dark", title="Pola Musiman Bulanan")
            fig_monthly.update_traces(line_color='#00e676', line_width=3)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        st.markdown("---")
        
        # FITUR BARU: 2D HEATMAP & DIURNAL
        c_bot1, c_bot2 = st.columns(2)
        with c_bot1:
            diurnal_agg = df_stats.groupby('Jam')[selected_param].mean().reset_index()
            fig_diurnal = px.line(diurnal_agg, x='Jam', y=selected_param, markers=True, template="plotly_dark", title="Siklus Diurnal Jam-jaman (WITA)")
            fig_diurnal.update_traces(line_color='#ff9100', line_width=3)
            fig_diurnal.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24)), range=[-0.3, 23.3]))
            st.plotly_chart(fig_diurnal, use_container_width=True)
            
        with c_bot2:
            heatmap_data = df_stats.groupby(['Nama_Bulan', 'Bulan', 'Jam'])[selected_param].mean().reset_index()
            heatmap_data = heatmap_data.sort_values('Bulan')
            fig_heat = px.density_heatmap(heatmap_data, x="Jam", y="Nama_Bulan", z=selected_param, histfunc="avg", template="plotly_dark", title="Heatmap: Jam vs Bulan", color_continuous_scale="Viridis")
            fig_heat.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))))
            st.plotly_chart(fig_heat, use_container_width=True)

with tab3:
    if has_benchmark:
        st.subheader("🌍 Status Indeks Terhadap Acuan Global")
        bench_info = GLOBAL_BENCHMARKS[selected_param]
        
        c_gauge1, c_gauge2 = st.columns([1, 1])
        with c_gauge1:
            # FITUR BARU: SPEEDOMETER / GAUGE CHART
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = mean_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Rata-rata Bariri vs {bench_info['name']}", 'font': {'size': 20}},
                delta = {'reference': bench_info['val'], 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                gauge = {
                    'axis': {'range': [None, bench_info['max_gauge']], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#00d2ff"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, bench_info['val']], 'color': "rgba(0, 255, 0, 0.2)"},
                        {'range': [bench_info['val'], bench_info['max_gauge']], 'color': "rgba(255, 0, 0, 0.3)"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': bench_info['val']}}
            ))
            fig_gauge.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with c_gauge2:
            st.markdown(f"""
            ### Analisis Status:
            - **Nilai Stasiun Bariri:** `{mean_val:.2f} {bench_info['unit']}`
            - **Ambang Batas Global:** `{bench_info['val']} {bench_info['unit']}`
            
            **Kesimpulan:**
            Konsentrasi {selected_param} saat ini berada **{abs(mean_val - bench_info['val']):.2f} {bench_info['unit']}** 
            *{'di atas (lebih buruk/tinggi)' if mean_val > bench_info['val'] else 'di bawah (lebih baik/rendah)'}* dari nilai standar latar belakang global.
            """)
    else:
        st.warning("Parameter ini tidak memiliki acuan baseline global.")

with tab4:
    st.subheader("📥 Download Data (Terproteksi)")
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1: user_id = st.text_input("User ID:", key="input_user_id")
    with col_auth2: user_pass = st.text_input("Password:", type="password", key="input_password")
        
    if user_id == "gawbariri" and user_pass == "gaw97094":
        st.success("✅ Autentikasi Berhasil!")
        selected_cols = st.multiselect("Pilih Kolom Data:", list(df_filtered.columns), default=['Tahun', 'Bulan', 'Tanggal', 'Jam', selected_param])
        df_download = df_filtered[selected_cols].dropna(subset=[selected_param]) if st.checkbox("Keluarkan data missing (-9999 / NaN)", value=True) else df_filtered[selected_cols].copy()
        st.dataframe(df_download.head(50), use_container_width=True)
        st.download_button("💾 Unduh CSV (WITA)", df_download.to_csv(index=False).encode('utf-8'), f"GAW_Bariri_{selected_param}.csv", "text/csv")
    elif user_id or user_pass:
        st.error("❌ Kredensial salah!")
