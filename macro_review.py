import pandas as pd
import numpy as np

class MacroReviewGenerator:
    def __init__(self):
        pass

    def generate_mock_match(self):
        # Simulate a cohesive match storyline (MR12 format)
        # Round 1: Limit testing Pistol
        rounds = []
        scores = [0, 0] # Team A, Team B
        
        for r in range(1, 26): # Up to 25 rounds
            # Logic to create specific scenarios
            
            # Defaults
            team_buy_type = "Full Buy"
            enemy_buy_type = "Full Buy"
            win = np.random.choice([True, False])
            details = "Standard Gun Round"
            
            # Scenario: Pistol Rounds
            if r == 1 or r == 13:
                team_buy_type = "Pistol"
                enemy_buy_type = "Pistol"
                details = "Pistol Round"
                win = False # Let's say we lose pistols to trigger that review point
            
            # Scenario: Force Buy after Pistol Loss
            elif r == 2 and rounds[-1]['win'] == False:
                team_buy_type = "Force Buy"
                enemy_buy_type = "Anti-Eco"
                details = "Force Buy vs Anti-Eco"
                win = False # Lose the force -> Economic collapse
                
            # Scenario: Throwing a 5v3
            elif r == 15:
                team_buy_type = "Full Buy"
                enemy_buy_type = "Full Buy"
                details = "5v3 Advantage"
                win = False # Throw
                
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
        
        print("Analyzing Match Data...")
        
        # 1. Pistol Round Analysis
        pistols = df[df['round_num'].isin([1, 13])]
        pistol_wins = pistols[pistols['win'] == True]
        if len(pistol_wins) < 2:
            lost_pistols = pistols[pistols['win'] == False]['round_num'].tolist()
            agenda.append(f"CRITICAL: Lost Pistol Rounds ({', '.join(map(str, lost_pistols))}). Momentum starter failed.")

        # 2. Economy Management (Force Buy detection)
        # Check rounds where we Forced vs Anti-Eco and Lost
        bad_forces = df[
            (df['team_buy'] == "Force Buy") & 
            (df['enemy_buy'] == "Anti-Eco") & 
            (df['win'] == False)
        ]
        if not bad_forces.empty:
            rounds_str = ", ".join(map(str, bad_forces['round_num'].tolist()))
            agenda.append(f"ECONOMY: Failed Force Buys on rounds {rounds_str}. Resulted in broken economy.")

        # 3. Choke Points (Throws)
        # In real implementation, we'd use the Predictor here.
        # For now, look for "5v3 Advantage" in details that resulted in Loss
        throws = df[
            (df['details'].str.contains("5v3")) & 
            (df['win'] == False)
        ]
        if not throws.empty:
            rounds_str = ", ".join(map(str, throws['round_num'].tolist()))
            agenda.append(f"STRATEGY: Threw 5v3 advantage on round {rounds_str}. Review player positioning.")

        return agenda

if __name__ == "__main__":
    reviewer = MacroReviewGenerator()
    match_data = reviewer.generate_mock_match()
    
    print("\n--- Match History ---")
    print(match_data[['round_num', 'team_score_before', 'team_buy', 'win', 'details']].to_string(index=False))
    
    print("\n\n=== AUTOMATED COACH AGENDA ===")
    agenda_items = reviewer.analyze_match(match_data)
    for i, item in enumerate(agenda_items, 1):
        print(f"{i}. {item}")
    
    if not agenda_items:
        print("No critical issues found. Good game!")
