"""
Main script for processing equipment performance data.

This script orchestrates the complete workflow:
1. Load gradeability data
2. Fit performance curves
3. Generate visualizations
4. Export documentation and data files
"""

import json
from pathlib import Path
import argparse
import sys

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent))

from curve_fitting import (
    fit_curve, 
    generate_rimpull_curve, 
    generate_retarding_curve,
    extract_gradeability_data,
    compare_models,
    generate_gradeability_curves,
    generate_grade_speed_lookup
)
from visualization import generate_all_plots
from export_utils import (
    generate_quick_reference,
    generate_curve_fitting_summary,
    export_to_csv
)


def process_equipment(
    model: str,
    config_file: Path,
    output_base_dir: Path
):
    """
    Process equipment data from configuration file.
    
    Args:
        model: Model identifier (e.g., 'cat_794_ac')
        config_file: Path to configuration JSON file
        output_base_dir: Base directory for outputs
    """
    print(f"\n{'='*60}")
    print(f"Processing: {model.upper()}")
    print(f"{'='*60}\n")
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Extract data from config
    specs = config.get('specifications', {})
    gradeability_input = config.get('gradeability_input', {})
    retarding_input = config.get('retarding_input', {})
    
    # Prepare output directories
    data_dir = output_base_dir / 'data' / model
    output_dir = output_base_dir / 'outputs' / model
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Structure gradeability data
    print("Step 1: Structuring gradeability data...")
    gradeability_data = extract_gradeability_data(
        grades_empty=gradeability_input['empty']['grade_percent'],
        rimpull_empty=gradeability_input['empty']['rimpull'],
        speed_empty=gradeability_input['empty']['speed_kmh'],
        grades_loaded=gradeability_input['loaded']['grade_percent'],
        rimpull_loaded=gradeability_input['loaded']['rimpull'],
        speed_loaded=gradeability_input['loaded']['speed_kmh'],
        empty_weight_kg=specs['weights']['empty_kg'],
        loaded_weight_kg=specs['weights']['loaded_kg'],
        unit=gradeability_input.get('unit', 'kN')
    )
    
    # Step 2: Fit rimpull curve
    print("Step 2: Fitting rimpull curve...")
    
    # Combine empty and loaded data for fitting
    import numpy as np
    all_speeds = np.array(
        gradeability_data['empty']['speed_kmh'] + 
        gradeability_data['loaded']['speed_kmh']
    )
    all_forces = np.array(
        gradeability_data['empty']['rimpull_kn'] + 
        gradeability_data['loaded']['rimpull_kn']
    )
    
    # Fit curve
    fitted_func, coeffs, quality = fit_curve(
        all_speeds,
        all_forces,
        model_type=config.get('fitting_method', 'rational'),
        max_force=config.get('max_rimpull_kn')
    )
    
    print(f"  R² = {quality['r_squared']:.6f}")
    print(f"  RMSE = {quality['rmse_kn']:.2f} kN")
    
    # Generate complete rimpull curve
    # Use max speed from specifications, default to 70 if not specified
    max_speed = config.get('specifications', {}).get('drivetrain', {}).get('max_speed_kmh_loaded', 70)
    rimpull_data = generate_rimpull_curve(
        speed_range=(0, max_speed),
        speed_step=1.0,
        fitted_function=fitted_func,
        max_rimpull_kn=config.get('max_rimpull_kn')
    )
    
    # Step 2.5: Fit gradeability curves
    print("Step 2.5: Fitting gradeability curves...")
    gradeability_curves = generate_gradeability_curves(
        gradeability_input=gradeability_input,
        grade_step=0.5
    )
    
    # Print quality metrics
    for condition in ['empty', 'loaded']:
        if condition in gradeability_curves:
            quality = gradeability_curves[condition]['fitting_quality']
            print(f"  {condition.upper()}: R² = {quality['r_squared']:.4f}, RMSE = {quality['rmse_kmh']:.2f} km/h")
    
    # Step 3: Generate retarding curve
    print("Step 3: Generating retarding curve...")
    retarding_data = generate_retarding_curve(
        retarding_power_kw=retarding_input.get('continuous_power_kw', 0),
        efficiency=retarding_input.get('efficiency', 0.85),
        speed_range=(1, max_speed),
        max_retarding_kn=retarding_input.get('max_retarding_kn', 2000)
    )
    
    # Step 3.5: Generate grade-speed lookup tables
    print("Step 3.5: Generating grade-speed lookup tables...")
    grade_speed_lookup = {}
    for condition in ['empty', 'loaded']:
        lookup = generate_grade_speed_lookup(
            specifications=specs,
            gradeability_curves=gradeability_curves,
            retarding_data={'speed_kmh': retarding_data['speed_kmh'], 
                          'retarding_kn': retarding_data['retarding_kn']},
            condition=condition,
            min_grade=-15.0,
            max_grade=20.0,
            grade_step=1.0
        )
        grade_speed_lookup[condition] = lookup
        
        # Print summary
        data = lookup['data']
        descent_speeds = [d['speed_kmh'] for d in data if d['grade_pct'] < 0]
        climb_speeds = [d['speed_kmh'] for d in data if d['grade_pct'] > 0]
        print(f"  {condition.upper()}: Descent {min(descent_speeds):.0f}-{max(descent_speeds):.0f} km/h, "
              f"Climb {min(climb_speeds):.0f}-{max(climb_speeds):.0f} km/h")
    
    # Step 4: Structure output data
    print("Step 4: Structuring output files...")
    
    # Specifications
    specifications = config['specifications']
    with open(data_dir / 'specifications.json', 'w') as f:
        json.dump(specifications, f, indent=2)
    
    # Performance curves
    performance_curves = {
        'rimpull_curve': {
            'description': 'Maximum available rimpull force vs speed',
            'conditions': config.get('conditions', 'Standard conditions'),
            'model_type': config.get('fitting_method', 'rational'),
            'formula': config.get('formula', ''),
            'constraints': {
                'max_rimpull_kn': config.get('max_rimpull_kn'),
                'max_speed_kmh': max_speed,
                'min_speed_kmh': 0
            },
            'units': {
                'speed': 'km/h',
                'force_kn': 'kilonewtons',
                'force_tf': 'tonnes-force'
            },
            'data': rimpull_data
        },
        'retarding_curve': {
            'description': 'Continuous retarding force vs speed',
            'conditions': 'Continuous operation',
            'continuous_power_kw': retarding_input.get('continuous_power_kw'),
            'continuous_power_hp': retarding_input.get('continuous_power_hp'),
            'efficiency': retarding_input.get('efficiency', 0.85),
            'type': retarding_input.get('type', 'dynamic_brake'),
            'units': {
                'speed': 'km/h',
                'force_kn': 'kilonewtons',
                'force_tf': 'tonnes-force'
            },
            'data': retarding_data
        },
        'gradeability_data': gradeability_data,
        'gradeability_curves': gradeability_curves,
        'grade_speed_lookup': grade_speed_lookup
    }
    
    with open(data_dir / 'performance_curves.json', 'w') as f:
        json.dump(performance_curves, f, indent=2)
    
    # Metadata
    metadata = {
        'data_source': config.get('data_source', ''),
        'extraction_date': config.get('extraction_date', ''),
        'extracted_by': config.get('extracted_by', 'automated'),
        'fitting_method': config.get('fitting_method', 'rational'),
        'fitting_quality': quality,
        'corrections_applied': config.get('corrections_applied', []),
        'validation_status': config.get('validation_status', 'draft'),
        'validation_method': config.get('validation_method', ''),
        'comparison_equipment': config.get('comparison_equipment', []),
        'notes': config.get('notes', ''),
        'warnings': config.get('warnings', []),
        'version': '1.0.0',
        'last_updated': config.get('extraction_date', '')
    }
    
    with open(data_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Step 5: Generate visualizations
    print("Step 5: Generating visualizations...")
    generate_all_plots(model, data_dir, output_dir)
    
    # Step 6: Generate documentation
    print("Step 6: Generating documentation...")
    generate_quick_reference(
        model, specifications, performance_curves, metadata,
        output_dir / 'quick_reference.md'
    )
    generate_curve_fitting_summary(
        model, performance_curves, metadata,
        output_dir / 'curve_fitting_summary.md'
    )
    
    # Step 7: Export CSV files
    print("Step 7: Exporting CSV files...")
    export_to_csv(model, performance_curves, output_dir)
    
    print(f"\n✅ Processing complete for {model}!")
    print(f"   Data saved to: {data_dir}")
    print(f"   Outputs saved to: {output_dir}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Process equipment performance data'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Model identifier (e.g., cat_794_ac)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        required=True,
        help='Path to configuration JSON file'
    )
    # Default to trucks directory (parent of utilities)
    trucks_dir = Path(__file__).parent.parent
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=trucks_dir,
        help='Base output directory (default: trucks directory)'
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    process_equipment(args.model, args.config, args.output_dir)


if __name__ == "__main__":
    main()
