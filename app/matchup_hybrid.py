import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from typing import Tuple, List

CFG = yaml.safe_load(Path("config/feature_weight.yaml").read_text(encoding="utf-8"))

# Required (min-5)
REQ_COLS = ["date","tour","surface","player1","player2"]

# Optional
OPT_COLS = [
    "p1_rank","p2_rank","p1_elo","p2_elo",
    "p1_h2h","p2_h2h","p1_form14","p2_form14",
    "bestof","odds_p1","odds_p2"
]

def _sigmoid(x):
    # متجهية بالكامل (NumPy)
    return 1.0 / (1.0 + np.exp(-x))

def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """Returns (ok, missing_required, warnings)"""
    missing_req = [c for c in REQ_COLS if c not in df.columns]
    missing_opt = [c for c in OPT_COLS if c not in df.columns]

    warnings = []
    if missing_opt:
        warnings.append(f"أعمدة اختيارية ناقصة: {missing_opt}")
        warnings.append("سيتم استخدام قيم افتراضية.")

    if "date" in df.columns:
        try:
            pd.to_datetime(df["date"], errors="raise")
        except Exception:
            warnings.append("تنسيق التاريخ غير صحيح (استخدم YYYY-MM-DD).")

    return (len(missing_req)==0, missing_req, warnings)

def compute_probs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Safe defaults
    out["p1_elo"]    = out.get("p1_elo",    1500)
    out["p2_elo"]    = out.get("p2_elo",    1500)
    out["p1_h2h"]    = out.get("p1_h2h",    0)
    out["p2_h2h"]    = out.get("p2_h2h",    0)
    out["p1_form14"] = out.get("p1_form14", 0.50)
    out["p2_form14"] = out.get("p2_form14", 0.50)
    out["p1_rank"]   = out.get("p1_rank",   100)
    out["p2_rank"]   = out.get("p2_rank",   100)
    out["bestof"]    = out.get("bestof",    3)

    # تأكد أن الأعمدة رقمية إن جاءت كنصوص
    for col in ["p1_elo","p2_elo","p1_h2h","p2_h2h","p1_form14","p2_form14","p1_rank","p2_rank"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(out[col].median() if pd.api.types.is_numeric_dtype(out[col]) else 0)

    w_elo = CFG.get("elo",0.55)
    w_h2h = CFG.get("h2h",0.20)
    w_form= CFG.get("form14",0.20)
    w_rank= CFG.get("rank",0.05)
    bias  = CFG.get("bias_floor",0.02)

    elo_delta  = (out["p1_elo"] - out["p2_elo"]) / 400.0
    denom      = out[["p1_h2h","p2_h2h"]].replace(0,1).max(axis=1).clip(lower=1)
    h2h_delta  = (out["p1_h2h"] - out["p2_h2h"]) / denom
    form_delta = (out["p1_form14"] - out["p2_form14"])
    rank_delta = (out["p2_rank"] - out["p1_rank"]) / 100.0  # lower rank is better

    logits = (w_elo*elo_delta) + (w_h2h*h2h_delta) + (w_form*form_delta) + (w_rank*rank_delta)
    p1_prob = _sigmoid(logits).clip(bias, 1-bias)
    p2_prob = 1 - p1_prob

    out["p1_prob"] = (p1_prob*100).round(1)
    out["p2_prob"] = (p2_prob*100).round(1)
    out["pred_winner"] = np.where(out["p1_prob"] >= 50.0, out["player1"], out["player2"])
    out["confidence_band"] = (abs(out["p1_prob"] - 50.0) * 2).round(1)  # 0..100

    return out

