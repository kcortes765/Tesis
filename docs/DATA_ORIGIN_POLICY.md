# Politica de origen de datos y carpetas canonicas

Fecha: 2026-05-10

## Regla principal

El repo canonico local es:

```text
C:\Seba\Tesis
```

Nota operativa: en esta laptop `C:\Seba\Tesis` es una junction hacia:

```text
C:\Users\kevin\projects\Tesis
```

Son la misma carpeta de trabajo. No deben tratarse como dos repos distintos.

No debe existir una segunda carpeta de trabajo con APOS vivo. Cualquier worktree temporal usado para rescate, comparacion o auditoria debe retirarse al terminar la reconciliacion.

## Fuentes de datos

### 1. GitHub / WS UCN

Fuente:

```text
origin/master
```

Uso:

- codigo versionado;
- configs;
- docs;
- APOS del proyecto;
- exports livianos generados en la WS;
- resultados CSV/SQLite livianos que se decida versionar.

La WS UCN produce simulaciones pesadas. Lo que viaja por Git debe ser un paquete liviano auditable, por ejemplo:

```text
exports/pilot_productivo_20260501/
exports/batch2_productivo_20260505/
exports/batch3_productivo_20260509/
```

No se debe asumir que GitHub contiene todos los crudos de simulacion.

### 2. Laptop principal

Fuente:

```text
C:\Seba\Tesis
```

Uso:

- analisis local;
- documentos;
- web/figuras;
- scripts auxiliares;
- STL recibidos localmente;
- archivos temporales o historicos.

Los archivos locales no versionados pueden ser valiosos, pero no son automaticamente fuente canonica. Si se incorporan, deben pasar por revision y commit selectivo.

### 3. Crudos pesados

Fuente recomendada:

```text
disco externo / storage dedicado
```

Uso:

- `cases/*_out/`;
- `Part*`;
- `*.bi4`, `*.ibi4`, VTK;
- outputs crudos completos de DualSPHysics;
- exports masivos.

Estos datos no deben entrar a Git normal salvo decision explicita con Git LFS o storage separado.

## APOS

APOS canonico vive solo en:

```text
C:\Seba\Tesis\.apos
```

Reglas:

- `STATUS.md`, `HANDOFF.md` e `INDEX.md` son estado vivo.
- `DECISIONS.md`, `JOURNAL.md`, `SOURCES.md` y `RESEARCH_LOG.md` son append-only.
- Si una IA de la WS actualiza APOS, debe subirlo por Git como parte de un export liviano.
- Si una IA local actualiza APOS, debe hacerlo en el repo canonico y dejar claro si el dato viene de WS/GitHub o de laptop local.

## Que hacer cuando llega data desde WS

1. `git fetch` / `git pull` solo en el repo canonico.
2. Leer primero el export liviano correspondiente.
3. No copiar crudos enormes al repo sin decision explicita.
4. Registrar en APOS:
   - lote;
   - origen;
   - commit;
   - archivos incluidos;
   - archivos deliberadamente excluidos.

## Que hacer con data local nueva

1. Identificar si es resultado cientifico, soporte reproducible o crudo pesado.
2. Versionar solo lo liviano y necesario.
3. Guardar crudos pesados fuera de Git.
4. Si el dato local contradice WS/GitHub, registrar la contradiccion en `OPEN_QUESTIONS.md` o `RISKS.md`.

## Estado al 2026-05-10

- `C:\Seba\Tesis` fue actualizado a `origin/master` en commit `3c443e9`.
- Los cambios trackeados locales previos quedaron en `stash@{0}` y backup externo.
- El backup externo principal esta en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- Los 8 archivos no trackeados que chocaban con GitHub fueron movidos a `.apos/cache/git-untracked-conflicts-20260510_125339/` y respaldados.
- La carpeta temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639` fue solo una herramienta de rescate y no debe quedar como fuente de trabajo.
