# FAFO GitHub & Streamlit Cloud Deployment Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository with:
   - **Repository name:** `FAFO`
   - **Description:** Forensic Analysis & Forensic Operations - Streamlit-based evidence management system
   - **Visibility:** Public (required for Streamlit Cloud free tier)
   - **Do NOT initialize with README** (you already have one)
   - Click **Create repository**

## Step 2: Connect Local Repo to GitHub

Run these commands in your terminal from the FAFO directory:

```powershell
cd c:\Users\HP\Downloads\FAFO
git remote add origin https://github.com/adesojikola/FAFO.git
git branch -M main
git push -u origin main
```

**Note:** Replace `adesojikola` with your GitHub username if different.

If you get authentication errors, use a GitHub Personal Access Token (PAT):
- Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Create a token with `repo` scope
- When prompted for password during git push, use your PAT instead

## Step 3: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click **"Deploy an app"**
3. Select:
   - **GitHub repo:** `adesojikola/FAFO`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"**

## Step 4: Configure Environment Variables

After Streamlit Cloud deploys, add these secrets:

1. Go to your app's settings (gear icon)
2. Click **"Secrets"**
3. Paste your secrets in TOML format:

```toml
OCR_FALLBACK_ENABLED = "true"
FFMPEG_FALLBACK_ENABLED = "true"
# Add any additional API keys or credentials needed
```

## Deployment Files Included

The repository contains only the minimal set of files needed:

```
FAFO/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
├── .env.example             # Environment variables template
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── config/
│   ├── __init__.py
│   ├── roles.py             # Role-based access control
│   └── settings.py          # Configuration settings
└── modules/
    ├── __init__.py
    ├── auth.py              # Authentication logic
    ├── ocr_engine.py        # OCR text extraction
    ├── ffmpeg_processor.py  # Video metadata extraction
    ├── utils.py             # Styling and utilities
    ├── incident_manager.py  # Incident management
    ├── repository.py        # File repository management
    ├── audit_logger.py      # Audit logging
    ├── dashboard.py         # Dashboard utilities
    ├── export_manager.py    # Export functionality
    ├── notifications.py     # Notification system
    ├── lawyer_portal.py     # Lawyer portal
    ├── security.py          # Security utilities
    └── hashing.py           # File hashing utilities
```

## Excluded from Repository

These are automatically ignored and won't be pushed:

- `evidence_repository/` - Runtime-generated evidence storage
- `logs/` - Application logs
- `database/` - Local SQLite database
- `.env` - Credentials (only `.env.example` is tracked)
- `.vscode/` - IDE configuration
- `scratch/` - Development/testing files
- `*.docx`, `*.pdf` - Documentation files
- Any `__pycache__/` or `.pyc` files

## Troubleshooting

### Issue: "pytesseract" not found on Streamlit Cloud

**Solution:** The app uses cross-platform binary detection. Tesseract will fall back to heuristic text extraction if the binary is unavailable.

### Issue: "ffmpeg/ffprobe" not found on Streamlit Cloud

**Solution:** The app uses cross-platform binary detection. Video metadata extraction will gracefully degrade if ffprobe is unavailable.

### Issue: App crashes on startup

1. Check Streamlit Cloud app logs (click **"Manage app"** → **"Logs"**)
2. Verify all environment variables are set in Secrets
3. Ensure Python version is 3.8+

### Issue: Authentication not working

Check that `config/roles.py` and `modules/auth.py` are properly included and accessible.

## Local Development

To test before deploying to Streamlit Cloud:

```powershell
cd c:\Users\HP\Downloads\FAFO
pip install -r requirements.txt
streamlit run app.py
```

Then visit `http://localhost:8501` in your browser.

## Updating Streamlit Cloud

After making changes locally:

```powershell
git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy within 1-2 minutes.

## Next Steps

- [ ] Create GitHub repository named "FAFO"
- [ ] Run the git remote commands above
- [ ] Push code to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Test the app in production
- [ ] Configure environment secrets as needed
