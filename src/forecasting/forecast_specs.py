"""Forecast evaluation specification registry."""

from __future__ import annotations

from copy import deepcopy


FORECAST_SPECS = {
    "baseline_m4": {
        "spec_name": "baseline_m4",
        "description": "Baseline evaluation around the COVID period using fixed split A.",
        "split": "fixed_a",
        "train_start": "2002-04-01",
        "train_end": "2019-12-01",
        "test_start": "2020-01-01",
        "test_end": "2021-12-01",
        "target_col": "number_parcels",
        "target_scale": "original",
        "exog_periods": {
            "hike_dummy": ("2017-10-01", "2019-12-01"),
            "covid_main": ("2020-03-01", "2023-05-01"),
            "covid_wave1": ("2020-04-01", "2020-05-01"),
            "covid_2021": ("2021-01-01", "2021-09-01"),
            "post_stat_change": ("2022-08-01", None),
        },
    },
    "post2020_m5": {
        "spec_name": "post2020_m5",
        "description": "Post-2020 connected-data evaluation using fixed split B.",
        "split": "fixed_b",
        "train_start": "2002-04-01",
        "train_end": "2023-12-01",
        "test_start": "2024-01-01",
        "test_end": "2026-02-01",
        "target_col": "number_parcels",
        "target_scale": "original",
    },
}


def get_forecast_spec(spec_name: str) -> dict:
    """Return a copy of one forecast specification."""
    if spec_name not in FORECAST_SPECS:
        available = ", ".join(sorted(FORECAST_SPECS))
        raise KeyError(f"Unknown forecast spec '{spec_name}'. Available specs: {available}")
    return deepcopy(FORECAST_SPECS[spec_name])


def list_forecast_specs() -> list[str]:
    """List available forecast specification names."""
    return sorted(FORECAST_SPECS)
