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
st.set_page_config(
    page_title="GAW Lore Lindu Bariri",
    page_icon=BMKG_LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mematikan Block & Copy Text
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e364f;
    }
    body, .stApp, p, h1, h2, h3, h4, h5, h6, span {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Mematikan Klik Kanan & F12
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('contextmenu', event => event.preventDefault());
    doc.addEventListener('keydown', function(e) {
        if(e.keyCode == 123) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && e.keyCode == 73) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && e.keyCode == 67) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && e.keyCode == 74) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.keyCode == 85) { e.preventDefault(); return false; }
    });
    </script>
    """,
    height=0, width=0
)

# ------------------------------------------------------------------------------
# 2. LOAD DATA & KONVERSI WAKTU KE WITA (UTC +8)
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
    ) + pd.Timedelta(hours=8)
    
    df['Tahun'] = df['Date_Time'].dt.year
    df['Bulan'] = df['Date_Time'].dt.month
    df['Tanggal'] = df['Date_Time'].dt.day
    df['Jam'] = df['Date_Time'].dt.hour
    
    return df

GLOBAL_BENCHMARKS = {
    "CO2_sync": {"name": "Rata-Rata CO2 Global (WMO)", "val": 422.0, "unit": "ppm"},
    "CO2_dry_sync": {"name": "Rata-Rata CO2 Dry Global", "val": 422.0, "unit": "ppm"},
    "CH4_sync": {"name": "Rata-Rata CH4 Global (WMO)", "val": 1.93, "unit": "ppm"},
    "CH4_dry_sync": {"name": "Rata-Rata CH4 Dry Global", "val": 1.93, "unit": "ppm"},
    "CO_sync": {"name": "Latar Belakang CO Global", "val": 0.10, "unit": "ppm"},
    "O3_Concentration_ppb": {"name": "Pedoman Udara WHO (O3)", "val": 50.0, "unit": "ppb"}
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

min_date = df['Date_Time'].min().date()
max_date = df['Date_Time'].max().date()

start_date, end_date = st.sidebar.date_input(
    "📅 Rentang Waktu (WITA):", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

show_trend = st.sidebar.checkbox("📈 Tampilkan Garis Tren Linear", value=True)
apply_ma = st.sidebar.checkbox("🌊 Gunakan Moving Average")
ma_window = st.sidebar.slider("Jendela Jam (MA):", 3, 72, 24) if apply_ma else 1

mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()

df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, np.nan)

if apply_ma:
    df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param].rolling(window=ma_window, min_periods=1).mean()
else:
    df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param]

# ------------------------------------------------------------------------------
# 4. DASHBOARD HEADER & METRICS
# ------------------------------------------------------------------------------
st.title(f"📡 Monitoring {instrument} - GAW Lore Lindu Bariri")
st.caption(f"Lokasi: Bariri, Sulawesi Tengah | Zona Waktu: WITA (UTC+8) | Periode: {start_date} s/d {end_date}")

valid_series = df_filtered[selected_param].dropna()
mean_val = valid_series.mean() if not valid_series.empty else 0
max_val = valid_series.max() if not valid_series.empty else 0
min_val = valid_series.min() if not valid_series.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-Rata Lokal", f"{mean_val:.3f}")
col2.metric("Nilai Maksimum", f"{max_val:.3f}")
col3.metric("Nilai Minimum", f"{min_val:.3f}")

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
    col4.metric("Ketersediaan Data", f"{(len(valid_series)/len(df_filtered)*100):.1f}%")

st.markdown("---")

# ------------------------------------------------------------------------------
# 5. TABS INTERFACE
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Time Series Interaktif & Tren", 
    "📊 Statistik (WITA)", 
    "🌍 Acuan Global", 
    "🔒 Download Data"
])

# --- TAB 1: TIME SERIES & LINEAR TRENDLINE ---
with tab1:
    fig = go.Figure()

    # 1. Plot Data Utama (Raw / Moving Average)
    fig.add_trace(go.Scatter(
        x=df_filtered["Date_Time"],
        y=df_filtered[f'{selected_param}_plot'],
        mode='lines',
        name=f"Data {selected_param} {'(MA)' if apply_ma else ''}",
        line=dict(color='#00d2ff', width=1.5)
    ))

    # 2. Hitung & Plot Garis Tren Linear (Regresi)
    df_trend_valid = df_filtered.dropna(subset=[selected_param]).copy()
    if show_trend and len(df_trend_valid) > 1:
        x_secs = (df_trend_valid["Date_Time"] - df_trend_valid["Date_Time"].min()).dt.total_seconds()
        y_vals = df_trend_valid[selected_param]
        
        slope, intercept = np.polyfit(x_secs, y_vals, 1)
        trend_y = slope * x_secs + intercept
        
        fig.add_trace(go.Scatter(
            x=df_trend_valid["Date_Time"],
            y=trend_y,
            mode='lines',
            name='Garis Tren Linear',
            line=dict(color='#ff007f', width=2.5, dash='dash')
        ))

    # 3. Garis Acuan Global
    if has_benchmark:
        fig.add_hline(
            y=GLOBAL_BENCHMARKS[selected_param]["val"], 
            line_dash="dot", line_color="red", 
            annotation_text=f"Global Ref: {GLOBAL_BENCHMARKS[selected_param]['val']}"
        )

    fig.update_layout(
        title=f"Tren Waktu Pengamatan: {selected_param}",
        xaxis_title="Waktu Lokal (WITA)",
        yaxis_title=selected_param,
        hovermode="x unified",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: ANALISIS STATISTIK BERJENJANG ---
with tab2:
    st.subheader("📊 Analisis Variabilitas Waktu (WITA)")
    df_stats = df_filtered.dropna(subset=[selected_param]).copy()
    
    if not df_stats.empty:
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 
                       7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
        df_stats['Nama_Bulan'] = df_stats['Bulan'].map(month_names)
        
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            st.markdown("#### 📅 1. Distribusi Statistik Tahunan")
            fig_yearly = px.box(
                df_stats, x="Tahun", y=selected_param, color="Tahun", template="plotly_dark"
            )
            fig_yearly.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig_yearly, use_container_width=True)
            
        with c_top2:
            st.markdown("#### 🗓️ 2. Pola Climatology Bulanan")
            df_monthly_agg = df_stats.groupby(['Bulan', 'Nama_Bulan'])[selected_param].agg(['mean', 'std']).reset_index().sort_values('Bulan')
            fig_monthly = px.line(
                df_monthly_agg, x="Nama_Bulan", y="mean", markers=True, template="plotly_dark"
            )
            fig_monthly.update_traces(line_color='#00e676', line_width=3, marker_size=8)
            fig_monthly.update_layout(height=380)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        st.markdown("---")
        st.markdown("#### ⏰ 3. Siklus Diurnal Jam-jaman (Jam 00:00 - 23:00 WITA)")
        col_d1, col_d2 = st.columns([3, 1])
        
        with col_d1:
            diurnal_agg = df_stats.groupby('Jam')[selected_param].agg(['mean', 'min', 'max', 'std']).reset_index()
            fig_diurnal = go.Figure()
            fig_diurnal.add_trace(go.Scatter(
                x=diurnal_agg['Jam'], y=diurnal_agg['mean'], mode='lines+markers', line=dict(color='#ff9100', width=3)
            ))
            fig_diurnal.update_layout(
                xaxis=dict(title="Jam WITA", tickmode='array', tickvals=list(range(24)), range=[-0.3, 23.3]),
                yaxis=dict(title=selected_param), template="plotly_dark", height=420
            )
            st.plotly_chart(fig_diurnal, use_container_width=True)
            
        with col_d2:
            st.markdown("##### 📌 Karakteristik Puncak WITA")
            if not diurnal_agg.empty:
                max_row = diurnal_agg.loc[diurnal_agg['mean'].idxmax()]
                min_row = diurnal_agg.loc[diurnal_agg['mean'].idxmin()]
                st.info(f"**Tertinggi:**\nJam **{int(max_row['Jam']):02d}:00** WITA\n({max_row['mean']:.3f})")
                st.success(f"**Terendah:**\nJam **{int(min_row['Jam']):02d}:00** WITA\n({min_row['mean']:.3f})")

# --- TAB 3: PERBANDINGAN GLOBAL ---
with tab3:
    st.subheader("🌍 Perbandingan Konsentrasi Lokal vs Acuan Standar Global")
    if has_benchmark:
        bench_info = GLOBAL_BENCHMARKS[selected_param]
        comp_df = pd.DataFrame({
            "Kategori": ["Pengamatan Bariri", bench_info["name"]],
            "Nilai": [mean_val, bench_info["val"]]
        })
        fig_comp = px.bar(
            comp_df, x="Kategori", y="Nilai", color="Kategori", text_auto='.2f',
            template="plotly_dark", color_discrete_sequence=['#00d2ff', '#ff4b4b']
        )
        fig_comp.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)

# --- TAB 4: CUSTOM DOWNLOAD DATA ---
with tab4:
    st.subheader("📥 Filter & Unduh Data Kustom (Terproteksi)")
    st.info("🔒 Masukkan kredensial untuk dapat mengunduh data.")
    
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        user_id = st.text_input("User ID:", key="input_user_id")
    with col_auth2:
        user_pass = st.text_input("Password:", type="password", key="input_password")
        
    if user_id == "gawbariri" and user_pass == "gaw97094":
        st.success("✅ Autentikasi Berhasil!")
        all_cols = list(df_filtered.columns)
        selected_cols = st.multiselect("Pilih Kolom Data:", all_cols, default=['Tahun', 'Bulan', 'Tanggal', 'Jam', selected_param])
        
        drop_missing = st.checkbox("Keluarkan data missing (-9999 / NaN)", value=True)
        df_download = df_filtered[selected_cols].copy()
        if drop_missing and selected_param in df_download.columns:
            df_download = df_download.dropna(subset=[selected_param])
        
        st.dataframe(df_download.head(50), use_container_width=True)
        csv_bytes = df_download.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Unduh Dataset Terfilter WITA (CSV)",
            data=csv_bytes,
            file_name=f"GAW_Bariri_WITA_{selected_param}_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    elif user_id != "" or user_pass != "":
        st.error("❌ User ID atau Password salah!")
