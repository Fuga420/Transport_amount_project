import pandas as pd
import numpy as np

def load_transport_data(file_path: str) -> pd.DataFrame:
    """
    輸送量データを読み込み、対数変換済みカラム 'y' を追加して返す。
    """
    df = pd.read_csv(file_path)
    
    # 日付変換
    if 'label' in df.columns:
        df['label'] = pd.to_datetime(df['label'])
        df.set_index('label', inplace=True)

    df['y'] = np.log(df['number_parcels'])
    
    return df