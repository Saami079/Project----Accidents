import pandas as pd
import numpy as np
from pathlib import Path

# 1. Paths

base_dir = Path(r"D:\Data Analysis\Project  - Accidents")
raw_file = base_dir / "data" / "raw" / "accidents_raw.csv"

cleaned_file = base_dir / "data" / "processed" / "accidents_cleaned.csv"
location_file = base_dir / "data" / "processed" / "accidents_location_valid.csv"

severity_file = base_dir / "outputs" / "tables" / "severity_distribution.csv"
weather_file = base_dir / "outputs" / "tables" / "weather_risk_summary.csv"
night_file = base_dir / "outputs" / "tables" / "night_risk_summary.csv"
peak_file = base_dir / "outputs" / "tables" / "peak_risk_summary.csv"


# 2. Load data

df = pd.read_csv(raw_file, nrows=300000)


# 3. Keep required columns

df = df[
    [
        "Severity",
        "Start_Time",
        "Start_Lat",
        "Start_Lng",
        "Weather_Condition",
        "Visibility(mi)",
        "Junction",
        "Traffic_Signal"
    ]
].copy()


# 4. Clean missing values

df = df.dropna(subset=["Severity", "Start_Time"])

df["Weather_Condition"] = df["Weather_Condition"].fillna("Unknown")

df["Visibility(mi)"] = pd.to_numeric(df["Visibility(mi)"], errors="coerce")
df["Visibility(mi)"] = df["Visibility(mi)"].fillna(df["Visibility(mi)"].median())


# 5. Convert data types

df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
df["Severity"] = pd.to_numeric(df["Severity"], errors="coerce")

df = df.dropna(subset=["Start_Time", "Severity"])


# 6. Filter years

df["year"] = df["Start_Time"].dt.year
df = df[(df["year"] >= 2019) & (df["year"] <= 2023)].copy()


# 7. Create time features

df["hour"] = df["Start_Time"].dt.hour
df["day_of_week"] = df["Start_Time"].dt.dayofweek
df["month"] = df["Start_Time"].dt.month


# 8. Create target variable

df["high_severity"] = np.where(df["Severity"] >= 3, 1, 0)


# 9. Create derived features

df["night"] = df["hour"].apply(lambda x: 1 if x >= 19 or x <= 6 else 0)
df["peak_hour"] = df["hour"].apply(lambda x: 1 if (7 <= x <= 10) or (16 <= x <= 19) else 0)


# 10. Simplify weather

def simplify_weather(x):
    x = str(x).lower()

    if "rain" in x or "drizzle" in x or "shower" in x:
        return "Rain"
    elif "fog" in x or "mist" in x or "haze" in x:
        return "Fog"
    elif "snow" in x or "ice" in x or "sleet" in x:
        return "Snow/Ice"
    elif "storm" in x or "thunder" in x:
        return "Storm"
    elif "clear" in x or "fair" in x or "sunny" in x:
        return "Clear"
    elif "cloud" in x or "overcast" in x:
        return "Cloudy"
    else:
        return "Other"


df["weather_group"] = df["Weather_Condition"].apply(simplify_weather)
df["adverse_weather"] = df["weather_group"].apply(
    lambda x: 1 if x in ["Rain", "Fog", "Snow/Ice", "Storm"] else 0
)


# 11. Create location-valid subset

location_df = df.dropna(subset=["Start_Lat", "Start_Lng"]).copy()


# 12. Create summary tables

severity_distribution = df["Severity"].value_counts().sort_index().reset_index()
severity_distribution.columns = ["Severity", "Count"]

weather_risk = (
    df.groupby("weather_group")["high_severity"]
    .agg(["count", "mean"])
    .reset_index()
)
weather_risk.columns = ["weather_group", "count", "high_severity_rate"]
weather_risk = weather_risk.sort_values("high_severity_rate", ascending=False)

night_risk = (
    df.groupby("night")["high_severity"]
    .agg(["count", "mean"])
    .reset_index()
)
night_risk["night"] = night_risk["night"].replace({0: "Day", 1: "Night"})
night_risk.columns = ["time_period", "count", "high_severity_rate"]

peak_risk = (
    df.groupby("peak_hour")["high_severity"]
    .agg(["count", "mean"])
    .reset_index()
)
peak_risk["peak_hour"] = peak_risk["peak_hour"].replace({0: "Non-Peak", 1: "Peak"})
peak_risk.columns = ["peak_period", "count", "high_severity_rate"]


# 13. Save outputs

df.to_csv(cleaned_file, index=False)
location_df.to_csv(location_file, index=False)

severity_distribution.to_csv(severity_file, index=False)
weather_risk.to_csv(weather_file, index=False)
night_risk.to_csv(night_file, index=False)
peak_risk.to_csv(peak_file, index=False)


# 14. Print final results

print("Final shape:", df.shape)

print("\nSeverity distribution:")
print(severity_distribution)

print("\nHigh severity distribution:")
print(df["high_severity"].value_counts())

print("\nWeather risk summary:")
print(weather_risk)

print("\nNight risk summary:")
print(night_risk)

print("\nPeak hour risk summary:")
print(peak_risk)

print("STEP 0 - After loading:", df.shape)
print(df.head(3))

df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")

print("\nSTEP 1 - After datetime conversion")
print("Shape:", df.shape)
print("Null Start_Time:", df["Start_Time"].isna().sum())
print("Sample parsed time:")
print(df["Start_Time"].head())

df = df.dropna(subset=["Start_Time"])

print("\nSTEP 2 - After dropping invalid Start_Time")
print("Shape:", df.shape)

df["year"] = df["Start_Time"].dt.year

print("\nSTEP 3 - Year distribution")
print(df["year"].value_counts(dropna=False).sort_index())
print("Min year:", df["year"].min())
print("Max year:", df["year"].max())

print("\nSTEP 4 - Before filtering")
print("Shape:", df.shape)

df = df[df["year"].between(2019, 2023)]

print("\nSTEP 5 - After filtering 2019–2023")
print("Shape:", df.shape)
print(df["year"].value_counts().sort_index())

file_path = r"D:\Data Analysis\Project  - Accidents\data\raw\accidents.csv"
print("Loading file from:", file_path)

df = pd.read_csv(file_path)

print("Loaded shape:", df.shape)
print(df.head(3))
print(df.columns.tolist())
