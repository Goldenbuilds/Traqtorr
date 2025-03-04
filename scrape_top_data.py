import requests
import pandas as pd

API_KEY = "AIzaSyCSeY8fofPevSHLPEu-62a3KxQI1EMZ2Ds"
print("Starting speed scrape...")

# Load topsites CSV
try:
    topsites_df = pd.read_csv("top_sites.csv", sep='\t')
    print(f"Loaded {len(topsites_df)} domains from topsites.csv")
    print(topsites_df.head())
except Exception as e:
    print(f"Failed to load topsites.csv: {e}")
    topsites_df = pd.DataFrame(columns=["Rank", "Domain", "Open Page Rank"])

# Load traffic data
try:
    traffic_df = pd.read_csv("site_traffic.csv")
    print("Loaded site_traffic.csv")
    if "Bounce Rate" in traffic_df.columns:
        traffic_df["Bounce Rate"] = pd.to_numeric(traffic_df["Bounce Rate"].replace('%', '', regex=True), errors='coerce') / 100
    if "Conversion Rate" in traffic_df.columns:
        traffic_df["Conversion Rate"] = pd.to_numeric(traffic_df["Conversion Rate"].replace('%', '', regex=True), errors='coerce') / 100
    avg_traffic = traffic_df["traffic_monthly"].mean()
    avg_bounce = traffic_df["Bounce Rate"].mean() if "Bounce Rate" in traffic_df.columns and traffic_df["Bounce Rate"].notna().any() else 0
    avg_conv = traffic_df["Conversion Rate"].mean() if "Conversion Rate" in traffic_df.columns and traffic_df["Conversion Rate"].notna().any() else 0
    print(f"Averages - Traffic: {avg_traffic:.2f}, Bounce: {avg_bounce:.2f}, Conv: {avg_conv:.2f}")
except Exception as e:
    print(f"Failed to load site_traffic.csv: {e}")
    avg_traffic, avg_bounce, avg_conv = 0, 0, 0

data = {
    "rank": [],
    "domain": [],
    "open_page_rank": [],
    "fcp": [],
    "lcp": [],
    "traffic": [],
    "bounce": [],
    "conv": []
}

# Scrape speed only
for _, row in topsites_df.iterrows():
    rank = row["Rank"]
    domain = row["Domain"]
    open_page_rank = row["Open Page Rank"]
    url = f"https://{domain}"
    print(f"Scraping {url} (Rank: {rank})...")

    try:
        ps_response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}", timeout=20)
        ps_data = ps_response.json()
        lighthouse = ps_data["lighthouseResult"]
        fcp = lighthouse["audits"]["first-contentful-paint"]["numericValue"] / 1000
        lcp = lighthouse["audits"]["largest-contentful-paint"]["numericValue"] / 1000
        print(f"  PageSpeed: FCP={fcp:.2f}s, LCP={lcp:.2f}s")
    except Exception as e:
        print(f"  PageSpeed failed: {e}")
        fcp, lcp = 0, 0
    
    data["rank"].append(rank)
    data["domain"].append(domain)
    data["open_page_rank"].append(open_page_rank)
    data["fcp"].append(fcp)
    data["lcp"].append(lcp)
    data["traffic"].append(avg_traffic)
    data["bounce"].append(avg_bounce)
    data["conv"].append(avg_conv)

# Save speed data
df = pd.DataFrame(data)
df.to_csv("top_site_speed.csv", index=False)  # New file
print("✅ Top site speed data saved!")