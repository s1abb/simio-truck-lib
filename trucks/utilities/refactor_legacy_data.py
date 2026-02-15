"""
Utility script to refactor existing performance curve data into the new structured format.

This script splits a monolithic performance curves JSON file into:
1. specifications.json - Basic equipment specs
2. performance_curves.json - Performance curve data only
3. metadata.json - Data quality and source information
"""

import json
from pathlib import Path
from typing import Dict, Any


def split_legacy_json(input_file: Path, output_dir: Path) -> None:
    """
    Split a legacy combined JSON file into structured components.
    
    Args:
        input_file: Path to the legacy JSON file
        output_dir: Directory to save the split files
    """
    # Load the legacy file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract specifications
    specifications = {
        "model": data.get("truck_model", ""),
        "manufacturer": data.get("manufacturer", ""),
        "category": "ultra_class_haul_truck",  # Default, update as needed
        "weights": {
            "empty_kg": data.get("specifications", {}).get("empty_weight_kg", 0),
            "loaded_kg": data.get("specifications", {}).get("loaded_weight_kg", 0),
            "payload_kg": data.get("specifications", {}).get("payload_capacity_kg", 0),
            "payload_tonnes": data.get("specifications", {}).get("payload_capacity_kg", 0) / 1000
        },
        "dimensions": {
            "wheelbase_mm": data.get("specifications", {}).get("wheelbase_mm", 0)
        },
        "tires": {
            "size": data.get("specifications", {}).get("tire_size", "")
        },
        "drivetrain": {
            "type": data.get("drivetrain", {}).get("type", ""),
            "max_speed_kmh": data.get("specifications", {}).get("max_speed_kmh", 0),
            "total_reduction_ratio": data.get("drivetrain", {}).get("total_reduction_ratio", ""),
            "generator": data.get("drivetrain", {}).get("generator", ""),
            "motor": data.get("drivetrain", {}).get("wheel_motors", ""),
            "inverter": data.get("drivetrain", {}).get("controls", "")
        }
    }
    
    # Extract performance curves
    performance_curves = data.get("performance_curves", {})
    
    # Extract metadata
    metadata = {
        "data_source": data.get("data_source", ""),
        "extraction_date": "2025-11-26",  # Update as needed
        "fitting_method": data.get("fitting_method", ""),
        "fitting_quality": data.get("fitting_quality", {}),
        "corrections_applied": [data.get("correction_note", "")] if data.get("correction_note") else [],
        "validation_status": "verified",  # Update as needed
        "version": "1.0.0"
    }
    
    # Save the split files
    with open(output_dir / "specifications.json", 'w') as f:
        json.dump(specifications, f, indent=2)
    
    with open(output_dir / "performance_curves.json", 'w') as f:
        json.dump(performance_curves, f, indent=2)
    
    with open(output_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Successfully split data into {output_dir}")
    print(f"  - specifications.json")
    print(f"  - performance_curves.json")
    print(f"  - metadata.json")


if __name__ == "__main__":
    # Example usage for CAT 794 AC
    legacy_file = Path("../outputs/cat_794_ac_performance_curves.json")
    output_directory = Path("../data/cat_794_ac")
    
    if legacy_file.exists():
        split_legacy_json(legacy_file, output_directory)
    else:
        print(f"Legacy file not found: {legacy_file}")
