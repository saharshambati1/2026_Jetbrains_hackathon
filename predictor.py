import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class HypotheticalPredictor:
    def __init__(self):
        self.model = xgb.XGBClassifier(eval_metric='logloss')
        self.is_trained = False
        self.historical_db = None 
        self.EXPECTED_COLS = [
            'numerical_advantage', 'economy_diff', 'spike_planted', 'team_health_avg',
            'map_Ascent', 'map_Bind', 'map_Haven', 'map_Split', 'map_Lotus', 'map_Sunset', 'map_Abyss'
        ]

    def _generate_realistic_history(self, n_samples=5000):
        np.random.seed(42)
        maps = ['Ascent', 'Bind', 'Haven', 'Split', 'Lotus', 'Sunset', 'Abyss']
        
        data = {
            'map': np.random.choice(maps, n_samples),
            'numerical_advantage': np.random.choice([-2, -1, 0, 1, 2], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1]),
            'economy_diff': np.random.normal(0, 2000, n_samples),
            'spike_planted': np.random.choice([0, 1], n_samples),
            'team_health_avg': np.random.normal(100, 20, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        scores = (
            0.5 + 
            (df['numerical_advantage'] * 0.2) + 
            (df['economy_diff'] / 10000) + 
            (df['spike_planted'] * 0.1)
        )
        probs = np.clip(scores, 0.1, 0.9)
        df['win'] = [1 if np.random.random() < p else 0 for p in probs]
        return df

    def _prepare_features(self, df):
        # One-hot encode
        df_encoded = pd.get_dummies(df, columns=['map'])
        
        # Enforce columns
        for col in self.EXPECTED_COLS:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        # Select and Sort
        return df_encoded[self.EXPECTED_COLS]

    def train(self):
        print("Loading Historical Match Data (Simulated 5,000 Rounds)...")
        self.historical_db = self._generate_realistic_history()
        
        X = self._prepare_features(self.historical_db.drop('win', axis=1))
        y = self.historical_db['win']
        
        print("Training XGBoost Scenario Model...")
        self.model.fit(X, y)
        self.is_trained = True
        print("Predictor Ready.")

    def predict_scenario(self, map_name, numerical_advantage, economy_diff, spike_planted):
        if not self.is_trained:
            self.train()
            
        similar_df = self.historical_db[
            (self.historical_db['map'] == map_name) &
            (self.historical_db['economy_diff'].between(economy_diff - 1500, economy_diff + 1500))
        ]
        
        hist_win_rate = similar_df['win'].mean() if not similar_df.empty else 0.5
        sample_count = len(similar_df)
        
        input_data = pd.DataFrame([{
            'map': map_name,
            'numerical_advantage': numerical_advantage,
            'economy_diff': economy_diff,
            'spike_planted': 1 if spike_planted else 0,
            'team_health_avg': 100 
        }])
        
        X_final = self._prepare_features(input_data)
        prob = self.model.predict_proba(X_final)[0][1]
        
        return {
            "prediction_prob": float(prob),
            "historical_win_rate": float(hist_win_rate),
            "sample_size": int(sample_count),
            "interpretation": self._interpret_prob(prob)
        }
        
    def _interpret_prob(self, p):
        if p < 0.3: return "Low Probability (Risky)"
        if p < 0.5: return "Unfavorable"
        if p < 0.7: return "Favorable"
        return "High Probability (Execute recommended)"

if __name__ == "__main__":
    predictor = HypotheticalPredictor()
    predictor.train()
    
    print("\n--- 'What If' Analysis: Force Buy vs Save on Ascent ---")
    res_force = predictor.predict_scenario('Ascent', 0, -1500, False)
    print(f"Force Buy Scenario: {res_force['prediction_prob']:.1%} Win Rate ({res_force['interpretation']})")
    
    res_save = predictor.predict_scenario('Ascent', 0, -4000, False)
    print(f"Save Scenario:      {res_save['prediction_prob']:.1%} Win Rate ({res_save['interpretation']})")
    
    delta = res_force['prediction_prob'] - res_save['prediction_prob']
    print(f"Conclusion: Force Buying increases round win probability by {delta*100:.1f}%")
