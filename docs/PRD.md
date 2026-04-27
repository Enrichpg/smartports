# SmartPort Galicia Operations Center — PRD.md

**Version:** 1.0  
**Date:** 2026-04-27  
**Status:** Approved  
**Product Owner:** SmartPort Project Lead

---

## Executive Summary

**SmartPort Galicia Operations Center** is an intelligent, real-time operational management platform for the Galician port system. It integrates multiple ports (minimum 11, scalable to 128+) into a unified multipurpose network, enabling centralized operational control, real-time monitoring, historical analytics, ML-based forecasting and recommendations, and conversational AI assistance.

**Market Need:** Port operations require real-time visibility across distributed assets, predictive capacity for resource allocation, and intelligent decision support. Existing solutions are port-isolated, reactive, or lack integration with modern IoT and AI capabilities.

**Solution:** A FIWARE-based, NGSI-LD-compliant platform that combines:
- Real-time context (Orion-LD)
- Persistent analytics (QuantumLeap/TimescaleDB)
- Operational intelligence (FastAPI backend)
- Predictive AI (Prophet, scikit-learn)
- Conversational interface (Ollama LLM)
- Geospatial visualization (Leaflet + OpenStreetMap)

---

## 1. Vision and Goals

### 1.1 Product Vision

A unified, intelligent command center for Galician ports that provides:
- **Situational Awareness:** Real-time view of port operations across 11+ locations
- **Operational Efficiency:** Optimized berth assignment, reduced dwell times, better resource utilization
- **Predictive Capacity:** Anticipate occupancy, congestion, and service demand
- **Environmental Compliance:** Monitor air quality, weather, and regulatory thresholds
- **Decision Support:** ML recommendations and natural language queries on live data

### 1.2 Strategic Goals

1. **Multipurpose Integration** → Treat Galician ports as a unified system, not isolated entities
2. **Real-Time First** → Data propagates within seconds, not hours
3. **FIWARE Native** → Leverage official Smart Data Models, NGSI-LD compliance, ecosystem integration
4. **Scalability** → Architecture supports growing from 11 pilot ports to 128+
5. **Intelligent Operations** → ML forecasting and recommendations reduce manual workload
6. **Data-Driven Culture** → Historical analytics enable evidence-based decisions

---

## 2. Problem Statement

### Current State

- **Port Isolation:** Each Galician port operates independently with limited inter-port visibility
- **Reactive Management:** Operations are reactive (respond to events) rather than predictive
- **Data Silos:** Port data lives in separate systems; no unified query capability
- **Manual Allocation:** Berth assignment, service scheduling done manually by humans
- **Limited Forecasting:** No predictive capacity for occupancy or congestion
- **No Environmental Integration:** Weather and air quality monitored separately, not operationally
- **Language Barrier:** Operators lack natural language interface to query data

### Consequences

- Inefficient resource allocation (berths empty while ships wait)
- Missed optimization opportunities
- Delayed decision-making
- Compliance risk (environmental thresholds not monitored)
- Operator fatigue (manual processes)

### Solution Approach

SmartPort centralizes data, applies FIWARE standards, integrates real-time sensors, and adds ML and LLM layers to enable intelligent, proactive, multipurpose operations.

---

## 3. Target Users

### Primary Users

1. **Port Authorities & Operations Managers**
   - Role: Oversee multiple ports, allocate resources, manage priorities
   - Needs: System-wide visibility, KPIs, alerts, forecasts, recommendations
   - Usage: Daily, mostly strategic decisions

2. **Berth/Terminal Operators**
   - Role: Assign berths, manage port calls, track operations
   - Needs: Real-time berth status, occupancy, vessel info, quick decisions
   - Usage: Continuous, tactical control

3. **Environmental & Safety Officers**
   - Role: Monitor environmental compliance, weather, alerts
   - Needs: Sensor data, thresholds, alert history, compliance reports
   - Usage: Continuous + ad-hoc

4. **Logistics & Planning Teams**
   - Role: Forecast demand, optimize schedules, predict congestion
   - Needs: Historical trends, forecasts, comparisons across ports
   - Usage: Weekly planning + ad-hoc analysis

### Secondary Users

5. **Ship Masters & Agents**
   - Role: Check berth availability, get ETA confirmations
   - Needs: Availability calendar, recommendations, status updates
   - Usage: Pre-arrival queries, ETA tracking

6. **Analytics & BI Teams**
   - Role: Extract insights, generate reports, feed dashboards
   - Needs: Historical data access, API, export capabilities
   - Usage: Ad-hoc + scheduled reports

7. **System Administrators**
   - Role: Deploy, monitor, maintain the platform
   - Needs: Health checks, logs, configuration, backup/restore
   - Usage: Continuous monitoring + maintenance

---

## 4. Scope: Galician Port Network

### 4.1 Geographic & Organizational Scope

**Minimum Pilot Network (11 ports):**
- A Coruña (Port Authority)
- Vigo (Port Authority)
- Ferrol-San Cibrao (Port Authority)
- Marín (Port Authority)
- Vilagarcía de Arousa (Port Authority)
- Ribeira
- Burela
- Celeiro
- Cangas
- Baiona
- Viveiro

**Expansion Scope (future, 10+):**
- Cariño, Cee, Laxe, A Pobra do Caramiñal, and others
- Scalable to full Portos de Galicia network (128 ports)

**Administrative Structure:**
- State-managed: 5 Port Authorities (Vigo, Marín, Vilagarcía, A Coruña, Ferrol-San Cibrao)
- Regional: Portos de Galicia (122 additional)
- Platform support: All ports as unified system

### 4.2 Operational Scope

**Entities Managed:**
- Ports (geographic, operational, administrative data)
- Berths (docks, mooring points, service areas)
- Vessels (commercial ships, dimensions, characteristics)
- Port Calls (vessel visits, lifecycle, operations)
- Operations (cargo handling, services, maintenance)
- Sensors (environmental, meteorological, operational)
- Authorizations (documentation, insurance, compliance)
- Pricing & Availability (tariffs, forecasting)

**Operations Covered:**
- General cargo, containers, breakbulk, rolling stock
- Liquid cargo (tanker operations)
- Services (bunkering, provisioning, repairs)
- Environmental monitoring
- Security & authorization

**Not in Scope (Phase 1):**
- Vessel design/classification (reference only via MasterVessel)
- Crew management
- Cargo manifest details (reference to port call only)
- Financial billing (tracked, not calculated)
- Supply chain planning (outside port gates)

---

## 5. Core Requirements

### 5.1 Functional Requirements by Module

#### **Module 1: Port Network Visualization**

**FR-1.1** Global map showing all Galician ports with current status  
**Acceptance Criteria:**
- [ ] Leaflet map displays 11+ ports with correct coordinates (WGS84)
- [ ] Each port shows real-time KPI (occupancy %, vessels count, alerts count)
- [ ] Click on port opens detailed port view
- [ ] Map updates in real-time (WebSocket-driven)
- [ ] Zoom, pan, basemap toggle (OpenStreetMap default)

**FR-1.2** Per-port dashboard showing operational state  
**Acceptance Criteria:**
- [ ] Displays port name, authority, contact info
- [ ] Shows berth grid (visual or table) with occupancy
- [ ] Shows live vessel list with ETA/ETD
- [ ] Shows active operations count
- [ ] Shows alert list (latest 10)
- [ ] Shows port KPIs (occupancy trend, avg dwell time, revenue)

#### **Module 2: Berth Management**

**FR-2.1** Real-time berth availability view  
**Acceptance Criteria:**
- [ ] List/grid showing all berths in a port with status (free, reserved, occupied, maintenance)
- [ ] Filter by berth type, draft, length, service
- [ ] Show occupancy timeline (expected, actual, next expected)
- [ ] Show pricing for each berth category
- [ ] Color-coded by status (green=free, yellow=reserved, red=occupied, gray=maintenance)
- [ ] Updates every 5 seconds

**FR-2.2** Berth occupancy forecasting  
**Acceptance Criteria:**
- [ ] Show 7-day occupancy forecast (% occupancy per day)
- [ ] ML model (Prophet) trained on historical 90-day data
- [ ] Confidence intervals displayed
- [ ] Updated daily
- [ ] Forecast available via API

**FR-2.3** Berth recommendation engine  
**Acceptance Criteria:**
- [ ] Given vessel specs (type, LOA, draft, cargo), recommend optimal berths
- [ ] Ranking based on: availability, service match, price, distance to cranes
- [ ] Rationale shown (why this berth?)
- [ ] Available via API and UI widget
- [ ] ML model (Random Forest) on historical assignment data

#### **Module 3: Port Call Lifecycle Management**

**FR-3.1** Port call creation and lifecycle tracking  
**Acceptance Criteria:**
- [ ] Create port call with vessel, ETA, services requested
- [ ] Transition states: expected → active → operations → completed
- [ ] Each state change logged with timestamp
- [ ] Automatic alerts for delay/no-show
- [ ] Historical archive of completed port calls

**FR-3.2** Expected vs actual tracking  
**Acceptance Criteria:**
- [ ] ETA vs actual arrival time tracked
- [ ] Delay alerts generated (>6h difference)
- [ ] Actual berth vs planned displayed
- [ ] Dwell time calculated (actual minus arrival)
- [ ] KPIs: on-time performance, avg dwell time per port

#### **Module 4: Operations Logging**

**FR-4.1** Operational events recording  
**Acceptance Criteria:**
- [ ] Log operations: cargo load, cargo unload, bunkering, repairs, inspections
- [ ] Each operation: type, start time, end time, units (tons, barrels, etc.), personnel
- [ ] Linked to port call and berth
- [ ] Real-time or near-real-time entry
- [ ] Searchable by port call, berth, operation type, date range

**FR-4.2** Operational KPIs  
**Acceptance Criteria:**
- [ ] Cargo tonnage by operation type, port, vessel
- [ ] Service hours (berth occupancy time)
- [ ] Operational efficiency (cargo/hour)
- [ ] Revenue-aligned metrics (fees by service type)

#### **Module 5: Authorization & Compliance**

**FR-5.1** Vessel authorization tracking  
**Acceptance Criteria:**
- [ ] Maintain authorizations per vessel: insurance, certifications, port permits
- [ ] Flag vessels with expired/missing authorizations
- [ ] Alert operators before vessel arrival if unauthorized
- [ ] Block port call if critical authorization missing (configurable)
- [ ] Authorization history and updates tracked

**FR-5.2** Compliance & alert rules  
**Acceptance Criteria:**
- [ ] Define thresholds for environmental, safety, operational alerts
- [ ] Rule engine evaluates conditions against real-time data
- [ ] Alert generated and broadcast if threshold exceeded
- [ ] Alert history with resolution status

#### **Module 6: Environmental Monitoring**

**FR-6.1** Environmental sensor integration  
**Acceptance Criteria:**
- [ ] Ingest air quality data (PM2.5, PM10, NO2, SO2, CO)
- [ ] Ingest weather data (wind, temperature, humidity, pressure)
- [ ] Associate sensors with port facilities or zones
- [ ] Display latest observations in dashboard
- [ ] Historical time-series queryable

**FR-6.2** Environmental alerts  
**Acceptance Criteria:**
- [ ] Alert if air quality threshold exceeded
- [ ] Alert if weather condition hazardous (wind >40 km/h, etc.)
- [ ] Alert if visibility poor (<500m)
- [ ] Alerts logged and visible to environmental officers
- [ ] Configurable thresholds per port, zone, parameter

#### **Module 7: Historical Analytics & Dashboards**

**FR-7.1** Historical analytics views  
**Acceptance Criteria:**
- [ ] Query occupancy trends (daily, weekly, monthly)
- [ ] Query dwell time statistics (min, max, avg, median)
- [ ] Query operational volume (cargo tonnage, operations count)
- [ ] Query revenue trends
- [ ] Compare across ports (benchmark)
- [ ] Export to CSV

**FR-7.2** Embedded Grafana dashboards  
**Acceptance Criteria:**
- [ ] Grafana queries QuantumLeap/TimescaleDB directly
- [ ] Pre-built dashboards for port manager, berth operator, environmental officer
- [ ] Custom dashboard builder available
- [ ] Alerts integrated with Grafana notification channels

#### **Module 8: Forecasting & Predictive Analytics**

**FR-8.1** Occupancy forecasting  
**Acceptance Criteria:**
- [ ] Prophet model trained on 90-day historical occupancy
- [ ] Generate 7-day forecast
- [ ] Forecast per port, per berth category, or global
- [ ] Confidence intervals included
- [ ] Publish forecast as NGSI-LD BoatPlacesAvailable entities
- [ ] Retrain weekly

**FR-8.2** Congestion prediction  
**Acceptance Criteria:**
- [ ] Alert if forecast shows >85% occupancy
- [ ] Predict conflict (two vessels assigned same berth)
- [ ] Recommend alternative berths or ETA adjustment

#### **Module 9: Conversational AI Assistant**

**FR-9.1** Natural language query interface  
**Acceptance Criteria:**
- [ ] User asks question in Galician, Spanish, or English
- [ ] LLM (Ollama + Llama) interprets query
- [ ] LLM calls backend tools (Orion queries, QL queries, ML models)
- [ ] LLM composes answer in user's language
- [ ] Example queries:
  - "¿Qué puertos tienen ocupación máxima ahora?"
  - "¿Hay atraques libres en A Coruña para un buque de 200m?"
  - "¿Cuál es la ocupación promedio en Vigo esta semana?"

**FR-9.2** Tool calling against backend  
**Acceptance Criteria:**
- [ ] LLM can call functions: get_port_occupancy, get_berth_availability, predict_occupancy
- [ ] Returns data in structured format
- [ ] Handles multi-step queries (e.g., forecast then compare)

#### **Module 10: Real-Time WebSocket Updates**

**FR-10.1** Live data streaming  
**Acceptance Criteria:**
- [ ] Frontend WebSocket connections receive updates on:
  - Berth status changes
  - Vessel arrivals/departures
  - New alerts
  - Operational events
- [ ] Latency <2 seconds
- [ ] Connection resilience (auto-reconnect on disconnect)
- [ ] Dashboard UI updates without page refresh

#### **Module 11: 3D Immersive Visualization**

**FR-11.1** 3D port model  
**Acceptance Criteria:**
- [ ] 3D view of port layout (Three.js)
- [ ] Berths rendered as 3D objects
- [ ] Vessels rendered with correct dimensions/colors
- [ ] Sensors visible on map
- [ ] Click/hover for details
- [ ] Real-time state sync

#### **Module 12: System Administration & Monitoring**

**FR-12.1** Health and status monitoring  
**Acceptance Criteria:**
- [ ] Health endpoint: GET /health returns status of all services
- [ ] Metrics exported (Prometheus format): requests, latency, errors, DB connections
- [ ] Logs aggregated (structure: timestamp, level, service, message, context)
- [ ] Alerts for service failures

---

### 5.2 Non-Functional Requirements

#### **Performance**

- **NF-1.1** API Response Time
  - [ ] 95% of requests <500ms
  - [ ] 99% of requests <2s
  - [ ] Measured under 100 concurrent users

- **NF-1.2** Real-Time Data Propagation
  - [ ] Sensor data → Orion: <1s
  - [ ] Orion → QuantumLeap: <1s (via subscription)
  - [ ] Backend → WebSocket: <2s
  - [ ] Total sensor to UI: <5s

- **NF-1.3** Database Performance
  - [ ] QL queries on 1M time-series points: <5s
  - [ ] Historical analytics queries: <10s
  - [ ] Backup completes within 1 hour

#### **Scalability**

- **NF-2.1** User Concurrency
  - [ ] Support 100+ concurrent users
  - [ ] Linear degradation beyond 100

- **NF-2.2** Data Volume
  - [ ] Support 10,000+ daily port calls
  - [ ] 1M+ observations per day (sensors)
  - [ ] 1+ year historical retention

- **NF-2.3** Geographic Expansion
  - [ ] Architecture supports 128+ ports without redesign
  - [ ] Multipurpose model scales horizontally

#### **Reliability**

- **NF-3.1** Availability
  - [ ] Target: 99% uptime (SLA)
  - [ ] Planned maintenance: monthly, <1h

- **NF-3.2** Data Durability
  - [ ] No data loss (transactional DB commits)
  - [ ] Backup every 6 hours to geographically different location
  - [ ] Recovery Time Objective (RTO): <4 hours
  - [ ] Recovery Point Objective (RPO): <6 hours

- **NF-3.3** FIWARE Resilience
  - [ ] Orion LD failover to backup instance
  - [ ] QuantumLeap decoupled from Orion (async via broker)
  - [ ] Backend resilient to Orion/QL temporary failures

#### **Security**

- **NF-4.1** Authentication & Authorization
  - [ ] OAuth2 or JWT for API authentication
  - [ ] Role-based access control (RBAC)
  - [ ] Operator role: view own port
  - [ ] Manager role: view all ports + configuration
  - [ ] Admin role: all permissions

- **NF-4.2** Data Protection
  - [ ] HTTPS/TLS for all external communication
  - [ ] Database credentials in .env, not versioned
  - [ ] API keys rotated quarterly
  - [ ] Audit logs for sensitive operations (delete, config change)

- **NF-4.3** Network Security
  - [ ] Nginx reverse proxy with rate limiting (100 req/min per IP)
  - [ ] CORS configured for approved origins only
  - [ ] SQL injection prevention (parameterized queries)
  - [ ] NGSI-LD payload validation

#### **Compliance & Governance**

- **NF-5.1** NGSI-LD & Standards
  - [ ] 100% NGSI-LD v1.6 compliance
  - [ ] Reutilization of Official Smart Data Models
  - [ ] Linked data principles (URIs, RDF semantics optional)

- **NF-5.2** Data Privacy
  - [ ] GDPR compliance (if applicable): personal data anonymized
  - [ ] Data retention policy: operational data 1 year, analytics 3 years
  - [ ] Right to deletion implemented

- **NF-5.3** Environmental & Port Regulations
  - [ ] Air quality thresholds per EU regulations
  - [ ] Weather safety thresholds per maritime law
  - [ ] Authorization compliance with Puertos del Estado rules

#### **Operational**

- **NF-6.1** Monitoring & Observability
  - [ ] Structured logging (JSON format)
  - [ ] Centralized logs accessible (future: ELK stack)
  - [ ] Distributed tracing optional (future)
  - [ ] Metrics dashboard (Prometheus + Grafana)

- **NF-6.2** Configuration Management
  - [ ] All config via environment variables or config files
  - [ ] No hardcoded secrets
  - [ ] Feature flags for experimental features
  - [ ] Version-controlled configuration (except secrets)

- **NF-6.3** Deployment & DevOps
  - [ ] Docker containers for all services
  - [ ] docker-compose for local development
  - [ ] Kubernetes manifests (future) for production
  - [ ] CI/CD pipeline (future): auto-test on push, deploy on merge

#### **Usability**

- **NF-7.1** UI/UX
  - [ ] Dashboard loads in <3 seconds
  - [ ] Mobile-responsive (tablets at minimum)
  - [ ] Dark mode option
  - [ ] Keyboard navigation supported

- **NF-7.2** Documentation
  - [ ] README with 15-minute quickstart
  - [ ] API documentation (OpenAPI/Swagger)
  - [ ] Data model documentation with examples
  - [ ] Troubleshooting guide

---

## 6. Use Cases

### UC-1: Real-Time Berth Status Dashboard

**Actor:** Berth Operator  
**Scenario:** Operator logs in, sees all berths in assigned port with current occupancy, next scheduled vessel, and alerts.

**Flow:**
1. Login to web UI
2. Dashboard loads with port's berth grid
3. Each berth shows: name, type, status (free/occupied/reserved), vessel name if occupied, ETA of next vessel
4. Color-coding: green=free, yellow=reserved, red=occupied
5. Click berth → details (dimensions, services, pricing, operations log)

**Acceptance:**
- [ ] Dashboard loads in <3s
- [ ] Data refreshes every 5s
- [ ] Status accurate within 30s of change

### UC-2: Berth Recommendation for Incoming Vessel

**Actor:** Port Agent or Operator  
**Scenario:** Ship calls ahead with arrival notice. Operator needs to assign a berth optimally.

**Flow:**
1. Open "New Port Call" form
2. Enter: vessel name, LOA (length), draft, cargo type, service duration
3. Click "Recommend Berth"
4. System shows ranked list: Berth A (score 9.2 → available now, matches specs), Berth B (score 8.1 → available tomorrow), Berth C (score 7.5 → requires crane repositioning)
5. Click "Assign" to confirm

**Acceptance:**
- [ ] Recommendation completes in <2s
- [ ] Ranking based on availability, service match, efficiency
- [ ] Rationale displayed
- [ ] Manual override possible

### UC-3: Environmental Alert on High Pollution

**Actor:** Environmental Officer  
**Scenario:** Air quality sensor detects PM2.5 above threshold. System alerts.

**Flow:**
1. Sensor publishes data: PM2.5 = 85 µg/m³ (threshold: 75)
2. IoT Agent transforms to NGSI-LD AirQualityObserved entity
3. Orion updates entity
4. Backend rule engine checks threshold
5. Alert triggered and broadcast
6. UI shows red alert banner: "Air quality poor in Port A - PM2.5 85 µg/m³"
7. Environmental officer sees alert, notifies port authority, operational pause possible

**Acceptance:**
- [ ] Alert generated within 10s of threshold breach
- [ ] Alert visible in UI, email, SMS (configurable)
- [ ] Alert history logged

### UC-4: Occupancy Forecasting for Capacity Planning

**Actor:** Port Manager  
**Scenario:** Manager needs to forecast occupancy for the next week to plan maintenance and staffing.

**Flow:**
1. Open "Forecasting" view
2. Select port, berth category, time range (7 days)
3. View chart: occupancy % over time with confidence bands
4. See prediction: Tuesday 85% occupancy, Wednesday peak 92% occupancy
5. Export to spreadsheet for planning

**Acceptance:**
- [ ] Forecast generated daily
- [ ] Accuracy >75% on 7-day horizon (MAPE)
- [ ] Chart interactive (hover, zoom)
- [ ] Export works

### UC-5: Conversational Query on Occupancy

**Actor:** Port Authority Official  
**Scenario:** Director asks: "Which ports have the highest occupancy right now?"

**Flow:**
1. Open LLM chat widget
2. Type: "¿Qué puertos tienen la ocupación más alta ahora?"
3. LLM processes query, calls backend GET /ports/occupancy
4. Backend returns real-time occupancy from Orion
5. LLM composes answer: "Vigo has 92% occupancy, A Coruña 78%, Ferrol 65%"
6. Director sees answer in chat

**Acceptance:**
- [ ] Query response in <3s
- [ ] Answer factually correct (data-backed)
- [ ] Supports follow-up questions

### UC-6: Operational Event Logging

**Actor:** Cargo Handler / Terminal Operator  
**Scenario:** Cargo unloading operation completes. Operator logs event.

**Flow:**
1. Worker or supervisor logs into mobile/tablet version
2. Selects port call / berth
3. Logs operation: "Unload general cargo"
4. Enters: start time, end time, tonnage (500 tons)
5. Clicks "Submit"
6. Event recorded in real-time
7. Manager dashboard updates with new operational metrics

**Acceptance:**
- [ ] Mobile UI responsive on tablet
- [ ] Submission confirms in <2s
- [ ] Data visible in dashboard within 10s

---

## 7. Acceptance Criteria Summary

### General Criteria (All Features)

- [ ] Code passes tests (pytest coverage >80%)
- [ ] NGSI-LD compliance verified
- [ ] No hardcoded secrets
- [ ] Documentation updated (PRD, data_model, architecture, README)
- [ ] Performance benchmarks met
- [ ] UI/UX tested on target browsers (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility baseline (WCAG 2.1 AA target)

### Data Criteria

- [ ] All NGSI-LD entities include @context
- [ ] Dynamic attributes include observedAt
- [ ] Relationships use correct NGSI Relationship type
- [ ] Geospatial data use GeoProperty
- [ ] No missing or null values in critical fields

### Integration Criteria

- [ ] Orion integration: create, read, update, delete entities
- [ ] QuantumLeap integration: query time-series correctly
- [ ] MQTT integration: receive, parse, transform sensor data
- [ ] Backend API: all routes documented, tested
- [ ] WebSocket: connections stable, messages reliable

---

## 8. Out of Scope (Phase 1)

The following are NOT included in Phase 1 but may be future enhancements:

- Vessel design/construction data (reference only)
- Crew management and scheduling
- Cargo manifest and commercial documents (reference to port call only)
- Financial invoicing and payment processing (data collection only)
- Supply chain planning upstream/downstream of ports
- Customs and immigration clearance tracking
- International conventions (SOLAS, MARPOL) compliance database
- Vessel acquisition/disposition lifecycle
- Port infrastructure projects and capital planning
- Tariff optimization algorithms
- Insurance claims processing

---

## 9. Success Metrics

### Functional Success

- ✓ 95%+ of planned functional requirements implemented
- ✓ All 15 NGSI-LD entities operational
- ✓ All 11 pilot ports loaded and operational
- ✓ Real-time data flow end-to-end (sensor to UI <5s)
- ✓ ML models trained and predictions accurate (>75% MAPE)
- ✓ LLM assistant responds to sample queries correctly

### Operational Success

- ✓ System uptime >99%
- ✓ <2s API response time p95
- ✓ <1s real-time propagation latency
- ✓ 0 data loss events

### User Success

- ✓ Usability testing: 8/10 average score
- ✓ User adoption: 80%+ of intended users active within 1 month
- ✓ Feedback: 75%+ positive sentiment

### Technical Success

- ✓ 100% NGSI-LD compliance
- ✓ 80%+ code test coverage
- ✓ 0 critical security vulnerabilities
- ✓ Architecture supports 128+ ports expansion

---

## 10. Dependencies & Risks

### External Dependencies

- **FIWARE Ecosystem:** Orion-LD, QuantumLeap, IoT Agent JSON availability
- **Smart Data Models:** Official definitions stability and versioning
- **Weather/Environmental Data:** 3rd party sensor providers (accuracy, uptime)
- **Computational Resources:** ML training time, inference latency
- **Network Infrastructure:** Port site connectivity, MQTT broker availability

### Internal Dependencies

- **Backend API:** Must be operational for frontend to function
- **Orion-LD:** Context broker downtime → no real-time updates
- **QuantumLeap:** Time-series downtime → no historical analytics
- **PostgreSQL/TimescaleDB:** Database downtime → data loss risk

### Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Orion LD unavailable | Medium | High | Implement failover, queue unprocessed updates |
| Poor forecast accuracy | Medium | Medium | Retrain weekly, tune Prophet hyperparameters |
| Network latency >5s | Low | Medium | Optimize queries, add caching |
| NGSI-LD spec changes | Low | Medium | Version lock, monitor official repo |
| User adoption <50% | Medium | High | UX testing, user training, phased rollout |

---

## 11. Timeline & Phases

### Phase 1: Foundation (Weeks 1-2)
- Documentation (this PRD, architecture, data model)
- Infrastructure (docker-compose, nginx, config)
- Seed data and initial population

### Phase 2: Backend (Weeks 3-5)
- FastAPI server, health checks
- Orion integration (CRUD)
- QuantumLeap queries
- Initial REST API routes

### Phase 3: Frontend Dashboard (Weeks 6-8)
- Leaflet map with ports
- Berth grid and status
- Real-time WebSocket integration
- Alerts view

### Phase 4: ML & Real-Time (Weeks 9-10)
- Prophet forecasting model training
- ML recommendation engine
- MQTT simulator
- Real-time data flow end-to-end

### Phase 5: Advanced Features (Weeks 11-12)
- 3D visualization
- Environmental monitoring dashboard
- LLM assistant integration
- Historical analytics / Grafana

### Phase 6: Polish & Release (Week 13+)
- Testing and bug fixes
- Performance optimization
- Documentation completion
- Production deployment

---

## 12. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-27 | Product Lead | Initial comprehensive PRD |

---

**Approval Status:** Draft → Review → Approved  
**Next Review:** After Phase 1 completion  
**Contact:** SmartPort Project Lead
