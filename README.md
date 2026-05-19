# Streamlit Keep-Awake Bot

This project opens your Streamlit app every 6 hours using GitHub Actions.

It does not click your app's processing buttons. It only:

1. Opens your Streamlit app.
2. Clicks Streamlit's wake button if the sleeping page appears.
3. Clicks a neutral area of the page.
4. Keeps the browser open for 60 seconds.

App:

```text
https://lytlerushcalculator.streamlit.app/
```

## Run locally in VS Code

### Mac/Linux

```bash
chmod +x run_local_mac_linux.sh
./run_local_mac_linux.sh
```

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run_local_windows.ps1
```

## Manual local setup

```bash
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
# .venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -r requirements.txt
playwright install chromium

HEADLESS=false VISIT_SECONDS=60 python keep_awake.py
```

For Windows PowerShell:

```powershell
$env:HEADLESS="false"
$env:VISIT_SECONDS="60"
python keep_awake.py
```

## Upload to GitHub

1. Create a new GitHub repository.
2. Upload all files from this folder.
3. Make sure this file exists in the repository:

```text
.github/workflows/keep-awake.yml
```

4. Go to the repository's **Actions** tab.
5. Enable workflows if GitHub asks.
6. Open **Keep Streamlit App Awake**.
7. Click **Run workflow** to test it manually.

After that, it will run every 6 hours automatically.

## Schedule

The workflow uses:

```yaml
schedule:
  - cron: "17 */6 * * *"
```

That means every 6 hours at minute 17.
