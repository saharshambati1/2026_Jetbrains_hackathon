import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class HypotheticalPredictor:
    def __init__(self):
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.is_trained = False
        self.historical_db = None # Storage for similarity constraints

    def generate_training_data(self, n_samples=2000):
        np.random.seed(42)
        
        maps = ['Haven', 'Ascent', 'Bind', 'Split']
        num_adv = np.random.randint(-5, 6, n_samples)
        hp_diff = np.random.normal(0, 200, n_samples)
        econ_diff = np.random.normal(0, 5000, n_samples)
        spike = np.random.randint(0, 2, n_samples)
        map_labels = [np.random.choice(maps) for _ in range(n_samples)]
        
        # Ground Truth Probability
        score = (num_adv * 1.5) + (hp_diff / 100) + (econ_diff / 2000) - (spike * 0.8)
        prob = 1 / (1 + np.exp(-score))
        wins = [1 if np.random.random() < p else 0 for p in prob]
        
        X = pd.DataFrame({
            'numerical_advantage': num_adv,
            'health_diff': hp_diff,
            'economy_diff': econ_diff,
            'spike_planted': spike,
            'map': map_labels
        })
        y = np.array(wins)
        return X, y

    def train(self):
        print("Training XGBoost Hypothetical Predictor with Similarity Layer...")
        X, y = self.generate_training_data()
        
        # Store for similarity filtering
        self.historical_db = X.copy()
        self.historical_db['outcome'] = y
        
        # One-hot encode map for the model
        X_encoded = pd.get_dummies(X, columns=['map'])
        
        X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        print(f"Model Trained. Accuracy: {accuracy_score(y_test, preds):.2f}")
        self.is_trained = True

    def predict_scenario(self, map_name, numerical_advantage, health_diff, economy_diff, spike_planted):
        if not self.is_trained:
            self.train()
            
        # 1. SIMILARITY CONSTRAINT: Filter historical data
        # Find matches with same map and similar economy (+/- 2000)
        similar_cases = self.historical_db[
            (self.historical_db['map'] == map_name) & 
            (self.historical_db['economy_diff'].between(economy_diff - 1000, economy_diff + 1000)) &
            (self.historical_db['numerical_advantage'] == numerical_advantage)
        ]
        
        sample_size = len(similar_cases)
        historical_win_rate = similar_cases['outcome'].mean() if sample_size > 0 else 0.0

        # 2. MODEL PREDICTION
        input_row = pd.DataFrame([{
            'numerical_advantage': numerical_advantage,
            'health_diff': health_diff,
            'economy_diff': economy_diff,
            'spike_planted': 1 if spike_planted else 0,
            'map': map_name
        }])
        
        # Ensure all columns exist for encoded model
        X_encoded = pd.get_dummies(input_row, columns=['map'])
        # Realign with training columns
        model_cols = pd.get_dummies(self.historical_db.drop('outcome', axis=1), columns=['map']).columns
        X_encoded = X_encoded.reindex(columns=model_cols, fill_value=0)
        
        model_prob = self.model.predict_proba(X_encoded)[0][1]
        
        # Confidence Tier
        confidence = "Low"
        if sample_size > 50: confidence = "High"
        elif sample_size > 15: confidence = "Medium"

        return {
            "prediction_prob": model_prob,
            "historical_win_rate": historical_win_rate,
            "sample_size": sample_size,
            "confidence_tier": confidence
        }

if __name__ == "__main__":
    predictor = HypotheticalPredictor()
    predictor.train()
    
    print("\n--- 'What If' Analysis: Retake vs Save on Haven ---")
    
    # 3v5 Retake
    res = predictor.predict_scenario('Haven', -2, -50, -1000, True)
    print(f"Scenario: Attempting 3v5 Retake")
    print(f"  Model Prediction: {res['prediction_prob']:.1%}")
    print(f"  Historical Base (n={res['sample_size']}): {res['historical_win_rate']:.1%}")
    print(f"  Confidence: {res['confidence_tier']}")
