import requests
import csv

API_KEY = "AIzaSyCSeY8fofPevSHLPEu-62a3KxQI1EMZ2Ds"
with open("top_sites.txt", "r") as f:
    urls = f.read().splitlines()

with open("success_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["input", "output", "metric_value"])
    for url in urls:
        data = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}").json()
        lighthouse = data["lighthouseResult"]
        fcp = lighthouse["audits"]["first-contentful-paint"]["numericValue"] / 1000
        lcp = lighthouse["audits"]["largest-contentful-paint"]["numericValue"] / 1000
        cls = lighthouse["audits"]["cumulative-layout-shift"]["numericValue"]
        writer.writerow([f"FCP on {url}", "Top sites avg 1.5s—match it or lose.", f"{fcp:.1f}"])
        writer.writerow([f"LCP on {url}", "Winners hit 2s—beat it for 20% more conversions.", f"{lcp:.1f}"])
        writer.writerow([f"CLS on {url}", "Keep it under 0.1—stable sites win.", f"{cls:.2f}"])