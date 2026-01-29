import os
import openai
from dotenv import load_dotenv

load_dotenv()

class CoachBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.mock_mode = False
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY not found. Running in MOCK MODE.")
            self.mock_mode = True
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)

    def ask_coach(self, system_persona, user_query, match_context=None, data_evidence=None):
        """
        Generic method to query the LLM with a specific persona and context.
        """
        messages = [
            {"role": "system", "content": system_persona},
        ]
        
        if match_context:
            messages.append({"role": "system", "content": f"MATCH CONTEXT: {match_context}"})
        
        if data_evidence:
            messages.append({"role": "system", "content": f"HARD DATA EVIDENCE: {data_evidence}"})
            
        messages.append({"role": "user", "content": user_query})

        if self.mock_mode:
            return self._mock_data_backed_response(user_query, data_evidence)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=messages,
                max_tokens=400,
                temperature=0.3 # Lower temperature for better data fidelity
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"DEBUG: LLM Error ({e}). Using Enhanced Mock Response.")
            return self._mock_data_backed_response(user_query, data_evidence)

    def _mock_data_backed_response(self, query, evidence):
        # Fallback that simulates data-driven reasoning
        evidence_str = f" (Based on: {evidence})" if evidence else ""
        return f"Coach (Data-Driven Mock): Looking at the numbers{evidence_str}, the high-impact play here involves adjusting your positioning. Our models suggest this is a recurring pattern with a High confidence tier."

    def analyze_mistake(self, mistake_row):
        """
        Explains a specific mistake flagged by MistakeDetector.
        """
        context = f"Event: {mistake_row['event_type']}. Score: {mistake_row['anomaly_score']:.2f}."
        evidence = f"Dist: {mistake_row['teammate_dist']}m, Util: {mistake_row['util']}, Explanation: {mistake_row['explanation']}"
        persona = """You are a Valorant Strategy Coach. Explain the mistake clearly. 
        Connect the micro-action (e.g. overextending) to the macro result (round loss). 
        Always mention the 'hard data' provided in your explanation."""
        return self.ask_coach(persona, "Why was this flagged as a mistake?", context, evidence)

    def explain_prediction(self, scenario_name, prediction_data):
        """
        Explains an XGBoost prediction with transparency tiers.
        """
        context = f"Scenario: {scenario_name}"
        evidence = (f"Predicted Win %: {prediction_data['prediction_prob']:.1%}, "
                   f"Historical Context: {prediction_data['historical_win_rate']:.1%}, "
                   f"Sample Size: {prediction_data['sample_size']}, "
                   f"Confidence: {prediction_data['confidence_tier']}")
        
        persona = """You are a Performance Analyst. Explain the win probability for this 'What If' scenario. 
        Be transparent about the confidence level and sample size. If confidence is 'Low', advise caution."""
        
        return self.ask_coach(persona, "Should we have made this choice?", context, evidence)

if __name__ == "__main__":
    coach = CoachBrain()
    
    print("--- Coach Brain (Data-Driven Mode) ---\n")
    
    # 1. Explaining a Prediction (XGBoost Result)
    prediction_data = {
        "prediction_prob": 0.147,
        "historical_win_rate": 0.12,
        "sample_size": 132,
        "confidence_tier": "High"
    }
    
    print(">>> Scenario: 3v5 Retake on Haven")
    advice = coach.explain_prediction("3v5 Retake Attempt", prediction_data)
    print(f"Coach Says:\n{advice}\n")
    
    # 2. Explaining a Mistake (Isolation Forest Result)
    mistake_data = {
        "event_type": "Opening Duel",
        "anomaly_score": -0.45,
        "teammate_dist": 45,
        "util": 0,
        "explanation": "Overextended & Dry-peeking"
    }
    print(">>> Mistake: Overextended Duel")
    explanation = coach.analyze_mistake(mistake_data)
    print(f"Coach Says:\n{explanation}\n")
