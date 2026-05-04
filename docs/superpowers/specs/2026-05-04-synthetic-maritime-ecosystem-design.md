# Especificación: Sistema Sintético Masivo para Puertos Gallegos

**Fecha:** 2026-05-04  
**Versión:** 1.0  
**Autor:** Brainstorming + Design Phase  
**Estado:** Approved for Implementation  

---

## 1. Visión General

Implementar un **sistema completo de generación de datos sintéticos realistas** que populate los puertos gallegos con un ecosistema portuario vivo, creíble y dinámico. El sistema debe generar:

- **4000-5000 buques activos** con arquetipos distintos y comportamientos coherentes
- **300-350 atraques heterogéneos** distribuidos entre 8 puertos con identidad propia
- **150-200 sensores IoT** con observaciones ambientales periódicas
- **Histórico de 60-90 días simulados** para entrenar modelos de predicción
- **Simulación dinámica continua** con escala de tiempo acelerada (1 hora real = 1 día simulado)

El sistema debe ser **realista, variado, coherente, escalable y usable** sin degradación de rendimiento.

---

## 2. Requisitos Funcionales

### 2.1 Generación de Entidades Base

#### Puertos (8 entidades, fijas)
- **Identificadores:** `urn:ngsi-ld:Port:galicia-{key}` donde key ∈ {a-coruna, vigo, ferrol, marin, vilagarcia, ribeira, burela, baiona}
- **Propiedades por puerto:**
  - nombre oficial
  - coordenadas reales
  - autoridad responsable
  - tipo principal (comercial, pesquero, mixto, recreativo)
  - municipio y ubicación
  - capacidad relativa
  - relación a atraques y sensores

#### Atraques / Berths (~300-350 total)
- Distribuidos heterogéneamente entre puertos (no uniformes)
- **Propiedades:**
  - id único estable (`urn:ngsi-ld:Berth:galicia-{puerto}-{zona}-{num}`)
  - nombre semirealista (ej: "Muelle de Carga A", "Terminal Pesquera Sur")
  - puerto propietario (relationship)
  - longitud/calado (según tipo puerto y buques esperados)
  - especialización (carga general, pesquería, ro-ro, contenedores, recreo)
  - estado (available, occupied, maintenance)
  - buque asignado actual (si occupied)
- **Distribución de ejemplo:**
  - A Coruña: 50 atraques (mercantes dominantes)
  - Vigo: 60 atraques (pesqueros + mercantes)
  - Ferrol: 45 atraques (navales + comerciales)
  - Marín: 25 atraques (pesqueros pequeños)
  - Vilagarcía: 35 atraques (mixtos)
  - Ribeira: 30 atraques (pesquería especializada)
  - Burela: 20 atraques (flota costera)
  - Baiona: 15 atraques (recreo, histórico)

#### Buques / Vessel Instances (~4000-5000 total)
- **Arquetipos (con ratios realistas):**
  - Pesqueros: ~35% (~1400-1750 buques) — ciclos 6-36 horas en puerto
  - Mercantes: ~25% (~1000-1250) — rutas entre puertos 4-16 horas
  - Auxiliares/Remolcadores: ~20% (~800-1000) — alta movilidad local
  - Llegadas oceánicas: ~15% (~600-750) — entrada desde mar abierto
  - Recreativos/Deportivos: ~5% (~200-250) — puertos pequeños

- **Propiedades por buque:**
  - id único (`urn:ngsi-ld:Vessel:galicia-{tipo}-{num}`)
  - nombre verosímil (no secuencial)
  - tipo NGSI (Vessel)
  - master vessel reference (relationship a VesselMaster)
  - estado actual (DOCKED, MOVING, ANCHORED, APPROACHING_PORT, LEAVING_PORT, etc.)
  - posición geográfica [lon, lat] en tiempo actual
  - velocidad (knots) y rumbo (grados) si MOVING
  - atraque asignado si DOCKED
  - puerto si está en escala
  - última actualización timestamp (ISO 8601)
  - atributos técnicos: eslora (m), manga (m), calado (m), tonelaje bruto

- **Nombres:** Algoritmo generativo semirealista
  - Pesqueros: prefijos tipo "Mar", "Ría", "Pesca" + nombres de lugar/característica
  - Mercantes: nombres comerciales tipo "Atlantic", "Trader", "Express"
  - Auxiliares: "Remolcador + Ciudad" o números de flota
  - Sin secuencias triviales, buena variedad

#### Master Vessels (~300-400 entries en catálogo base)
- Registro de tipos/características de buques
- Reutilizado para crear instancias dinámicamente
- **Propiedades:**
  - IMO (ficticio pero único)
  - Nombre tipo
  - Ship type (container ship, bulk carrier, fishing vessel, etc.)
  - Dimensiones típicas
  - Tonelaje
  - Año construido (para verosimilitud)
  - Flag state

#### Entidades de Autorización y Disponibilidad

**BoatAuthorized** (~500-800 registros)
- Autorizaciones vinculadas a buques, puertos, zonas o categorías
- Estados: authorized, restricted, expired, temporary, permanent
- **Coherencia:** Si un buque está authorizado, puede atracar en ese puerto

**BoatPlacesAvailable** (~40-50 registros por categoría×puerto)
- Disponibilidad dinámica de plazas por categoría y puerto
- Ligado a ocupación real de atraques
- Se actualiza con simulación

**BoatPlacesPricing** (~40-50 registros)
- Precios heterogéneos por puerto, categoría, tipo de servicio
- Variación realista (no uniformes)
- Estancia corta vs. larga

#### Sensores IoT (~150-200 devices)

**Distribución realista:**
- Estaciones de aire: 1-2 por puerto grande (A Coruña, Vigo), 0-1 pequeño
- Estaciones weather: 1-2 por puerto (costa)
- Sensores mixtos en zonas de máxima densidad

**Propiedades por device:**
- id (`urn:ngsi-ld:Device:galicia-{tipo}-{puerto}-{num}`)
- nombre (ej: "Estación de Aire A Coruña 01")
- tipo (AirQualityDevice, WeatherDevice)
- puerto propietario
- coordenadas realistas dentro de puerto
- estado operativo (operational, maintenance, offline)
- fecha de última calibración
- frecuencia de reporte (ej: cada 15 minutos simulados)

#### Observaciones Ambientales (Generadas dinámicamente)

**AirQualityObserved** (periódicas, cada sensor cada N minutos sim)
- Timestamp
- Sensor reference
- Mediciones:
  - PM2.5 (µg/m³): rango típico 15-30, picos 40-60
  - PM10 (µg/m³): rango típico 25-50, picos 60-100
  - NO2 (µg/m³): rango típico 40-60 costero
  - O3 (µg/m³): rango 30-80 según estación
  - CO (mg/m³): rango 0.3-1.0
  - SO2 (µg/m³): rango 5-20
  - AQI sintético (0-500 scale)

**WeatherObserved** (periódicas)
- Timestamp
- Sensor reference
- Mediciones:
  - Temperatura (°C): rango 8-22 según estación
  - Humedad relativa (%): rango 60-95
  - Presión (hPa): rango 1000-1020
  - Velocidad viento (m/s): rango 2-15
  - Dirección viento (°): 0-360
  - Racha máxima (m/s): rango 5-25
  - Precipitación (mm): 0-10 si lluvia
  - Nubosidad (%): 0-100

- **Realismo:**
  - Variaciones suaves en tiempo (no saltos aleatorios)
  - Correlación entre sensores cercanos
  - Ciclos diarios plausibles
  - Valores acotados a rangos Galicia costera

### 2.2 Simulación Dinámica

#### Escala Temporal
- **1 hora real = 1 día simulado** (24x aceleración)
- Permite ver movimiento dinámico rápidamente en demos
- Coherencia: cambios graduales, sin teletransportes

#### Máquina de Estados por Arquetipo

**Pesqueros:**
```
DOCKED (8-18h sim) 
  → LEAVING_PORT (1h) 
  → FISHING (6-20h) 
  → RETURNING (1-2h) 
  → DOCKED
```

**Mercantes:**
```
DOCKED (12-48h sim) 
  → LEAVING_PORT (2h) 
  → MOVING (4-16h entre puertos) 
  → APPROACHING_PORT (1h) 
  → DOCKED
```

**Auxiliares/Remolcadores:**
```
IN_HARBOR_TRANSIT (1-3h) ↔ DOCKED (2-6h) ↔ MANEUVERING (0.5-1h)
```

**Llegadas Oceánicas:**
```
OPEN_SEA (histórico)
  → APPROACHING_PORT (2-4h)
  → DOCKED
```

#### Reglas de Coherencia
1. Buque DOCKED → asignado a atraque concreto (relación)
2. Buque MOVING → velocidad/rumbo fisicamente plausibles
3. Buque APPROACHING_PORT → coordenadas acercándose gradualmente
4. Buque ANCHORED → cercano a puerto pero fuera de atraques
5. Ocupación de atraques → afecta llegadas (espera, fondeo si lleno)
6. Cambios de estado → timestamped, sin saltaos
7. Rutas entre puertos → trayectorias plausibles

#### Tick de Simulación (Celery Task)
- **Frecuencia:** cada 5 minutos reales = 2 días simulados
- **Por tick, actualizar:**
  - Posiciones de buques (avanzar trayectoria)
  - Estados (transiciones coherentes)
  - Ocupación de atraques
  - Disponibilidad de plazas
  - Observaciones IoT (nuevas mediciones)
  - Eventos: berth.updated, vessel.moved, occupancy.changed, etc.
  - Publica a Redis/WebSocket para frontend

---

## 3. Arquitectura Técnica

### 3.1 Módulos (Arquitectura Híbrida)

```
backend/
├── generators/
│   ├── __init__.py
│   ├── synthetic_data_generator.py       # Orquestador principal
│   ├── port_profiles.py                  # Definiciones de puertos
│   ├── vessel_factory.py                 # Factory de buques por arquetipo
│   ├── berth_generator.py                # Generador de atraques
│   ├── sensor_factory.py                 # Factory de dispositivos IoT
│   ├── scenario_config.py                # Parámetros globales
│   ├── simulation_initializer.py         # Crea histórico inicial
│   └── data_validator.py                 # Validaciones de coherencia
│
├── services/
│   ├── ngsi_builders.py                  # REUTILIZAR (existente)
│   ├── orion_service.py                  # REUTILIZAR (existente)
│   ├── simulation_engine.py              # NUEVO: lógica de tick
│   └── ...
│
├── api/routes/
│   └── admin.py                          # NUEVO: endpoint regenerate
│
└── tasks/
    └── simulation_tasks.py               # Celery: periodic tick
```

### 3.2 Integración con Stack Existente

- **Orion-LD:** Almacena todas las entidades NGSI-LD
- **PostgreSQL:** Auditoría, histórico de cambios
- **Redis:** Cache de entidades, cola Celery
- **Celery:** Worker ejecuta tick cada 5 min reales
- **WebSocket:** Eventos de simulación → frontend en vivo
- **Nginx:** Reverse proxy, cache

### 3.3 Flujos de Integración

#### Flujo A: Inicialización (Startup)
```
docker compose up -d
→ Backend startup hook
  → python backend/scripts/load_seed.py --synthetic-xlarge
    → synthetic_data_generator.generate_all()
      ├→ vessel_factory.generate_4000_5000_vessels()
      ├→ berth_generator.generate_300_350_berths()
      ├→ sensor_factory.generate_150_200_sensors()
      └→ simulation_initializer.create_historical_movement(days=90)
    → OrionService.batch_create()
      → Orion-LD + PostgreSQL
    → Redis cache (precalcula métricas)
→ Backend ready, Celery inicia tick
```

#### Flujo B: Regeneración (Endpoint REST)
```
POST /api/v1/admin/synthetic/regenerate
{
  "volume": "xlarge",
  "historical_days": 90,
  "seed": 42
}
→ async job en background
→ {status: "regenerating", eta_seconds: 120}
```

#### Flujo C: Simulación Continua
```
[Celery Beat, cada 5 min reales]
→ simulation_tasks.tick_simulation()
  → simulation_engine.advance_time(delta=2_days_sim)
    ├→ Actualiza posiciones/estados de buques
    ├→ Recalcula ocupación de atraques
    ├→ Genera observaciones IoT
    └→ Publica eventos a Redis → WebSocket → Frontend
```

---

## 4. Calidad de Dato

### 4.1 Validaciones Automáticas

```
✓ test_no_duplicate_ids()
✓ test_all_references_valid()
✓ test_coordinate_validity()
✓ test_state_machine_coherence()
✓ test_occupancy_bounds()
✓ test_name_variety()
✓ test_distribution_heterogeneity()
✓ test_environmental_realism()
✓ test_ngsi_ld_format()
```

### 4.2 Coherencia Referencial

- Cada buque referencia master vessel válido
- Cada atraque referencia puerto válido
- Cada observación referencia sensor válido
- Ocupación = conteo actual de DOCKED

---

## 5. Parámetros de Configuración

### scenario_config.py

```python
SCENARIOS = {
    "small": {"num_vessels": 300, "num_berths": 50, "num_sensors": 40},
    "medium": {"num_vessels": 1500, "num_berths": 150, "num_sensors": 80},
    "large": {"num_vessels": 2500, "num_berths": 180, "num_sensors": 100},
    "xlarge": {"num_vessels": 4500, "num_berths": 320, "num_sensors": 180}
}

VESSEL_ARCHETYPES = {
    "fishing": {"ratio": 0.35},
    "merchant": {"ratio": 0.25},
    "auxiliary": {"ratio": 0.20},
    "oceanic": {"ratio": 0.15},
    "recreational": {"ratio": 0.05}
}

SIMULATION = {
    "time_acceleration": 24,
    "tick_interval_minutes": 5,
    "days_per_tick": 2
}
```

---

## 6. Impacto en UI

- **Dashboard:** Métricas actualizadas en vivo
- **Mapa:** 4500 buques con clustering
- **Tablas:** Filtrable por puerto/tipo/estado
- **WebSocket:** Sin reload de página

---

## 7. Requisitos No Funcionales

- ✅ Inicialización: <5 minutos
- ✅ Tick simulación: <30 segundos
- ✅ Mapa: <200ms para 4500+ marcadores
- ✅ Reproducibilidad: seed configurable
- ✅ Escalabilidad: parámetro scenario config

---

## 8. Éxito Criteria

✅ 4500 buques generados sin error  
✅ 320 atraques distribuidos realísticamente  
✅ Todos los tests de validación pasan  
✅ Dashboard muestra métricas actualizadas  
✅ Mapa renderiza 4500+ buques sin lag  
✅ WebSocket actualiza en vivo  
✅ Endpoint REST regenerate funcional  

---

**Especificación Completa. Listo para Implementación.**
