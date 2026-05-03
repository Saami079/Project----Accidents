import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(r"D:\Data Analysis\Project - Accidents")
input_file = PROJECT_ROOT / "data" / "processed" / "accidents_cleaned.csv"
output_file = PROJECT_ROOT / "data" / "processed" / "dashboard_sample.csv"

df = pd.read_csv(input_file)
dashboard_df = df.sample(n=50000, random_state=42)
dashboard_df.to_csv(output_file, index=False)

print(output_file)
print(dashboard_df.shape)
