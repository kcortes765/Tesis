# Registro objetivo de estado y decisiones

## 1. Objetivo de esta etapa

El objetivo de esta etapa ha sido cerrar el dp de produccion para el setup 5D actual,
es decir, para una configuracion donde varian dam_h, mass, rot_z, friction y slope_inv.
La pregunta no es solo numerica; tambien es metodologica: con que observable se debe
defender el dp en un problema de movimiento incipiente.

## 2. Estado previo

Antes de esta etapa ya estaban operativos:

- el pipeline 5D
- el screening R1 y R2
- el analisis que mostro que la friccion es una variable muy sensible

Tambien se habia hecho una convergencia en el caso de referencia de Moris. Esa convergencia
no cerraba limpio para la trayectoria post-falla. A partir de eso se decidio cambiar la
estrategia: en vez de cerrar dp con un caso fuertemente fallido, buscar un caso cerca
de la frontera ESTABLE/FALLO.

## 3. Cambio de estrategia hacia frontera

Para estudiar la frontera se hizo un corte 1D de una frontera multidimensional. Se fijaron:

- dam_h = 0.20
- mass = 1.0
- slope = 1:20
- rot_z = 0

y se vario solo mu. Esto no significa que solo importe mu; significa que se quiso aislar
su efecto manteniendo el resto fijo.

## 4. Hallazgo critico en la geometria inicial

Durante el scouting se detecto un problema metodologico importante:

- el bloque quedaba a la altura correcta de la playa, pero horizontal respecto del mundo
- no quedaba alineado con la pendiente real de la playa
- ademas, el STL real rotado partia con una pequena penetracion en la rampa

La penetracion observada fue de aproximadamente +0.508 mm de correccion necesaria en z
para dejar contacto exacto.

## 5. Fix implementado

Se corrigieron dos cosas:

1. alineacion del bloque con la pendiente de la playa
2. ajuste fino en z para apoyo exacto

Para slope = 1:20:

- angulo en y = -2.862405 deg
- ajuste de apoyo = +0.508 mm

Esto se verifico en los logs de la WS con mensajes del tipo:

- rot=(0.0, -2.862405..., 0.0)
- Ajuste apoyo boulder: elevando 0.508 mm para dejar contacto exacto con la playa

## 6. Precision del umbral

El umbral del script no es 5.000 mm redondos, sino:

- 0.05 * d_eq

Con d_eq = 0.100421 m:

- umbral exacto = 0.00502105 m = 5.021 mm

Esto importa porque varios casos quedaron practicamente pegados al umbral.

## 7. Scouts corregidos con geometria valida

Resultados corregidos de scouting a dp = 0.004:

- mu=0.665 -> 14.119 mm -> FALLO
- mu=0.670 -> 11.412 mm -> FALLO
- mu=0.675 -> 9.313 mm -> FALLO
- mu=0.680 -> 6.819 mm -> FALLO
- mu=0.685 -> 10.343 mm -> FALLO
- mu=0.690 -> 4.323 mm -> ESTABLE
- mu=0.695 -> 7.712 mm -> FALLO
- mu=0.700 -> 5.020 mm -> ESTABLE
- mu=0.705 -> 3.673 mm -> ESTABLE
- mu=0.710 -> 5.081 mm -> FALLO
- mu=0.720 -> 3.543 mm -> ESTABLE

Interpretacion:

- la nueva banda critica quedo alrededor de mu ~ 0.69-0.71
- la respuesta no es monotona en mu
- cerca del onset la respuesta es muy sensible

## 8. Decisiones tomadas

Decision operativa principal:

- dejar de scout-ear mas a dp=0.004
- pasar a convergencia corregida en dos casos marginales

Casos elegidos:

- mu=0.700 como lado estable marginal
- mu=0.710 como lado fallo marginal

Razon:

- no bastaba con un solo lado del borde
- se queria probar la robustez de la clasificacion al refinar dp desde ambos lados

## 9. Estado de convergencia corregida en mu=0.700

Resultados disponibles:

- dp=0.004: disp=5.020 mm, rot=4.89 deg, vel=0.1000 m/s, Fsph=16.483 N, class=ESTABLE
- dp=0.003: disp=2.322 mm, rot=4.87 deg, vel=0.1001 m/s, Fsph=8.387 N, class=ESTABLE
- dp=0.002: disp=1.845 mm, rot=7.04 deg, vel=0.0699 m/s, Fsph=8.044 N, class=FALLO

Lectura:

- el desplazamiento baja al refinar
- la fuerza SPH baja fuertemente al refinar
- la clasificacion cambia por rotacion acumulada, no por desplazamiento

## 10. Estado de convergencia corregida en mu=0.710

Resultados actualmente consolidados:

- dp=0.004: disp=5.081 mm, rot=4.79 deg, vel=0.1000 m/s, Fsph=16.442 N, class=FALLO
- dp=0.003: disp=1.437 mm, rot=4.93 deg, vel=0.1001 m/s, Fsph=8.433 N, class=ESTABLE
- dp=0.002: disp=1.809 mm, rot=7.44 deg, vel=0.0700 m/s, Fsph=8.054 N, class=FALLO

Lectura:

- el desplazamiento fino tambien queda bajo el umbral
- la fuerza SPH baja con fuerza al refinar
- la clasificacion vuelve a cambiar por rotacion acumulada, no por desplazamiento

## 11. Tema metodologico abierto

La rotacion actual es rotacion acumulada, no angulo neto final. Esto significa que la
metrica integra |omega| y por tanto captura rocking acumulado. Un bloque puede oscilar
sin quedar con una gran rotacion neta final y aun asi acumular una rotacion alta.

Eso deja abierta la pregunta metodologica:

- para cerrar dp, debe privilegiarse displacement/onset como metrica primaria?
- o la rotacion acumulada debe seguir participando del criterio principal de falla?

## 12. Que se puede afirmar hoy

- la geometria inicial corregida cambia de forma relevante la frontera
- los resultados pre-fix ya no son defendibles para cerrar esta decision
- la banda corregida de frontera queda en mu ~ 0.69-0.71
- mu=0.700 ya muestra que displacement y forcing bajan al refinar dp
- mu=0.710 confirma el mismo patron: displacement bajo en la malla fina y fallo por rotacion acumulada
- en ambos casos marginales, el problema metodologico dominante pasa a ser la metrica de rotacion acumulada

## 13. Preguntas concretas para discutir con el profesor

1. Para cerrar dp en esta tesis, conviene usar displacement/onset como criterio primario
   y dejar rotacion acumulada como diagnostico?
2. El profesor esta de acuerdo en descartar formalmente los scouts y convergencias de
   frontera previos al fix geometrico?
3. Le parece suficiente cerrar dp con dos convergencias corregidas a ambos lados del
   umbral (mu=0.700 y mu=0.710), o quiere una escalera mas clasica y completa?

## 14. Estado del paquete

Este paquete incluye:

- figuras corrected_story para la historia corregida
- resumen corto de corrected_story
- registro objetivo de hechos, decisiones y estado actual
