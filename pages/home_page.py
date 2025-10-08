import logging
from utils.helpers import by_css
from .base_page import BasePage

log = logging.getLogger(__name__)


class HomePage(BasePage):
    URL = "https://useinsider.com/"
    COOKIE_ACCEPT = by_css(
        "[id*='accept'], [aria-label*='accept'], "
        ".cookie-accept, .cookies-accept, button[aria-label='Accept']"
    )

    def open_home(self):
        self.open(self.URL)
        self.accept_cookies()
        log.info("Home sayfası açıldı.")
        return self

    def accept_cookies(self):
        elements = self.driver.find_elements(*self.COOKIE_ACCEPT)
        if not elements:
            log.debug("Cookie bildirimi bulunamadı.")
            return
        try:
            self.safe_click(self.COOKIE_ACCEPT)
            log.info("Cookie bildirimi kapatıldı (safe_click).")
        except Exception:
            self.js_click(self.COOKIE_ACCEPT)
            log.info("Cookie bildirimi kapatıldı (js_click).")

    def go_to_careers(self):
        self.open("https://useinsider.com/careers/")
        log.info("Careers sayfasına yönlendirildi.")
