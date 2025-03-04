import pandas as pd
import os

top_data = pd.read_csv("top_site_data.csv")  # FCP, LCP, copy
kaggle_data = pd.read_csv("site_traffic.csv")  # Traffic, bounce, conv
similarweb_data = pd.read_csv("similarweb_traffic.csv")  # Real traffic, bounce
ad_data = pd.read_csv("ad_campaign.csv") if "ad_campaign.csv" in os.listdir() else pd.DataFrame(columns=["input", "output"])

# Align and merge
top_data["input"] = top_data.apply(lambda row: f"FCP: {row['fcp']:.1f}s" if row["fcp"] > 0 else f"LCP: {row['lcp']:.1f}s" if row["lcp"] > 0 else f"Headline: '{row['headline']}'" if row["headline"] else f"CTA: '{row['cta']}'", axis=1)
top_data["output"] = top_data.apply(lambda row: f"Traffic: {row['traffic']/1000000:.1f}M, Bounce: {row['bounce']:.2f}, Conv: {row['conv']:.2f}", axis=1)
ad_data["input"] = ad_data["ad_text"].apply(lambda x: f"CTA: '{x}'")
ad_data["output"] = ad_data.apply(lambda row: f"CTR: {row['ctr']:.2%}, Conv: {row['conversions']}", axis=1)

combined = pd.concat([top_data[["input", "output"]], kaggle_data[["input", "output"]], similarweb_data[["input", "output"]], ad_data[["input", "output"]]], ignore_index=True)
combined.to_csv("training_data.csv", index=False)
print("Training data saved with all datasets")