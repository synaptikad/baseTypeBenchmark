"""
Environment Model for building simulation.

Generates realistic environmental conditions:
- Outdoor temperature (seasonal + diurnal patterns)
- Outdoor humidity
- Solar radiation (simplified)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EnvironmentContext:
    """Environmental conditions at a given moment."""
    outdoor_temp: float  # °C
    outdoor_humidity: float  # %RH
    solar_intensity: float  # 0-1 normalized
    is_daytime: bool
    season_factor: float  # -1 (winter) to 1 (summer)


@dataclass
class EnvironmentModel:
    """
    Generates realistic outdoor environmental conditions.

    Based on simplified sinusoidal models:
    - Annual temperature cycle (seasonal)
    - Daily temperature cycle (diurnal)
    - Random weather variations
    """

    # Location parameters (default: temperate climate like Paris)
    latitude: float = 48.8  # degrees
    annual_mean_temp: float = 12.0  # °C
    annual_amplitude: float = 10.0  # °C (difference summer-winter)
    daily_amplitude: float = 8.0  # °C (difference day-night)
    humidity_mean: float = 65.0  # %RH
    humidity_amplitude: float = 20.0  # %RH

    # Weather noise
    weather_sigma: float = 3.0  # °C random variation
    weather_persistence: float = 0.95  # How much yesterday's weather affects today

    # Internal state
    _weather_offset: float = field(default=0.0, repr=False)
    rng: random.Random = field(default_factory=random.Random)

    def get_environment(self, timestamp: datetime) -> EnvironmentContext:
        """
        Get environmental conditions for a specific timestamp.

        Args:
            timestamp: The moment to evaluate

        Returns:
            EnvironmentContext with current conditions
        """
        # Day of year (0-365)
        day_of_year = timestamp.timetuple().tm_yday
        hour = timestamp.hour + timestamp.minute / 60.0

        # Season factor (-1 = winter solstice, +1 = summer solstice)
        # Shifted so peak is around July 21 (day ~200)
        season_factor = -math.cos(2 * math.pi * (day_of_year - 10) / 365)

        # Seasonal temperature component
        seasonal_temp = self.annual_mean_temp + self.annual_amplitude * season_factor

        # Diurnal temperature component
        # Peak around 15:00, minimum around 05:00
        diurnal_factor = -math.cos(2 * math.pi * (hour - 3) / 24)
        diurnal_temp = self.daily_amplitude * diurnal_factor * (0.5 + 0.5 * max(0, season_factor))

        # Update weather noise (random walk with mean reversion)
        self._weather_offset = (
            self.weather_persistence * self._weather_offset +
            math.sqrt(1 - self.weather_persistence ** 2) * self.weather_sigma * self.rng.gauss(0, 1)
        )

        # Final outdoor temperature
        outdoor_temp = seasonal_temp + diurnal_temp + self._weather_offset

        # Humidity (inverse relationship with temperature during day)
        humidity_diurnal = -diurnal_factor * 15  # Higher humidity at night
        outdoor_humidity = max(20, min(100,
            self.humidity_mean + humidity_diurnal + self.rng.gauss(0, 5)
        ))

        # Solar intensity (simplified)
        # Based on sun altitude approximation
        solar_noon = 12.5  # Solar noon around 12:30
        hour_angle = abs(hour - solar_noon)

        if hour_angle > 7:  # Before 5:30 or after 19:30
            solar_intensity = 0.0
            is_daytime = False
        else:
            # Bell curve peaking at solar noon
            solar_intensity = max(0, math.cos(math.pi * hour_angle / 14))
            # Seasonal scaling (more sun in summer)
            solar_intensity *= (0.5 + 0.5 * max(0, season_factor))
            is_daytime = solar_intensity > 0.05

        return EnvironmentContext(
            outdoor_temp=outdoor_temp,
            outdoor_humidity=outdoor_humidity,
            solar_intensity=solar_intensity,
            is_daytime=is_daytime,
            season_factor=season_factor,
        )

    def get_design_temps(self) -> tuple[float, float]:
        """
        Get design temperatures for heating/cooling.

        Returns:
            Tuple of (heating_design_temp, cooling_design_temp)
        """
        heating_design = self.annual_mean_temp - self.annual_amplitude - 5
        cooling_design = self.annual_mean_temp + self.annual_amplitude + 5
        return heating_design, cooling_design

    def reset_weather(self):
        """Reset weather noise to neutral."""
        self._weather_offset = 0.0


@dataclass
class ClimatePreset:
    """Preset climate configurations for different regions."""

    @staticmethod
    def temperate() -> EnvironmentModel:
        """Temperate climate (e.g., Paris, London)."""
        return EnvironmentModel(
            latitude=48.8,
            annual_mean_temp=12.0,
            annual_amplitude=10.0,
            daily_amplitude=8.0,
            humidity_mean=70.0,
        )

    @staticmethod
    def continental() -> EnvironmentModel:
        """Continental climate (e.g., Chicago, Berlin)."""
        return EnvironmentModel(
            latitude=52.0,
            annual_mean_temp=10.0,
            annual_amplitude=15.0,
            daily_amplitude=10.0,
            humidity_mean=65.0,
        )

    @staticmethod
    def mediterranean() -> EnvironmentModel:
        """Mediterranean climate (e.g., Nice, Barcelona)."""
        return EnvironmentModel(
            latitude=43.0,
            annual_mean_temp=16.0,
            annual_amplitude=8.0,
            daily_amplitude=10.0,
            humidity_mean=60.0,
        )

    @staticmethod
    def tropical() -> EnvironmentModel:
        """Tropical climate (e.g., Singapore, Miami)."""
        return EnvironmentModel(
            latitude=25.0,
            annual_mean_temp=27.0,
            annual_amplitude=3.0,
            daily_amplitude=6.0,
            humidity_mean=80.0,
        )
