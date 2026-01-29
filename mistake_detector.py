import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from grid_client import GridClient
import json

# MOCK DATA GENERATOR (Advanced Valorant-Specific)
def generate_valorant_event_data(n_events=300):
    np.random.seed(42)
    events = []
    
    event_types = ['Opening Duel', 'Mid-Round Push', 'Retake Attempt', 'Force Buy Decision']
    
    for i in range(n_events):
        e_type = np.random.choice(event_types)
        
        # Base features
        teammate_dist = np.random.normal(15, 5) # Meters
        utility_used = np.random.randint(0, 5)
        kast = np.random.choice([0, 1], p=[0.2, 0.8]) # 80% KAST is normal
        outcome_win = np.random.choice([0, 1], p=[0.4, 0.6])
        
        # Inject OXY Scenario (Data 1 from user prompt)
        # "C9 loses 78% of rounds when OXY dies without KAST"
        is_oxy = (i % 20 == 0)
        if is_oxy:
            e_type = 'Opening Duel'
            kast = 0
            teammate_dist = 40
            outcome_win = np.random.choice([0, 1], p=[0.78, 0.22]) # 78% Loss
        
        events.append({
            "event_id": i + 1,
            "player_id": "OXY" if is_oxy else "PlayerX",
            "event_type": e_type,
            "teammate_distance": max(0, teammate_dist),
            "utility_used": utility_used,
            "kast_success": kast,
            "round_win": outcome_win
        })
    return pd.DataFrame(events)

class MistakeDetector:
    def __init__(self):
        self.models = {} 
        self.scalers = {}
        # Features: Teammate Dist, Utility, KAST, and Momentum (New)
        self.features = ['teammate_distance', 'utility_used', 'kast_success', 'momentum_score']

    def calculate_momentum(self, df):
        """
        Calculates if the previous round for this player had a critical mistake.
        Value > 0 means the player is potentially 'tilted' or under-performing.
        """
        df = df.sort_values(['player_id', 'event_id'])
        df['momentum_score'] = 0.0
        
        # Simple shift: if previous event for same player was a round loss
        # In real data, we'd check previous anomaly scores.
        df['prev_win'] = df.groupby('player_id')['round_win'].shift(1)
        df.loc[df['prev_win'] == 0, 'momentum_score'] = 1.0 # Pressure increase
        return df

    def train_per_event(self, df):
        df = self.calculate_momentum(df)
        event_types = df['event_type'].unique()
        for et in event_types:
            success_data = df[(df['event_type'] == et) & (df['round_win'] == 1)][self.features]
            if len(success_data) < 5: 
                success_data = df[df['event_type'] == et][self.features]
            
            scaler = StandardScaler()
            model = IsolationForest(contamination=0.15, random_state=42)
            X_scaled = scaler.fit_transform(success_data)
            model.fit(X_scaled)
            self.models[et] = model
            self.scalers[et] = scaler

    def detect_mistakes(self, df):
        # Automatically calculate momentum if features are missing
        if 'momentum_score' not in df.columns:
            df = self.calculate_momentum(df)
            
        results = []
        for idx, row in df.iterrows():
            et = row['event_type']
            if et not in self.models: continue
                
            X = row[self.features].values.reshape(1, -1)
            X_scaled = self.scalers[et].transform(X)
            
            anomaly_score = self.models[et].decision_function(X_scaled)[0]
            is_anomaly = self.models[et].predict(X_scaled)[0] == -1
            
            if is_anomaly and row['round_win'] == 0:
                results.append({
                    "event_id": row['event_id'],
                    "player_id": row['player_id'],
                    "event_type": et,
                    "anomaly_score": anomaly_score,
                    "teammate_dist": row['teammate_distance'],
                    "util": row['utility_used'],
                    "kast": row['kast_success'],
                    "explanation": self.explain_mistake(row, df)
                })
        return pd.DataFrame(results)

    def explain_mistake(self, row, full_df):
        reasons = []
        # Calculate impact of this specific anomaly type
        # E.g. Round loss rate for this player when they die without KAST
        player_data = full_df[full_df['player_id'] == row['player_id']]
        no_kast_loss = player_data[(player_data['kast_success'] == 0) & (player_data['round_win'] == 0)]
        no_kast_total = player_data[player_data['kast_success'] == 0]
        
        impact_pct = (len(no_kast_loss) / len(no_kast_total) * 100) if len(no_kast_total) > 0 else 0
        
        if row['kast_success'] == 0:
            reasons.append(f"Died without KAST ({impact_pct:.0f}% Team Loss Rate)")
        
        if row['event_type'] == 'Opening Duel' and row['teammate_distance'] > 30:
            reasons.append("Extreme Overextension (No Trade Support)")
            
        return " & ".join(reasons) if reasons else "Data-backed tactical error"

if __name__ == "__main__":
    detector = MistakeDetector()
    df = generate_valorant_event_data()
    detector.train_per_event(df)
    mistakes = detector.detect_mistakes(df)
    
    print("\n[PROMPT 1: PERSONALIZED INSIGHTS]")
    for _, m in mistakes[mistakes['player_id'] == 'OXY'].head(2).iterrows():
        print(f"Data-Backed Insight for {m['player_id']}:")
        print(f"  {m['explanation']}. (Anomaly Score: {m['anomaly_score']:.2f})")
        print(f"  Context: Dist {m['teammate_dist']:.1f}m, Util {m['util']}, KAST {m['kast']}")
        print("---")
