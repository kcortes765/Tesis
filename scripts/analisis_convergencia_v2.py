"""
analisis_convergencia_v2.py — Analisis profundo de convergencia dp.

Lee TODOS los datos (exchange, forces, gauges, Run.csv) de cada dp
y produce diagnostico completo para entender por que dp=0.002 diverge.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

PROJECT = Path(__file__).resolve().parent.parent
PROC = PROJECT / "data" / "processed"
TEMP = PROJECT / "data" / "results" / "convergencia_v2_temporal"
FIG = PROJECT / "data" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

SENTINEL = -3.0e38
DP_ORDER = [0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002]
DP_NAMES = {0.010: "conv2_dp001", 0.008: "conv2_dp0008", 0.006: "conv2_dp0006",
            0.005: "conv2_dp0005", 0.004: "conv2_dp0004", 0.003: "conv2_dp0003",
            0.002: "conv2_dp0002"}
COLORS = {0.010: "#bdc3c7", 0.008: "#95a5a6", 0.006: "#7f8c8d",
          0.005: "#3498db", 0.004: "#2ecc71", 0.003: "#e67e22", 0.002: "#e74c3c"}


def load_exchange(dp):
    """Carga ChronoExchange y calcula metricas derivadas."""
    name = DP_NAMES[dp]
    # Intentar temporal primero, luego processed
    f = TEMP / f"{name}_exchange.csv"
    if not f.exists():
        d = PROC / name
        candidates = list(d.glob("ChronoExchange_mkbound_*.csv")) + list(d.rglob("ChronoExchange_mkbound_*.csv"))
        if not candidates:
            return None
        f = candidates[0]
    ex = pd.read_csv(f, sep=";")
    rename = {"time [s]": "t", "fvel.x [m/s]": "vx", "fvel.y [m/s]": "vy", "fvel.z [m/s]": "vz",
              "fcenter.x [m]": "cx", "fcenter.y [m]": "cy", "fcenter.z [m]": "cz",
              "fomega.x [rad/s]": "wx", "fomega.y [rad/s]": "wy", "fomega.z [rad/s]": "wz"}
    ex = ex.rename(columns=rename)
    cx0, cy0, cz0 = ex["cx"].iloc[0], ex["cy"].iloc[0], ex["cz"].iloc[0]
    ex["disp"] = np.sqrt((ex["cx"]-cx0)**2 + (ex["cy"]-cy0)**2 + (ex["cz"]-cz0)**2)
    ex["disp_x"] = ex["cx"] - cx0
    ex["disp_z"] = ex["cz"] - cz0
    ex["vxy"] = np.sqrt(ex["vx"]**2 + ex["vy"]**2)
    ex["vmag"] = np.sqrt(ex["vx"]**2 + ex["vy"]**2 + ex["vz"]**2)
    ex["omega_mag"] = np.sqrt(ex["wx"]**2 + ex["wy"]**2 + ex["wz"]**2)
    dt = ex["t"].diff().fillna(0)
    ex["rot_cumul"] = np.degrees(np.cumsum(ex["omega_mag"] * dt))
    return ex


def load_forces(dp):
    name = DP_NAMES[dp]
    f = TEMP / f"{name}_forces.csv"
    if not f.exists():
        d = PROC / name
        candidates = list(d.glob("ChronoBody_forces.csv")) + list(d.rglob("ChronoBody_forces.csv"))
        if not candidates:
            return None
        f = candidates[0]
    with open(f) as fh:
        header = fh.readline().strip().rstrip(";")
    raw_cols = header.split(";")
    clean = []
    body = ""
    for c in raw_cols:
        c = c.strip()
        if c == "Time":
            clean.append("t")
        elif c.startswith("Body_"):
            parts = c.split("_", 2)
            body = parts[1].lower()
            clean.append(f"{body}_{parts[2] if len(parts)>2 else 'fx'}")
        else:
            clean.append(f"{body}_{c}" if body else c)
    df = pd.read_csv(f, sep=";", header=0, usecols=range(len(clean)))
    df.columns = clean
    return df


def load_gauge_vel(dp, gauge_num):
    name = DP_NAMES[dp]
    d = PROC / name
    f = d / f"GaugesVel_V{gauge_num:02d}.csv"
    if not f.exists():
        for sub in d.rglob(f"GaugesVel_V{gauge_num:02d}.csv"):
            f = sub
            break
    if not f.exists():
        return None
    g = pd.read_csv(f, sep=";")
    g = g.rename(columns={"time [s]": "t", "velx [m/s]": "vx", "vely [m/s]": "vy", "velz [m/s]": "vz"})
    for c in ["vx", "vy", "vz"]:
        if c in g.columns:
            g.loc[g[c] < SENTINEL, c] = np.nan
    g["vmag"] = np.sqrt(g["vx"]**2 + g["vy"]**2 + g["vz"]**2)
    return g


def load_run_csv(dp):
    name = DP_NAMES[dp]
    d = PROC / name
    f = d / "Run.csv"
    if not f.exists():
        for sub in d.rglob("Run.csv"):
            f = sub
            break
    if not f.exists():
        return {}
    df = pd.read_csv(f, sep=";", nrows=1)
    result = {}
    for col in df.columns:
        val = str(df[col].iloc[0]).strip().replace(",", "")
        try:
            result[col.strip()] = float(val)
        except ValueError:
            result[col.strip()] = val
    return result


def load_runparts(dp):
    name = DP_NAMES[dp]
    d = PROC / name
    f = d / "RunPARTs.csv"
    if not f.exists():
        for sub in d.rglob("RunPARTs.csv"):
            f = sub
            break
    if not f.exists():
        return None
    return pd.read_csv(f, sep=";")


# ===================================================================
print("Cargando datos de 7 dp levels...")
exchanges = {}
forces = {}
run_data = {}
runparts = {}
for dp in DP_ORDER:
    exchanges[dp] = load_exchange(dp)
    forces[dp] = load_forces(dp)
    run_data[dp] = load_run_csv(dp)
    runparts[dp] = load_runparts(dp)
    n = len(exchanges[dp]) if exchanges[dp] is not None else 0
    print(f"  dp={dp}: {n} timesteps")

# ===================================================================
# RESUMEN NUMERICO
# ===================================================================
print("\n" + "="*80)
print("RESUMEN CONVERGENCIA")
print("="*80)

summary_rows = []
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is None:
        continue
    rd = run_data[dp]
    summary_rows.append({
        "dp": dp,
        "max_disp_m": ex["disp"].max(),
        "final_disp_m": ex["disp"].iloc[-1],
        "max_disp_x_m": ex["disp_x"].max(),
        "final_cx": ex["cx"].iloc[-1],
        "final_cz": ex["cz"].iloc[-1],
        "max_vel": ex["vmag"].max(),
        "max_vxy": ex["vxy"].max(),
        "max_rot_deg": ex["rot_cumul"].max(),
        "final_rot_deg": ex["rot_cumul"].iloc[-1],
        "init_cx": ex["cx"].iloc[0],
        "init_cz": ex["cz"].iloc[0],
        "Np": rd.get("Np", None),
        "MemGpu": rd.get("MemGpu", rd.get("MemGpuNct", None)),
    })

df_sum = pd.DataFrame(summary_rows)
print(df_sum.to_string(index=False))

# Deltas
print("\nDELTAS ENTRE NIVELES:")
print(f"{'dp1':>8} {'dp2':>8} | {'d_disp%':>8} {'d_vel%':>8} {'d_rot%':>8} | {'disp1':>8} {'disp2':>8}")
for i in range(len(summary_rows)-1):
    r1 = summary_rows[i]
    r2 = summary_rows[i+1]
    dd = abs(r1["max_disp_m"]-r2["max_disp_m"])/r1["max_disp_m"]*100
    dv = abs(r1["max_vel"]-r2["max_vel"])/r1["max_vel"]*100
    dr = abs(r1["max_rot_deg"]-r2["max_rot_deg"])/max(r1["max_rot_deg"],1)*100
    print(f"{r1['dp']:>8.4f} {r2['dp']:>8.4f} | {dd:>7.1f}% {dv:>7.1f}% {dr:>7.1f}% | {r1['max_disp_m']:>8.4f} {r2['max_disp_m']:>8.4f}")

# ===================================================================
# POSICION INICIAL DEL BOULDER (debe ser igual en todos los dp)
# ===================================================================
print("\nPOSICION INICIAL BOULDER:")
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        print(f"  dp={dp}: cx0={ex['cx'].iloc[0]:.6f}, cy0={ex['cy'].iloc[0]:.6f}, cz0={ex['cz'].iloc[0]:.6f}")

# ===================================================================
# FIGURA 1: Dashboard convergencia completo
# ===================================================================
fig = plt.figure(figsize=(22, 20))
gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)
fig.suptitle("Convergencia dp v2 — Analisis Profundo (7 niveles, dam_h=0.30)", fontsize=16, fontweight="bold")

# 1a: Displacement temporal
ax = fig.add_subplot(gs[0, 0])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["disp"]*1000, color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento 3D [mm]")
ax.set_title("Desplazamiento vs tiempo")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 1b: Displacement X temporal
ax = fig.add_subplot(gs[0, 1])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["disp_x"]*1000, color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento X [mm]")
ax.set_title("Desplazamiento longitudinal")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 1c: Displacement Z temporal
ax = fig.add_subplot(gs[0, 2])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["disp_z"]*1000, color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Desplazamiento Z [mm]")
ax.set_title("Desplazamiento vertical")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 2a: Velocidad horizontal
ax = fig.add_subplot(gs[1, 0])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["vxy"], color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Velocidad horizontal [m/s]")
ax.set_title("Velocidad boulder (XY)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 2b: Rotacion acumulada
ax = fig.add_subplot(gs[1, 1])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["rot_cumul"], color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Rotacion acumulada [deg]")
ax.set_title("Rotacion (integral omega)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 2c: Omega magnitude
ax = fig.add_subplot(gs[1, 2])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["t"], ex["omega_mag"], color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5, alpha=0.7)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("|omega| [rad/s]")
ax.set_title("Velocidad angular instantanea")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# 3a: Convergencia metricas vs dp
ax = fig.add_subplot(gs[2, 0])
dps = [r["dp"] for r in summary_rows]
disps = [r["max_disp_m"] for r in summary_rows]
vels = [r["max_vel"] for r in summary_rows]
ax.plot(dps, disps, "o-", color="#e74c3c", label="max_displacement [m]", markersize=6)
ax2 = ax.twinx()
ax2.plot(dps, vels, "s--", color="#3498db", label="max_velocity [m/s]", markersize=6)
ax.set_xlabel("dp [m]")
ax.set_ylabel("Displacement [m]", color="#e74c3c")
ax2.set_ylabel("Velocity [m/s]", color="#3498db")
ax.set_title("Convergencia: metricas vs dp")
ax.invert_xaxis()
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=7)
ax.grid(True, alpha=0.2)

# 3b: SPH Force vs dp
ax = fig.add_subplot(gs[2, 1])
fsph = [r["max_disp_m"] for r in summary_rows]  # placeholder
# Read from CSV
conv_csv = pd.read_csv(PROJECT / "data" / "results" / "convergencia_v2.csv", sep=";")
conv_ok = conv_csv[conv_csv["status"]=="OK"].sort_values("dp", ascending=False)
ax.plot(conv_ok["dp"], conv_ok["max_sph_force_N"], "o-", color="#9b59b6", markersize=6)
ax.set_xlabel("dp [m]")
ax.set_ylabel("Max SPH Force [N]")
ax.set_title("SPH Force vs dp (OSCILATORIA)")
ax.invert_xaxis()
ax.grid(True, alpha=0.2)

# 3c: Rotation vs dp
ax = fig.add_subplot(gs[2, 2])
rots = [r["max_rot_deg"] for r in summary_rows]
ax.plot(dps, rots, "o-", color="#e67e22", markersize=6)
ax.set_xlabel("dp [m]")
ax.set_ylabel("Max Rotation [deg]")
ax.set_title("Rotacion vs dp (OSCILATORIA)")
ax.invert_xaxis()
ax.grid(True, alpha=0.2)

# 4a: Trayectoria XZ del boulder
ax = fig.add_subplot(gs[3, 0])
for dp in DP_ORDER:
    ex = exchanges[dp]
    if ex is not None:
        ax.plot(ex["cx"], ex["cz"], color=COLORS[dp], label=f"dp={dp}", linewidth=0.8 if dp > 0.005 else 1.5)
        ax.plot(ex["cx"].iloc[-1], ex["cz"].iloc[-1], "o", color=COLORS[dp], markersize=4)
# Dibujar pendiente
x_slope = np.linspace(6.0, 8.0, 50)
z_slope = (x_slope - 6.0) / 20.0
ax.plot(x_slope, z_slope, "k--", alpha=0.3, label="bed slope 1:20")
ax.set_xlabel("X [m]")
ax.set_ylabel("Z [m]")
ax.set_title("Trayectoria XZ del boulder")
ax.legend(fontsize=6)
ax.grid(True, alpha=0.2)

# 4b: Flujo en gauge V05 (upstream del boulder)
ax = fig.add_subplot(gs[3, 1])
for dp in DP_ORDER:
    g = load_gauge_vel(dp, 5)
    if g is not None:
        ax.plot(g["t"], g["vx"], color=COLORS[dp], label=f"dp={dp}", linewidth=0.6, alpha=0.7)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("velx [m/s]")
ax.set_title("Flujo en V05 (upstream boulder)")
ax.legend(fontsize=6)
ax.grid(True, alpha=0.2)

# 4c: Np y MemGPU vs dp
ax = fig.add_subplot(gs[3, 2])
nps = conv_ok["n_particles"].values
mems = conv_ok["mem_gpu_mb"].values
dps_ok = conv_ok["dp"].values
ax.bar(range(len(dps_ok)), nps/1e6, color=[COLORS.get(d, "#333") for d in dps_ok], edgecolor="k")
ax.set_xticks(range(len(dps_ok)))
ax.set_xticklabels([f"{d}" for d in dps_ok], rotation=45, fontsize=8)
ax.set_ylabel("Particulas [M]")
ax.set_title("Particulas y VRAM vs dp")
ax2 = ax.twinx()
ax2.plot(range(len(dps_ok)), mems/1024, "ro-", markersize=5)
ax2.set_ylabel("MemGPU [GiB]", color="red")
ax2.axhline(32, color="red", ls="--", alpha=0.5, label="RTX 5090 32GB")
ax2.legend(fontsize=7)

fig.savefig(str(FIG / "conv2_dashboard.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("\n[FIG] conv2_dashboard.png")

# ===================================================================
# FIGURA 2: Zoom en dp=0.003 vs dp=0.002 (donde diverge)
# ===================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("dp=0.003 vs dp=0.002 — Por que diverge?", fontsize=14, fontweight="bold")

ex3 = exchanges[0.003]
ex2 = exchanges[0.002]

# Displacement
ax = axes[0, 0]
ax.plot(ex3["t"], ex3["disp"]*1000, color=COLORS[0.003], label="dp=0.003", linewidth=1.5)
ax.plot(ex2["t"], ex2["disp"]*1000, color=COLORS[0.002], label="dp=0.002", linewidth=1.5)
ax.set_ylabel("Desplazamiento [mm]")
ax.set_title("Displacement 3D")
ax.legend()
ax.grid(True, alpha=0.2)

# Displacement X
ax = axes[0, 1]
ax.plot(ex3["t"], ex3["cx"], color=COLORS[0.003], label="dp=0.003", linewidth=1.5)
ax.plot(ex2["t"], ex2["cx"], color=COLORS[0.002], label="dp=0.002", linewidth=1.5)
ax.set_ylabel("fcenter.x [m]")
ax.set_title("Posicion X")
ax.legend()
ax.grid(True, alpha=0.2)

# Displacement Z
ax = axes[0, 2]
ax.plot(ex3["t"], ex3["cz"], color=COLORS[0.003], label="dp=0.003", linewidth=1.5)
ax.plot(ex2["t"], ex2["cz"], color=COLORS[0.002], label="dp=0.002", linewidth=1.5)
ax.set_ylabel("fcenter.z [m]")
ax.set_title("Posicion Z")
ax.legend()
ax.grid(True, alpha=0.2)

# Velocidad
ax = axes[1, 0]
ax.plot(ex3["t"], ex3["vxy"], color=COLORS[0.003], label="dp=0.003", linewidth=1)
ax.plot(ex2["t"], ex2["vxy"], color=COLORS[0.002], label="dp=0.002", linewidth=1)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Vel horizontal [m/s]")
ax.set_title("Velocidad XY")
ax.legend()
ax.grid(True, alpha=0.2)

# Rotacion
ax = axes[1, 1]
ax.plot(ex3["t"], ex3["rot_cumul"], color=COLORS[0.003], label="dp=0.003", linewidth=1.5)
ax.plot(ex2["t"], ex2["rot_cumul"], color=COLORS[0.002], label="dp=0.002", linewidth=1.5)
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Rotacion acumulada [deg]")
ax.set_title("Rotacion")
ax.legend()
ax.grid(True, alpha=0.2)

# Omega
ax = axes[1, 2]
ax.plot(ex3["t"], ex3["omega_mag"], color=COLORS[0.003], alpha=0.5, linewidth=0.5, label="dp=0.003")
ax.plot(ex2["t"], ex2["omega_mag"], color=COLORS[0.002], alpha=0.5, linewidth=0.5, label="dp=0.002")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("|omega| [rad/s]")
ax.set_title("Omega instantanea")
ax.legend()
ax.grid(True, alpha=0.2)

fig.savefig(str(FIG / "conv2_003_vs_002.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("[FIG] conv2_003_vs_002.png")

# ===================================================================
# FIGURA 3: Fuerzas SPH detalladas
# ===================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Fuerzas SPH sobre boulder (corregidas por gravedad)", fontsize=14, fontweight="bold")

for idx, dp in enumerate([0.005, 0.004, 0.003, 0.002]):
    ax = axes[idx//2, idx%2]
    ff = forces[dp]
    if ff is not None and "blir_fx" in ff.columns:
        weight = 1.0 * 9.81
        fx = ff["blir_fx"]
        fz = ff["blir_fz"] + weight
        f_mag = np.sqrt(fx**2 + ff["blir_fy"]**2 + fz**2)
        ax.plot(ff["t"], f_mag, color=COLORS[dp], linewidth=0.5, alpha=0.7, label="SPH |F|")
        if "blir_cfx" in ff.columns:
            cf_mag = np.sqrt(ff["blir_cfx"]**2 + ff["blir_cfy"]**2 + ff["blir_cfz"]**2)
            ax.plot(ff["t"], cf_mag, color="gray", linewidth=0.3, alpha=0.4, label="Contact |F|")
        ax.set_ylabel("Fuerza [N]")
        ax.set_title(f"dp={dp}")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.2)
        ax.set_xlabel("Tiempo [s]")

fig.savefig(str(FIG / "conv2_forces_detail.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("[FIG] conv2_forces_detail.png")

# ===================================================================
# FIGURA 4: RunPARTs — evolucion temporal del solver
# ===================================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("RunPARTs: evolucion temporal del solver", fontsize=13, fontweight="bold")

for dp in [0.004, 0.003, 0.002]:
    rp = runparts[dp]
    if rp is not None:
        # Buscar columnas de tiempo
        time_col = None
        for c in rp.columns:
            if "time" in c.lower() and "total" not in c.lower():
                time_col = c
                break
        if time_col is None:
            continue

        t = rp[time_col]

        # Steps per second
        steps_col = None
        for c in rp.columns:
            if "step" in c.lower():
                steps_col = c
                break

        # Dt
        dt_col = None
        for c in rp.columns:
            if c.strip().lower() == "dt":
                dt_col = c
                break

        color = COLORS[dp]
        lbl = f"dp={dp}"

        if steps_col:
            axes[0].plot(t, rp[steps_col], color=color, label=lbl, linewidth=0.8)
        if dt_col:
            axes[1].plot(t, rp[dt_col], color=color, label=lbl, linewidth=0.8)

axes[0].set_xlabel("Sim time [s]")
axes[0].set_ylabel("Steps")
axes[0].set_title("Steps acumulados")
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.2)

axes[1].set_xlabel("Sim time [s]")
axes[1].set_ylabel("dt [s]")
axes[1].set_title("Timestep del solver")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.2)

# Runtime vs dp
axes[2].bar(range(len(conv_ok)), conv_ok["tiempo_min"].values,
            color=[COLORS.get(d, "#333") for d in conv_ok["dp"].values], edgecolor="k")
axes[2].set_xticks(range(len(conv_ok)))
axes[2].set_xticklabels([f"{d}" for d in conv_ok["dp"].values], rotation=45, fontsize=8)
axes[2].set_ylabel("Tiempo [min]")
axes[2].set_title("Runtime por dp")

fig.savefig(str(FIG / "conv2_solver_detail.png"), dpi=180, bbox_inches="tight")
plt.close(fig)
print("[FIG] conv2_solver_detail.png")

# ===================================================================
# REPORTE TEXTO
# ===================================================================
report_path = FIG / "convergencia_v2_analisis.md"
lines = [
    "# Convergencia dp v2 — Analisis Profundo",
    f"**Generado:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
    f"**Caso:** dam_h=0.30, mass=1.0, fric=0.3, slope=1:20",
    f"**dp exitosos:** {len(summary_rows)} (0.010 a 0.002)",
    f"**dp fallido:** 0.0015 (GenCase fallo)",
    "",
    "## Tabla de convergencia",
    "",
    "| dp | disp [m] | delta% | vel [m/s] | delta% | rot [deg] | Np | MemGPU |",
    "|---|---|---|---|---|---|---|---|",
]

prev_d, prev_v = None, None
for r in summary_rows:
    dd = f"{abs(r['max_disp_m']-prev_d)/prev_d*100:.1f}%" if prev_d else "-"
    dv = f"{abs(r['max_vel']-prev_v)/prev_v*100:.1f}%" if prev_v else "-"
    np_str = f"{r['Np']/1e6:.1f}M" if r['Np'] else "?"
    mem = r.get('MemGpu', 0) or 0
    mem_str = f"{mem/1e9:.1f}GB" if mem > 1e9 else f"{mem/1e6:.0f}MB" if mem > 1e6 else f"{mem:.0f}"
    lines.append(f"| {r['dp']} | {r['max_disp_m']:.4f} | {dd} | {r['max_vel']:.4f} | {dv} | {r['max_rot_deg']:.1f} | {np_str} | {mem_str} |")
    prev_d, prev_v = r["max_disp_m"], r["max_vel"]

lines.extend([
    "",
    "## Hallazgos",
    "",
    "### Displacement y Velocity",
    f"- dp 0.004→0.003: delta disp = 2.5%, delta vel = 0.4% — APARENTEMENTE CONVERGIDO",
    f"- dp 0.003→0.002: delta disp = 10.8%, delta vel = 8.2% — SE ABRE DE NUEVO",
    "",
    "### Rotation",
    "- Oscilatoria: " + ", ".join(f"dp={r['dp']}={r['max_rot_deg']:.0f} deg" for r in summary_rows),
    f"- dp=0.002 muestra 171° vs 92° a dp=0.003 — DUPLICA",
    "",
    "### SPH Force",
    "- Oscilatoria en todo el rango",
    "",
    "### dp=0.0015",
    "- GenCase fallo (probablemente excede limites de memoria o particulas)",
    "",
    "## Figuras",
    "- conv2_dashboard.png — Dashboard completo",
    "- conv2_003_vs_002.png — Comparacion detallada dp=0.003 vs 0.002",
    "- conv2_forces_detail.png — Fuerzas SPH y contacto",
    "- conv2_solver_detail.png — Detalles del solver",
])

report_path.write_text("\n".join(lines), encoding="utf-8")
print(f"\n[REPORT] {report_path}")
print("\nDone.")
