from selenium.webdriver.common.by import By

def by_css(css):
    return (By.CSS_SELECTOR, css)

def by_xpath(xp):
    return (By.XPATH, xp)
