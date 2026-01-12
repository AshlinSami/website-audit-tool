# 🔍 Website Audit Tool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0%2B-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg)]()

A comprehensive website auditing tool that analyzes performance, SEO, accessibility, and technical health. Built by **Algorithm Agency** for professional website analysis and client reporting.

## ✨ Features

### 🔧 Technical Analysis
- ✅ **Broken Links Detection** - Identifies all broken internal and external links
- ✅ **Page Speed Analysis** - Measures load times and performance metrics
- ✅ **Redirect Chain Detection** - Finds redirect chains that slow down navigation
- ✅ **Security Headers Check** - Validates presence of essential security headers

### 📊 SEO Analysis
- ✅ **Meta Tags Validation** - Checks title tags, meta descriptions, and length
- ✅ **Heading Structure** - Analyzes H1-H6 hierarchy
- ✅ **Canonical Tags** - Verifies proper canonical implementation
- ✅ **Content Analysis** - Identifies duplicate or thin content

### ⚡ Performance Checks
- ✅ **Render-blocking Resources** - Detects CSS/JS blocking first paint
- ✅ **Resource Optimization** - Identifies large images and unoptimized assets
- ✅ **Load Time Metrics** - Measures actual page load performance

### ♿ Accessibility
- ✅ **Alt Text Validation** - Checks all images for alt attributes
- ✅ **Mobile Viewport** - Ensures proper mobile meta tags
- ✅ **Touch Target Sizes** - Identifies elements too small for mobile interaction

## 🚀 Quick Start

### Option 1: Automated Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/website-audit-tool.git
cd website-audit-tool

# Run the installer
chmod +x install.sh
./install.sh

# Run your first audit
python3 backend/website-auditor.py https://yourwebsite.com
```

### Option 2: Manual Installation
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt --break-system-packages

# Run an audit
python3 website-auditor.py https://example.com 50
```

## 📖 Usage

### Basic Audit
```bash
python3 backend/website-auditor.py https://subaru.co.za
```

### Audit with Custom Page Limit
```bash
python3 backend/website-auditor.py https://environ.co.za 100
```

## 📊 Output Example
```
============================================================
WEBSITE AUDIT REPORT
============================================================

URL: https://subaru.co.za
Date: 2025-01-12 14:30:22

SCORES:
  Overall:        72/100
  Performance:    65/100
  SEO:            85/100
  Accessibility:  70/100
  Best Practices: 78/100

STATISTICS:
  Pages Crawled:   47
  Broken Links:    7
  Redirects:       12
  External Links:  124
```

## 🏗️ Project Structure
```
website-audit-tool/
├── backend/
│   ├── website-auditor.py      # Main Python auditor
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── website-audit-tool.jsx  # React UI component
│   └── package.json            # Node dependencies
├── docs/
│   └── USAGE.md               # Detailed guide
├── .github/
│   └── workflows/
│       └── audit.yml          # GitHub Actions
├── README.md
└── install.sh
```

## 📊 Scoring System

### Overall Score (0-100)
- **90-100**: 🟢 Excellent - Few issues, well-optimized
- **70-89**: 🟡 Good - Some improvements needed
- **50-69**: 🟠 Fair - Multiple issues to address
- **0-49**: 🔴 Poor - Significant problems requiring attention

### Deductions
- **Critical Issues**: -10 points each
- **Warning Issues**: -5 points each
- **Info Issues**: -2 points each
- **Broken Links**: -3 points each (max -30)

## 🎯 Use Cases

### For Algorithm Agency Clients

**Subaru South Africa:**
```bash
python3 backend/website-auditor.py https://subaru.co.za 100
```

**Environ Skincare:**
```bash
python3 backend/website-auditor.py https://environ.co.za 75
```

### Ongoing Monitoring

Schedule regular audits with cron:
```bash
# Weekly audit every Sunday at midnight
0 0 * * 0 python3 /path/to/website-auditor.py https://client.com 50
```

## 📝 Documentation

- [Usage Guide](docs/USAGE.md) - Detailed usage instructions
- [Contributing](CONTRIBUTING.md) - How to contribute
- [GitHub Setup](GITHUB_SETUP.md) - GitHub integration guide
- [Changelog](CHANGELOG.md) - Version history

## 🔮 Roadmap

- [ ] PDF report generation with charts
- [ ] Historical tracking with trend analysis
- [ ] Email notifications for critical issues
- [ ] Lighthouse integration for Core Web Vitals
- [ ] WordPress-specific checks
- [ ] Docker support

## 👨‍💻 Authors

Built with ❤️ by the **Algorithm Agency** development team.

**Lead Developer:** Ashlin Sami  
**Company:** Algorithm Agency  
**Location:** Johannesburg, South Africa

## 📧 Support

For support: dev@algorithmagency.co.za

## 📝 License

Proprietary - Algorithm Agency © 2025

All rights reserved. This software is proprietary and confidential.

---

**Algorithm Agency** - Delivering Excellence in Digital Solutions