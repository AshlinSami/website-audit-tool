import requests
import json

# Test PageSpeed Insights API (free, no auth needed)
url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
params = {
    'url': 'https://example.com',
    'category': 'PERFORMANCE',
    'strategy': 'MOBILE'
}

print("Testing PageSpeed Insights API...")
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    # Extract Core Web Vitals
    lcp = data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']
    fcp = data['lighthouseResult']['audits']['first-contentful-paint']['numericValue']
    cls = data['lighthouseResult']['audits']['cumulative-layout-shift']['numericValue']
    tbt = data['lighthouseResult']['audits']['total-blocking-time']['numericValue']
    
    print(f"✅ Success!")
    print(f"LCP: {lcp/1000:.2f}s")
    print(f"FCP: {fcp/1000:.2f}s")
    print(f"CLS: {cls:.3f}")
    print(f"TBT: {tbt:.0f}ms")
else:
    print(f"❌ Error: {response.status_code}")
