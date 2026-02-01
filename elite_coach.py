import pandas as pd
import numpy as np
import json
from coach_brain import CoachBrain
from mistake_detector import MistakeDetector, generate_valorant_event_data
from predictor import HypotheticalPredictor
from macro_review import MacroReviewGenerator

class EliteCoach:
    def __init__(self, use_mock_data=True):
        self.brain = CoachBrain()
        self.detector = MistakeDetector()
        self.predictor = HypotheticalPredictor()
        self.reviewer = MacroReviewGenerator()
        self.use_mock_data = use_mock_data
        
        # Pre-train models if using mock data
        if use_mock_data:
            print("Initializing Elite Coach with pre-trained models...")
            event_df = generate_valorant_event_data(500)
            self.detector.train_per_event(event_df)
            self.predictor.train()

    def generate_elite_report(self, team_name="Cloud9", opponent="Team Liquid", map_name="Ascent"):
        print(f"Generating Elite Coaching Report for {team_name}...")
        
        # 1. Macro Analysis
        match_df = self.reviewer.generate_mock_match()
        macro_agenda = self.reviewer.analyze_match(match_df)
        
        # 2. Player-Specific Anomaly Detection
        # Simulate recent events for OXY and Vanity
        events = generate_valorant_event_data(50)
        # Force some anomalies for demonstration
        events.loc[0, ['teammate_distance', 'kast_success', 'round_win']] = [60.0, 0, 0] # OXY overextend
        events.loc[1, ['utility_used', 'kast_success', 'round_win']] = [5, 0, 0] # Vanity panic util
        
        mistakes = self.detector.detect_mistakes(events)
        
        # 3. Hypothetical "What-If" Analysis
        # What if they forced instead of saving on a lost pistol?
        what_if_force = self.predictor.predict_scenario(map_name, 0, 0, -2000, False)
        what_if_save = self.predictor.predict_scenario(map_name, 0, 0, 3000, False)
        
        # 4. Synthesize for LLM
        # Handle non-serializable float32 from XGBoost/NumPy
        context = {
            "team": team_name,
            "opponent": opponent,
            "map": map_name,
            "macro_issues": macro_agenda,
            "player_mistakes": mistakes[['player_id', 'event_type', 'explanation']].head(3).to_dict('records'),
            "win_probs": {
                "force_buy_prob": float(what_if_force['prediction_prob']),
                "save_buy_prob": float(what_if_save['prediction_prob'])
            }
        }
        
        system_persona = f"""You are the Elite Assistant Coach for {team_name} Valorant. 
        Your advice must be extremely dynamic, data-backed, and accurate.
        Focus on Cloud9's aggressive style but highlight where discipline is failing.
        Be concise but impactful. Address players like OXY and Vanity directly if they appear in the data.
        """
        
        user_query = f"Based on the latest match data on {map_name}, give us a strategic review."
        
        # Safe JSON dump for debugging/logging
        try:
            context_str = json.dumps(context, indent=2)
        except TypeError:
            # Emergency fallback: convert everything to str if complex types persist
            context_str = str(context)

        report = self.brain.ask_coach(system_persona, user_query, match_context=context_str)
        
        return {
            "llm_advice": report,
            "raw_data": context
        }

if __name__ == "__main__":
    coach = EliteCoach()
    result = coach.generate_elite_report()
    
    print("\n" + "="*50)
    print("ELITE COACHING REPORT (Cloud9)")
    print("="*50)
    print(result['llm_advice'])
    print("\n--- Summary of Data Used ---")
    print(f"Macro Issues: {len(result['raw_data']['macro_issues'])}")
    print(f"Mistakes Detected: {len(result['raw_data']['player_mistakes'])}")
    print(f"Alternative Strategy Prob (Save): {result['raw_data']['win_probs']['save_buy_prob']:.1%}")
