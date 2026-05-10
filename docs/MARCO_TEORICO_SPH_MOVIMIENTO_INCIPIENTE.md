# Marco teorico: simulacion SPH de movimiento incipiente de bloques costeros

## 1. Introduccion

El transporte de bloques costeros por eventos extremos, como tsunamis o marejadas severas, es un problema relevante para la ingenieria costera, la geomorfologia litoral y la evaluacion de peligro. Los bloques de gran tamano encontrados en plataformas rocosas, playas elevadas o zonas de inundacion pueden actuar como evidencia fisica de eventos de alta energia. Sin embargo, inferir las condiciones hidrodinamicas que permitieron su movilizacion no es directo, porque el movimiento depende simultaneamente de la forma del bloque, su masa, el contacto con el fondo, la pendiente local, la rugosidad, la friccion, la duracion del flujo y la historia temporal de las fuerzas aplicadas.

En este contexto, la tesis aborda el movimiento incipiente de un bloque costero bajo un flujo tipo tsunami. El interes principal no es simular el transporte largo posterior al inicio del movimiento, sino identificar las condiciones bajo las cuales un bloque inicialmente en reposo comienza a desplazarse. Este enfoque requiere representar de manera razonable la superficie libre del flujo, la interaccion fluido-solido, el contacto bloque-playa y la transicion entre estabilidad y movimiento. Para ello se utiliza el metodo SPH (Smoothed Particle Hydrodynamics), implementado en DualSPHysics, acoplado con Chrono para la dinamica de cuerpos rigidos.

El presente marco teorico organiza los fundamentos fisicos y numericos necesarios para interpretar esta aproximacion. Primero se revisa el problema de bloques costeros y movimiento incipiente; luego se describen los conceptos basicos de flujos con superficie libre y simulacion CFD; posteriormente se desarrolla el metodo SPH, su formulacion conceptual, ventajas y limitaciones; finalmente se explica el acoplamiento fluido-solido y su relacion con la decision metodologica de la tesis.

## 2. Bloques costeros y transporte por eventos extremos

Los depositos de bloques costeros se asocian a procesos de alta energia capaces de extraer, levantar, deslizar, rotar o transportar clastos de gran tamano. En la literatura se ha discutido ampliamente si ciertos depositos fueron originados por tsunamis, marejadas extremas u oleaje de tormenta. Esta distincion es importante porque la presencia de bloques de gran volumen puede usarse como indicador paleohidrodinamico, pero las ecuaciones simplificadas para estimar alturas o velocidades de flujo suelen depender de supuestos fuertes sobre la geometria del bloque, el modo de transporte y la distribucion temporal de cargas.

El transporte de un bloque no depende solo de la magnitud maxima de la ola o del flujo. Tambien influyen la orientacion del bloque, el area expuesta, el brazo de momento respecto del punto de apoyo, la densidad relativa bloque-agua, el coeficiente de friccion con el sustrato y la rugosidad de la superficie de contacto. Por esta razon, dos bloques con volumen similar pueden tener respuestas distintas si cambian su forma, apoyo, orientacion o condicion inicial.

Desde el punto de vista mecanico, el inicio de movimiento puede ocurrir por distintos modos:

- **Deslizamiento:** el bloque supera la resistencia friccional y comienza a moverse sobre la superficie de apoyo.
- **Volcamiento o rotacion:** el momento hidrodinamico supera el momento resistente asociado al peso y la geometria de apoyo.
- **Saltacion o levantamiento:** el bloque pierde contacto significativo con el fondo y se desplaza de forma intermitente.
- **Rocking:** el bloque oscila o rota parcialmente sin necesariamente experimentar transporte neto significativo.

La tesis se concentra en el **movimiento incipiente**, entendido como el paso desde una condicion inicialmente estable hacia una condicion con desplazamiento medible. Esta definicion es mas acotada que el transporte completo, pero es especialmente util para construir fronteras de estabilidad en funcion de parametros fisicos, como altura de columna de agua, masa, orientacion, pendiente y friccion.

## 3. Movimiento incipiente y equilibrio de fuerzas

El movimiento incipiente se produce cuando las acciones hidrodinamicas superan las resistencias mecanicas del bloque. En forma simplificada, el bloque esta sometido a peso, empuje, fuerza de arrastre, presion hidrodinamica, fuerzas de contacto, normal y friccion. Si el flujo es suficientemente intenso, estas acciones pueden generar traslacion, rotacion o ambas.

Una lectura clasica del problema considera un balance entre fuerzas impulsoras y resistentes. Para deslizamiento, la resistencia principal suele aproximarse mediante una relacion friccional:

```text
F_resistente ~= mu * N
```

donde `mu` es el coeficiente de friccion y `N` es la fuerza normal efectiva. El movimiento por deslizamiento se vuelve posible cuando la componente horizontal de la fuerza hidrodinamica supera esa resistencia. Para rotacion o volcamiento, el criterio se expresa mejor como balance de momentos respecto a un punto o arista de apoyo.

Sin embargo, en flujos tipo tsunami la carga no es necesariamente estacionaria. El frente de agua puede generar impacto, incremento brusco de presion, variaciones de empuje, cambios en la fuerza normal y oscilaciones del bloque. Por ello, una formulacion puramente cuasiestatica puede no capturar toda la historia temporal del inicio de movimiento. La simulacion numerica permite observar directamente la evolucion temporal de posicion, velocidad, rotacion y fuerzas sobre el bloque.

En esta tesis, el criterio operativo de movimiento incipiente se basa en el desplazamiento del centro de masa. La rotacion se considera una variable diagnostica, porque un bloque puede experimentar rocking o rotacion acumulada sin presentar transporte neto suficiente para clasificarlo como movilizado. Esta distincion evita confundir oscilaciones locales con desplazamiento efectivo.

## 4. Flujos con superficie libre y desafios numericos

Un flujo tipo tsunami en zona costera puede incluir propagacion sobre pendiente, frente de inundacion, superficie libre altamente deformable, impacto contra obstaculos, cambios rapidos de profundidad, turbulencia local y zonas de secado y mojado. Estos fenomenos son numericamente exigentes, especialmente cuando se busca resolver la interaccion con un cuerpo solido movil.

Los metodos CFD tradicionales de malla, como volumenes finitos o elementos finitos, suelen representar el dominio mediante celdas fijas o deformables. Estos metodos son muy potentes y ampliamente usados, pero en problemas con superficie libre muy deformada, rompimiento, salpicaduras o contacto con solidos moviles pueden requerir tratamientos adicionales para rastrear la interfaz agua-aire, manejar deformaciones de malla o resolver regiones de secado y mojado.

SPH ofrece una alternativa lagrangiana y sin malla. En lugar de describir el flujo sobre una grilla fija, el fluido se representa mediante particulas que se mueven con el campo de velocidad. Esta caracteristica vuelve al metodo atractivo para problemas con grandes deformaciones, superficie libre y geometria movil.

## 5. Fundamentos del metodo SPH

SPH, o Smoothed Particle Hydrodynamics, es un metodo numerico de particulas desarrollado originalmente para problemas de astrofisica por Lucy (1977) y Gingold y Monaghan (1977). Posteriormente fue extendido a problemas de mecanica de fluidos, hidraulica, oleaje, impacto, geotecnia, solidos y flujos multifasicos. Su idea central es aproximar un campo continuo mediante una suma ponderada sobre particulas vecinas.

En SPH, cada particula representa un volumen discreto de fluido y transporta propiedades como masa, posicion, velocidad, densidad y presion. Una variable continua `A(r)` puede aproximarse mediante una interpolacion integral usando una funcion kernel `W`:

```text
A(r) ~= integral A(r') W(r-r', h) dr'
```

Al discretizar el dominio en particulas, esta aproximacion se escribe como una suma:

```text
A_i ~= sum_j m_j * (A_j / rho_j) * W(r_i - r_j, h)
```

donde `i` es la particula evaluada, `j` representa las particulas vecinas, `m_j` es la masa de la particula vecina, `rho_j` su densidad, `W` es el kernel de suavizado y `h` es la longitud de suavizado. En terminos fisicos, el valor de una propiedad en una particula se obtiene a partir de sus vecinas, ponderando mas a las particulas cercanas y menos a las lejanas.

La funcion kernel cumple un rol central. Debe ser suave, compacta, positiva y normalizada. Su radio de influencia determina cuantas particulas contribuyen a la aproximacion local. Si el soporte es demasiado pequeno, la estimacion puede ser ruidosa; si es demasiado grande, el campo puede quedar excesivamente suavizado.

## 6. Formulacion fisica en SPH

Las ecuaciones de gobierno para un fluido se basan en conservacion de masa y cantidad de movimiento. En una forma lagrangiana, el movimiento de las particulas sigue la velocidad del fluido, mientras la densidad y la velocidad cambian por interacciones con particulas vecinas y fuerzas externas.

En SPH debilmente compresible, usado frecuentemente en problemas de superficie libre, la presion se obtiene mediante una ecuacion de estado que relaciona densidad y presion. El fluido se permite ligeramente compresible para evitar resolver una ecuacion de Poisson de presion en cada paso. Esta aproximacion exige controlar que las variaciones de densidad se mantengan pequenas y que la velocidad del sonido numerica sea suficientemente alta en relacion con la velocidad del flujo.

La ecuacion de cantidad de movimiento incluye contribuciones de presion, viscosidad, gravedad y terminos numericos de estabilizacion. Conceptualmente, las particulas se aceleran cuando existen gradientes de presion, diferencias de velocidad con sus vecinas o fuerzas externas. En problemas de oleaje e inundacion costera, la gravedad es esencial para reproducir la propagacion, el run-up y el avance del frente libre.

La viscosidad puede representarse mediante modelos fisicos o terminos numericos, dependiendo de la formulacion implementada. En aplicaciones ingenieriles, el objetivo no siempre es resolver todas las escalas turbulentas, sino capturar de manera robusta las fuerzas globales y la dinamica relevante del fenomeno.

## 7. Superficie libre en SPH

Una de las principales ventajas de SPH es su tratamiento natural de la superficie libre. Como las particulas se mueven con el flujo, la interfaz agua-aire emerge de la distribucion de particulas sin necesidad de una malla que se deforme o de un algoritmo explicito de captura de interfaz.

Esto resulta especialmente util en problemas donde el frente de agua se rompe, salpica o interactua con geometria compleja. En el caso de un flujo tipo tsunami sobre una playa, el frente puede avanzar sobre una pendiente, generar impacto sobre el bloque y producir zonas de flujo poco profundas. SPH permite representar estas configuraciones con menor dependencia de tecnicas de remallado o seguimiento de superficie.

Sin embargo, esta ventaja tiene costos. La precision depende de la resolucion espacial, de la calidad de la distribucion de particulas, del tratamiento de fronteras y de los parametros numericos. Ademas, la superficie libre puede presentar ruido numerico si la resolucion es insuficiente o si las condiciones de borde no estan bien configuradas.

## 8. Condiciones de borde y geometria solida

La representacion de fronteras es un aspecto critico en SPH. Las paredes, fondos y obstaculos deben impedir la penetracion de particulas de fluido y transmitir adecuadamente las fuerzas. En la practica, los solidos pueden representarse mediante particulas de frontera, geometria discretizada o formulaciones especiales de contorno.

En la tesis, la geometria relevante incluye un canal, una playa inclinada y un bloque rigido. La condicion inicial del bloque es especialmente importante porque pequenas diferencias en apoyo, orientacion o penetracion inicial pueden cambiar la respuesta cerca del umbral de movimiento. Por ello, el bloque se posiciona alineado con la pendiente y apoyado sobre la playa, evitando que una configuracion geometrica artificial contamine la lectura de estabilidad.

El tratamiento de frontera tambien afecta las fuerzas hidrodinamicas. Una resolucion gruesa puede modificar localmente la forma del frente de agua, la distribucion de presion y la interaccion con el cuerpo rigido. Por esta razon, la convergencia practica debe evaluarse cerca del caso fisicamente relevante, no solo en una configuracion generica.

## 9. Interaccion fluido-estructura y cuerpos rigidos

La interaccion fluido-estructura ocurre cuando el flujo ejerce fuerzas sobre un cuerpo y el cuerpo responde con movimiento, rotacion o deformacion. En esta tesis el bloque se considera un cuerpo rigido, por lo que no se modela deformacion interna, sino traslacion, rotacion y contacto con la playa.

DualSPHysics permite acoplar el solver SPH con Chrono, una biblioteca de dinamica multibody. En este acoplamiento, el fluido calcula las acciones hidrodinamicas sobre el cuerpo, mientras Chrono resuelve la dinamica del solido, incluyendo contacto, friccion y rotacion. La respuesta actualizada del cuerpo vuelve al solver SPH, cerrando el acoplamiento en el tiempo.

Este enfoque es adecuado para el problema de bloques costeros porque el inicio de movimiento depende de la competencia entre fuerza hidrodinamica, peso, normal, friccion y momento. El uso de un motor de cuerpos rigidos evita reducir el problema a una ecuacion estatica unica y permite observar directamente si el bloque se desplaza, rota o solo oscila.

## 10. DualSPHysics como herramienta numerica

DualSPHysics es un solver SPH orientado a problemas de superficie libre y aplicaciones ingenieriles. Esta desarrollado en C++/CUDA/OpenMP y aprovecha GPU para simular casos con gran cantidad de particulas. Su uso es frecuente en problemas de hidraulica, oleaje, impacto de agua, estructuras costeras y acoplamientos multiphysica.

Para esta tesis, DualSPHysics aporta tres elementos principales:

1. Permite representar un flujo con superficie libre y avance sobre pendiente sin malla fija.
2. Permite resolver interaccion con geometria solida y cuerpo rigido.
3. Permite usar GPU para casos de alta resolucion que serian muy costosos en CPU.

El uso de DualSPHysics no elimina la necesidad de verificacion. Al contrario, exige controlar resolucion, parametros numericos, condiciones iniciales, tratamiento de fronteras y criterios de clasificacion. La confiabilidad del resultado depende tanto del metodo como de la calidad de su configuracion.

## 11. Resolucion, convergencia y costo computacional

En SPH, la resolucion espacial se controla principalmente mediante `dp`, el espaciamiento inicial entre particulas. Al disminuir `dp`, aumenta el numero de particulas y se resuelven mejor las variaciones espaciales del flujo y la geometria. Sin embargo, el costo computacional crece rapidamente, aproximadamente con el volumen dividido por `dp^3`.

Por esta razon, una malla mas fina no siempre es viable ni necesariamente proporcional al objetivo cientifico. En problemas de frontera de estabilidad, refinar la malla puede cambiar la clasificacion de casos marginales, porque el movimiento incipiente es una respuesta de umbral. Pequenas diferencias en presion, contacto, fuerza normal o rocking pueden desplazar la frontera aparente.

La convergencia numerica puede entenderse de dos maneras:

- **Convergencia asintotica fuerte:** el resultado tiende de forma clara a un valor unico al refinar progresivamente la malla.
- **Convergencia practica:** la resolucion es suficientemente robusta para tomar una decision metodologica y avanzar con una campana productiva, reconociendo la incertidumbre y sensibilidad residual.

En esta tesis, el objetivo es cerrar una convergencia practica defendible para una campana parametrica. La frontera se reporta asociada a la resolucion operativa, evitando afirmar una precision formal que los datos no sostienen. Esta postura es conservadora y coherente con la naturaleza del problema de movimiento incipiente.

## 12. Criterios de clasificacion: desplazamiento y rotacion

Un punto metodologico clave es distinguir entre desplazamiento efectivo y rotacion diagnostica. En un bloque irregular apoyado sobre una pendiente, el flujo puede inducir rocking: pequeñas oscilaciones o rotaciones acumuladas que no necesariamente implican transporte neto.

Si se usara la rotacion como criterio primario, algunos casos podrian clasificarse como fallidos aunque el centro de masa permanezca bajo el umbral de desplazamiento. Para una pregunta centrada en movimiento incipiente por transporte, esto puede sobreestimar la falla. Por ello, la tesis usa el desplazamiento del centro de masa como criterio principal y reporta la rotacion como informacion adicional sobre la dinamica del bloque.

El umbral de desplazamiento se expresa como porcentaje del diametro equivalente `d_eq`, lo que normaliza el movimiento respecto del tamano del bloque. En el caso actual, el umbral adoptado es 5% de `d_eq`.

## 13. Pertinencia de SPH para la tesis

SPH es pertinente para esta tesis porque el problema combina superficie libre, avance sobre pendiente, impacto sobre un bloque, contacto solido-fondo y posible movimiento rigido. Estos elementos son dificiles de representar con modelos simplificados sin introducir supuestos fuertes sobre la forma temporal de la carga y el modo de movimiento.

El metodo permite observar de manera directa:

- La evolucion del frente de agua.
- La distribucion temporal de fuerzas hidrodinamicas.
- El desplazamiento del centro de masa del bloque.
- La rotacion acumulada y posible rocking.
- La influencia de parametros como friccion, masa, pendiente y orientacion.

Al mismo tiempo, la tesis debe reconocer las limitaciones del metodo. SPH requiere alta resolucion para reducir ruido numerico, es sensible al tratamiento de fronteras y puede tener alto costo computacional. Por ello, la interpretacion de resultados debe acompañarse de analisis de sensibilidad y decisiones metodologicas explicitas.

## 14. Sintesis del marco teorico

La simulacion del movimiento incipiente de bloques costeros exige una herramienta capaz de representar tanto la hidrodinamica del flujo con superficie libre como la dinamica mecanica del bloque. SPH ofrece una formulacion lagrangiana sin malla adecuada para grandes deformaciones, impacto y avance de frentes de agua. DualSPHysics implementa esta formulacion de manera eficiente en GPU, mientras Chrono permite resolver la respuesta de cuerpos rigidos y contacto.

El movimiento incipiente se interpreta como una condicion de umbral, no como una variable suave. Por esto, la convergencia debe evaluarse con cuidado: una frontera practica puede ser suficiente para una tesis parametrica si se reporta con honestidad, se distingue entre desplazamiento y rotacion, y se evita presentar como exacto un valor que depende de la resolucion.

En consecuencia, el marco teorico sustenta la eleccion de SPH + Chrono como herramienta apropiada para estudiar bloques costeros bajo flujos tipo tsunami, siempre que los resultados se interpreten como simulaciones numericas sensibles a resolucion, condiciones iniciales y criterio de movimiento.

## Referencias base

- Crespo, A. J. C., Dominguez, J. M., Rogers, B. D., Gomez-Gesteira, M., Longshaw, S., Canelas, R., Vacondio, R., Barreiro, A., & Garcia-Feal, O. (2015). DualSPHysics: Open-source parallel CFD solver based on Smoothed Particle Hydrodynamics (SPH). *Computer Physics Communications*, 187, 204-216.
- DualSPHysics Wiki. SPH formulation and DualSPHysics-Chrono coupling documentation.
- Gingold, R. A., & Monaghan, J. J. (1977). Smoothed particle hydrodynamics: theory and application to non-spherical stars. *Monthly Notices of the Royal Astronomical Society*, 181, 375-389.
- Lucy, L. B. (1977). A numerical approach to the testing of the fission hypothesis. *The Astronomical Journal*, 82, 1013-1024.
- Monaghan, J. J. (1992). Smoothed Particle Hydrodynamics. *Annual Review of Astronomy and Astrophysics*, 30, 543-574.
- Monaghan, J. J. (2012). Smoothed Particle Hydrodynamics and its diverse applications. *Annual Review of Fluid Mechanics*, 44, 323-346.
- Project Chrono / DualSPHysics-Chrono coupling literature for rigid-body and multiphysics interaction.
- Nott, J., & Bryant, E. (2003). Extreme marine inundations of coastal Western Australia. *Journal of Geology*, 111, 691-706.
- Nandasena, N. A. K., Tanaka, N., Sasaki, Y., & Osada, M. (2011). Boulder transport by tsunami: hydrodynamic approaches for incipient motion and transport modes.

