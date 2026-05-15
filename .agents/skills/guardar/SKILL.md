---
name: guardar
description: Guarda el avance APOS de la sesion. Usar cuando el usuario diga /guardar, guardar avance, cerrar sesion, dejar handoff, actualizar APOS o preparar el proximo chat.
---

# /guardar

## Objetivo
Persistir el estado real de la sesion para que el proximo chat pueda continuar sin depender de memoria conversacional.

## Leer antes
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/STATUS.md`
3. `.apos/HANDOFF.md`
4. `.apos/PLAN.md`
5. `.apos/RISKS.md`
6. `.apos/OPEN_QUESTIONS.md`

Si faltan, reportar que el proyecto necesita `/apos`.

## Actualizar archivos vivos
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/QUALITY.md` si hubo validacion.
- `.apos/RISKS.md` si cambio un riesgo.
- `.apos/OPEN_QUESTIONS.md` si cambio una incertidumbre.

## Append-only
Agregar entradas nuevas, nunca reescribir historia:
- `.apos/JOURNAL.md` siempre.
- `.apos/DECISIONS.md` si hubo decision real.
- `.apos/SOURCES.md` si hubo fuente nueva.
- `.apos/RESEARCH_LOG.md` si hubo investigacion cerrada.

## Clasificacion obligatoria
Separar:
- hecho verificado
- decision
- inferencia
- pendiente
- riesgo
- desconocido

## Cierre
Responder con:
- archivos actualizados
- evidencia/comandos relevantes
- proxima accion recomendada
- que no tocar todavia

## Sincronizacion laptop por Git
Cada vez que el usuario invoque `/guardar`, ademas del guardado APOS normal, preparar contexto para la laptop.

### Objetivo
Que la laptop pueda hacer `git pull` y recuperar un resumen inteligente del estado de la WS sin depender del chat.

### Paso obligatorio
Ejecutar:

```powershell
python scripts\apos_prepare_laptop_sync.py
```

Esto genera o actualiza:

```text
.apos/LAPTOP_SYNC.md
```

El archivo debe resumir:
- estado APOS;
- handoff;
- plan;
- riesgos;
- preguntas abiertas;
- estado de simulaciones si existe `data/production_status.json`;
- exports livianos recientes;
- estado Git;
- advertencias sobre archivos runtime no sincronizados.

### Commit/push seguro
Despues de generar `.apos/LAPTOP_SYNC.md`, si el usuario no pidio lo contrario, sincronizar por Git solo archivos livianos:

```powershell
git add .apos scripts\apos_prepare_laptop_sync.py .agents\skills\guardar\SKILL.md
git status
git commit -m "Update APOS laptop sync context"
git push
```

Si durante la sesion se crearon exports livianos, docs, configs o scripts relevantes, agregarlos explicitamente:

```powershell
git add exports docs config scripts .agents .apos
```

### No subir automaticamente
No agregar a ciegas:
- `cases/`;
- `data/processed/`;
- `*_out/`;
- `Part*`;
- `.bi4`, `.ibi4`, `.vtk`;
- logs runtime grandes;
- `data/results.sqlite` si hay una simulacion activa o el lote no esta cerrado.

Si `data/results.sqlite` aparece modificado mientras corre una simulacion, reportarlo como runtime vivo y dejarlo fuera del commit.

### Mensaje final adicional
Al cerrar `/guardar`, incluir:
- si `.apos/LAPTOP_SYNC.md` fue actualizado;
- commit y push realizados, si aplica;
- que debe hacer la laptop: `git pull` y leer `.apos/LAPTOP_SYNC.md`;
- cualquier archivo que quedo local por seguridad.
