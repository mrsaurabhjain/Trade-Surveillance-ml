# 🔍 Trade Surveillance & Market Abuse Detection

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![ML](https://img.shields.io/badge/ML-XGBoost%20%7C%20Isolation%20Forest-red?style=flat-square)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b?style=flat-square&logo=streamlit)
![Compliance](https://img.shields.io/badge/Regulatory-FCA%20MAR-darkgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

> **An AI-powered compliance system that monitors trading activity across 5 major investment banks, automatically flagging suspicious patterns aligned to FCA Market Abuse Regulation (MAR) Article 8 and Article 12 obligations.**

---

## 📌 Business Problem

Every investment bank in the UK is legally required under **FCA MAR** to monitor trading activity and report suspicious transactions. Failure to comply carries fines of up to **£76.7 million**.

Traditional surveillance is:
- ❌ Manual and reactive — analysts review alerts after the fact
- ❌ Rule-based — misses novel manipulation patterns  
- ❌ Slow — suspicious patterns identified days or weeks late
- ❌ Inconsistent — different analysts flag different events

**This system automates that monitoring using Machine Learning** — detecting statistically unusual trading days in real time, correlating them with corporate announcements, and prioritising alerts by risk level for analyst review.

---

## 📊 Key Findings

| Metric | Result |
|--------|--------|
| Banks monitored | 5 (JPM, GS, BARC, HSBC, MS) |
| Date range | January 2023 — January 2025 |
| Suspicious trading days detected | **78** |
| Correlation with corporate events | **24.4%** |
| Most predictive signal | **Event proximity (72% feature importance)** |
| HIGH risk flags requiring review | **18** |
| Model | XGBoost + Isolation Forest ensemble |

> 💡 **24.4% of flagged trades occurred within 5 days of an earnings announcement** — directly consistent with FCA MAR Article 8 insider dealing patterns.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DATA PIPELINE                          │
│  Yahoo Finance API → 5 Banks × 2 Years × OHLCV Data    │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│               FEATURE ENGINEERING                        │
│  Daily Return │ Volume Ratio │ Volatility │ Z-Score     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│            ANOMALY DETECTION (Notebook 2)                │
│         Isolation Forest — 78 flags detected            │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│         CORPORATE EVENT CORRELATION (Notebook 3)         │
│    Earnings dates + Dividends — 24.4% correlation       │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│            RISK SCORING (Notebook 4)                     │
│      XGBoost Classifier — HIGH / MEDIUM / LOW           │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│           STREAMLIT DASHBOARD (app.py)                   │
│    Live compliance UI — filter, drill down, export      │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 ML Approach

### Why Isolation Forest?
Most fraud datasets suffer from severe class imbalance — real abuse events are rare. **Isolation Forest is an unsupervised algorithm** that learns what "normal" looks like and flags statistical outliers, without needing labelled fraud examples. This mirrors how real banks bootstrap new surveillance systems before building labelled datasets.

### Feature Engineering
Each feature maps directly to FCA MAR surveillance criteria:

| Feature | Calculation | What It Detects |
|---------|-------------|-----------------|
| `daily_return` | `pct_change()` | Abnormal price movement |
| `volume_ratio` | `volume / 20d_avg` | Unusual trading activity — key insider trading signal |
| `volatility_5d` | `rolling(5).std()` | Elevated short-term instability |
| `return_zscore` | Z-score vs 20d avg | Statistically extreme price moves |

### Why XGBoost for Risk Scoring?
After Isolation Forest flags suspicious days, XGBoost classifies each flag as HIGH/MEDIUM/LOW risk. This two-stage approach:
- Stage 1 (unsupervised): Catches unknown patterns
- Stage 2 (supervised): Prioritises alerts by severity

**Feature importance result:** Event proximity (72%) >> Volume ratio (15%) >> Price move (11%) — confirming that trading near corporate announcements is the strongest abuse signal.

---

## 🗂️ Project Structure

```
trade-surveillance-ml/
│
├── notebooks/
│   ├── 01_data_collection.ipynb        # Data pipeline — Yahoo Finance API
│   ├── 02_anomaly_detection.ipynb      # Isolation Forest — 78 flags
│   ├── 03_news_nlp_correlation.ipynb   # Corporate event correlation
│   └── 04_xgboost_risk_scorer.ipynb    # XGBoost HIGH/MEDIUM/LOW classifier
│
├── data/
│   ├── bank_stocks_overview.png        # Price + volume charts
│   ├── anomaly_detection_results.png   # Flagged trades visualisation
│   ├── correlation_analysis.png        # Event correlation breakdown
│   ├── xgboost_results.png             # Feature importance + risk distribution
│   ├── flagged_trades_correlated.csv   # Full correlated dataset
│   ├── final_risk_scored.csv           # Risk-scored output
│   ├── xgboost_model.pkl               # Saved XGBoost model
│   └── encoders.pkl                    # Saved label encoders
│
├── app.py                              # Streamlit dashboard
├── requirements.txt                    # Dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/mrsaurabhjain/trade-surveillance-ml.git
cd trade-surveillance-ml

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app.py
```

### Run the Notebooks
Open Jupyter and run notebooks in order (01 → 02 → 03 → 04):

```bash
jupyter notebook
```

---

## 📈 Dashboard Features

- **KPI Metrics** — Total flags, HIGH/MEDIUM/LOW counts, event correlation rate
- **Interactive Price Chart** — Price history with flagged trades overlaid by risk level
- **Bank Filter** — Drill into individual bank surveillance
- **Risk Level Filter** — Focus on HIGH priority alerts only
- **Feature Importance** — XGBoost model explainability
- **Flagged Trade Log** — Full sortable table with colour-coded risk levels
- **CSV Export** — Download filtered report for analyst review

---

## 🏦 Real-World Applications

This system is directly applicable to:

| Team | Use Case |
|------|----------|
| **Compliance** | MAR Article 16 transaction monitoring obligations |
| **Risk Management** | Pre-trade surveillance and position monitoring |
| **Legal** | Evidence gathering for regulatory investigations |
| **Quant Research** | Alpha signal research — event-driven anomalies |
| **RegTech** | Scalable alternative to rule-based surveillance systems |

---

## 🔮 Future Enhancements

- [ ] Real-time streaming data via WebSocket (replace daily batch)
- [ ] NLP sentiment scoring on earnings call transcripts
- [ ] Network graph analysis — detect coordinated trading across accounts
- [ ] Expand to options market — unusual options activity precedes M&A
- [ ] REST API endpoint for integration with existing compliance platforms
- [ ] Backtesting framework — validate against known historical abuse cases

---

## 👤 Author

**SaurabhKumar Jain**  
Senior Data Analyst → AI/ML Analyst  
📍 London, United Kingdom  
🔗 [LinkedIn](https://linkedin.com/in/saurabhkumar-jain249706a1)  
💻 [GitHub](https://github.com/mrsaurabhjain)

*Domain expertise: Finance & Banking | 5+ years in financial data analytics*

---

## 📄 Regulatory Reference

This system is designed in alignment with:
- **FCA MAR Article 8** — Insider dealing prohibition and detection
- **FCA MAR Article 12** — Market manipulation detection  
- **FCA MAR Article 16** — Suspicious transaction and order reporting (STOR) obligations

---

> *"The strongest predictor of market abuse in this analysis was corporate event proximity — 72% of model importance. This directly validates the FCA's own guidance: unusual trading concentrated around announcements is the hallmark of insider dealing."*
