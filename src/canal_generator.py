"""
canal_generator.py — Genera STLs de canal parametrico con trimesh.

Replica la topologia del STL original del profe:
  - Fondo: plano + rampa (+ plataforma opcional)
  - Paredes laterales y=0 e y=W (siguen perfil del fondo hasta H)
  - Pared trasera x=0
  - Pared frontal x=L_end
  - SIN tapa (abierto arriba)

Autor: Kevin Cortes (UCN 2026)
"""

import logging
from pathlib import Path
import numpy as np
import trimesh

logger = logging.getLogger(__name__)


def generate_canal_stl(
    slope_inv: float = 20.0,
    L_flat: float = 6.0,
    L_ramp: float = 9.0,
    L_platform: float = 0.0,
    W: float = 1.0,
    H_walls: float = 1.5,
    output_path: Path = None,
) -> trimesh.Trimesh:
    H_ramp = L_ramp / slope_inv
    L_end = L_flat + L_ramp + L_platform
    # Tope de paredes: 1.5m fijo, o H_ramp + 0.5cm si la rampa supera 1.5m
    H = max(H_walls, H_ramp + 0.005)

    logger.info(f"Generando canal: L_flat={L_flat}m, L_ramp={L_ramp}m, "
                f"slope=1:{slope_inv:.0f}, H_ramp={H_ramp:.4f}m, "
                f"L_end={L_end:.1f}m, W={W}m, H={H}m")

    if L_platform > 0:
        # --- CON PLATAFORMA (como original 30m) ---
        # 14 vertices, 20 faces
        #
        # Perfil fondo y=0: A(0,0,0) B(Lf,0,0) C(Lf+Lr,0,Hr) D(Le,0,Hr)
        # Top pared y=0:    E(0,0,H) F(Lf+Lr,0,H) G(Le,0,H)
        # Perfil fondo y=W: A'...D' (indices +7)
        # Top pared y=W:    E'...G' (indices +7)

        Lf, Lr, Le, Hr = L_flat, L_ramp, L_end, H_ramp
        Xr = Lf + Lr  # x fin rampa

        vertices = [
            # y=0: fondo
            [0, 0, 0],       # 0 = A
            [Lf, 0, 0],      # 1 = B
            [Xr, 0, Hr],     # 2 = C
            [Le, 0, Hr],     # 3 = D
            # y=0: top pared
            [0, 0, H],       # 4 = E
            [Xr, 0, H],      # 5 = F
            [Le, 0, H],      # 6 = G
            # y=W: fondo
            [0, W, 0],       # 7 = A'
            [Lf, W, 0],      # 8 = B'
            [Xr, W, Hr],     # 9 = C'
            [Le, W, Hr],     # 10 = D'
            # y=W: top pared
            [0, W, H],       # 11 = E'
            [Xr, W, H],      # 12 = F'
            [Le, W, H],      # 13 = G'
        ]

        faces = [
            # === FONDO (6 caras) ===
            [0, 8, 1], [0, 7, 8],       # plano
            [1, 9, 2], [1, 8, 9],       # rampa
            [2, 10, 3], [2, 9, 10],     # plataforma

            # === PARED LATERAL y=0 (5 caras) ===
            # Sigue perfil: A-B al fondo, E arriba
            [0, 1, 4],                   # triangulo: A-B-E
            # B-C al fondo, E-F arriba
            [1, 2, 4], [4, 2, 5],       # cuadrilatero B-C-F-E
            # C-D al fondo, F-G arriba
            [2, 3, 5], [5, 3, 6],       # cuadrilatero C-D-G-F

            # === PARED LATERAL y=W (5 caras) ===
            [7, 11, 8],                  # A'-E'-B'
            [8, 11, 9], [11, 12, 9],    # B'-E'-C' y E'-F'-C'
            [9, 12, 10], [12, 13, 10],  # C'-F'-D' y F'-G'-D'

            # === PARED TRASERA x=0 (2 caras) ===
            [0, 4, 11], [0, 11, 7],

            # === PARED FRONTAL x=L_end (2 caras) ===
            [3, 6, 13], [3, 13, 10],
        ]

    else:
        # --- SIN PLATAFORMA (15m, termina en fin de rampa) ---
        # 10 vertices, 14 faces
        #
        # Perfil fondo y=0: A(0,0,0) B(Lf,0,0) C(Le,0,Hr)
        # Top pared y=0:    D(0,0,H) E(Le,0,H)
        # Perfil fondo y=W: A'(0,W,0) B'(Lf,W,0) C'(Le,W,Hr)
        # Top pared y=W:    D'(0,W,H) E'(Le,W,H)

        Lf, Hr = L_flat, H_ramp

        vertices = [
            # y=0: fondo
            [0, 0, 0],       # 0 = A
            [Lf, 0, 0],      # 1 = B
            [L_end, 0, Hr],  # 2 = C
            # y=0: top pared
            [0, 0, H],       # 3 = D
            [L_end, 0, H],   # 4 = E
            # y=W: fondo
            [0, W, 0],       # 5 = A'
            [Lf, W, 0],      # 6 = B'
            [L_end, W, Hr],  # 7 = C'
            # y=W: top pared
            [0, W, H],       # 8 = D'
            [L_end, W, H],   # 9 = E'
        ]

        faces = [
            # === FONDO (4 caras) ===
            [0, 6, 1], [0, 5, 6],       # plano
            [1, 7, 2], [1, 6, 7],       # rampa

            # === PARED LATERAL y=0 (3 caras) ===
            [0, 1, 3],                   # A-B-D (triangulo sobre zona plana)
            [1, 2, 3], [3, 2, 4],       # B-C-D y D-C-E (sobre rampa)

            # === PARED LATERAL y=W (3 caras) ===
            [5, 8, 6],                   # A'-D'-B'
            [6, 8, 7], [8, 9, 7],       # B'-D'-C' y D'-E'-C'

            # === PARED TRASERA x=0 (2 caras) ===
            [0, 3, 8], [0, 8, 5],

            # === PARED FRONTAL x=L_end (2 caras) ===
            [2, 4, 9], [2, 9, 7],
        ]

    mesh = trimesh.Trimesh(
        vertices=np.array(vertices, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
    )
    mesh.fix_normals()

    logger.info(f"  Canal: {len(mesh.vertices)} verts, {len(mesh.faces)} faces, "
                f"watertight={mesh.is_watertight}")

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mesh.export(str(output_path))
        logger.info(f"  STL guardado: {output_path}")

    return mesh


def get_boulder_position(slope_inv: float, L_flat: float = 6.0,
                         offset_from_ramp_start: float = 0.5,
                         y_center: float = 0.5) -> tuple:
    """Calcula la posicion del boulder al inicio de la rampa."""
    x = L_flat + offset_from_ramp_start
    z = offset_from_ramp_start / slope_inv
    return (x, y_center, z)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    out_dir = Path(__file__).parent.parent / 'models' / 'canales'
    out_dir.mkdir(parents=True, exist_ok=True)

    for slope in [5, 10, 20, 30]:
        mesh = generate_canal_stl(
            slope_inv=slope,
            L_flat=6.0,
            L_ramp=9.0,
            L_platform=0.0,
            output_path=out_dir / f'canal_1to{slope}.stl',
        )
        pos = get_boulder_position(slope)
        print(f"  1:{slope} -> boulder pos: {pos}")

    generate_canal_stl(
        slope_inv=20,
        L_flat=6.0,
        L_ramp=9.0,
        L_platform=15.0,
        output_path=out_dir / 'canal_1to20_30m.stl',
    )

    print("\nCanales generados en:", out_dir)
