## Hackatón HPE – Fase II

Heimdall es un proyecto diseñado para evidenciar la factibilidad técnica y estratégica de la toma de decisiones fundamentadas en datos sintéticos y análisis predictivo en tiempo casi real. El proyecto trasciende la mera simulación descriptiva para consolidarse como un sistema evaluable orientado al apoyo en la toma de decisiones operativas.

El sistema compara dos estrategias fundamentales:

- **Reactiva (Baseline)**: Las unidades son movilizadas únicamente después de la aparición de un incidente confirmado, utilizando una política determinística basada en el tiempo estimado de llegada.
- **Inteligente (Predictiva)**: El sistema realiza un análisis continuo de datos observables, estima probabilidades de riesgo y redistribuye patrullas proactivamente antes de la ocurrencia de eventos.

---

## Contexto del Problema

Los sistemas tradicionales de despacho policial operan bajo un modelo reactivo. Este enfoque produce:

- Tiempos de respuesta elevados.
- Sobrecarga de ciertas unidades.
- Zonas urbanas sin cobertura.
- Imposibilidad de anticipar eventos.
- Vulnerabilidad ante fallos internos.

El proyecto propone sustituir la reacción posterior al evento por anticipación basada en análisis de datos operativos continuos.

---

## Objetivos del Sistema

### Objetivo General

Desarrollar un sistema multi-agente de gemelos digitales policiales interconectados. Este sistema debe ser capaz de:

- Analizar telemetría operativa en tiempo casi real.
- Predecir probabilidades de incidente por zona.
- Detectar fallos internos de unidades.
- Optimizar la asignación de recursos.
- Asistir la toma de decisiones del centro de control, sin ejercer control autónomo real sobre las unidades.

### Indicadores de Desempeño (KPI)

El sistema será evaluado mediante las siguientes métricas cuantificables:

- Reducción del tiempo promedio de respuesta ≥ 20%.
- Reducción del consumo promedio de combustible ≥ 10%.
- Cobertura urbana operativa ≥ 95% del territorio simulado.
- Precisión en detección de anomalías internas ≥ 90%.

---

## Arquitectura Técnica

Se adopta una arquitectura híbrida distribuida Edge–Cloud estructurada en contenedores Docker y orquestada con Kubernetes.

- **Nivel Edge (Patrullas):** Cada unidad ejecuta un gemelo digital local responsable de representar su estado operativo, validar la coherencia básica de los datos y detectar fallas mecánicas inmediatas.
- **Nivel Cloud (Centro de Coordinación):** Una plataforma central consolida la información global, supervisa el sistema completo, coordina múltiples patrullas y prepara los datos para el análisis predictivo.

El sistema asegura la integridad de los datos mediante comunicación MQTT sobre TLS 1.3, autenticación mutua por certificados, y cifrado en tránsito y reposo (AES-256).

---

## Modelo Operativo y de Inteligencia Artificial

### Generación de Telemetría y Simulación

Debido a la inexistencia de sensores físicos, el sistema emplea telemetría sintética con una frecuencia de actualización de 1 Hz. Los incidentes son generados por un Simulador Urbano Estocástico (SUE) independiente, el cual utiliza un proceso de Poisson espacial–temporal para modelar la ocurrencia de eventos.

### Lógica de Despacho (Optimización Multi-Criterio)

Para asignar unidades a un incidente, el sistema evalúa una función de costo que minimiza el tiempo esperado de atención sin comprometer la estabilidad del sistema. El tiempo estimado de llegada (ETA) se calcula como:

```
ETA = Distancia / Velocidad
```

La asignación selecciona la patrulla que minimiza múltiples variables, incluyendo el riesgo mecánico y la pérdida de cobertura territorial.

### Modelo Predictivo

El cálculo de riesgo se basa en un modelo matemático híbrido compuesto por:

- **Media móvil ponderada con decaimiento temporal:** Evalúa el riesgo histórico donde los eventos recientes incrementan significativamente el riesgo y los antiguos tienen influencia marginal.
- **Inferencia probabilística Bayesiana:** Ajusta el modelo histórico utilizando factores contextuales observables como la hora del día y el nivel de tráfico.

### Detección de Amenazas Internas

El sistema incorpora un modelo de amenazas basado en inconsistencias medibles. Se generan alertas automáticas y reasignación preventiva cuando ocurre:

- Discrepancia GPS-velocidad mayor a 10 km/h sostenida por 5 segundos.
- Caída de combustible no proporcional con la distancia recorrida.
- Unidad sin respuesta operativa durante 30 segundos.
- Temperatura crítica del motor (> 105°C) sostenida por más de 30 ciclos de simulación.

---

## Estructura del Repositorio

```
Prototipo/
│
├── main.py                      -> Punto de entrada de la simulación
├── experiments_parallel.py      -> Ejecuta múltiples simulaciones en paralelo
├── generate_compare.py          -> Agrega resultados y genera comparación
│
├── simulation/
│   ├── world.py                 -> Mundo de simulación (mapa, tiempo, unidades)
│   ├── incident_generator.py    -> Generación de incidentes (SUE)
│   ├── dispatcher.py            -> Lógica de despacho/asignación de unidades
│   ├── predictor.py             -> Predicción de zonas de riesgo (hotspots)
│   ├── unit.py                  -> Gemelos digitales de unidades móviles
│   └── metrics_engine.py        -> Registro de auditoría y cálculo de métricas
│
└── results_*.csv                -> Resultados de corridas para evaluación
```

---

## Requisitos y Ejecución

- **Python 3.10+** (probado en 3.12)

### Corrida individual:

```bash
python main.py --mode reactive --seed 1
python main.py --mode intelligent --seed 1
```

### Experimentos con múltiples corridas (Estabilidad estadística):

```bash
python experiments_parallel.py
```

### Comparación y análisis de métricas:

```bash
python generate_compare.py
```
---

## Equipo y Créditos

**Proyecto desarrollado para el Hackatón de Hewlett Packard Enterprise (HPE) - Fase II.**

* **Equipo:** MonkeyTypers (México)
* *Periodo de desarrollo:** Febrero – Marzo 2026

**Integrantes:**
* [Ivan Ramos] - [GitHub](https://github.com/FishyOfixial)
* [Lucas Castineiras] - [GitHub](https://github.com/Locas1000)
* [Patricio Dávila ] - [GitHub](https://github.com/patodaas)
* [Juan Marco ] -   [GitHub](https://github.com/JuanMarcoGosselin)
* [Carlo Virgilio ] -  [GitHub](https://github.com/carlovirgil)
