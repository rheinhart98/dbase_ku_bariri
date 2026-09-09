import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

BMKG_LOGO_URL = "https://www.bmkg.go.id/asset/img/logo/logo-bmkg.png"

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="GAW Lore Lindu Bariri",
    page_icon=BMKG_LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# 2. DICTIONARY MULTI-BAHASA (I18N)
# ------------------------------------------------------------------------------
LANG_DATA = {
    "English": {
        "theme_title": "🎨 Display Theme",
        "light_mode": "☀️ Light Mode",
        "lang_select": "🌐 Language",
        "inst_select": "📌 Select Instrument:",
        "param_select": "📊 Select Parameter:",
        "range_select": "📅 Time Range:",
        "preset_options": ["All Years (Full Data)", "Last 1 Year", "Last 6 Months", "Last 1 Month", "Custom Date"],
        "show_trend": "📈 Show Trendline",
        "apply_ma": "🌊 Apply Moving Average",
        "ma_window": "MA Window (Hours):",
        "status_badge": "SYSTEM OPERATIONAL — WITA TIMEZONE",
        "map_title": "📍 Station Location Map",
        "avg_local": "Local Average",
        "max_val": "Maximum Value",
        "min_val": "Minimum Value",
        "global_ref": "Global Ref",
        "valid_data": "Valid Data",
        "tabs": ["📈 Time Series", "📊 Statistics & Heatmap", "🌍 Air Quality Status", "🔒 Data Download"],
        "trend_line_name": "Linear Trend",
        "time_x": "Time (WITA)",
        "trend_title": "Observation Trend:",
        "yearly_title": "Yearly Variation",
        "monthly_title": "Monthly Seasonal Pattern",
        "diurnal_title": "Diurnal Cycle (WITA)",
        "heatmap_title": "Concentration Heatmap",
        "month_names": {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'},
        "aq_subheader": "🌍 Status Index Against Global Baseline",
        "aq_analysis": "Status Analysis:",
        "aq_bariri_val": "Bariri Station Value:",
        "aq_global_val": "Global Threshold:",
        "aq_conclusion": "Conclusion:",
        "aq_above": "above (higher/worse)",
        "aq_below": "below (lower)",
        "aq_conc_text": "The current concentration of **{param}** is **{diff:.2f} {unit}** {status} standard global background levels.",
        "no_benchmark": "This parameter does not have a global baseline reference.",
        "dl_subheader": "📥 Data Download (Protected)",
        "dl_user": "User ID:",
        "dl_pass": "Password:",
        "dl_success": "✅ Authentication Successful!",
        "dl_error": "❌ Invalid Credentials!",
        "dl_cols": "Select Data Columns:",
        "dl_drop_na": "Exclude missing data (-9999 / NaN)",
        "dl_btn": "💾 Download CSV (WITA)",
        "benchmarks": {
            "CO2_sync": {"name": "Global CO2 (WMO)", "val": 422.0, "unit": "ppm", "max_gauge": 500},
            "CO2_dry_sync": {"name": "Global Dry CO2", "val": 422.0, "unit": "ppm", "max_gauge": 500},
            "CH4_sync": {"name": "Global CH4 (WMO)", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
            "CH4_dry_sync": {"name": "Global Dry CH4", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
            "CO_sync": {"name": "Background CO", "val": 0.10, "unit": "ppm", "max_gauge": 2.0},
            "O3_Concentration_ppb": {"name": "WHO Guideline (O3)", "val": 50.0, "unit": "ppb", "max_gauge": 100.0}
        }
    },
    "Bahasa Indonesia": {
        "theme_title": "🎨 Tema Tampilan",
        "light_mode": "☀️ Mode Cerah (Light)",
        "lang_select": "🌐 Bahasa",
        "inst_select": "📌 Pilih Instrumen:",
        "param_select": "📊 Pilih Parameter:",
        "range_select": "📅 Rentang Waktu:",
        "preset_options": ["Semua Tahun (Full Data)", "1 Tahun Terakhir", "6 Bulan Terakhir", "1 Bulan Terakhir", "Custom Tanggal"],
        "show_trend": "📈 Tampilkan Garis Tren",
        "apply_ma": "🌊 Gunakan Moving Average",
        "ma_window": "Jendela MA (Jam):",
        "status_badge": "SYSTEM OPERATIONAL — WITA TIMEZONE",
        "map_title": "📍 Peta Lokasi Stasiun",
        "avg_local": "Rata-Rata Lokal",
        "max_val": "Nilai Maksimum",
        "min_val": "Nilai Minimum",
        "global_ref": "Acuan Global",
        "valid_data": "Data Valid",
        "tabs": ["📈 Time Series", "📊 Statistik & Heatmap", "🌍 Status Kualitas Udara", "🔒 Download Data"],
        "trend_line_name": "Tren Linear",
        "time_x": "Waktu (WITA)",
        "trend_title": "Tren Waktu Pengamatan:",
        "yearly_title": "Variasi Tahunan",
        "monthly_title": "Pola Musiman Bulanan",
        "diurnal_title": "Siklus Diurnal (WITA)",
        "heatmap_title": "Heatmap Konsentrasi",
        "month_names": {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'},
        "aq_subheader": "🌍 Status Indeks Terhadap Acuan Global",
        "aq_analysis": "Analisis Status:",
        "aq_bariri_val": "Nilai Stasiun Bariri:",
        "aq_global_val": "Ambang Batas Global:",
        "aq_conclusion": "Kesimpulan:",
        "aq_above": "di atas (lebih buruk/tinggi)",
        "aq_below": "di bawah (lebih rendah)",
        "aq_conc_text": "Konsentrasi **{param}** saat ini berada **{diff:.2f} {unit}** {status} dari nilai standar latar belakang global.",
        "no_benchmark": "Parameter ini tidak memiliki acuan baseline global.",
        "dl_subheader": "📥 Download Data (Terproteksi)",
        "dl_user": "User ID:",
        "dl_pass": "Password:",
        "dl_success": "✅ Autentikasi Berhasil!",
        "dl_error": "❌ Kredensial salah!",
        "dl_cols": "Pilih Kolom Data:",
        "dl_drop_na": "Keluarkan data missing (-9999 / NaN)",
        "dl_btn": "💾 Unduh CSV (WITA)",
        "benchmarks": {
            "CO2_sync": {"name": "CO2 Global (WMO)", "val": 422.0, "unit": "ppm", "max_gauge": 500},
            "CO2_dry_sync": {"name": "CO2 Dry Global", "val": 422.0, "unit": "ppm", "max_gauge": 500},
            "CH4_sync": {"name": "CH4 Global (WMO)", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
            "CH4_dry_sync": {"name": "CH4 Dry Global", "val": 1.93, "unit": "ppm", "max_gauge": 3.0},
            "CO_sync": {"name": "Latar Belakang CO", "val": 0.10, "unit": "ppm", "max_gauge": 2.0},
            "O3_Concentration_ppb": {"name": "Pedoman WHO (O3)", "val": 50.0, "unit": "ppb", "max_gauge": 100.0}
        }
    }
}

# ------------------------------------------------------------------------------
# 3. LOAD DATA DARI GITHUB
# ------------------------------------------------------------------------------
URL_PICARRO = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/PICARRO_FULL_TIMESERIES_QC.csv"
URL_OZON = "https://raw.githubusercontent.com/rheinhart98/dbase_ku_bariri/main/OZON_ACOEM_ALL_YEARS_hourly_clean.csv"

@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    df['Date_Time'] = pd.to_datetime(df['Tahun'].astype(str) + '-' + df['Bulan'].astype(str) + '-' + df['Tanggal'].astype(str) + ' ' + df['Jam'].astype(str) + ':00:00', errors='coerce') + pd.Timedelta(hours=8)
    df['Tahun'] = df['Date_Time'].dt.year
    df['Bulan'] = df['Date_Time'].dt.month
    df['Tanggal'] = df['Date_Time'].dt.day
    df['Jam'] = df['Date_Time'].dt.hour
    return df

# ------------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & LANGUAGE TOGGLE
# ------------------------------------------------------------------------------
st.sidebar.image(BMKG_LOGO_URL, width=85)
st.sidebar.title("GAW Lore Lindu Bariri")
st.sidebar.caption("Global Atmosphere Watch - BMKG")
st.sidebar.markdown("---")

# Opsi Pemilih Bahasa (Default English)
selected_lang = st.sidebar.radio("🌐 Language / Bahasa", ["English", "Bahasa Indonesia"], index=0)
t = LANG_DATA[selected_lang]

st.sidebar.markdown(f"### {t['theme_title']}")
light_mode = st.sidebar.toggle(t['light_mode'], value=False)
st.sidebar.markdown("---")

instrument = st.sidebar.radio(t['inst_select'], ["Picarro (GHG)", "Ozon (ACOEM)"])
if instrument == "Picarro (GHG)":
    df = load_data(URL_PICARRO)
    available_params = ["CO2_sync", "CO2_dry_sync", "CH4_sync", "CH4_dry_sync", "CO_sync", "H2O_sync"]
else:
    df = load_data(URL_OZON)
    available_params = ["O3_Concentration_ppb", "Chassis_Temp_C", "Lamp_Temp_C", "Ambient_Pressure_torr"]

selected_param = st.sidebar.selectbox(t['param_select'], available_params)

min_date, max_date = df['Date_Time'].min().date(), df['Date_Time'].max().date()
preset_options = t['preset_options']
preset_range = st.sidebar.selectbox(t['range_select'], preset_options)

if preset_range == preset_options[0]: start_date, end_date = min_date, max_date
elif preset_range == preset_options[1]: start_date, end_date = max_date - pd.Timedelta(days=365), max_date
elif preset_range == preset_options[2]: start_date, end_date = max_date - pd.Timedelta(days=180), max_date
elif preset_range == preset_options[3]: start_date, end_date = max_date - pd.Timedelta(days=30), max_date
else:
    date_selection = st.sidebar.date_input("Custom:", [min_date, max_date], min_value=min_date, max_value=max_date)
    start_date, end_date = date_selection if len(date_selection) == 2 else (min_date, max_date)

show_trend = st.sidebar.checkbox(t['show_trend'], value=True)
apply_ma = st.sidebar.checkbox(t['apply_ma'])
ma_window = st.sidebar.slider(t['ma_window'], 3, 72, 24) if apply_ma else 1

GLOBAL_BENCHMARKS = t['benchmarks']

# ------------------------------------------------------------------------------
# 5. SKEMA WARNA DUAL TEMA & GRADIENT SIDEBAR + MAIN BACKGROUND
# ------------------------------------------------------------------------------
if light_mode:
    bg_gradient = """
        radial-gradient(circle at 12% 15%, rgba(56, 189, 248, 0.22), transparent 40%),
        radial-gradient(circle at 88% 85%, rgba(129, 140, 248, 0.18), transparent 45%),
        linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)
    """
    bg_sidebar = """
        radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.15), transparent 60%),
        linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%)
    """
    card_bg = "rgba(255, 255, 255, 0.82)"
    card_border = "#E2E8F0"
    text_color = "#0F172A"
    text_sub = "#0284C7"
    grid_color = "#CBD5E1"
    plotly_template = "plotly_white"
    line_main = "#0284C7"
    line_trend = "#EF4444"
    plotly_bg = "rgba(0,0,0,0)"
    hover_bg, hover_text = "#FFFFFF", "#0F172A"
    glow_shadow = "0 10px 25px -5px rgba(2, 132, 199, 0.08)"

    dock_bg = "rgba(241, 245, 249, 0.85)"
    dock_border = "rgba(2, 132, 199, 0.3)"
    dock_item_bg = "rgba(255, 255, 255, 0.85)"
    dock_item_border = "rgba(203, 213, 225, 0.8)"
    dock_text = "#475569"
    dock_active_bg = "rgba(2, 132, 199, 0.18)"
    dock_active_border = "#0284C7"
    dock_active_text = "#0284C7"

    input_bg = "rgba(255, 255, 255, 0.9)"
    input_border = "#CBD5E1"
    input_text = "#0F172A"
else:
    bg_gradient = """
        radial-gradient(circle at 15% 18%, rgba(0, 242, 254, 0.14), transparent 42%),
        radial-gradient(circle at 85% 82%, rgba(112, 0, 255, 0.14), transparent 48%),
        linear-gradient(135deg, #040711 0%, #0B1226 50%, #03050E 100%)
    """
    bg_sidebar = """
        radial-gradient(circle at 50% 0%, rgba(0, 242, 254, 0.15), transparent 60%),
        linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(3, 7, 18, 0.96) 100%)
    """
    card_bg = "rgba(15, 23, 42, 0.72)"
    card_border = "rgba(56, 189, 248, 0.22)"
    text_color = "#F8FAFC"
    text_sub = "#38BDF8"
    grid_color = "rgba(30, 41, 59, 0.6)"
    plotly_template = "plotly_dark"
    line_main = "#00F2FE"
    line_trend = "#FF2A6D"
    plotly_bg = "rgba(0,0,0,0)"
    hover_bg, hover_text = "#0F172A", "#F8FAFC"
    glow_shadow = "0 10px 30px -5px rgba(0, 242, 254, 0.18)"

    dock_bg = "rgba(15, 23, 42, 0.75)"
    dock_border = "rgba(56, 189, 248, 0.3)"
    dock_item_bg = "rgba(255, 255, 255, 0.04)"
    dock_item_border = "rgba(255, 255, 255, 0.08)"
    dock_text = "#94A3B8"
    dock_active_bg = "rgba(56, 189, 248, 0.22)"
    dock_active_border = "rgba(56, 189, 248, 0.8)"
    dock_active_text = "#38BDF8"

    input_bg = "rgba(30, 41, 59, 0.85)"
    input_border = "#334155"
    input_text = "#F8FAFC"

st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background: {bg_gradient} !important;
        background-attachment: fixed !important;
    }}

    section.main, .block-container, [data-testid="stVerticalBlock"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        border-right: 1px solid {card_border} !important;
        backdrop-filter: blur(16px) !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 99999 !important;
    }}

    [data-testid="collapsedControl"],
    button[data-testid="stHeaderIconButton"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 10px !important;
        padding: 6px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }}
    [data-testid="collapsedControl"] svg,
    button[data-testid="stHeaderIconButton"] svg {{
        fill: #38BDF8 !important;
        color: #38BDF8 !important;
    }}

    .stMetric {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        box-shadow: {glow_shadow};
        backdrop-filter: blur(16px) !important;
        padding: 18px 20px;
        border-radius: 16px !important;
    }}
    .stMetric label {{ color: {text_sub} !important; font-weight: 700 !important; font-size: 0.78rem !important; }}
    .stMetric div[data-testid="stMetricValue"] {{ color: {text_color} !important; font-weight: 800 !important; }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border-color: {input_border} !important;
        color: {input_text} !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }}
    div[data-baseweb="select"] span {{ color: {input_text} !important; }}

    [data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        margin-bottom: 4px !important;
        backdrop-filter: blur(10px) !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        background: {dock_bg} !important;
        backdrop-filter: blur(16px) !important;
        padding: 8px 14px !important;
        border-radius: 40px !important;
        border: 1px solid {dock_border} !important;
        box-shadow: {glow_shadow} !important;
        margin-bottom: 25px !important;
        width: fit-content !important;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {{ display: none !important; }}
    div[data-testid="stRadio"] label[data-baseweb="radio"] {{
        background: {dock_item_bg} !important;
        border: 1px solid {dock_item_border} !important;
        padding: 8px 20px !important;
        border-radius: 30px !important;
        margin: 0 !important;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {{
        color: {dock_text} !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {{
        background: {dock_active_bg} !important;
        border: 1px solid {dock_active_border} !important;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color: {dock_active_text} !important;
        font-weight: 700 !important;
    }}

    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10B981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    .pulse-dot {{
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.6s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    body, .stApp, p, h1, h2, h3, h4, h5, h6, span, label {{
        color: {text_color} !important;
        -webkit-user-select: none !important; -moz-user-select: none !important; -ms-user-select: none !important; user-select: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. JS LOCK TITLE & ADMIN HIDE
# ------------------------------------------------------------------------------
components.html(
    """<script>
    const doc = window.parent.document;

    function lockTitle() {
        if (doc.title !== "GAW Lore Lindu Bariri") {
            doc.title = "GAW Lore Lindu Bariri";
        }
    }
    lockTitle();
    setInterval(lockTitle, 300);

    const style = doc.createElement('style');
    style.innerHTML = `
        [data-testid="stStatusWidget"],
        [data-testid="manage-app-button"],
        .stAppViewer,
        footer,
        #MainMenu { display: none !important; visibility: hidden !important; }
    `;
    doc.head.appendChild(style);

    doc.addEventListener('contextmenu', event => event.preventDefault());
    doc.addEventListener('keydown', function(e) {
        if(e.keyCode == 123) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) { e.preventDefault(); return false; }
        if(e.ctrlKey && e.keyCode == 85) { e.preventDefault(); return false; }
    });
    </script>""", height=0, width=0
)

def apply_chart_theme(fig, chart_title="", is_gauge=False):
    layout_update = dict(
        paper_bgcolor=plotly_bg,
        plot_bgcolor=plotly_bg,
        font=dict(color=text_color, family="sans-serif"),
        legend=dict(font=dict(color=text_color)),
        hoverlabel=dict(bgcolor=hover_bg, font_color=hover_text, font_size=12, bordercolor=card_border)
    )
    if chart_title:
        layout_update["title"] = dict(text=chart_title, font=dict(color=text_color, size=16))

    fig.update_layout(**layout_update)

    if not is_gauge:
        fig.update_xaxes(title_font=dict(color=text_color), tickfont=dict(color=text_color), gridcolor=grid_color, zerolinecolor=grid_color)
        fig.update_yaxes(title_font=dict(color=text_color), tickfont=dict(color=text_color), gridcolor=grid_color, zerolinecolor=grid_color)

    return fig

# ------------------------------------------------------------------------------
# 7. FILTERING DATA & METRICS
# ------------------------------------------------------------------------------
mask = (df['Date_Time'].dt.date >= start_date) & (df['Date_Time'].dt.date <= end_date)
df_filtered = df.loc[mask].copy()
df_filtered[selected_param] = df_filtered[selected_param].replace(-9999, np.nan)
df_filtered[f'{selected_param}_plot'] = df_filtered[selected_param].rolling(window=ma_window, min_periods=1).mean() if apply_ma else df_filtered[selected_param]

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f'<div class="status-badge"><div class="pulse-dot"></div> {t["status_badge"]}</div>', unsafe_allow_html=True)
    st.title(f"📡 {instrument} Monitoring")
    st.caption(f"Bariri Global Atmosphere Watch Station | Period: **{start_date}** to **{end_date}**" if selected_lang == "English" else f"Stasiun Pemantau Atmosfer Global Bariri | Periode: **{start_date}** s/d **{end_date}**")
with col_head2:
    with st.expander(t['map_title']):
        loc_df = pd.DataFrame({'lat': [-1.65], 'lon': [120.16]})
        st.map(loc_df, zoom=10, use_container_width=True)

valid_series = df_filtered[selected_param].dropna()
mean_val, max_val, min_val = (valid_series.mean(), valid_series.max(), valid_series.min()) if not valid_series.empty else (0,0,0)

col1, col2, col3, col4 = st.columns(4)
col1.metric(t['avg_local'], f"{mean_val:.3f}")
col2.metric(t['max_val'], f"{max_val:.3f}")
col3.metric(t['min_val'], f"{min_val:.3f}")

has_benchmark = selected_param in GLOBAL_BENCHMARKS
if has_benchmark:
    bench_val = GLOBAL_BENCHMARKS[selected_param]["val"]
    col4.metric(
        label=f"{t['global_ref']} ({GLOBAL_BENCHMARKS[selected_param]['unit']})",
        value=f"{bench_val}",
        delta=f"{mean_val - bench_val:+.3f} vs Global",
        delta_color="inverse" if (mean_val - bench_val) > 0 else "normal"
    )
else:
    col4.metric(t['valid_data'], f"{(len(valid_series)/len(df_filtered)*100):.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 8. NAV-DOCK & TAB CONTENT
# ------------------------------------------------------------------------------
selected_tab = st.radio(
    "Navigation Dock",
    t['tabs'],
    horizontal=True,
    label_visibility="collapsed"
)

if selected_tab == t['tabs'][0]:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered["Date_Time"],
        y=df_filtered[f'{selected_param}_plot'],
        mode='lines',
        name=f"Data {selected_param}",
        line=dict(color=line_main, width=1.8, shape='spline')
    ))

    df_trend_valid = df_filtered.dropna(subset=[selected_param]).copy()
    if show_trend and len(df_trend_valid) > 1:
        x_secs = (df_trend_valid["Date_Time"] - df_trend_valid["Date_Time"].min()).dt.total_seconds()
        slope, intercept = np.polyfit(x_secs, df_trend_valid[selected_param], 1)
        fig.add_trace(go.Scatter(
            x=df_trend_valid["Date_Time"],
            y=slope * x_secs + intercept,
            mode='lines',
            name=t['trend_line_name'],
            line=dict(color=line_trend, width=2.2, dash='dash')
        ))

    if has_benchmark:
        fig.add_hline(y=bench_val, line_dash="dot", line_color="#F43F5E", annotation_text=f"Global Ref: {bench_val}")

    fig.update_layout(xaxis_title=t['time_x'], yaxis_title=selected_param, hovermode="x unified", template=plotly_template, height=520)
    apply_chart_theme(fig, chart_title=f"{t['trend_title']} {selected_param}")
    st.plotly_chart(fig, use_container_width=True)

elif selected_tab == t['tabs'][1]:
    df_stats = df_filtered.dropna(subset=[selected_param]).copy()
    if not df_stats.empty:
        month_names = t['month_names']
        df_stats['Nama_Bulan'] = df_stats['Bulan'].map(month_names)

        c_top1, c_top2 = st.columns(2)
        with c_top1:
            fig_yearly = px.box(df_stats, x="Tahun", y=selected_param, color="Tahun", template=plotly_template, title=t['yearly_title'], color_discrete_sequence=['#38BDF8', '#0284C7', '#0369A1'])
            fig_yearly.update_layout(showlegend=False, height=380)
            apply_chart_theme(fig_yearly, chart_title=t['yearly_title'])
            st.plotly_chart(fig_yearly, use_container_width=True)

        with c_top2:
            df_monthly_agg = df_stats.groupby(['Bulan', 'Nama_Bulan'])[selected_param].mean().reset_index().sort_values('Bulan')
            fig_monthly = px.line(df_monthly_agg, x="Nama_Bulan", y=selected_param, markers=True, template=plotly_template, title=t['monthly_title'])
            fig_monthly.update_traces(line_color='#0284C7', line_width=3, marker=dict(size=8, color='#0284C7'), line_shape='spline')
            fig_monthly.update_layout(height=380)
            apply_chart_theme(fig_monthly, chart_title=t['monthly_title'])
            st.plotly_chart(fig_monthly, use_container_width=True)

        st.markdown("---")

        c_bot1, c_bot2 = st.columns(2)
        with c_bot1:
            diurnal_agg = df_stats.groupby('Jam')[selected_param].mean().reset_index()
            fig_diurnal = px.line(diurnal_agg, x='Jam', y=selected_param, markers=True, template=plotly_template, title=t['diurnal_title'])
            fig_diurnal.update_traces(line_color='#0284C7', line_width=3, marker=dict(size=8), line_shape='spline')
            fig_diurnal.update_layout(height=380)
            fig_diurnal.update_xaxes(tickmode='array', tickvals=list(range(24)), range=[-0.3, 23.3])
            apply_chart_theme(fig_diurnal, chart_title=t['diurnal_title'])
            st.plotly_chart(fig_diurnal, use_container_width=True)

        with c_bot2:
            heatmap_data = df_stats.groupby(['Nama_Bulan', 'Bulan', 'Jam'])[selected_param].mean().reset_index().sort_values('Bulan')
            fig_heat = px.density_heatmap(heatmap_data, x="Jam", y="Nama_Bulan", z=selected_param, histfunc="avg", template=plotly_template, title=t['heatmap_title'], color_continuous_scale="Blues" if light_mode else "ice")
            fig_heat.update_layout(height=380)
            fig_heat.update_xaxes(tickmode='array', tickvals=list(range(24)))
            fig_heat.update_coloraxes(colorbar_tickfont_color=text_color, colorbar_title_font_color=text_color)
            apply_chart_theme(fig_heat, chart_title=t['heatmap_title'])
            st.plotly_chart(fig_heat, use_container_width=True)

elif selected_tab == t['tabs'][2]:
    if has_benchmark:
        st.subheader(t['aq_subheader'])
        bench_info = GLOBAL_BENCHMARKS[selected_param]

        c_gauge1, c_gauge2 = st.columns([1, 1])
        with c_gauge1:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = mean_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Bariri vs {bench_info['name']}", 'font': {'size': 18, 'color': text_color}},
                number = {'font': {'size': 48, 'color': text_color}},
                delta = {
                    'reference': bench_info['val'],
                    'position': "bottom",
                    'font': {'size': 22},
                    'increasing': {'color': "#F43F5E"},
                    'decreasing': {'color': "#10B981"}
                },
                gauge = {
                    'axis': {'range': [None, bench_info['max_gauge']], 'tickwidth': 1, 'tickcolor': text_color},
                    'bar': {'color': line_main},
                    'bgcolor': "rgba(0,0,0,0.1)",
                    'borderwidth': 2,
                    'bordercolor': card_border,
                    'steps': [
                        {'range': [0, bench_info['val']], 'color': "rgba(16, 185, 129, 0.18)"},
                        {'range': [bench_info['val'], bench_info['max_gauge']], 'color': "rgba(244, 63, 94, 0.22)"}],
                    'threshold': {
                        'line': {'color': "#F43F5E", 'width': 4},
                        'thickness': 0.75,
                        'value': bench_info['val']}}
            ))

            fig_gauge.update_layout(
                template=plotly_template,
                height=350,
                margin=dict(l=40, r=40, t=50, b=60)
            )
            apply_chart_theme(fig_gauge, is_gauge=True)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with c_gauge2:
            status_str = t['aq_above'] if mean_val > bench_info['val'] else t['aq_below']
            diff_val = abs(mean_val - bench_info['val'])
            conc_desc = t['aq_conc_text'].format(param=selected_param, diff=diff_val, unit=bench_info['unit'], status=status_str)

            st.markdown(f"""
            ### {t['aq_analysis']}
            - **{t['aq_bariri_val']}** `{mean_val:.2f} {bench_info['unit']}`
            - **{t['aq_global_val']}** `{bench_info['val']} {bench_info['unit']}`

            **{t['aq_conclusion']}**
            {conc_desc}
            """)
    else:
        st.warning(t['no_benchmark'])

elif selected_tab == t['tabs'][3]:
    st.subheader(t['dl_subheader'])
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1: user_id = st.text_input(t['dl_user'], key="input_user_id")
    with col_auth2: user_pass = st.text_input(t['dl_pass'], type="password", key="input_password")

    if user_id == "gawbariri" and user_pass == "gaw97094":
        st.success(t['dl_success'])
        selected_cols = st.multiselect(t['dl_cols'], list(df_filtered.columns), default=['Tahun', 'Bulan', 'Tanggal', 'Jam', selected_param])
        df_download = df_filtered[selected_cols].dropna(subset=[selected_param]) if st.checkbox(t['dl_drop_na'], value=True) else df_filtered[selected_cols].copy()
        st.dataframe(df_download.head(50), use_container_width=True)
        st.download_button(t['dl_btn'], df_download.to_csv(index=False).encode('utf-8'), f"GAW_Bariri_{selected_param}.csv", "text/csv")
    elif user_id or user_pass:
        st.error(t['dl_error'])
