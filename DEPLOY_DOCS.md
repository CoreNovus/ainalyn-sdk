# Deploying Documentation to GitHub Pages

This guide walks you through deploying the Ainalyn SDK documentation to GitHub Pages.

## Prerequisites

- Git installed and configured
- GitHub account
- Documentation already committed (✅ Done!)

## Step 1: Create GitHub Repository

If you haven't already created a repository on GitHub:

1. Go to https://github.com/new
2. Repository name: `ainalyn-sdk` (or your preferred name)
3. Description: "Agent Definition Compiler for Ainalyn Platform"
4. Visibility: Public (for GitHub Pages to work freely)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Add GitHub Remote

After creating the repository, GitHub will show you the repository URL. Use it to add the remote:

```bash
# Replace YOUR_USERNAME with your GitHub username or organization
git remote add origin https://github.com/YOUR_USERNAME/ainalyn-sdk.git

# Verify the remote was added
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/ainalyn-sdk.git (fetch)
origin  https://github.com/YOUR_USERNAME/ainalyn-sdk.git (push)
```

## Step 3: Push Code to GitHub

Push your master branch:

```bash
git push -u origin master
```

This uploads all your code and documentation to GitHub.

## Step 4: Deploy Documentation to GitHub Pages

Now deploy the documentation using MkDocs:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Deploy to GitHub Pages
.venv/Scripts/python.exe -m mkdocs gh-deploy
```

This command will:
1. Build the documentation in the `site/` directory
2. Create a `gh-pages` branch (if it doesn't exist)
3. Copy the built site to the `gh-pages` branch
4. Push the `gh-pages` branch to GitHub

## Step 5: Enable GitHub Pages

After deploying, enable GitHub Pages in your repository:

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Source", select:
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
5. Click **Save**

## Step 6: Access Your Documentation

After a few minutes, your documentation will be available at:

```
https://YOUR_USERNAME.github.io/ainalyn-sdk/
```

For example:
- User repo: https://yourname.github.io/ainalyn-sdk/
- Organization repo: https://ainalyn.github.io/ainalyn-sdk/

## Automatic Deployment (Future Updates)

The GitHub Actions workflow is already configured in `.github/workflows/docs.yml`.

After you push to master, GitHub Actions will automatically:
1. Build the documentation
2. Deploy to GitHub Pages
3. Your site updates automatically!

**Note**: The first deployment must be done manually with `mkdocs gh-deploy`. After that, GitHub Actions takes over.

## Custom Domain (Optional)

If you want to use a custom domain (e.g., docs.ainalyn.io):

1. Add a `CNAME` file to `docs/` directory:
   ```bash
   echo "docs.ainalyn.io" > docs/CNAME
   ```

2. Configure DNS with your domain provider:
   - Add a CNAME record pointing to `YOUR_USERNAME.github.io`

3. In GitHub repository settings → Pages:
   - Enter your custom domain
   - Enable "Enforce HTTPS"

4. Redeploy:
   ```bash
   git add docs/CNAME
   git commit -m "docs: add custom domain"
   git push
   .venv/Scripts/python.exe -m mkdocs gh-deploy
   ```

## Troubleshooting

### "remote origin already exists"

If you get this error when adding the remote:

```bash
# Remove existing remote
git remote remove origin

# Add the correct remote
git remote add origin https://github.com/YOUR_USERNAME/ainalyn-sdk.git
```

### "Permission denied" when pushing

If you're using HTTPS and get permission errors:

```bash
# Use SSH instead (if you have SSH keys set up)
git remote set-url origin git@github.com:YOUR_USERNAME/ainalyn-sdk.git
```

Or use a personal access token:
1. Generate token at https://github.com/settings/tokens
2. Use token as password when prompted

### "gh-pages branch already exists"

If the gh-pages branch exists but is out of date:

```bash
# Force deploy
.venv/Scripts/python.exe -m mkdocs gh-deploy --force
```

### Documentation not showing up

1. Check that `gh-pages` branch exists: https://github.com/YOUR_USERNAME/ainalyn-sdk/branches
2. Check GitHub Pages settings (Settings → Pages)
3. Wait 5-10 minutes for first deployment
4. Check build status in Actions tab

## Quick Reference

```bash
# First time setup
git remote add origin https://github.com/YOUR_USERNAME/ainalyn-sdk.git
git push -u origin master
.venv/Scripts/python.exe -m mkdocs gh-deploy

# Future updates (after GitHub Actions is active)
git add .
git commit -m "docs: update documentation"
git push  # GitHub Actions will auto-deploy

# Manual deployment (if needed)
.venv/Scripts/python.exe -m mkdocs gh-deploy
```

## Next Steps

After deployment:
- [ ] Share documentation URL with users
- [ ] Add documentation badge to README
- [ ] Test all links in the deployed site
- [ ] Set up custom domain (optional)

---

**Questions?** Check the [MkDocs deployment guide](https://www.mkdocs.org/user-guide/deploying-your-docs/) or open an issue!
