# Usage Guide

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Understanding Reports](#understanding-reports)
- [Best Practices](#best-practices)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Node.js 16+ (for frontend only)

### Quick Install
```bash
git clone https://github.com/algorithm-agency/website-audit-tool.git
cd website-audit-tool
chmod +x install.sh
./install.sh
```

### Manual Install
```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages

# Frontend (optional)
cd ../frontend
npm install
```

## Basic Usage

### Run Your First Audit
```bash
python3 backend/website-auditor.py https://example.com
```

### Specify Page Limit
```bash
python3 backend/website-auditor.py https://example.com 100
```

### Output Location
Reports are saved in the `backend/` directory with format:
```
audit-report-YYYYMMDD_HHMMSS.json
```

## Advanced Usage

### Python Script Integration
```python
from website_auditor import WebsiteAuditor

# Create auditor instance
auditor = WebsiteAuditor('https://example.com', max_pages=100)

# Run audit
report = auditor.run_audit()

# Access results
print(f"Overall Score: {report['scores']['overall']}")
print(f"Broken Links: {len(report['broken_links'])}")

# Save custom report
auditor.save_report(report, 'custom-report.json')
```

### Batch Auditing
```python
import json
from datetime import datetime

sites = [
    'https://subaru.co.za',
    'https://environ.co.za',
    'https://client1.com',
    'https://client2.com'
]

all_reports = []

for site in sites:
    print(f"Auditing {site}...")
    auditor = WebsiteAuditor(site, max_pages=50)
    report = auditor.run_audit()
    all_reports.append(report)

# Save combined report
with open(f'batch-report-{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
    json.dump(all_reports, f, indent=2)
```

### Scheduled Audits (Cron)
```bash
# Edit crontab
crontab -e

# Add weekly audit (every Sunday at 2 AM)
0 2 * * 0 /usr/bin/python3 /path/to/backend/website-auditor.py https://yoursite.com 50

# Add daily audit
0 2 * * * /usr/bin/python3 /path/to/backend/website-auditor.py https://yoursite.com 50

# Add monthly audit (1st of month)
0 2 1 * * /usr/bin/python3 /path/to/backend/website-auditor.py https://yoursite.com 100
```

## Understanding Reports

### Score Interpretation

**Overall Score (0-100)**
- **90-100**: Excellent - Site is well-optimized
- **70-89**: Good - Minor improvements needed
- **50-69**: Fair - Several issues to address
- **0-49**: Poor - Requires immediate attention

**Category Scores**
- **Performance**: Page speed, render-blocking resources
- **SEO**: Meta tags, structure, content optimization
- **Accessibility**: Alt tags, mobile viewport, touch targets
- **Best Practices**: Security headers, broken links, redirects

### Issue Priorities

**Critical** 🔴
- Security vulnerabilities
- Broken functionality
- Major performance issues
- Immediate attention required

**Warning** 🟡
- SEO issues
- Missing meta tags
- Unoptimized images
- Should be addressed soon

**Info** 🔵
- Minor optimizations
- Best practice suggestions
- Nice-to-have improvements

## Best Practices

### For Client Audits

1. **Initial Assessment**
```bash
   # Run comprehensive audit
   python3 backend/website-auditor.py https://client.com 100
```

2. **Pre-Launch Check**
```bash
   # Audit staging site
   python3 backend/website-auditor.py https://staging.client.com 50
```

3. **Monthly Monitoring**
```bash
   # Schedule regular audits
   0 0 1 * * python3 /path/to/website-auditor.py https://client.com 50
```

### Optimal Page Limits

- **Small site (< 50 pages)**: Use 50-100 page limit
- **Medium site (50-500 pages)**: Use 100-200 page limit
- **Large site (> 500 pages)**: Use 200+ page limit or sample key pages

## Troubleshooting

### Common Issues

**"Connection timeout"**
```bash
# Increase timeout in code
response = requests.get(url, timeout=20)  # Default is 10
```

**"SSL Certificate Error"**
```bash
# Already handled with verify=False in production
# For staging sites, this is normal
```

**"Memory error"**
```bash
# Reduce max_pages
python3 website-auditor.py https://site.com 25
```

## Examples

### Algorithm Agency Workflow
```bash
# Monday: Audit main clients
python3 backend/website-auditor.py https://subaru.co.za 100
python3 backend/website-auditor.py https://environ.co.za 75
```

---

For more information, see the main [README](../README.md)