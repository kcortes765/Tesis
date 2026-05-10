# Analisis de bloques STL - b02_variantes_20260510

## Ubicacion

- STL extraidos en: `models\bloques\b02_variantes_20260510`
- Metricas fisicas escaladas: `data\geometry\bloques_b02_20260510\stl_metrics_physical_scaled.csv`
- Metricas relativas: `data\geometry\bloques_b02_20260510\stl_metrics_physical_scaled_with_relative.csv`
- Figura: `data\geometry\bloques_b02_20260510\shape_space_b02_scaled.png`

## Nota de unidades

Los STL vienen en unidades internas. El pipeline actual los usa con `drawscale=0.04` en el XML de DualSPHysics. Por eso las metricas fisicas de este informe aplican escala 0.04. El bloque activo `models/BLIR3.stl` es identico por SHA256 a `b02_Original.stl`.

## Resumen cuantitativo fisico

- Numero de STL: 10.
- Todos watertight: True.
- Rango de volumen escalado: 0.000529987 a 0.000530372 m3.
- Rango de diametro equivalente escalado: 0.1004 a 0.1004 m.
- Rango L/B: 1.01 a 1.27.
- Rango T/B: 0.18 a 0.37.
- Rango de solidez volumen/convex hull: 0.83 a 0.98.
- Rango de fraccion de huella inferior estimada: 0.062 a 0.983.

## Lectura de cobertura

- Las 10 geometrias no cubren diez bloques independientes: son una familia `b02` con volumen y `d_eq` casi constantes.
- La variacion principal es morfologica: el bloque original es mas extendido/plano; las reducciones son mas compactas, con mayor espesor relativo y mayor solidez.
- Esta familia sirve para sensibilidad de forma cercana alrededor de una misma escala fisica, no para declarar un dominio amplio de bloques costeros.
- Las bases son operativamente planas o con banda inferior de apoyo. Eso ayuda a controlar el contacto, pero puede subrepresentar apoyos naturales sobre pocos puntos, trabamiento y rocking.

## Tabla resumida

| file | triangles | watertight | volume_m3_scaled | d_eq_m_scaled | obb_L_m_scaled | obb_B_m_scaled | obb_T_m_scaled | aspect_L_over_B | aspect_T_over_B | sphericity | solidity_volume_over_convex_hull | bottom_band_fraction_xy | bottom_band_z_range_m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b02_Original.stl | 2392 | True | 0.0005302 | 0.1004 | 0.2557 | 0.2544 | 0.04588 | 1.005 | 0.1804 | 0.622 | 0.831 | 0.06224 | 0.001982 |
| b02_Reduccion_1.stl | 1974 | True | 0.0005304 | 0.1004 | 0.2 | 0.1656 | 0.04345 | 1.208 | 0.2624 | 0.6273 | 0.8511 | 0.1816 | 0.001949 |
| b02_Reduccion_2.stl | 2116 | True | 0.00053 | 0.1004 | 0.1939 | 0.1585 | 0.0479 | 1.223 | 0.3021 | 0.6307 | 0.8561 | 0.1968 | 0.001995 |
| b02_Reduccion_3.stl | 2302 | True | 0.0005303 | 0.1004 | 0.1928 | 0.1518 | 0.04747 | 1.269 | 0.3126 | 0.627 | 0.855 | 0.1195 | 0.001993 |
| b02_Reduccion_4.stl | 1846 | True | 0.0005301 | 0.1004 | 0.1793 | 0.1466 | 0.04737 | 1.223 | 0.3231 | 0.6328 | 0.8615 | 0.5195 | 0.001994 |
| b02_Reduccion_5.stl | 1522 | True | 0.0005301 | 0.1004 | 0.1696 | 0.1373 | 0.04222 | 1.236 | 0.3076 | 0.6283 | 0.8858 | 0.7288 | 0.001991 |
| b02_Reduccion_6.stl | 2520 | True | 0.00053 | 0.1004 | 0.1584 | 0.129 | 0.04033 | 1.228 | 0.3126 | 0.6403 | 0.8998 | 0.7773 | 0.001983 |
| b02_Reduccion_7.stl | 1970 | True | 0.0005302 | 0.1004 | 0.1466 | 0.1196 | 0.04043 | 1.226 | 0.3382 | 0.6685 | 0.9434 | 0.9168 | 0.001996 |
| b02_Reduccion_8.stl | 1754 | True | 0.00053 | 0.1004 | 0.1386 | 0.1134 | 0.04078 | 1.222 | 0.3596 | 0.6686 | 0.9673 | 0.9738 | 0.001997 |
| b02_Reduccion_9.stl | 2206 | True | 0.00053 | 0.1004 | 0.1342 | 0.1096 | 0.04048 | 1.224 | 0.3692 | 0.6855 | 0.9799 | 0.9827 | 0.001604 |

## Recomendacion metodologica

1. Mantener `BLIR3.stl`/`b02_Original.stl` como geometria base ya verificada.
2. Elegir 2-3 representantes de esta familia para sensibilidad de forma cercana: por ejemplo original, una reduccion intermedia y una reduccion compacta.
3. Si se quiere cubrir un dominio de formas, generar una familia adicional con parametros controlados: elongacion L/B, espesor T/B, angularidad/solidez, rugosidad inferior y condicion de apoyo.
4. No codificar un `mu` especifico en la geometria. `mu` debe quedar como parametro de contacto Chrono; la geometria inferior debe tratarse como otra variable fisica distinta.
5. Para cada STL nuevo se debe recalcular volumen, centro de masa, masa, tensor de inercia, escala, posicion de insercion y sanity test de contacto antes de produccion.
