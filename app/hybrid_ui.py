import io, os, sys
import pandas as pd
import streamlit as st

_USE_MPL = True
try:
    import matplotlib.pyplot as plt
except Exception:
    _USE_MPL = False
    import plotly.express as px

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_APP_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.matchup_hybrid import validate_schema, compute_probs

_DEF_NAMES = ("df_filtered","filtered_df","df","matches_df","matches","data","source_df","table_df")

def _pick_any_df_from_globals():
    for name, obj in globals().items():
        if isinstance(obj, pd.DataFrame) and not obj.empty:
            cols = {c.lower() for c in obj.columns}
            if {"player1","player2"}.issubset(cols) or {"p1","p2"}.issubset(cols):
                return obj
    for name, obj in globals().items():
        if isinstance(obj, pd.DataFrame) and not obj.empty:
            return obj
    return None

def _resolve_df(df_filtered: pd.DataFrame|None) -> pd.DataFrame:
    if isinstance(df_filtered, pd.DataFrame) and not df_filtered.empty:
        return df_filtered.copy()
    for nm in _DEF_NAMES:
        if nm in globals():
            v = globals()[nm]
            if isinstance(v, pd.DataFrame) and not v.empty:
                return v.copy()
    try:
        for nm in _DEF_NAMES:
            v = st.session_state.get(nm)
            if isinstance(v, pd.DataFrame) and not v.empty:
                return v.copy()
    except Exception:
        pass
    anydf = _pick_any_df_from_globals()
    if anydf is not None:
        return anydf.copy()
    raise NameError("No DataFrame available after filters. Please load/choose data first.")

def _validate(df: pd.DataFrame):
    try:
        return validate_schema(df, min_rows=5)
    except TypeError:
        return validate_schema(df)

def _show_histogram(out: pd.DataFrame):
    if _USE_MPL:
        fig = plt.figure()
        out["confidence_band"].plot.hist(bins=20)
        plt.title("Confidence Distribution")
        plt.xlabel("Confidence Band (%)")
        plt.ylabel("Count")
        st.pyplot(fig)
    else:
        fig = px.histogram(out, x="confidence_band", nbins=20, title="Confidence Distribution")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

def render_hybrid(df_filtered: pd.DataFrame | None = None):
    st.divider()
    if st.button("Run Hybrid Scoring", type="primary"):
        try:
            df = _resolve_df(df_filtered)
            ok, msg = _validate(df)
            if not ok:
                st.error(f"Schema error: {msg}")
                return
            out = compute_probs(df)
            st.success("Hybrid scoring completed.")
            st.subheader("Prediction Results")
            st.dataframe(out, use_container_width=True)
            _show_histogram(out)
            csv_bytes = out.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download results CSV", data=csv_bytes, file_name="hybrid_results.csv", mime="text/csv")
        except Exception as e:
            st.exception(e)
