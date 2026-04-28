#!/usr/bin/env python3
"""
Stack Validation Script - SmartPort Galicia
Validates Docker Compose configuration and service readiness
"""

import yaml
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_docker_compose(compose_file: str = "docker-compose.yml") -> Dict:
    """Load and parse docker-compose.yml"""
    try:
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ Loaded {compose_file}")
        return config
    except FileNotFoundError:
        logger.error(f"✗ File not found: {compose_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"✗ YAML parse error: {e}")
        sys.exit(1)


def validate_services(config: Dict) -> Tuple[List[str], List[str]]:
    """Validate all services in docker-compose"""
    services = config.get('services', {})
    healthy_services = []
    issues = []

    required_services = [
        'mongodb', 'postgres', 'timescaledb', 'redis', 'mosquitto',
        'orion-ld', 'iot-agent', 'quantumleap', 'backend', 'celery-worker',
        'nginx', 'grafana', 'prometheus'
    ]

    # Check all required services exist
    for service in required_services:
        if service not in services:
            issues.append(f"Missing service: {service}")
        else:
            healthy_services.append(service)

    return healthy_services, issues


def validate_healthchecks(config: Dict) -> Tuple[List[str], List[str]]:
    """Validate healthchecks for each service"""
    services = config.get('services', {})
    with_healthchecks = []
    without_healthchecks = []

    for service_name, service_config in services.items():
        if 'healthcheck' in service_config:
            with_healthchecks.append(service_name)
        else:
            without_healthchecks.append(service_name)

    return with_healthchecks, without_healthchecks


def validate_dependencies(config: Dict) -> List[str]:
    """Validate service dependencies"""
    services = config.get('services', {})
    issues = []

    for service_name, service_config in services.items():
        depends_on = service_config.get('depends_on', {})
        if isinstance(depends_on, dict):
            for dep_service in depends_on.keys():
                if dep_service not in services:
                    issues.append(f"{service_name} depends on non-existent {dep_service}")

    return issues


def validate_networks(config: Dict) -> Tuple[int, List[str]]:
    """Validate networks configuration"""
    networks = config.get('networks', {})
    issues = []

    if 'smartports_net' not in networks:
        issues.append("Missing network: smartports_net")

    return len(networks), issues


def validate_volumes(config: Dict) -> Tuple[int, List[str]]:
    """Validate volumes configuration"""
    volumes = config.get('volumes', {})
    issues = []

    required_volumes = [
        'mongodb_data', 'postgres_data', 'timescaledb_data',
        'redis_data', 'grafana_storage', 'prometheus_data'
    ]

    for vol in required_volumes:
        if vol not in volumes:
            issues.append(f"Missing volume: {vol}")

    return len(volumes), issues


def validate_environment_file(env_file: str = "config/.env.example") -> Tuple[int, List[str]]:
    """Validate environment configuration file"""
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        var_count = sum(1 for line in lines if '=' in line and not line.strip().startswith('#'))
        logger.info(f"✓ Found {var_count} environment variables in {env_file}")
        
        return var_count, []
    except FileNotFoundError:
        return 0, [f"Environment file not found: {env_file}"]


def validate_backend_files() -> List[str]:
    """Validate required backend files exist"""
    issues = []
    required_files = [
        'backend/main.py',
        'backend/config.py',
        'backend/requirements.txt',
        'backend/Dockerfile',
        'backend/api/health.py',
        'backend/api/v1.py',
        'backend/tasks/celery_app.py',
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing backend file: {file_path}")

    return issues


def main():
    """Run all validations"""
    logger.info("="*60)
    logger.info("SmartPort Stack Validation")
    logger.info("="*60)

    # Load configuration
    config = load_docker_compose()

    # Validate services
    services, service_issues = validate_services(config)
    logger.info(f"✓ Services found: {len(services)}/{len(services) + len(service_issues)}")
    for issue in service_issues:
        logger.warning(f"  ✗ {issue}")

    # Validate healthchecks
    with_hc, without_hc = validate_healthchecks(config)
    logger.info(f"✓ Healthchecks configured: {len(with_hc)} services")
    if without_hc:
        logger.warning(f"  ⚠ Services without healthchecks: {', '.join(without_hc)}")

    # Validate dependencies
    dep_issues = validate_dependencies(config)
    if dep_issues:
        logger.warning(f"✗ Dependency issues found:")
        for issue in dep_issues:
            logger.warning(f"  ✗ {issue}")
    else:
        logger.info("✓ All service dependencies valid")

    # Validate networks
    net_count, net_issues = validate_networks(config)
    logger.info(f"✓ Networks configured: {net_count}")
    for issue in net_issues:
        logger.warning(f"  ✗ {issue}")

    # Validate volumes
    vol_count, vol_issues = validate_volumes(config)
    logger.info(f"✓ Volumes configured: {vol_count}")
    for issue in vol_issues:
        logger.warning(f"  ✗ {issue}")

    # Validate environment
    env_count, env_issues = validate_environment_file()
    for issue in env_issues:
        logger.warning(f"  ✗ {issue}")

    # Validate backend files
    backend_issues = validate_backend_files()
    if backend_issues:
        logger.warning(f"✗ Backend file issues:")
        for issue in backend_issues:
            logger.warning(f"  ✗ {issue}")
    else:
        logger.info("✓ All required backend files present")

    # Summary
    all_issues = service_issues + dep_issues + net_issues + vol_issues + env_issues + backend_issues
    logger.info("="*60)
    if all_issues:
        logger.warning(f"⚠ Found {len(all_issues)} issues:")
        for issue in all_issues:
            logger.warning(f"  ✗ {issue}")
        return 1
    else:
        logger.info("✓ All validations passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
