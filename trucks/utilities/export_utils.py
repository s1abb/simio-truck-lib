"""
Export utilities for generating documentation and data files.

Provides functions to export equipment data in various formats.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


def generate_quick_reference(
    model: str,
    specifications: Dict,
    performance_curves: Dict,
    metadata: Dict,
    output_file: Path
) -> None:
    """
    Generate a quick reference markdown document.
    
    Args:
        model: Model identifier
        specifications: Specifications dictionary
        performance_curves: Performance curves dictionary
        metadata: Metadata dictionary
        output_file: Path to save markdown file
    """
    model_name = model.replace('_', ' ').upper()
    
    md_content = f"""# {model_name} - Quick Reference for Simulation

## Core Specifications

```
Model: {model_name}
Manufacturer: {specifications.get('manufacturer', 'N/A')}
Empty Weight: {specifications.get('weights', {}).get('empty_kg', 0):,} kg
Loaded Weight: {specifications.get('weights', {}).get('loaded_kg', 0):,} kg
Payload: {specifications.get('weights', {}).get('payload_tonnes', 0)} tonnes ({specifications.get('weights', {}).get('payload_kg', 0):,} kg)
Max Speed: {specifications.get('drivetrain', {}).get('max_speed_kmh', 0)} km/h
Tire Size: {specifications.get('tires', {}).get('size', 'N/A')}
Wheelbase: {specifications.get('dimensions', {}).get('wheelbase_mm', 0)} mm
Drivetrain: {specifications.get('drivetrain', {}).get('type', 'N/A')}
```

## Performance Summary

### Rimpull Curve
"""
    
    rimpull = performance_curves.get('rimpull_curve', {})
    if 'data' in rimpull:
        speeds = rimpull['data']['speed_kmh']
        forces_kn = rimpull['data']['rimpull_kn']
        forces_tf = rimpull['data']['rimpull_tf']
        
        md_content += """
| Speed (km/h) | Rimpull (kN) | Rimpull (tf) |
|--------------|--------------|--------------|
"""
        # Sample every 10 km/h
        for i in range(0, len(speeds), 10):
            if i < len(speeds):
                md_content += f"| {speeds[i]:<12.0f} | {forces_kn[i]:<12.1f} | {forces_tf[i]:<12.1f} |\n"
    
    md_content += f"""
**Max Rimpull:** {rimpull.get('constraints', {}).get('max_rimpull_kn', 'N/A')} kN  
**Model Type:** {rimpull.get('model_type', 'N/A')}
"""
    
    retarding = performance_curves.get('retarding_curve', {})
    if retarding:
        md_content += f"""
### Retarding System

**Continuous Power:** {retarding.get('continuous_power_kw', 'N/A')} kW ({retarding.get('continuous_power_hp', 'N/A')} hp)  
**Efficiency:** {retarding.get('efficiency', 0) * 100:.0f}%  
**Type:** {retarding.get('type', 'N/A')}
"""
    
    # Data quality
    quality = metadata.get('fitting_quality', {})
    r_squared = quality.get('r_squared', None)
    rmse_kn = quality.get('rmse_kn', None)
    
    md_content += f"""
## Data Quality

**R² Score:** {f"{r_squared:.4f}" if r_squared is not None else 'N/A'}  
**RMSE:** {f"{rmse_kn:.2f} kN" if rmse_kn is not None else 'N/A'}  
**Fitting Method:** {metadata.get('fitting_method', 'N/A')}  
**Validation Status:** {metadata.get('validation_status', 'N/A')}
"""
    
    # Corrections
    if metadata.get('corrections_applied'):
        md_content += "\n### Corrections Applied\n\n"
        for correction in metadata['corrections_applied']:
            md_content += f"- {correction}\n"
    
    # Usage example
    md_content += f"""
## Usage Example (Python)

```python
import json

# Load performance curves
with open('data/{model}/performance_curves.json', 'r') as f:
    curves = json.load(f)

# Get rimpull at 30 km/h
speed_idx = curves['rimpull_curve']['data']['speed_kmh'].index(30.0)
rimpull_kn = curves['rimpull_curve']['data']['rimpull_kn'][speed_idx]
print(f"Rimpull at 30 km/h: {{rimpull_kn:.1f}} kN")
```

## References

**Data Source:** {metadata.get('data_source', 'N/A')}  
**Extraction Date:** {metadata.get('extraction_date', 'N/A')}  
**Version:** {metadata.get('version', 'N/A')}

---
*Generated on {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(md_content)
    
    print(f"Generated quick reference: {output_file}")


def generate_curve_fitting_summary(
    model: str,
    performance_curves: Dict,
    metadata: Dict,
    output_file: Path
) -> None:
    """
    Generate a detailed curve fitting summary document.
    
    Args:
        model: Model identifier
        performance_curves: Performance curves dictionary
        metadata: Metadata dictionary
        output_file: Path to save markdown file
    """
    model_name = model.replace('_', ' ').upper()
    
    md_content = f"""# {model_name} Performance Curves - Fitting Summary

## Overview

**Model:** {model_name}  
**Data Source:** {metadata.get('data_source', 'N/A')}  
**Fitting Method:** {metadata.get('fitting_method', 'N/A')}  
**Extraction Date:** {metadata.get('extraction_date', 'N/A')}

## Curve Fitting Results

### Rimpull Curve

"""
    
    rimpull = performance_curves.get('rimpull_curve', {})
    quality = metadata.get('fitting_quality', {})
    
    md_content += f"""**Model Type:** {rimpull.get('model_type', 'N/A')}  
**Formula:** {rimpull.get('formula', 'N/A')}  

**Quality Metrics:**
- R² = {quality.get('r_squared', 0):.6f} ({quality.get('r_squared', 0) * 100:.2f}% variance explained)
- RMSE = {quality.get('rmse_kn', 0):.2f} kN
- Max Error = {quality.get('max_error_kn', 0):.2f} kN
- Mean Error = {quality.get('mean_error_kn', 0):.2f} kN

**Physical Constraints:**
- Maximum Rimpull: {rimpull.get('constraints', {}).get('max_rimpull_kn', 'N/A')} kN
- Speed Range: {rimpull.get('constraints', {}).get('min_speed_kmh', 0)} - {rimpull.get('constraints', {}).get('max_speed_kmh', 'N/A')} km/h

**Conditions:** {rimpull.get('conditions', 'N/A')}
"""
    
    # Gradeability data
    gradeability = performance_curves.get('gradeability_data', {})
    if gradeability:
        md_content += "\n### Source Gradeability Data\n\n"
        
        if 'empty' in gradeability:
            empty = gradeability['empty']
            md_content += f"""**Empty Truck ({empty.get('weight_kg', 0):,} kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
"""
            for i in range(len(empty.get('grade_percent', []))):
                md_content += f"| {empty['grade_percent'][i]:<7} | {empty['rimpull_kn'][i]:<12.1f} | {empty['rimpull_tf'][i]:<12.2f} | {empty['speed_kmh'][i]:<12} |\n"
        
        if 'loaded' in gradeability:
            loaded = gradeability['loaded']
            md_content += f"""
**Loaded Truck ({loaded.get('weight_kg', 0):,} kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
"""
            for i in range(len(loaded.get('grade_percent', []))):
                md_content += f"| {loaded['grade_percent'][i]:<7} | {loaded['rimpull_kn'][i]:<12.1f} | {loaded['rimpull_tf'][i]:<12.2f} | {loaded['speed_kmh'][i]:<12} |\n"
    
    # Corrections and validation
    if metadata.get('corrections_applied'):
        md_content += "\n## Corrections Applied\n\n"
        for correction in metadata['corrections_applied']:
            md_content += f"- {correction}\n"
    
    if metadata.get('validation_method'):
        md_content += f"""
## Validation

**Method:** {metadata.get('validation_method', 'N/A')}  
**Status:** {metadata.get('validation_status', 'N/A')}
"""
    
    if metadata.get('comparison_equipment'):
        md_content += "\n**Compared with:**\n"
        for equip in metadata['comparison_equipment']:
            md_content += f"- {equip}\n"
    
    if metadata.get('notes'):
        md_content += f"\n## Notes\n\n{metadata['notes']}\n"
    
    if metadata.get('warnings'):
        md_content += "\n## ⚠️ Warnings\n\n"
        for warning in metadata['warnings']:
            md_content += f"- {warning}\n"
    
    md_content += f"""
---
*Generated on {datetime.now().strftime('%Y-%m-%d')}*  
*Version: {metadata.get('version', 'N/A')}*
"""
    
    with open(output_file, 'w') as f:
        f.write(md_content)
    
    print(f"Generated curve fitting summary: {output_file}")


def export_to_csv(
    model: str,
    performance_curves: Dict,
    output_dir: Path
) -> None:
    """
    Export performance curves to CSV files.
    
    Args:
        model: Model identifier (e.g., 'cat_794_ac')
        performance_curves: Performance curves dictionary
        output_dir: Directory to save CSV files
    """
    import csv
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export rimpull curve
    rimpull = performance_curves.get('rimpull_curve', {}).get('data', {})
    if rimpull:
        filename = f'{model}_rimpull_curve.csv'
        with open(output_dir / filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Speed (km/h)', 'Rimpull (kN)', 'Rimpull (tf)'])
            for i in range(len(rimpull['speed_kmh'])):
                writer.writerow([
                    rimpull['speed_kmh'][i],
                    rimpull['rimpull_kn'][i],
                    rimpull['rimpull_tf'][i]
                ])
        print(f"Exported rimpull curve to {output_dir / filename}")
    
    # Export retarding curve
    retarding = performance_curves.get('retarding_curve', {}).get('data', {})
    if retarding:
        filename = f'{model}_retarding_curve.csv'
        with open(output_dir / filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Speed (km/h)', 'Retarding (kN)', 'Retarding (tf)'])
            for i in range(len(retarding['speed_kmh'])):
                writer.writerow([
                    retarding['speed_kmh'][i],
                    retarding['retarding_kn'][i],
                    retarding['retarding_tf'][i]
                ])
        print(f"Exported retarding curve to {output_dir / filename}")
    
    # Export gradeability data
    gradeability = performance_curves.get('gradeability_data', {})
    if gradeability:
        filename = f'{model}_gradeability_data.csv'
        with open(output_dir / filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Condition', 'Speed (km/h)', 'Grade (%)', 'Rimpull (kN)', 'Rimpull (tf)'])
            
            # Export empty truck data
            if 'empty' in gradeability:
                empty = gradeability['empty']
                for i in range(len(empty['speed_kmh'])):
                    writer.writerow([
                        'Empty',
                        empty['speed_kmh'][i],
                        empty['grade_percent'][i],
                        empty['rimpull_kn'][i],
                        empty['rimpull_tf'][i]
                    ])
            
            # Export loaded truck data
            if 'loaded' in gradeability:
                loaded = gradeability['loaded']
                for i in range(len(loaded['speed_kmh'])):
                    writer.writerow([
                        'Loaded',
                        loaded['speed_kmh'][i],
                        loaded['grade_percent'][i],
                        loaded['rimpull_kn'][i],
                        loaded['rimpull_tf'][i]
                    ])
        print(f"Exported gradeability data to {output_dir / filename}")
    
    # Export fitted gradeability curves
    gradeability_curves = performance_curves.get('gradeability_curves', {})
    if gradeability_curves:
        filename = f'{model}_gradeability_curves.csv'
        with open(output_dir / filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Condition', 'Grade (%)', 'Fitted Speed (km/h)', 'Model Type', 'R²', 'RMSE (km/h)'])
            
            model_type = gradeability_curves.get('model_type', 'exponential_decay')
            
            # Export empty truck fitted curve
            if 'empty' in gradeability_curves:
                empty = gradeability_curves['empty']
                curve_data = empty.get('fitted_curve', {})
                quality = empty.get('fitting_quality', {})
                r_squared = quality.get('r_squared', '')
                rmse = quality.get('rmse_kmh', '')
                
                grades = curve_data.get('grade_percent', [])
                speeds = curve_data.get('speed_kmh', [])
                
                for i in range(len(grades)):
                    writer.writerow([
                        'Empty',
                        grades[i],
                        speeds[i],
                        model_type,
                        r_squared if i == 0 else '',  # Only show on first row
                        rmse if i == 0 else ''
                    ])
            
            # Export loaded truck fitted curve
            if 'loaded' in gradeability_curves:
                loaded = gradeability_curves['loaded']
                curve_data = loaded.get('fitted_curve', {})
                quality = loaded.get('fitting_quality', {})
                r_squared = quality.get('r_squared', '')
                rmse = quality.get('rmse_kmh', '')
                
                grades = curve_data.get('grade_percent', [])
                speeds = curve_data.get('speed_kmh', [])
                
                for i in range(len(grades)):
                    writer.writerow([
                        'Loaded',
                        grades[i],
                        speeds[i],
                        model_type,
                        r_squared if i == 0 else '',
                        rmse if i == 0 else ''
                    ])
        print(f"Exported gradeability curves to {output_dir / filename}")
    
    # Export grade-speed lookup tables
    grade_speed_lookup = performance_curves.get('grade_speed_lookup', {})
    if grade_speed_lookup:
        for condition in ['empty', 'loaded']:
            if condition not in grade_speed_lookup:
                continue
            
            lookup = grade_speed_lookup[condition]
            filename = f'{model}_grade_speed_{condition}.csv'
            
            with open(output_dir / filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Grade (%)', 'Speed (km/h)', 'Limiting Factor'])
                
                for entry in lookup.get('data', []):
                    writer.writerow([
                        entry['grade_pct'],
                        entry['speed_kmh'],
                        entry['limiting_factor']
                    ])
            
            print(f"Exported grade-speed lookup to {output_dir / filename}")


if __name__ == "__main__":
    print("Export Utilities")
    print("Import this module to use export functions")
