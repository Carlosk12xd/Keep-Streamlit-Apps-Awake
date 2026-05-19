import os
import re
import time
from typing import List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


DEFAULT_URLS = [
    "https://lytlerushcalculator.streamlit.app/",
    "https://quantanalysisck.streamlit.app/",
    "https://exceltopdfck.streamlit.app/",
]

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# How long to keep each app open after it loads.
VISIT_SECONDS = int(os.getenv("VISIT_SECONDS", "60"))

# Wait between apps so the visits are clean and not rushed.
BETWEEN_APPS_SECONDS = int(os.getenv("BETWEEN_APPS_SECONDS", "10"))

WAKE_BUTTONS = [
    "Yes, get this app back up!",
    "Get this app back up",
    "Wake up",
]


def parse_streamlit_urls() -> List[str]:
    """
    Supports either:
    1. STREAMLIT_URLS as comma-separated URLs
    2. STREAMLIT_URLS as newline-separated URLs
    3. STREAMLIT_URL as one single URL for backwards compatibility
    4. DEFAULT_URLS if neither variable is provided
    """
    urls_raw = os.getenv("STREAMLIT_URLS", "").strip()

    if urls_raw:
        urls = []
        for chunk in urls_raw.replace(",", "\n").splitlines():
            cleaned = chunk.strip()
            if cleaned:
                urls.append(cleaned)
        return urls

    single_url = os.getenv("STREAMLIT_URL", "").strip()
    if single_url:
        return [single_url]

    return DEFAULT_URLS


def click_wake_button_if_present(page) -> bool:
    """
    If Streamlit shows the sleeping-app screen, click its official wake button.
    If the app is already awake, this does nothing.
    """
    for label in WAKE_BUTTONS:
        try:
            button = page.get_by_role(
                "button",
                name=re.compile(re.escape(label), re.I),
            )

            if button.count() > 0:
                button.first.click(timeout=7000)
                print(f"Clicked Streamlit wake button: {label}")
                return True

        except Exception as exc:
            print(f"Wake button check failed for '{label}': {exc}")

    print("No wake button found. The app may already be awake.")
    return False


def visit_one_app(page, url: str) -> None:
    print("\n" + "=" * 80)
    print(f"Opening Streamlit app: {url}")
    print("=" * 80)

    page.goto(url, wait_until="domcontentloaded", timeout=120000)
    time.sleep(10)

    clicked_wake = click_wake_button_if_present(page)

    if clicked_wake:
        print("Waiting for Streamlit to wake up...")
        time.sleep(45)

    try:
        page.wait_for_load_state("networkidle", timeout=60000)
    except PlaywrightTimeoutError:
        print("Network idle timeout. Continuing anyway.")

    # Harmless page interaction without touching app buttons.
    try:
        page.locator("body").click(position={"x": 20, "y": 20}, timeout=5000)
        print("Clicked neutral page area.")
    except Exception as exc:
        print(f"Neutral page click skipped: {exc}")

    print(f"Holding page open for {VISIT_SECONDS} seconds...")
    time.sleep(VISIT_SECONDS)

    print(f"Finished visit for: {url}")


def keep_awake_all_apps() -> None:
    urls = parse_streamlit_urls()

    if not urls:
        raise ValueError("No Streamlit URLs were provided.")

    print(f"Headless mode: {HEADLESS}")
    print(f"Visit seconds per app: {VISIT_SECONDS}")
    print(f"Between apps seconds: {BETWEEN_APPS_SECONDS}")
    print(f"Apps to visit: {len(urls)}")

    failures = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            user_agent="Mozilla/5.0 KeepAwakeBot/1.0 Playwright Streamlit Multi-App Visit",
        )
        page = context.new_page()

        try:
            for index, url in enumerate(urls, start=1):
                print(f"\nStarting app {index} of {len(urls)}")

                try:
                    visit_one_app(page, url)
                except Exception as exc:
                    print(f"ERROR visiting {url}: {exc}")
                    failures.append((url, str(exc)))

                if index < len(urls):
                    print(f"Waiting {BETWEEN_APPS_SECONDS} seconds before next app...")
                    time.sleep(BETWEEN_APPS_SECONDS)

        finally:
            browser.close()

    if failures:
        print("\nSome app visits failed:")
        for url, error in failures:
            print(f"- {url}: {error}")
        raise SystemExit(1)

    print("\nAll Streamlit apps were visited successfully.")


if __name__ == "__main__":
    keep_awake_all_apps()
