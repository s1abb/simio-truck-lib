"""
Curve fitting utilities for mining equipment performance curves.

This module provides functions to fit mathematical curves to gradeability data
and generate complete performance curves for simulation use.
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, List, Tuple, Callable
import json


def rational_function(v: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """
    Rational function model: F = (a + b*v) / (1 + c*v + d*v²)
    
    Best for AC electric drive trucks with smooth torque curves.
    
    Args:
        v: Speed array (km/h)
        a, b, c, d: Model coefficients
        
    Returns:
        Force array (kN)
    """
    return (a + b * v) / (1 + c * v + d * v**2)


def polynomial_function(v: np.ndarray, *coeffs: float) -> np.ndarray:
    """
    Polynomial model: F = a + b*v + c*v² + d*v³ + ...
    
    Args:
        v: Speed array (km/h)
        coeffs: Polynomial coefficients (a, b, c, ...)
        
    Returns:
        Force array (kN)
    """
    return np.polyval(coeffs[::-1], v)


def power_function(v: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Power function model: F = a / (v + b)^c
    
    Args:
        v: Speed array (km/h)
        a, b, c: Model coefficients
        
    Returns:
        Force array (kN)
    """
    return a / (v + b)**c


def exponential_function(v: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Exponential decay model: F = a * exp(-b*v) + c
    
    Args:
        v: Speed array (km/h)
        a, b, c: Model coefficients
        
    Returns:
        Force array (kN)
    """
    return a * np.exp(-b * v) + c


def fit_curve(
    speed_data: np.ndarray,
    force_data: np.ndarray,
    model_type: str = 'rational',
    max_force: float = None
) -> Tuple[Callable, np.ndarray, Dict]:
    """
    Fit a curve to gradeability data points.
    
    Args:
        speed_data: Speed values in km/h
        force_data: Rimpull force values in kN
        model_type: Type of model ('rational', 'polynomial', 'power', 'exponential')
        max_force: Maximum force constraint (kN)
        
    Returns:
        Tuple of (fitted_function, coefficients, quality_metrics)
    """
    models = {
        'rational': (rational_function, [10000, -100, 1.0, -0.01]),
        'polynomial': (polynomial_function, [1000, -50, 0.5, -0.01]),
        'power': (power_function, [10000, 1, 1]),
        'exponential': (exponential_function, [1000, 0.05, 100])
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}")
    
    func, initial_guess = models[model_type]
    
    # Fit the curve
    popt, pcov = curve_fit(func, speed_data, force_data, p0=initial_guess, maxfev=10000)
    
    # Calculate quality metrics
    fitted_values = func(speed_data, *popt)
    residuals = force_data - fitted_values
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((force_data - np.mean(force_data))**2)
    r_squared = 1 - (ss_res / ss_tot)
    rmse = np.sqrt(np.mean(residuals**2))
    
    quality_metrics = {
        'r_squared': float(r_squared),
        'rmse_kn': float(rmse),
        'max_error_kn': float(np.max(np.abs(residuals))),
        'mean_error_kn': float(np.mean(np.abs(residuals)))
    }
    
    # Create fitted function with max force constraint
    if max_force is not None:
        def constrained_func(v):
            return np.minimum(func(v, *popt), max_force)
        return constrained_func, popt, quality_metrics
    else:
        return lambda v: func(v, *popt), popt, quality_metrics


def generate_rimpull_curve(
    speed_range: Tuple[float, float] = (0, 70),
    speed_step: float = 1.0,
    fitted_function: Callable = None,
    max_rimpull_kn: float = None
) -> Dict:
    """
    Generate complete rimpull curve data.
    
    Args:
        speed_range: (min, max) speed in km/h
        speed_step: Speed increment in km/h
        fitted_function: Fitted rimpull function
        max_rimpull_kn: Maximum rimpull constraint
        
    Returns:
        Dictionary with speed and force arrays
    """
    speeds = np.arange(speed_range[0], speed_range[1] + speed_step, speed_step)
    rimpull_kn = fitted_function(speeds)
    
    # Apply constraints: minimum 0 kN, maximum as specified
    rimpull_kn = np.maximum(rimpull_kn, 0.0)
    if max_rimpull_kn is not None:
        rimpull_kn = np.minimum(rimpull_kn, max_rimpull_kn)
    
    # Convert to tonnes-force (1 tf = 9.80665 kN)
    rimpull_tf = rimpull_kn / 9.80665
    
    return {
        'speed_kmh': speeds.tolist(),
        'rimpull_kn': rimpull_kn.tolist(),
        'rimpull_tf': rimpull_tf.tolist()
    }


def generate_retarding_curve(
    retarding_power_kw: float,
    efficiency: float = 0.85,
    speed_range: Tuple[float, float] = (1, 70),
    speed_step: float = 1.0,
    max_retarding_kn: float = 2000
) -> Dict:
    """
    Generate retarding curve from power rating.
    
    Formula: F = P / v (power-limited)
    where F is in kN, P is in kW, v is in m/s
    
    Args:
        retarding_power_kw: Continuous retarding power (kW)
        efficiency: System efficiency (0-1)
        speed_range: (min, max) speed in km/h
        speed_step: Speed increment in km/h
        max_retarding_kn: Maximum retarding force (low speed limit)
        
    Returns:
        Dictionary with speed and force arrays
    """
    speeds_kmh = np.arange(speed_range[0], speed_range[1] + speed_step, speed_step)
    speeds_ms = speeds_kmh / 3.6
    
    effective_power = retarding_power_kw * efficiency
    
    # F = P/v, with max limit at low speeds
    retarding_kn = np.minimum(
        effective_power / speeds_ms,
        max_retarding_kn
    )
    
    # Convert to tonnes-force
    retarding_tf = retarding_kn / 9.80665
    
    return {
        'speed_kmh': speeds_kmh.tolist(),
        'retarding_kn': retarding_kn.tolist(),
        'retarding_tf': retarding_tf.tolist()
    }


def compare_models(
    speed_data: np.ndarray,
    force_data: np.ndarray
) -> Dict[str, Dict]:
    """
    Compare multiple curve fitting models and select the best.
    
    Args:
        speed_data: Speed values in km/h
        force_data: Rimpull force values in kN
        
    Returns:
        Dictionary with results for each model type
    """
    results = {}
    
    for model_type in ['rational', 'polynomial', 'power', 'exponential']:
        try:
            func, coeffs, metrics = fit_curve(speed_data, force_data, model_type)
            results[model_type] = {
                'coefficients': coeffs.tolist(),
                'metrics': metrics
            }
        except Exception as e:
            results[model_type] = {'error': str(e)}
    
    return results


def extract_gradeability_data(
    grades_empty: List[float],
    rimpull_empty: List[float],
    speed_empty: List[float],
    grades_loaded: List[float],
    rimpull_loaded: List[float],
    speed_loaded: List[float],
    empty_weight_kg: float,
    loaded_weight_kg: float,
    unit: str = 'kN'
) -> Dict:
    """
    Structure gradeability data from spec sheet extractions.
    
    Args:
        grades_empty: Grade percentages for empty truck
        rimpull_empty: Rimpull values for empty truck
        speed_empty: Speed values for empty truck
        grades_loaded: Grade percentages for loaded truck
        rimpull_loaded: Rimpull values for loaded truck
        speed_loaded: Speed values for loaded truck
        empty_weight_kg: Empty truck weight
        loaded_weight_kg: Loaded truck weight
        unit: Unit of rimpull values ('kN' or 'tf')
        
    Returns:
        Structured gradeability data dictionary
    """
    # Convert to kN if needed
    if unit == 'tf':
        rimpull_empty_kn = [r * 9.80665 for r in rimpull_empty]
        rimpull_loaded_kn = [r * 9.80665 for r in rimpull_loaded]
        rimpull_empty_tf = rimpull_empty
        rimpull_loaded_tf = rimpull_loaded
    else:  # kN
        rimpull_empty_kn = rimpull_empty
        rimpull_loaded_kn = rimpull_loaded
        rimpull_empty_tf = [r / 9.80665 for r in rimpull_empty]
        rimpull_loaded_tf = [r / 9.80665 for r in rimpull_loaded]
    
    # Sort data by speed (ascending) for proper curve fitting
    # Empty truck
    empty_sorted = sorted(zip(speed_empty, grades_empty, rimpull_empty_kn, rimpull_empty_tf))
    speed_empty_sorted = [x[0] for x in empty_sorted]
    grades_empty_sorted = [x[1] for x in empty_sorted]
    rimpull_empty_kn_sorted = [x[2] for x in empty_sorted]
    rimpull_empty_tf_sorted = [x[3] for x in empty_sorted]
    
    # Loaded truck
    loaded_sorted = sorted(zip(speed_loaded, grades_loaded, rimpull_loaded_kn, rimpull_loaded_tf))
    speed_loaded_sorted = [x[0] for x in loaded_sorted]
    grades_loaded_sorted = [x[1] for x in loaded_sorted]
    rimpull_loaded_kn_sorted = [x[2] for x in loaded_sorted]
    rimpull_loaded_tf_sorted = [x[3] for x in loaded_sorted]
    
    return {
        'empty': {
            'weight_kg': empty_weight_kg,
            'grade_percent': grades_empty_sorted,
            'rimpull_kn': rimpull_empty_kn_sorted,
            'rimpull_tf': rimpull_empty_tf_sorted,
            'speed_kmh': speed_empty_sorted
        },
        'loaded': {
            'weight_kg': loaded_weight_kg,
            'grade_percent': grades_loaded_sorted,
            'rimpull_kn': rimpull_loaded_kn_sorted,
            'rimpull_tf': rimpull_loaded_tf_sorted,
            'speed_kmh': speed_loaded_sorted
        }
    }


def exponential_decay_gradeability(grade: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Exponential decay model for gradeability: speed = a * exp(-b * grade) + c
    
    This model describes how truck speed decreases with increasing grade.
    Selected based on Phase 1 analysis (100% success rate, R²=0.9804).
    
    Args:
        grade: Grade percentage
        a: Amplitude coefficient (km/h)
        b: Decay rate (1/%)
        c: Offset/minimum speed (km/h)
        
    Returns:
        Speed array (km/h)
    """
    return a * np.exp(-b * grade) + c


def fit_gradeability_curve_exponential(
    grades: np.ndarray,
    speeds: np.ndarray
) -> Tuple[np.ndarray, Dict]:
    """
    Fit exponential decay curve to gradeability data.
    
    Model: speed = a * exp(-b * grade) + c
    
    Special handling: If minimum speed is 0, force c=0 to allow curve to reach zero.
    
    Args:
        grades: Grade percentages (%)
        speeds: Speeds at each grade (km/h)
        
    Returns:
        Tuple of (coefficients, quality_metrics)
        - coefficients: [a, b, c]
        - quality_metrics: dict with r_squared, rmse_kmh, max_error_kmh, data_points
    """
    # Initial guess: max speed, moderate decay, min speed
    max_speed = np.max(speeds)
    min_speed = np.min(speeds)
    
    # Special case: if truck comes to complete stop (0 km/h), force c=0
    if min_speed == 0:
        # Use modified model: speed = a * exp(-b * grade)
        # This allows the curve to reach 0 at high grades
        def exponential_zero(grade, a, b):
            return a * np.exp(-b * grade)
        
        initial_guess = [max_speed, 0.05]
        
        try:
            popt, pcov = curve_fit(
                exponential_zero,
                grades,
                speeds,
                p0=initial_guess,
                maxfev=10000,
                bounds=([0, 0], [np.inf, np.inf])
            )
        except Exception as e:
            raise ValueError(f"Failed to fit gradeability curve: {e}")
        
        # Add c=0 to coefficients for consistency
        popt = np.array([popt[0], popt[1], 0.0])
        fitted_speeds = exponential_decay_gradeability(grades, *popt)
    else:
        # Normal case: use full 3-parameter model
        initial_guess = [max_speed - min_speed, 0.05, min_speed]
        
        try:
            popt, pcov = curve_fit(
                exponential_decay_gradeability,
                grades,
                speeds,
                p0=initial_guess,
                maxfev=10000,
                bounds=([0, 0, 0], [np.inf, np.inf, max_speed])  # Ensure positive coefficients
            )
        except Exception as e:
            raise ValueError(f"Failed to fit gradeability curve: {e}")
        
        fitted_speeds = exponential_decay_gradeability(grades, *popt)
    
    # Calculate quality metrics
    residuals = speeds - fitted_speeds
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((speeds - np.mean(speeds))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    rmse = np.sqrt(np.mean(residuals**2))
    max_error = np.max(np.abs(residuals))
    
    quality_metrics = {
        'r_squared': float(r_squared),
        'rmse_kmh': float(rmse),
        'max_error_kmh': float(max_error),
        'data_points': int(len(grades))
    }
    
    return popt, quality_metrics


def generate_gradeability_curves(
    gradeability_input: Dict,
    grade_step: float = 0.5
) -> Dict:
    """
    Generate complete gradeability curves for empty and loaded conditions.
    
    Fits exponential decay curves and generates smooth curves at specified intervals.
    
    Args:
        gradeability_input: Dict with 'empty' and 'loaded' conditions
        grade_step: Grade interval for generated curves (%)
        
    Returns:
        Dictionary with fitted gradeability curves and metadata
    """
    result = {
        'model_type': 'exponential_decay',
        'formula': 'speed = a * exp(-b * grade) + c',
        'description': 'Speed as a function of grade percentage for empty and loaded conditions'
    }
    
    for condition in ['empty', 'loaded']:
        if condition not in gradeability_input:
            continue
        
        data = gradeability_input[condition]
        grades = np.array(data['grade_percent'])
        speeds = np.array(data['speed_kmh'])
        rimpull = np.array(data.get('rimpull', data.get('rimpull_kn', [])))
        
        # Fit the curve
        coefficients, quality = fit_gradeability_curve_exponential(grades, speeds)
        a, b, c = coefficients
        
        # Generate complete curve from MIN grade to MAX grade (not extrapolating to 0%)
        # This prevents unrealistic speed predictions outside the measured range
        min_grade = float(np.min(grades))
        max_grade = float(np.max(grades))
        grade_range = np.arange(min_grade, max_grade + grade_step, grade_step)
        fitted_speeds = exponential_decay_gradeability(grade_range, a, b, c)
        
        # Ensure physical constraints
        fitted_speeds = np.maximum(fitted_speeds, 0.0)  # No negative speeds
        
        # Cap at maximum observed speed to prevent unrealistic extrapolation
        max_speed = float(np.max(speeds))
        fitted_speeds = np.minimum(fitted_speeds, max_speed)
        
        # Special handling: if source data has 0 km/h at max grade, force fitted curve to 0
        min_source_speed = float(np.min(speeds))
        if min_source_speed == 0.0:
            # Find if the 0 is at max grade
            zero_indices = np.where(speeds == 0.0)[0]
            if len(zero_indices) > 0:
                # Force the fitted curve to reach exactly 0 at max grade
                # by scaling down speeds proportionally near the end
                fitted_speeds[-1] = 0.0
        
        result[condition] = {
            'description': f'{condition.capitalize()} truck speed-grade relationship',
            'coefficients': {
                'a': float(a),
                'b': float(b),
                'c': float(c)
            },
            'fitting_quality': quality,
            'fitted_curve': {
                'grade_percent': grade_range.tolist(),
                'speed_kmh': fitted_speeds.tolist()
            },
            'source_data': {
                'grade_percent': grades.tolist(),
                'speed_kmh': speeds.tolist(),
                'rimpull_kn': rimpull.tolist() if len(rimpull) > 0 else []
            }
        }
    
    return result


# ============================================================================
# GRADEABILITY LOOKUP TABLE GENERATION
# ============================================================================

def lookup_retarding_force(speed_kmh: float, retarding_data: Dict) -> float:
    """
    Look up retarding force at a given speed using linear interpolation.
    
    Args:
        speed_kmh: Speed in km/h
        retarding_data: Dictionary with 'speed_kmh' and 'retarding_kn' arrays
        
    Returns:
        Retarding force in kN
    """
    speeds = np.array(retarding_data['speed_kmh'])
    forces = np.array(retarding_data['retarding_kn'])
    
    # Handle edge cases
    if speed_kmh <= speeds[0]:
        return float(forces[0])
    if speed_kmh >= speeds[-1]:
        return float(forces[-1])
    
    # Linear interpolation
    return float(np.interp(speed_kmh, speeds, forces))


def calculate_descent_speed(
    grade_pct: float,
    truck_mass_kg: float,
    max_speed_kmh: float,
    retarding_data: Dict,
    rolling_resistance: float = 0.02
) -> Tuple[float, str]:
    """
    Calculate maximum safe descent speed based on retarding capacity.
    
    Finds equilibrium speed where retarding force = net downhill force.
    
    Args:
        grade_pct: Grade percentage (negative value for descent)
        truck_mass_kg: Truck mass in kg
        max_speed_kmh: Maximum truck speed in km/h
        retarding_data: Dictionary with retarding curve data
        rolling_resistance: Rolling resistance coefficient (default 0.02)
        
    Returns:
        Tuple of (speed_kmh, limiting_factor)
    """
    # Convert grade to positive decimal
    grade_decimal = abs(grade_pct) / 100.0
    
    # Calculate forces (in kN)
    gravity = 9.81  # m/s²
    
    # Grade resistance (downhill force from gravity)
    grade_resistance_kn = (truck_mass_kg * gravity * grade_decimal) / 1000.0
    
    # Rolling resistance (opposes motion, reduces net downhill force)
    rolling_resistance_kn = (truck_mass_kg * gravity * rolling_resistance) / 1000.0
    
    # Net downhill force (what retarding must overcome)
    net_downhill_force_kn = grade_resistance_kn - rolling_resistance_kn
    
    # If net force is negative or zero, truck can coast uphill or stay stationary
    if net_downhill_force_kn <= 0:
        return max_speed_kmh, "max_speed"
    
    # Check if retarding at max speed is sufficient
    retarding_at_max = lookup_retarding_force(max_speed_kmh, retarding_data)
    
    if retarding_at_max >= net_downhill_force_kn:
        # Retarding is sufficient at max speed
        return max_speed_kmh, "max_speed"
    
    # Need to find equilibrium speed using binary search
    equilibrium_speed = solve_equilibrium_speed(
        net_downhill_force_kn,
        retarding_data,
        max_speed_kmh
    )
    
    return equilibrium_speed, "retarding"


def solve_equilibrium_speed(
    target_force_kn: float,
    retarding_data: Dict,
    max_speed_kmh: float,
    tolerance: float = 0.5
) -> float:
    """
    Binary search to find speed where retarding force equals target force.
    
    Args:
        target_force_kn: Net downhill force to match (kN)
        retarding_data: Dictionary with retarding curve data
        max_speed_kmh: Maximum search speed (km/h)
        tolerance: Speed tolerance (km/h)
        
    Returns:
        Equilibrium speed in km/h
    """
    min_speed = 1.0  # Minimum speed to consider
    speed_low = min_speed
    speed_high = max_speed_kmh
    
    # Binary search
    while (speed_high - speed_low) > tolerance:
        speed_mid = (speed_low + speed_high) / 2.0
        retarding_force = lookup_retarding_force(speed_mid, retarding_data)
        
        if retarding_force > target_force_kn:
            # Retarding too strong at this speed - can go faster
            speed_low = speed_mid
        else:
            # Retarding too weak at this speed - must go slower
            speed_high = speed_mid
    
    return (speed_low + speed_high) / 2.0


def interpolate_climb_speed(
    grade_pct: float,
    gradeability_curves: Dict,
    condition: str,
    max_speed_kmh: float
) -> Tuple[float, str]:
    """
    Interpolate speed from fitted gradeability data for climbing.
    
    Args:
        grade_pct: Grade percentage (positive value for climb)
        gradeability_curves: Dictionary with fitted gradeability curves
        condition: "empty" or "loaded"
        max_speed_kmh: Maximum truck speed in km/h
        
    Returns:
        Tuple of (speed_kmh, limiting_factor)
    """
    if condition not in gradeability_curves:
        return max_speed_kmh, "max_speed"
    
    curve_data = gradeability_curves[condition].get('fitted_curve', {})
    grades = np.array(curve_data.get('grade_percent', []))
    speeds = np.array(curve_data.get('speed_kmh', []))
    
    if len(grades) == 0 or len(speeds) == 0:
        return max_speed_kmh, "max_speed"
    
    # Check if grade is within data range
    min_grade = grades[0]
    max_grade = grades[-1]
    
    if grade_pct < min_grade:
        # Grade below data range - use max speed
        return max_speed_kmh, "max_speed"
    
    if grade_pct > max_grade:
        # Grade above data range - use minimum speed (conservative)
        return max(float(speeds[-1]), 0.0), "gradeability"
    
    # Linear interpolation
    interpolated_speed = float(np.interp(grade_pct, grades, speeds))
    
    # Ensure speed doesn't exceed max
    return min(interpolated_speed, max_speed_kmh), "gradeability"


def generate_grade_speed_lookup(
    specifications: Dict,
    gradeability_curves: Dict,
    retarding_data: Dict,
    condition: str,
    min_grade: float = -15.0,
    max_grade: float = 20.0,
    grade_step: float = 1.0,
    rolling_resistance: float = 0.02
) -> Dict:
    """
    Generate complete grade-speed lookup table for simulation.
    
    Covers descent (negative grades), flat (0%), and climb (positive grades).
    
    Args:
        specifications: Truck specifications dictionary
        gradeability_curves: Fitted gradeability curves dictionary
        retarding_data: Retarding curve data dictionary
        condition: "empty" or "loaded"
        min_grade: Minimum grade (steepest descent), default -15%
        max_grade: Maximum grade (steepest climb), default 20%
        grade_step: Grade increment, default 1%
        rolling_resistance: Rolling resistance coefficient, default 0.02
        
    Returns:
        Dictionary with lookup table data and metadata
    """
    # Get truck parameters
    weights = specifications.get('weights', {})
    drivetrain = specifications.get('drivetrain', {})
    
    if condition == 'loaded':
        truck_mass_kg = weights.get('loaded_kg', 0)
        max_speed_kmh = drivetrain.get('max_speed_kmh_loaded', 
                                       drivetrain.get('max_speed_kmh', 60))
    else:  # empty
        truck_mass_kg = weights.get('empty_kg', 0)
        max_speed_kmh = drivetrain.get('max_speed_kmh_empty',
                                       drivetrain.get('max_speed_kmh', 64))
    
    # Use rolling resistance from specs if available
    rr = drivetrain.get('rolling_resistance', rolling_resistance)
    
    # Generate lookup table
    lookup_data = []
    grades = np.arange(min_grade, max_grade + grade_step, grade_step)
    
    for grade in grades:
        grade = float(grade)
        
        if grade < 0:
            # DESCENT: Calculate based on retarding capacity
            speed, limiting_factor = calculate_descent_speed(
                grade_pct=grade,
                truck_mass_kg=truck_mass_kg,
                max_speed_kmh=max_speed_kmh,
                retarding_data=retarding_data,
                rolling_resistance=rr
            )
        elif grade == 0:
            # FLAT: Maximum speed
            speed = max_speed_kmh
            limiting_factor = "max_speed"
        else:
            # CLIMB: Interpolate from gradeability data
            speed, limiting_factor = interpolate_climb_speed(
                grade_pct=grade,
                gradeability_curves=gradeability_curves,
                condition=condition,
                max_speed_kmh=max_speed_kmh
            )
        
        # Round to 0.5 km/h precision
        speed = round(speed * 2) / 2.0
        
        # Ensure non-negative
        speed = max(speed, 0.0)
        
        lookup_data.append({
            'grade_pct': grade,
            'speed_kmh': speed,
            'limiting_factor': limiting_factor
        })
    
    return {
        'description': f'Maximum sustainable speed at each grade for {condition} truck',
        'condition': condition,
        'truck_mass_kg': truck_mass_kg,
        'max_speed_kmh': max_speed_kmh,
        'rolling_resistance': rr,
        'grade_range': {
            'min': min_grade,
            'max': max_grade,
            'step': grade_step
        },
        'data': lookup_data
    }


if __name__ == "__main__":
    # Example usage
    print("Curve Fitting Utilities")
    print("Import this module to use curve fitting functions")
