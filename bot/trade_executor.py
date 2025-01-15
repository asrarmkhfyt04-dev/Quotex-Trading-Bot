# bot/trade_executor.py (excerpt)

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from .config import QUOTEX_USERNAME, QUOTEX_PASSWORD, USE_DEMO, ASSET_NAME

class TradeExecutor:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.5672.127 Safari/537.36"
        )
        self.driver = uc.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.login_to_quotex()

    def login_to_quotex(self):
        self.driver.get("https://qxbroker.com/en/sign-in/modal/")
        time.sleep(2)

        email_field = self.driver.find_element(By.NAME, "email")
        email_field.clear()
        email_field.send_keys(QUOTEX_USERNAME)

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(QUOTEX_PASSWORD)

        sign_in_button = self.driver.find_element(
            By.CSS_SELECTOR, "button.button.button--primary.button--spaced[type='submit']"
        )
        sign_in_button.click()

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.asset-select__button"))
        )
        print("DEBUG: Logged in successfully.")

        if USE_DEMO:
            self._switch_to_demo()
        else:
            print("DEBUG: USE_DEMO is false => staying in Live mode.")
            time.sleep(1)

        final_balance = self.get_account_balance()
        print(f"DEBUG: Final account balance: {final_balance}")

    def _switch_to_demo(self):
        menu_container = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.usermenu__info-wrapper"))
        )
        menu_container.click()
        time.sleep(1)

        demo_link = self.driver.find_element(
            By.CSS_SELECTOR, "a.usermenu__select-name[href='/en/demo-trade']"
        )
        demo_link.click()
        time.sleep(2)
        print("DEBUG: Clicked Demo Account => should be in Demo mode now.")

        close_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.button.button--dark.modal-account-type-changed__body-button")
            )
        )
        close_btn.click()
        time.sleep(1)
        print("DEBUG: Clicked 'Close' on the account-type-changed modal.")

    def get_account_balance(self) -> float:
        balance_elem = self.driver.find_element(By.CSS_SELECTOR, "div.usermenu__info-balance")
        raw_text = balance_elem.text
        clean_text = raw_text.replace("$", "").replace(",", "").strip()
        return float(clean_text)

    def fetch_market_data(self) -> dict:
        data = {"last_price": 0.0}
        if USE_DEMO:
            data["last_price"] = 1.2345
            return data
        try:
            price_elem = self.driver.find_element(By.CSS_SELECTOR, "span.current-price")
            data["last_price"] = float(price_elem.text)
        except NoSuchElementException:
            print("DEBUG: 'span.current-price' not found in Live mode. Setting last_price=0.0.")
            data["last_price"] = 0.0
        return data

    def select_asset(self, asset_text=None):
        if not asset_text:
            asset_text = ASSET_NAME
        plus_button = self.driver.find_element(By.CSS_SELECTOR, "button.asset-select__button")
        plus_button.click()
        xpath_asset = f"//span[contains(text(),'{asset_text}')]"
        asset_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_asset))
        )
        asset_element.click()

    def set_investment_amount(self, target_amount=1.0):
        invest_container = self.driver.find_element(
            By.CSS_SELECTOR,
            "div.input-control.input-control--number.input-control--dark.input-control--text-left"
        )
        minus_btn = invest_container.find_element(
            By.CSS_SELECTOR,
            "button.input-control__button:nth-of-type(1)"
        )
        plus_btn = invest_container.find_element(
            By.CSS_SELECTOR,
            "button.input-control__button:nth-of-type(2)"
        )
        def read_current_investment():
            input_elem = invest_container.find_element(By.CSS_SELECTOR, "input.input-control__input")
            raw = input_elem.get_attribute("value")
            return float(raw.replace("$", "").strip())
        max_clicks = 100
        for _ in range(max_clicks):
            current = read_current_investment()
            if abs(current - target_amount) < 1e-9:
                break
            if current < target_amount:
                plus_btn.click()
            else:
                minus_btn.click()
            time.sleep(0.2)
        else:
            raise RuntimeError(f"Could not set investment from {current} to {target_amount} in {max_clicks} clicks.")

    def place_trade(self, direction="UP"):
        if direction.upper() == "UP":
            up_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button.button--success.call-btn.section-deal__button"
            )
            up_btn.click()
        else:
            down_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button.button--danger.put-btn.section-deal__button"
            )
            down_btn.click()
        time.sleep(1)

    def close(self):
        self.driver.quit()
