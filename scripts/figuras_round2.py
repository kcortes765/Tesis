"""
figuras_round2.py — Figuras autocontenidas del analisis Round 2.
Cada figura cuenta una historia completa sin necesidad de leer el reporte.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import spearmanr

PROJECT = Path(__file__).resolve().parent.parent
PROC = PROJECT / "data" / "processed"
FIG_DIR = PROJECT / "data" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SENTINEL_THRESHOLD = -3.0e38

# --- Cargar datos ---
params = pd.read_csv(PROJECT / "config" / "screening_round2.csv")
results = pd.read_csv(PROJECT / "data" / "results" / "results_round2.csv")
df = params.merge(results, on="case_id", suffixes=("", "_dup"))
# Limpiar columnas duplicadas del merge
dup_cols = [c for c in df.columns if c.endswith("_dup")]
df = df.drop(columns=dup_cols)
# Asegurar que slope_inv existe
if "slope_inv" not in df.columns and "slope_inv_x" in df.columns:
    df["slope_inv"] = df["slope_inv_x"]


def load_exchange(case_id):
    d = PROC / case_id / f"{case_id}_out"
    if not d.exists():
        d = PROC / case_id
    f = list(d.glob("ChronoExchange_mkbound_*.csv"))
    if not f:
        return None
    ex = pd.read_csv(f[0], sep=";")
    rename = {
        "time [s]": "time",
        "fvel.x [m/s]": "vx", "fvel.y [m/s]": "vy", "fvel.z [m/s]": "vz",
        "fcenter.x [m]": "cx", "fcenter.y [m]": "cy", "fcenter.z [m]": "cz",
    }
    ex = ex.rename(columns=rename)
    ex["vxy"] = np.sqrt(ex["vx"]**2 + ex["vy"]**2)
    cx0, cy0, cz0 = ex["cx"].iloc[0], ex["cy"].iloc[0], ex["cz"].iloc[0]
    ex["disp"] = np.sqrt((ex["cx"]-cx0)**2 + (ex["cy"]-cy0)**2 + (ex["cz"]-cz0)**2) * 1000
    return ex


def load_gauge_vel(case_id, gauge_num):
    d = PROC / case_id / f"{case_id}_out"
    if not d.exists():
        d = PROC / case_id
    f = d / f"GaugesVel_V{gauge_num:02d}.csv"
    if not f.exists():
        return None
    g = pd.read_csv(f, sep=";")
    rename = {"time [s]": "time", "velx [m/s]": "velx", "vely [m/s]": "vely", "velz [m/s]": "velz"}
    g = g.rename(columns=rename)
    for c in ["velx", "vely", "velz"]:
        if c in g.columns:
            g.loc[g[c] < SENTINEL_THRESHOLD, c] = np.nan
    return g


# Precargar exchanges
exchanges = {}
for _, row in df.iterrows():
    cid = row["case_id"]
    exchanges[cid] = load_exchange(cid)

print("Datos cargados. Generando figuras...")

# =====================================================================
# FIGURA 1: Dashboard completo Round 2 (la figura principal)
# =====================================================================
fig = plt.figure(figsize=(22, 16))
fig.suptitle("Screening Round 2 — Dashboard Completo (15 casos, dp=0.004)",
             fontsize=16, fontweight="bold", y=0.98)
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

colors_estado = {"ESTABLE": "#27ae60", "UMBRAL": "#f39c12", "FALLO": "#e74c3c"}

# 1a: dam_h vs disp (log), size=mass, color=estado
ax = fig.add_subplot(gs[0, 0])
for estado, color in colors_estado.items():
    mask = df["estado"] == estado
    if mask.any():
        ax.scatter(df.loc[mask, "dam_height"], df.loc[mask, "max_disp_mm"],
                   c=color, s=df.loc[mask, "boulder_mass"]*80, label=estado,
                   edgecolors="k", linewidths=0.5, zorder=3, alpha=0.85)
ax.axhline(5, color="gray", ls="--", lw=0.8, alpha=0.6)
ax.axhline(10, color="gray", ls=":", lw=0.8, alpha=0.6)
ax.set_yscale("log")
ax.set_xlabel("dam_height [m]")
ax.set_ylabel("max displacement [mm] (log)")
ax.set_title("dam_h vs Desplazamiento\n(tamano = masa)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 1b: friction vs disp (log)
ax = fig.add_subplot(gs[0, 1])
for estado, color in colors_estado.items():
    mask = df["estado"] == estado
    if mask.any():
        ax.scatter(df.loc[mask, "friction_coefficient"], df.loc[mask, "max_disp_mm"],
                   c=color, s=80, edgecolors="k", linewidths=0.5, zorder=3, alpha=0.85)
        for _, r in df.loc[mask].iterrows():
            ax.annotate(r["case_id"].replace("sc2_", ""), (r["friction_coefficient"], r["max_disp_mm"]),
                        fontsize=6, ha="center", va="bottom", xytext=(0, 4), textcoords="offset points")
ax.axhline(5, color="gray", ls="--", lw=0.8, alpha=0.6)
ax.set_yscale("log")
ax.set_xlabel("friction coefficient")
ax.set_ylabel("max displacement [mm] (log)")
ax.set_title("Friccion vs Desplazamiento\n(rho=-0.916, p<0.001)")
ax.grid(True, alpha=0.2)

# 1c: Spearman barchart
ax = fig.add_subplot(gs[0, 2])
vars_in = ["dam_height", "boulder_mass", "boulder_rot_z", "friction_coefficient", "slope_inv"]
labels = ["dam_h", "mass", "rot_z", "friction", "slope"]
rhos, pvals = [], []
for v in vars_in:
    r, p = spearmanr(df[v], df["max_disp_mm"])
    rhos.append(r)
    pvals.append(p)
bar_colors = ["#e74c3c" if p < 0.05 else "#bdc3c7" for p in pvals]
bars = ax.barh(labels, rhos, color=bar_colors, edgecolor="k", linewidth=0.5)
ax.axvline(0, color="k", lw=0.5)
for i, (r, p) in enumerate(zip(rhos, pvals)):
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    ax.text(r + (0.03 if r >= 0 else -0.03), i, f"  {r:+.2f} {sig}",
            va="center", ha="left" if r >= 0 else "right", fontsize=9)
ax.set_xlabel("Spearman rho")
ax.set_title("Correlaciones con desplazamiento\n(rojo = p<0.05)")
ax.set_xlim(-1.1, 1.1)

# 2a: Series temporales ESTABLE
ax = fig.add_subplot(gs[1, 0])
estables = df[df["estado"] == "ESTABLE"]["case_id"].tolist()
for cid in estables:
    ex = exchanges[cid]
    if ex is not None:
        ax.plot(ex["time"], ex["disp"], label=cid.replace("sc2_", ""), linewidth=1)
ax.axhline(5, color="gray", ls="--", lw=0.8, alpha=0.6, label="umbral 5mm")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento [mm]")
ax.set_title("Casos ESTABLE: serie temporal")
ax.legend(fontsize=7, ncol=2)
ax.set_ylim(-0.2, 8)
ax.grid(True, alpha=0.2)

# 2b: Series temporales FALLO
ax = fig.add_subplot(gs[1, 1])
fallos = df[df["estado"] == "FALLO"].sort_values("max_disp_mm")["case_id"].tolist()
cmap = plt.cm.Reds(np.linspace(0.3, 1.0, len(fallos)))
for i, cid in enumerate(fallos):
    ex = exchanges[cid]
    if ex is not None:
        ax.plot(ex["time"], ex["disp"], label=cid.replace("sc2_", ""),
                linewidth=1, color=cmap[i])
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento [mm]")
ax.set_title("Casos FALLO: serie temporal")
ax.legend(fontsize=6, ncol=2, loc="upper left")
ax.grid(True, alpha=0.2)

# 2c: Velocidad horizontal todos
ax = fig.add_subplot(gs[1, 2])
for cid in estables:
    ex = exchanges[cid]
    if ex is not None:
        ax.plot(ex["time"], ex["vxy"], color="#27ae60", alpha=0.4, linewidth=0.8)
for i, cid in enumerate(fallos):
    ex = exchanges[cid]
    if ex is not None:
        ax.plot(ex["time"], ex["vxy"], color=cmap[i], alpha=0.7, linewidth=0.8)
ax.axhline(0.01, color="gray", ls=":", lw=0.8, alpha=0.6, label="v=0.01 m/s")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Velocidad horizontal [m/s]")
ax.set_title("Velocidad del boulder (verde=estable, rojo=fallo)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 3a: Variables aisladas - friction
ax = fig.add_subplot(gs[2, 0])
pairs = [
    ("sc2_012", "sc2_013", "friction", [0.1, 0.8]),
]
x = [0, 1]
vals = [df[df["case_id"]=="sc2_012"]["max_disp_mm"].values[0],
        df[df["case_id"]=="sc2_013"]["max_disp_mm"].values[0]]
bars = ax.bar(x, vals, color=["#e74c3c", "#27ae60"], edgecolor="k", width=0.6)
ax.set_xticks(x)
ax.set_xticklabels(["sc2_012\nmu=0.1", "sc2_013\nmu=0.8"])
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 30, f"{v:.0f}mm",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_ylabel("max displacement [mm]")
ax.set_title("Efecto Friccion (aislado)\ndam_h=0.20, mass=1.0, slope=1:20\n1763x diferencia")

# 3b: Variables aisladas - slope
ax = fig.add_subplot(gs[2, 1])
vals = [df[df["case_id"]=="sc2_010"]["max_disp_mm"].values[0],
        df[df["case_id"]=="sc2_011"]["max_disp_mm"].values[0]]
bars = ax.bar(x, vals, color=["#3498db", "#e67e22"], edgecolor="k", width=0.6)
ax.set_xticks(x)
ax.set_xticklabels(["sc2_010\nslope 1:5", "sc2_011\nslope 1:30"])
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 15, f"{v:.0f}mm",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_ylabel("max displacement [mm]")
ax.set_title("Efecto Pendiente (aislado)\ndam_h=0.20, mass=1.0, fric=0.3\n8.5x diferencia")

# 3c: Caso sorpresa sc2_007 vs sc2_008
ax = fig.add_subplot(gs[2, 2])
ex7 = exchanges["sc2_007"]
ex8 = exchanges["sc2_008"]
ax.plot(ex7["time"], ex7["disp"], color="#e74c3c", linewidth=1.5,
        label="sc2_007: dh=0.12, m=0.8, mu=0.1")
ax.plot(ex8["time"], ex8["disp"], color="#27ae60", linewidth=1.5,
        label="sc2_008: dh=0.10, m=1.6, mu=0.8")
ax.axhline(5, color="gray", ls="--", lw=0.8, alpha=0.6)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento [mm]")
ax.set_title("Caso sorpresa: dam_h bajo NO garantiza estabilidad\nbaja masa + baja friccion = FALLO")
ax.legend(fontsize=7, loc="upper left")
ax.grid(True, alpha=0.2)

fig.savefig(str(FIG_DIR / "r2_dashboard_completo.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("  [1/5] r2_dashboard_completo.png")


# =====================================================================
# FIGURA 2: Mapa de calor parametros vs resultado
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Round 2: Mapa Parametrico (cada fila = un caso, ordenado por desplazamiento)",
             fontsize=13, fontweight="bold")

df_sorted = df.sort_values("max_disp_mm")

# Panel izquierdo: parametros de entrada (normalizados 0-1)
ax = axes[0]
input_cols = ["dam_height", "boulder_mass", "friction_coefficient", "boulder_rot_z", "slope_inv"]
input_labels = ["dam_h", "mass", "friction", "rot_z", "slope_inv"]
input_data = df_sorted[input_cols].copy()
for c in input_cols:
    mn, mx = input_data[c].min(), input_data[c].max()
    if mx > mn:
        input_data[c] = (input_data[c] - mn) / (mx - mn)
    else:
        input_data[c] = 0.5

im = ax.imshow(input_data.values, cmap="viridis", aspect="auto", vmin=0, vmax=1)
ax.set_yticks(range(len(df_sorted)))
ax.set_yticklabels([f"{r['case_id']} ({r['estado']})" for _, r in df_sorted.iterrows()], fontsize=8)
ax.set_xticks(range(len(input_labels)))
ax.set_xticklabels(input_labels, fontsize=9)
ax.set_title("Parametros de entrada (normalizados)")
# Anotar valores reales
for i, (_, row) in enumerate(df_sorted.iterrows()):
    for j, c in enumerate(input_cols):
        ax.text(j, i, f"{row[c]:.2f}", ha="center", va="center", fontsize=7,
                color="white" if input_data.iloc[i, j] < 0.5 else "black")
fig.colorbar(im, ax=ax, shrink=0.6, label="Normalizado [0-1]")

# Panel derecho: resultados
ax = axes[1]
out_cols = ["max_disp_mm", "max_rot_deg", "max_vel_mps", "flow_vel_mps", "water_h_m"]
out_labels = ["disp [mm]", "rot [deg]", "vel boulder", "vel flujo", "water_h"]
out_data = df_sorted[out_cols].copy()
# Log-normalizar desplazamiento para visualizacion
out_norm = out_data.copy()
for c in out_cols:
    mn, mx = out_norm[c].min(), out_norm[c].max()
    if mx > mn:
        out_norm[c] = (out_norm[c] - mn) / (mx - mn)
    else:
        out_norm[c] = 0.5

im2 = ax.imshow(out_norm.values, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=1)
ax.set_yticks(range(len(df_sorted)))
ax.set_yticklabels([f"{r['max_disp_mm']:.0f}mm" for _, r in df_sorted.iterrows()], fontsize=8)
ax.set_xticks(range(len(out_labels)))
ax.set_xticklabels(out_labels, fontsize=9)
ax.set_title("Variables de respuesta (normalizadas)")
for i, (_, row) in enumerate(df_sorted.iterrows()):
    for j, c in enumerate(out_cols):
        val = row[c]
        txt = f"{val:.0f}" if val > 10 else f"{val:.2f}"
        ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                color="white" if out_norm.iloc[i, j] > 0.5 else "black")
fig.colorbar(im2, ax=ax, shrink=0.6, label="Normalizado [0-1]")

fig.savefig(str(FIG_DIR / "r2_mapa_parametrico.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("  [2/5] r2_mapa_parametrico.png")


# =====================================================================
# FIGURA 3: Investigacion sc2_010 + comparacion slopes
# =====================================================================
fig = plt.figure(figsize=(18, 10))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
fig.suptitle("Investigacion sc2_010 (slope=1:5) — water_h=0.0 explicado",
             fontsize=14, fontweight="bold")

# 3a: Perfil del canal con gauges
ax = fig.add_subplot(gs[0, :2])
# Canal slope 1:5
x_canal = np.array([0, 5, 15])
z_canal = np.array([0, 0, 2.0])  # 1:5 desde x=5
ax.fill_between(x_canal, z_canal, -0.5, color="#d4a574", alpha=0.3, label="Playa slope 1:5")
ax.plot(x_canal, z_canal, "k-", linewidth=2)
# Dam
ax.fill_between([0, 1], [0.20, 0.20], [0, 0], color="#3498db", alpha=0.3, label="Dam (h=0.20m)")
# Boulder
ax.plot(6.48, 0.119, "s", color="#e67e22", markersize=12, markeredgecolor="k", label="Boulder", zorder=5)

# Gauges vel con color segun si detectaron
gauge_data = [
    (0.25, 0.004, True, "V01"), (1.50, 0.004, True, "V02"),
    (2.50, 0.004, True, "V03"), (3.00, 0.004, True, "V04"),
    (6.41, 0.087, True, "V05"), (6.48, 0.119, False, "V06"),
    (6.59, 0.122, True, "V07"), (8.75, 0.554, False, "V08"),
    (9.50, 0.704, False, "V11"), (12.0, 1.204, False, "V12"),
]
for gx, gz, wet, name in gauge_data:
    color = "#27ae60" if wet else "#e74c3c"
    marker = "v" if wet else "x"
    ax.plot(gx, gz, marker, color=color, markersize=8, markeredgecolor=color, zorder=4)
    ax.annotate(name, (gx, gz), fontsize=6, ha="center", va="bottom",
                xytext=(0, 6), textcoords="offset points")

# Gauges hmax
hmax_data = [
    (0.25, 0.050, True), (3.00, 0.050, True), (5.25, 0.050, True),
    (7.50, 0.350, False), (8.25, 0.500, False), (8.75, 0.600, False),
    (9.50, 0.750, False), (12.0, 1.250, False),
]
for gx, gz, wet in hmax_data:
    color = "#27ae60" if wet else "#e74c3c"
    ax.plot(gx, gz, "^" if wet else "x", color=color, markersize=7, zorder=4)

ax.set_xlabel("x [m]")
ax.set_ylabel("z [m]")
ax.set_title("Perfil del canal slope=1:5 con posicion de gauges\n(verde=detecta agua, rojo=seco)")
ax.legend(fontsize=8, loc="upper left")
ax.set_xlim(-0.5, 13)
ax.set_ylim(-0.1, 2.0)
ax.grid(True, alpha=0.2)

# 3b: Gauges velocidad que si detectaron
ax = fig.add_subplot(gs[0, 2])
for gnum in [1, 2, 3, 4, 5]:
    g = load_gauge_vel("sc2_010", gnum)
    if g is not None:
        ax.plot(g["time"], g["velx"], label=f"V{gnum:02d}", linewidth=0.8)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("velx [m/s]")
ax.set_title("sc2_010: velocidad en gauges activos")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 3c: Comparacion slopes - desplazamiento
ax = fig.add_subplot(gs[1, 0])
ex10 = exchanges["sc2_010"]
ex11 = exchanges["sc2_011"]
ax.plot(ex10["time"], ex10["disp"], color="#3498db", linewidth=1.5, label="sc2_010 (1:5)")
ax.plot(ex11["time"], ex11["disp"], color="#e67e22", linewidth=1.5, label="sc2_011 (1:30)")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento [mm]")
ax.set_title("Efecto pendiente: 1:5 vs 1:30\n(dam_h=0.20, mass=1.0, fric=0.3)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 3d: Comparacion slopes - velocidad
ax = fig.add_subplot(gs[1, 1])
ax.plot(ex10["time"], ex10["vxy"], color="#3498db", linewidth=1.5, label="sc2_010 (1:5)")
ax.plot(ex11["time"], ex11["vxy"], color="#e67e22", linewidth=1.5, label="sc2_011 (1:30)")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Velocidad horizontal [m/s]")
ax.set_title("Velocidad del boulder")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 3e: Explicacion texto
ax = fig.add_subplot(gs[1, 2])
ax.axis("off")
txt = (
    "EXPLICACION\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "water_h = 0.0 para sc2_010 es un\n"
    "ARTEFACTO de gauges, no ausencia\n"
    "de agua.\n\n"
    "Con slope 1:5, los gauges hmax04-08\n"
    "estan a z >= 0.35m, MUY por encima\n"
    "del nivel del agua (dam_h=0.20m).\n\n"
    "Los gauges aguas arriba (V01-V05,\n"
    "hmax01-03) SI detectan flujo.\n\n"
    "El boulder se movio 133.5mm — hay\n"
    "impacto real, solo que los gauges\n"
    "seleccionados para el reporte\n"
    "estaban en zona seca.\n\n"
    "SOLUCION: para produccion con\n"
    "slopes extremos, usar gauges a\n"
    "altura adaptada al perfil."
)
ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=9,
        verticalalignment="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff9e6", edgecolor="#e6b800"))

fig.savefig(str(FIG_DIR / "r2_investigacion_sc2_010.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("  [3/5] r2_investigacion_sc2_010.png")


# =====================================================================
# FIGURA 4: Replicacion sc_008 vs sc2_015
# =====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Verificacion de Replicacion: sc_008 (R1, dp=0.005) vs sc2_015 (R2, dp=0.004)\n"
             "Parametros identicos: dam_h=0.145, mass=0.949, rot_z=56.6, fric=0.564, slope=1:28",
             fontsize=12, fontweight="bold")

ex_r1 = load_exchange("sc_008")
ex_r2 = exchanges["sc2_015"]

if ex_r1 is not None and ex_r2 is not None:
    # Desplazamiento
    ax = axes[0, 0]
    ax.plot(ex_r1["time"], ex_r1["disp"], color="#3498db", linewidth=1.5, label="sc_008 (dp=0.005)")
    ax.plot(ex_r2["time"], ex_r2["disp"], color="#e74c3c", linewidth=1.5, ls="--", label="sc2_015 (dp=0.004)")
    ax.set_ylabel("Desplazamiento [mm]")
    ax.set_title("Desplazamiento 3D")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

    # Velocidad
    ax = axes[0, 1]
    ax.plot(ex_r1["time"], ex_r1["vxy"], color="#3498db", linewidth=1, label="sc_008")
    ax.plot(ex_r2["time"], ex_r2["vxy"], color="#e74c3c", linewidth=1, ls="--", label="sc2_015")
    ax.set_ylabel("Velocidad horizontal [m/s]")
    ax.set_title("Velocidad del boulder")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

    # Posicion X
    ax = axes[1, 0]
    ax.plot(ex_r1["time"], ex_r1["cx"], color="#3498db", linewidth=1.5, label="sc_008")
    ax.plot(ex_r2["time"], ex_r2["cx"], color="#e74c3c", linewidth=1.5, ls="--", label="sc2_015")
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("fcenter.x [m]")
    ax.set_title("Posicion X del centro de masa")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

    # Posicion Z
    ax = axes[1, 1]
    ax.plot(ex_r1["time"], ex_r1["cz"], color="#3498db", linewidth=1.5, label="sc_008")
    ax.plot(ex_r2["time"], ex_r2["cz"], color="#e74c3c", linewidth=1.5, ls="--", label="sc2_015")
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("fcenter.z [m]")
    ax.set_title("Posicion Z (vertical)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

    # Anotar diferencia
    d1 = ex_r1["disp"].max()
    d2 = ex_r2["disp"].max()
    axes[0, 0].annotate(
        f"R1: {d1:.2f}mm\nR2: {d2:.2f}mm\nDiff: {abs(d1-d2):.2f}mm ({abs(d1-d2)/d1*100:.0f}%)",
        xy=(0.98, 0.98), xycoords="axes fraction", ha="right", va="top",
        fontsize=9, bbox=dict(boxstyle="round", facecolor="#eaf2f8", edgecolor="#2980b9"))

fig.savefig(str(FIG_DIR / "r2_replicacion_detalle.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("  [4/5] r2_replicacion_detalle.png")


# =====================================================================
# FIGURA 5: R1 vs R2 combinado + frontera multidimensional
# =====================================================================
fig = plt.figure(figsize=(18, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
fig.suptitle("Round 1 (dp=0.005) vs Round 2 (dp=0.004) — Vision Combinada",
             fontsize=14, fontweight="bold")

# Cargar R1
r1_csv = PROJECT / "data" / "results" / "results_round2.csv"  # R2
# Intentar cargar R1 desde SQLite
import sqlite3
db = PROJECT / "data" / "results.sqlite"
r1_data = None
if db.exists():
    conn = sqlite3.connect(str(db))
    try:
        all_data = pd.read_sql("SELECT * FROM results", conn)
        r1_data = all_data[all_data["case_name"].str.startswith("sc_")].copy()
        if len(r1_data) == 0:
            r1_data = None
    except:
        pass
    conn.close()

# Cargar R1 desde el screening report si SQLite no tiene
if r1_data is None:
    # Cargar R1 de los exchanges directamente
    r1_params = pd.read_csv(PROJECT / "config" / "screening_5d.csv")
    r1_rows = []
    for _, row in r1_params.iterrows():
        cid = row["case_id"]
        ex = load_exchange(cid)
        if ex is not None:
            disp_mm = ex["disp"].max()
            r1_rows.append({
                "case_id": cid,
                "dam_h": row["dam_height"],
                "mass": row["boulder_mass"],
                "friction": row.get("friction_coefficient", 0.3),
                "rot_z": row.get("boulder_rot_z", 0),
                "slope_inv": row.get("slope_inv", 20),
                "disp_mm": disp_mm,
                "round": "R1",
            })
    r1_df = pd.DataFrame(r1_rows) if r1_rows else pd.DataFrame()
else:
    r1_df = r1_data.rename(columns={
        "case_name": "case_id", "dam_height": "dam_h",
        "boulder_mass": "mass", "friction_coefficient": "friction",
        "boulder_rot_z": "rot_z",
    })
    r1_df["disp_mm"] = r1_df["max_displacement"] * 1000
    r1_df["round"] = "R1"

r2_cols = {"dam_height": "dam_h", "boulder_mass": "mass",
           "friction_coefficient": "friction", "boulder_rot_z": "rot_z"}
r2_rename = {k: v for k, v in r2_cols.items() if k in df.columns and v not in df.columns}
r2_df = df.rename(columns=r2_rename).copy()
if "dam_h" not in r2_df.columns and "dam_height" in r2_df.columns:
    r2_df["dam_h"] = r2_df["dam_height"]
if "mass" not in r2_df.columns and "boulder_mass" in r2_df.columns:
    r2_df["mass"] = r2_df["boulder_mass"]
if "friction" not in r2_df.columns and "friction_coefficient" in r2_df.columns:
    r2_df["friction"] = r2_df["friction_coefficient"]
if "rot_z" not in r2_df.columns and "boulder_rot_z" in r2_df.columns:
    r2_df["rot_z"] = r2_df["boulder_rot_z"]
r2_df["disp_mm"] = r2_df["max_disp_mm"]
r2_df["round"] = "R2"

# 5a: dam_h vs disp ambos rounds
ax = fig.add_subplot(gs[0, 0])
if len(r1_df) > 0:
    ax.scatter(r1_df["dam_h"], r1_df["disp_mm"], c="#3498db", s=40, marker="o",
               alpha=0.6, edgecolors="k", linewidths=0.3, label="R1 (dp=0.005)")
ax.scatter(r2_df["dam_h"], r2_df["disp_mm"], c="#e74c3c", s=60, marker="^",
           alpha=0.8, edgecolors="k", linewidths=0.3, label="R2 (dp=0.004)")
ax.axhline(5, color="gray", ls="--", lw=0.8, alpha=0.6)
ax.set_yscale("log")
ax.set_xlabel("dam_height [m]")
ax.set_ylabel("max displacement [mm] (log)")
ax.set_title("dam_h vs Desplazamiento")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 5b: mass vs disp
ax = fig.add_subplot(gs[0, 1])
if len(r1_df) > 0:
    ax.scatter(r1_df["mass"], r1_df["disp_mm"], c="#3498db", s=40, marker="o",
               alpha=0.6, edgecolors="k", linewidths=0.3, label="R1")
ax.scatter(r2_df["mass"], r2_df["disp_mm"], c="#e74c3c", s=60, marker="^",
           alpha=0.8, edgecolors="k", linewidths=0.3, label="R2")
ax.set_yscale("log")
ax.set_xlabel("boulder_mass [kg]")
ax.set_ylabel("max displacement [mm] (log)")
ax.set_title("Masa vs Desplazamiento")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 5c: friction vs disp
ax = fig.add_subplot(gs[0, 2])
if len(r1_df) > 0 and "friction" in r1_df.columns:
    ax.scatter(r1_df["friction"], r1_df["disp_mm"], c="#3498db", s=40, marker="o",
               alpha=0.6, edgecolors="k", linewidths=0.3, label="R1")
ax.scatter(r2_df["friction"], r2_df["disp_mm"], c="#e74c3c", s=60, marker="^",
           alpha=0.8, edgecolors="k", linewidths=0.3, label="R2")
ax.set_yscale("log")
ax.set_xlabel("friction coefficient")
ax.set_ylabel("max displacement [mm] (log)")
ax.set_title("Friccion vs Desplazamiento")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 5d: dam_h vs friction coloreado por estado (R2 only)
ax = fig.add_subplot(gs[1, 0])
for estado, color in colors_estado.items():
    mask = df["estado"] == estado
    if mask.any():
        ax.scatter(df.loc[mask, "dam_height"], df.loc[mask, "friction_coefficient"],
                   c=color, s=100, edgecolors="k", linewidths=0.5, label=estado, zorder=3)
        for _, r in df.loc[mask].iterrows():
            ax.annotate(r["case_id"].replace("sc2_", ""),
                        (r["dam_height"], r["friction_coefficient"]),
                        fontsize=6, ha="center", va="bottom",
                        xytext=(0, 5), textcoords="offset points")
ax.set_xlabel("dam_height [m]")
ax.set_ylabel("friction coefficient")
ax.set_title("Espacio dam_h x friction\n(la frontera es 2D, no 1D)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 5e: dam_h vs mass coloreado por estado
ax = fig.add_subplot(gs[1, 1])
for estado, color in colors_estado.items():
    mask = df["estado"] == estado
    if mask.any():
        ax.scatter(df.loc[mask, "dam_height"], df.loc[mask, "boulder_mass"],
                   c=color, s=100, edgecolors="k", linewidths=0.5, label=estado, zorder=3)
        for _, r in df.loc[mask].iterrows():
            ax.annotate(r["case_id"].replace("sc2_", ""),
                        (r["dam_height"], r["boulder_mass"]),
                        fontsize=6, ha="center", va="bottom",
                        xytext=(0, 5), textcoords="offset points")
ax.set_xlabel("dam_height [m]")
ax.set_ylabel("boulder_mass [kg]")
ax.set_title("Espacio dam_h x mass")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# 5f: Resumen texto
ax = fig.add_subplot(gs[1, 2])
ax.axis("off")
summary = (
    "RESUMEN R1 + R2\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "R1 (24 casos, dp=0.005):\n"
    "  - dam_h domina (rho=+0.75)\n"
    "  - Frontera ~dam_h=0.20m\n"
    "  - friction/rot_z/slope: n.s.\n\n"
    "R2 (15 casos, dp=0.004):\n"
    "  - friction domina (rho=-0.92)\n"
    "  - mass significativa (rho=-0.61)\n"
    "  - dam_h n.s. (diseno dirigido)\n\n"
    "COMBINADO (39 casos):\n"
    "  - La frontera es MULTIDIMENSIONAL\n"
    "  - dam_h + friction + mass definen\n"
    "    la superficie de estabilidad\n"
    "  - slope y rot_z son moduladores\n\n"
    "  sc2_007 demuestra que dam_h bajo\n"
    "  NO garantiza estabilidad si\n"
    "  friction y mass son bajos.\n\n"
    "VALIDACION:\n"
    "  - Dominio 15m: OK (margen >6m)\n"
    "  - TimeMax 10s: OK\n"
    "  - Sin reflexion problematica\n"
    "  - Replicacion OK (32% diff en dp)"
)
ax.text(0.05, 0.95, summary, transform=ax.transAxes, fontsize=9,
        verticalalignment="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#eaf7ea", edgecolor="#27ae60"))

fig.savefig(str(FIG_DIR / "r2_vs_r1_combinado.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("  [5/5] r2_vs_r1_combinado.png")

print("\nFiguras generadas en:", FIG_DIR)
print("Done.")
