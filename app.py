import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# URL Logo Resmi BMKG
BMKG_LOGO_URL = "https://www.bmkg.go.id/asset/img/logo/logo-bmkg.png"

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GAW Lore Lindu Bariri", page_icon=BMKG_LOGO_URL, layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------------------
# 2. LOAD DATA DARI DATABASE
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
# 3. SIDEBAR NAVIGATION & TOGGLE TEMA CERAH/GELAP
# ------------------------------------------------------------------------------
st.sidebar.image(BMKG_LOGO_URL, width=80)
st.sidebar.title("GAW Lore Lindu Bariri")
st.sidebar.caption("Stasiun Pemantau Atmosfer Global - BMKG")
st.sidebar.markdown("---")

# SLIDE TOGGLE MODE CERAH (LIGHT MODE)
st.sidebar.markdown("### 🎨 Tema Tampilan")
light_mode = st.sidebar.toggle("☀️ Mode Cerah (Light)", value=False)

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

# ------------------------------------------------------------------------------
# 4. PENGATURAN SKEMA WARNA DUAL TEMA (DYNAMIC CSS)
# ------------------------------------------------------------------------------
if light_mode:
    # WAKTU CERAH: BIRU MUDA & PUTIH
    bg_main = "#F0F9FF"
    bg_sidebar = "#E0F2FE"
    card_bg = "#FFFFFF"
    card_border = "#BAE6FD"
    text_color = "#0F172A"
    text_sub = "#0369A1"
    grid_color = "#E2E8F0"
    plotly_template = "plotly_white"
    line_main = "#0284C7"
    line_trend = "#DC2626"
    plotly_bg = "#FFFFFF"
else:
    # WAKTU GELAP: MIDNIGHT COOL BLUE
    bg_main = "#0B1120"
    bg_sidebar = "#020617"
    card_bg = "#1E293B"
    card_border = "#334155"
    text_color = "#E2E8F0"
    text_sub = "#94A3B8"
    grid_color = "#1E293B"
    plotly_template = "plotly_dark"
    line_main = "#00E5FF"
    line_trend = "#FF3366"
    plotly_bg = "#0B1120"

# Inject Custom CSS berdasarkan pilihan tema
st.markdown(f"""
    <style>
    .stApp, .main {{ background-color: {bg_main} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; border-right: 1px solid {card_border}; }}
    
    .stMetric {{ 
        background-color: {card_bg} !important; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid {card_border}; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }}
    .stMetric label {{ color: {text_sub} !important; font-weight: 600; }}
    .stMetric div {{ color: {text_color} !important; }}
    
    .stTabs [aria-selected="true"] {{ color: #0284C7 !important; border-bottom-color: #0284C7 !important; }}
    
    body, .stApp, p, h1, h2, h3, h4, h5, h6, span, label {{
        color: {text_color} !important;
        -webkit-user-select: none !important; -moz-user-select: none !important; -ms-user-select: none !important; user-select: none !important;
    }}
    
    /* Sembunyikan Bawaan Streamlit */
    #MainMenu, footer, header {{ visibility: hidden; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# INJEKSI JS: MENUBAH JUDUL TAB BROWSER & MENYEMBUNYIKAN MANAGE APP + INSPECT
components.html(
    """<script>
    const doc = window.parent.document;
    
    // 1. Ubah Judul Tab Browser (Hapus '· Streamlit')
    doc.title = "GAW Lore Lindu Bariri";
    
    // 2. Injeksi CSS Sembunyikan 'Manage app' Button Secara Paksa
    const style = doc.createElement('style');
    style.innerHTML = `
        [data-testid="stStatusWidget"],
        [data-testid="manage-app-button"],
        .stAppViewer,
        footer,
        #MainMenu { display: none !important; }
    `;
    doc.head.appendChild(style);

    // 3. Matikan Klik Kanan & F12
    doc.addEventListener('contextmenu', event => event.preventDefault());
    doc.addEventListener('keydown', function(e) {
        if(e.keyCode == 123) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.keyCode == 85) { e.preventDefault(); return false; }
    });
    </script>""", height=0, width=0
)

custom_bg = dict(paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, font=dict(color=text_color))

# ------------------------------------------------------------------------------
# 5. FILTERING DATA & METRICS HEADER
# ------------------------------------------------------------------------------
mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()
df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, np.nan)
df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param].rolling(window=ma_window, min_periods=1).mean() if apply_ma else df_filtered[selected_param]

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(f"📡 Monitoring {instrument}")
    st.caption(f"Lokasi: Bariri, Sulawesi Tengah | Zona Waktu: WITA | Periode: {start_date} s/d {end_date}")
with col_head2:
    with st.expander("📍 Peta Lokasi Stasiun"):
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
# 6. TABS INTERFACE
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Time Series", "📊 Statistik & Heatmap", "🌍 Status Kualitas Udara", "🔒 Download Data"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date_Time"], y=df_filtered[f'{selected_param}_plot'], mode='lines', name=f"Data {selected_param}", line=dict(color=line_main, width=1.5)))
    
    df_trend_valid = df_filtered.dropna(subset=[selected_param]).copy()
    if show_trend and len(df_trend_valid) > 1:
        x_secs = (df_trend_valid["Date_Time"] - df_trend_valid["Date_Time"].min()).dt.total_seconds()
        slope, intercept = np.polyfit(x_secs, df_trend_valid[selected_param], 1)
        fig.add_trace(go.Scatter(x=df_trend_valid["Date_Time"], y=slope * x_secs + intercept, mode='lines', name='Tren Linear', line=dict(color=line_trend, width=2.5, dash='dash')))
    
    if has_benchmark:
        fig.add_hline(y=bench_val, line_dash="dot", line_color="#F43F5E", annotation_text=f"Global Ref: {bench_val}")
    
    fig.update_layout(xaxis_title="Waktu (WITA)", yaxis_title=selected_param, hovermode="x unified", template=plotly_template, height=500, **custom_bg)
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df_stats = df_filtered.dropna(subset=[selected_param]).copy()
    if not df_stats.empty:
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
        df_stats['Nama_Bulan'] = df_stats['Bulan'].map(month_names)
        
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            fig_yearly = px.box(df_stats, x="Tahun", y=selected_param, color="Tahun", template=plotly_template, title="Variasi Tahunan", color_discrete_sequence=['#38BDF8', '#0284C7', '#0369A1'])
            fig_yearly.update_layout(showlegend=False, height=380, **custom_bg)
            fig_yearly.update_xaxes(gridcolor=grid_color)
            fig_yearly.update_yaxes(gridcolor=grid_color)
            st.plotly_chart(fig_yearly, use_container_width=True)
            
        with c_top2:
            df_monthly_agg = df_stats.groupby(['Bulan', 'Nama_Bulan'])[selected_param].mean().reset_index().sort_values('Bulan')
            fig_monthly = px.line(df_monthly_agg, x="Nama_Bulan", y=selected_param, markers=True, template=plotly_template, title="Pola Musiman Bulanan")
            fig_monthly.update_traces(line_color='#0284C7', line_width=3, marker=dict(size=8, color='#0284C7'))
            fig_monthly.update_layout(height=380, **custom_bg)
            fig_monthly.update_xaxes(gridcolor=grid_color)
            fig_monthly.update_yaxes(gridcolor=grid_color)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        st.markdown("---")
        
        c_bot1, c_bot2 = st.columns(2)
        with c_bot1:
            diurnal_agg = df_stats.groupby('Jam')[selected_param].mean().reset_index()
            fig_diurnal = px.line(diurnal_agg, x='Jam', y=selected_param, markers=True, template=plotly_template, title="Siklus Diurnal (WITA)")
            fig_diurnal.update_traces(line_color='#0284C7', line_width=3, marker=dict(size=8))
            fig_diurnal.update_layout(height=380, **custom_bg)
            fig_diurnal.update_xaxes(tickmode='array', tickvals=list(range(24)), range=[-0.3, 23.3], gridcolor=grid_color)
            fig_diurnal.update_yaxes(gridcolor=grid_color)
            st.plotly_chart(fig_diurnal, use_container_width=True)
            
        with c_bot2:
            heatmap_data = df_stats.groupby(['Nama_Bulan', 'Bulan', 'Jam'])[selected_param].mean().reset_index().sort_values('Bulan')
            fig_heat = px.density_heatmap(heatmap_data, x="Jam", y="Nama_Bulan", z=selected_param, histfunc="avg", template=plotly_template, title="Heatmap Konsentrasi", color_continuous_scale="Blues" if light_mode else "ice")
            fig_heat.update_layout(height=380, **custom_bg)
            fig_heat.update_xaxes(tickmode='array', tickvals=list(range(24)), gridcolor=grid_color)
            fig_heat.update_yaxes(gridcolor=grid_color)
            st.plotly_chart(fig_heat, use_container_width=True)

with tab3:
    if has_benchmark:
        st.subheader("🌍 Status Indeks Terhadap Acuan Global")
        bench_info = GLOBAL_BENCHMARKS[selected_param]
        
        c_gauge1, c_gauge2 = st.columns([1, 1])
        with c_gauge1:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = mean_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Bariri vs {bench_info['name']}", 'font': {'size': 20, 'color': text_color}},
                delta = {'reference': bench_info['val'], 'increasing': {'color': "#F43F5E"}, 'decreasing': {'color': "#10B981"}},
                gauge = {
                    'axis': {'range': [None, bench_info['max_gauge']], 'tickwidth': 1, 'tickcolor': grid_color},
                    'bar': {'color': line_main},
                    'bgcolor': card_bg,
                    'borderwidth': 2,
                    'bordercolor': card_border,
                    'steps': [
                        {'range': [0, bench_info['val']], 'color': "rgba(16, 185, 129, 0.15)"},
                        {'range': [bench_info['val'], bench_info['max_gauge']], 'color': "rgba(244, 63, 94, 0.2)"}],
                    'threshold': {
                        'line': {'color': "#F43F5E", 'width': 4},
                        'thickness': 0.75,
                        'value': bench_info['val']}}
            ))
            fig_gauge.update_layout(template=plotly_template, height=400, **custom_bg)
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
