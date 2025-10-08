import os
import logging
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

log = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="chrome|firefox")
    parser.addoption("--headless", action="store_true", help="Run browser in headless mode")


def _make_screenshot(driver, item, prefix="FAIL"):
    os.makedirs("screenshots", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = getattr(item, "name", "test").replace("/", "_")
    path = os.path.join("screenshots", f"{prefix}_{ts}_{name}.png")

    try:
        if driver.save_screenshot(path):
            log.warning(f"Ekran görüntüsü kaydedildi → {path}")
        else:
            log.error(f"Ekran görüntüsü alınamadı: {path}")
    except Exception as e:
        log.error(f"Ekran görüntüsü hatası: {e}")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    log.info(f"Tarayıcı başlatılıyor: {browser} | headless={headless}")

    if browser == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = "eager"
        if headless:
            options.add_argument("-headless")
        options.set_preference("layout.css.devPixelsPerPx", "1.0")

        drv = webdriver.Firefox(options=options)
        try:
            drv.set_window_size(1400, 1000)
        except Exception:
            pass

    elif browser == "chrome":
        options = ChromeOptions()
        options.page_load_strategy = "eager"
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        drv = webdriver.Chrome(options=options)

    else:
        raise ValueError(f"Desteklenmeyen browser: {browser}")

    drv.implicitly_wait(5)
    log.info("WebDriver hazır.")

    yield drv

    try:
        drv.quit()
        log.info("WebDriver kapatıldı.")
    except Exception:
        log.warning("WebDriver kapatılırken hata oluştu.")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed and rep.when in ("setup", "call"):
        driver = item.funcargs.get("driver")
        if driver:
            _make_screenshot(driver, item)
