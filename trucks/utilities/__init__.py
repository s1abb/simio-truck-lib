"""
Mining Equipment Performance Data Utilities

This package provides tools for processing equipment performance curves.

Main modules:
- curve_fitting: Fit mathematical curves to gradeability data
- visualization: Generate charts and plots
- export_utils: Export documentation and data files
- process_equipment: Main processing pipeline

Example usage:
    from utilities import curve_fitting, visualization
    
    # Fit curves
    func, coeffs, quality = curve_fitting.fit_curve(speeds, forces, 'rational')
    
    # Generate plots
    visualization.generate_all_plots('cat_794_ac', data_dir, output_dir)
"""

__version__ = '1.0.0'
__author__ = 'Simio Electric Truck Library Team'

# Make main utilities easily accessible
from . import curve_fitting
from . import visualization
from . import export_utils

__all__ = [
    'curve_fitting',
    'visualization',
    'export_utils',
]
