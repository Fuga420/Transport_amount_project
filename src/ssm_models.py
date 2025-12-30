import numpy as np
import statsmodels.api as sm

class LocalLinearTrendSeasonalWithMultiFixedExog(sm.tsa.statespace.MLEModel):
    """
    トレンド(レベル+傾き) + 季節性 + 複数の固定係数の外生変数
    """
    def __init__(self, endog, exog_list, param_names, seasonal_period=12, **kwargs):
        # 季節性の周期に応じて状態数を動的に計算
        # レベル(1) + 傾き(1) + 季節性(seasonal_period - 1)
        self.k_seasonal = seasonal_period
        k_states = 2 + (self.k_seasonal - 1)
        k_posdef = 3
        
        self.param_names_custom = param_names
        self.num_exog = len(exog_list)
        
        super().__init__(endog=endog, k_states=k_states, k_posdef=k_posdef, initialization='diffuse', **kwargs)

        # デザイン行列: 観測値 = レベル + 季節性要素の先頭
        self.ssm['design'] = np.zeros((1, k_states))
        self.ssm['design', 0, 0] = 1
        self.ssm['design', 0, 2] = 1
        
        # 遷移行列 (Transition Matrix)
        T = np.zeros((k_states, k_states))
        # トレンド部分: level_t = level_{t-1} + slope_{t-1}
        T[0, 0] = 1; T[0, 1] = 1
        # 傾き部分: slope_t = slope_{t-1}
        T[1, 1] = 1
        
        # 季節性部分: ダミー変数法のような和がゼロになる制約
        # seasonal_t = -sum(seasonal_{t-1} ... seasonal_{t-(s-1)})
        T[2, 2:] = -1
        # シフトさせる部分
        for i in range(3, k_states):
            T[i, i - 1] = 1
            
        self.ssm['transition'] = T
        
        # 選択行列 (Selection Matrix)
        S = np.zeros((k_states, k_posdef))
        S[0, 0] = 1  # level noise
        S[1, 1] = 1  # slope noise
        S[2, 2] = 1  # seasonal noise
        self.ssm['selection'] = S

        # 外生変数の処理
        # 外生変数は pandas Series 等を想定して values を取得
        self.exogs = [ex.values.reshape(1, -1) for ex in exog_list]
        self.ssm['obs_intercept'] = np.zeros((1, len(endog)))

    @property
    def param_names(self):
        return self.param_names_custom

    def transform_params(self, unconstrained):
        # 最初の4つ（分散パラメータ）だけ正の値に変換
        c = unconstrained.copy()
        c[:4] = c[:4] ** 2 
        return c

    def untransform_params(self, constrained):
        u = constrained.copy()
        u[:4] = np.sqrt(u[:4])
        return u

    def update(self, params, **kwargs):
        params = super().update(params, **kwargs)
        
        # 分散パラメータの更新
        self['obs_cov', 0, 0] = params[0]
        self['state_cov', 0, 0] = params[1]
        self['state_cov', 1, 1] = params[2]
        self['state_cov', 2, 2] = params[3]
        
        # 外生変数の効果を計算 (5番目のパラメータ以降を使用)
        total_exog_effect = 0
        for i in range(self.num_exog):
            # params[4] から外生変数の係数が始まると仮定
            total_exog_effect += params[4 + i] * self.exogs[i]
            
        self['obs_intercept', 0, :] = total_exog_effect