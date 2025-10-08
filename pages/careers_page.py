import time
import logging
from utils.helpers import by_css, by_xpath
from .base_page import BasePage

log = logging.getLogger(__name__)

HEADINGS_LOCATIONS = ["locations", "offices", "ofisler"]
HEADINGS_TEAMS = ["teams", "takımlar", "departments"]
HEADINGS_LIFE = ["life at insider", "culture", "kültür"]


class CareersPage(BasePage):
    QA_URL = "https://useinsider.com/careers/quality-assurance/"
    QA_SEE_ALL = by_xpath("//a[contains(.,'See all QA jobs') or contains(.,'See all jobs') or contains(.,'All QA')]")

    def _body_text_lower(self):
        try:
            return self.driver.find_element(*by_css("body")).text.lower()
        except Exception:
            return (self.driver.page_source or "").lower()

    def _ensure_keywords(self, words, tries=12, step_px=1000):
        for _ in range(tries):
            text = self._body_text_lower()
            if any(w in text for w in words):
                return True
            self.driver.execute_script(f"window.scrollBy(0,{step_px});")
            time.sleep(0.4)
        return False

    def assert_on_careers(self):
        url_ok = "careers" in self.driver.current_url.lower()
        text_ok = "career" in self._body_text_lower()
        assert url_ok or text_ok, "Careers sayfası yüklenemedi."
        log.info("Careers sayfası doğrulandı.")

    def assert_blocks(self):
        self.assert_on_careers()
        assert self._ensure_keywords(HEADINGS_LOCATIONS), "Locations / Ofisler bloğu bulunamadı."
        assert self._ensure_keywords(HEADINGS_TEAMS), "Teams / Takımlar bloğu bulunamadı."
        assert self._ensure_keywords(HEADINGS_LIFE), "Life at Insider bloğu bulunamadı."
        log.info("Careers sayfasındaki tüm bloklar doğrulandı.")

    def open_qa(self):
        self.open(self.QA_URL)
        self.wait_page_ready()
        try:
            self.safe_click(self.QA_SEE_ALL)
            log.info("QA sayfası açıldı (See all jobs tıklandı).")
        except Exception:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.safe_click(self.QA_SEE_ALL)
            log.info("QA sayfası açıldı (alt scroll ile See all jobs tıklandı).")
