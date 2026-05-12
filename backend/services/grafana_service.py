"""
Grafana Service - Automated Dashboard Provisioning and Integration

Handles:
- Dashboard creation/update
- Datasource configuration
- Alert provisioning
- Grafana API communication
"""

import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)


class GrafanaClient:
    """Grafana API client for dashboard and datasource management"""
    
    def __init__(self):
        self.base_url = f"http://grafana:3000"
        self.api_url = f"{self.base_url}/api"
        self.username = getattr(settings, "grafana_user", "admin")
        self.password = getattr(settings, "grafana_password", "admin123")
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _auth(self, client: httpx.Client) -> httpx.Client:
        """Apply basic auth to client"""
        client.auth = (self.username, self.password)
        return client
    
    async def health_check(self) -> bool:
        """Check if Grafana is accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/health",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    logger.info("✅ Grafana is healthy")
                    return True
        except Exception as e:
            logger.error(f"❌ Grafana health check failed: {e}")
        return False
    
    async def get_datasource(self, name: str) -> Optional[Dict[str, Any]]:
        """Get datasource by name"""
        try:
            async with httpx.AsyncClient() as client:
                client = self._auth(client)
                response = await client.get(
                    f"{self.api_url}/datasources/name/{name}",
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error fetching datasource {name}: {e}")
        return None
    
    async def create_datasource(self, name: str, ds_type: str, url: str, 
                               database: str = "", user: str = "", password: str = "") -> Dict[str, Any]:
        """Create or update datasource"""
        try:
            payload = {
                "name": name,
                "type": ds_type,
                "url": url,
                "access": "proxy",
                "isDefault": False,
                "jsonData": {},
                "secureJsonData": {}
            }
            
            if ds_type == "postgres":
                payload["database"] = database
                payload["user"] = user
                payload["secureJsonData"]["password"] = password
                payload["jsonData"]["postgresVersion"] = 1200
                payload["jsonData"]["sslmode"] = "disable"
            elif ds_type == "prometheus":
                payload["jsonData"]["timeInterval"] = "60s"
            
            async with httpx.AsyncClient() as client:
                client = self._auth(client)
                # Check if exists
                existing = await self.get_datasource(name)
                
                if existing:
                    response = await client.put(
                        f"{self.api_url}/datasources/{existing['id']}",
                        json=payload,
                        headers=self._get_headers(),
                        timeout=self.timeout
                    )
                else:
                    response = await client.post(
                        f"{self.api_url}/datasources",
                        json=payload,
                        headers=self._get_headers(),
                        timeout=self.timeout
                    )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Datasource '{name}' created/updated")
                    return response.json()
                else:
                    logger.error(f"Failed to create datasource: {response.text}")
        except Exception as e:
            logger.error(f"Error creating datasource {name}: {e}")
        return {}
    
    async def get_dashboard(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get dashboard by UID"""
        try:
            async with httpx.AsyncClient() as client:
                client = self._auth(client)
                response = await client.get(
                    f"{self.api_url}/dashboards/uid/{uid}",
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error fetching dashboard {uid}: {e}")
        return None
    
    async def create_dashboard(self, dashboard_json: Dict[str, Any], overwrite: bool = True) -> Dict[str, Any]:
        """Create or update dashboard"""
        try:
            payload = {
                "dashboard": dashboard_json,
                "overwrite": overwrite
            }
            
            async with httpx.AsyncClient() as client:
                client = self._auth(client)
                response = await client.post(
                    f"{self.api_url}/dashboards/db",
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"✅ Dashboard '{dashboard_json.get('title', 'Unknown')}' created/updated")
                    return result
                else:
                    logger.error(f"Failed to create dashboard: {response.text}")
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
        return {}
    
    async def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """Get all dashboards"""
        try:
            async with httpx.AsyncClient() as client:
                client = self._auth(client)
                response = await client.get(
                    f"{self.api_url}/search",
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error fetching dashboards: {e}")
        return []


class GrafanaService:
    """High-level Grafana service for SmartPorts"""
    
    def __init__(self):
        self.client = GrafanaClient()
    
    async def initialize(self) -> bool:
        """Initialize Grafana: check health, setup datasources, create dashboards"""
        logger.info("🚀 Initializing Grafana...")
        
        try:
            # 1. Health check
            if not await self.client.health_check():
                logger.warning("⚠️  Grafana is not available")
                return False
            
            # 2. Setup datasources
            await self._setup_datasources()
            
            # 3. Create dashboards
            await self._create_dashboards()
            
            logger.info("✅ Grafana initialization complete")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing Grafana: {e}")
            return False
    
    async def _setup_datasources(self):
        """Setup required datasources"""
        logger.info("Setting up Grafana datasources...")
        
        # TimescaleDB datasource
        await self.client.create_datasource(
            name="QuantumLeap TimeSeries",
            ds_type="postgres",
            url="timescaledb:5432",
            database="quantumleap",
            user="quantumleap",
            password="timescale123"
        )
        
        # Prometheus datasource
        await self.client.create_datasource(
            name="Prometheus",
            ds_type="prometheus",
            url="http://prometheus:9090"
        )
    
    async def _create_dashboards(self):
        """Create SmartPorts dashboards"""
        logger.info("Creating Grafana dashboards...")
        
        dashboards = [
            self._get_berth_dashboard(),
            self._get_weather_dashboard(),
            self._get_alerts_dashboard(),
            self._get_system_dashboard()
        ]
        
        for dashboard in dashboards:
            await self.client.create_dashboard(dashboard, overwrite=True)
    
    def _get_berth_dashboard(self) -> Dict[str, Any]:
        """Get Berth occupancy dashboard definition"""
        return {
            "uid": "smartports-berths",
            "title": "SmartPort Galicia - Amarres",
            "description": "Real-time berth occupancy and status monitoring",
            "tags": ["smartports", "berths", "operations"],
            "timezone": "browser",
            "schemaVersion": 27,
            "version": 0,
            "refresh": "30s",
            "time": {
                "from": "now-24h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Berth Occupancy Rate",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT $__time(timestamp) AS time, occupancy_percentage FROM berth_status WHERE timestamp > $__from AND timestamp < $__to ORDER BY timestamp",
                            "format": "time_series"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "Active Berths",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT COUNT(*) as count FROM berth_status WHERE status = 'occupied' AND timestamp > NOW() - INTERVAL '5 minutes'"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Berth Status Distribution",
                    "type": "piechart",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT status, COUNT(*) FROM berth_status WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY status"
                        }
                    ]
                }
            ]
        }
    
    def _get_weather_dashboard(self) -> Dict[str, Any]:
        """Get Weather conditions dashboard definition"""
        return {
            "uid": "smartports-weather",
            "title": "SmartPort Galicia - Clima",
            "description": "Weather and environmental conditions",
            "tags": ["smartports", "weather", "environment"],
            "timezone": "browser",
            "schemaVersion": 27,
            "version": 0,
            "refresh": "5m",
            "panels": [
                {
                    "id": 1,
                    "title": "Wind Speed",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT MAX(wind_speed) FROM weather_observed WHERE timestamp > NOW() - INTERVAL '1 hour'"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "Wave Height",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT MAX(wave_height) FROM weather_observed WHERE timestamp > NOW() - INTERVAL '1 hour'"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Visibility",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT MAX(visibility) FROM weather_observed WHERE timestamp > NOW() - INTERVAL '1 hour'"
                        }
                    ]
                },
                {
                    "id": 4,
                    "title": "Weather Timeline",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT $__time(timestamp) AS time, wind_speed, wave_height, visibility FROM weather_observed WHERE timestamp > $__from ORDER BY timestamp"
                        }
                    ]
                }
            ]
        }
    
    def _get_alerts_dashboard(self) -> Dict[str, Any]:
        """Get Alerts dashboard definition"""
        return {
            "uid": "smartports-alerts",
            "title": "SmartPort Galicia - Alertas",
            "description": "System alerts and incident tracking",
            "tags": ["smartports", "alerts", "incidents"],
            "timezone": "browser",
            "schemaVersion": 27,
            "version": 0,
            "refresh": "1m",
            "panels": [
                {
                    "id": 1,
                    "title": "Active Alerts by Type",
                    "type": "piechart",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT alert_type, COUNT(*) FROM alerts WHERE status = 'active' GROUP BY alert_type"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "Critical Alerts",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT COUNT(*) FROM alerts WHERE severity = 'critical' AND status = 'active'"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Alert Timeline",
                    "type": "table",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    "targets": [
                        {
                            "refId": "A",
                            "rawSql": "SELECT timestamp, alert_type, severity, message FROM alerts WHERE timestamp > NOW() - INTERVAL '24 hours' ORDER BY timestamp DESC LIMIT 50"
                        }
                    ]
                }
            ]
        }
    
    def _get_system_dashboard(self) -> Dict[str, Any]:
        """Get System health dashboard definition"""
        return {
            "uid": "smartports-system",
            "title": "SmartPort Galicia - Sistema",
            "description": "System health and infrastructure monitoring",
            "tags": ["smartports", "system", "monitoring"],
            "timezone": "browser",
            "schemaVersion": 27,
            "version": 0,
            "refresh": "30s",
            "panels": [
                {
                    "id": 1,
                    "title": "Active Connections",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {"type": "prometheus", "uid": "prometheus"},
                            "expr": "websocket_connections_active"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "API Requests/sec",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 18, "x": 6, "y": 0},
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {"type": "prometheus", "uid": "prometheus"},
                            "expr": "rate(http_requests_total[1m])"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Task Queue Length",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 0, "y": 6},
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {"type": "prometheus", "uid": "prometheus"},
                            "expr": "celery_queue_length"
                        }
                    ]
                },
                {
                    "id": 4,
                    "title": "System Status",
                    "type": "table",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12},
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {"type": "prometheus", "uid": "prometheus"},
                            "expr": "up"
                        }
                    ]
                }
            ]
        }
