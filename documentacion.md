ETAPA 1 — Definición Estratégica (Versión Reconstruida y Formalizada)
1. Propósito de la Etapa
La presente etapa establece la base conceptual, operativa y medible del sistema.
El proyecto deja de plantearse como una simulación descriptiva y pasa a definirse como un sistema evaluable de apoyo a decisiones operativas.
Se define formalmente el objetivo: diseñar un sistema de gemelos digitales interconectados capaz de anticipar incidentes, detectar anomalías operativas y optimizar la coordinación de múltiples unidades policiales mediante análisis predictivo en tiempo casi real.
El sistema no pretende controlar unidades reales. Su finalidad es demostrar la viabilidad técnica, estratégica y operativa de la toma de decisiones basada en datos.
El proyecto no se limita a una simulación descriptiva del comportamiento urbano.
El entorno permanece simulado; sin embargo, el sistema se define formalmente como un prototipo operativo de gemelos digitales (Prototype Digital Twin) cuyo propósito es evaluar estrategias de coordinación y toma de decisiones.
Debido a la inexistencia de sensores físicos, la telemetría utilizada es sintética, pero estructuralmente equivalente a la telemetría real, permitiendo validar algoritmos, modelos predictivos y políticas operativas sin necesidad de desplegar hardware.

2. Contexto del Problema
Los sistemas tradicionales de despacho policial operan bajo un modelo reactivo.
Las unidades son movilizadas únicamente después de la aparición de un incidente, utilizando información incompleta o desactualizada. Este enfoque produce:
	tiempos de respuesta elevados
	sobrecarga de ciertas unidades
	zonas urbanas sin cobertura
	imposibilidad de anticipar eventos
	vulnerabilidad ante fallos internos
Cuando ocurren múltiples incidentes simultáneos, la coordinación humana se vuelve insuficiente debido a la limitada capacidad de procesar grandes volúmenes de información en tiempo real.
El proyecto propone sustituir la reacción posterior al evento por anticipación basada en análisis de datos operativos continuos.

3. Objetivo General
Diseñar un sistema multi-agente de gemelos digitales policiales capaz de:
	analizar telemetría operativa en tiempo casi real
	predecir probabilidades de incidente por zona
	detectar fallos internos de unidades
	optimizar la asignación de recursos
	asistir la toma de decisiones del centro de control

4. Indicadores de Desempeño (KPI)
El sistema será evaluado mediante métricas cuantificables:
	Reducción del tiempo promedio de respuesta ≥ 20%
	Reducción del consumo promedio de combustible ≥ 10%
	Cobertura urbana operativa ≥ 95% del territorio simulado
	Precisión en detección de anomalías internas ≥ 90%
Estas métricas permiten validar el sistema como una mejora objetiva frente al modelo reactivo.
5. Alcance de la Solución
La solución consiste en una simulación de múltiples patrullas policiales, donde cada unidad posee un gemelo digital que reporta continuamente su estado operativo a una plataforma central.
El sistema incluye:
	múltiples unidades policiales simuladas
	comunicación continua entre gemelos digitales
	análisis coordinado entre patrullas
	asignación inteligente de recursos
	detección de inconsistencias operativas
	patrullaje preventivo basado en riesgo
El sistema se define como apoyo a decisiones, no como control autónomo real.

6. Modelo Operativo del Sistema
Cada patrulla transmite telemetría periódica con frecuencia fija de 1 Hz (una muestra por segundo).
El sistema mantiene un estado global discreto del entorno urbano simulado. En cada ciclo de actualización se ejecuta un proceso de evaluación operacional cuyo objetivo es seleccionar la acción que minimiza el tiempo esperado de atención a incidentes sin comprometer la cobertura territorial.
Para cada patrulla pse define su estado operativo:
State_p (t)={pos_p (t),vel_p (t),fuel_p (t),mech_p (t),availability_p (t)}
donde:
	pos_p (t)= posición en el mapa
	vel_p (t)= velocidad actual
	fuel_p (t)= combustible restante
	mech_p (t)= estado mecánico
	availability_p (t)= disponibilidad operativa
Para cada incidente i el sistema calcula el tiempo estimado de llegada:
ETA_(p,i)=(dist(pos_p,pos_i))/(vel_estimada (p,t))
La decisión operativa consiste en seleccionar la patrulla p^* que minimiza la función de costo:
p^*=arg⁡(min⁡)┬p (ETA_(p,i)+αR_coverage (p,t)+βR_fuel (p,t))
donde:
	R_coverage penaliza pérdida de cobertura territorial
	R_fuel penaliza asignar patrullas con combustible bajo
	α,β son pesos operativos configurables
El objetivo del sistema no es únicamente minimizar distancia, sino minimizar el costo operativo global manteniendo estabilidad del sistema.
7. Problemas Clave a Resolver
El proyecto aborda cinco deficiencias principales de los sistemas reactivos:
	reacción tardía ante incidentes
	asignación ineficiente basada solo en cercanía
	falta de coordinación multi-unidad
	vulnerabilidad ante manipulación o fallos internos
	inexistencia de patrullaje preventivo
8. Amenazas Internas y Detección de Anomalías
El sistema incorpora un modelo de amenazas internas basado en inconsistencias medibles entre variables operativas.
Se considerarán anomalías cuando ocurra:
	discrepancia GPS-velocidad mayor a 10 km/h sostenida por 5 segundos
	caída de combustible no proporcional con distancia recorrida
	unidad sin respuesta operativa durante 30 segundos
Estas condiciones generan alertas automáticas y provocan la reasignación de recursos antes de afectar la operación.
9. Contrato Inicial de Datos
Todas las patrullas deberán cumplir un esquema mínimo obligatorio de telemetría:
	posición (x, y)
	velocidad
	nivel de combustible
	temperatura de motor
	presión de neumáticos
	estado operativo
	sim operación
Esto garantiza consistencia de análisis y permite la interoperabilidad entre unidades.

10. Escenarios de Simulación
Para validar el sistema se definen tres escenarios:
Operación Normal
El sistema aprende patrones base y distribuye patrullas para cobertura territorial.
Evento Crítico Externo
Múltiples incidentes simultáneos.
El sistema coordina la respuesta optimizando recursos y tiempos de llegada.
Amenaza Interna
Una unidad presenta datos inconsistentes.
El sistema detecta la anomalía, la aísla y reasigna cobertura.

11. Valor Estratégico del Proyecto
El proyecto evidencia que la integración de gemelos digitales, análisis predictivo y la coordinación entre múltiples agentes permite evolucionar de un sistema de seguridad reactivo a uno preventivo. Age of Ultron se presenta como un modelo viable para diversas aplicaciones, tales como:
	centros de control urbano,
	seguridad pública,
	logística de emergencias,
	infraestructura de ciudades inteligentes (Smart City).
 
ETAPA 2 — Arquitectura Técnica del Sistema
1. Propósito de la Arquitectura
La presente etapa define la arquitectura técnica formal del sistema Age of Ultron.
Su objetivo es establecer la estructura computacional que permitirá la operación coordinada de múltiples gemelos digitales policiales, garantizando transmisión confiable de datos, operación distribuida y soporte para análisis predictivo posterior.
El sistema no se concibe como un simulador aislado, sino como una plataforma de coordinación operativa basada en telemetría continua.
La arquitectura busca:
	Permitir monitoreo en tiempo casi real de unidades
	Evitar dependencia de un único nodo central
	Detectar fallas operativas internas
	Proporcionar datos confiables para análisis predictivo
	Operar incluso ante fallas parciales del sistema
El sistema es explícitamente definido como sistema de apoyo a la decisión, no como control autónomo de unidades reales.

2. Modelo Arquitectónico General
Se adopta una arquitectura híbrida distribuida Edge–Cloud.
Nivel Edge (Patrullas)
Cada patrulla posee un gemelo digital local encargado de validaciones inmediatas y operación básica independiente.
Nivel Cloud (Centro de Coordinación)
Una plataforma central consolida la información global, coordina unidades y mantiene el histórico del sistema.
El sistema funciona como un sistema multi-agente coordinado, donde cada patrulla es un agente autónomo supervisado por un coordinador global.

3. Flujo Operativo del Sistema
El flujo funcional queda definido como:
Telemetría → Validación local → Envío seguro → Plataforma central → Evaluación → Decisión → Ejecución → Registro auditable
Cada decisión generada por el sistema queda almacenada para auditoría posterior.

4. Capa de Datos
4.1 Generación de Datos
Debido a la inexistencia de sensores físicos, el sistema emplea telemetría sintética generada por software que simula el comportamiento real de patrullas policiales.
La frecuencia de actualización queda establecida en:
	1 Hz (una actualización por segundo por patrulla)
Esto permite modelar un entorno dinámico sin sobrecargar la infraestructura.
4.2 Esquema de Telemetría Estandarizado
El contrato de telemetría se amplía para garantizar la reconstrucción completa del estado operativo del gemelo digital.
Cada paquete de telemetría incluirá las siguientes variables obligatorias:
	unit_id (UUID): identificador único de la unidad
	timestamp (epoch)
	position (lat, lon)
	speed (km/hr)
	fuel_level (%)
	tire_pressure (kPa)
	engine_temperature (°C)
	operating_state (AVAILABLE, PATROLLING, RESPONDING, REFUELING, MAINTENANCE, OUT_OF_SERVICE, EMERGENCY_RETURN)
	operating_time (s)
	task_queue_length (int)
Estas variables permiten la sincronización de estado entre el sistema físico simulado y su representación digital, cumpliendo la definición formal de gemelo digital.

4.3 Integridad y Seguridad
Cada mensaje de telemetría cumple:
	Comunicación mediante MQTT sobre TLS 1.3
	Autenticación mutua por certificados
	Firma HMAC por mensaje
	Cifrado en tránsito
	Cifrado en reposo (AES-256)
Esto evita manipulación de datos y permite detectar sabotaje interno.

5. Gemelo Digital de Patrulla (Edge Computing)
Cada unidad ejecuta un gemelo digital local responsable de representar su estado operativo.
Responsabilidades
	Validar coherencia básica de datos
	Detectar fallas mecánicas inmediatas
	Evaluar disponibilidad operativa
	Mantener operación degradada si el nodo central falla
	Enviar telemetría firmada

Validaciones Locales
El gemelo local detecta inconsistencias medibles:
	Diferencia GPS-velocidad mayor a 10 km/h sostenida por 5 s
	Caída de combustible no correlacionada con distancia
	Falta de respuesta de sensores
Estas condiciones generan alertas internas antes de cualquier análisis central.
6. Plataforma Central de Coordinación (Cloud)
La plataforma central es el coordinador global del sistema.
Funciones
	Recepción continua de telemetría
	Almacenamiento histórico
	Supervisión global
	Coordinación multi-patrulla
	Preparación de datos para análisis predictivo
El sistema no controla directamente a las unidades; recomienda acciones operativas.

Coordinación Operativa
La plataforma permite:
	Asignar unidades a incidentes
	Detectar sobrecarga de patrullas
	Reforzar zonas
	Reasignar misiones automáticamente

7. Comunicación Distribuida
Comunicación Principal
Patrulla → Plataforma Central
(telemetría y eventos)
Plataforma Central → Patrulla
(órdenes operativas)
Comunicación de Respaldo
Se define comunicación P2P entre patrullas en caso de caída del nodo central, permitiendo operación degradada.

8. Persistencia y Auditoría
Toda la información es almacenada en una base histórica cifrada.
Cada evento guarda:
	timestamp
	unidad involucrada
	decisión tomada
	justificación
	estado previo y posterior
Esto permite trazabilidad completa del sistema, requisito esencial en sistemas de misión crítica.

9. Control de Acceso y Visualización
El sistema incluye un Centro de Comando Digital accesible por navegador.
Se implementa RBAC:
	Operador → monitoreo y despacho manual
	Supervisor → control operativo
	Auditor → revisión histórica
El dashboard muestra:
	ubicación de patrullas
	estado operativo
	alertas
	decisiones del sistema

10. Escalabilidad y Orquestación
La infraestructura se implementa utilizando contenedores Docker y se gestiona mediante Kubernetes para la orquestación. Esta arquitectura facilita la incorporación de nuevas patrullas sin necesidad de rediseñar el sistema, ofrece tolerancia a fallos y permite el despliegue distribuido.
11. Justificación Técnica
La arquitectura propuesta convierte el sistema de simulación aislado en una plataforma distribuida auditable. En esta fase, aún no se incorpora la inteligencia artificial; su propósito principal es establecer una infraestructura de datos confiables indispensable para el funcionamiento futuro de la IA predictiva. La precisión de las predicciones dependerá directamente de la robustez de esta capa arquitectónica.
Esta arquitectura permite al sistema:
	operar sin la necesidad de conexión permanente,
	identificar fallas internas,
	registrar decisiones,
	proporcionar soporte para análisis predictivos posteriores.
Por tanto, la Etapa 2 representa el fundamento técnico sobre el que se desarrollará la implementación de inteligencia artificial en la etapa siguiente.


 
ETAPA 3 — Diseño del Prototipo Funcional (POC Operativo)
1. Propósito de la Etapa
La Etapa 3 define el comportamiento operativo formal del sistema mediante un Prototipo Funcional Conceptual (Proof of Concept).
El objetivo es demostrar que la arquitectura diseñada en la etapa anterior es capaz de coordinar múltiples unidades simuladas bajo reglas operativas verificables.
En esta fase no se desarrolla software productivo definitivo; se modela con precisión cómo operaría el sistema si estuviera desplegado.
El prototipo busca validar que el sistema puede:
	Supervisar múltiples patrullas simultáneamente
	Detectar riesgos operativos internos
	Coordinar respuestas ante incidentes
	Tomar decisiones explicables basadas en reglas
	Mantener operación segura ante fallos
La finalidad principal es comprobar viabilidad operativa, no rendimiento ni precisión predictiva.
2. Modelo Operativo del Sistema
El sistema opera como un sistema multi-agente discreto en tiempo sincronizado con la telemetría.
Se define un ciclo operativo con paso temporal: Δt = 1 segundo
Este valor coincide con la frecuencia de generación de telemetría establecida en la Etapa 2 (1 Hz). Cada iteración del sistema corresponde a la recepción de una nueva muestra de estado de cada gemelo digital, garantizando coherencia temporal entre la evolución del modelo y los datos observados.
En cada iteración del sistema se ejecuta:
	Actualización de telemetría
	Validación local del gemelo digital
	Sincronización con plataforma central
	Evaluación de eventos activos
	Asignación de recursos
	Registro de auditoría
Formalmente, el estado global del sistema se representa como:
S(t)={P(t),E(t),Z(t)}
donde:
	P(t)= conjunto de patrullas
	E(t)= conjunto de incidentes activos
	Z(t)= estado de zonas urbanas
El sistema evoluciona como un proceso dinámico discreto:
S(t+1)=F(S(t),A(t))

donde A(t)son las acciones decididas por el coordinador.
3. Máquina de Estados de las Patrullas
Para evitar comportamientos ambiguos, cada patrulla queda modelada mediante una máquina de estados finitos verificable.
Estados Operativos
	AVAILABLE: disponible para asignaciones
	PATROLLING: patrullaje preventivo
	RESPONDING: atendiendo incidente
	REFUELING: repostando combustible
	MAINTENANCE: revisión técnica
	OUT_OF_SERVICE: fuera de operación
	EMERGENCY_RETURN: retorno inmediato por riesgo crítico
Cada estado posee condiciones formales de entrada y salida.
Se eliminan estados indefinidos o “agentes huérfanos”.



Transiciones Críticas
Ejemplo:
Si una patrulla en RESPONDING detecta temperatura crítica del motor:
RESPONDING → EMERGENCY_RETURN
El sistema central automáticamente:
	Reasigna la misión a otra unidad
	Registra la anomalía
	Marca la unidad como no disponible
Esto introduce tolerancia a fallos operativos.

4. Entidades del Prototipo
4.1 Patrullas (Agentes Operativos)
Generan telemetría continua y ejecutan acciones asignadas.
Responsabilidades:
	Reportar estado
	Ejecutar misiones
	Detectar fallos locales
	Entrar en modo degradado si pierden conexión
4.2 Plataforma Central
Supervisa el sistema completo.
Funciones:
	Consolidar información global
	Detectar conflictos operativos
	Asignar unidades
	Reasignar tareas automáticamente


4.3 Entorno Urbano Simulado
El sistema incluye un mapa conceptual dividido en zonas operativas donde pueden ocurrir incidentes y variaciones de tráfico.
El entorno afecta:
	tiempo de llegada
	disponibilidad
	asignación de recursos

5. Lógica de Decisión (Pre-IA)
En esta etapa aún no existe inteligencia artificial predictiva.
Las decisiones se basan en reglas operativas determinísticas.
El sistema evalúa:
	proximidad al incidente
	disponibilidad
	estado mecánico
	carga operativa
Ejemplo de regla:
Seleccionar la patrulla disponible con menor tiempo estimado de llegada (ETA) y estado mecánico válido.
Esto establece una línea base contra la cual posteriormente se comparará la IA.
6. Escenarios de Operación
Escenario 1 — Operación Normal
Las patrullas realizan recorridos en las zonas asignadas. El sistema monitorea permanentemente la actividad, registra los eventos relevantes y optimiza la cobertura para establecer el comportamiento base.
Escenario 2 — Incidente Externo
Los incidentes son originados por el Simulador Urbano Estocástico mediante un proceso probabilístico espacial-temporal independiente del sistema de toma de decisiones. El sistema evalúa la disponibilidad de recursos, asigna unidades a los incidentes y coordina refuerzos cuando es necesario, con el objetivo de disminuir los tiempos de respuesta.
Escenario 3 — Anomalía Interna
En caso de que una patrulla reporte datos inconsistentes, como una disminución anormal de combustible, discrepancia entre GPS y velocidad, o ausencia de respuesta, el sistema detecta la anomalía, retira la unidad de manera preventiva y reasigna la cobertura. Este procedimiento evidencia la capacidad del sistema para garantizar la seguridad operativa.

7. Modo Degradado y Control Humano
Si el sistema automático falla o el módulo inteligente queda inactivo:
	El sistema entra en modo despacho manual.
	El operador humano asume la asignación de unidades mediante el dashboard.
Esto asegura que el sistema:
	Mantenga su operatividad en todo momento,
	No dependa únicamente de procesos automatizados.
8. Trazabilidad y Auditoría
Cada acción del sistema queda registrada mediante logs firmados:
Se almacena:
	evento recibido
	decisión tomada
	unidad asignada
	estado previo y posterior
	timestamp
Esto permite reconstruir completamente cualquier operación.
9. Centro de Comando Digital
El prototipo incluye un dashboard que representa el gemelo digital global del sistema.

Permite visualizar:
	ubicación de patrullas
	estado operativo
	alertas
	decisiones automáticas
El objetivo no es controlar manualmente, sino comprender el comportamiento del sistema.
10. Validación del Prototipo
El POC demuestra que:
	la arquitectura distribuida es operable
	las patrullas pueden coordinarse
	el sistema detecta anomalías
	las decisiones son explicables
	existe continuidad operativa
La etapa valida la lógica del sistema antes de introducir predicción.
11. Justificación Técnica
La Etapa 3 constituye la validación funcional del sistema.
Antes de aplicar inteligencia artificial, es necesario demostrar que el sistema funciona correctamente con reglas determinísticas.
Esto es crítico porque:
una IA no puede aprender ni predecir correctamente sobre un sistema cuya lógica base es inestable.
Por lo tanto, esta etapa crea la línea base operativa sobre la cual la Etapa 4 implementará la inteligencia artificial predictiva.
El resultado es un sistema verificable, auditable y controlable, preparado para incorporar modelos predictivos sin comprometer seguridad operativa.
 
ETAPA 4 — Implementación de Inteligencia Artificial Predictiva
1. Objetivo
El objetivo de esta etapa es incorporar un módulo formal de inteligencia artificial capaz de transformar el sistema de un modelo reactivo a un modelo preventivo y auto-adaptativo.
A diferencia de las etapas anteriores, el sistema ya no depende de la creación manual de incidentes para operar. El sistema analiza continuamente los datos observables, estima probabilidades de riesgo y redistribocuuye patrullas antes de que ocurra un evento.
El gemelo digital pasa a funcionar como un sistema de apoyo a decisiones operativas capaz de:
	anticipar incidentes
	detectar fallos internos
	prevenir pérdida de cobertura
	optimizar el despliegue de unidades
El sistema no reemplaza al operador humano; lo asiste con decisiones fundamentadas en datos.
2. Flujo Operativo Predictivo
El sistema no genera decisiones únicamente en respuesta a incidentes.
El análisis predictivo ocurre de manera continua sobre el estado del entorno.
El flujo operacional correcto queda definido como:
"Observaci" "o"  ˊ"n"→"Actualizaci" "o"  ˊ"n del Modelo"→"Estimaci" "o"  ˊ"n de Riesgo"→"Decisi" "o"  ˊ"n Preventiva"→"Ocurrencia del Evento"→"Evaluaci" "o"  ˊ"n" 
Proceso:
	El simulador urbano produce eventos estocásticos independientes.
	El sistema registra telemetría y eventos históricos.
	El modelo predictivo estima el riesgo por zona.
	El sistema redistribuye patrullas preventivamente.
	Puede ocurrir o no un incidente real.
	El sistema compara predicción vs realidad y actualiza el modelo.
Esto convierte al sistema en aprendizaje en línea.
3. Arquitectura Funcional del Módulo Inteligente
El sistema queda dividido en seis módulos:
	Simulación del entorno
	Gemelos digitales de patrullas
	Registro histórico
	Evaluación de estado interno
	Motor predictivo
	Coordinador de decisiones
La IA se ubica entre el historial y la decisión operativa.

4. Modelo de Datos
4.1 Patrulla (Estado Operativo)
AVAILABLE
PATROLLING
RESPONDING
REFUELING
MAINTENANCE
OUT_OF_SERVICE
EMERGENCY_RETURN
Cada patrulla incluye:
	posición
	combustible
	velocidad
	temperatura del motor
	presión de llantas
	tiempo operativo
	cola interna de tareas


4.2 Amenazas Externas
Cada incidente posee:
	zona
	severidad (1-5)
	tiempo
	activo/inactivo

4.3 Amenazas Internas
El sistema considera fallos realistas:
	sobrecalentamiento de motor
	baja presión de neumáticos
	desgaste mecánico
	batería baja
	consumo anómalo de combustible
	ausencia de respuesta
Esto permite mantenimiento predictivo, no solo reacción.
4.4 Registro Histórico
Cada decisión y evento queda almacenado de forma estructurada.
Este historial es la memoria del sistema y el dataset de entrenamiento continuo.
4.5 Simulador Urbano Estocástico (SUE)
El sistema incorpora un simulador independiente responsable de moderar el comportamiento del entorno urbano.
El simulador representa la realidad operacional del sistema y actúa como fuente de verdad (ground truth).
Funciones:
	generar incidentes
	modelar tráfico
	variar condiciones temporales
	afectar tiempos de llegada
El simulador opera mediante un proceso probabilístico espacial-temporal.
El módulo de inteligencia artificial no tiene acceso a su estado interno y solo observa eventos ya ocurridos.

El entorno simulado no genera incidentes de manera aleatoria uniforme. Para que el modelo predictivo sea evaluable, los eventos deben surgir de un proceso probabilístico coherente con el comportamiento de sistemas reales. 
El simulador utiliza un proceso de Poisson espacial–temporal, comúnmente empleado para modelar la ocurrencia de eventos discretos en el tiempo.
Cada zona z del mapa posee una intensidad de ocurrencia:
λ_z (t)
donde:
	 λ= tasa esperada de incidentes por unidad de tiempo
	depende de condiciones del entorno
La probabilidad de al menos un incidente en un intervalo corto Δt es:
P(N_z (t+Δt)-N_z (t)≥1)=1-e^(-λ_z (t)Δt)

Para intervalos pequeños
P≈λz(t)Δt
Esto permite generar eventos no deterministas, pero con patrones estadísticos.
La tasa de incidentes depende de factores contextuales:
λ_z (t)=λ_base (z)⋅F_hora (t)⋅F_trafico (z,t)⋅F_historial (z,t)
donde:
F_trafico (z,t)=1+α⋅density(z,t)
F_historial (z,t)=1+β⋅recent_events(z,t)
Esto produce agrupaciones espaciales de eventos (crime clustering), evitando generación uniforme irrealista.
4.6 Sistema de Referencia Reactivo (Baseline Operativo)
El proyecto incorpora un sistema de referencia denominado Baseline Reactivo, cuyo objetivo es establecer una línea base de desempeño operativo sin el uso del módulo predictivo.
En este modo, el sistema opera bajo un modelo tradicional de despacho policial: las unidades son asignadas únicamente después de la aparición de un incidente confirmado. No existe patrullaje preventivo basado en riesgo ni redistribución anticipada.
La asignación de patrullas se realiza mediante una política determinística basada en tiempo estimado de llegada (ETA). Para cada incidente, el sistema selecciona la unidad disponible con menor tiempo de arribo considerando distancia, velocidad estimada y estado operativo válido.
El Baseline utiliza exactamente:
	el mismo simulador urbano
	la misma cantidad de patrullas
	las mismas reglas físicas
	la misma telemetría
La única diferencia respecto al sistema inteligente es la ausencia del modelo predictivo.
Este sistema representa el comportamiento realista de un centro de despacho convencional y permite evaluar objetivamente si la inteligencia artificial produce mejoras medibles.

5. Aprendizaje Inicial (Sin Datos)
Problema: primera ejecución sin historial.
Solución: modo exploratorio controlado.
Durante la primera ejecución, los incidentes son producidos por el Simulador Urbano Estocástico.
El sistema no conoce la distribución real del entorno y debe estimarla progresivamente a partir de observaciones históricas.

6. Modelo Predictivo
6.1 Descripción General
El sistema incorpora un módulo de predicción de riesgo espacial–temporal cuyo objetivo es estimar la probabilidad relativa de ocurrencia de incidentes dentro del entorno urbano simulado.
Este módulo permite pasar de un esquema operativo reactivo (respuesta posterior al evento) a un esquema preventivo basado en inferencia probabilística.
El modelo predictivo no determina la ocurrencia determinística de un incidente; en su lugar, calcula un nivel de riesgo relativo por zona, el cual es utilizado por el sistema de coordinación para ejecutar despliegues preventivos y optimizar la cobertura operativa.
El cálculo de riesgo se basa en un modelo matemático híbrido compuesto por:
	Media móvil ponderado con decaimiento temporal
	Inferencia probabilística Bayesiana
El sistema estima:
 P(Incidente|Historial,Tiempo,Trafico)
Esta probabilidad representa la propensión estadística de una zona a presentar un evento operativo en el corto plazo.
6.2 Representación Espacial del Entorno
El entorno urbano simulado es discretizado en una malla bidimensional configurable.
El tamaño de la celda se calculará dinámicamente:
cell_size=√((area total)/(N_unidades ×k))
Donde k es el factor de densidad operacional
Cada celda de la malla mantiene un valor dinámico de riesgo:
risk_map[x][y]

Este valor no corresponde a un contador de incidentes, sino a una estimación probabilística acumulada, actualizada continuamente en función de eventos históricos y condiciones operativas actuales.

6.3 Componente Histórico (Media Móvil Ponderada)
Cada incidente registrado actualiza el riesgo de la zona correspondiente.
El modelo incorpora un mecanismo de decaimiento temporal para reflejar la pérdida de relevancia de eventos antiguos.
El riesgo histórico se calcula mediante:
R_hist (x,y)=∑_(i=1)^n▒S_i ⋅e^(-λΔt_i )

Donde:
	S_i= severidad del evento
	Δt_i= tiempo transcurrido desde el evento
	λ= coeficiente de decaimiento temporal
Este enfoque produce un sistema de memoria adaptativa en el cual:
• eventos recientes incrementan significativamente el riesgo
• eventos antiguos tienen influencia marginal
La actualización operativa del mapa se realiza:
R_hist (t+1)=e^(-λΔt) R_hist (t)+S_nuevo

6.4 Componente Probabilístico (Inferencia Bayesiana)
El modelo histórico se ajusta mediante factores contextuales operativos utilizando inferencia Bayesiana simplificada.
Se consideran variables observables del entorno:
	hora del día
	nivel de tráfico
	día de la semana
El riesgo final no es un producto directo de probabilidades absolutas.
Se define como una probabilidad posterior proporcional:
P(incidente∣X)∝P(X∣incidente)P(incidente)
Dado que no se conocen distribuciones reales completas, el sistema emplea una aproximación:
Risk(x,y,t)=R_hist (x,y,t)⋅w_h F_hora (t)+w_t F_trafico (z,t)+w_d F_dia (t)
donde:
	w_h,w_t,w_d son pesos normalizados
	∑w_i=1

6.5 Clasificación de Zonas
El sistema clasifica cada zona según un umbral configurable:
Risk(x,y)>θ⇒HIGH_RISK

Cuando una zona supera el umbral:
HIGH_RISK → el sistema ordena patrullaje preventivo automático
Este mecanismo permite desplegar unidades antes de la materialización del evento.
6.6 Naturaleza de la Predicción
El modelo no predice incidentes individuales ni afirma ocurrencias futuras específicas.
El sistema estima entre zonas.
Interpretación correcta:
El sistema determina qué zonas presentan mayor probabilidad estadística de generar un evento en comparación con el resto del entorno en un intervalo temporal corto.
6.7 Uso Operativo
El valor de riesgo alimenta el sistema de coordinación multi-agente, el cual utiliza esta información para:
	asignación preventiva de patrullas
	redistribución territorial
	refuerzo de cobertura
	reducción de tiempos de respuesta
De esta manera, el sistema no actúa únicamente ante eventos reportados, sino ante probabilidades inferidas.
7. Detección de Amenazas Internas
El sistema compara telemetría real con comportamiento esperado.
Ejemplos:
	GPS indica movimiento, pero velocidad = 0
	caída abrupta de combustible
	unidad no responde por 30 segundos
	Se definen umbrales operativos para los sensores:
	Temperatura nominal: 70°C – 95°C
	Temperatura elevada: 95°C – 105°C
	Temperatura crítica: > 105°C durante más de 30 segundos consecutivos
La condición de “temperatura crítica sostenida” se activa únicamente cuando el valor excede el umbral crítico durante un intervalo continuo mayor a 30 ciclos de simulación (Δt = 1 s).
Acción:
	retiro preventivo
	reasignación automática
	registro de anomalía
Esto cumple el KPI de detección de anomalías internas.

8. Sistema de Colas y Coordinación Multi-Agente
Cola Interna de Patrulla
Cada patrulla posee un planificador interno de tareas.
	Prioridad: emergencia critica → refuerzo → patrullaje preventivo → regreso a base
	Una tarea solo puede interrumpirse por otra de mayor prioridad.
Antes de ejecutar una tarea, la patrulla verifica si el evento sigue activo.
Esto evita:
	abandono de amenazas
	bucles de asignación
	intercambio de objetivos entre patrullas
Cola Global del Sistema
El centro de control mantiene una cola concurrente protegida por mutex:
Funciones:
	registrar amenazas
	evitar duplicaciones
	balancear carga
	asignar unidades

9. Asignación Inteligente de Recursos
La asignación de patrullas se formula como un problema de optimización.
Para cada patrulla p y evento i se define:
Score_(p,i)=w_1⋅ETA_(p,i)+w_2⋅FuelPenalty_p+w_3⋅MechanicalRisk_p+w_4⋅CoverageLoss_p-w_5⋅Severity_i
Se selecciona la patrulla cuyo Score sea la menor entre todas las posibilidades:
p^*=arg⁡(min⁡)┬p Score_(p,i)
Para severidad alta (Severityⓜ≥4)se resuelve un problema de asignación múltiple seleccionando las k mejores patrullas.
Esto transforma la decisión en optimización multi-criterio, no heurística simple.
10. Base Operativa (Cuartel)
Se introduce una estación central.
Funciones:
	reabastecimiento
	mantenimiento
	descanso operativo
El sistema puede retirar preventivamente una unidad sin perder cobertura territorial.
Esto habilito mantenimiento predictivo realista.

11. Seguridad y Auditoría
Cada decisión de la IA queda registrada:
	entrada analizada
	predicción realizada
	unidad seleccionada
	resultado obtenido

Si el módulo de IA falla:
→ activación automática de despacho manual (Etapa 3)
No existe dependencia absoluta de la IA.

12. Resultados Esperados (Medibles)
El sistema debe demostrar:
	generación automática de recomendaciones operativas y ejecución automatizada dentro del entorno simulado 
	predicción de zonas de riesgo
	reducción del tiempo de respuesta
	detección de fallos mecánicos
	balance de carga entre patrullas
	prevención de pérdida de cobertura
El término automático se refiere exclusivamente a la ejecución de acciones dentro del entorno virtual del gemelo digital. El sistema no controla vehículos reales ni sustituye al operador humano. En un despliegue real, el sistema funcionaría como sistema de apoyo a decisiones (Decision Support System), donde las recomendaciones serían validadas por un operador antes de su ejecución física.
13. Métricas de Evaluación Experimental
13.1 Tiempo de respuesta promedio 
Mide cuánto tarda una patrulla en llegar tras el incidente.
T_resp =1/N ∑_(i=1)^N▒〖(t_(llegada,i)-t_(reporte,i))〗 
13.2 Cobertura territorial
Porcentaje del mapa que tiene al menos una patrulla a distancia ≤ d.
Coverage=(|{z∈Z∶dist(p,z)≤d})/(|Z|)×100
13.3 Anticipación predictiva
Un incidente es anticipado si, antes de que ocurra, la zona ya estaba marcada como HIGH_RISK.
Prediction Rate=(Incidentes Anticipados)/(Incidentes Totales)
13.4 Precisión del modelo
	Cuantas veces se marcó una zona como peligrosa y si ocurrió algo.
Precision=(True Positives)/(True Positives+False Positives)
13.5 Recall
	Capacidad de no dejar pasar incidentes.
Recall=(True Positives)/(True Positives+False Negatives)
14. Justificación Técnica
El sistema cumple rigurosamente con los principios fundamentales de la inteligencia artificial aplicada:
	percepción (telemetría)
	memoria (historial)
	aprendizaje (actualización probabilística)
	predicción (zonas de riesgo)
	toma de decisiones autónoma asistida
Con esta fase, el proyecto pasa de ser un simulador coordinado a un sistema inteligente verificable. El sistema evoluciona de una respuesta reactiva ante incidentes a una capacidad anticipatoria, garantizando trazabilidad, seguridad operativa y supervisión humana, en plena concordancia con los requisitos de una misión crítica auditable.
 
ANEXO TÉCNICO — Especificación de Implementación y Datos Operacionales
1. Propósito del Anexo
El presente Anexo Técnico describe los componentes tecnológicos, estructuras de datos, contratos de comunicación, datasets y definiciones operativas que soportan el funcionamiento del sistema de Gemelo Digital.
El presente Anexo Técnico describe los componentes tecnológicos, estructuras de datos, contratos de comunicación, datasets y definiciones operativas que soportan el funcionamiento del sistema de Gemelo Digital.
2. Arquitectura General del Sistema
El sistema se compone de cuatro subsistemas principales:
	Unidad Vehicular (Patrulla simulada)
	Simulador del Entorno Urbano (SUE)
	Centro de Control
	Motor de Inteligencia Artificial del Gemelo Digital
Flujo operativo: Vehículo → Telemetría → Broker de Mensajes → Centro de Control → IA → Decisiones → Asignación de tareas → Vehículo
3. Identificación de la Unidad Vehicular
Cada patrulla debe poseer un identificador único persistente.
	unit_id (UUID v4)
	timestamp (Unix time)
Todo paquete de telemetría deberá incluir ambos campos para garantizar trazabilidad de origen.





4. Contrato de Telemetría
La telemetría es la representación digital del estado del vehículo.
 
5. Sensores Definidos
El sistema reconoce únicamente los siguientes sensores:
Sensor	Tipo	Unidad
GPS	Posicional	Lat/Lon
Velocidad	Derivado GPS	m/s
Combustible	Nivel	0–1
Presión neumáticos	Analógico	PSI
Estado motor	Binario	ON/OFF
Temperatura del motor	Analógico	°C

6. Definición de Anomalía
Se considera anomalía cualquier comportamiento observable que viole el modelo físico esperado del vehículo o el modelo estadístico aprendido por la IA.
	Velocidad incompatible con desplazamiento GPS
	Temperatura crítica sostenida
	Inactividad operativa anormal
	Consumo de combustible fuera de patrón
	Detenciones prolongadas fuera de zonas autorizadas


7. Modelo del Entorno (SUE)
	Red vial
	Intersecciones
	Zonas de servicio
	Eventos
El mapa se divide en una malla adaptable según el tamaño del entorno simulado (resolución dinámica).

8. Priorización de Tareas
Las tareas poseen prioridad numérica:
Prioridad	Tipo
5	Emergencia crítica
4	Emergencia alta
3	Evento reportado
2	Patrullaje preventivo
1	Reubicación logística
Regla de desempate: menor ETA → menor distancia → menor carga operativa.
9. Función de Costo Normalizada
J = w1·ETA' + w2·Cc' + w3·Cf'
ETA': tiempo estimado normalizado
Cc': carga operativa normalizada
Cf': consumo de combustible normalizado
10. Contratos de datos
Los contratos de datos incluyen eventos urbanos, asignaciones de tarea y estado global del sistema, garantizando interoperabilidad entre módulos.
 
Evento en la ciudad:
 
Asignación de tarea
 
Estado de la tarea
 
Estados válidos:
	ASSIGNED
	EN_ROUTE
	ARRIVED
	RESOLVED
	CANCELLED

 
Estado Global del Sistema
 

Resultado experimental
 

11. Política de Transmisión de Telemetría
Heartbeat periódico cada 1 segundo
Cambio de estado: transmisión inmediata
Anomalía detectada: transmisión inmediata
Apagado del motor: transmisión inmediata

12. Estados Operativos de la Unidad
	AVAILABLE
	PATROLLING
	RESPONDING
	REFUELING
	MAINTENANCE
	OUT_OF_SERVICE
	EMERGENCY_RETURN

13. Modelo Temporal del Sistema
	El simulador es la fuente de verdad temporal
	Todos los timestamps utilizan Unix Time
	El sistema puede operar en tiempo simulado acelerado
14. Dataset Inicial Sintético
El sistema inicia con simulaciones históricas generadas automáticamente para construir el mapa de riesgo inicial antes de la operación evaluada.
15. Metodología de Evaluación Experimental
	Ejecutar simulación sin IA
	Medir tiempos de respuesta
	Ejecutar simulación con IA
	Comparar métricas operativas
16. Manejo de Desconexión
	15 s sin telemetría: advertencia
	30 s sin telemetría: unidad perdida
	Reasignación automática de tareas
17. Persistencia de Datos
	Base de datos de eventos
	Archivo histórico de telemetría
	Dataset para entrenamiento del modelo

