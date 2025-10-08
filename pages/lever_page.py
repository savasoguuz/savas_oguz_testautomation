import logging
from utils.helpers import by_css, by_xpath
from .base_page import BasePage

log = logging.getLogger(__name__)


class LeverPage(BasePage):
    LEVER_IFRAME = by_xpath("//iframe[contains(@src,'lever.co') or contains(@id,'lever')]")
    LEVER_ROOT = by_css(
        "#lever-jobs-container, .posting, .posting-headline, .postings, [data-qa='posting-title'], .main-header"
    )

    def assert_loaded(self):
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            log.debug("Yeni sekmeye geçildi.")

        try:
            iframe = self.driver.find_element(*self.LEVER_IFRAME)
            self.driver.switch_to.frame(iframe)
            log.debug("Lever iframe'e geçiş yapıldı.")
        except Exception:
            log.debug("Iframe bulunamadı, doğrudan sayfa doğrulanacak.")

        self.visible(self.LEVER_ROOT)
        log.info("Lever sayfası başarıyla yüklendi.")
