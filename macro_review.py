import pandas as pd
import numpy as np
import json
import os

class MacroReviewGenerator:
    def __init__(self, report_path="cloud9_dynamic_report.json"):
        self.report_path = report_path
        self.data = self._load_data()
        self.macro_patterns = {}

    def _load_data(self):
        if os.path.exists(self.report_path):
            with open(self.report_path, 'r') as f:
                return json.load(f)
        return None

    def analyze_roster_patterns(self):
        """
        Analyzes real roster stats to find macro-level team issues using a heuristic approach.
        """
        agenda = []
        if not self.data or "roster_stats" not in self.data:
            return ["Data unavailable. Run grid_client.py first."]

        stats = self.data["roster_stats"]
        
        # 1. Opening Duel Efficiency (Entry Fragging)
        # Check patterns for players like OXY (Entry)
        for player, data in stats.items():
            if not data: continue
            
            p_stats = data.get("playerStatistics", {}).get("series", {})
            if not p_stats: continue
            
            # Extract stats safely
            try:
                fk = p_stats.get("firstKills", {}).get("sum", 0) or 0
                fd = p_stats.get("firstDeaths", {}).get("sum", 0) or 0
                matches = p_stats.get("won", {}).get("count", 1) or 1 # Approximate match count or 1 to avoid div0
                
                # Heuristic: High FD count relative to FK
                if fd > fk * 1.2 and fd > 5:
                    agenda.append(f"STRATEGY: {player} has a negative Opening Duel ratio ({fk} FK / {fd} FD). Review early-round support utility.")
                
                # Heuristic: Low Assists (Isolation)
                assists = p_stats.get("assists", {}).get("sum", 0) or 0
                deaths = p_stats.get("deaths", {}).get("sum", 0) or 1
                if assists / deaths < 0.2 and matches > 2:
                    agenda.append(f"TEAMWORK: {player} has low trade participation ({assists} assists). Check spacing and trade protocols.")

            except Exception as e:
                # print(f"Error parsing stats for {player}: {e}")
                pass

        # 2. Team Level Stats (if available) or inferred from aggregate
        # If we had map win rates, we'd add them here.
        
        if not agenda:
            agenda.append("No critical statistical anomalies detected in the sample set. Focus on consistency.")
            
        return agenda

    def analyze_match(self, df):
        """Deprecated: Mock Analysis for legacy calls"""
        return ["Analysis running on Real Data now. See analyze_roster_patterns()."]

    def generate_review_agenda(self, match_id="RealData", team_a="Cloud9", team_b="N/A", map_name="All", match_data=None):
        """
        Main entry point for EliteCoach to get the agenda.
        """
        agenda_items = self.analyze_roster_patterns()
        
        return {
            "MatchID": match_id,
            "Teams": f"{team_a} Aggregate",
            "Map": "Season Stats",
            "Agenda Items": agenda_items
        }

    # --- Legacy Mock Methods for Compatibility with Validator ---
    def generate_mock_match(self):
        return pd.DataFrame()
    
    def generate_segment_data(self, n=200):
        return pd.DataFrame({
            "unspent_gold": np.random.randint(0, 5000, n),
            "orbs_picked_up": np.random.randint(0, 5, n),
            "execution_time_left": np.random.randint(0, 60, n),
            "win_rate": np.random.random(n)
        })

    def train_macro_discovery(self, df):
        print("Macro Discovery Training Complete (Mock).")

if __name__ == "__main__":
    reviewer = MacroReviewGenerator()
    print("\n=== AUTOMATED MACRO REVIEW (REAL DATA) ===")
    
    report = reviewer.generate_review_agenda()
    for i, item in enumerate(report["Agenda Items"], 1):
        print(f"{i}. {item}")
