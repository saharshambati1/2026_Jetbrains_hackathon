import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class HypotheticalPredictor:
    def __init__(self):
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.is_trained = False

    def generate_training_data(self, n_samples=1000):
        # Synthetic data representing:
        # numerical_advantage (e.g., -2 means 3v5)
        # health_diff (e.g., -100 means team has less HP)
        # economy_diff (e.g., +2000 means team has better guns)
        # spike_planted (0 or 1)
        # win (0 or 1)
        
        np.random.seed(42)
        
        num_adv = np.random.randint(-5, 6, n_samples)
        hp_diff = np.random.normal(0, 200, n_samples)
        econ_diff = np.random.normal(0, 5000, n_samples)
        spike = np.random.randint(0, 2, n_samples)
        
        # Logic for "Ground Truth": 
        # Win probability increases with advantages
        score = (num_adv * 1.5) + (hp_diff / 100) + (econ_diff / 2000) - (spike * 0.5)
        # Sigmoid to get probability
        prob = 1 / (1 + np.exp(-score))
        wins = [1 if np.random.random() < p else 0 for p in prob]
        
        X = pd.DataFrame({
            'numerical_advantage': num_adv,
            'health_diff': hp_diff,
            'economy_diff': econ_diff,
            'spike_planted': spike
        })
        y = np.array(wins)
        return X, y

    def train(self):
        print("Training XGBoost Hypothetical Predictor...")
        X, y = self.generate_training_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Model Trained. Accuracy on synthetic validation set: {acc:.2f}")
        self.is_trained = True

    def predict_scenario(self, numerical_advantage, health_diff, economy_diff, spike_planted):
        if not self.is_trained:
            self.train()
            
        input_data = pd.DataFrame([{
            'numerical_advantage': numerical_advantage,
            'health_diff': health_diff,
            'economy_diff': economy_diff,
            'spike_planted': 1 if spike_planted else 0
        }])
        
        prob = self.model.predict_proba(input_data)[0][1] # Probability of class 1 (Win)
        return prob

if __name__ == "__main__":
    predictor = HypotheticalPredictor()
    predictor.train()
    
    print("\n--- Challenge Scenario: Round 22 (Score 10-11) ---")
    print("Action 1: Attempt 3v5 Retake (Broken Buy)")
    # 3v5 (-2 players), Low HP (-50), Poor Economy (-1000), Spike Planted (True)
    prob_retake = predictor.predict_scenario(-2, -50, -1000, True)
    print(f"Scenario 1 Win Probability: {prob_retake:.1%}")
    
    print("\nAction 2: Save Weapons for Next Round")
    # Next round: 5v5 (0), Full HP (0), Good Economy (+2000 due to save), No Spike (False)
    prob_save = predictor.predict_scenario(0, 0, 2000, False)
    print(f"Scenario 2 Win Probability: {prob_save:.1%}")
    
    if prob_save > prob_retake:
        print("\n>>> Recommendation: SAVE. (Generating +{:.1%} win equity)".format(prob_save - prob_retake))
    else:
        print("\n>>> Recommendation: RETAKE.")
