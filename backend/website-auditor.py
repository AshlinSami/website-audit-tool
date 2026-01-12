#!/usr/bin/env python3
"""
Website Audit Tool - Algorithm Agency
Comprehensive website analysis tool for performance, SEO, accessibility, and technical health
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from datetime import datetime
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class WebsiteAuditor:
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited_urls = set()
        self.all_links = set()
        self.broken_links = []
        self.redirects = []
        self.external_links = set()
        self.pages_data = []
        self.issues = {
            'critical': [],
            'warnings': [],
            'info': []
        }
        
    def fetch_page(self, url):
        """Fetch a page and return response"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Website Audit Tool) Algorithm Agency'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            return response
        except Exception as e:
            return None
    
    def analyze_page_speed(self, url, response):
        """Analyze page load time and resource sizes"""
        start_time = time.time()
        content_size = len(response.content)
        load_time = time.time() - start_time
        
        return {
            'url': url,
            'load_time': round(load_time, 2),
            'content_size': content_size,
            'status_code': response.status_code
        }
    
    def check_seo_elements(self, soup, url):
        """Check for SEO-related elements"""
        seo_issues = []
        
        # Check title
        title = soup.find('title')
        if not title or not title.string:
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'Missing page title',
                'url': url
            })
        elif len(title.string) > 60:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Page title too long',
                'url': url,
                'details': f'Title length: {len(title.string)} characters (recommended: <60)'
            })
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'Missing meta description',
                'url': url
            })
        
        # Check H1 tags
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'No H1 tag found',
                'url': url
            })
        elif len(h1_tags) > 1:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Multiple H1 tags',
                'url': url,
                'details': f'Found {len(h1_tags)} H1 tags'
            })
        
        # Check for canonical tag
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Missing canonical tag',
                'url': url
            })
        
        return seo_issues
    
    def check_images(self, soup, url):
        """Check image optimization and alt tags"""
        image_issues = []
        images = soup.find_all('img')
        
        missing_alt = 0
        for img in images:
            if not img.get('alt'):
                missing_alt += 1
        
        if missing_alt > 0:
            image_issues.append({
                'type': 'warning',
                'category': 'Accessibility',
                'title': 'Images missing alt attributes',
                'url': url,
                'details': f'{missing_alt} images without alt text'
            })
        
        return image_issues
    
    def check_security_headers(self, response):
        """Check for security headers"""
        security_issues = []
        headers = response.headers
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None
        }
        
        for header, expected_value in required_headers.items():
            if header not in headers:
                security_issues.append({
                    'type': 'critical',
                    'category': 'Security',
                    'title': f'Missing security header: {header}',
                    'recommendation': f'Add {header} header to server configuration'
                })
        
        return security_issues
    
    def check_mobile_viewport(self, soup, url):
        """Check for mobile viewport meta tag"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            return [{
                'type': 'warning',
                'category': 'Mobile',
                'title': 'Missing viewport meta tag',
                'url': url,
                'recommendation': 'Add <meta name="viewport" content="width=device-width, initial-scale=1">'
            }]
        return []
    
    def check_render_blocking_resources(self, soup, url):
        """Check for render-blocking CSS and JS"""
        blocking_issues = []
        
        # Check for CSS in head without media or async
        css_links = soup.find_all('link', attrs={'rel': 'stylesheet'})
        blocking_css = [link for link in css_links if not link.get('media')]
        
        if len(blocking_css) > 2:
            blocking_issues.append({
                'type': 'critical',
                'category': 'Performance',
                'title': 'Multiple render-blocking CSS files',
                'url': url,
                'details': f'{len(blocking_css)} CSS files blocking render',
                'recommendation': 'Consider inlining critical CSS and deferring non-critical styles'
            })
        
        # Check for JS without async/defer
        scripts = soup.find_all('script', src=True)
        blocking_scripts = [s for s in scripts if not s.get('async') and not s.get('defer')]
        
        if len(blocking_scripts) > 1:
            blocking_issues.append({
                'type': 'critical',
                'category': 'Performance',
                'title': 'Render-blocking JavaScript',
                'url': url,
                'details': f'{len(blocking_scripts)} scripts without async/defer',
                'recommendation': 'Add async or defer attributes to script tags'
            })
        
        return blocking_issues
    
    def crawl_page(self, url):
        """Crawl a single page and extract information"""
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return
        
        print(f"Crawling: {url}")
        self.visited_urls.add(url)
        
        response = self.fetch_page(url)
        if not response:
            self.broken_links.append({'url': url, 'status': 'Failed to fetch'})
            return
        
        # Check for redirects
        if response.history:
            self.redirects.append({
                'from': url,
                'to': response.url,
                'status_codes': [r.status_code for r in response.history]
            })
        
        # Check status code
        if response.status_code >= 400:
            self.broken_links.append({'url': url, 'status': response.status_code})
            return
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Analyze page
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'speed': self.analyze_page_speed(url, response)
        }
        self.pages_data.append(page_data)
        
        # Check various elements
        self.issues['warnings'].extend(self.check_seo_elements(soup, url))
        self.issues['warnings'].extend(self.check_images(soup, url))
        self.issues['critical'].extend(self.check_security_headers(response))
        self.issues['warnings'].extend(self.check_mobile_viewport(soup, url))
        self.issues['critical'].extend(self.check_render_blocking_resources(soup, url))
        
        # Extract all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            
            # Skip anchors and javascript
            if parsed.fragment or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            self.all_links.add(full_url)
            
            # Check if internal or external
            if parsed.netloc == self.domain or not parsed.netloc:
                # Internal link - add to crawl queue
                if full_url not in self.visited_urls:
                    self.crawl_page(full_url)
            else:
                # External link
                self.external_links.add(full_url)
    
    def check_broken_links(self):
        """Check all found links for broken ones"""
        print("\nChecking for broken links...")
        checked = set()
        
        for link in list(self.all_links)[:50]:  # Limit checking to avoid long runtime
            if link in checked or link in self.visited_urls:
                continue
            
            checked.add(link)
            response = self.fetch_page(link)
            
            if not response or response.status_code >= 400:
                status = response.status_code if response else 'Failed'
                self.broken_links.append({'url': link, 'status': status})
    
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Broken links recommendation
        if len(self.broken_links) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Broken Links',
                'title': f'{len(self.broken_links)} broken links found',
                'description': 'Multiple pages are linking to non-existent resources',
                'affected_count': len(self.broken_links),
                'recommendation': 'Update or remove broken links. Set up proper 301 redirects for moved content.'
            })
        
        # Group issues by category
        issue_counts = defaultdict(int)
        for issue_list in self.issues.values():
            for issue in issue_list:
                issue_counts[issue['category']] += 1
        
        # SEO recommendations
        if issue_counts['SEO'] > 0:
            recommendations.append({
                'priority': 'warning',
                'category': 'SEO',
                'title': f'{issue_counts["SEO"]} SEO issues found',
                'description': 'Missing or suboptimal meta tags and heading structure',
                'affected_count': issue_counts['SEO'],
                'recommendation': 'Add unique meta descriptions, optimize title tags, ensure proper heading hierarchy'
            })
        
        # Performance recommendations
        if issue_counts['Performance'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Performance',
                'title': f'{issue_counts["Performance"]} performance issues found',
                'description': 'Render-blocking resources detected',
                'affected_count': issue_counts['Performance'],
                'recommendation': 'Defer non-critical CSS/JS, optimize resource loading, implement lazy loading'
            })
        
        # Security recommendations
        if issue_counts['Security'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Security',
                'title': f'{issue_counts["Security"]} security issues found',
                'description': 'Missing security headers',
                'affected_count': issue_counts['Security'],
                'recommendation': 'Configure server to include security headers: X-Content-Type-Options, X-Frame-Options, CSP'
            })
        
        return recommendations
    
    def calculate_score(self):
        """Calculate overall score based on issues"""
        base_score = 100
        
        # Deduct points for issues
        critical_deduction = len([i for lst in self.issues.values() for i in lst if i.get('type') == 'critical']) * 10
        warning_deduction = len([i for lst in self.issues.values() for i in lst if i.get('type') == 'warning']) * 5
        info_deduction = len([i for lst in self.issues.values() for i in lst if i.get('type') == 'info']) * 2
        
        # Deduct for broken links
        broken_deduction = min(len(self.broken_links) * 3, 30)
        
        final_score = max(0, base_score - critical_deduction - warning_deduction - info_deduction - broken_deduction)
        
        return {
            'overall': final_score,
            'performance': max(0, 100 - critical_deduction - warning_deduction),
            'seo': max(0, 100 - len([i for lst in self.issues.values() for i in lst if i.get('category') == 'SEO']) * 8),
            'accessibility': max(0, 100 - len([i for lst in self.issues.values() for i in lst if i.get('category') == 'Accessibility']) * 10),
            'bestPractices': max(0, 100 - broken_deduction - len([i for lst in self.issues.values() for i in lst if i.get('category') == 'Security']) * 8)
        }
    
    def run_audit(self):
        """Run complete audit"""
        print(f"\n{'='*60}")
        print(f"Starting Website Audit for: {self.base_url}")
        print(f"{'='*60}\n")
        
        # Crawl website
        self.crawl_page(self.base_url)
        
        # Check broken links
        self.check_broken_links()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Calculate scores
        scores = self.calculate_score()
        
        # Prepare report
        report = {
            'url': self.base_url,
            'timestamp': datetime.now().isoformat(),
            'scores': scores,
            'statistics': {
                'total_pages': len(self.visited_urls),
                'broken_links': len(self.broken_links),
                'redirects': len(self.redirects),
                'external_links': len(self.external_links)
            },
            'recommendations': recommendations,
            'broken_links': self.broken_links[:20],  # Limit to first 20
            'page_speeds': [page['speed'] for page in self.pages_data[:10]]
        }
        
        return report
    
    def print_report(self, report):
        """Print formatted report to console"""
        print(f"\n{'='*60}")
        print("WEBSITE AUDIT REPORT")
        print(f"{'='*60}\n")
        print(f"URL: {report['url']}")
        print(f"Date: {datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("SCORES:")
        print(f"  Overall:        {report['scores']['overall']}/100")
        print(f"  Performance:    {report['scores']['performance']}/100")
        print(f"  SEO:            {report['scores']['seo']}/100")
        print(f"  Accessibility:  {report['scores']['accessibility']}/100")
        print(f"  Best Practices: {report['scores']['bestPractices']}/100\n")
        
        print("STATISTICS:")
        print(f"  Pages Crawled:   {report['statistics']['total_pages']}")
        print(f"  Broken Links:    {report['statistics']['broken_links']}")
        print(f"  Redirects:       {report['statistics']['redirects']}")
        print(f"  External Links:  {report['statistics']['external_links']}\n")
        
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            priority_marker = "🔴" if rec['priority'] == 'critical' else "🟡"
            print(f"\n  {priority_marker} {i}. [{rec['category']}] {rec['title']}")
            print(f"     {rec['description']}")
            print(f"     → {rec['recommendation']}")
        
        if report['broken_links']:
            print(f"\n\nBROKEN LINKS (showing first 20):")
            for link in report['broken_links']:
                print(f"  ✗ {link['url']} (Status: {link['status']})")
        
        print(f"\n{'='*60}\n")
    
    def save_report(self, report, filename='audit-report.json'):
        """Save report to JSON file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {filename}")


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python website-auditor.py <url> [max_pages]")
        print("Example: python website-auditor.py https://example.com 50")
        sys.exit(1)
    
    url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    auditor = WebsiteAuditor(url, max_pages=max_pages)
    report = auditor.run_audit()
    auditor.print_report(report)
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"audit-report-{timestamp}.json"
    auditor.save_report(report, filename)


if __name__ == "__main__":
    main()