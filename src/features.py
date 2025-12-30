import pandas as pd

def add_period_dummies(df: pd.DataFrame, periods: dict) -> pd.DataFrame:
    """
    辞書定義に基づいて期間ダミー変数をまとめて追加する関数
    """
    df = df.copy() 
    idx = df.index
    
    for name, (start, end) in periods.items():
        if end is None:
            # 終了日なし（継続）
            df[name] = (idx >= start).astype(int)
        else:
            # 期間指定
            df[name] = ((idx >= start) & (idx <= end)).astype(int)
            
    return df

def prepare_event_data(df: pd.DataFrame, event_config: dict):
    """
    設定辞書に基づいてダミー変数を作成し、モデル入力用の形式にまとめて返す。
    """
    # 上で定義した関数を利用してダミー変数を追加
    df = add_period_dummies(df, event_config)
    
    # 名前リストを作成
    exog_names = list(event_config.keys())
    
    # データリストを作成（Seriesのリスト）
    exog_data = [df[name] for name in exog_names]
    
    return df, exog_data, exog_names