import pandas as pd
from pathlib import Path
import sys

# 1. DYNAMIC PATHING
# This sets the root based on the script location, avoiding "D:\" hardcoding issues
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent 

# Alternatively, keep your hardcoded path but use the 'r' prefix correctly:
# PROJECT_ROOT = Path(r"D:\Data Analysis\Project - Accidents")

# 2. DEFINE PATHS
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "accidents_cleaned.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "dashboard_sample.csv"

def generate_sample(n_samples=50000):
    try:
        # 3. VALIDATION
        if not INPUT_FILE.exists():
            raise FileNotFoundError(f"Could not find: {INPUT_FILE}\nCheck for double spaces in folder names!")

        print(f"Reading data from: {INPUT_FILE}...")
        df = pd.read_csv(INPUT_FILE)

        # 4. SAMPLING LOGIC
        # Ensure we don't try to sample more rows than exist
        actual_n = min(n_samples, len(df))
        dashboard_df = df.sample(n=actual_n, random_state=42)

        # 5. SAFE EXPORT
        # Create 'processed' directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        dashboard_df.to_csv(OUTPUT_FILE, index=False)
        
        print("-" * 30)
        print(f"Success! Sample saved to: {OUTPUT_FILE}")
        print(f"Sample Shape: {dashboard_df.shape}")
        print("-" * 30)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_sample(50000)

