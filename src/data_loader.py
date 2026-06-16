# src/data_loader.py

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_numeric_series(series: pd.Series) -> pd.Series:
    """
    カンマ付き文字列などを数値型に変換する内部関数。

    例:
        "373,849" -> 373849.0
    """
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
        .astype(float)
    )


def _set_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    date または label 列を datetime index に変換する。
    """
    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    elif "label" in df.columns:
        df["label"] = pd.to_datetime(df["label"])
        df = df.set_index("label")
    else:
        raise ValueError("データには 'date' または 'label' 列が必要です。")

    df = df.sort_index()
    return df


def add_log_target(
    df: pd.DataFrame,
    target_col: str = "number_parcels",
    log_col: str = "y",
) -> pd.DataFrame:
    """
    目的変数の対数変換列を追加する。

    Parameters
    ----------
    df : pd.DataFrame
        入力データ
    target_col : str
        対数変換する列名
    log_col : str
        作成する対数変換列名

    Returns
    -------
    pd.DataFrame
        対数変換列を追加したデータ
    """
    df = df.copy()

    if target_col not in df.columns:
        raise ValueError(f"'{target_col}' 列が見つかりません。")

    df[target_col] = _to_numeric_series(df[target_col])

    if (df[target_col] <= 0).any():
        raise ValueError(f"'{target_col}' に0以下の値が含まれています。対数変換できません。")

    df[log_col] = np.log(df[target_col])
    return df


def add_post_stat_change_dummy(
    df: pd.DataFrame,
    cutoff: str = "2022-08-01",
    col_name: str = "post_stat_change",
) -> pd.DataFrame:
    """
    後続統計への接続以降を表すダミー変数を追加する。

    Parameters
    ----------
    df : pd.DataFrame
        datetime index を持つデータ
    cutoff : str
        後続統計に切り替わる年月
    col_name : str
        作成するダミー変数名

    Returns
    -------
    pd.DataFrame
        接続ダミーを追加したデータ
    """
    df = df.copy()

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("df.index は DatetimeIndex である必要があります。")

    cutoff_ts = pd.Timestamp(cutoff)
    df[col_name] = (df.index >= cutoff_ts).astype(int)
    return df


def validate_monthly_index(df: pd.DataFrame) -> None:
    """
    月次データとして、欠損月や重複月がないか簡易チェックする。
    問題がある場合は ValueError を投げる。
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("df.index は DatetimeIndex である必要があります。")

    if df.index.has_duplicates:
        duplicated = df.index[df.index.duplicated()].unique()
        raise ValueError(f"日付インデックスに重複があります: {duplicated}")

    expected = pd.date_range(start=df.index.min(), end=df.index.max(), freq="MS")
    actual = df.index.sort_values()

    missing = expected.difference(actual)
    if len(missing) > 0:
        raise ValueError(f"月次データに欠損月があります: {missing}")


def load_transport_data(file_path: str) -> pd.DataFrame:
    """
    旧系列または既存形式の輸送量データを読み込み、
    対数変換済みカラム 'y' を追加して返す。

    想定列:
        - label または date
        - number_parcels
    """
    df = pd.read_csv(file_path)
    df = _set_datetime_index(df)
    df = add_log_target(df, target_col="number_parcels", log_col="y")
    validate_monthly_index(df)
    return df


def load_connected_parcel_data(
    file_path: str,
    cutoff: str = "2022-08-01",
) -> pd.DataFrame:
    """
    旧系列と後続統計を接続した分析用データを読み込む。

    想定列:
        - date または label
        - number_parcels
        - source             任意
        - definition         任意
        - post_stat_change   任意

    post_stat_change が存在しない場合は自動作成する。
    """
    df = pd.read_csv(file_path)
    df = _set_datetime_index(df)
    df = add_log_target(df, target_col="number_parcels", log_col="y")

    if "post_stat_change" not in df.columns:
        df = add_post_stat_change_dummy(df, cutoff=cutoff, col_name="post_stat_change")

    validate_monthly_index(df)
    return df


def load_mlit_monthly_economy_cargo(file_path: str) -> pd.DataFrame:
    """
    国土交通月例経済の後続統計のみのデータを読み込む。

    想定列:
        - date または label
        - number_parcels
    """
    df = pd.read_csv(file_path)
    df = _set_datetime_index(df)
    df = add_log_target(df, target_col="number_parcels", log_col="y")
    validate_monthly_index(df)
    return df