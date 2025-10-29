# TennisPredictorX — Demo (FOR + UTFP)

## Run (Windows)
1) python -m venv .venv
2) .\.venv\Scripts\activate
3) pip install -U -r requirements.txt
4) streamlit run app/streamlit_app.py

## Data Sources (ONE per run)
- Local CSV: data/sample_matches.csv
- Google Sheet (publish as CSV): paste the CSV URL in the UI

## Contract (UTFP-D1, Min-5)
Required (minimum): `date, tour, surface, player1, player2`
Optional (improves accuracy): `p1_rank, p2_rank, p1_elo, p2_elo, p1_h2h, p2_h2h, p1_form14, p2_form14, bestof, odds_p1, odds_p2`

Defaults if optional columns are missing:
- `p1_elo/p2_elo=1500`, `p1_h2h/p2_h2h=0`, `p1_form14/p2_form14=0.50`, `p1_rank/p2_rank=100`, `bestof=3`, `odds_p1/odds_p2` ignored if absent.

## Google Sheet Template (Daily-Lite)
1. أنشئ Google Sheet بالأعمدة أعلاه (حد أدنى الخمسة المطلوبة).
2. أدخل المباريات يوميًا (5–10 دقائق).
3. File → Share → Publish to web → **CSV**.
4. الصق رابط الـCSV في واجهة التطبيق.

## Files
- config/feature_weight.yaml — feature weights
- app/matchup_hybrid.py — hybrid model (Elo/H2H/Form + defaults)
- app/streamlit_app.py — UI with Source Selector + Filters + Histogram
- ops/Run-Demo.ps1 — launcher script (fixed .venv path)

## Freeze (FOR-F3)
Use this folder as the demo artifact. Do not change file names or schema.
