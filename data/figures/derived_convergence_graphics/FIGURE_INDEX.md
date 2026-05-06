# Derived Convergence Graphics

Fuente: archivos locales `data/results/conv_edge_*.csv`, `conv_reassure_*.csv`, `conv_repeat_*.csv`, `conv_probe_*.csv`, `data/results.sqlite` y `conv_edge_*_gci.json`.

No se usaron binarios pesados ni se corrieron simulaciones nuevas.

## Dataset

- Filas tabla maestra: 27
- Familias: conv_edge, conv_probe, conv_reassure, conv_repeat
- Alcances de evidencia: frontier_refinement, principal_frontier, repeatability_check, supplemental_fine_probe
- Modos de criterio: displacement_only
- GCI JSON disponibles: 4 prefixes conv_edge
- Umbral desplazamiento: 5.0% d_eq = 5.021 mm

## Figuras esenciales

### 01_mu_vs_disp_pct_by_dp
- PNG: `data\figures\derived_convergence_graphics\01_mu_vs_disp_pct_by_dp.png`
- SVG: `data\figures\derived_convergence_graphics\01_mu_vs_disp_pct_by_dp.svg`
- Que muestra: mu versus desplazamiento relativo, con umbral 5% d_eq
- Por que importa: Es la figura base para ubicar FALLO/ESTABLE bajo displacement_only.
- Advertencia: Ninguna especifica.

### 02_mu_vs_disp_mm_by_dp
- PNG: `data\figures\derived_convergence_graphics\02_mu_vs_disp_mm_by_dp.png`
- SVG: `data\figures\derived_convergence_graphics\02_mu_vs_disp_mm_by_dp.svg`
- Que muestra: mu versus desplazamiento en mm, con umbral fisico
- Por que importa: Traduce el criterio porcentual a una magnitud medible.
- Advertencia: Ninguna especifica.

### 03_class_by_mu_dp
- PNG: `data\figures\derived_convergence_graphics\03_class_by_mu_dp.png`
- SVG: `data\figures\derived_convergence_graphics\03_class_by_mu_dp.svg`
- Que muestra: Clase ESTABLE/FALLO para cada mu y dp
- Por que importa: Muestra directamente la frontera practica sin convertirla en curva suave.
- Advertencia: Ninguna especifica.

### 04_heatmap_class_mu_dp
- PNG: `data\figures\derived_convergence_graphics\04_heatmap_class_mu_dp.png`
- SVG: `data\figures\derived_convergence_graphics\04_heatmap_class_mu_dp.svg`
- Que muestra: Heatmap mu x dp con clase displacement_only
- Por que importa: Condensa la frontera y evidencia la sensibilidad por resolucion.
- Advertencia: Ninguna especifica.

### 06_zoom_fine_dp003_dp002
- PNG: `data\figures\derived_convergence_graphics\06_zoom_fine_dp003_dp002.png`
- SVG: `data\figures\derived_convergence_graphics\06_zoom_fine_dp003_dp002.svg`
- Que muestra: Solo mallas finas en el rango de frontera
- Por que importa: Muestra que dp=0.002 reduce desplazamiento y cambia la transicion aparente.
- Advertencia: Ninguna especifica.

### 07_bracket_dp003_fine
- PNG: `data\figures\derived_convergence_graphics\07_bracket_dp003_fine.png`
- SVG: `data\figures\derived_convergence_graphics\07_bracket_dp003_fine.svg`
- Que muestra: Bracket 0.68050-0.68075 para dp=0.003
- Por que importa: Figura directa para defender la frontera practica en la malla dp=0.003.
- Advertencia: Ninguna especifica.

### 17_edge_vs_repeat_side_by_side
- PNG: `data\figures\derived_convergence_graphics\17_edge_vs_repeat_side_by_side.png`
- SVG: `data\figures\derived_convergence_graphics\17_edge_vs_repeat_side_by_side.svg`
- Que muestra: Comparacion lado a lado entre corrida edge y repeticion
- Por que importa: Verifica consistencia operativa de los casos marginales repetidos.
- Advertencia: Ninguna especifica.

### 23_cost_vs_practical_precision_panel
- PNG: `data\figures\derived_convergence_graphics\23_cost_vs_practical_precision_panel.png`
- SVG: `data\figures\derived_convergence_graphics\23_cost_vs_practical_precision_panel.svg`
- Que muestra: Panel costo frente a desplazamiento y margen al umbral
- Por que importa: Conecta el argumento metodologico con el costo computacional.
- Advertencia: El margen pequeno no implica mayor precision si la respuesta es oscilatoria.

### 25_summary_practical_frontier
- PNG: `data\figures\derived_convergence_graphics\25_summary_practical_frontier.png`
- SVG: `data\figures\derived_convergence_graphics\25_summary_practical_frontier.svg`
- Que muestra: Resumen principal de frontera y rotacion diagnostica
- Por que importa: Es la figura integradora mas defendible para tesis/presentacion.
- Advertencia: Ninguna especifica.

### 26_summary_resolution_sensitivity
- PNG: `data\figures\derived_convergence_graphics\26_summary_resolution_sensitivity.png`
- SVG: `data\figures\derived_convergence_graphics\26_summary_resolution_sensitivity.svg`
- Que muestra: Panel de sensibilidad por resolucion en metricas principales
- Por que importa: Muestra honestamente la no monotonia y el cambio al refinar.
- Advertencia: No debe presentarse como prueba de convergencia asintotica.

### 27_summary_refinement_cost
- PNG: `data\figures\derived_convergence_graphics\27_summary_refinement_cost.png`
- SVG: `data\figures\derived_convergence_graphics\27_summary_refinement_cost.svg`
- Que muestra: Costo de refinamiento de malla
- Por que importa: Cuantifica la diferencia practica entre dp=0.003 y dp=0.002.
- Advertencia: Ninguna especifica.

### 28_rotation_diagnostic_vs_displacement_only
- PNG: `data\figures\derived_convergence_graphics\28_rotation_diagnostic_vs_displacement_only.png`
- SVG: `data\figures\derived_convergence_graphics\28_rotation_diagnostic_vs_displacement_only.svg`
- Que muestra: Rotacion frente a desplazamiento y clase final
- Por que importa: Aclara que la rotacion no gobierna la clase en displacement_only.
- Advertencia: Ninguna especifica.

## Figuras de apoyo y suplementarias

### 05_displacement_margin_mu_by_dp (support)
- PNG: `data\figures\derived_convergence_graphics\05_displacement_margin_mu_by_dp.png`
- SVG: `data\figures\derived_convergence_graphics\05_displacement_margin_mu_by_dp.svg`
- Que muestra: Margen positivo/negativo respecto del umbral de desplazamiento
- Por que importa: Hace visible cuan marginales son los casos cerca del 5% d_eq.
- Advertencia: Ninguna especifica.

### 08_dp_vs_disp_pct_by_mu (support)
- PNG: `data\figures\derived_convergence_graphics\08_dp_vs_disp_pct_by_mu.png`
- SVG: `data\figures\derived_convergence_graphics\08_dp_vs_disp_pct_by_mu.svg`
- Que muestra: Resolucion versus Desplazamiento [% d_eq]
- Por que importa: Usa solo conv_edge para no mezclar corridas de una sola malla.
- Advertencia: No interpretar como convergencia asintotica si la tendencia es oscilatoria.

### 09_dp_vs_displacement_m_by_mu (support)
- PNG: `data\figures\derived_convergence_graphics\09_dp_vs_displacement_m_by_mu.png`
- SVG: `data\figures\derived_convergence_graphics\09_dp_vs_displacement_m_by_mu.svg`
- Que muestra: Resolucion versus Desplazamiento [m]
- Por que importa: Usa solo conv_edge para no mezclar corridas de una sola malla.
- Advertencia: No interpretar como convergencia asintotica si la tendencia es oscilatoria.

### 10_dp_vs_rotation_by_mu (support)
- PNG: `data\figures\derived_convergence_graphics\10_dp_vs_rotation_by_mu.png`
- SVG: `data\figures\derived_convergence_graphics\10_dp_vs_rotation_by_mu.svg`
- Que muestra: Resolucion versus Rotacion [deg]
- Por que importa: Usa solo conv_edge para no mezclar corridas de una sola malla.
- Advertencia: No interpretar como convergencia asintotica si la tendencia es oscilatoria.

### 11_dp_vs_velocity_by_mu (support)
- PNG: `data\figures\derived_convergence_graphics\11_dp_vs_velocity_by_mu.png`
- SVG: `data\figures\derived_convergence_graphics\11_dp_vs_velocity_by_mu.svg`
- Que muestra: Resolucion versus Velocidad [m/s]
- Por que importa: Usa solo conv_edge para no mezclar corridas de una sola malla.
- Advertencia: No interpretar como convergencia asintotica si la tendencia es oscilatoria.

### 12_dp_vs_sph_force_by_mu (support)
- PNG: `data\figures\derived_convergence_graphics\12_dp_vs_sph_force_by_mu.png`
- SVG: `data\figures\derived_convergence_graphics\12_dp_vs_sph_force_by_mu.svg`
- Que muestra: Resolucion versus Fuerza SPH [N]
- Por que importa: Usa solo conv_edge para no mezclar corridas de una sola malla.
- Advertencia: No interpretar como convergencia asintotica si la tendencia es oscilatoria.

### 13_relative_change_displacement (supplementary)
- PNG: `data\figures\derived_convergence_graphics\13_relative_change_displacement.png`
- SVG: `data\figures\derived_convergence_graphics\13_relative_change_displacement.svg`
- Que muestra: Cambio relativo de disp_pct_deq entre dp consecutivos
- Por que importa: Sirve como diagnostico de sensibilidad, no como prueba formal de convergencia.
- Advertencia: Comportamiento oscilatorio en algunos casos.

### 14_relative_change_rotation (supplementary)
- PNG: `data\figures\derived_convergence_graphics\14_relative_change_rotation.png`
- SVG: `data\figures\derived_convergence_graphics\14_relative_change_rotation.svg`
- Que muestra: Cambio relativo de max_rotation_deg entre dp consecutivos
- Por que importa: Sirve como diagnostico de sensibilidad, no como prueba formal de convergencia.
- Advertencia: Comportamiento oscilatorio en algunos casos.

### 15_relative_change_velocity (supplementary)
- PNG: `data\figures\derived_convergence_graphics\15_relative_change_velocity.png`
- SVG: `data\figures\derived_convergence_graphics\15_relative_change_velocity.svg`
- Que muestra: Cambio relativo de max_velocity_ms entre dp consecutivos
- Por que importa: Sirve como diagnostico de sensibilidad, no como prueba formal de convergencia.
- Advertencia: Comportamiento oscilatorio en algunos casos.

### 16_relative_change_sph_force (supplementary)
- PNG: `data\figures\derived_convergence_graphics\16_relative_change_sph_force.png`
- SVG: `data\figures\derived_convergence_graphics\16_relative_change_sph_force.svg`
- Que muestra: Cambio relativo de max_sph_force_N entre dp consecutivos
- Por que importa: Sirve como diagnostico de sensibilidad, no como prueba formal de convergencia.
- Advertencia: Comportamiento oscilatorio en algunos casos.

### 18_marginal_repeats_highlight (support)
- PNG: `data\figures\derived_convergence_graphics\18_marginal_repeats_highlight.png`
- SVG: `data\figures\derived_convergence_graphics\18_marginal_repeats_highlight.svg`
- Que muestra: Puntos repetidos marginales con su clase
- Por que importa: Resalta que las repeticiones conservan el patron de clase.
- Advertencia: Ninguna especifica.

### 19_repeat_dumbbell (support)
- PNG: `data\figures\derived_convergence_graphics\19_repeat_dumbbell.png`
- SVG: `data\figures\derived_convergence_graphics\19_repeat_dumbbell.svg`
- Que muestra: Distancia entre corrida original y repeticion en casos marginales
- Por que importa: Hace visible la reproducibilidad numerica reportada.
- Advertencia: Ninguna especifica.

### 20_dp_vs_time_min (support)
- PNG: `data\figures\derived_convergence_graphics\20_dp_vs_time_min.png`
- SVG: `data\figures\derived_convergence_graphics\20_dp_vs_time_min.svg`
- Que muestra: Costo computacional: Tiempo [min]
- Por que importa: Cuantifica el precio de refinar la malla.
- Advertencia: Ninguna especifica.

### 21_dp_vs_n_particles (support)
- PNG: `data\figures\derived_convergence_graphics\21_dp_vs_n_particles.png`
- SVG: `data\figures\derived_convergence_graphics\21_dp_vs_n_particles.svg`
- Que muestra: Costo computacional: Numero de particulas
- Por que importa: Cuantifica el precio de refinar la malla.
- Advertencia: Ninguna especifica.

### 22_dp_vs_mem_gpu (support)
- PNG: `data\figures\derived_convergence_graphics\22_dp_vs_mem_gpu.png`
- SVG: `data\figures\derived_convergence_graphics\22_dp_vs_mem_gpu.svg`
- Que muestra: Costo computacional: Memoria GPU [MB]
- Por que importa: Cuantifica el precio de refinar la malla.
- Advertencia: Ninguna especifica.

### 24_displacement_margin_vs_cost (support)
- PNG: `data\figures\derived_convergence_graphics\24_displacement_margin_vs_cost.png`
- SVG: `data\figures\derived_convergence_graphics\24_displacement_margin_vs_cost.svg`
- Que muestra: Margen al umbral frente al tiempo de corrida
- Por que importa: Ayuda a discutir si el costo adicional cambia la decision practica.
- Advertencia: Ninguna especifica.

### 30_dp002_probe_context (support)
- PNG: `data\figures\derived_convergence_graphics\30_dp002_probe_context.png`
- SVG: `data\figures\derived_convergence_graphics\30_dp002_probe_context.svg`
- Que muestra: Contexto del probe conv_probe_dp002_f06625 dentro de dp=0.002
- Por que importa: Documenta que el probe fino es evidencia suplementaria y no bracket principal.
- Advertencia: No usar este punto para redefinir la frontera principal dp=0.003.

### 29_gci_available_edge_only (supplementary)
- PNG: `data\figures\derived_convergence_graphics\29_gci_available_edge_only.png`
- SVG: `data\figures\derived_convergence_graphics\29_gci_available_edge_only.svg`
- Que muestra: GCI fine por caso y metrica donde existe JSON
- Por que importa: Documenta que el GCI no respalda una convergencia fuerte general.
- Advertencia: No hay GCI JSON para conv_reassure ni conv_repeat.
