# How to Use Your Models for the Challenge

You now have a working **Introduction to the Assistant Coach**. Here is how to map what we built to the specific Challenge Prompts:

## 1. Personalized Insight Generation
**Goal:** "Analyze this player's match data and provide direct, data-backed feedback."

**Your Tool:** `mistake_detector.py`
-   **How to run:** `python mistake_detector.py`
-   **What it does:** It scans match data and uses an **Isolation Forest** to find statistical outliers (anomalies).
-   **Demo Output:**
    > "[Round 21] Score: -0.12 -> High Economy but 0 Kills and Early Death"
-   **Coach Interpretation:** "In Round 21, you had a full buy (4500 credits) but died in 10 seconds with 0 impact. This is a critical error in positioning."



## 2. Hypothetical Outcome Prediction (Implemented)
**Goal:** "Answer this 'what if' question... Would it have been better to save?"

**Your Tool:** `predictor.py`
-   **How to run:** `python predictor.py`
-   **What it does:** Trains an XGBoost model on synthetic match data to learn the impact of advantages (numbers, health, economy).
-   **Demo Output:**
    > "Scenario 1 Win Probability: 12.3%"
    > "Scenario 2 Win Probability: 45.8%"
    > "Recommendation: SAVE"



## 3. Automated Macro Review (Next Step)
**Goal:** "Generate a Game Review Agenda."

**Your Tool:** *Not yet built* (Planned: KMeans Clustering)
-   **Concept:** Cluster rounds into types (e.g., "Fast B Rush", "Slow Default").
-   **Plan:** Identify if a specific strategy (Cluster A) has a low win rate.

---

### Recommended Next Action
I can build the **Hypothetical Outcome Predictor** (XGBoost) next. This will allow you to answer questions like:
*   "Win probability if we force buy vs save?"
