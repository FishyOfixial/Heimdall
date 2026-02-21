# Prototipo de Sistema Inteligente de Respuesta a Incidentes

**Hackatón HPE – Fase II**

Este repositorio contiene un prototipo de simulación de una ciudad donde se generan incidentes (eventos) y un sistema de despacho decide cómo responderlos. El objetivo es comparar dos enfoques:

* **Reactivo**: atiende los incidentes cuando aparecen.
* **Inteligente (predictivo)**: intenta anticipar dónde ocurrirán y posicionar unidades antes de que sucedan.

El propósito del proyecto es evaluar si un sistema de predicción puede **reducir el tiempo de respuesta y prevenir incidentes**, manteniendo o mejorando la cobertura del sistema.

---

## 1. Idea general

La simulación modela una ciudad dividida en celdas. Durante cada *tick* del reloj virtual:

1. Se generan incidentes de manera estocástica.
2. Las unidades (patrullas) se mueven por el mapa.
3. El sistema decide a dónde enviarlas.
4. Se registran métricas de desempeño.

El modo **reactivo** solo reacciona a eventos ya ocurridos.
El modo **inteligente** utiliza un predictor de zonas calientes (*hotspots*) para adelantarse.

---

## 2. Arquitectura del sistema

El sistema está dividido en módulos desacoplados para facilitar experimentación:

```
Prototipo/
│
├── main.py                      -> Punto de entrada de la simulación
├── experiments_parallel.py      -> Ejecuta múltiples simulaciones en paralelo
├── generate_compare.py          -> Calcula promedios, desviaciones y genera gráfica
│
├── simulation/
│   ├── world.py                 -> Entorno de simulación (mapa, tiempo, unidades)
│   ├── incident_generator.py    -> Generación probabilística de incidentes
│   ├── dispatcher.py            -> Lógica de asignación de unidades
│   ├── predictor.py             -> Sistema de predicción de hotspots
│   ├── unit.py                  -> Agentes móviles (patrullas)
│   └── metrics_engine.py        -> Registro y cálculo de métricas
│
└── results_*.csv                -> Resultados de corridas
```

---

## 3. Modelo de simulación

### Tiempo

El sistema avanza por pasos discretos llamados **ticks**.
Un experimento típico corre **3600 ticks** (simula varias horas de operación).

### Incidentes

Los incidentes se generan con probabilidad dependiente de zona y tiempo. Cada incidente tiene:

* Posición
* Tick de ocurrencia
* Tick de resolución

Un incidente puede:

* Ser atendido
* Ser atendido tarde
* Ser prevenido (solo modo inteligente)

---

## 4. Sistema predictivo (modo inteligente)

El predictor construye un mapa de calor dinámico basado en:

* Historial reciente de incidentes
* Frecuencia por celda

El sistema entonces:

1. Identifica zonas con mayor probabilidad de incidentes.
2. Mueve unidades preventivamente.
3. Si ocurre un evento cerca, la respuesta es inmediata.

Esto permite reducir el **tiempo de respuesta promedio**.

---

## 5. Métricas evaluadas

Cada corrida genera un CSV con las siguientes métricas:

| Métrica              | Significado                               |
| -------------------- | ----------------------------------------- |
| avg_response_time    | Tiempo promedio de respuesta              |
| coverage_percent     | Porcentaje del mapa cubierto por unidades |
| incidents_prevented  | Incidentes evitados (solo inteligente)    |
| prediction_rate      | Frecuencia de predicciones realizadas     |
| prediction_precision | Precisión de predicción                   |
| prediction_recall    | Recall de predicción                      |
| incidents_total      | Total de incidentes generados             |
| resolved_incidents   | Incidentes resueltos                      |

---

## 6. Ejecución de la simulación

Requisitos:

* Python 3.10+ (probado en 3.12)

Ejecutar una corrida individual:

```
python main.py --mode reactive --seed 1
python main.py --mode intelligent --seed 1
```

El parámetro `seed` permite reproducibilidad experimental.

Cada ejecución genera una fila CSV con resultados.

---

## 7. Múltiples corridas (experimentos)

Para obtener resultados estadísticamente válidos se deben ejecutar muchas simulaciones con diferentes semillas:

```
python experiments_parallel.py
```

Este script:

* Ejecuta múltiples seeds
* Usa multiprocessing
* Genera:

```
results_reactive.csv
results_intelligent.csv
```

---

## 8. Comparación y análisis

Después de ejecutar los experimentos:

```
python generate_compare.py
```

Esto:

1. Calcula promedio
2. Calcula desviación estándar
3. Genera `compare.csv`
4. Muestra gráfica comparativa

La gráfica compara principalmente:

* Tiempo de respuesta
* Incidentes prevenidos
* Cobertura

---

## 9. Interpretación esperada

El sistema inteligente debería:

* Reducir significativamente el **tiempo de respuesta**
* Prevenir incidentes
* Mantener cobertura similar al sistema reactivo

Si esto se cumple, el prototipo valida la hipótesis del proyecto.

---

## 10. Limitaciones del prototipo

Este es un modelo experimental, no un sistema real. Limitaciones:

* El mapa es una grilla simplificada
* No hay tráfico real
* Las unidades tienen velocidad constante
* El predictor es heurístico (no ML real)
* No se modela comportamiento humano complejo

El objetivo es evaluar el **concepto**, no replicar una ciudad real.

---

## 11. Posibles mejoras futuras

* Modelo de tráfico realista
* Aprendizaje automático (ML) real
* Predicción por hora del día
* Tipos de incidentes
* Recursos limitados
* Rutas óptimas

---

## 12. Objetivo del Hackatón

Demostrar que un sistema de posicionamiento preventivo basado en predicción puede mejorar la operación de servicios de respuesta (seguridad, emergencias, logística urbana) mediante simulación reproducible y medible.

Este prototipo busca validar la viabilidad técnica antes de implementar en un entorno real.

---

**Proyecto desarrollado para el Hackatón de Hewlett Packard Enterprise (HPE).**
