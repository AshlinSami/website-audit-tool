import sys
sys.path.insert(0, '/workspaces/website-audit-tool/web-app')
from website_auditor import WebsiteAuditor

# Create auditor
auditor = WebsiteAuditor('https://www.subaru.co.za', max_pages=5)

# Manually inspect what happens
print(f"Starting crawl...")
print(f"Domain: {auditor.domain}")
print(f"Domain without www: {auditor.domain_without_www}")
print(f"Domain with www: {auditor.domain_with_www}")
print()

# Run the audit
report = auditor.run_audit()

print(f"\n\nFinal stats:")
print(f"Pages visited: {len(auditor.visited_urls)}")
print(f"Visited URLs: {auditor.visited_urls}")
print(f"External links: {len(auditor.external_links)}")
