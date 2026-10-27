import subprocess
import sys
import time

PIPELINE_STEPS = [
    ("1. Database Ingestion", "1_load_db.py"),
    ("2. Baseline Business Audit", "2_audit_baseline.py"),
    ("3. Feature Engineering & SQL Indexing", "3_feature_engineering.py"),
    ("4. Model Training & Out-of-Time Evaluation", "4_train_model.py"),
    ("5. SHAP Explainability & Summary Plot", "5_shap_analysis.py"),
]

def run():
    print("=" * 65)
    print("  OLIST DELAY PREDICTION ENGINE: END-TO-END PIPELINE")
    print("=" * 65)
    
    total_start = time.time()
    
    for step_num, (desc, script_name) in enumerate(PIPELINE_STEPS, 1):
        print(f"\n[{step_num}/{len(PIPELINE_STEPS)}] Executing: {desc} ({script_name})...")
        step_start = time.time()
        
        result = subprocess.run([sys.executable, script_name], capture_output=False)
        
        if result.returncode != 0:
            print(f"\nPipeline halted at step: {script_name} (Exit Code: {result.returncode})")
            sys.exit(result.returncode)
            
        elapsed = time.time() - step_start
        print(f"Completed {script_name} in {elapsed:.1f}s")
        
    total_time = time.time() - total_start
    print("\n" + "=" * 65)
    print(f"Complete pipeline finished successfully in {total_time:.1f}s!")
    print("=" * 65)

if __name__ == "__main__":
    run()