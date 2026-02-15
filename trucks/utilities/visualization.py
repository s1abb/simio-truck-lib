"""
Visualization utilities for equipment performance curves.

Generates standardized charts and plots for documentation.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json


def plot_performance_curves(
    performance_data: Dict,
    title: str = "Performance Curves",
    output_file: Optional[Path] = None,
    show_gradeability_points: bool = True
) -> None:
    """
    Plot rimpull and retarding curves with optional gradeability data points.
    
    Args:
        performance_data: Performance curves dictionary
        title: Plot title
        output_file: Path to save PNG (None to display only)
        show_gradeability_points: Whether to show original data points
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Extract data
    rimpull = performance_data.get('rimpull_curve', {})
    retarding = performance_data.get('retarding_curve', {})
    gradeability = performance_data.get('gradeability_data', {})
    
    # Plot 1: Rimpull curve
    if 'data' in rimpull:
        speeds = rimpull['data']['speed_kmh']
        forces = rimpull['data']['rimpull_kn']
        ax1.plot(speeds, forces, 'b-', linewidth=2, label='Fitted Curve')
        
        # Plot original data points if available
        if show_gradeability_points and gradeability:
            if 'empty' in gradeability:
                ax1.scatter(
                    gradeability['empty']['speed_kmh'],
                    gradeability['empty']['rimpull_kn'],
                    c='green', s=100, marker='o', label='Empty (data)', zorder=5
                )
            if 'loaded' in gradeability:
                ax1.scatter(
                    gradeability['loaded']['speed_kmh'],
                    gradeability['loaded']['rimpull_kn'],
                    c='red', s=100, marker='s', label='Loaded (data)', zorder=5
                )
    
    ax1.set_xlabel('Speed (km/h)', fontsize=12)
    ax1.set_ylabel('Rimpull Force (kN)', fontsize=12)
    ax1.set_title('Rimpull vs Speed', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Retarding curve
    if 'data' in retarding:
        speeds = retarding['data']['speed_kmh']
        forces = retarding['data']['retarding_kn']
        ax2.plot(speeds, forces, 'r-', linewidth=2, label='Retarding Curve')
    
    ax2.set_xlabel('Speed (km/h)', fontsize=12)
    ax2.set_ylabel('Retarding Force (kN)', fontsize=12)
    ax2.set_title('Retarding vs Speed', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {output_file}")
    else:
        plt.show()
    
    plt.close()


def plot_comparison(
    models: List[str],
    data_dir: Path,
    output_file: Optional[Path] = None,
    curve_type: str = 'rimpull'
) -> None:
    """
    Plot comparison of multiple equipment models.
    
    Args:
        models: List of model identifiers (e.g., ['cat_793f', 'cat_794_ac'])
        data_dir: Base directory containing model data subdirectories
        output_file: Path to save PNG
        curve_type: 'rimpull' or 'retarding'
    """
    plt.figure(figsize=(12, 7))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, model in enumerate(models):
        model_file = data_dir / model / 'performance_curves.json'
        
        if not model_file.exists():
            print(f"Warning: {model_file} not found, skipping")
            continue
        
        with open(model_file, 'r') as f:
            data = json.load(f)
        
        if curve_type == 'rimpull':
            curve_data = data.get('rimpull_curve', {}).get('data', {})
            speeds = curve_data.get('speed_kmh', [])
            forces = curve_data.get('rimpull_kn', [])
            ylabel = 'Rimpull Force (kN)'
            title = 'Rimpull Comparison'
        else:
            curve_data = data.get('retarding_curve', {}).get('data', {})
            speeds = curve_data.get('speed_kmh', [])
            forces = curve_data.get('retarding_kn', [])
            ylabel = 'Retarding Force (kN)'
            title = 'Retarding Comparison'
        
        if speeds and forces:
            plt.plot(speeds, forces, linewidth=2, color=colors[i % len(colors)],
                    label=model.replace('_', ' ').upper())
    
    plt.xlabel('Speed (km/h)', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved comparison plot to {output_file}")
    else:
        plt.show()
    
    plt.close()


def plot_gradeability_chart(
    gradeability_data: Dict,
    gradeability_curves: Dict = None,
    title: str = "Gradeability Chart",
    output_file: Optional[Path] = None
) -> None:
    """
    Plot traditional gradeability chart (grade % vs speed).
    
    Shows both raw data points and fitted curves (if available).
    
    Args:
        gradeability_data: Gradeability data dictionary (raw points)
        gradeability_curves: Fitted gradeability curves (optional)
        title: Plot title
        output_file: Path to save PNG
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot fitted curves first (if available)
    if gradeability_curves:
        for condition, color, label_suffix in [('empty', 'green', 'Empty'), ('loaded', 'red', 'Loaded')]:
            if condition in gradeability_curves:
                curve_data = gradeability_curves[condition]['fitted_curve']
                speeds = curve_data['speed_kmh']
                grades = curve_data['grade_percent']
                
                # Plot fitted curve as smooth line
                ax.plot(speeds, grades, color=color, linewidth=2.5, alpha=0.6, 
                       label=f'{label_suffix} (fitted)', linestyle='-')
    
    # Plot raw data points on top
    if 'empty' in gradeability_data:
        empty = gradeability_data['empty']
        speeds = empty['speed_kmh']
        grades = empty['grade_percent']
        
        # Remove duplicate speeds - keep the point with highest grade for each speed
        speed_grade_dict = {}
        for s, g in zip(speeds, grades):
            if s not in speed_grade_dict or g > speed_grade_dict[s]:
                speed_grade_dict[s] = g
        
        # Sort by speed
        sorted_speeds = sorted(speed_grade_dict.keys())
        sorted_grades = [speed_grade_dict[s] for s in sorted_speeds]
        
        # Plot raw data points
        ax.scatter(sorted_speeds, sorted_grades, 
                  c='green', s=120, marker='o', label='Empty (data)', 
                  zorder=10, edgecolors='darkgreen', linewidths=2)
    
    # Plot loaded truck
    if 'loaded' in gradeability_data:
        loaded = gradeability_data['loaded']
        speeds = loaded['speed_kmh']
        grades = loaded['grade_percent']
        
        # Remove duplicate speeds - keep the point with highest grade for each speed
        speed_grade_dict = {}
        for s, g in zip(speeds, grades):
            if s not in speed_grade_dict or g > speed_grade_dict[s]:
                speed_grade_dict[s] = g
        
        # Sort by speed
        sorted_speeds = sorted(speed_grade_dict.keys())
        sorted_grades = [speed_grade_dict[s] for s in sorted_speeds]
        
        # Plot raw data points
        ax.scatter(sorted_speeds, sorted_grades,
                  c='red', s=120, marker='s', label='Loaded (data)', 
                  zorder=10, edgecolors='darkred', linewidths=2)
    
    # Add R² annotations if curves available
    if gradeability_curves:
        y_pos = 0.98
        for condition in ['empty', 'loaded']:
            if condition in gradeability_curves:
                r2 = gradeability_curves[condition]['fitting_quality']['r_squared']
                ax.text(0.02, y_pos, f'{condition.capitalize()} R² = {r2:.4f}', 
                       transform=ax.transAxes, fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                y_pos -= 0.06
    
    ax.set_xlabel('Speed (km/h)', fontsize=12)
    ax.set_ylabel('Grade (%)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')
    ax.invert_xaxis()  # Traditional gradeability charts show high speed on left
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved gradeability chart to {output_file}")
    else:
        plt.show()
    
    plt.close()


def generate_all_plots(
    model: str,
    data_dir: Path,
    output_dir: Path
) -> None:
    """
    Generate all standard plots for a model.
    
    Args:
        model: Model identifier
        data_dir: Directory containing performance_curves.json
        output_dir: Directory to save plots
    """
    # Load performance data
    perf_file = data_dir / 'performance_curves.json'
    if not perf_file.exists():
        print(f"Error: {perf_file} not found")
        return
    
    with open(perf_file, 'r') as f:
        performance_data = json.load(f)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate performance curves plot
    plot_performance_curves(
        performance_data,
        title=f"{model.replace('_', ' ').upper()} - Performance Curves",
        output_file=output_dir / 'performance_curves.png'
    )
    
    # Generate gradeability chart if data exists
    if 'gradeability_data' in performance_data:
        gradeability_curves = performance_data.get('gradeability_curves', None)
        plot_gradeability_chart(
            performance_data['gradeability_data'],
            gradeability_curves=gradeability_curves,
            title=f"{model.replace('_', ' ').upper()} - Gradeability",
            output_file=output_dir / 'gradeability_chart.png'
        )
    
    print(f"Generated all plots for {model} in {output_dir}")


if __name__ == "__main__":
    print("Visualization Utilities")
    print("Import this module to use plotting functions")
