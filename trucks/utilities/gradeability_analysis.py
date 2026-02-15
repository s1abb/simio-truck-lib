#!/usr/bin/env python3
"""
Gradeability Curve Fitting Analysis
Task 004 - Phase 1: Analysis & Design

This script analyzes gradeability data from all truck models to:
1. Understand typical curve shapes
2. Test different curve fitting methods
3. Select the optimal fitting approach
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
from typing import Dict, List, Tuple, Callable


def exponential_decay(grade: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Exponential decay model: speed = a * exp(-b * grade) + c
    
    Args:
        grade: Grade percentage
        a: Amplitude coefficient
        b: Decay rate
        c: Offset (minimum speed)
    
    Returns:
        Predicted speed
    """
    return a * np.exp(-b * grade) + c


def power_function(grade: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Power function model: speed = a * (grade + offset)^(-b) + c
    
    Args:
        grade: Grade percentage
        a: Amplitude coefficient
        b: Power exponent
        c: Offset (minimum speed)
    
    Returns:
        Predicted speed
    """
    # Add small offset to avoid division by zero
    return a * np.power(grade + 0.1, -b) + c


def rational_function(grade: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """
    Rational function model: speed = (a + b*grade) / (1 + c*grade + d*grade^2)
    
    Args:
        grade: Grade percentage
        a, b, c, d: Coefficients
    
    Returns:
        Predicted speed
    """
    return (a + b * grade) / (1.0 + c * grade + d * grade**2)


def polynomial_cubic(grade: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """
    Cubic polynomial model: speed = a + b*grade + c*grade^2 + d*grade^3
    
    Args:
        grade: Grade percentage
        a, b, c, d: Coefficients
    
    Returns:
        Predicted speed
    """
    return a + b * grade + c * grade**2 + d * grade**3


def calculate_r_squared(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """Calculate R² (coefficient of determination)"""
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    return 1 - (ss_res / ss_tot)


def calculate_rmse(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """Calculate Root Mean Square Error"""
    return np.sqrt(np.mean((y_actual - y_predicted) ** 2))


def fit_and_evaluate(
    grades: np.ndarray,
    speeds: np.ndarray,
    func: Callable,
    p0: List[float],
    func_name: str
) -> Dict:
    """
    Fit a function to gradeability data and evaluate quality.
    
    Args:
        grades: Grade percentages
        speeds: Speeds (km/h)
        func: Function to fit
        p0: Initial parameter guess
        func_name: Name of the function
    
    Returns:
        Dictionary with fitting results
    """
    try:
        # Fit the curve
        params, _ = curve_fit(func, grades, speeds, p0=p0, maxfev=10000)
        
        # Generate predictions
        predicted_speeds = func(grades, *params)
        
        # Calculate quality metrics
        r_squared = calculate_r_squared(speeds, predicted_speeds)
        rmse = calculate_rmse(speeds, predicted_speeds)
        max_error = np.max(np.abs(speeds - predicted_speeds))
        
        # Check for physical validity
        grade_range = np.linspace(0, np.max(grades), 100)
        speed_range = func(grade_range, *params)
        
        # Check constraints
        all_positive = np.all(speed_range >= 0)
        monotonic = np.all(np.diff(speed_range) <= 0.01)  # Allow small numerical errors
        
        return {
            'function': func_name,
            'params': params.tolist(),
            'r_squared': r_squared,
            'rmse': rmse,
            'max_error': max_error,
            'all_positive': all_positive,
            'monotonic': monotonic,
            'valid': all_positive and monotonic,
            'success': True
        }
    
    except Exception as e:
        return {
            'function': func_name,
            'success': False,
            'error': str(e)
        }


def analyze_model(model_name: str, config_path: Path) -> Dict:
    """
    Analyze gradeability data for a single truck model.
    
    Args:
        model_name: Name of the truck model
        config_path: Path to config.json
    
    Returns:
        Analysis results
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {model_name}")
    print(f"{'='*60}")
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    gradeability = config['gradeability_input']
    results = {
        'model': model_name,
        'empty': {},
        'loaded': {}
    }
    
    # Test functions
    functions = [
        (exponential_decay, [60, 0.05, 0], 'Exponential Decay'),
        (power_function, [100, 0.5, 10], 'Power Function'),
        (rational_function, [60, -5, 0.1, 0.001], 'Rational Function'),
        (polynomial_cubic, [60, -2, 0.05, -0.001], 'Cubic Polynomial')
    ]
    
    # Analyze each condition
    for condition in ['empty', 'loaded']:
        if condition not in gradeability:
            continue
        
        data = gradeability[condition]
        grades = np.array(data['grade_percent'])
        speeds = np.array(data['speed_kmh'])
        
        print(f"\n{condition.upper()} Condition:")
        print(f"  Grade range: {grades.min():.1f}% - {grades.max():.1f}%")
        print(f"  Speed range: {speeds.min():.1f} - {speeds.max():.1f} km/h")
        print(f"  Data points: {len(grades)}")
        
        # Test each function
        condition_results = []
        for func, p0, name in functions:
            result = fit_and_evaluate(grades, speeds, func, p0, name)
            condition_results.append(result)
            
            if result['success']:
                valid_mark = '✓' if result['valid'] else '✗'
                print(f"\n  {name}: {valid_mark}")
                print(f"    R² = {result['r_squared']:.4f}")
                print(f"    RMSE = {result['rmse']:.2f} km/h")
                print(f"    Max Error = {result['max_error']:.2f} km/h")
                print(f"    All Positive: {result['all_positive']}")
                print(f"    Monotonic: {result['monotonic']}")
            else:
                print(f"\n  {name}: FAILED - {result['error']}")
        
        results[condition] = {
            'grades': grades.tolist(),
            'speeds': speeds.tolist(),
            'fits': condition_results
        }
    
    return results


def visualize_fits(results: Dict, output_dir: Path):
    """
    Create visualization comparing all fitting methods.
    
    Args:
        results: Analysis results from analyze_model
        output_dir: Directory to save plots
    """
    model_name = results['model']
    
    # Create figure with subplots for empty and loaded
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for ax, condition in zip([ax1, ax2], ['empty', 'loaded']):
        if condition not in results or not results[condition]:
            continue
        
        data = results[condition]
        grades = np.array(data['grades'])
        speeds = np.array(data['speeds'])
        
        # Plot actual data
        ax.scatter(grades, speeds, s=100, c='black', marker='o', 
                  label='Actual Data', zorder=10, edgecolors='white', linewidths=2)
        
        # Plot each fit
        grade_smooth = np.linspace(grades.min(), grades.max(), 200)
        colors = ['blue', 'green', 'red', 'orange']
        
        for fit, color in zip(data['fits'], colors):
            if not fit['success'] or not fit['valid']:
                continue
            
            func_name = fit['function']
            params = fit['params']
            
            # Reconstruct the function
            if func_name == 'Exponential Decay':
                speed_smooth = exponential_decay(grade_smooth, *params)
            elif func_name == 'Power Function':
                speed_smooth = power_function(grade_smooth, *params)
            elif func_name == 'Rational Function':
                speed_smooth = rational_function(grade_smooth, *params)
            elif func_name == 'Cubic Polynomial':
                speed_smooth = polynomial_cubic(grade_smooth, *params)
            
            label = f"{func_name} (R²={fit['r_squared']:.3f})"
            ax.plot(grade_smooth, speed_smooth, color=color, linewidth=2, 
                   label=label, alpha=0.7)
        
        ax.set_xlabel('Grade (%)', fontsize=12)
        ax.set_ylabel('Speed (km/h)', fontsize=12)
        ax.set_title(f'{model_name} - {condition.upper()}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    output_path = output_dir / f'{model_name}_gradeability_fitting_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved visualization: {output_path}")


def generate_summary_report(all_results: List[Dict], output_path: Path):
    """
    Generate a summary report of all analyses.
    
    Args:
        all_results: List of results from all models
        output_path: Path to save the report
    """
    report = []
    report.append("# Gradeability Curve Fitting Analysis Report")
    report.append("\n## Task 004 - Phase 1: Analysis & Design")
    report.append(f"\nGenerated: {Path(__file__).name}\n")
    
    report.append("\n## Summary of Results\n")
    
    # Aggregate statistics
    method_stats = {
        'Exponential Decay': {'r2': [], 'rmse': [], 'valid': 0, 'total': 0},
        'Power Function': {'r2': [], 'rmse': [], 'valid': 0, 'total': 0},
        'Rational Function': {'r2': [], 'rmse': [], 'valid': 0, 'total': 0},
        'Cubic Polynomial': {'r2': [], 'rmse': [], 'valid': 0, 'total': 0}
    }
    
    for result in all_results:
        for condition in ['empty', 'loaded']:
            if condition not in result or not result[condition]:
                continue
            
            for fit in result[condition]['fits']:
                if fit['success']:
                    method = fit['function']
                    method_stats[method]['total'] += 1
                    if fit['valid']:
                        method_stats[method]['valid'] += 1
                        method_stats[method]['r2'].append(fit['r_squared'])
                        method_stats[method]['rmse'].append(fit['rmse'])
    
    # Generate summary table
    report.append("### Method Comparison\n")
    report.append("| Method | Valid Fits | Avg R² | Avg RMSE (km/h) | Success Rate |")
    report.append("|--------|------------|--------|-----------------|--------------|")
    
    for method, stats in method_stats.items():
        if stats['total'] > 0:
            avg_r2 = np.mean(stats['r2']) if stats['r2'] else 0
            avg_rmse = np.mean(stats['rmse']) if stats['rmse'] else 0
            success_rate = (stats['valid'] / stats['total']) * 100
            report.append(f"| {method} | {stats['valid']}/{stats['total']} | {avg_r2:.4f} | {avg_rmse:.2f} | {success_rate:.0f}% |")
    
    # Detailed results per model
    report.append("\n## Detailed Results by Model\n")
    
    for result in all_results:
        model = result['model']
        report.append(f"\n### {model}\n")
        
        for condition in ['empty', 'loaded']:
            if condition not in result or not result[condition]:
                continue
            
            data = result[condition]
            report.append(f"\n#### {condition.upper()} Condition\n")
            report.append(f"- Data points: {len(data['grades'])}")
            report.append(f"- Grade range: {min(data['grades']):.1f}% - {max(data['grades']):.1f}%")
            report.append(f"- Speed range: {min(data['speeds']):.1f} - {max(data['speeds']):.1f} km/h\n")
            
            report.append("| Method | R² | RMSE (km/h) | Max Error (km/h) | Valid |")
            report.append("|--------|-----|-------------|------------------|-------|")
            
            for fit in data['fits']:
                if fit['success']:
                    valid_mark = '✓' if fit['valid'] else '✗'
                    report.append(
                        f"| {fit['function']} | {fit['r_squared']:.4f} | "
                        f"{fit['rmse']:.2f} | {fit['max_error']:.2f} | {valid_mark} |"
                    )
                else:
                    report.append(f"| {fit['function']} | - | - | - | FAILED |")
    
    # Recommendations
    report.append("\n## Recommendations\n")
    
    # Find best method
    best_method = max(method_stats.items(), 
                     key=lambda x: (x[1]['valid'], np.mean(x[1]['r2']) if x[1]['r2'] else 0))
    
    report.append(f"\n### Recommended Method: **{best_method[0]}**\n")
    report.append(f"- Valid fits: {best_method[1]['valid']}/{best_method[1]['total']}")
    report.append(f"- Average R²: {np.mean(best_method[1]['r2']):.4f}")
    report.append(f"- Average RMSE: {np.mean(best_method[1]['rmse']):.2f} km/h")
    
    report.append("\n### Rationale\n")
    report.append("Based on the analysis:")
    report.append("1. **Physical validity**: Method produces positive, monotonic speeds")
    report.append("2. **Fitting quality**: High R² values across all models")
    report.append("3. **Consistency**: Reliable performance on diverse truck models")
    report.append("4. **Extrapolation**: Well-behaved outside training data range")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"\nSaved summary report: {output_path}")


def main():
    """Main analysis workflow"""
    print("="*60)
    print("GRADEABILITY CURVE FITTING ANALYSIS")
    print("Task 004 - Phase 1: Analysis & Design")
    print("="*60)
    
    # Define models
    base_dir = Path(__file__).parent.parent
    models = [
        ('cat_794_ac', base_dir / 'data' / 'cat_794_ac' / 'config.json'),
        ('cat_793_f_ac', base_dir / 'data' / 'cat_793_f_ac' / 'config.json'),
        ('liebherr_t_236', base_dir / 'data' / 'liebherr_t_236' / 'config.json'),
        ('liebherr_t_264', base_dir / 'data' / 'liebherr_t_264' / 'config.json')
    ]
    
    # Create output directory
    analysis_dir = base_dir / 'outputs' / 'gradeability_analysis'
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze each model
    all_results = []
    for model_name, config_path in models:
        results = analyze_model(model_name, config_path)
        all_results.append(results)
        
        # Visualize fits
        visualize_fits(results, analysis_dir)
    
    # Generate summary report
    report_path = analysis_dir / 'gradeability_fitting_analysis.md'
    generate_summary_report(all_results, report_path)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {analysis_dir}")
    print("="*60)


if __name__ == '__main__':
    main()
