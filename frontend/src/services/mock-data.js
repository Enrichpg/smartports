/**
 * Synthetic / Mock Data Service
 * Provides realistic data when the backend is unavailable.
 * All pages use this as fallback via: try { api } catch { mockData }
 */

export const PORTS = [
  { id: 'galicia-a-coruna', name: 'Puerto de A Coruña', shortName: 'A Coruña', location: { lat: 43.3623, lon: -8.4115 }, address: 'Muelle de Trasatlánticos, 15001 A Coruña', phone: '+34 981 22 11 00', email: 'info@apcorunha.es', type: 'commercial', status: 'active', totalBerths: 12, freeBerths: 4, occupiedBerths: 7, reservedBerths: 1, occupancyPct: 67, vessels24h: { in: 8, out: 6 }, description: 'Principal puerto comercial de Galicia' },
  { id: 'galicia-vigo', name: 'Puerto de Vigo', shortName: 'Vigo', location: { lat: 42.2406, lon: -8.7207 }, address: 'Avda. de Beiramar, 36202 Vigo', phone: '+34 986 26 82 00', email: 'info@apvigo.es', type: 'commercial', status: 'active', totalBerths: 18, freeBerths: 6, occupiedBerths: 10, reservedBerths: 2, occupancyPct: 72, vessels24h: { in: 12, out: 10 }, description: 'Mayor puerto de Galicia por tráfico de mercancías' },
  { id: 'galicia-ferrol', name: 'Puerto de Ferrol', shortName: 'Ferrol', location: { lat: 43.4888, lon: -8.2337 }, address: 'Muelle de Curuxeiras, 15402 Ferrol', phone: '+34 981 34 12 00', email: 'info@apferrol.es', type: 'industrial', status: 'active', totalBerths: 8, freeBerths: 3, occupiedBerths: 4, reservedBerths: 1, occupancyPct: 62, vessels24h: { in: 5, out: 4 }, description: 'Puerto industrial y naval de Ferrol' },
  { id: 'galicia-marin', name: 'Puerto de Marín', shortName: 'Marín', location: { lat: 42.3878, lon: -8.7001 }, address: 'Muelle de Pesca, 36900 Marín', phone: '+34 986 88 10 00', email: 'info@apmarin.es', type: 'fishing', status: 'active', totalBerths: 6, freeBerths: 2, occupiedBerths: 3, reservedBerths: 1, occupancyPct: 58, vessels24h: { in: 4, out: 3 }, description: 'Puerto pesquero y base naval' },
  { id: 'galicia-vilagarcia', name: 'Puerto de Vilagarcía', shortName: 'Vilagarcía', location: { lat: 42.5957, lon: -8.7648 }, address: 'Muelle de Ferrazo, 36600 Vilagarcía de Arousa', phone: '+34 986 50 10 00', email: 'info@apvilagarcia.es', type: 'commercial', status: 'active', totalBerths: 5, freeBerths: 2, occupiedBerths: 2, reservedBerths: 1, occupancyPct: 46, vessels24h: { in: 3, out: 2 }, description: 'Puerto de la Ría de Arousa' },
  { id: 'galicia-ribadeo', name: 'Puerto de Ribadeo', shortName: 'Ribadeo', location: { lat: 43.5358, lon: -7.0417 }, address: 'Muelle del Puerto, 27700 Ribadeo', phone: '+34 982 12 80 00', email: 'info@apribadeo.es', type: 'fishing', status: 'maintenance', totalBerths: 4, freeBerths: 4, occupiedBerths: 0, reservedBerths: 0, occupancyPct: 0, vessels24h: { in: 0, out: 0 }, description: 'Puerto en el límite con Asturias, actualmente en mantenimiento' },
];

const VESSEL_NAMES = ['MSC GALICIA', 'PORTO RICO', 'ATLANTIC STAR', 'OCEAN SPIRIT', 'IBERIAN SEA', 'NORDIC WAVE', 'TERRA NOVA', 'MARIA PITA', 'RÍA DE AROUSA', 'CABO FISTERRA'];
const BERTH_STATUSES = ['free', 'occupied', 'occupied', 'reserved', 'free', 'occupied'];
const BERTH_TYPES = ['container', 'bulk', 'roro', 'general', 'tanker', 'cruise'];
const FLAGS = ['ES', 'PT', 'NO', 'DE', 'GR'];

export function generateBerths(portId, count) {
  const port = PORTS.find(p => p.id === portId);
  return Array.from({ length: count }, (_, i) => {
    const idx = i + 1;
    const status = portId === 'galicia-ribadeo' ? 'free' : BERTH_STATUSES[idx % BERTH_STATUSES.length];
    const hasVessel = status === 'occupied';
    return {
      id: `${portId}-berth-${String(idx).padStart(2, '0')}`,
      name: `Muelle ${idx}`,
      portId,
      portName: port?.shortName || portId,
      status,
      type: BERTH_TYPES[idx % BERTH_TYPES.length],
      length: 80 + idx * 15,
      beam: 12 + idx * 2,
      depth: 6 + (idx % 4),
      equipment: ['Grúa pórtico', 'Toma de agua', 'Corriente eléctrica', 'Señalización'].slice(0, 2 + idx % 3),
      tariff: 45 + idx * 5,
      vesselName: hasVessel ? VESSEL_NAMES[idx % VESSEL_NAMES.length] : null,
      vesselIMO: hasVessel ? `IMO${9000000 + idx * 137}` : null,
      vesselFlag: hasVessel ? FLAGS[idx % FLAGS.length] : null,
      etd: hasVessel ? new Date(Date.now() + idx * 3600000 * 4).toISOString() : null,
      eta: status === 'reserved' ? new Date(Date.now() + idx * 3600000 * 2).toISOString() : null,
      occupancyPct: Math.round(50 + (idx % 5) * 8),
      lastActivity: new Date(Date.now() - idx * 3600000).toISOString(),
    };
  });
}

export function getAllBerths() {
  return PORTS.flatMap(p => generateBerths(p.id, p.totalBerths));
}

export function generatePortCalls(count = 30) {
  const vessels = [
    { name: 'MSC GALICIA', imo: 'IMO9123456', type: 'container', flag: 'ES' },
    { name: 'PORTO RICO', imo: 'IMO9234567', type: 'bulk', flag: 'PT' },
    { name: 'ATLANTIC STAR', imo: 'IMO9345678', type: 'tanker', flag: 'NO' },
    { name: 'OCEAN SPIRIT', imo: 'IMO9456789', type: 'roro', flag: 'DE' },
    { name: 'IBERIAN SEA', imo: 'IMO9567890', type: 'container', flag: 'GR' },
    { name: 'NORDIC WAVE', imo: 'IMO9678901', type: 'general', flag: 'NO' },
    { name: 'TERRA NOVA', imo: 'IMO9789012', type: 'cruise', flag: 'IT' },
    { name: 'MARIA PITA', imo: 'IMO9890123', type: 'fishing', flag: 'ES' },
    { name: 'RÍA DE AROUSA', imo: 'IMO9901234', type: 'roro', flag: 'ES' },
    { name: 'CABO FISTERRA', imo: 'IMO9012345', type: 'bulk', flag: 'ES' },
  ];
  const states = ['active', 'active', 'authorized', 'pending', 'completed', 'completed', 'completed'];
  const activePorts = PORTS.filter(p => p.status !== 'maintenance');
  const captains = ['García Rodríguez', 'López Vidal', 'Santos Núñez', 'Ferreira Costa', 'Andersen'];
  const cargos = ['Contenedores', 'Cereales', 'Petróleo', 'Vehículos', 'Carga general'];

  return Array.from({ length: count }, (_, i) => {
    const vessel = vessels[i % vessels.length];
    const port = activePorts[i % activePorts.length];
    const state = states[i % states.length];
    const eta = new Date(Date.now() + (i - 10) * 3600000 * 6);
    const duration = 24 + (i % 5) * 8;
    const etd = new Date(eta.getTime() + duration * 3600000);
    return {
      id: `pc-${String(i + 1).padStart(4, '0')}`,
      vesselName: vessel.name,
      vesselIMO: vessel.imo,
      vesselType: vessel.type,
      vesselFlag: vessel.flag,
      portId: port.id,
      portName: port.shortName,
      berthId: `${port.id}-berth-${String((i % 5) + 1).padStart(2, '0')}`,
      berthName: `Muelle ${(i % 5) + 1}`,
      state,
      eta: eta.toISOString(),
      etd: etd.toISOString(),
      actualArrival: (state === 'active' || state === 'completed') ? new Date(eta.getTime() + 1800000).toISOString() : null,
      actualDeparture: state === 'completed' ? new Date(etd.getTime() - 1800000).toISOString() : null,
      durationHours: duration,
      captain: `Capitán ${captains[i % captains.length]}`,
      cargo: cargos[i % cargos.length],
      grossTonnage: 5000 + i * 1200,
    };
  }).sort((a, b) => new Date(b.eta) - new Date(a.eta));
}

export function generateAlerts(count = 24) {
  const types = ['SECURITY', 'OPERATIONAL', 'ENVIRONMENTAL', 'TECHNICAL', 'WEATHER_WIND', 'VESSEL_DELAYED'];
  const severities = ['critical', 'high', 'medium', 'low'];
  const statuses = ['active', 'active', 'active', 'resolved', 'resolved', 'ignored'];
  const messages = [
    'Velocidad de viento superior a 25 nudos detectada',
    'Buque con retraso superior a 2 horas en ETA',
    'Nivel de combustible bajo en muelle 3',
    'Fallo de comunicación con sensor IoT en atraque 7',
    'Oleaje superior al límite operativo (2.5m)',
    'Visibilidad reducida por niebla (<500m)',
    'Alerta de seguridad en zona de acceso restringido',
    'Mantenimiento programado de grúa pórtico',
    'Derrame menor detectado en muelle 5',
    'Inspección de seguridad requerida',
    'Temperatura motores fuera de rango',
    'Presión hidráulica baja en bomba de achique',
  ];
  return Array.from({ length: count }, (_, i) => {
    const port = PORTS[i % PORTS.length];
    const status = statuses[i % statuses.length];
    return {
      id: `alert-${String(i + 1).padStart(4, '0')}`,
      type: types[i % types.length],
      severity: severities[i % severities.length],
      status,
      portId: port.id,
      portName: port.shortName,
      berthId: i % 3 === 0 ? `${port.id}-berth-${String((i % 4) + 1).padStart(2, '0')}` : null,
      message: messages[i % messages.length],
      description: `Alerta registrada automáticamente por el sistema de monitoreo. Código interno: ALT-${String(i + 1).padStart(4, '0')}.`,
      timestamp: new Date(Date.now() - i * 1800000).toISOString(),
      resolvedAt: status === 'resolved' ? new Date(Date.now() - i * 900000).toISOString() : null,
      assignedTo: i % 2 === 0 ? ['González', 'Martínez', 'Rodríguez'][i % 3] : null,
      comments: status === 'resolved' ? [{ text: 'Situación resuelta', author: 'Op. Guardia', time: new Date(Date.now() - i * 800000).toISOString() }] : [],
    };
  });
}

export function generateVessels() {
  return [
    { id: 'v001', name: 'MSC GALICIA', imo: 'IMO9123456', mmsi: '224456789', flag: 'ES', type: 'container', grossTonnage: 25000, length: 180, beam: 28, draft: 9.5, yearBuilt: 2018, company: 'MSC Spain', status: 'in_port', portId: 'galicia-a-coruna', portName: 'A Coruña', captain: 'Juan García', phone: '+34 616 123 456' },
    { id: 'v002', name: 'PORTO RICO', imo: 'IMO9234567', mmsi: '255678901', flag: 'PT', type: 'bulk', grossTonnage: 18000, length: 155, beam: 24, draft: 8.0, yearBuilt: 2015, company: 'Porto Armadores', status: 'in_port', portId: 'galicia-vigo', portName: 'Vigo', captain: 'Paulo Santos', phone: '+351 91 234 5678' },
    { id: 'v003', name: 'ATLANTIC STAR', imo: 'IMO9345678', mmsi: '257901234', flag: 'NO', type: 'tanker', grossTonnage: 32000, length: 210, beam: 32, draft: 11.0, yearBuilt: 2020, company: 'Nordic Tankers AS', status: 'underway', portId: null, portName: null, captain: 'Erik Andersen', phone: '+47 99 123 456' },
    { id: 'v004', name: 'OCEAN SPIRIT', imo: 'IMO9456789', mmsi: '211234567', flag: 'DE', type: 'roro', grossTonnage: 15000, length: 145, beam: 22, draft: 7.5, yearBuilt: 2017, company: 'Deutsche RoRo GmbH', status: 'in_port', portId: 'galicia-ferrol', portName: 'Ferrol', captain: 'Hans Mueller', phone: '+49 170 1234567' },
    { id: 'v005', name: 'IBERIAN SEA', imo: 'IMO9567890', mmsi: '224567890', flag: 'ES', type: 'container', grossTonnage: 22000, length: 175, beam: 27, draft: 9.0, yearBuilt: 2019, company: 'Transmediterranea', status: 'in_port', portId: 'galicia-vigo', portName: 'Vigo', captain: 'María López', phone: '+34 677 234 567' },
    { id: 'v006', name: 'NORDIC WAVE', imo: 'IMO9678901', mmsi: '257012345', flag: 'NO', type: 'general', grossTonnage: 8500, length: 120, beam: 18, draft: 6.5, yearBuilt: 2012, company: 'Viking Lines', status: 'approaching', portId: 'galicia-a-coruna', portName: 'A Coruña', captain: 'Lars Eriksson', phone: '+47 91 567 890' },
    { id: 'v007', name: 'TERRA NOVA', imo: 'IMO9789012', mmsi: '247890123', flag: 'IT', type: 'cruise', grossTonnage: 85000, length: 290, beam: 35, draft: 8.5, yearBuilt: 2022, company: 'Costa Crociere', status: 'underway', portId: null, portName: null, captain: 'Marco Rossi', phone: '+39 335 1234567' },
    { id: 'v008', name: 'MARIA PITA', imo: 'IMO9890123', mmsi: '224890123', flag: 'ES', type: 'fishing', grossTonnage: 2500, length: 65, beam: 12, draft: 4.0, yearBuilt: 2010, company: 'Pesca Atlántica S.L.', status: 'in_port', portId: 'galicia-marin', portName: 'Marín', captain: 'Antonio Fernández', phone: '+34 619 345 678' },
    { id: 'v009', name: 'RÍA DE AROUSA', imo: 'IMO9901234', mmsi: '224901234', flag: 'ES', type: 'roro', grossTonnage: 12000, length: 138, beam: 20, draft: 7.0, yearBuilt: 2016, company: 'Naviera Arousana', status: 'in_port', portId: 'galicia-vilagarcia', portName: 'Vilagarcía', captain: 'Carlos Pérez', phone: '+34 636 456 789' },
    { id: 'v010', name: 'CABO FISTERRA', imo: 'IMO9012345', mmsi: '224012345', flag: 'ES', type: 'bulk', grossTonnage: 14000, length: 148, beam: 22, draft: 7.8, yearBuilt: 2014, company: 'Armadores Gallegos S.A.', status: 'approaching', portId: 'galicia-vigo', portName: 'Vigo', captain: 'Ramón Iglesias', phone: '+34 657 567 890' },
  ];
}

export function generateUsers() {
  return [
    { id: 'u001', name: 'Ana García Rodríguez', email: 'a.garcia@portsgalicia.es', phone: '+34 981 001 001', role: 'port_captain', portId: 'galicia-a-coruna', portName: 'A Coruña', status: 'online', lastAction: 'Autorizó escala PC-0023', lastActionTime: new Date(Date.now() - 600000).toISOString(), avatar: 'AG' },
    { id: 'u002', name: 'Carlos López Vidal', email: 'c.lopez@portsgalicia.es', phone: '+34 986 002 002', role: 'operations_chief', portId: 'galicia-vigo', portName: 'Vigo', status: 'online', lastAction: 'Asignó atraque VIG-05 a IBERIAN SEA', lastActionTime: new Date(Date.now() - 1200000).toISOString(), avatar: 'CL' },
    { id: 'u003', name: 'María Fernández Castro', email: 'm.fernandez@portsgalicia.es', phone: '+34 981 003 003', role: 'inspector', portId: 'galicia-a-coruna', portName: 'A Coruña', status: 'offline', lastAction: 'Completó inspección MSC GALICIA', lastActionTime: new Date(Date.now() - 7200000).toISOString(), avatar: 'MF' },
    { id: 'u004', name: 'José Martínez Pose', email: 'j.martinez@portsgalicia.es', phone: '+34 981 004 004', role: 'operator', portId: 'galicia-ferrol', portName: 'Ferrol', status: 'online', lastAction: 'Actualizó estado sensor IOT-F07', lastActionTime: new Date(Date.now() - 300000).toISOString(), avatar: 'JM' },
    { id: 'u005', name: 'Laura Santos Núñez', email: 'l.santos@portsgalicia.es', phone: '+34 986 005 005', role: 'operations_chief', portId: 'galicia-vigo', portName: 'Vigo', status: 'online', lastAction: 'Revisó alertas activas', lastActionTime: new Date(Date.now() - 180000).toISOString(), avatar: 'LS' },
    { id: 'u006', name: 'Pedro Iglesias Varela', email: 'p.iglesias@portsgalicia.es', phone: '+34 986 006 006', role: 'inspector', portId: 'galicia-marin', portName: 'Marín', status: 'offline', lastAction: 'Cerró alerta ALT-0042', lastActionTime: new Date(Date.now() - 10800000).toISOString(), avatar: 'PI' },
    { id: 'u007', name: 'Elena Romero Díaz', email: 'e.romero@portsgalicia.es', phone: '+34 986 007 007', role: 'port_captain', portId: 'galicia-vigo', portName: 'Vigo', status: 'online', lastAction: 'Aprobó manifiesto CABO FISTERRA', lastActionTime: new Date(Date.now() - 900000).toISOString(), avatar: 'ER' },
    { id: 'u008', name: 'Marcos Blanco Sousa', email: 'm.blanco@portsgalicia.es', phone: '+34 982 008 008', role: 'operator', portId: 'galicia-ribadeo', portName: 'Ribadeo', status: 'online', lastAction: 'Registró inicio de mantenimiento en dique', lastActionTime: new Date(Date.now() - 450000).toISOString(), avatar: 'MB' },
  ];
}

export function generateOccupancyHistory(days = 30) {
  return Array.from({ length: days + 1 }, (_, d) => {
    const date = new Date(Date.now() - (days - d) * 86400000);
    const entry = { date: date.toISOString().split('T')[0] };
    PORTS.forEach((p, pi) => {
      const base = [67, 72, 62, 58, 46, 0][pi] || 55;
      entry[p.id] = base === 0 ? 0 : Math.max(0, Math.min(100, Math.round(base + Math.sin(d * 0.4 + pi) * 12)));
    });
    return entry;
  });
}

export function generateSensorHistory(hours = 24) {
  return Array.from({ length: hours }, (_, h) => ({
    time: new Date(Date.now() - (hours - h) * 3600000).toISOString(),
    temperature: +(14 + Math.sin(h * 0.26) * 4 + Math.random() * 1.5).toFixed(1),
    humidity: +(62 + Math.cos(h * 0.18) * 12 + Math.random() * 3).toFixed(1),
    windSpeed: +(8 + Math.abs(Math.sin(h * 0.3) * 15) + Math.random() * 2).toFixed(1),
    current: +(42 + Math.sin(h * 0.4) * 18 + Math.random() * 4).toFixed(1),
  }));
}

export function getKPISummary() {
  return {
    totalPorts: PORTS.length,
    activePorts: PORTS.filter(p => p.status === 'active').length,
    totalBerths: PORTS.reduce((s, p) => s + p.totalBerths, 0),
    freeBerths: PORTS.reduce((s, p) => s + p.freeBerths, 0),
    occupiedBerths: PORTS.reduce((s, p) => s + p.occupiedBerths, 0),
    reservedBerths: PORTS.reduce((s, p) => s + p.reservedBerths, 0),
    avgOccupancyPct: Math.round(PORTS.reduce((s, p) => s + p.occupancyPct, 0) / PORTS.length),
    activePortCalls: 6,
    activeAlerts: 8,
    totalVessels: 10,
    inPortVessels: 6,
    portCallsToday: 12,
    avgStayHours: 28,
    estimatedRevenue: 284500,
    efficiencyPct: 87,
  };
}

export function generateDocuments() {
  const types = ['manifest', 'certificate', 'inspection', 'permit', 'insurance'];
  const typeLabels = { manifest: 'Manifiesto de carga', certificate: 'Certificado', inspection: 'Inspección', permit: 'Permiso de atraque', insurance: 'Seguro' };
  const statuses = ['valid', 'valid', 'pending', 'expired'];
  return Array.from({ length: 20 }, (_, i) => {
    const type = types[i % types.length];
    const port = PORTS[i % PORTS.length];
    return {
      id: `doc-${String(i + 1).padStart(4, '0')}`,
      type,
      typeLabel: typeLabels[type],
      title: `${typeLabels[type]} — ${['MSC GALICIA', 'PORTO RICO', 'ATLANTIC STAR', 'OCEAN SPIRIT'][i % 4]}`,
      vessel: ['MSC GALICIA', 'PORTO RICO', 'ATLANTIC STAR', 'OCEAN SPIRIT'][i % 4],
      portId: port.id,
      portName: port.shortName,
      status: statuses[i % statuses.length],
      issueDate: new Date(Date.now() - i * 86400000 * 5).toISOString().split('T')[0],
      expiryDate: new Date(Date.now() + (30 - i * 2) * 86400000).toISOString().split('T')[0],
      size: `${(50 + i * 13) % 900 + 50} KB`,
      version: i % 3 === 0 ? 'v2' : 'v1',
    };
  });
}
