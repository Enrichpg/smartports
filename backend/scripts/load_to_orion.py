#!/usr/bin/env python3
"""
SmartPort Galicia - Load Seed Data to Orion-LD
Loads pre-generated NGSI-LD entities from JSON file to Orion-LD context broker

Usage:
    python load_to_orion.py                      # Load from default file
    python load_to_orion.py --file <path>        # Load from custom file
    python load_to_orion.py --dry-run             # Preview without loading
    python load_to_orion.py --orion-url <url>    # Custom Orion URL (default: http://localhost:1026)
    python load_to_orion.py --verbose             # Verbose output
    python load_to_orion.py --check-only          # Only check connection to Orion

Environment variables:
    ORION_BASE_URL          Orion-LD base URL (default: http://localhost:1026)
    FIWARE_SERVICE          Service header (default: smartports)
    FIWARE_SERVICE_PATH     Service path header (default: /Galicia)
"""

import asyncio
import json
import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

# Configure logging
def setup_logger(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


class OrionLoader:
    """Load entities to Orion-LD context broker"""
    
    def __init__(
        self,
        orion_url: str = None,
        fiware_service: str = "smartports",
        fiware_service_path: str = "/Galicia",
        verbose: bool = False
    ):
        """Initialize loader"""
        self.verbose = verbose
        self.logger = setup_logger(verbose)
        
        self.orion_url = orion_url or os.getenv("ORION_BASE_URL", "http://localhost:1026")
        self.fiware_service = fiware_service or os.getenv("FIWARE_SERVICE", "smartports")
        self.fiware_service_path = fiware_service_path or os.getenv("FIWARE_SERVICE_PATH", "/Galicia")
        
        self.headers = {
            "FIWARE-Service": self.fiware_service,
            "FIWARE-ServicePath": self.fiware_service_path,
            "Content-Type": "application/ld+json",
        }
        
        self.stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        self.logger.info(f"Orion-LD URL: {self.orion_url}")
        self.logger.info(f"FIWARE Service: {self.fiware_service}")
        self.logger.info(f"FIWARE Service Path: {self.fiware_service_path}")
    
    async def check_connection(self) -> bool:
        """Check if Orion-LD is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.orion_url}/version")
                if response.status_code == 200:
                    version_info = response.json()
                    self.logger.info(f"✓ Connected to Orion-LD {version_info.get('version', 'unknown')}")
                    return True
                else:
                    self.logger.error(f"✗ Orion-LD returned status {response.status_code}")
                    return False
        except Exception as e:
            self.logger.error(f"✗ Cannot connect to Orion-LD: {e}")
            return False
    
    async def create_entity(self, entity: Dict[str, Any]) -> bool:
        """Create entity in Orion-LD"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.orion_url}/ngsi-ld/v1/entities"
                
                response = await client.post(
                    url,
                    json=entity,
                    headers=self.headers,
                    params={"options": "keyValues"}
                )
                
                if response.status_code in [201, 204]:
                    self.stats["created"] += 1
                    self.logger.debug(f"✓ Created {entity.get('type')}: {entity.get('id')}")
                    return True
                elif response.status_code == 409:
                    # Entity exists, try update
                    return await self.update_entity(entity)
                else:
                    self.stats["failed"] += 1
                    error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    self.stats["errors"].append((entity.get('id'), error_msg))
                    self.logger.error(f"✗ Failed to create {entity.get('id')}: {error_msg}")
                    return False
                    
        except Exception as e:
            self.stats["failed"] += 1
            self.stats["errors"].append((entity.get('id'), str(e)))
            self.logger.error(f"✗ Error creating entity {entity.get('id')}: {e}")
            return False
    
    async def update_entity(self, entity: Dict[str, Any]) -> bool:
        """Update entity in Orion-LD"""
        try:
            entity_id = entity.get('id')
            # Remove @context and id for update
            update_body = {k: v for k, v in entity.items() if k not in ["@context", "id", "type"]}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.orion_url}/ngsi-ld/v1/entities/{entity_id}/attrs"
                
                response = await client.patch(
                    url,
                    json=update_body,
                    headers=self.headers,
                    params={"options": "keyValues"}
                )
                
                if response.status_code in [204]:
                    self.stats["updated"] += 1
                    self.logger.debug(f"✓ Updated {entity.get('type')}: {entity_id}")
                    return True
                else:
                    self.stats["failed"] += 1
                    error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    self.stats["errors"].append((entity_id, error_msg))
                    self.logger.error(f"✗ Failed to update {entity_id}: {error_msg}")
                    return False
                    
        except Exception as e:
            self.stats["failed"] += 1
            self.stats["errors"].append((entity.get('id'), str(e)))
            self.logger.error(f"✗ Error updating entity {entity.get('id')}: {e}")
            return False
    
    async def load_entities_from_file(self, filepath: str, dry_run: bool = False) -> bool:
        """Load entities from JSON file"""
        try:
            path = Path(filepath)
            if not path.exists():
                self.logger.error(f"✗ File not found: {filepath}")
                return False
            
            self.logger.info(f"Loading entities from {filepath}...")
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            entities = data.get('entities', [])
            if not entities:
                self.logger.error("No entities found in file")
                return False
            
            self.stats["total"] = len(entities)
            self.logger.info(f"Loaded {len(entities)} entities from file")
            
            if dry_run:
                self.logger.info("DRY RUN MODE - No entities will be loaded to Orion")
                self._print_dry_run_summary(entities)
                return True
            
            # Load entities to Orion
            self.logger.info("=" * 80)
            self.logger.info("Loading entities to Orion-LD...")
            self.logger.info("=" * 80)
            
            tasks = [self.create_entity(entity) for entity in entities]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"✗ Invalid JSON in file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error loading file: {e}")
            return False
    
    def _print_dry_run_summary(self, entities: List[Dict[str, Any]]):
        """Print summary of entities for dry-run"""
        self.logger.info("\nDRY RUN - Entity Summary:")
        self.logger.info("=" * 80)
        
        type_counts = {}
        for entity in entities:
            entity_type = entity.get('type', 'Unknown')
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        for entity_type, count in sorted(type_counts.items()):
            self.logger.info(f"  {entity_type}: {count} entities")
        
        self.logger.info("=" * 80)
        self.logger.info(f"Total: {len(entities)} entities ready to load")
        self.logger.info("\nTo load these entities, run without --dry-run flag")
    
    def print_summary(self):
        """Print loading summary"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("LOADING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total entities:     {self.stats['total']}")
        self.logger.info(f"Created:            {self.stats['created']}")
        self.logger.info(f"Updated:            {self.stats['updated']}")
        self.logger.info(f"Failed:             {self.stats['failed']}")
        
        if self.stats['errors']:
            self.logger.info(f"\nErrors ({len(self.stats['errors'])}):")
            for entity_id, error in self.stats['errors'][:5]:  # Show first 5
                self.logger.error(f"  - {entity_id}: {error}")
            if len(self.stats['errors']) > 5:
                self.logger.error(f"  ... and {len(self.stats['errors']) - 5} more")
        
        self.logger.info("=" * 80)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Load NGSI-LD entities to Orion-LD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--file",
        default="data/seed/galicia_entities.json",
        help="Path to seed JSON file (default: data/seed/galicia_entities.json)"
    )
    parser.add_argument(
        "--orion-url",
        default=None,
        help="Orion-LD base URL (default: http://localhost:1026)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without loading to Orion"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check connection to Orion, don't load"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = OrionLoader(
        orion_url=args.orion_url,
        verbose=args.verbose
    )
    
    logger = setup_logger(args.verbose)
    
    # Check connection
    logger.info("Checking connection to Orion-LD...")
    connected = await loader.check_connection()
    
    if args.check_only:
        sys.exit(0 if connected else 1)
    
    if not connected:
        logger.error("Cannot proceed without Orion-LD connection")
        sys.exit(1)
    
    # Load entities
    success = await loader.load_entities_from_file(
        args.file,
        dry_run=args.dry_run
    )
    
    loader.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
