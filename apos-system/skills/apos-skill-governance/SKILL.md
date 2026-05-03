---
name: apos-skill-governance
description: Gobierno APOS de skills. Decide crear, actualizar, documentar en APOS, preguntar o no crear skill. Nunca modifica global/system sin backup, auditoria y confirmacion.
---

# apos-skill-governance

Gates:
1. Si es memoria de proyecto, usar APOS y no skill global.
2. Si existe skill similar, actualizar o proponer merge.
3. Si toca global, `.system`, hooks o config, pedir confirmacion.
4. Crear skill solo si reduce error repetido o encapsula workflow real.

Decisiones posibles:
- NO CREAR SKILL
- CREAR NOTA APOS
- ACTUALIZAR SKILL EXISTENTE
- CREAR SKILL NUEVA
- PROPONER Y PREGUNTAR
