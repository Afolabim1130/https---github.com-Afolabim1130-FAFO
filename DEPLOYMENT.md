# FAFO Streamlit Cloud Deployment

## Minimal deployable repository contents

Include these files and folders in the GitHub repository:

- `app.py`
- `requirements.txt`
- `README.md`
- `config/`
- `database/`
- `modules/`
- `.streamlit/config.toml`
- `.env.example`
- `.gitignore`

## Files and folders to exclude

These should not be committed or pushed to GitHub for deployment:

- `evidence_repository/`
- `logs/`
- `fafo_database.db`
- `.env`
- `.vscode/`
- `scratch/`
- `*.docx`
- `*.pdf`
- any temporary or generated files

## How to create the GitHub repository

1. Create a new repository on GitHub called `FAFO`.
2. Copy the repository URL.
3. In this local workspace, run:

```bash
cd c:/Users/HP/Downloads/FAFO
git init
git add .
git commit -m "Initial FAFO Streamlit Cloud deploy package"
git remote add origin <YOUR_GITHUB_URL>
git branch -M main
git push -u origin main
```

## Streamlit Cloud deployment steps

1. Go to [Streamlit Cloud](https://streamlit.io/cloud).
2. Create a new app and connect it to your `FAFO` GitHub repository.
3. For the app file, choose `app.py`.
4. Streamlit Cloud will install dependencies from `requirements.txt`.

## Notes

- `app.py` is the Streamlit application entrypoint.
- `requirements.txt` must contain all Python packages the app depends on.
- `config/settings.py` creates required directories at runtime if they do not exist.
- Keep sensitive credentials out of the repository by using `.env` locally and not pushing it.
