# 💹 Event Study: M&A Market Impact Analysis

### 🚀 Overview
This project is a **Quantitative Finance Dashboard** built to analyze the stock market's reaction to major corporate acquisitions. Using **Event Study Methodology**, it measures whether a "Deal" created immediate shareholder value or resulted in "Value Destruction."

The app pulls live market data from Yahoo Finance and benchmarks individual stock performance against the **S&P 500 Index** to isolate the true "Alpha" of the transaction.

---

### 📊 Key Financial Metrics
To provide professional-grade insights, the dashboard calculates:

* **Cumulative Return:** The total percentage growth of the stock from 30 days before to 90 days after the announcement.
* **Market Benchmark (S&P 500):** The baseline performance of the broader market during the same window.
* **Alpha (Excess Return):** The core metric. It represents the stock's performance **above or below** the market. 
    > $Alpha = R_{stock} - R_{market}$
* **Day 0 Marker:** A visual "Announcement Date" line to observe pre-deal "leakage" or post-deal volatility.

---

### 🛠️ Technical Stack
* **Language:** Python 3.11+
* **Framework:** Streamlit (UI & Deployment)
* **Data Source:** `yfinance` API (Live Market Data)
* **Visualization:** Plotly Graph Objects (Interactive Time-Series)
* **Environment:** Optimized for macOS M4 and Streamlit Cloud
