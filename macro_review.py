from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class MacroReviewGenerator:
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.archetypes = {
            0: "Delayed Reset (High Gold/Low Tempo)",
            1: "Post-Plant Collapse (Late Round Issues)",
            2: "Ultimate Deficit (Low Orb Control)",
            3: "Optimal Tempo (High Win Rate)"
        }

    def generate_segment_data(self, n_segments=100):
        np.random.seed(42)
        segments = []
        for i in range(n_segments):
            # Features: Gold, Orb Control, Execution Time, Win Rate
            unspent_gold = np.random.normal(2000, 1000)
            orbs_picked_up = np.random.randint(2, 10)
            avg_exec_time = np.random.normal(45, 15) # Seconds left in round
            win_rate = np.random.uniform(0, 1)
            
            # Pattern: Late Round Executions (<20s)
            if i % 8 == 0:
                avg_exec_time = 15
                win_rate = 0.2
            
            # Pattern: Ultimate Deficit
            if i % 6 == 0:
                orbs_picked_up = 3
            
            segments.append({
                "segment_id": i,
                "unspent_gold": max(0, unspent_gold),
                "orbs_picked_up": orbs_picked_up,
                "execution_time_left": max(5, avg_exec_time),
                "win_rate": win_rate
            })
        return pd.DataFrame(segments)

    def train_macro_discovery(self, df):
        features = ["unspent_gold", "orbs_picked_up", "execution_time_left", "win_rate"]
        X = df[features]
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans.fit(X_scaled)

    def generate_review_agenda(self, match_id, team_name, opponent, map_name, match_df):
        """
        Generates a structured Game Review Agenda report.
        """
        features = ["unspent_gold", "orbs_picked_up", "execution_time_left", "win_rate"]
        X = match_df[features]
        X_scaled = self.scaler.transform(X)
        clusters = self.kmeans.predict(X_scaled)
        
        counts = pd.Series(clusters).value_counts(normalize=True)
        dominant_id = counts.idxmax()

        # Structured Agenda
        agenda = {
            "Match": f"BO1 vs {opponent}",
            "Map": map_name,
            "Dominant Pattern": self.archetypes.get(dominant_id),
            "Agenda Items": []
        }

        # 1. Ultimate Economy
        avg_orbs = match_df['orbs_picked_up'].mean()
        if avg_orbs < 5:
            agenda["Agenda Items"].append(f"Ultimate Economy: Only {avg_orbs:.1f} orbs picked up per phase. Deficit in ultimate pressure.")

        # 2. Execution Timing
        late_execs = match_df[match_df['execution_time_left'] < 20]
        if not late_execs.empty:
            agenda["Agenda Items"].append(f"Mid-Round Calls: {len(late_execs)} attack phases saw late pushes (<20s left). Critical for round conversions.")

        # 3. Economy (Cluster 0)
        if dominant_id == 0:
            agenda["Agenda Items"].append("Eco Management: Recurring high unspent gold in lost rounds. Review buy/save criteria.")

        return agenda

if __name__ == "__main__":
    reviewer = MacroReviewGenerator()
    pop_data = reviewer.generate_segment_data(200)
    reviewer.train_macro_discovery(pop_data)
    
    # Specific Match Data (from user prompt scenario)
    match_data = pd.DataFrame([
        {"unspent_gold": 1200, "orbs_picked_up": 4, "execution_time_left": 15, "win_rate": 0.0},
        {"unspent_gold": 2500, "orbs_picked_up": 3, "execution_time_left": 18, "win_rate": 0.0},
        {"unspent_gold": 4000, "orbs_picked_up": 6, "execution_time_left": 40, "win_rate": 0.5},
    ])
    
    report = reviewer.generate_review_agenda("M1", "C9", "Team X", "Corrode", match_data)
    
    print("\n[PROMPT 2: AUTOMATED MACRO REVIEW]")
    print(f"Generated Review Agenda for {report['Map']}:")
    print(f"Match: {report['Match']}")
    print(f"Dominant Pattern: {report['Dominant Pattern']}")
    for item in report['Agenda Items']:
        print(f"- {item}")
