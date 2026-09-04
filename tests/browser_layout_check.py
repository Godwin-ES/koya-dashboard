"""Browser regression check for the fixed Streamlit toolbar clearance.

Run against a local dashboard with:
    uv run --with selenium python tests/browser_layout_check.py
"""

from __future__ import annotations

import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


MINIMUM_TOOLBAR_GAP = 8


def element_top(driver: webdriver.Chrome, selector: str) -> float:
    element = driver.find_element(By.CSS_SELECTOR, selector)
    return float(
        driver.execute_script(
            "return arguments[0].getBoundingClientRect().top;",
            element,
        )
    )


def element_bottom(driver: webdriver.Chrome, selector: str) -> float:
    element = driver.find_element(By.CSS_SELECTOR, selector)
    return float(
        driver.execute_script(
            "return arguments[0].getBoundingClientRect().bottom;",
            element,
        )
    )


def check_toolbar_clearance(url: str, width: int) -> tuple[float, float]:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={width},900")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda active_driver: active_driver.find_elements(
                By.CSS_SELECTOR,
                ".report-header .eyebrow",
            )
        )

        toolbar_bottom = element_bottom(driver, '[data-testid="stHeader"]')
        eyebrow_top = element_top(driver, ".report-header .eyebrow")

        assert eyebrow_top >= toolbar_bottom + MINIMUM_TOOLBAR_GAP, (
            f"At {width}px, the report eyebrow starts at {eyebrow_top:.1f}px "
            f"but must start at or below {toolbar_bottom + MINIMUM_TOOLBAR_GAP:.1f}px "
            "to clear the fixed Streamlit toolbar."
        )
        return toolbar_bottom, eyebrow_top
    finally:
        driver.quit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    args = parser.parse_args()

    for width in (1488, 760):
        toolbar_bottom, eyebrow_top = check_toolbar_clearance(args.url, width)
        print(
            f"{width}px: toolbar bottom {toolbar_bottom:.1f}px; "
            f"eyebrow top {eyebrow_top:.1f}px"
        )


if __name__ == "__main__":
    main()
