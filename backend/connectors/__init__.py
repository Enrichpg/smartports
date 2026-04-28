# API Connectors for SmartPorts Real Data Ingestion
# Each connector handles a specific external API source

from .base_connector import BaseConnector
from .aemet_connector import AEMETConnector
from .meteogalicia_connector import MeteoGaliciaConnector
from .puertos_estado_connector import PuertosEstadoConnector

__all__ = [
    "BaseConnector",
    "AEMETConnector",
    "MeteoGaliciaConnector",
    "PuertosEstadoConnector",
]
