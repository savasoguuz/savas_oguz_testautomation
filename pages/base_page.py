import time
import logging
from selenium.webdriver import ActionChains
from utils.waits import wait_visible, wait_clickable

log = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)
        log.info(f"Sayfa açıldı → {url}")
        return self

    def wait_page_ready(self, timeout=20):
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.driver.execute_script("return document.readyState") == "complete":
                    return
            except Exception:
                pass
            time.sleep(0.2)
        log.warning("Sayfa tam olarak yüklenemedi (timeout).")

    def visible(self, locator):
        return wait_visible(self.driver, locator)

    def click(self, locator):
        wait_clickable(self.driver, locator).click()
        log.debug(f"Tıklandı: {locator}")

    def scroll_into_view(self, locator):
        el = self.visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        log.debug(f"Scroll edildi: {locator}")
        return el

    def scroll_by(self, y=800):
        self.driver.execute_script(f"window.scrollBy(0,{y});")
        log.debug(f"Sayfa {y}px aşağı kaydırıldı.")

    def hover(self, locator):
        el = self.visible(locator)
        ActionChains(self.driver).move_to_element(el).perform()
        log.debug(f"Hover edildi: {locator}")
        return el

    def js_click(self, locator):
        el = self.visible(locator)
        self.driver.execute_script("arguments[0].click();", el)
        log.debug(f"JS click uygulandı: {locator}")

    def safe_click(self, locator):
        for action in (self.click, self.scroll_into_view, self.hover, self.js_click):
            try:
                action(locator)
                return
            except Exception:
                continue
        log.error(f"Tıklama başarısız: {locator}")

    def get_text(self, locator):
        text = self.visible(locator).text
        log.debug(f"Text alındı: {text[:60]}...")
        return text
