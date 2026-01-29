import pandas as pd
import numpy as np
from mistake_detector import MistakeDetector
from macro_review import MacroReviewGenerator
from predictor import HypotheticalPredictor
from coach_brain import CoachBrain

def validate_prompt_1():
    print("\n--- VALIDATING PROMPT 1: PERSONALIZED INSIGHTS ---")
    detector = MistakeDetector()
    
    # Simulate Scenario: OXY loses 78% of rounds when dying without KAST
    data = []
    for i in range(100):
        is_oxy = (i < 50)
        kast = 0 if is_oxy and i < 40 else 1 # OXY dies without KAST in 40/50 cases
        win = 0 if (is_oxy and kast == 0 and i < 31) else 1 # 31/40 = 77.5% Loss
        
        data.append({
            "event_id": i,
            "player_id": "OXY" if is_oxy else "Other",
            "event_type": "Opening Duel",
            "teammate_distance": 40 if kast == 0 else 10,
            "utility_used": 0 if kast == 0 else 2,
            "kast_success": kast,
            "round_win": win
        })
    df = pd.DataFrame(data)
    detector.train_per_event(df)
    mistakes = detector.detect_mistakes(df)
    
    if mistakes.empty:
        print("NO MISTAKES DETECTED. Check anomaly contamination or data variance.")
        return

    if 'player_id' in mistakes.columns:
        oxy_mistakes = mistakes[mistakes['player_id'] == 'OXY']
        print(f"OXY Mistakes Found: {len(oxy_mistakes)}")
        if not oxy_mistakes.empty:
            print(f"SAMPLE INSIGHT: {oxy_mistakes.iloc[0]['explanation']}")
    else:
        print(f"Error: 'player_id' missing from mistakes. Columns: {mistakes.columns}")

def validate_prompt_2():
    print("\n--- VALIDATING PROMPT 2: MACRO REVIEW AGENDA ---")
    reviewer = MacroReviewGenerator()
    pop_data = reviewer.generate_segment_data(200)
    reviewer.train_macro_discovery(pop_data)
    
    # Specific Match Data: Lost pistols, Late pushes, Low orbs
    match_data = pd.DataFrame([
        {"unspent_gold": 1200, "orbs_picked_up": 2, "execution_time_left": 10, "win_rate": 0.0},
        {"unspent_gold": 1500, "orbs_picked_up": 3, "execution_time_left": 15, "win_rate": 0.0},
    ])
    
    agenda = reviewer.generate_review_agenda("M1", "C9", "Team X", "Corrode", match_data)
    print(f"AGENDA FOR {agenda['Map']}:")
    for item in agenda['Agenda Items']:
        print(f"- {item}")

def validate_prompt_3():
    print("\n--- VALIDATING PROMPT 3: HYPOTHETICAL OUTCOME ---")
    predictor = HypotheticalPredictor()
    predictor.train()
    
    # Round 22 Haven 3v5
    res = predictor.predict_scenario('Haven', -2, -50, -1000, True)
    print(f"RETAKE PROBABILITY (3v5): {res['prediction_prob']:.1%}")
    
    # Save (5v5, Full HP, Better Econ)
    res_save = predictor.predict_scenario('Haven', 0, 0, 2000, False)
    print(f"SAVE PROBABILITY (Following Round): {res_save['prediction_prob']:.1%}")

if __name__ == "__main__":
    validate_prompt_1()
    validate_prompt_2()
    validate_prompt_3()
