"""
Generate NGSI-LD seed entities to JSON file

Usage:
    python generate_seed_json.py                    # Generate to file
    python generate_seed_json.py --pretty           # Pretty JSON output
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, '/home/enrique/XDEI/SmartPorts')

from backend.scripts.load_seed import SeedGenerator
from backend.services.orion_service import OrionService


def generate_and_save_seed(
    output_file: str = "data/seed/galicia_entities.json",
    pretty: bool = False
):
    """Generate seed entities and save to JSON file"""
    
    # Initialize OrionService (not needed for generation, just for interface)
    orion = OrionService()
    
    # Generate all entities
    generator = SeedGenerator(orion)
    entities = generator.generate_all()
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    seed_data = {
        "generated_at": generator.entities[0]["@context"] if generator.entities else None,
        "statistics": generator.stats,
        "entities": entities
    }
    
    # Remove @context from stats output
    seed_data["statistics"] = {k: v for k, v in generator.stats.items()}
    
    with open(output_path, 'w') as f:
        if pretty:
            json.dump(seed_data, f, indent=2)
        else:
            json.dump(seed_data, f)
    
    print(f"\n✓ Seed entities saved to {output_file}")
    print(f"  Total entities: {len(entities)}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    # Print entity count by type
    print("\nEntity breakdown:")
    for entity_type, count in sorted(generator.stats.items()):
        if count > 0:
            print(f"  - {entity_type}: {count}")
    
    print("\nFirst entity example (Port):")
    for entity in entities:
        if entity.get("type") == "Port":
            print(json.dumps(entity, indent=2)[:500] + "...")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate NGSI-LD seed to JSON")
    parser.add_argument(
        "--output",
        default="data/seed/galicia_entities.json",
        help="Output JSON file"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON"
    )
    
    args = parser.parse_args()
    
    generate_and_save_seed(
        output_file=args.output,
        pretty=args.pretty
    )
