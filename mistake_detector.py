import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from grid_client import GridClient
import json

# MOCK DATA GENERATOR (Fallback)
def generate_mock_data(n_rounds=100):
    np.random.seed(42)
    data = result = []
    
    for i in range(n_rounds):
        # Normal play
        kills = np.random.poisson(1.0)
        deaths = np.random.binomial(1, 0.5)
        assist = np.random.poisson(0.5)
        damage = np.random.normal(150, 50)
        economy = np.random.normal(3000, 1000)
        time_alive = np.random.normal(60, 20) # Seconds
        
        # Inject anomalies (Mistakes)
        if i % 20 == 0: 
            # High economy, early death, no impact
            kills = 0
            deaths = 1
            damage = 0
            economy = 4500
            time_alive = 10 # Died in 10s
        
        data.append({
            "round_id": i + 1,
            "kills": kills,
            "deaths": deaths,
            "assists": assist,
            "damage": max(0, damage),
            "economy": max(0, economy),
            "time_alive": max(0, time_alive)
        })
    return pd.DataFrame(data)

class MistakeDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()

    def train_and_detect(self, df):
        features = ['kills', 'deaths', 'damage', 'economy', 'time_alive']
        X = df[features]
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model.fit(X_scaled)
        
        # Predict anomalies (-1 is anomaly, 1 is normal)
        df['anomaly_score'] = self.model.decision_function(X_scaled)
        df['is_anomaly'] = self.model.predict(X_scaled)
        
        anomalies = df[df['is_anomaly'] == -1]
        return anomalies

    def explain_anomaly(self, row):
        # Simple heuristic explanation
        reasons = []
        if row['deaths'] == 1 and row['time_alive'] < 20:
            reasons.append("Early Death")
        if row['economy'] > 4000 and row['damage'] < 50:
            reasons.append("Wasted Economy (Low Damage)")
        if row['kills'] == 0 and row['deaths'] == 1 and row['damage'] == 0:
            reasons.append("Zero Impact Round")
            
        return ", ".join(reasons) if reasons else "Statistical Outlier"

if __name__ == "__main__":
    print("Cloud9 Assistant Coach - Mistake Detector")
    print("-----------------------------------------")
    
    # 1. Try to fetch real data
    try:
        client = GridClient()
        # TODO: Implement actual fetching logic here once query is stable
        # series = client.get_recent_valorant_series()
        # For now, start with Mock because query is being debugged
        raise Exception("Force Mock for demo stability while debugging Query")
    except Exception as e:
        print(f"Status: Using Mock Data ({e})")
        df = generate_mock_data()

    print(f"Loaded {len(df)} rounds of data.")
    
    # 2. Detect Mistakes
    detector = MistakeDetector()
    anomalies = detector.train_and_detect(df)
    
    print("\nDetected Mistakes (Anomalies):")
    for idx, row in anomalies.iterrows():
        reason = detector.explain_anomaly(row)
        print(f"[Round {int(row['round_id'])}] Score: {row['anomaly_score']:.2f} -> {reason}")
        print(f"  Stats: K({int(row['kills'])}) D({int(row['deaths'])}) Econ({int(row['economy'])}) Time({int(row['time_alive'])})s")
        print("---")
