# AI Financial Intelligence & Advisory System

An industry-style Streamlit fintech application that combines expense tracking, ML-based categorization, anomaly detection, forecasting, advisor-style insights, and investment suggestions in one authenticated workspace.

## Features

- Secure signup and login with SQLite-backed users and hashed passwords
- CSV upload and manual transaction entry
- Automatic category prediction when category data is missing
- Financial dashboard with metric cards and interactive Plotly charts
- AI insights for overspending, savings discipline, and budget pressure
- Next-month expense forecasting
- Financial Health Score from 0 to 100
- Fraud and anomaly detection using Isolation Forest
- Investment recommendations based on savings capacity
- Built-in chatbot for quick financial questions

## Project Structure

```text
ai-finance-analyzer/
├── app/
├── data/
├── database/
├── ml_models/
├── tests/
├── utils/
├── requirements.txt
└── run.py
```

## Setup

```powershell
cd "c:\Users\Himanshu Sharma\OneDrive\Desktop\project final\ai-finance-analyzer"
pip install -r requirements.txt
python run.py
```

Or run directly:

```powershell
python -m streamlit run app/main.py
```

## CSV Format

Required columns:

- `Date`
- `Description`
- `Amount`

Optional column:

- `Category`

If `Category` is missing, the system predicts it using the trained classifier.

## Testing

```powershell
pytest
```

## Future Improvements

- Bank API integrations
- Multi-user budgeting goals and alerts
- Role-based admin analytics
- Portfolio risk profiling
- LLM-backed conversational advisor
