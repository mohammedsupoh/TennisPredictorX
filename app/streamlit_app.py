import streamlit as st
import pandas as pd
from pathlib import Path

# استيراد مرن يعمل سواء app باكدج or لا
try:
    from app.matchup_hybrid import validate_schema, compute_probs
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))  # .../app
    from matchup_hybrid import validate_schema, compute_probs

st.set_page_config(page_title="TennisPredictorX — Demo", layout="wide")
st.title("🎾 TennisPredictorX — Demo (FOR + UTFP)")
st.markdown("**Source Selector (ONE at a time):** Local CSV or Google Sheet (CSV).")

src = st.radio("Source Selector:", ["Local CSV (data/sample_matches.csv)", "Google Sheet (CSV URL)"], index=0, horizontal=True)

df = None
err = None

if src.startswith("Local"):
    csv_path = Path("data/sample_matches.csv")
    if not csv_path.exists():
        err = f"لم يتم العثور على {csv_path}"
    else:
        df = pd.read_csv(csv_path)
else:
    url = st.text_input("أدخل رابط Google Sheet (CSV):", value="", placeholder="https://docs.google.com/.../pub?output=csv")
    if url:
        try:
            df = pd.read_csv(url)
        except Exception as e:
            err = f"فشل تحميل Google Sheet: {e}"

if err:
    st.error(err)

if df is not None:
    ok, missing_req, warnings = validate_schema(df)
    if not ok:
        st.error(f"عقد البيانات غير مستوفى. أعمدة ناقصة: {missing_req}")
        st.dataframe(df.head(20), width="stretch")
        st.stop()

    if warnings:
        for w in warnings:
            st.warning(w)

    st.success("✅ Contract satisfied (Min-5, UTFP-D1)")
    st.caption(f"Matches count: {len(df)}")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        tours = ["All"] + sorted([str(x) for x in df["tour"].dropna().unique().tolist()]) if "tour" in df.columns else ["All"]
        tour_filter = st.selectbox("Tour:", tours)
    with col2:
        surfaces = ["All"] + sorted([str(x) for x in df["surface"].dropna().unique().tolist()]) if "surface" in df.columns else ["All"]
        surface_filter = st.selectbox("Surface:", surfaces)

    filtered = df.copy()
    if tour_filter != "All" and "tour" in filtered.columns:
        filtered = filtered[filtered["tour"].astype(str) == tour_filter]
    if surface_filter != "All" and "surface" in filtered.columns:
        filtered = filtered[filtered["surface"].astype(str) == surface_filter]

    st.dataframe(filtered.head(100), width="stretch")

    if st.button("Run Hybrid Scoring"):
        out = compute_probs(filtered)
        st.subheader("Prediction Results")

        # Histogram: confidence_band
        try:
            import plotly.express as px
            fig = px.histogram(out, x="confidence_band",
                               title="Confidence Distribution",
                               labels={"confidence_band": "Confidence Band (%)"})
            st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False})
        except Exception as e:
            st.info(f"Plotly غير متوفر: {e}")

        st.dataframe(out[[
            "date","tour","round","surface","player1","player2",
            "p1_prob","p2_prob","pred_winner","confidence_band"
        ]].head(200), width="stretch")

        st.download_button("⬇️ Download results CSV",
                           data=out.to_csv(index=False).encode("utf-8"),
                           file_name="predictions.csv",
                           mime="text/csv")





