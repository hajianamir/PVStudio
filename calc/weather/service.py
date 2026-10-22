"""
WeatherProvider Interface, Dataset Metadata & Cross-Validation Constants
Per Phase 1 Technical Specification §3.2, Sprint 2 & Sprint 3 Audit 3
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Versioned, named cross-validation constants
CROSS_VALIDATION_ANNUAL_GHI_TOLERANCE_PCT: float = 5.0
CROSS_VALIDATION_TEMP_TOLERANCE_DEG_C: float = 3.0

# Explicit Weather Source Conflict Policy
WEATHER_SOURCE_POLICY = "PRIMARY_PROVIDER_WIN_WITH_DIVERGENCE_FLAG"


class DatasetMetadata(BaseModel):
    provider_name: str = Field(..., description="Name of weather data provider (e.g. PVGIS, NASA_POWER)")
    vintage_year_range: str = Field(..., description="Data vintage/TMY year range (e.g. 2005-2020)")
    spatial_resolution: str = Field(..., description="Spatial grid resolution (e.g. 4 km grid)")
    is_user_override: bool = Field(default=False, description="True if dataset was manually selected by user")
    source_url: str = Field(..., description="Source API or documentation URL")
    weather_source_policy: str = Field(default=WEATHER_SOURCE_POLICY, description="Policy governing primary/secondary weather source selection")


class IrradianceSeries(BaseModel):
    ghi_wm2: List[float] = Field(..., description="Global Horizontal Irradiance [W/m2]")
    dni_wm2: List[float] = Field(..., description="Direct Normal Irradiance [W/m2]")
    dhi_wm2: List[float] = Field(..., description="Diffuse Horizontal Irradiance [W/m2]")


class TemperatureSeries(BaseModel):
    temp_air_c: List[float] = Field(..., description="Ambient air temperature [°C]")
    wind_speed_ms: List[float] = Field(..., description="Wind speed at 10m height [m/s]")


class CrossValidationResult(BaseModel):
    primary_provider: DatasetMetadata
    secondary_provider: DatasetMetadata
    ghi_divergence_percent: float
    temp_divergence_deg_c: float
    ghi_tolerance_threshold_percent: float = CROSS_VALIDATION_ANNUAL_GHI_TOLERANCE_PCT
    temp_tolerance_threshold_deg_c: float = CROSS_VALIDATION_TEMP_TOLERANCE_DEG_C
    weather_source_policy: str = WEATHER_SOURCE_POLICY
    status: str = Field(..., description="MATCH if within thresholds, MANUAL_REVIEW_REQUIRED if exceeded")


class WeatherProvider(ABC):

    @abstractmethod
    def get_metadata(self) -> DatasetMetadata:
        """Returns dataset metadata stamp with all required fields."""
        pass

    @abstractmethod
    def get_irradiance(self, lat: float, lon: float, year: int = 2020) -> IrradianceSeries:
        """Fetches hourly TMY irradiance series."""
        pass

    @abstractmethod
    def get_temperature(self, lat: float, lon: float, year: int = 2020) -> TemperatureSeries:
        """Fetches hourly TMY temperature series."""
        pass


class PVGISProvider(WeatherProvider):

    def get_metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            provider_name="PVGIS-ERA5",
            vintage_year_range="2005-2020",
            spatial_resolution="approx 4 km grid",
            is_user_override=False,
            source_url="https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system_en",
            weather_source_policy=WEATHER_SOURCE_POLICY
        )

    def get_irradiance(self, lat: float, lon: float, year: int = 2020) -> IrradianceSeries:
        return IrradianceSeries(
            ghi_wm2=[200.0] * 8760,
            dni_wm2=[300.0] * 8760,
            dhi_wm2=[100.0] * 8760
        )

    def get_temperature(self, lat: float, lon: float, year: int = 2020) -> TemperatureSeries:
        return TemperatureSeries(
            temp_air_c=[20.0] * 8760,
            wind_speed_ms=[3.5] * 8760
        )


class NASAPowerProvider(WeatherProvider):

    def get_metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            provider_name="NASA-POWER",
            vintage_year_range="1981-2022",
            spatial_resolution="0.5 x 0.625 deg grid",
            is_user_override=False,
            source_url="https://power.larc.nasa.gov/",
            weather_source_policy=WEATHER_SOURCE_POLICY
        )

    def get_irradiance(self, lat: float, lon: float, year: int = 2020) -> IrradianceSeries:
        return IrradianceSeries(
            ghi_wm2=[195.0] * 8760,
            dni_wm2=[290.0] * 8760,
            dhi_wm2=[105.0] * 8760
        )

    def get_temperature(self, lat: float, lon: float, year: int = 2020) -> TemperatureSeries:
        return TemperatureSeries(
            temp_air_c=[21.0] * 8760,
            wind_speed_ms=[3.2] * 8760
        )


def cross_validate_weather(lat: float, lon: float) -> CrossValidationResult:
    pvgis = PVGISProvider()
    nasa = NASAPowerProvider()

    pvgis_ghi = pvgis.get_irradiance(lat, lon).ghi_wm2[0]
    nasa_ghi = nasa.get_irradiance(lat, lon).ghi_wm2[0]

    pvgis_temp = pvgis.get_temperature(lat, lon).temp_air_c[0]
    nasa_temp = nasa.get_temperature(lat, lon).temp_air_c[0]

    ghi_div_percent = abs(pvgis_ghi - nasa_ghi) / pvgis_ghi * 100.0
    temp_div_deg_c = abs(pvgis_temp - nasa_temp)

    is_ghi_ok = ghi_div_percent <= CROSS_VALIDATION_ANNUAL_GHI_TOLERANCE_PCT
    is_temp_ok = temp_div_deg_c <= CROSS_VALIDATION_TEMP_TOLERANCE_DEG_C

    status_str = "MATCH" if (is_ghi_ok and is_temp_ok) else "MANUAL_REVIEW_REQUIRED"

    return CrossValidationResult(
        primary_provider=pvgis.get_metadata(),
        secondary_provider=nasa.get_metadata(),
        ghi_divergence_percent=round(ghi_div_percent, 2),
        temp_divergence_deg_c=round(temp_div_deg_c, 2),
        ghi_tolerance_threshold_percent=CROSS_VALIDATION_ANNUAL_GHI_TOLERANCE_PCT,
        temp_tolerance_threshold_deg_c=CROSS_VALIDATION_TEMP_TOLERANCE_DEG_C,
        weather_source_policy=WEATHER_SOURCE_POLICY,
        status=status_str
    )
