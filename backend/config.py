# SmartPort Backend - Configuration
# Loads environment variables and provides centralized configuration

from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Core
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Server
    server_host: str = Field(default="0.0.0.0", alias="SERVER_HOST")
    server_port: int = Field(default=8000, alias="SERVER_PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="", alias="SECRET_KEY")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")

    # Database
    database_url: str = Field(default="", alias="DATABASE_URL")

    # FIWARE
    orion_base_url: str = Field(default="http://orion-ld:1026", alias="ORION_BASE_URL")
    quantumleap_base_url: str = Field(default="http://quantumleap:8668", alias="QUANTUMLEAP_BASE_URL")
    fiware_service: str = Field(default="smartports", alias="FIWARE_SERVICE")
    fiware_service_path: str = Field(default="/Galicia", alias="FIWARE_SERVICE_PATH")

    # Redis
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    # Celery
    celery_broker_url: str = Field(default="redis://redis:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://redis:6379/2", alias="CELERY_RESULT_BACKEND")

    # Application info
    app_name: str = Field(default="SmartPort API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    api_title: str = Field(default="SmartPort Galicia API", alias="API_TITLE")
    api_description: str = Field(default="Real-time multipurpose port network operations", alias="API_DESCRIPTION")

    # MQTT
    mqtt_broker_url: str = Field(default="mqtt://mosquitto:1883", alias="MQTT_BROKER_URL")

    # Optional features
    enable_prometheus: bool = Field(default=True, alias="ENABLE_PROMETHEUS")
    enable_grafana: bool = Field(default=True, alias="ENABLE_GRAFANA")
    enable_ml_forecasting: bool = Field(default=True, alias="ENABLE_ML_FORECASTING")
    enable_ml_recommendations: bool = Field(default=True, alias="ENABLE_ML_RECOMMENDATIONS")

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()


# Export singleton instance for convenience
settings = get_settings()
