# Streamlit Keep-Awake Bot

A small GitHub Actions + Playwright automation that visits a Streamlit Community Cloud app every 6 hours so it stays active.

This is useful for personal Streamlit apps that go to sleep after a period of inactivity.

Current default app:

```text
https://lytlerushcalculator.streamlit.app/
```

## What this app does

This bot runs on a schedule and performs a harmless browser visit to your Streamlit app.

It does the following:

1. Opens the Streamlit app URL.
2. Checks whether Streamlit shows the sleeping-app wake screen.
3. If the wake screen appears, it clicks the Streamlit wake button:
   - `Yes, get this app back up!`
   - `Get this app back up`
   - `Wake up`
4. Waits for the app to load.
5. Clicks a neutral area of the page body.
6. Keeps the browser open for a short time so the visit registers.
7. Closes the browser.

It does **not** click your app's processing buttons, upload files, download files, submit forms, delete data, or run calculations.

## How often does it run?

The GitHub Actions workflow runs every 6 hours using cron:

```yaml
schedule:
  - cron: "17 */6 * * *"
```

This means it runs at approximately:

```text
00:17 UTC
06:17 UTC
12:17 UTC
18:17 UTC
```

GitHub scheduled workflows use UTC time.

## Project structure

```text
Keep-Streamlit-Apps-Awake/
├── .github/
│   └── workflows/
│       └── keep-awake.yml
├── keep_awake.py
├── requirements.txt
└── README.md
```

## How to change it to your own Streamlit app

There are two easy ways to change the target app.

### Option 1: Edit the workflow file directly

Open:

```text
.github/workflows/keep-awake.yml
```

Find this section:

```yaml
env:
  STREAMLIT_URL: https://lytlerushcalculator.streamlit.app/
  HEADLESS: "true"
  VISIT_SECONDS: "60"
```

Change `STREAMLIT_URL` to your own Streamlit app URL:

```yaml
env:
  STREAMLIT_URL: https://your-app-name.streamlit.app/
  HEADLESS: "true"
  VISIT_SECONDS: "60"
```

Commit the change.

### Option 2: Use a GitHub repository variable

This is cleaner if you want other people to fork the repo and configure their own app without editing code.

1. Go to your GitHub repository.
2. Click **Settings**.
3. Click **Secrets and variables**.
4. Click **Actions**.
5. Click the **Variables** tab.
6. Click **New repository variable**.
7. Create this variable:

```text
STREAMLIT_URL
```

Set the value to your app URL:

```text
https://your-app-name.streamlit.app/
```

Then update the workflow file to use the variable:

```yaml
env:
  STREAMLIT_URL: ${{ vars.STREAMLIT_URL }}
  HEADLESS: "true"
  VISIT_SECONDS: "60"
```

## How to test it manually

After uploading the project to GitHub:

1. Go to the repository.
2. Click the **Actions** tab.
3. Click **Keep Streamlit App Awake**.
4. Click **Run workflow**.
5. Wait for the run to finish.

If it says **Success**, the bot opened your Streamlit app correctly.

## How to know it is running automatically

The workflow has two triggers:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "17 */6 * * *"
```

`workflow_dispatch` lets you run it manually.

`schedule` makes it run automatically every 6 hours.

After the next scheduled time passes, go to:

```text
Repository → Actions → Keep Streamlit App Awake
```

You should see a new run labeled as a scheduled run.

## Local testing in VS Code

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

Run locally with the browser visible:

```bash
HEADLESS=false VISIT_SECONDS=60 python keep_awake.py
```

On Windows PowerShell:

```powershell
$env:HEADLESS="false"
$env:VISIT_SECONDS="60"
python keep_awake.py
```

## Settings

The script reads these environment variables:

| Variable | Default | What it does |
|---|---:|---|
| `STREAMLIT_URL` | `https://lytlerushcalculator.streamlit.app/` | The Streamlit app to visit |
| `HEADLESS` | `true` | Whether the browser runs invisibly |
| `VISIT_SECONDS` | `60` | How long to keep the page open after loading |

## Important notes

Use this only for Streamlit apps that you own or are authorized to keep active.

This project is designed to create a harmless visit, not to spam clicks or interact with private data.

If your app has expensive computations that run automatically on page load, be careful. This bot will load the page every 6 hours.

## Troubleshooting

### The workflow does not appear in GitHub Actions

Make sure the workflow file exists exactly here:

```text
.github/workflows/keep-awake.yml
```

If it is anywhere else, GitHub will not detect it.

### The workflow runs manually but not automatically

Wait until the next UTC scheduled time passes. The schedule is:

```text
00:17 UTC
06:17 UTC
12:17 UTC
18:17 UTC
```

GitHub scheduled jobs can sometimes run a few minutes late.

### The app still sleeps

Try increasing `VISIT_SECONDS` from `60` to `90` or `120` in the workflow:

```yaml
VISIT_SECONDS: "120"
```

### The app URL changed

Update `STREAMLIT_URL` in the workflow or in your GitHub repository variable.
