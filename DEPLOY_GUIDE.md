# 🚀 Deploy to Streamlit Cloud - Step by Step

Your app is ready to deploy! Follow these simple steps to get a public URL you can share with anyone.

---

## ✅ What's Ready

- ✅ Git repository initialized
- ✅ Standalone Streamlit app created ([streamlit_app.py](streamlit_app.py))
- ✅ Dependencies listed ([requirements.txt](requirements.txt))
- ✅ Sample data included
- ✅ Initial commit made

---

## 📋 Steps to Deploy

### Step 1: Create GitHub Account (if you don't have one)

1. Go to https://github.com
2. Click "Sign up"
3. Follow the registration process (free account is fine)

### Step 2: Create a New GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `hometown-incentive-calculator` (or any name you like)
   - **Description**: "Employee incentive calculator for Hometown stores"
   - **Visibility**: Choose **Public** (required for free Streamlit Cloud)
3. **DO NOT** check "Add a README file" (we already have one)
4. Click "Create repository"

### Step 3: Push Your Code to GitHub

GitHub will show you commands. Use these **in your project folder**:

```bash
git remote add origin https://github.com/YOUR_USERNAME/hometown-incentive-calculator.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username.

**Example**:
```bash
git remote add origin https://github.com/johnsmith/hometown-incentive-calculator.git
git branch -M main
git push -u origin main
```

When prompted, enter your GitHub username and password (or use a Personal Access Token).

### Step 4: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "Sign in" (use your GitHub account)
3. Click "New app"
4. Fill in:
   - **Repository**: Select your `hometown-incentive-calculator` repo
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click "Deploy!"

### Step 5: Wait for Deployment

- Deployment takes 2-5 minutes
- You'll see a progress indicator
- Once done, you'll get a public URL like:
  `https://hometown-incentive-calculator-xxx.streamlit.app`

### Step 6: Share Your Link! 🎉

Your app is now live! Anyone with the link can:
- Upload their Excel files
- Get instant calculations
- Download results

---

## 🎯 Quick Commands

**If you need to make changes later:**

```bash
# Make your changes to streamlit_app.py
# Then:
git add streamlit_app.py
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud will automatically redeploy when you push!

---

## 🆘 Troubleshooting

### "Permission denied" when pushing to GitHub

**Solution**: Create a Personal Access Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token (classic)
3. Check "repo" scope
4. Copy the token
5. Use it as your password when pushing

### Deployment fails on Streamlit Cloud

**Common fixes**:
1. Check that `streamlit_app.py` is in the root folder
2. Verify `requirements.txt` has the right packages
3. Look at the deployment logs for specific errors

### Want to update the app?

1. Edit `streamlit_app.py` locally
2. Test it: `streamlit run streamlit_app.py`
3. Commit and push:
   ```bash
   git add streamlit_app.py
   git commit -m "Update: your changes"
   git push
   ```
4. Streamlit Cloud auto-deploys in ~2 minutes

---

## 📝 What Was Created for Cloud Deployment

1. **[streamlit_app.py](streamlit_app.py)** - Standalone app (no backend needed)
   - Includes all calculation logic
   - File upload & processing
   - Results display & download
   - Works completely on Streamlit Cloud

2. **[requirements.txt](requirements.txt)** - Minimal dependencies
   - streamlit
   - pandas
   - openpyxl

3. **[.gitignore](.gitignore)** - Excludes unnecessary files
   - Virtual environments
   - Cache files
   - Local data (except sample file)

4. **Git repository** - Ready to push
   - Initial commit done
   - Just need to add GitHub remote

---

## 💡 Tips

- **Free tier limits**: Streamlit Cloud free tier can handle moderate traffic
- **Update anytime**: Just push to GitHub, auto-deploys
- **View logs**: Check Streamlit Cloud dashboard for errors
- **Custom domain**: Available on paid plans
- **Privacy**: Make repo private (requires paid Streamlit plan)

---

## 🎉 Next Steps

1. **Create GitHub account** (if needed)
2. **Create new repo** on GitHub
3. **Run the push commands** shown in Step 3
4. **Deploy on Streamlit Cloud**
5. **Share your link** with anyone!

**Estimated time**: 10-15 minutes total

---

Need help? The commands are ready to copy-paste. Just replace `YOUR_USERNAME` with your GitHub username and you're good to go!
