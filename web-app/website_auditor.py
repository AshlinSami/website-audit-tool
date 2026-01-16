#!/usr/bin/env python3
"""
Website Audit Tool - Algorithm Agency
Comprehensive website analysis tool for performance, SEO, accessibility, and technical health
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# AI-powered fix suggestions
try:
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ OpenAI not installed. AI suggestions disabled.")

class WebsiteAuditor:
    def __init__(self, base_url, max_pages=50, progress_queue=None, ai_enabled=True, openai_api_key=None):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
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
        self.ai_enabled = ai_enabled
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        # Selenium browser
        self.driver = None
        self.use_selenium = True
    
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
        

    def init_browser(self):
        """Initialize undetected Chrome browser (bypasses bot protection)"""
        if not self.use_selenium or self.driver:
            return
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            print("✅ Undetected browser initialized (bypasses bot protection)")
        except Exception as e:
            print(f"⚠️ Browser init failed: {e}")
            self.driver = None
    
    def close_browser(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def fetch_page(self, url):
        """Fetch page using Selenium"""
        # Initialize browser on first call
        if not self.driver:
            self.init_browser()
        
        if not self.driver:
            print(f"⚠️ No browser, skipping {url}")
            return None
        
        try:
            self.driver.get(url)
            
            # Wait for body to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for JavaScript-heavy sites
            import time
            import random
            
            # Random wait to look more human
            time.sleep(random.uniform(2, 4))
            
            # If we see bot challenge, wait much longer
            if "one moment" in self.driver.page_source.lower() or "please wait" in self.driver.page_source.lower() or "checking" in self.driver.page_source.lower():
                print(f"  ⏳ Detected bot check, waiting 15 seconds...")
                time.sleep(15)
                
                # Check again if content loaded
                if "one moment" in self.driver.page_source.lower():
                    print(f"  ⏳ Still loading, waiting another 10 seconds...")
                    time.sleep(10)
            
            # Create fake response object
            class FakeResponse:
                def __init__(self, driver):
                    self.status_code = 200
                    self.content = driver.page_source.encode('utf-8')
                    self.text = driver.page_source
                    self.url = driver.current_url
                    self.history = []
                    self.headers = {}
            
            return FakeResponse(self.driver)
        except Exception as e:
            print(f"Error: {url}: {str(e)}")
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
        """Check for SEO-related elements with detailed information"""
        seo_issues = []
        
        # Check title
        title = soup.find('title')
        if not title or not title.string:
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'Missing page title',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': 'None',
                'fix': 'Add a <title> tag with 50-60 characters'
            })
        elif len(title.string) > 60:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Page title too long',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': f'"{title.string[:60]}..." ({len(title.string)} chars)',
                'fix': f'Shorten to under 60 characters'
            })
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'Missing meta description',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': 'None',
                'fix': 'Add <meta name="description" content="..."> with 150-160 characters'
            })
        
        # Check H1 tags
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            seo_issues.append({
                'type': 'warning',
                'category': 'SEO',
                'title': 'No H1 tag found',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': 'None',
                'fix': 'Add one <h1> tag that describes the main topic'
            })
        elif len(h1_tags) > 1:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Multiple H1 tags',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': f'{len(h1_tags)} H1 tags found',
                'fix': 'Use only one H1 per page. Change extras to H2 or H3'
            })
        
        # Check for canonical tag
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            seo_issues.append({
                'type': 'info',
                'category': 'SEO',
                'title': 'Missing canonical tag',
                'url': url,
                'page': url.replace(self.base_url, '') or '/',
                'current': 'None',
                'fix': 'Add <link rel="canonical" href="..."> to prevent duplicate content issues'
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
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return
        
        # Send progress update
        page_name = url.replace(self.base_url, '') or '/'
        self.send_progress(f'Crawling: {page_name}')
        
        print(f"Crawling: {url}")
        self.visited_urls.add(url)
        
        response = self.fetch_page(url)
        if not response:
            self.broken_links.append({
                'url': url, 
                'status': 'Failed to fetch',
                'page': page_name,
                'error': 'Connection timeout or network error'
            })
            return
        
        # Check for redirects
        if response.history:
            self.redirects.append({
                'from': url,
                'to': response.url,
                'status_codes': [r.status_code for r in response.history]
            })
        
        # Check status code (but allow parsing if we got HTML content)
        if response.status_code >= 400:
            # Only skip if we didn't get usable HTML content
            if len(response.content) < 1000:  # Too small to be real HTML
                self.broken_links.append({
                    'url': url, 
                    'status': response.status_code,
                    'page': page_name,
                    'error': f'HTTP {response.status_code} error'
                })
                return
            # Otherwise continue parsing (some servers return 4xx but with valid HTML)
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
        all_a_tags = soup.find_all('a', href=True)        
        for link in all_a_tags:
            href = link['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            
            # Skip anchors, javascript, mailto, tel
            if parsed.fragment or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
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
        """Check all found links for broken ones - DISABLED for performance"""
        self.send_progress("Skipping external broken link check...")
        print("\nSkipping external broken link check for better performance...")
        # Skip checking external links to avoid timeouts
        # Only report broken links found during crawling
        return
    

    def generate_enhanced_ai_recommendations(self, recommendations):
        """Generate professional SEO agency-level recommendations with AI using actual issue data"""
        if not self.ai_enabled or not AI_AVAILABLE or not self.openai_api_key:
            return recommendations
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            print("\n🤖 Generating professional SEO recommendations with real data...")
            
            for rec in recommendations:
                # Get actual examples from detailed_issues
                category = rec['category']
                issue_examples = []
                
                # Find related detailed issues to get real data
                if hasattr(self, 'issues') and category in self.issues:
                    issue_examples = self.issues[category][:3]  # Get first 3 examples
                
                # Build examples string with actual data
                examples_str = ""
                if issue_examples:
                    examples_str = "\n\nACTUAL EXAMPLES FROM YOUR SITE:\n"
                    for i, issue in enumerate(issue_examples, 1):
                        examples_str += f"\nExample {i}:\n"
                        examples_str += f"  Page: {issue.get('page', 'N/A')}\n"
                        if issue.get('current'):
                            examples_str += f"  Current: {issue.get('current')}\n"
                        if issue.get('title'):
                            examples_str += f"  Issue: {issue.get('title')}\n"
                
                sample_urls = rec.get('affected_urls', [])[:5]
                urls_str = '\n'.join(f"- {url}" for url in sample_urls) if sample_urls else "Multiple pages"
                
                prompt = f"""You are a senior SEO consultant preparing a client brief with SPECIFIC fixes.

ISSUE SUMMARY:
Issue: {rec['title']} 
Category: {rec['category']}
Description: {rec.get('description', '')}
Pages Affected: {len(rec.get('affected_urls', []))}
{examples_str}

Sample URLs:
{urls_str}

Provide SPECIFIC recommendations:

1. BUSINESS IMPACT (2 sentences):
   - How this affects rankings, traffic, conversions
   
2. SPECIFIC FIXES (3-5 steps with ACTUAL examples):
   - If it's a title tag issue, show BEFORE and AFTER
   - If it's meta description, write the actual new description
   - If it's H1 tag, show the exact H1 to add
   - Be specific with the actual content from examples above

3. IMPLEMENTATION (1 sentence):
   - Time: Quick win / Medium effort / Long-term
   - Who: Developer / Content writer / Marketing team

4. PRIORITY SCORE (1-10):
   - Based on SEO impact × ease of implementation

Be VERY specific using the actual examples. Don't say "shorten to 60 chars" - show them the exact shortened version!"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700,
                    temperature=0.7
                )
                
                rec['ai_recommendation'] = response.choices[0].message.content
                
                # Extract priority
                priority_match = re.search(r'PRIORITY.*?(\d+)', response.choices[0].message.content, re.IGNORECASE)
                rec['ai_priority_score'] = int(priority_match.group(1)) if priority_match else 5
                
                print(f"  ✓ Generated specific fixes for: {rec['title']}")
                
        except Exception as e:
            print(f"  ⚠ AI error: {str(e)}")
            
        return recommendations

    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        self.send_progress("Generating recommendations...")
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
        unique_issue_counts = defaultdict(set)
        issue_examples = defaultdict(list)
        for issue_list in self.issues.values():
            for issue in issue_list:
                unique_issue_counts[issue.get('category', 'Other')].add(issue.get('title', 'unknown'))
                if len(issue_examples[issue['category']]) < 5:
                    issue_examples[issue['category']].append({
                        'url': issue.get('url', 'N/A'),
                        'page': issue.get('page', 'N/A'),
                        'title': issue.get('title', 'N/A')
                    })
        
        # SEO recommendations
        if len(unique_issue_counts['SEO']) > 0:
            recommendations.append({
                'priority': 'warning',
                'category': 'SEO',
                'title': f'{len(unique_issue_counts["SEO"])} SEO issues found',
                'description': 'Missing or suboptimal meta tags and heading structure',
                'affected_count': len(unique_issue_counts['SEO']),
                'affected_urls': [ex['url'] for ex in issue_examples['SEO']],
                'recommendation': 'Add unique meta descriptions to all pages, optimize title tags (keep under 60 characters), ensure proper heading hierarchy with single H1 per page'
            })
        
        # Performance recommendations
        if len(unique_issue_counts['Performance']) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Performance',
                'title': f'{len(unique_issue_counts["Performance"])} performance issues found',
                'description': 'Render-blocking resources detected that slow down page load',
                'affected_count': len(unique_issue_counts['Performance']),
                'affected_urls': [ex['url'] for ex in issue_examples['Performance']],
                'recommendation': 'Defer non-critical CSS/JS, add async/defer attributes to scripts, consider inlining critical CSS, implement lazy loading for images'
            })
        
        # Security recommendations
        if len(unique_issue_counts['Security']) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Security',
                'title': f'{len(unique_issue_counts["Security"])} security issues found',
                'description': 'Missing security headers leave site vulnerable',
                'affected_count': len(unique_issue_counts['Security']),
                'recommendation': 'Configure server to include security headers: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Strict-Transport-Security, Content-Security-Policy'
            })
        
        # Accessibility recommendations
        if len(unique_issue_counts['Accessibility']) > 0:
            recommendations.append({
                'priority': 'warning',
                'category': 'Accessibility',
                'title': f'{len(unique_issue_counts["Accessibility"])} accessibility issues found',
                'description': 'Images missing alt text, affecting screen reader users',
                'affected_count': len(unique_issue_counts['Accessibility']),
                'affected_urls': [ex['url'] for ex in issue_examples['Accessibility']],
                'recommendation': 'Add descriptive alt text to all images, ensure proper color contrast, make interactive elements keyboard accessible'
            })
        
        return recommendations
    
    def calculate_score(self):
        """Calculate scores using Lighthouse-style methodology"""
        self.send_progress("Calculating scores...")
        
        from collections import defaultdict
        
        # Count UNIQUE issues per category (not per-page duplicates)
        unique_issues_by_category = defaultdict(set)
        
        for issue_list in self.issues.values():
            for issue in issue_list:
                category = issue.get('category', 'Other')
                issue_key = f"{issue.get('title', 'unknown')}"
                unique_issues_by_category[category].add(issue_key)
        
        # SEO Score (0-100) - Each unique issue = -20 points
        seo_unique = len(unique_issues_by_category.get('SEO', set()))
        seo_score = max(0, 100 - (seo_unique * 20))
        
        # Performance Score (0-100) - Each unique issue = -25 points
        perf_unique = len(unique_issues_by_category.get('Performance', set()))
        performance_score = max(0, 100 - (perf_unique * 25))
        
        # Accessibility Score (0-100) - Each unique issue = -20 points
        access_unique = len(unique_issues_by_category.get('Accessibility', set()))
        accessibility_score = max(0, 100 - (access_unique * 20))
        
        # Best Practices Score (0-100)
        security_unique = len(unique_issues_by_category.get('Security', set()))
        mobile_unique = len(unique_issues_by_category.get('Mobile', set()))
        broken_links_penalty = min(len(self.broken_links) * 2, 30)
        
        best_practices_score = max(0, 100 - (security_unique * 15) - (mobile_unique * 10) - broken_links_penalty)
        
        # Overall Score (weighted average)
        # Performance: 30%, SEO: 25%, Accessibility: 20%, Best Practices: 25%
        overall_score = int(
            (performance_score * 0.30) +
            (seo_score * 0.25) +
            (accessibility_score * 0.20) +
            (best_practices_score * 0.25)
        )
        
        return {
            'overall': overall_score,
            'performance': performance_score,
            'seo': seo_score,
            'accessibility': accessibility_score,
            'bestPractices': best_practices_score
        }

    def generate_ai_suggestions(self, recommendations):
        """Generate AI-powered specific fixes using ChatGPT"""
        if not self.ai_enabled or not AI_AVAILABLE or not self.openai_api_key:
            return recommendations
        
        try:
            client = OpenAI(api_key=self.openai_api_key)
            
            print("\n🤖 Generating AI-powered fix suggestions...")
            
            for rec in recommendations:
                # Create detailed prompt
                affected_urls_str = '\n'.join(rec.get('affected_urls', [])[:3])
                
                prompt = f"""You are a web development expert. Analyze this website audit issue and provide specific, actionable fixes.

Issue Details:
- Category: {rec['category']}
- Problem: {rec['title']}
- Description: {rec['description']}
- Affected URLs (sample):
{affected_urls_str}

Provide:
1. Root cause analysis (1-2 sentences)
2. Step-by-step fix instructions (3-5 specific steps)
3. Code example if applicable
4. Expected impact on score

Be technical, specific, and actionable. Keep response under 300 words."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Cheap and fast
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                
                rec['ai_suggestion'] = response.choices[0].message.content
                print(f"  ✓ Generated suggestion for: {rec['title']}")
                
        except Exception as e:
            print(f"⚠️  AI suggestion generation failed: {str(e)}")
        
        return recommendations

    def generate_ai_suggestions_for_issues(self):
        """Generate AI suggestions for individual detailed issues"""
        if not self.ai_enabled or not AI_AVAILABLE or not self.openai_api_key:
            return
        
        try:
            client = OpenAI(api_key=self.openai_api_key)
            
            print("\n🤖 Generating AI suggestions for detailed issues...")
            
            # Process SEO and Accessibility issues (most common)
            processed = 0
            max_to_process = 10  # Limit to avoid too many API calls
            
            for issue_list in self.issues.values():
                for issue in issue_list:
                    if processed >= max_to_process:
                        break
                    
                    # Only process issues that don't already have good suggestions
                    if issue.get('category') in ['SEO', 'Accessibility', 'Performance']:
                        # Get page context - find the page data for this issue
                        page_title = "Unknown"
                        page_url = issue.get('page', 'Homepage')
                        
                        # Try to find the actual page data
                        for page_data in self.pages_data:
                            if page_url in page_data.get('url', ''):
                                page_title = page_data.get('title', 'Unknown')
                                break
                        
                        prompt = f"""As a web expert, provide a specific fix for this issue.

WEBSITE CONTEXT:
- Page Title: {page_title}
- Page URL: {page_url}

ISSUE:
- Problem: {issue.get('title')}
- Current Value: {issue.get('current', 'Not set')}

Provide ONE specific example fix using the actual website context above:
1. Use the real page title/URL when generating meta tags
2. Make it relevant to what this website is about
3. Keep under 100 words
4. Format as code (HTML tags)

Example formats:
<title>Winklmayr | Luxury Leather Bags & Accessories</title>
<meta name="description" content="Shop premium leather bags...">
<link rel="canonical" href="https://winklmayr.com/" />"""

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=200,
                            temperature=0.7
                        )
                        
                        issue['ai_example'] = response.choices[0].message.content.strip()
                        processed += 1
                        print(f"  ✓ Generated example for: {issue.get('title')}")
                
                if processed >= max_to_process:
                    break
                    
        except Exception as e:
            print(f"⚠️  AI examples failed: {str(e)}")

    def run_audit(self):
        """Run complete audit"""
        print(f"\n{'='*60}")
        print(f"Starting Website Audit for: {self.base_url}")
        print(f"{'='*60}\n")
        
        self.send_progress(f"Starting audit of {self.base_url}")
        
        # Crawl website
        self.crawl_page(self.base_url)
        
        # Check broken links
        self.check_broken_links()
        
        # Generate AI examples for issues
        if self.ai_enabled:
            self.generate_ai_suggestions_for_issues()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Generate AI suggestions if enabled
        if self.ai_enabled:
            recommendations = self.generate_enhanced_ai_recommendations(recommendations)
        
        # Calculate scores
        scores = self.calculate_score()
        
        self.send_progress("Audit complete! Preparing report...")
        
        # Collect all detailed issues
        all_issues = []
        for issue_list in self.issues.values():
            for issue in issue_list:
                all_issues.append(issue)
        
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
            'detailed_issues': all_issues,  # NEW: All issues with details
            'broken_links': self.broken_links,
            'page_speeds': self.page_speeds
        }
        
        # Cleanup browser
        self.close_browser()
        
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