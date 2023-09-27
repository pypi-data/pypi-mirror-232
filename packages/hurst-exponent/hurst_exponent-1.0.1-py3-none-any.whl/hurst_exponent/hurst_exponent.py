import numpy as np
import pandas as pd
from powerlaw_function import Fit
from typing import Tuple, Any


from util.utils import std_of_sums, structure_function, interpret_hurst, bootstrap


def _preprocess_series(series: np.array) -> np.array:
    """Preprocesses the given series: handles non-array input, zeroes, NaNs, Infs, and removes mean."""
    if not isinstance(series, (np.ndarray, pd.Series)):
        series = np.array(series, dtype=float)

    replace_zero = 1e-10
    series[series == 0] = replace_zero

    if np.any(np.isnan(series)) or np.any(np.isinf(series)):
        raise ValueError("Time series contains NaN or Inf values")

    # Subtract mean to center data around zero
    mean = np.mean(series)
    series = series - mean

    return series


def _check_fitting_method_validity(fitting_method: str):
    """Validates if the given fitting_method is supported."""
    valid_methods = ["MLE", "Least_squares"]
    if fitting_method not in valid_methods:
        raise ValueError(f"Unknown method: {fitting_method}. Expected one of {valid_methods}.")


def _fit_data(fitting_method: str, xy_values: pd.DataFrame) -> Fit:
    """Fits the data using the specified method and returns the fitting results."""
    if fitting_method == "MLE":
        return Fit(xy_values, xmin_distance="BIC")
    return Fit(xy_values, nonlinear_fit_method=fitting_method, xmin_distance="BIC")


def standard_hurst(
    series: np.array, fitting_method: str = "MLE", min_lag: int = 1, max_lag: int = 100
) -> Tuple[float, Fit]:
    """
    Compute the Hurst exponent using standard the standard deviation of sums:

        Patzelt, Felix, and Jean-Philippe Bouchaud. "Universal scaling and
        nonlinearity of aggregate price impact in financial markets."
        Physical Review E 97, no. 1 (2018): 012304.

    Args:
        series (np.array): Time series data.
        fitting_method (str): Method for fitting. Either "MLE" or "Least_squares".
        min_lag (int): Minimum lag for analysis.
        max_lag (int): Maximum lag for analysis. Fitting is process highly sensitive to hyperparameter

    Returns:
        H (float): Hurst exponent value.
        fit_results (Fit): Object containing fitting results.
    """

    if len(series) < 100:
        raise ValueError("Length of series cannot be less than 100")

    # Check if the time series is stationary
    mean = np.mean(series)
    if not np.isclose(mean, 0.0):
        series = np.diff(series)

    series = _preprocess_series(series)
    _check_fitting_method_validity(fitting_method)

    max_lag = min(max_lag, len(series))
    num_lags = int(np.sqrt(len(series)))
    lag_sizes = np.linspace(min_lag, max_lag, num=num_lags, dtype=int)

    y_values, valid_lags = zip(
        *[(std_of_sums(series, lag), lag) for lag in lag_sizes if np.isfinite(std_of_sums(series, lag))]
    )

    if not valid_lags or not y_values:
        return np.nan, np.nan, [[], []]

    xy_df = pd.DataFrame({"x_values": valid_lags, "y_values": y_values})
    fit_results = _fit_data(fitting_method, xy_df)
    H = fit_results.powerlaw.params.alpha

    return H, fit_results


def generalized_hurst(
    series: np.array,
    moment: int = 1,
    fitting_method: str = "MLE",
    min_lag: int = 1,
    max_lag: int = 100,
) -> Tuple[float, Fit]:
    """
    Calculates the generalized Hurst exponent using structure function method:

        Barunik, Jozef, and Ladislav Kristoufek. "On Hurst exponent estimation under
        heavy-tailed distributions." Physica A: statistical mechanics and its
        applications 389.18 (2010): 3844-3855.

    Args:
        series (np.array): Time series data.
        moment (int): Order of the moment for the structure function.
        fitting_method (str): Method for fitting. Either "MLE" or "Least_squares".
        min_lag (int): Minimum lag for analysis.
        max_lag (int): Maximum lag for analysis. Fitting process is highly sensitive to hyperparameter

    Returns:
        H (float): Hurst exponent value.
        fit_results (Fit): Object containing fitting results.
    """

    if len(series) < 100:
        raise ValueError("Length of series cannot be less than 100")

    series = _preprocess_series(series)
    _check_fitting_method_validity(fitting_method)

    min_lag = min_lag
    max_lag = min(max_lag, len(series))
    num_lags = int(np.sqrt(len(series)))
    lag_sizes = np.linspace(min_lag, max_lag, num=num_lags, dtype=int)

    S_q_tau_values = [
        structure_function(series, moment, lag)
        for lag in lag_sizes
        if np.isfinite(structure_function(series, moment, lag))
    ]
    valid_lags = [lag for lag in lag_sizes if np.isfinite(structure_function(series, moment, lag))]

    if not valid_lags or not S_q_tau_values:
        return np.nan, np.nan, [[], []]

    xy_df = pd.DataFrame({"x_values": valid_lags, "y_values": S_q_tau_values})
    fit_results = _fit_data(fitting_method, xy_df)
    H = fit_results.powerlaw.params.alpha

    return H, fit_results


if __name__ == "__main__":
    # Fractal BM
    from stochastic.processes.continuous import FractionalBrownianMotion
    from matplotlib import pyplot as plt

    fbm = FractionalBrownianMotion(hurst=0.3, t=1)
    fbm_series = fbm.sample(10000)
    lags = fbm.times(10000)
    plt.plot(lags, fbm_series)
    plt.show()

    # Estimate Hurst Exponent using both methods
    hurst_std, fit_std = standard_hurst(fbm_series)
    hurst_gen, fit_gen = generalized_hurst(fbm_series)

    # Print fitting results
    fit_std.powerlaw.print_fitted_results()
    fit_gen.powerlaw.print_fitted_results()

    # Interpret and display the results
    fit_std.powerlaw.plot_fit()
    fit_gen.powerlaw.plot_fit()
    print(f"Standard Hurst Exponent: {hurst_std} ({interpret_hurst(hurst_std)})")
    print(f"Generalized Hurst Exponent: {hurst_gen} ({interpret_hurst(hurst_gen)})")

    # Bootstrap
    results = bootstrap(generalized_hurst, reps=1000, seed=50)

    lower_ci = np.percentile(results, 5)
    upper_ci = np.percentile(results, 95)

    print(pd.DataFrame(results, columns=["H"]).describe())
    print()
    print("95% Confidence Interval:", (lower_ci, upper_ci))
