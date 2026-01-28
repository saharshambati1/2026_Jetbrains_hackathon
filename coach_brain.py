import os
import openai
from dotenv import load_dotenv

load_dotenv()

class CoachBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = openai.OpenAI(api_key=self.api_key)

    def ask_coach(self, system_persona, user_query, match_context=None):
        """
        Generic method to query the LLM with a specific persona and context.
        """
        messages = [
            {"role": "system", "content": system_persona},
        ]
        
        if match_context:
            messages.append({"role": "system", "content": f"MATCH CONTEXT: {match_context}"})
            
        messages.append({"role": "user", "content": user_query})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"DEBUG: LLM Error ({e}). Using Mock Response.")
            # Fallback for Demo purposes if API fails
            if "buy" in user_query.lower():
                return "Coach (Mock): Since you have 2000 credits and lost the last round, I recommend a 'Force Buy' with a Sheriff or Spectre to try and break their economy. Don't full save."
            if "aim" in user_query.lower() or "missing" in user_query.lower():
                return "Coach (Mock): Your headshot rate is low (12%). Try keeping your crosshair at head-level when turning corners. Practice 'pre-aiming' common spots on the map."
            if "map" in user_query.lower() or "corners" in user_query.lower() or "angles" in user_query.lower():
                return "Coach (Mock): On Ascent, avoid peeking Mid aggressively without utility. A good corner for your team is the Boat House in B Market."
            
            return f"Coach (Mock): Interesting question! Based on the data, I'd suggest reviewing your positioning in likely 1v1 scenarios."

    def get_buy_recommendation(self, round_num, credits, team_loadout, outcome_prev_round):
        """
        Personalized Buy Phase advice.
        """
        context = f"Round: {round_num}. Credits: {credits}. Team Loadout: {team_loadout}. Previous Round: {'Won' if outcome_prev_round else 'Lost'}."
        persona = "You are a strategic Valorant coach. Advise the player on what to buy (Eco, Force, Full Buy) and suggest specific weapons based on their economy."
        return self.ask_coach(persona, "What should I buy this round?", context)

    def get_aim_advice(self, headshot_percentage, weapon_type):
        """
        Aim and Crosshair placement advice.
        """
        context = f"Headshot %: {headshot_percentage}%. Weapon: {weapon_type}."
        persona = "You are a mechanical skills coach for Valorant. pinpoint why the player might be missing shots and give actionable advice on crosshair placement, hygiene, and counter-strafing."
        return self.ask_coach(persona, "I am missing a lot of shots. How can I improve my aim and crosshair placement?", context)

    def get_map_tips(self, map_name, key_locations):
        """
        Map knowledge: Good/Bad corners.
        """
        context = f"Map: {map_name}. Areas of trouble: {key_locations}."
        persona = "You are a map expert. Tell the player about common 'noob traps' (bad corners) and 'power positions' (good corners) on this map."
        return self.ask_coach(persona, f"What are the best angles to hold and which corners should I avoid on {map_name}?", context)

    def analyze_hypothetical(self, question, predictor_func=None):
        """
        Handles any 'What if' question, potentially using the predictor.
        """
        persona = """You are a data-driven Assistant Coach. 
        If the user asks a question about a specific game state change (e.g. 'Should we have saved?'), 
        you should formulate a hypothesis. 
        If available, use provided probability data to back up your answer.
        """
        # In a real app, we would use function calling here to invoke predictor.py
        # For now, we just pass the question to the LLM to interpret conceptually.
        return self.ask_coach(persona, question)

if __name__ == "__main__":
    coach = CoachBrain()
    
    print("--- Coach Brain Initialized ---\n")
    
    # 1. Buy Phase Advice
    print(">>> Scenario: Round 3, 2000 credits, Team is saving, Lost previous round.")
    advice = coach.get_buy_recommendation(3, 2000, "Classic/Sheriff", False)
    print(f"Coach Says: {advice}\n")
    
    # 2. Aim Advice
    print(">>> Scenario: 12% Headshot rate with Vandal.")
    advice = coach.get_aim_advice(12, "Vandal")
    print(f"Coach Says: {advice}\n")
    
    # 3. Map Tips
    print(">>> Scenario: Playing on Ascent.")
    advice = coach.get_map_tips("Ascent", "Mid Courtyard, B Main")
    print(f"Coach Says: {advice}\n")
