"""
Ornstein-Uhlenbeck Process for temporal correlation in timeseries.

The OU process is a mean-reverting stochastic process:
    dX = θ(μ - X)dt + σdW

Where:
    - θ (theta): Mean reversion rate (higher = faster reversion)
    - μ (mean): Long-term mean
    - σ (sigma): Volatility/noise level
    - dW: Wiener process (Brownian motion)

This creates realistic time-correlated values that fluctuate around a setpoint
with configurable inertia (thermal lag, response time, etc.)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


@dataclass
class OUProcess:
    """
    Ornstein-Uhlenbeck process for generating correlated random values.

    Typical theta values:
        - Fast response (damper position): 0.5 - 1.0
        - Medium response (air temp): 0.1 - 0.3
        - Slow response (water temp, humidity): 0.02 - 0.1
    """
    mean: float
    theta: float  # Mean reversion rate
    sigma: float  # Volatility
    current: float = field(default=None)
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self):
        if self.current is None:
            self.current = self.mean

    def step(self, dt: float) -> float:
        """
        Advance the process by dt seconds.

        Uses the exact solution for OU process:
        X(t+dt) = μ + (X(t) - μ)e^(-θdt) + σ√((1-e^(-2θdt))/(2θ)) * Z

        Where Z ~ N(0,1)

        Args:
            dt: Time step in seconds

        Returns:
            New value after time step
        """
        if dt <= 0:
            return self.current

        # Convert theta to per-second rate if needed
        # theta is already in per-second units
        decay = math.exp(-self.theta * dt)

        # Exact variance for the OU process
        if self.theta > 0:
            variance = (self.sigma ** 2) * (1 - math.exp(-2 * self.theta * dt)) / (2 * self.theta)
        else:
            # Pure random walk if theta = 0
            variance = self.sigma ** 2 * dt

        std_dev = math.sqrt(variance) if variance > 0 else 0

        # Update current value
        self.current = self.mean + (self.current - self.mean) * decay + std_dev * self.rng.gauss(0, 1)

        return self.current

    def set_mean(self, new_mean: float):
        """Update the target mean (e.g., when setpoint changes)."""
        self.mean = new_mean

    def reset(self, value: float | None = None):
        """Reset the process to a specific value or the mean."""
        self.current = value if value is not None else self.mean


@dataclass
class BoundedOUProcess(OUProcess):
    """OU process with hard bounds (for physical constraints like 0-100%)."""

    min_value: float = float('-inf')
    max_value: float = float('inf')

    def step(self, dt: float) -> float:
        """Step with bounds enforcement."""
        value = super().step(dt)
        self.current = max(self.min_value, min(self.max_value, value))
        return self.current


def calculate_theta_from_time_constant(time_constant_seconds: float) -> float:
    """
    Convert a time constant (seconds to reach ~63% of target) to theta.

    In OU process, the time constant τ = 1/θ

    Args:
        time_constant_seconds: Time to reach 63.2% of the way to the mean

    Returns:
        Theta value for OU process
    """
    if time_constant_seconds <= 0:
        return 1.0  # Fast response
    return 1.0 / time_constant_seconds


def calculate_theta_from_lag_minutes(lag_minutes: float) -> float:
    """
    Convert thermal lag in minutes to theta.

    Args:
        lag_minutes: Thermal lag in minutes (time to reach 63% of target)

    Returns:
        Theta value for OU process
    """
    return calculate_theta_from_time_constant(lag_minutes * 60)
