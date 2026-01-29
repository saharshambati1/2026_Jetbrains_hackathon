import pandas as pd
import numpy as np
from mistake_detector import MistakeDetector
from macro_review import MacroReviewGenerator

def test_momentum_tilt():
    print("\n--- DEEP TEST: MOMENTUM & TILT DETECTION ---")
    detector = MistakeDetector()
    
    # Simulate: Player loses 3 rounds in a row, then overextends
    data = []
    for i in range(20):
        # Normal play for first 10
        win = 1 if i < 10 else 0
        dist = 15 if i < 10 else 18
        
        # Injected Tilt: Round 11-13 lost, Round 14 player TRIES 50m overextend
        if i == 13:
            dist = 50
            win = 0
            
        data.append({
            "event_id": i,
            "player_id": "TiltPlayer",
            "event_type": "Opening Duel",
            "teammate_distance": dist,
            "utility_used": 1,
            "kast_success": 1 if i != 13 else 0,
            "round_win": win
        })
    
    df = pd.DataFrame(data)
    detector.train_per_event(df)
    mistakes = detector.detect_mistakes(df)
    
    if mistakes.empty:
        print("FAILURE: No mistakes detected in Tilt scenario.")
        return

    # We expect Round 13 to be a high-impact mistake
    if 'event_id' in mistakes.columns:
        tilt_mistake = mistakes[mistakes['event_id'] == 13]
        if not tilt_mistake.empty:
            print(f"SUCCESS: Detected 'Tilt' mistake at Round 13 (Anomaly Score: {tilt_mistake.iloc[0]['anomaly_score']:.2f})")
        else:
            print("FAILURE: Round 13 not flagged as mistake.")
    else:
        print(f"Error: 'event_id' missing. Cols: {mistakes.columns}")

def test_utility_waste():
    print("\n--- DEEP TEST: UTILITY WASTE DETECTION ---")
    detector = MistakeDetector()
    
    # Success Baseline (Normal utility usage)
    baseline = []
    for i in range(100):
        baseline.append({
            "event_id": i, "player_id": "P1", "event_type": "Retake Attempt",
            "teammate_distance": 10, "utility_used": 2, "kast_success": 1, "round_win": 1
        })
    
    # Anomaly: Dumped 5 utility items but failed KAST (Panic Utility)
    baseline.append({
        "event_id": 101, "player_id": "P1", "event_type": "Retake Attempt",
        "teammate_distance": 10, "utility_used": 5, "kast_success": 0, "round_win": 0
    })
    
    df = pd.DataFrame(baseline)
    detector.train_per_event(df)
    mistakes = detector.detect_mistakes(df)
    
    if mistakes.empty:
        print("FAILURE: No mistakes detected in Utility Waste scenario.")
        return

    if 'event_id' in mistakes.columns:
        waste = mistakes[mistakes['event_id'] == 101]
        if not waste.empty:
            print(f"SUCCESS: Detected 'Panic Utility' at Round 101 (Anomaly Score: {waste.iloc[0]['anomaly_score']:.2f})")
        else:
            print("FAILURE: Round 101 not flagged as waste.")
    else:
        print(f"Error: 'event_id' missing. Cols: {mistakes.columns}")

if __name__ == "__main__":
    test_momentum_tilt()
    test_utility_waste()
