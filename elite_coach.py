import pandas as pd
import numpy as np
import json
from coach_brain import CoachBrain
from mistake_detector import MistakeDetector, generate_valorant_event_data
from predictor import HypotheticalPredictor
from macro_review import MacroReviewGenerator

class EliteCoach:
    def __init__(self):
        self.brain = CoachBrain()
        # self.detector = MistakeDetector() # Deprecated for this iteration unless using granular events
        self.predictor = HypotheticalPredictor()
        self.reviewer = MacroReviewGenerator(report_path="cloud9_dynamic_report.json")
        
        # Train predictor once on init
        self.predictor.train()

    def generate_elite_report(self, team_name="Cloud9", opponent="TBD", map_name="Ascent"):
        print(f"Generating Elite Coaching Report for {team_name}...")
        
        # 1. Macro Analysis (Real Data)
        print(" -> Running Automated Macro Review...")
        macro_report = self.reviewer.generate_review_agenda(match_id="Latest", team_a=team_name)
        macro_agenda = macro_report.get("Agenda Items", [])
        
        # 2. Hypothetical "What-If" Analysis (Historical Data)
        print(" -> Running Hypothetical Scenario Analysis...")
        # What if they forced instead of saving on a lost pistol? (-1500 econ diff example)
        what_if_force = self.predictor.predict_scenario(map_name, 0, -1500, False)
        what_if_save = self.predictor.predict_scenario(map_name, 0, -3500, False) # Full save
        
        # 3. Synthesize for LLM
        context = {
            "team": team_name,
            "opponent": opponent,
            "map": map_name,
            "macro_issues": macro_agenda,
            "hypothetical_analysis": {
                "force_buy_scenario": f"Win Prob: {what_if_force['prediction_prob']:.1%} ({what_if_force['interpretation']})",
                "save_scenario": f"Win Prob: {what_if_save['prediction_prob']:.1%} ({what_if_save['interpretation']})",
                "recommendation": "Force Buy" if what_if_force['prediction_prob'] > what_if_save['prediction_prob'] else "Save"
            }
        }
        
        system_persona = f"""You are the Elite Assistant Coach for {team_name} Valorant. 
        Your advice must be extremely dynamic, data-backed, and accurate.
        Use the provided Macro Review Agenda to highlight team weaknesses (e.g., if stats show 'Negative Opening Duel Ratio', mention it).
        Use the Hypothetical Analysis to give a definitive answer on 'What If' scenarios.
        Review the JSON context and generate a cohesive, professional coaching report.
        """
        
        user_query = f"Give me a strategic review of the team's recent performance and advice on whether we should force buy more often."
        
        # Safe JSON dump
        try:
            context_str = json.dumps(context, indent=2)
        except TypeError:
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
    print(f"Macro Issues Identified: {len(result['raw_data']['macro_issues'])}")
    print(f"Hypothetical Rec: {result['raw_data']['hypothetical_analysis']['recommendation']}")
