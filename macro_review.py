import pandas as pd
import numpy as np

class MacroReviewGenerator:
    def __init__(self):
        self.macro_patterns = {}

    def generate_mock_match(self):
        # Simulate a cohesive match storyline (MR12 format)
        rounds = []
        scores = [0, 0] # Team A, Team B
        
        for r in range(1, 26): # Up to 25 rounds
            team_buy_type = "Full Buy"
            enemy_buy_type = "Full Buy"
            win = np.random.choice([True, False])
            details = "Standard Gun Round"
            
            # Scenario: Pistol Rounds
            if r == 1 or r == 13:
                team_buy_type = "Pistol"
                enemy_buy_type = "Pistol"
                details = "Pistol Round"
                win = False 
            
            # Scenario: Force Buy after Pistol Loss
            elif r == 2 and rounds[-1]['win'] == False:
                team_buy_type = "Force Buy"
                enemy_buy_type = "Anti-Eco"
                details = "Force Buy vs Anti-Eco"
                win = False 
                
            # Scenario: Throwing a 5v3
            elif r == 15:
                team_buy_type = "Full Buy"
                enemy_buy_type = "Full Buy"
                details = "5v3 Advantage"
                win = False 
                
            rounds.append({
                "round_num": r,
                "team_score_before": f"{scores[0]}-{scores[1]}",
                "team_buy": team_buy_type,
                "enemy_buy": enemy_buy_type,
                "win": win,
                "details": details
            })
            
            if win: scores[0] += 1
            else: scores[1] += 1
            
            if scores[0] == 13 or scores[1] == 13: break
            
        return pd.DataFrame(rounds)

    def analyze_match(self, df):
        agenda = []
        
        # 1. Pistol Round Analysis
        pistols = df[df['round_num'].isin([1, 13])]
        lost_pistols = pistols[pistols['win'] == False]['round_num'].tolist()
        if lost_pistols:
            agenda.append(f"CRITICAL: Lost Pistol Rounds ({', '.join(map(str, lost_pistols))}). Momentum starter failed.")

        # 2. Economy Management
        bad_forces = df[(df['team_buy'] == "Force Buy") & (df['enemy_buy'] == "Anti-Eco") & (df['win'] == False)]
        if not bad_forces.empty:
            rounds_str = ", ".join(map(str, bad_forces['round_num'].tolist()))
            agenda.append(f"ECONOMY: Failed Force Buys on rounds {rounds_str}. Resulted in broken economy.")

        # 3. Choke Points
        throws = df[(df['details'].str.contains("5v3")) & (df['win'] == False)]
        if not throws.empty:
            rounds_str = ", ".join(map(str, throws['round_num'].tolist()))
            agenda.append(f"STRATEGY: Threw 5v3 advantage on round {rounds_str}. Review player positioning.")

        return agenda

    def generate_segment_data(self, n=200):
        """Mock method needed by scenario_validation.py"""
        return pd.DataFrame({
            "unspent_gold": np.random.randint(0, 5000, n),
            "orbs_picked_up": np.random.randint(0, 5, n),
            "execution_time_left": np.random.randint(0, 60, n),
            "win_rate": np.random.random(n)
        })

    def train_macro_discovery(self, df):
        """Mock method needed by scenario_validation.py"""
        self.macro_patterns['avg_gold'] = df['unspent_gold'].mean()
        print("Macro Discovery Training Complete.")

    def generate_review_agenda(self, match_id, team_a, team_b, map_name, match_data):
        """Mock method needed by scenario_validation.py"""
        agenda_items = []
        if match_data['unspent_gold'].mean() > 1000:
            agenda_items.append("Excessive unspent gold in lost rounds.")
        if match_data['orbs_picked_up'].mean() < 3:
            agenda_items.append("Poor ultimate orb control.")
        
        return {
            "MatchID": match_id,
            "Teams": f"{team_a} vs {team_b}",
            "Map": map_name,
            "Agenda Items": agenda_items
        }

if __name__ == "__main__":
    reviewer = MacroReviewGenerator()
    match_data = reviewer.generate_mock_match()
    print("\n=== AUTOMATED COACH AGENDA ===")
    agenda_items = reviewer.analyze_match(match_data)
    for i, item in enumerate(agenda_items, 1):
        print(f"{i}. {item}")
