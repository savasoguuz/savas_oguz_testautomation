from __future__ import annotations
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from utils.helpers import by_xpath
from .base_page import BasePage

log = logging.getLogger(__name__)


class QAJobsPage(BasePage):
    SEE_ALL_LINK = by_xpath("//a[contains(., 'See all QA jobs') or contains(., 'See all jobs')]")
    JOB_CONTAINER = by_xpath("//*[@id='jobs-list']/div")
    JOB_CARDS = by_xpath(
        "//div[contains(@class,'posting') or contains(@class,'job') or contains(@class,'position') or contains(@class,'vacancy')]"
        " | //a[contains(@href,'lever.co')]"
    )
    VIEW_ROLE_BUTTON = by_xpath(".//a[contains(., 'View Role') or contains(., 'View role')]")

    def _wait(self, cond, to=20):
        return WebDriverWait(self.driver, to).until(cond)

    def _click_js(self, el):
        try:
            el.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", el)
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def _close_overlays(self):
        time.sleep(1)
        for xp in [
            "//*[@id='onetrust-accept-btn-handler']",
            "//button[contains(., 'Accept') or contains(., 'OK')]",
            "//button[contains(@class,'close') or @aria-label='Close']",
        ]:
            try:
                el = self._wait(EC.element_to_be_clickable((By.XPATH, xp)), to=2)
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                self._click_js(el)
                log.debug(f"Overlay kapatıldı: {xp}")
                time.sleep(0.3)
            except Exception:
                pass

    def _set_select2(self, select_id, value):
        script = f"""
            var s = $('#{select_id}');
            if (!s.length) return;
            if (!s.find('option[value="{value}"]').length) {{
                var o = new Option('{value}', '{value}', true, true);
                s.append(o);
            }} else s.val('{value}');
            s.val('{value}').trigger('change').trigger('select2:select');
        """
        self.driver.execute_script(script)

    def apply_filters(self, dept="Quality Assurance", loc="Istanbul, Turkiye"):
        self.wait_page_ready()
        self._close_overlays()
        try:
            self._set_select2("filter-by-location", loc)
            log.info(f"Konum filtresi: {loc}")
            time.sleep(7)
        except Exception as e:
            log.error(f"Location filtresi başarısız: {e}")
            raise AssertionError(f"Location filtresi başarısız: {e}")

        try:
            self._set_select2("filter-by-department", dept)
            log.info(f"Departman filtresi: {dept}")
            time.sleep(3)
        except Exception as e:
            log.error(f"Department filtresi başarısız: {e}")
            raise AssertionError(f"Department filtresi başarısız: {e}")

        time.sleep(5)
        cards = [c for c in self.driver.find_elements(*self.JOB_CARDS) if "no job postings" not in (c.text or "").lower()]
        self.last_cards = cards
        log.info(f"{len(cards)} iş ilanı bulundu.")
        return cards

    def open_qa(self):
        self.open("https://useinsider.com/careers/quality-assurance/")
        self.wait_page_ready()
        time.sleep(1)
        try:
            self.safe_click(self.SEE_ALL_LINK)
            log.info("QA sayfası açıldı.")
        except Exception:
            log.warning("See all jobs linki tıklanamadı.")

    def scroll_and_click_view_role(self, timeout=15):
        log.info("Container’a kaydırılıyor...")
        try:
            container = self._wait(EC.presence_of_element_located(self.JOB_CONTAINER), timeout)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", container)
            time.sleep(2)
        except TimeoutException:
            log.error("Job container bulunamadı.")
            raise AssertionError("Job container bulunamadı.")

        try:
            self._click_js(container)
            log.debug("Container tıklaması yapıldı.")
            time.sleep(1)
        except Exception:
            log.warning("Container tıklaması başarısız, devam ediliyor...")

        try:
            btn = container.find_element(*self.VIEW_ROLE_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(1)
            self._click_js(btn)
            log.info("View Role butonuna tıklandı.")
        except NoSuchElementException:
            log.error("View Role butonu bulunamadı.")
            raise AssertionError("View Role butonu bulunamadı.")
        except Exception:
            log.error("View Role butonuna tıklanamadı.")
            raise AssertionError("View Role butonuna tıklanamadı.")

        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) >= 1)
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 10).until(lambda d: d.title.strip() or "http" in d.current_url.lower())
        log.info("Yeni sekmeye geçildi.")
        return self.driver.current_url
