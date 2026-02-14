import pandas as pd

STATUS_ORDER = {"CRITICO": 0, "LIMITE": 1, "OK": 2}

def compute_kpis(snapshot: pd.DataFrame) -> pd.DataFrame:
    df = snapshot.copy()

    # Cast seguro
    df["stock_on_hand"] = pd.to_numeric(df["stock_on_hand"], errors="coerce").fillna(0)
    df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce").fillna(0)
    df["daily_demand"] = pd.to_numeric(df["daily_demand"], errors="coerce").fillna(0).clip(lower=0.0001)
    df["lead_time_days"] = pd.to_numeric(df["lead_time_days"], errors="coerce").fillna(0)

    # KPIs
    df["days_of_cover"] = df["stock_on_hand"] / df["daily_demand"]
    df["reorder_point"] = df["daily_demand"] * df["lead_time_days"]

    # Estado semáforo para tablero
    def classify(row) -> str:
        stock = float(row["stock_on_hand"])
        min_stock = float(row["min_stock"])
        cover = float(row["days_of_cover"])
        lt = float(row["lead_time_days"])

        near_min = stock <= (min_stock * 1.10)  # 10% por encima del mínimo
        near_cover = cover < (lt * 1.5) if lt > 0 else False

        if stock < min_stock or (lt > 0 and cover < lt):
            return "CRITICO"
        if near_min or near_cover:
            return "LIMITE"
        return "OK"

    df["status"] = df.apply(classify, axis=1)
    df["status_rank"] = df["status"].map(STATUS_ORDER)

    # Score simple para ordenar “peor primero” (para ranking visual)
    # combina: gap vs mínimo + gap vs cobertura
    df["stock_gap"] = (df["min_stock"] - df["stock_on_hand"]).clip(lower=0)
    df["cover_gap"] = (df["lead_time_days"] - df["days_of_cover"]).clip(lower=0)
    df["risk_score"] = (df["stock_gap"] * 1.0) + (df["cover_gap"] * 10.0)

    return df
