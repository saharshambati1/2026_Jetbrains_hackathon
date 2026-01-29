import subprocess
import sys
import time

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
    print("Starting System Verification...")
    
    tests = [
        ("deep_tests.py", "Mistake Detector Logic & Anomaly Detection"),
        ("coach_brain.py", "LLM Coach Brain (Mock/Live)"),
        ("predictor.py", "Win Probability Predictor (XGBoost)"),
        ("macro_review.py", "Match Strategy Reviewer")
    ]
    
    results = []
    
    for script, desc in tests:
        success, output = run_test(script, desc)
        # simplified check: rely on exit codes
        results.append((script, success))
        
    print(f"\n\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for script, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {script}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print(f"\n>>> SYSTEM READY. All components functioning successfully.")
    else:
        print(f"\n>>> SYSTEM ISSUES DETECTED. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
