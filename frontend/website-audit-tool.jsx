import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, XCircle, Clock, TrendingUp, Download, Search, Globe, Zap, Shield, Eye, FileText } from 'lucide-react';

const WebsiteAuditTool = () => {
  const [url, setUrl] = useState('');
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResults, setAuditResults] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('');

  // Simulated audit functions (in production, these would make actual API calls)
  const performAudit = async (targetUrl) => {
    setIsAuditing(true);
    setProgress(0);
    
    const tasks = [
      { name: 'Crawling website structure', weight: 15 },
      { name: 'Checking broken links', weight: 15 },
      { name: 'Analyzing page speed', weight: 20 },
      { name: 'Validating SEO elements', weight: 15 },
      { name: 'Testing mobile responsiveness', weight: 10 },
      { name: 'Checking security headers', weight: 10 },
      { name: 'Analyzing accessibility', weight: 10 },
      { name: 'Generating report', weight: 5 }
    ];

    let totalProgress = 0;

    for (const task of tasks) {
      setCurrentTask(task.name);
      await new Promise(resolve => setTimeout(resolve, 800));
      totalProgress += task.weight;
      setProgress(totalProgress);
    }

    // Simulated audit results
    const mockResults = {
      url: targetUrl,
      timestamp: new Date().toISOString(),
      score: {
        overall: 72,
        performance: 65,
        seo: 85,
        accessibility: 70,
        bestPractices: 78
      },
      issues: {
        critical: [
          {
            category: 'Performance',
            title: 'Render-blocking resources detected',
            description: '3 CSS files and 2 JavaScript files are blocking the first paint',
            pages: ['/index.html', '/about.html', '/contact.html'],
            impact: 'High',
            recommendation: 'Defer non-critical CSS and JavaScript. Use async/defer attributes for scripts. Consider inlining critical CSS.'
          },
          {
            category: 'Broken Links',
            title: '7 broken internal links found',
            description: 'Multiple pages are linking to non-existent resources',
            pages: ['/blog/old-post', '/products/discontinued', '/team/former-member'],
            impact: 'High',
            recommendation: 'Update or remove broken links. Set up proper 301 redirects for moved content.'
          },
          {
            category: 'Security',
            title: 'Missing security headers',
            description: 'X-Content-Type-Options and X-Frame-Options headers not set',
            pages: ['All pages'],
            impact: 'High',
            recommendation: 'Configure server to include security headers: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN'
          }
        ],
        warnings: [
          {
            category: 'SEO',
            title: 'Missing meta descriptions',
            description: '12 pages lack meta descriptions',
            pages: ['/services.html', '/portfolio.html', '/blog.html'],
            impact: 'Medium',
            recommendation: 'Add unique, descriptive meta descriptions (150-160 characters) to all pages to improve search visibility.'
          },
          {
            category: 'Images',
            title: 'Unoptimized images',
            description: '24 images are larger than 500KB',
            pages: ['/gallery.html', '/products.html'],
            impact: 'Medium',
            recommendation: 'Compress images using tools like TinyPNG. Consider WebP format. Implement lazy loading for below-fold images.'
          },
          {
            category: 'Accessibility',
            title: 'Missing alt attributes',
            description: '18 images missing alt text',
            pages: ['/index.html', '/services.html'],
            impact: 'Medium',
            recommendation: 'Add descriptive alt text to all images for screen readers and SEO.'
          },
          {
            category: 'Mobile',
            title: 'Touch targets too small',
            description: '15 interactive elements smaller than 48x48px',
            pages: ['/navigation', '/forms'],
            impact: 'Medium',
            recommendation: 'Increase touch target sizes to minimum 48x48px for better mobile usability.'
          }
        ],
        info: [
          {
            category: 'SEO',
            title: 'Multiple H1 tags',
            description: '5 pages contain multiple H1 tags',
            pages: ['/blog/article-1.html', '/blog/article-2.html'],
            impact: 'Low',
            recommendation: 'Use only one H1 tag per page for better SEO structure.'
          },
          {
            category: 'Performance',
            title: 'Missing browser caching',
            description: 'Static resources lack cache headers',
            pages: ['All pages'],
            impact: 'Low',
            recommendation: 'Set appropriate cache-control headers for static assets (images, CSS, JS).'
          }
        ]
      },
      pageSpeed: [
        { page: '/index.html', loadTime: 2.3, fcp: 1.2, lcp: 2.8, cls: 0.05, fid: 45 },
        { page: '/about.html', loadTime: 1.8, fcp: 0.9, lcp: 2.1, cls: 0.02, fid: 32 },
        { page: '/services.html', loadTime: 3.5, fcp: 1.8, lcp: 4.2, cls: 0.12, fid: 78 },
        { page: '/contact.html', loadTime: 1.5, fcp: 0.7, lcp: 1.9, cls: 0.01, fid: 28 }
      ],
      crawlStats: {
        totalPages: 47,
        crawledPages: 47,
        brokenLinks: 7,
        redirects: 12,
        externalLinks: 124
      }
    };

    setAuditResults(mockResults);
    setIsAuditing(false);
    setProgress(100);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      performAudit(url);
    }
  };

  const downloadReport = () => {
    if (!auditResults) return;
    
    const reportContent = `
WEBSITE AUDIT REPORT
═══════════════════════════════════════════

URL: ${auditResults.url}
Date: ${new Date(auditResults.timestamp).toLocaleString()}

OVERALL SCORE: ${auditResults.score.overall}/100

DETAILED SCORES:
├─ Performance: ${auditResults.score.performance}/100
├─ SEO: ${auditResults.score.seo}/100
├─ Accessibility: ${auditResults.score.accessibility}/100
└─ Best Practices: ${auditResults.score.bestPractices}/100

CRITICAL ISSUES (${auditResults.issues.critical.length}):
${auditResults.issues.critical.map((issue, i) => `
${i + 1}. ${issue.title}
   Category: ${issue.category}
   Impact: ${issue.impact}
   Description: ${issue.description}
   Affected Pages: ${issue.pages.join(', ')}
   Recommendation: ${issue.recommendation}
`).join('\n')}

WARNINGS (${auditResults.issues.warnings.length}):
${auditResults.issues.warnings.map((issue, i) => `
${i + 1}. ${issue.title}
   Category: ${issue.category}
   Impact: ${issue.impact}
   Description: ${issue.description}
   Affected Pages: ${issue.pages.join(', ')}
   Recommendation: ${issue.recommendation}
`).join('\n')}

PAGE SPEED ANALYSIS:
${auditResults.pageSpeed.map(page => `
${page.page}
├─ Load Time: ${page.loadTime}s
├─ First Contentful Paint: ${page.fcp}s
├─ Largest Contentful Paint: ${page.lcp}s
├─ Cumulative Layout Shift: ${page.cls}
└─ First Input Delay: ${page.fid}ms
`).join('\n')}

CRAWL STATISTICS:
├─ Total Pages: ${auditResults.crawlStats.totalPages}
├─ Crawled Pages: ${auditResults.crawlStats.crawledPages}
├─ Broken Links: ${auditResults.crawlStats.brokenLinks}
├─ Redirects: ${auditResults.crawlStats.redirects}
└─ External Links: ${auditResults.crawlStats.externalLinks}

════════════════════════════════════════════
Generated by Algorithm Agency Website Audit Tool
    `;

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `website-audit-${auditResults.url.replace(/[^a-z0-9]/gi, '-')}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-emerald-400';
    if (score >= 70) return 'text-amber-400';
    return 'text-rose-400';
  };

  const getScoreBgColor = (score) => {
    if (score >= 90) return 'bg-emerald-500/20';
    if (score >= 70) return 'bg-amber-500/20';
    return 'bg-rose-500/20';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 font-sans">
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-20 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(to right, rgba(148, 163, 184, 0.1) 1px, transparent 1px),
                           linear-gradient(to bottom, rgba(148, 163, 184, 0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-block mb-6">
            <div className="flex items-center gap-3 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 px-6 py-3 rounded-full border border-cyan-500/30">
              <Search className="w-5 h-5 text-cyan-400" />
              <span className="text-cyan-400 font-semibold text-sm tracking-wider uppercase">Website Auditor</span>
            </div>
          </div>
          <h1 className="text-6xl font-black mb-4 bg-gradient-to-r from-slate-100 via-slate-300 to-slate-100 bg-clip-text text-transparent leading-tight">
            Professional Website<br />Audit Tool
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Comprehensive analysis of performance, SEO, accessibility, and technical health
          </p>
        </div>

        {/* Audit Form */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto mb-16">
          <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
            <label className="block text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">
              Website URL
            </label>
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full pl-12 pr-4 py-4 bg-slate-950 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                  disabled={isAuditing}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={isAuditing}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 disabled:from-slate-700 disabled:to-slate-700 rounded-xl font-bold text-white shadow-lg hover:shadow-cyan-500/25 transition-all disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isAuditing ? (
                  <>
                    <Clock className="w-5 h-5 animate-spin" />
                    Auditing...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Start Audit
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Progress Bar */}
        {isAuditing && (
          <div className="max-w-3xl mx-auto mb-16">
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold text-slate-300">{currentTask}</span>
                <span className="text-sm font-bold text-cyan-400">{progress}%</span>
              </div>
              <div className="h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                <div 
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-300 ease-out rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {auditResults && !isAuditing && (
          <div className="space-y-8 animate-fadeIn">
            {/* Overall Score */}
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-slate-100 mb-2">Audit Results</h2>
                  <p className="text-slate-400 text-sm">
                    {auditResults.url} • {new Date(auditResults.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={downloadReport}
                  className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold text-slate-100 flex items-center gap-2 transition-colors border border-slate-700"
                >
                  <Download className="w-4 h-4" />
                  Download Report
                </button>
              </div>

              <div className="grid md:grid-cols-5 gap-6">
                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-24 h-24 rounded-2xl ${getScoreBgColor(auditResults.score.overall)} border-2 ${auditResults.score.overall >= 90 ? 'border-emerald-500/50' : auditResults.score.overall >= 70 ? 'border-amber-500/50' : 'border-rose-500/50'} mb-3`}>
                    <span className={`text-3xl font-black ${getScoreColor(auditResults.score.overall)}`}>
                      {auditResults.score.overall}
                    </span>
                  </div>
                  <p className="text-sm font-bold text-slate-300 uppercase tracking-wider">Overall</p>
                </div>

                {[
                  { label: 'Performance', value: auditResults.score.performance, icon: Zap },
                  { label: 'SEO', value: auditResults.score.seo, icon: TrendingUp },
                  { label: 'Accessibility', value: auditResults.score.accessibility, icon: Eye },
                  { label: 'Best Practices', value: auditResults.score.bestPractices, icon: Shield }
                ].map((metric) => (
                  <div key={metric.label} className="text-center">
                    <div className="bg-slate-800/50 rounded-2xl p-4 border border-slate-700 mb-3">
                      <metric.icon className={`w-6 h-6 mx-auto mb-2 ${getScoreColor(metric.value)}`} />
                      <span className={`text-2xl font-black ${getScoreColor(metric.value)}`}>
                        {metric.value}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{metric.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Issues */}
            <div className="grid md:grid-cols-2 gap-8">
              {/* Critical Issues */}
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center">
                    <XCircle className="w-5 h-5 text-rose-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Critical Issues</h3>
                    <p className="text-sm text-slate-400">{auditResults.issues.critical.length} items require immediate attention</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {auditResults.issues.critical.map((issue, index) => (
                    <div key={index} className="bg-slate-950/50 rounded-xl p-5 border border-slate-800 hover:border-rose-500/30 transition-colors">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="px-2 py-1 bg-rose-500/20 text-rose-400 text-xs font-bold rounded uppercase tracking-wider">
                          {issue.category}
                        </span>
                      </div>
                      <h4 className="font-bold text-slate-100 mb-2">{issue.title}</h4>
                      <p className="text-sm text-slate-400 mb-3">{issue.description}</p>
                      <div className="mb-3">
                        <p className="text-xs text-slate-500 font-semibold mb-1">AFFECTED PAGES:</p>
                        <p className="text-xs text-slate-400">{issue.pages.join(', ')}</p>
                      </div>
                      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
                        <p className="text-xs text-slate-500 font-semibold mb-1">RECOMMENDATION:</p>
                        <p className="text-xs text-slate-300">{issue.recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Warnings */}
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Warnings</h3>
                    <p className="text-sm text-slate-400">{auditResults.issues.warnings.length} items to improve</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {auditResults.issues.warnings.map((issue, index) => (
                    <div key={index} className="bg-slate-950/50 rounded-xl p-5 border border-slate-800 hover:border-amber-500/30 transition-colors">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs font-bold rounded uppercase tracking-wider">
                          {issue.category}
                        </span>
                      </div>
                      <h4 className="font-bold text-slate-100 mb-2">{issue.title}</h4>
                      <p className="text-sm text-slate-400 mb-3">{issue.description}</p>
                      <div className="mb-3">
                        <p className="text-xs text-slate-500 font-semibold mb-1">AFFECTED PAGES:</p>
                        <p className="text-xs text-slate-400">{issue.pages.slice(0, 3).join(', ')}{issue.pages.length > 3 ? '...' : ''}</p>
                      </div>
                      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
                        <p className="text-xs text-slate-500 font-semibold mb-1">RECOMMENDATION:</p>
                        <p className="text-xs text-slate-300">{issue.recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Page Speed Analysis */}
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100">Page Speed Analysis</h3>
                  <p className="text-sm text-slate-400">Core Web Vitals metrics</p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Page</th>
                      <th className="text-right py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Load Time</th>
                      <th className="text-right py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">FCP</th>
                      <th className="text-right py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">LCP</th>
                      <th className="text-right py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">CLS</th>
                      <th className="text-right py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">FID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditResults.pageSpeed.map((page, index) => (
                      <tr key={index} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4 text-sm font-medium text-slate-300">{page.page}</td>
                        <td className="py-3 px-4 text-sm text-right">
                          <span className={page.loadTime > 3 ? 'text-rose-400' : page.loadTime > 2 ? 'text-amber-400' : 'text-emerald-400'}>
                            {page.loadTime}s
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-slate-400">{page.fcp}s</td>
                        <td className="py-3 px-4 text-sm text-right">
                          <span className={page.lcp > 4 ? 'text-rose-400' : page.lcp > 2.5 ? 'text-amber-400' : 'text-emerald-400'}>
                            {page.lcp}s
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <span className={page.cls > 0.1 ? 'text-rose-400' : page.cls > 0.05 ? 'text-amber-400' : 'text-emerald-400'}>
                            {page.cls.toFixed(2)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <span className={page.fid > 100 ? 'text-rose-400' : page.fid > 50 ? 'text-amber-400' : 'text-emerald-400'}>
                            {page.fid}ms
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-6 grid grid-cols-5 gap-4 text-center">
                <div className="bg-slate-950/50 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 font-semibold mb-1">TOTAL PAGES</p>
                  <p className="text-2xl font-bold text-slate-100">{auditResults.crawlStats.totalPages}</p>
                </div>
                <div className="bg-slate-950/50 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 font-semibold mb-1">CRAWLED</p>
                  <p className="text-2xl font-bold text-emerald-400">{auditResults.crawlStats.crawledPages}</p>
                </div>
                <div className="bg-slate-950/50 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 font-semibold mb-1">BROKEN LINKS</p>
                  <p className="text-2xl font-bold text-rose-400">{auditResults.crawlStats.brokenLinks}</p>
                </div>
                <div className="bg-slate-950/50 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 font-semibold mb-1">REDIRECTS</p>
                  <p className="text-2xl font-bold text-amber-400">{auditResults.crawlStats.redirects}</p>
                </div>
                <div className="bg-slate-950/50 rounded-lg p-3 border border-slate-800">
                  <p className="text-xs text-slate-500 font-semibold mb-1">EXTERNAL LINKS</p>
                  <p className="text-2xl font-bold text-cyan-400">{auditResults.crawlStats.externalLinks}</p>
                </div>
              </div>
            </div>

            {/* Info Items */}
            {auditResults.issues.info.length > 0 && (
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Informational</h3>
                    <p className="text-sm text-slate-400">{auditResults.issues.info.length} minor optimization opportunities</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  {auditResults.issues.info.map((issue, index) => (
                    <div key={index} className="bg-slate-950/50 rounded-xl p-5 border border-slate-800">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded uppercase tracking-wider inline-block mb-3">
                        {issue.category}
                      </span>
                      <h4 className="font-bold text-slate-100 mb-2 text-sm">{issue.title}</h4>
                      <p className="text-xs text-slate-400 mb-2">{issue.description}</p>
                      <p className="text-xs text-slate-500">{issue.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        {!auditResults && !isAuditing && (
          <div className="text-center mt-20">
            <p className="text-slate-500 text-sm">
              Built by <span className="text-cyan-400 font-semibold">Algorithm Agency</span> • Professional Website Auditing
            </p>
          </div>
        )}
      </div>

      <style jsx>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        * {
          font-family: 'Inter', sans-serif;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }
      `}</style>
    </div>
  );
};

export default WebsiteAuditTool;