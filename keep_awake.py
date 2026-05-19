import os
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


APP_URL = os.getenv("STREAMLIT_URL", "https://lytlerushcalculator.streamlit.app/")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# How long to keep the browser open after the app loads.
# 60 seconds is conservative enough for Streamlit to register the visit.
VISIT_SECONDS = int(os.getenv("VISIT_SECONDS", "60"))

WAKE_BUTTONS = [
    "Yes, get this app back up!",
    "Get this app back up",
    "Wake up",
]


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


def keep_awake() -> None:
    print(f"Opening Streamlit app: {APP_URL}")
    print(f"Headless mode: {HEADLESS}")
    print(f"Visit seconds: {VISIT_SECONDS}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            user_agent="Mozilla/5.0 KeepAwakeBot/1.0 Playwright Streamlit Visit",
        )
        page = context.new_page()

        try:
            page.goto(APP_URL, wait_until="domcontentloaded", timeout=120000)
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

            print(f"Holding the page open for {VISIT_SECONDS} seconds...")
            time.sleep(VISIT_SECONDS)

            print("Keep-awake visit finished successfully.")

        finally:
            browser.close()


if __name__ == "__main__":
    keep_awake()
