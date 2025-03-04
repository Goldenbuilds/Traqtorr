import pandas as pd

# Load datasets safely with proper delimiter handling
def load_csv(file_path):
    return pd.read_csv(file_path, delimiter="\t", encoding="utf-8", on_bad_lines="skip", engine="python")


# Load datasets
kaggle_df = load_csv("website_traffic.csv")
lead_df = load_csv("lead_stream.csv")
ads_df = load_csv("b_testing_ads.csv")

# Standardize column names to remove any accidental spaces or newlines
kaggle_df.columns = kaggle_df.columns.str.strip()
lead_df.columns = lead_df.columns.str.strip()
ads_df.columns = ads_df.columns.str.strip()

# Merge datasets
traffic_df = pd.concat([kaggle_df, lead_df], ignore_index=True)

# Debug column names
print("Columns in traffic_df:", list(traffic_df.columns))


# Convert Bounce Rate and Conversion Rate to float—strip % if present
if "Bounce Rate" in traffic_df.columns:
    traffic_df["Bounce Rate"] = pd.to_numeric(traffic_df["Bounce Rate"].replace('%', '', regex=True)) / 100 if traffic_df["Bounce Rate"].dtype == 'object' else traffic_df["Bounce Rate"]
if "Conversion Rate" in traffic_df.columns:
    traffic_df["Conversion Rate"] = pd.to_numeric(traffic_df["Conversion Rate"].replace('%', '', regex=True)) / 100 if traffic_df["Conversion Rate"].dtype == 'object' else traffic_df["Conversion Rate"]

# Dynamic session estimate—default to reasonable value if all else fails
if "Previous Visits" in traffic_df.columns and traffic_df["Previous Visits"].notna().any():
    avg_sessions_per_month = traffic_df["Previous Visits"].mean() * 10
elif "Page Views" in traffic_df.columns and traffic_df["Page Views"].notna().any():
    avg_sessions_per_month = traffic_df["Page Views"].mean() * 5
elif "Session Duration" in traffic_df.columns and traffic_df["Session Duration"].notna().any():
    avg_sessions_per_month = (traffic_df["Session Duration"].mean() / 60) * 3
else:
    avg_sessions_per_month = 10  # Fallback—small but realistic
print(f"Calculated avg_sessions_per_month: {avg_sessions_per_month:.2f}")

# Calculate traffic_monthly—keep variation
if "Page Views" in traffic_df.columns and traffic_df["Page Views"].notna().any():
    traffic_df["traffic_monthly"] = traffic_df["Page Views"] * avg_sessions_per_month
else:
    print("Warning: 'Page Views' missing. Using fallback.")
    traffic_df["traffic_monthly"] = avg_sessions_per_month  # Still varied if rows differ

# Traffic calc
traffic_df["traffic_monthly"] = traffic_df["Page Views"] * avg_sessions_per_month if "Page Views" in traffic_df.columns else avg_sessions_per_month

# Ad metrics
avg_converted = ads_df["converted"].mean() if "converted" in ads_df.columns and ads_df["converted"].notna().any() else 0
avg_total_ads = ads_df["total_ads"].mean() if "total_ads" in ads_df.columns and ads_df["total_ads"].notna().any() else 0
print(f"Ad metrics - avg_converted: {avg_converted:.2f}, avg_total_ads: {avg_total_ads:.2f}")


# Add ad data
traffic_df["avg_converted"] = avg_converted
traffic_df["avg_total_ads"] = avg_total_ads

# Define required columns and filter only available ones
required_columns = ["traffic_monthly", "Bounce Rate", "Conversion Rate", "avg_converted", "avg_total_ads"]
available_columns = [col for col in required_columns if col in traffic_df.columns]

if available_columns:
    output_df = traffic_df[available_columns]
    output_df.to_csv("site_traffic.csv", index=False)
    print("✅ Traffic processed successfully!")
    print(output_df.head())

else:
    print("❌ Error: No valid columns. Check dataset structure.")
    raise ValueError("No columns to export!")
