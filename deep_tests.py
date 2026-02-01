import sys
import pandas as pd
import numpy as np
from mistake_detector import MistakeDetector
from macro_review import MacroReviewGenerator
from elite_coach import EliteCoach

def test_cloud9_oxy_entry():
    """Tests if the system correctly identifies OXY's isolated entry as a mistake."""
    print("\n--- DEEP TEST: CLOUD9 OXY ENTRY ANALYSIS ---")
    detector = MistakeDetector()
    
    # Simulate: OXY enters site but teammate is 45m away (too far to trade)
    data = []
    for i in range(250):
        # Baseline: Good entries (distance < 15m)
        if i < 200:
            dist = 10 + np.random.normal(0, 1)
            kast = 1
            win = 1
        else:
            dist = 45 + np.random.normal(0, 5)
            kast = 0
            win = 0
            
        data.append({
            "event_id": i, "player_id": "OXY", "event_type": "Opening Duel",
            "teammate_distance": max(0, dist), "utility_used": 1, "kast_success": kast, "round_win": win
        })
    
    df = pd.DataFrame(data)
    detector.train_per_event(df)
    mistakes = detector.detect_mistakes(df)
    
    oxy_errors = mistakes[mistakes['player_id'] == 'OXY']
    if not oxy_errors.empty:
        print(f"SUCCESS: Identified {len(oxy_errors)} isolation mistakes for OXY.")
        print(f"Insight: {oxy_errors.iloc[0]['explanation']}")
    else:
        print("FAILURE: System missed OXY's isolation error.")
        sys.exit(1)

def test_elite_coach_integration():
    """Verify the full pipeline from data to LLM advice."""
    print("\n--- DEEP TEST: ELITE COACH FULL PIPELINE ---")
    coach = EliteCoach(use_mock_data=True)
    report = coach.generate_elite_report(team_name="Cloud9", map_name="Lotus")
    
    print("LLM Advice received:")
    print("-" * 30)
    print(report['llm_advice'])
    print("-" * 30)
    
    if "OXY" in report['llm_advice'] or "Vanity" in report['llm_advice']:
        print("SUCCESS: Coach recognized specific players in context.")
    else:
        print("WARNING: Coach provided general advice. Check context injection.")
    
    assert "llm_advice" in report
    assert "raw_data" in report
    print("SUCCESS: Pipeline integration verified.")

if __name__ == "__main__":
    test_cloud9_oxy_entry()
    test_elite_coach_integration()
