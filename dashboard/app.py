import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Page Title and Layout
st.set_page_config(page_title="Traffic Accident Severity Dashboard", layout="wide")

st.title("Traffic Accident Severity Dashboard")
st.markdown(
    "Analyze when accident severity becomes high based on time, weather, and road conditions."
)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Load data
df = pd.read_csv(DATA_PROCESSED / "accidents_cleaned.csv")

df["year"] = df["year"].astype("Int64")

# Filters
st.sidebar.header("Filters")

# Year filter
years = sorted(df["year"].dropna().astype(int).unique())
selected_year = st.sidebar.selectbox("Select Year", years, key="year_filter")

# Weather filter
weather_options = df["weather_group"].dropna().unique()
selected_weather = st.sidebar.multiselect(
    "Select Weather",
    options=weather_options,
    default=weather_options,
    key="weather_filter",
)

# Nightfilter
night_option = st.sidebar.selectbox(
    "Night Condition", ["All", "Night Only", "Day Only"], key="night_filter"
)

filtered_df = df.copy()

# Year filter
filtered_df = filtered_df[filtered_df["year"] == selected_year]

# Weather filter
filtered_df = filtered_df[filtered_df["weather_group"].isin(selected_weather)]

# Night filter
if night_option == "Night Only":
    filtered_df = filtered_df[filtered_df["night"] == 1]
elif night_option == "Day Only":
    filtered_df = filtered_df[filtered_df["night"] == 0]

# Top KPIs
high_severity_rate = filtered_df["high_severity"].mean()
avg_visibility = filtered_df["Visibility(mi)"].mean()
night_rate = filtered_df["night"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Accidents", f"{len(filtered_df):,}")
col2.metric("High Severity Rate", f"{high_severity_rate:.2%}")
col3.metric("Average Visibility", f"{avg_visibility:.2f} mi")
col4.metric("Night Accident Share", f"{night_rate:.2%}")

# Risk Chart: severity risk by hour
st.subheader("Risk by Hour")

risk_by_hour = filtered_df.groupby("hour")["high_severity"].mean()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(risk_by_hour.index, risk_by_hour.values)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("High Severity Risk")
ax.set_title("Probability of High Severity by Hour")

st.pyplot(fig)

# Risk Chart: severity risk by weather
st.subheader("Risk by Weather Group")

risk_by_weather = (
    filtered_df.groupby("weather_group")["high_severity"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(risk_by_weather.index, risk_by_weather.values)
ax.set_xlabel("Weather Group")
ax.set_ylabel("High Severity Risk")
ax.set_title("Probability of High Severity by Weather Group")
plt.xticks(rotation=45)

st.pyplot(fig)

baseline_risk = filtered_df["high_severity"].mean()
st.markdown(f"**Baseline Risk:** {baseline_risk:.2%}")

# Risk vs Baseline table
st.subheader("Risk vs Baseline (Deviation)")

baseline_risk = filtered_df["high_severity"].mean()

risk_weather = (
    filtered_df.groupby("weather_group")["high_severity"]
    .mean()
    .sort_values(ascending=False)
)

risk_diff = risk_weather - baseline_risk

risk_df = (
    pd.DataFrame({"Risk": risk_weather, "Difference from Baseline": risk_diff})
    .sort_values("Difference from Baseline", ascending=False)
    .reset_index()
)

risk_df = risk_df.rename(columns={"weather_group": "Weather Group"})
risk_df.insert(0, "Sr. No.", range(1, len(risk_df) + 1))

st.dataframe(risk_df, width="stretch", hide_index=True)

# Top High-Risk Scenarios table with labels
st.subheader("Top High-Risk Scenarios")

scenario_risk = (
    filtered_df.groupby(["night", "adverse_weather", "peak_hour"])["high_severity"]
    .mean()
    .reset_index()
    .sort_values(by="high_severity", ascending=False)
    .reset_index(drop=True)
)

scenario_risk["night"] = scenario_risk["night"].map({0: "No", 1: "Yes"})
scenario_risk["adverse_weather"] = scenario_risk["adverse_weather"].map(
    {0: "No", 1: "Yes"}
)
scenario_risk["peak_hour"] = scenario_risk["peak_hour"].map({0: "No", 1: "Yes"})
scenario_risk = scenario_risk.rename(columns={"high_severity": "Risk"})
scenario_risk.insert(0, "Sr. No.", range(1, len(scenario_risk) + 1))

st.dataframe(scenario_risk, width="stretch", hide_index=True)

# Highest risk scenario box
st.subheader("Highest Risk Scenario")

top_scenario = scenario_risk.iloc[0]

st.success(
    f"Highest risk occurs when:\n\n"
    f"- Night: {top_scenario['night']}\n"
    f"- Adverse Weather: {top_scenario['adverse_weather']}\n"
    f"- Peak Hour: {top_scenario['peak_hour']}\n\n"
    f"Risk: {top_scenario['Risk']:.2%}"
)

# Interpretation
st.subheader("Interpretation")

st.warning(
    "Severity risk is not driven by single factors alone.\n\n"
    "Combined conditions such as night and adverse weather significantly increase the likelihood of severe accidents.\n\n"
    "This suggests that risk mitigation strategies should focus on high-risk scenarios rather than individual conditions."
)
