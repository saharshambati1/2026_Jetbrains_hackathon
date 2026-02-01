import subprocess
import sys
import time
from elite_coach import EliteCoach

def run_test(script_name, description):
    print(f"\n{'='*60}")
    print(f"RUNNING: {description} ({script_name})")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True,
            check=False
        )
        duration = time.time() - start_time
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n[PASSED] {script_name} (took {duration:.2f}s)")
            return True, result.stdout
        else:
            print(f"\n[FAILED] {script_name} (Exit Code: {result.returncode})")
            print("Errors:")
            print(result.stderr)
            return False, result.stderr
            
    except Exception as e:
        print(f"\n[ERROR] Could not run {script_name}: {e}")
        return False, str(e)

def main():
    print("="*60)
    print("VERIFICATION SUITE: AI ELITE ASSISTANT COACH (CLOUD9 EDITION)")
    print("="*60)
    print("This suite validates the integration of Isolation Forest anomaly detection,")
    print("XGBoost outcome prediction, and GPT-4o contextual reasoning.\n")

    tests = [
        ("scenario_validation.py", "ML Logic Validation"),
        ("deep_tests.py", "Elite Pipeline Integration & Cloud9 Specifics"),
        ("macro_review.py", "Macro Pattern Extraction")
    ]
    
    results = []
    for script, desc in tests:
        success, output = run_test(script, desc)
        results.append((script, success))

    # Direct Elite Coach Verification
    print(f"\n{'='*60}")
    print("DIRECT ELITE COACH EXECUTION (End-to-End)")
    print(f"{'='*60}\n")
    try:
        coach = EliteCoach()
        result = coach.generate_elite_report()
        print("ELITE COACH OUTPUT ANALYSIS:")
        print(f"  Advice dynamic? {'Yes' if len(result['llm_advice']) > 50 else 'No'}")
        print(f"  Context accurate? {'Yes' if result['raw_data']['team'] == 'Cloud9' else 'No'}")
        print("-" * 30)
        print(result['llm_advice'])
        results.append(("elite_coach.py", True))
    except Exception as e:
        print(f"FAILED: elite_coach.py execution error: {e}")
        results.append(("elite_coach.py", False))

    print(f"\n\n{'='*60}")
    print("FINAL VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for script, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {script}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print(f"\n>>> SYSTEM READY FOR CLOUD9 DEPLOYMENT.")
    else:
        print(f"\n>>> SYSTEM ISSUES DETECTED. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
