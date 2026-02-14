import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from metrics import compute_kpis

DATA_PATH = "data/sample_inventory.csv"
OUT_DIR = "outputs"

# Colores pedidos (se pueden ajustar)
COLORS = {
    "CRITICO": "#D32F2F",  # rojo
    "LIMITE":  "#FBC02D",  # amarillo
    "OK":      "#388E3C",  # verde
}

def load_latest_snapshot(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "sku"])

    last_date = df["date"].max()
    snap = df[df["date"] == last_date].copy()

    required = ["sku", "description", "stock_on_hand", "min_stock", "daily_demand", "lead_time_days"]
    for c in required:
        if c not in snap.columns:
            raise ValueError(f"Falta la columna requerida: {c}")

    snap = compute_kpis(snap)
    # orden: estado peor primero + score
    snap = snap.sort_values(["status_rank", "risk_score"], ascending=[True, False])
    return snap


def export_outputs(snap: pd.DataFrame) -> None:
    snap.to_csv(os.path.join(OUT_DIR, "kpi_summary.csv"), index=False)
    snap[snap["status"].isin(["CRITICO", "LIMITE"])].to_csv(os.path.join(OUT_DIR, "risk_items.csv"), index=False)


def chart_stock_semaphore(snap: pd.DataFrame, top_n: int = 15) -> str:
    """
    Imagen 1: Barras coloreadas por estado + línea de stock mínimo + etiquetas.
    """
    tmp = snap.head(top_n).copy().reset_index(drop=True)

    fig = plt.figure(figsize=(12, 6))
    bar_colors = [COLORS[s] for s in tmp["status"]]
    plt.bar(tmp["sku"], tmp["stock_on_hand"], label="Stock", color=bar_colors)
    plt.plot(tmp["sku"], tmp["min_stock"], marker="o", linestyle="--", label="Stock mínimo")

    # Etiquetas de estado arriba de cada barra
    for i, row in tmp.iterrows():
        plt.text(i, float(row["stock_on_hand"]), row["status"], ha="center", va="bottom", rotation=90, fontsize=9)

    plt.xticks(rotation=55, ha="right")
    plt.title("Inventarios: Stock vs Mínimo (Semáforo para monitoreo)")
    plt.xlabel("SKU")
    plt.ylabel("Unidades")
    plt.legend()
    plt.tight_layout()

    out = os.path.join(OUT_DIR, "01_stock_semaforo.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def dashboard_kpi_cards_and_ranking(snap: pd.DataFrame, top_n: int = 12) -> str:
    """
    Imagen 2: Tablero gerencial (cards KPI + ranking visual con filas coloreadas).
    Ajustado para evitar superposición en las tarjetas.
    """
    total = len(snap)
    crit = int((snap["status"] == "CRITICO").sum())
    lim = int((snap["status"] == "LIMITE").sum())
    ok  = int((snap["status"] == "OK").sum())
    risk_pct = ((crit + lim) / total * 100.0) if total else 0.0

    tmp = snap.head(top_n).copy().reset_index(drop=True)

    fig = plt.figure(figsize=(12, 7))
    ax = plt.gca()
    ax.set_axis_off()

    # --- Header
    ax.text(0.02, 0.95, "Operational Risk Dashboard (Inventory Monitoring)",
            fontsize=16, weight="bold", transform=ax.transAxes)
    ax.text(0.02, 0.91, "Semáforo de riesgo + KPIs para toma de decisiones",
            fontsize=11, transform=ax.transAxes)

    # --- KPI Cards (más altas + posiciones seguras)
    def card(x, y, w, h, title, value, color_hex):
        # Fondo suave + borde
        ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes,
                               facecolor=color_hex, edgecolor="none", alpha=0.16, zorder=1))
        ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes,
                               fill=False, edgecolor=color_hex, linewidth=1.4, zorder=2))

        pad_x = 0.02
        # Título arriba (anclado arriba)
        ax.text(x + pad_x, y + h - 0.02, title,
                fontsize=10.5, weight="bold", va="top", transform=ax.transAxes, zorder=3)

        # Valor abajo (anclado abajo) -> evita superposición
        ax.text(x + pad_x, y + 0.02, value,
                fontsize=22, weight="bold", va="bottom", transform=ax.transAxes, zorder=3)

    # Cards: un poco más altas que antes
    h = 0.12
    y_cards = 0.76

    card(0.02, y_cards, 0.23, h, "CRÍTICOS", f"{crit}", COLORS["CRITICO"])
    card(0.27, y_cards, 0.23, h, "EN LÍMITE", f"{lim}", COLORS["LIMITE"])
    card(0.52, y_cards, 0.23, h, "OK", f"{ok}", COLORS["OK"])
    card(0.77, y_cards, 0.21, h, "% EN RIESGO", f"{risk_pct:.0f}%",
         COLORS["CRITICO"] if risk_pct >= 30 else COLORS["LIMITE"])

    # --- Ranking Title
    ax.text(0.02, 0.69, f"Top {top_n} SKUs para monitoreo (prioridad por riesgo)",
            fontsize=12, weight="bold", transform=ax.transAxes)

    # --- Ranking rows (tarjetas horizontales)
    start_y = 0.64
    row_h = 0.045
    x0 = 0.02
    w = 0.96

    # Column headers
    ax.text(x0,           start_y + 0.02, "SKU", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.text(x0 + 0.16,    start_y + 0.02, "Estado", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.text(x0 + 0.30,    start_y + 0.02, "Stock", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.text(x0 + 0.40,    start_y + 0.02, "Mínimo", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.text(x0 + 0.52,    start_y + 0.02, "Cobertura (días)", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.text(x0 + 0.72,    start_y + 0.02, "Lead Time", fontsize=10, weight="bold", transform=ax.transAxes)

    y = start_y - 0.01
    for _, row in tmp.iterrows():
        y -= row_h
        status = row["status"]
        c = COLORS[status]

        ax.add_patch(Rectangle((x0, y), w, row_h, transform=ax.transAxes,
                               facecolor=c, alpha=0.14, edgecolor=c, linewidth=0.8))

        ax.text(x0,        y + 0.012, str(row["sku"]), fontsize=10, transform=ax.transAxes)
        ax.text(x0 + 0.16, y + 0.012, status, fontsize=10, weight="bold", transform=ax.transAxes)
        ax.text(x0 + 0.30, y + 0.012, f"{float(row['stock_on_hand']):.0f}", fontsize=10, transform=ax.transAxes)
        ax.text(x0 + 0.40, y + 0.012, f"{float(row['min_stock']):.0f}", fontsize=10, transform=ax.transAxes)
        ax.text(x0 + 0.52, y + 0.012, f"{float(row['days_of_cover']):.1f}", fontsize=10, transform=ax.transAxes)
        ax.text(x0 + 0.72, y + 0.012, f"{float(row['lead_time_days']):.0f}", fontsize=10, transform=ax.transAxes)

    # Footer note
    ax.text(0.02, 0.04,
            "Reglas: CRÍTICO si Stock<Mínimo o Cobertura<Lead Time | LÍMITE si cerca del mínimo o cobertura < LT×1.5",
            fontsize=9, transform=ax.transAxes)

    out = os.path.join(OUT_DIR, "02_dashboard_cards_ranking.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out



def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    snap = load_latest_snapshot(DATA_PATH)
    export_outputs(snap)

    img1 = chart_stock_semaphore(snap, top_n=15)
    img2 = dashboard_kpi_cards_and_ranking(snap, top_n=12)

    print("OK ✅ Imágenes generadas para LinkedIn:")
    print(" -", img1)
    print(" -", img2)
    print("Exportables:")
    print(" - outputs/kpi_summary.csv")
    print(" - outputs/risk_items.csv")


if __name__ == "__main__":
    main()
