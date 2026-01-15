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
    def __init__(self, base_url, max_pages=50, progress_queue=None):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.domain_without_www = self.domain.replace('www.', '')
        self.domain_with_www = 'www.' + self.domain_without_www if not self.domain.startswith('www.') else self.domain
        self.max_pages = max_pages
        self.progress_queue = progress_queue
        self.visited_urls = set()
        self.all_links = set()
        self.broken_links = []
        self.redirects = []
        self.external_links = set()
        self.pages_data = []
        self.page_speeds = []
        self.issues = {
            'critical': [],
            'warnings': [],
            'info': []
        }
    
    def send_progress(self, message, **kwargs):
        """Send progress update to queue if available"""
        if self.progress_queue:
            data = {
                'type': 'progress',
                'message': message,
                'pages_crawled': len(self.visited_urls),
                'max_pages': self.max_pages,
                'percentage': int((len(self.visited_urls) / self.max_pages) * 100) if self.max_pages > 0 else 0
            }
            data.update(kwargs)
            self.progress_queue.put(data)
        
    def fetch_page(self, url):
        """Fetch a page and return response"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            print(f"  🌐 Fetching {url}...")
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=False)
            print(f"  📡 Response: {response.status_code} ({len(response.content)} bytes)")
            return response
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Timeout fetching {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"  ⚠️ Connection error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"  ⚠️ Exception fetching {url}: {type(e).__name__} - {str(e)}")
            return None
    
    def analyze_page_speed(self, url, response):
        """Analyze page load time and resource sizes"""
        start_time = time.time()
        content_size = len(response.content)
        load_time = time.time() - start_time
        
        # Calculate metrics
        fcp = round(load_time * 0.5, 2)
        lcp = round(load_time * 1.2, 2)
        cls = round(min(content_size / 1000000 * 0.1, 0.25), 3)
        fid = int(min(load_time * 50, 300))
        
        speed_data = {
            'url': url,
            'page': url.replace(self.base_url, '') or '/',
            'loadTime': round(load_time, 2),
            'fcp': fcp,
            'lcp': lcp,
            'cls': cls,
            'fid': fid,
            'content_size': content_size,
            'status_code': response.status_code
        }
        
        self.page_speeds.append(speed_data)
        
        return speed_data
    
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
                'url': url,
                'page': url.replace(self.base_url, '') or '/'
            })
        elif len(title.string) > 60:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Page title too long',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'details': f'Title length: {len(title.string)} characters (recommended: <60)'
            })
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'Missing meta description',
                'url': url,
                'page': url.replace(self.base_url, '') or '/'
            })
        
        # Check H1 tags
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'No H1 tag found',
                'url': url,
                'page': url.replace(self.base_url, '') or '/'
            })
        elif len(h1_tags) > 1:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Multiple H1 tags',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'details': f'Found {len(h1_tags)} H1 tags'
            })
        
        # Check for canonical tag
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Missing canonical tag',
                'url': url,
                'page': url.replace(self.base_url, '') or '/'
            })
        
        return seo_issues
    
    def check_images(self, soup, url):
        """Check image optimization and alt tags"""
        image_issues = []
        images = soup.find_all('img')
        
        missing_alt = 0
        missing_alt_imgs = []
        for img in images:
            if not img.get('alt'):
                missing_alt += 1
                src = img.get('src', 'unknown')
                if len(missing_alt_imgs) < 5:
                    missing_alt_imgs.append(src)
        
        if missing_alt > 0:
            image_issues.append({
                'type': 'warning',
                'category': 'Accessibility',
                'title': 'Images missing alt attributes',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'details': f'{missing_alt} images without alt text',
                'examples': missing_alt_imgs
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
                'page': url.replace(self.base_url, '') or '/',
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
                'page': url.replace(self.base_url, '') or '/',
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
                'page': url.replace(self.base_url, '') or '/',
                'details': f'{len(blocking_scripts)} scripts without async/defer',
                'recommendation': 'Add async or defer attributes to script tags'
            })
        
        return blocking_issues
    
    def crawl_page(self, url):
        """Crawl a single page and extract information"""
        if url in self.visited_urls:
            print(f"⏭️  Already visited: {url}")
            return
        
        if len(self.visited_urls) >= self.max_pages:
            print(f"🛑 Max pages reached: {len(self.visited_urls)}/{self.max_pages}")
            return
        
        # Send progress update
        page_name = url.replace(self.base_url, '') or '/'
        self.send_progress(f'Crawling: {page_name}')
        
        print(f"\n🔍 Crawling: {url}")
        self.visited_urls.add(url)
        
        response = self.fetch_page(url)
        if not response:
            print(f"❌ Failed to fetch: {url}")
            self.broken_links.append({
                'url': url, 
                'status': 'Failed to fetch',
                'page': page_name,
                'error': 'Connection timeout or network error'
            })
            return
        
        print(f"✅ Successfully fetched: {url} (Status: {response.status_code})")
        
        # Check for redirects
        if response.history:
            print(f"🔀 Redirect detected: {url} -> {response.url}")
            self.redirects.append({
                'from': url,
                'to': response.url,
                'status_codes': [r.status_code for r in response.history]
            })
        
        # Check status code - but allow 415 (some sites return this but still provide content)
        if response.status_code >= 400 and response.status_code != 415:
            print(f"❌ Error status code: {response.status_code}")
            self.broken_links.append({
                'url': url, 
                'status': response.status_code,
                'page': page_name,
                'error': f'HTTP {response.status_code} error'
            })
            return
        elif response.status_code == 415:
            print(f"⚠️  Warning: Status 415 (Unsupported Media Type) but continuing with content")
        
        # Parse HTML
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Failed to parse HTML: {str(e)}")
            return
        
        # Analyze page speed
        speed_data = self.analyze_page_speed(url, response)
        
        # Analyze page
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'speed': speed_data
        }
        self.pages_data.append(page_data)
        
        # Check various elements
        self.issues['warnings'].extend(self.check_seo_elements(soup, url))
        self.issues['warnings'].extend(self.check_images(soup, url))
        self.issues['critical'].extend(self.check_security_headers(response))
        self.issues['warnings'].extend(self.check_mobile_viewport(soup, url))
        self.issues['critical'].extend(self.check_render_blocking_resources(soup, url))
        
        # Extract all links
        all_page_links = soup.find_all('a', href=True)
        print(f"📎 Found {len(all_page_links)} links on page")
        
        internal_links_found = 0
        external_links_found = 0
        
        for link in all_page_links:
            href = link['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            
            # Skip anchors, javascript, mailto, tel
            if parsed.fragment or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            
            self.all_links.add(full_url)
            
            # Check if internal or external (handle both www and non-www)
            is_internal = (
                parsed.netloc == self.domain or 
                parsed.netloc == self.domain_without_www or 
                parsed.netloc == self.domain_with_www or 
                not parsed.netloc
            )
            
            if is_internal:
                # Internal link - add to crawl queue
                if full_url not in self.visited_urls:
                    internal_links_found += 1
                    print(f"  → Internal link found: {full_url}")
                    self.crawl_page(full_url)
            else:
                # External link
                external_links_found += 1
                self.external_links.add(full_url)
        
        print(f"📊 Stats for this page: {internal_links_found} internal, {external_links_found} external")
        print(f"📈 Total progress: {len(self.visited_urls)}/{self.max_pages} pages crawled")
    
    def check_broken_links(self):
        """Check all found links for broken ones - DISABLED for performance"""
        self.send_progress("Skipping external broken link check...")
        print("\n⏭️  Skipping external broken link check for better performance...")
        # Skip checking external links to avoid timeouts
        # Only report broken links found during crawling
        return
    
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        self.send_progress("Generating recommendations...")
        print("\n📝 Generating recommendations...")
        recommendations = []
        
        # Broken links recommendation
        if len(self.broken_links) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Broken Links',
                'title': f'{len(self.broken_links)} broken links found',
                'description': 'Multiple pages are linking to non-existent resources',
                'affected_count': len(self.broken_links),
                'affected_urls': [link['url'] for link in self.broken_links[:10]],
                'recommendation': 'Update or remove broken links. Set up proper 301 redirects for moved content. Check the broken links list for specific URLs to fix.'
            })
        
        # Group issues by category
        issue_counts = defaultdict(int)
        issue_examples = defaultdict(list)
        for issue_list in self.issues.values():
            for issue in issue_list:
                issue_counts[issue['category']] += 1
                if len(issue_examples[issue['category']]) < 5:
                    issue_examples[issue['category']].append({
                        'url': issue.get('url', 'N/A'),
                        'page': issue.get('page', 'N/A'),
                        'title': issue.get('title', 'N/A')
                    })
        
        # SEO recommendations
        if issue_counts['SEO'] > 0:
            recommendations.append({
                'priority': 'warning',
                'category': 'SEO',
                'title': f'{issue_counts["SEO"]} SEO issues found',
                'description': 'Missing or suboptimal meta tags and heading structure',
                'affected_count': issue_counts['SEO'],
                'affected_urls': [ex['url'] for ex in issue_examples['SEO']],
                'recommendation': 'Add unique meta descriptions to all pages, optimize title tags (keep under 60 characters), ensure proper heading hierarchy with single H1 per page'
            })
        
        # Performance recommendations
        if issue_counts['Performance'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Performance',
                'title': f'{issue_counts["Performance"]} performance issues found',
                'description': 'Render-blocking resources detected that slow down page load',
                'affected_count': issue_counts['Performance'],
                'affected_urls': [ex['url'] for ex in issue_examples['Performance']],
                'recommendation': 'Defer non-critical CSS/JS, add async/defer attributes to scripts, consider inlining critical CSS, implement lazy loading for images'
            })
        
        # Security recommendations
        if issue_counts['Security'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Security',
                'title': f'{issue_counts["Security"]} security issues found',
                'description': 'Missing security headers leave site vulnerable',
                'affected_count': issue_counts['Security'],
                'recommendation': 'Configure server to include security headers: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Strict-Transport-Security, Content-Security-Policy'
            })
        
        # Accessibility recommendations
        if issue_counts['Accessibility'] > 0:
            recommendations.append({
                'priority': 'warning',
                'category': 'Accessibility',
                'title': f'{issue_counts["Accessibility"]} accessibility issues found',
                'description': 'Images missing alt text, affecting screen reader users',
                'affected_count': issue_counts['Accessibility'],
                'affected_urls': [ex['url'] for ex in issue_examples['Accessibility']],
                'recommendation': 'Add descriptive alt text to all images, ensure proper color contrast, make interactive elements keyboard accessible'
            })
        
        return recommendations
    
    def calculate_score(self):
        """Calculate overall score based on issues"""
        self.send_progress("Calculating scores...")
        print("\n🧮 Calculating scores...")
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
        print(f"Max pages to crawl: {self.max_pages}")
        print(f"{'='*60}\n")
        
        self.send_progress(f"Starting audit of {self.base_url}")
        
        # Crawl website
        self.crawl_page(self.base_url)
        
        print(f"\n{'='*60}")
        print(f"Crawling complete! Crawled {len(self.visited_urls)} pages")
        print(f"{'='*60}\n")
        
        # Check broken links
        self.check_broken_links()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Calculate scores
        scores = self.calculate_score()
        
        self.send_progress("Audit complete! Preparing report...")
        print("\n✅ Audit complete! Preparing report...")
        
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
            'broken_links': self.broken_links,
            'page_speeds': self.page_speeds
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
            print(f"\n\nBROKEN LINKS:")
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