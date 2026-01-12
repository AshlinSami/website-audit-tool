# Contributing to Website Audit Tool

Thank you for your interest in contributing to the Website Audit Tool! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Local Development

1. **Fork and Clone**
```bash
   git clone https://github.com/algorithm-agency/website-audit-tool.git
   cd website-audit-tool
```

2. **Create Branch**
```bash
   git checkout -b feature/your-feature-name
```

3. **Install Dependencies**
```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
```

4. **Make Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests where applicable

5. **Test Changes**
```bash
   # Test backend
   python3 backend/website-auditor.py https://example.com 10
   
   # Test frontend
   cd frontend
   npm start
```

6. **Commit Changes**
```bash
   git add .
   git commit -m "feat: add new audit check for X"
```

7. **Push and Create PR**
```bash
   git push origin feature/your-feature-name
```

## Code Style

### Python
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and small
```python
def check_seo_elements(self, soup, url):
    """
    Check for SEO-related elements on a page.
    
    Args:
        soup: BeautifulSoup object of the page
        url: URL of the page being checked
        
    Returns:
        list: List of SEO issues found
    """
    seo_issues = []
    # Implementation
    return seo_issues
```

### JavaScript/React
- Use functional components
- Follow React best practices
- Use meaningful component names
- Add comments for complex logic

## Commit Messages

Use conventional commit format:
```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: adding tests
chore: maintenance tasks
```

Examples:
```
feat: add SSL certificate expiry check
fix: resolve broken link detection issue
docs: update usage examples in README
refactor: optimize page crawling performance
```

## Pull Request Process

1. **Update Documentation**
   - Update README if adding features
   - Add usage examples
   - Update CHANGELOG.md

2. **Test Thoroughly**
   - Test on multiple websites
   - Verify no regressions
   - Check edge cases

3. **Create PR**
   - Use descriptive title
   - Explain what and why
   - Reference related issues
   - Add screenshots if UI changes

## Feature Requests

### New Audit Checks

To add a new audit check:

1. **Create Check Method**
```python
   def check_my_feature(self, soup, url):
       """Check for my feature"""
       issues = []
       
       # Your logic here
       if condition:
           issues.append({
               'type': 'warning',  # or 'critical', 'info'
               'category': 'MyCategory',
               'title': 'Issue title',
               'url': url,
               'details': 'Additional details'
           })
       
       return issues
```

2. **Integrate in Crawl**
```python
   def crawl_page(self, url):
       # ... existing code ...
       self.issues['warnings'].extend(
           self.check_my_feature(soup, url)
       )
```

3. **Add Documentation**
   - Update README features list
   - Add usage example
   - Document any new parameters

## Bug Reports

### Template
```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce:
1. Run command: `python3 website-auditor.py https://example.com`
2. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.10]
- Tool version: [e.g. 1.0.0]

**Additional context**
Any other relevant information
```

## Questions?

For questions about contributing:
- Create a GitHub Discussion
- Email: dev@algorithmagency.co.za

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

---

Thank you for contributing to making this tool better! 🚀