# 🚀 GitHub Setup Guide for Website Audit Tool

This guide will walk you through setting up the Website Audit Tool on GitHub.

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [GitHub](https://github.com)
2. Click the **"+"** icon in the top right
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `website-audit-tool`
   - **Description**: `Comprehensive website auditing tool for performance, SEO, and accessibility analysis`
   - **Visibility**: Choose Private or Public
   - **DO NOT** initialize with README (we have our own)
5. Click **"Create repository"**

### Option B: Using GitHub CLI
```bash
gh repo create website-audit-tool --private --description "Website auditing tool by Algorithm Agency"
```

## Step 2: Initialize Repository
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Website Audit Tool v1.0.0"
```

## Step 3: Connect to GitHub
```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/website-audit-tool.git

# Or for SSH:
git remote add origin git@github.com:YOUR_USERNAME/website-audit-tool.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Set Up GitHub Actions (Optional)

### Configure Secrets

For automated weekly audits, add these secrets to your repository:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add the following secrets:
```
Name: AUDIT_URL
Value: https://yourwebsite.com

Name: NOTIFICATION_EMAIL (optional)
Value: your@email.com
```

### Test GitHub Actions

1. Go to **Actions** tab
2. Select **"Website Audit Workflow"**
3. Click **"Run workflow"**
4. Enter test URL: `https://example.com`
5. Click **"Run workflow"**
6. Watch it run!

## Step 5: Customize for Your Organization

### Update README

Edit `README.md` and replace:
- `YOUR_USERNAME` with your GitHub username
- Email addresses with your organization's emails
- Add your company logo if desired

## Step 6: Create Your First Release
```bash
# Tag the release
git tag -a v1.0.0 -m "Initial release - Website Audit Tool"
git push origin v1.0.0
```

Then on GitHub:
1. Go to **Releases**
2. Click **"Draft a new release"**
3. Choose tag: `v1.0.0`
4. Title: `Website Audit Tool v1.0.0`
5. Description: Copy from CHANGELOG.md
6. Click **"Publish release"**

## Common Git Commands

### Daily Workflow
```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-audit-check

# Make changes, then:
git add .
git commit -m "feat: add SSL certificate expiry check"

# Push to GitHub
git push origin feature/new-audit-check

# Create Pull Request on GitHub
```

### View Status and History
```bash
# Check status
git status

# View commit history
git log --oneline

# View changes
git diff

# View remote
git remote -v
```

## Troubleshooting

### "Permission denied"
```bash
# Set up SSH key
ssh-keygen -t ed25519 -C "your@email.com"
# Add key to GitHub: Settings → SSH Keys
```

### "Repository not found"
```bash
# Check remote URL
git remote -v

# Update remote
git remote set-url origin https://github.com/YOUR_USERNAME/website-audit-tool.git
```

## Best Practices

### Commit Messages

Use conventional commits:
```
feat: add new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructuring
test: adding tests
chore: maintenance
```

### Security

1. **Never commit**:
   - API keys
   - Passwords
   - Tokens
   - Client data

2. **Use .gitignore**:
```
   .env
   *.key
   secrets/
```

## Next Steps

1. ✅ Clone and test locally
2. ✅ Run your first audit
3. ✅ Customize for your needs
4. ✅ Set up automated audits
5. ✅ Invite team members
6. ✅ Start using in production!

---

Happy auditing! 🚀