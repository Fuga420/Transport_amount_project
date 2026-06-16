# src/features.py

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pandas as pd


Period = Tuple[str, Optional[str]]
PeriodConfig = Dict[str, Period]


def add_period_dummies(df: pd.DataFrame, periods: PeriodConfig) -> pd.DataFrame:
    """
    辞書定義に基づいて期間ダミー変数をまとめて追加する。

    Parameters
    ----------
    df : pd.DataFrame
        DatetimeIndex を持つデータ
    periods : dict
        例:
        {
            "hike_dummy": ("2017-10-01", "2019-12-01"),
            "covid_main": ("2020-03-01", None),
        }

    Returns
    -------
    pd.DataFrame
        ダミー変数を追加したデータ
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("df.index は DatetimeIndex である必要があります。")

    df = df.copy()
    idx = df.index

    for name, (start, end) in periods.items():
        start_ts = pd.Timestamp(start)

        if end is None:
            df[name] = (idx >= start_ts).astype(int)
        else:
            end_ts = pd.Timestamp(end)
            df[name] = ((idx >= start_ts) & (idx <= end_ts)).astype(int)

    return df


def get_default_event_config() -> PeriodConfig:
    """
    本研究で用いる外部イベントダミーのデフォルト設定を返す。

    注意:
        post_stat_change は統計接続補正であり、
        需要イベントではないため、この関数には含めない。
    """
    return {
        "hike_dummy": ("2017-10-01", "2019-12-01"),
        "covid_main": ("2020-03-01", None),
        "covid_wave1": ("2020-04-01", "2020-05-01"),
        "covid_2021": ("2021-01-01", "2021-09-01"),
    }


def get_default_connection_config() -> PeriodConfig:
    """
    後続統計への接続ダミーのデフォルト設定を返す。

    post_stat_change:
        2022年8月以降を1とする。
        これは外部イベント効果ではなく、統計定義変更の補正項である。
    """
    return {
        "post_stat_change": ("2022-08-01", None),
    }


def get_default_model_config(include_connection_dummy: bool = True) -> PeriodConfig:
    """
    モデル推定に用いる外生変数設定を返す。

    Parameters
    ----------
    include_connection_dummy : bool
        True の場合、post_stat_change を含める。

    Returns
    -------
    dict
        モデル推定用の期間ダミー設定
    """
    event_config = get_default_event_config()

    if include_connection_dummy:
        connection_config = get_default_connection_config()
        return {**event_config, **connection_config}

    return event_config


def prepare_event_data(
    df: pd.DataFrame,
    config: PeriodConfig,
) -> tuple[pd.DataFrame, List[pd.Series], List[str]]:
    """
    設定辞書に基づいてダミー変数を作成し、
    モデル入力用の形式にまとめて返す。

    Returns
    -------
    df : pd.DataFrame
        ダミー変数追加後のデータ
    exog_data : list[pd.Series]
        モデルに渡す外生変数 Series のリスト
    exog_names : list[str]
        外生変数名のリスト
    """
    df = add_period_dummies(df, config)

    exog_names = list(config.keys())
    exog_data = [df[name] for name in exog_names]

    return df, exog_data, exog_names


def split_exog_names(exog_names: List[str]) -> dict:
    """
    外生変数名を、需要イベント効果と統計接続補正に分ける。

    Returns
    -------
    dict
        {
            "event_effects": [...],
            "connection_effects": [...]
        }
    """
    connection_vars = {"post_stat_change"}

    event_effects = [name for name in exog_names if name not in connection_vars]
    connection_effects = [name for name in exog_names if name in connection_vars]

    return {
        "event_effects": event_effects,
        "connection_effects": connection_effects,
    }