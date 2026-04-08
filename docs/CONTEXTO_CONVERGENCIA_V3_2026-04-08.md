# Contexto de Convergencia V3 — 2026-04-08

## Objetivo inmediato

Dejar corriendo una **segunda convergencia corta** cerca de la frontera `ESTABLE/FALLO` para comparar contra la convergencia v2 ya corrida (`dam_h=0.30`, fallo masivo) antes de hablar con Moris.

La idea NO es cerrar todavía la historia metodológica con el profe. Primero correr, comparar, y recién después decidir qué contar.

---

## Estado actual del proyecto

- La convergencia anterior **sí llegó a `dp=0.003`** y fue válida para su configuración original.
- Esa convergencia vieja **no es transferible automáticamente** al setup actual 5D porque cambió la física/configuración:
  - canal paramétrico
  - `slope_inv`
  - fricción Chrono
  - nueva posición del boulder
  - material / setup base distinto
- Esto quedó formalizado en `.apos/DECISIONS.md` como `DEC-032`.

---

## Qué pasó en la convergencia v2 ya corrida

Archivo principal: `data/results/convergencia_v2.csv`

Caso de referencia v2:
- `dam_h=0.30`
- `mass=1.0`
- `friction=0.3`
- `slope=1:20`
- `rot_z=0`
- canal 15 m

Resultados principales:

| dp | disp [m] | vel [m/s] | rot [deg] | Np | MemGPU |
|---|---:|---:|---:|---:|---:|
| 0.004 | 2.016 | 0.882 | 97.0 | 10.5 M | 2.0 GiB |
| 0.003 | 1.966 | 0.878 | 92.0 | 23.0 M | 4.3 GiB |
| 0.002 | 1.753 | 0.806 | 171.5 | 70.6 M | 13.3 GiB |

Hallazgos técnicos:

1. **El forcing hidráulico converge bien**
   - `max_flow_velocity` casi igual entre `0.004`, `0.003`, `0.002`
   - `max_water_height` casi igual entre `0.004`, `0.003`, `0.002`

2. **El onset converge razonablemente**
   - tiempos de cruce de `5% d_eq` y `50 mm` muy similares entre `0.004`, `0.003`, `0.002`

3. **Lo que no converge limpio es la trayectoria post-falla a 10 s**
   - `max_displacement` cambia bastante entre `0.003` y `0.002`
   - la respuesta rotacional cambia de rama

4. **`SPH force` pico es oscilatoria**
   - mala primaria para cerrar `dp` en este caso

5. **La rotación actual no es ángulo neto**
   - `src/data_cleaner.py` integra `|omega|`
   - sirve como diagnóstico bruto, no como observable fino

6. **`dp=0.0015` falló en GenCase**
   - muy probablemente por tamaño/memoria

Interpretación operativa actual:

- La v2 no demuestra que el solver esté mal.
- Demuestra que el caso Moris `dam_h=0.30` no es ideal para decidir resolución si la pregunta científica es `incipient motion`.
- La sospecha fuerte es: **forcing y onset sí están cerca de converger; la trayectoria larga post-falla no**.

---

## Qué se quiere probar con la V3

Se quiere correr una convergencia corta en un caso **mucho más cerca de la frontera** para probar si:

- `dp=0.004`, `0.003`, `0.002`
  - mantienen la misma clasificación `ESTABLE/FALLO`
  - tienen onset parecido
  - reducen mucho la sensibilidad observada en la v2

Si eso pasa, `dp=0.003` queda mucho mejor parado como resolución de trabajo para la tesis.

---

## Criterio para elegir el caso V3

No usar otro FALLO masivo.

Queremos un caso en la zona de transición. Mirando `results_round2.csv` y `screening_round3.csv`, el mejor candidato inmediato es:

### Caso recomendado 1

- `dam_h = 0.20`
- `mass = 1.0`
- `friction = 0.5`
- `slope_inv = 20`
- `rot_z = 0`

Justificación:
- está exactamente en la línea de transición que ya quedó diseñada en `screening_round3.csv`
- es mucho más informativo para `incipient motion` que `dam_h=0.30`
- no pisa ni contradice el razonamiento previo

### Caso recomendado 2 (opcional)

- `dam_h = 0.20`
- `mass = 1.0`
- `friction = 0.6`
- `slope_inv = 20`
- `rot_z = 0`

Este segundo caso sirve para comparar un punto algo más estable sin salir de la misma familia.

---

## Script listo para usar

Se creó:

- `scripts/run_convergence_threshold.py`

Características:

- reutiliza la infraestructura de `scripts/run_convergence_v2.py`
- corre solo dp finos por defecto: `0.004, 0.003, 0.002`
- permite fijar un caso de frontera por CLI
- escribe resultados en archivos separados usando `prefix`
- no pisa:
  - `convergencia_v2.csv`
  - `convergencia_v2_gci.json`
  - `convergencia_v2.log`
  - `convergencia_v2_temporal/`

Salidas esperadas por corrida:

- `data/results/<prefix>.csv`
- `data/results/<prefix>_gci.json`
- `data/results/<prefix>_temporal/`
- `data/logs/<prefix>.log`
- `data/logs/<prefix>_status.json`
- SQLite en tabla `convergence_<prefix>`

Smoke test realizado:

- `python scripts/run_convergence_threshold.py --solo-analisis --prefix smoke_threshold`
- El script arranca bien, crea rutas bien y falla de forma esperada si no existe CSV previo.

---

## Comandos sugeridos

### En laptop

Subir el nuevo script y este contexto a la WS:

```powershell
git add scripts/run_convergence_threshold.py docs/CONTEXTO_CONVERGENCIA_V3_2026-04-08.md
git commit -m "feat: add threshold-focused convergence runner"
git push origin master
```

### En la WS — corrida recomendada

```powershell
git pull origin master
python scripts/run_convergence_threshold.py --dam-height 0.20 --mass 1.0 --friction 0.5 --slope-inv 20 --prefix conv3_f05
```

### En la WS — segunda corrida opcional

```powershell
python scripts/run_convergence_threshold.py --dam-height 0.20 --mass 1.0 --friction 0.6 --slope-inv 20 --prefix conv3_f06
```

---

## Qué comparar cuando termine

Comparar, para cada corrida nueva:

1. **Clasificación final**
   - si `0.004`, `0.003`, `0.002` dan la misma clase o no

2. **Onset**
   - tiempo de cruce `5% d_eq`
   - tiempo de cruce `50 mm`

3. **Desplazamiento temprano**
   - desplazamiento a `2.0 s`
   - desplazamiento a `2.5 s`

4. **Trayectoria completa**
   - si la divergencia `0.003 -> 0.002` desaparece o baja mucho respecto a la v2

5. **Costo**
   - si `0.002` realmente aporta algo metodológicamente útil para la zona de frontera

---

## Qué no concluir todavía

- No decir aún que `dp=0.003` quedó cerrado.
- No decir aún que la v2 “fracasó”.
- No decir aún que el problema es el solver.
- No contarle al profe una narrativa cerrada antes de comparar la v3 con la v2.

La postura correcta, por ahora, es:

> “La v2 mostró que forcing y onset parecen converger mucho mejor que la trayectoria post-falla. Vamos a probar eso con una convergencia corta cerca de la frontera antes de fijar el `dp`.”

---

## Archivos clave para leer

- `data/results/convergencia_v2.csv`
- `data/results/convergencia_v2_gci.json`
- `data/logs/convergencia_v2.log`
- `data/figures/convergencia_v2_analisis.md`
- `scripts/run_convergence_v2.py`
- `scripts/run_convergence_threshold.py`
- `config/screening_round3.csv`
- `.apos/DECISIONS.md`

---

## Nota importante de trazabilidad

La convergencia vieja:
- sí llegó a `dp=0.003`
- sí fue válida para el setup viejo

Pero hay desalineación entre:
- resultados/documentos finales
- algunos scripts versionados que quedaron representando una etapa intermedia

Eso no invalida la convergencia vieja histórica; solo significa que no debe usarse de forma automática como evidencia para el setup 5D actual.
