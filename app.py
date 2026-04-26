import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pickle
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Trade Surveillance System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #2E75B6;
    }
    .high-risk  { border-left: 4px solid #C00000 !important; }
    .med-risk   { border-left: 4px solid #FF9900 !important; }
    .low-risk   { border-left: 4px solid #1E7145 !important; }
    .stDataFrame { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('data/final_risk_scored.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_stock_data():
    tickers = ['JPM', 'GS', 'BARC.L', 'HSBA.L', 'MS']
    raw = yf.download(tickers, start='2023-01-01',
                      end='2025-01-01', auto_adjust=True)
    return raw['Close'], raw['Volume']

df        = load_data()
close, volume = load_stock_data()

bank_tickers = {
    'JP Morgan':     'JPM',
    'Goldman Sachs': 'GS',
    'Barclays':      'BARC.L',
    'HSBC':          'HSBA.L',
    'Morgan Stanley':'MS'
}

risk_colours = {'HIGH': '#C00000', 'MEDIUM': '#FF9900', 'LOW': '#1E7145'}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/law.png", width=60)
    st.title("Trade Surveillance")
    st.caption("FCA MAR Compliance System")
    st.divider()

    selected_bank = st.selectbox(
        "Select Bank",
        ["All Banks"] + list(bank_tickers.keys())
    )
    selected_risk = st.multiselect(
        "Risk Level",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )
    st.divider()
    st.caption("📋 Regulatory Context")
    st.info("This system monitors trading activity under **FCA MAR Article 8** (Insider Dealing) and **Article 12** (Market Manipulation) obligations.")

# ── Filter Data ───────────────────────────────────────────────
filtered = df[df['risk_level'].isin(selected_risk)]
if selected_bank != "All Banks":
    filtered = filtered[filtered['bank'] == selected_bank]

# ── Header ────────────────────────────────────────────────────
st.title("🔍 Trade Surveillance & Market Abuse Detection")
st.caption("AI-powered monitoring system | 5 Major Investment Banks | 2023–2025")
st.divider()

# ── KPI Metrics ───────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_flags  = len(filtered)
high_flags   = len(filtered[filtered['risk_level'] == 'HIGH'])
med_flags    = len(filtered[filtered['risk_level'] == 'MEDIUM'])
low_flags    = len(filtered[filtered['risk_level'] == 'LOW'])
corr_rate    = round(
    len(filtered[filtered['event_type'] != 'No event in window']) /
    max(len(filtered), 1) * 100, 1
)

col1.metric("Total Flags",       total_flags,  "Flagged trades")
col2.metric("🔴 HIGH Risk",       high_flags,   "Immediate review")
col3.metric("🟠 MEDIUM Risk",     med_flags,    "Monitor closely")
col4.metric("🟢 LOW Risk",        low_flags,    "Log & watch")
col5.metric("Event Correlation", f"{corr_rate}%","Near announcements")

st.divider()

# ── Main Charts ───────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📈 Price Chart with Flagged Trades")

    if selected_bank != "All Banks":
        ticker     = bank_tickers[selected_bank]
        price_data = close[ticker].dropna()
        bank_flags = filtered[filtered['bank'] == selected_bank]

        fig = go.Figure()

        # Price line
        fig.add_trace(go.Scatter(
            x=price_data.index, y=price_data.values,
            mode='lines', name='Price',
            line=dict(color='#2E75B6', width=1.5),
            opacity=0.8
        ))

        # Flagged trades by risk level
        for risk, colour in risk_colours.items():
            risk_flags = bank_flags[bank_flags['risk_level'] == risk]
            if not risk_flags.empty:
                flag_prices = [
                    price_data.get(pd.Timestamp(d), None)
                    for d in risk_flags['date']
                ]
                fig.add_trace(go.Scatter(
                    x=risk_flags['date'],
                    y=flag_prices,
                    mode='markers',
                    name=f'{risk} Risk',
                    marker=dict(color=colour, size=12,
                                symbol='circle',
                                line=dict(color='white', width=1)),
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        f"Risk: {risk}<br>"
                        "Price: %{y:.2f}<extra></extra>"
                    )
                ))

        fig.update_layout(
            template='plotly_dark',
            height=400,
            showlegend=True,
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # All banks — show risk distribution over time
        monthly = filtered.copy()
        monthly['month'] = pd.to_datetime(monthly['date']).dt.to_period('M').astype(str)
        monthly_counts = monthly.groupby(['month','risk_level']).size().reset_index(name='count')

        fig = px.bar(
            monthly_counts, x='month', y='count',
            color='risk_level',
            color_discrete_map=risk_colours,
            title="Monthly Alert Volume by Risk Level",
            template='plotly_dark',
            height=400
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📊 Risk Distribution")

    risk_counts = filtered['risk_level'].value_counts().reset_index()
    risk_counts.columns = ['Risk Level', 'Count']

    fig_pie = px.pie(
        risk_counts, values='Count', names='Risk Level',
        color='Risk Level',
        color_discrete_map=risk_colours,
        template='plotly_dark',
        height=220,
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, margin=dict(t=20,b=0,l=0,r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🏦 Flags per Bank")
    bank_risk = filtered.groupby(['bank','risk_level']).size().unstack(fill_value=0)
    for col in ['HIGH','MEDIUM','LOW']:
        if col not in bank_risk.columns:
            bank_risk[col] = 0
    bank_risk = bank_risk[['HIGH','MEDIUM','LOW']]

    fig_bar = px.bar(
        bank_risk.reset_index(),
        x='bank', y=['HIGH','MEDIUM','LOW'],
        color_discrete_map=risk_colours,
        template='plotly_dark',
        height=220,
        barmode='stack'
    )
    fig_bar.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Flags",
        margin=dict(t=20,b=0,l=0,r=0),
        xaxis_tickangle=-20
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Feature Importance ────────────────────────────────────────
col_feat, col_finding = st.columns([2, 3])

with col_feat:
    st.subheader("🤖 XGBoost Feature Importance")
    features = pd.DataFrame({
        'Feature':    ['Event Type','Volume Ratio','Price Move',
                       'Days to Event','Bank'],
        'Importance': [0.72, 0.15, 0.11, 0.02, 0.01]
    }).sort_values('Importance')

    fig_feat = px.bar(
        features, x='Importance', y='Feature',
        orientation='h', template='plotly_dark',
        color='Importance',
        color_continuous_scale=['#2E75B6','#C00000'],
        height=280
    )
    fig_feat.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=10,b=0,l=0,r=0)
    )
    st.plotly_chart(fig_feat, use_container_width=True)

with col_finding:
    st.subheader("🔎 Key Findings")
    st.markdown("""
    | Finding | Value | Significance |
    |---------|-------|--------------|
    | Total suspicious trading days detected | **78** | Across 5 banks, 2 years |
    | Correlation with corporate events | **24.4%** | FCA MAR Article 8 signal |
    | Most predictive feature | **Event proximity** | 72% model importance |
    | Highest risk bank | **HSBC & JP Morgan** | 5 HIGH flags each |
    | Model | **XGBoost + Isolation Forest** | Ensemble approach |
    """)
    st.info("💡 **Interview Insight:** Event proximity being the strongest predictor (72%) directly validates FCA MAR Article 8 — unusual trading concentrated around corporate announcements is the hallmark of insider dealing.")

st.divider()

# ── Flagged Trades Table ──────────────────────────────────────
st.subheader("🚨 Flagged Trade Log")

display_cols = ['date','bank','price_move_pct',
                'volume_ratio','risk_level',
                'event_type','event_detail','days_to_event']

display_df = filtered[display_cols].copy()
display_df = display_df.sort_values(['risk_level','volume_ratio'],
             key=lambda x: x.map({'HIGH':0,'MEDIUM':1,'LOW':2})
             if x.name == 'risk_level' else x,
             ascending=[True, False])

def colour_risk(val):
    colours = {
        'HIGH':   'background-color: #3d0000; color: #ff4444; font-weight: bold',
        'MEDIUM': 'background-color: #3d2600; color: #ff9900; font-weight: bold',
        'LOW':    'background-color: #003d1a; color: #00cc44; font-weight: bold'
    }
    return colours.get(val, '')

styled = display_df.style.map(
    colour_risk, subset=['risk_level']
).format({
    'price_move_pct': '{:.2f}%',
    'volume_ratio':   '{:.2f}x'
})

st.dataframe(styled, use_container_width=True, height=400)

# ── Download Button ───────────────────────────────────────────
csv = filtered[display_cols].to_csv(index=False)
st.download_button(
    label="⬇️ Download Flagged Trades Report",
    data=csv,
    file_name="trade_surveillance_report.csv",
    mime="text/csv"
)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption("Trade Surveillance System | Built with Python, XGBoost, Isolation Forest & Streamlit | FCA MAR Compliance | Saurabh Kumar Jain | 2026")